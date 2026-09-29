"""Phase 0 §22 + §24: the output is canonical bytes, twice, and once more in another process.

Two different promises are tested here.

*Byte stability.* The same manifest audited twice yields identical bytes, on every platform, because
the writer pins ``newline="\\n"`` and the serializer sorts keys and fixes separators. No timestamp,
no run path, no volatile field appears anywhere in the payload.

*Hash-seed independence.* Python iterates a ``set`` in an order that depends on the interpreter's
hash seed, so a second run inside one process proves nothing about text assembled from a set. The
last test re-audits the same manifest in *separate* interpreters with different ``PYTHONHASHSEED``
values and compares the bytes; a reason built by unordered iteration would differ between them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from support import claim, document, float_anchor, link, write_case

from paper_doctor.audit import audit_manifest
from paper_doctor.cli import render_text
from paper_doctor.status import RuleFinding, RuleStatus, canonical_json, write_json

REPO = Path(__file__).resolve().parents[1]
FINDING_KEYS = {"rule_id", "rule_name", "target", "status", "question", "measurements", "evidence", "reason"}
VOLATILE = ("timestamp", "time", "date", "generated", "uuid", "session", "pid", "elapsed", "host", "seed")

PROSE = "Ours reaches $0.42$ in Table~\\ref{tab:main}."
PAPER = document(
    "\\begin{table}\\caption{Main}\\label{tab:main}"
    "\\begin{tabular}{|l|c|}\\hline A & 0.42 \\\\\\hline\\end{tabular}\\end{table}",
    "\\begin{table}\\caption{Other}\\label{tab:other}"
    "\\begin{tabular}{|l|c|}\\hline A & 0.99 \\\\\\hline\\end{tabular}\\end{table}",
    PROSE,
)


def _case(tmp_path: Path, name: str) -> Path:
    return write_case(
        tmp_path / name,
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", PROSE, form="NUMERIC_ATTRIBUTION", links=["L1"])],
        floats=[float_anchor("tab:main", float_id="tab-main"), float_anchor("tab:other", float_id="tab-other")],
        links=[link("L1", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE")],
    )


# --- byte stability --------------------------------------------------------------------------


def test_two_audits_of_one_manifest_are_the_same_bytes(tmp_path: Path) -> None:
    manifest = _case(tmp_path, "a")
    assert canonical_json(audit_manifest(manifest)) == canonical_json(audit_manifest(manifest))


def test_the_written_file_carries_no_carriage_return(tmp_path: Path) -> None:
    """`newline="\\n"` is the only thing standing between the byte promise and Windows text mode."""
    manifest = _case(tmp_path, "b")
    report = tmp_path / "report.json"
    write_json(audit_manifest(manifest), report)
    raw = report.read_bytes()
    assert b"\r" not in raw
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    write_json(audit_manifest(manifest), report)
    assert report.read_bytes() == raw


def test_the_text_face_is_stable_too(tmp_path: Path) -> None:
    manifest = _case(tmp_path, "c")
    assert render_text(audit_manifest(manifest)) == render_text(audit_manifest(manifest))


def test_payload_has_the_eight_frozen_keys_and_no_volatile_field(tmp_path: Path) -> None:
    manifest = _case(tmp_path, "d")
    rows: list[dict[str, Any]] = json.loads(canonical_json(audit_manifest(manifest)))
    assert rows, "a canonical-output test on an empty payload would prove nothing"
    for row in rows:
        assert set(row) == FINDING_KEYS
    names = [key for row in rows for key in (*row, *row["measurements"])]
    assert not [key for key in names if any(token in key.lower() for token in VOLATILE)]


def test_the_canonical_form_is_a_fixed_point_of_itself(tmp_path: Path) -> None:
    """Sorted keys at every depth, the fixed separators, and `ensure_ascii=False`: re-canonicalising
    the text changes not one byte, which is what "a diff of two runs is empty" means downstream."""
    manifest = _case(tmp_path, "e")
    text = canonical_json(audit_manifest(manifest))
    assert text == json.dumps(json.loads(text), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_non_ascii_stays_literal_in_the_bytes() -> None:
    """A reason that quotes a paper sentence keeps its sigma, its typographic minus and its accents
    as UTF-8, not as escapes a reader cannot line up against the source."""
    finding = RuleFinding(
        "PD003", "Quantitative Claim Consistency", "C1", RuleStatus.INCONCLUSIVE, "q", {}, (), "3σ is \u22120.499"
    )
    raw = (canonical_json([finding]) + "\n").encode("utf-8")
    assert "\u2212".encode("utf-8") in raw and b"\\u00b1" not in raw and b"\\u2212" not in raw
    assert json.loads(raw.decode("utf-8"))[0]["reason"].endswith("\u22120.499")


# --- cross-process: hash-seed independence ---------------------------------------------------

_CHILD = """
import sys
from paper_doctor.audit import audit_manifest
from paper_doctor.status import write_json
write_json(audit_manifest(sys.argv[1]), sys.argv[2])
"""


def _audit_in_a_fresh_interpreter(manifest: Path, destination: Path, seed: int) -> bytes:
    env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(REPO / "src"), PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable, "-c", _CHILD, str(manifest), str(destination)], env=env, cwd=str(REPO), check=True)
    return destination.read_bytes()


def test_the_bytes_survive_a_different_hash_seed_in_a_different_process(tmp_path: Path) -> None:
    manifest = _case(tmp_path, "f")
    runs = [_audit_in_a_fresh_interpreter(manifest, tmp_path / f"f{seed}.json", seed) for seed in (0, 1, 424242)]
    assert runs[0] == runs[1] == runs[2], "some finding text depends on set iteration order"


def test_the_directory_holding_the_manifest_is_not_part_of_the_payload(tmp_path: Path) -> None:
    """Evidence is quoted by path relative to the audit root, so the same paper audited out of two
    different checkouts produces identical bytes -- a rerun elsewhere is diffable."""
    left = _case(tmp_path / "one", "g")
    right = _case(tmp_path / "two", "g")
    assert canonical_json(audit_manifest(left)) == canonical_json(audit_manifest(right))
