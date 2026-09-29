"""Phase 3 §1-§13: the unseen end-to-end acceptance, on TabM (arXiv 2410.24210).

This is the paper Paper Doctor was never written for. The acceptance has to show two things, and
they are different things:

* **The machinery is generic.** The workspace below adds no adapter, no parser branch, no path
  convention and no schema key; it is the same `paper-doctor.yml` + structured-source + RD-snapshot
  workflow Phase 2 shipped, and the only link bases it uses are the declared ones. `
  `tests/test_phase3_firewalls.py` checks `src/` for the code half of that claim; this file checks
  the data half, because a manifest that invented a TabM-shaped escape hatch would also pass.
* **The statuses are the frozen ones.** Every expectation below was read off the audit output once
  and then written here as a literal, so a rule that quietly changed its mind is a test failure and
  not a documentation update. The tally is 10 PASS / 2 FAIL / 5 INCONCLUSIVE / 14 NOT_APPLICABLE /
  1 NOT_RUN over 32 findings.

C8 is the negative control and the point of the exercise: its text `$16\\,281$` is a real string in
the real source, so nothing at the manifest layer can reject it -- only the cell comparison can say
the attribution is false, and it does. C9 is the opposite boundary: a merged leading cell gives the
declared address two readings, and PD refuses to choose. A FAIL here means one claim disagreed with
one linked piece of evidence; it does not mean the paper is false, unreliable or rejected (§17).

The corpus is read-only and never vendored. `scripts/fetch_acceptance_inputs.py tabm` rebuilds it
from arXiv against a pinned tarball digest; `PAPER_DOCTOR_TABM_CORPUS` points this test at a
checkout elsewhere. A missing corpus is a hard error, never a skip.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml
from support import statuses

from paper_doctor.audit import audit_manifest
from paper_doctor.cli import EXIT_OK, main
from paper_doctor.status import RuleFinding

REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO / "phase3" / "tabm"
MANIFEST = WORKSPACE / "paper-doctor.yml"
RD_ARTIFACT = WORKSPACE / "findings.json"
LEDGER = WORKSPACE / "end_to_end_chain.json"
DEFAULT_CORPUS = WORKSPACE.parent / "acceptance-inputs" / "tabm-arxiv" / "src"
CORPUS_ENV = "PAPER_DOCTOR_TABM_CORPUS"
ENTRY_POINT = "main.tex"

#: The frozen TabM status matrix, one row per rule, keyed by claim id.
FROZEN_MATRIX: dict[str, dict[str, str]] = {
    "PD001": {
        "C1": "PASS",
        "C2": "PASS",
        "C3": "INCONCLUSIVE",
        "C4": "PASS",
        "C5": "PASS",
        "C6": "PASS",
        "C7": "PASS",
        "C8": "PASS",
        "C9": "PASS",
    },
    "PD002": {
        "C1": "NOT_APPLICABLE",
        "C2": "NOT_APPLICABLE",
        "C3": "NOT_APPLICABLE",
        "C4": "NOT_APPLICABLE",
        "C7": "INCONCLUSIVE",
    },
    "PD003": {"C6": "PASS", "C8": "FAIL", "C9": "INCONCLUSIVE"},
    "PD004": {"rule:PD004": "NOT_RUN"},
    "PD005": {"C4": "NOT_APPLICABLE"},
    "PD006": {"C1": "PASS", "C2": "FAIL", "C4": "INCONCLUSIVE", "C5": "INCONCLUSIVE"},
    "PD007": {claim: "NOT_APPLICABLE" for claim in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9")},
}

FROZEN_TALLY = {"PASS": 10, "FAIL": 2, "INCONCLUSIVE": 5, "NOT_APPLICABLE": 14, "NOT_RUN": 1}

#: §6: the only link bases the acceptance may use. `AUTHOR_NAMED_FLOAT` is legal but unused here.
ALLOWED_BASES = {"AUTHOR_REF_IN_SENTENCE", "AUTHOR_NAMED_FLOAT", "AUDITOR_DECLARED"}

_CHILD = """
import sys
from paper_doctor.cli import main
raise SystemExit(main(["audit", sys.argv[1], "--json", sys.argv[2]]))
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["_registry"]


def corpus_root() -> Path:
    """Where the read-only TabM source lies, or a hard error naming the way to rebuild it."""
    override = os.environ.get(CORPUS_ENV)
    root = Path(override) if override else DEFAULT_CORPUS
    if not (root / ENTRY_POINT).is_file():
        raise FileNotFoundError(
            f"the TabM acceptance corpus is not at {root}. Rebuild it with "
            f"`python scripts/fetch_acceptance_inputs.py tabm`, or point {CORPUS_ENV} at a checkout "
            f"of arXiv 2410.24210 whose {ENTRY_POINT} is sha256 {_registry()['paper']['sha256']}. "
            f"An acceptance that cannot read its paper is a failure, not a skip."
        )
    return root.resolve()


def _audit_case(tmp_path: Path) -> Path:
    """The frozen manifest, relocated only if the corpus lives somewhere other than its default.

    Two keys can move: the declared paper root, and -- because a relocated manifest no longer sits
    next to the upstream artifact -- the artifact path, which is made absolute. Nothing else is
    touched, so every declared claim, anchor, link, digest and size is the frozen one.
    """
    if corpus_root() == (MANIFEST.parent / str(_registry()["paper"].get("root", ""))).resolve():
        return MANIFEST
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    document["_registry"]["paper"]["root"] = corpus_root().as_posix()
    document["_registry"]["rd_findings"]["path"] = RD_ARTIFACT.resolve().as_posix()
    written = tmp_path / MANIFEST.name
    written.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return written


@pytest.fixture(scope="module")
def findings() -> list[RuleFinding]:
    with tempfile.TemporaryDirectory(prefix="paper-doctor-tabm-") as scratch:
        return audit_manifest(_audit_case(Path(scratch)))


def test_the_corpus_is_the_paper_the_manifest_committed_to() -> None:
    """The declared digest and size are recomputed here, independently of the reader."""
    paper = corpus_root() / ENTRY_POINT
    registry = _registry()["paper"]
    payload = paper.read_bytes()
    assert _sha256(paper) == registry["sha256"], "the corpus is not the frozen TabM source"
    assert len(payload) == registry["size"]


def test_the_upstream_artifact_is_the_snapshot_the_manifest_declares() -> None:
    """PD reads Result Doctor's bytes; it does not re-run or re-derive them."""
    registry = _registry()["rd_findings"]
    assert _sha256(RD_ARTIFACT) == registry["sha256"]
    assert RD_ARTIFACT.stat().st_size == registry["size"]
    assert registry["rd_version"] == "0.1.0"


def test_the_status_matrix_is_the_frozen_one(findings: list[RuleFinding]) -> None:
    assert statuses(findings) == FROZEN_MATRIX


def test_the_tally_and_the_finding_count_are_frozen(findings: list[RuleFinding]) -> None:
    assert dict(Counter(finding.status.value for finding in findings)) == FROZEN_TALLY
    assert len(findings) == sum(FROZEN_TALLY.values()) == 32


def test_pd003_agrees_with_the_paper_s_own_printed_cell(findings: list[RuleFinding]) -> None:
    """C6 is the paper's Adult `# Train` cell, addressed by column and row, printed with `$26\\,048$`."""
    row = next(f for f in findings if f.rule_id == "PD003" and f.target == "C6")
    assert row.status.value == "PASS"
    assert "column=# Train" in row.reason and "row=Adult" in row.reason


def test_pd003_fails_a_real_sentence_declared_against_the_wrong_cell(findings: list[RuleFinding]) -> None:
    """C8 is the negative control: genuine source text, false attribution.

    The manifest layer cannot reject it -- the sentence exists, the anchor exists, the link is
    declared -- so only the cell comparison can say the stated value is not the printed one.
    """
    row = next(f for f in findings if f.rule_id == "PD003" and f.target == "C8")
    assert row.status.value == "FAIL"
    assert "16281" in row.reason and "26048" in row.reason
    assert "round:0" in row.reason, "the declared precision is what licenses the comparison"


def test_pd003_refuses_a_cell_address_with_two_readings(findings: list[RuleFinding]) -> None:
    """C9 names a row a vertical merge prints on two source rows: PD stops, it does not pick."""
    row = next(f for f in findings if f.rule_id == "PD003" and f.target == "C9")
    assert row.status.value == "INCONCLUSIVE"
    assert "more than one reading" in row.reason


def test_pd002_will_not_pass_a_partial_universe(findings: list[RuleFinding]) -> None:
    """C7 states 15 seeds; the aggregation on file lists them but does not close the universe."""
    row = next(f for f in findings if f.rule_id == "PD002" and f.target == "C7")
    assert row.status.value == "INCONCLUSIVE"
    assert "PARTIAL" in row.reason


def test_pd006_is_a_literal_presence_test_and_only_that(findings: list[RuleFinding]) -> None:
    """PD006 asks whether the referenced float prints the number, not whether the number is right."""
    passed = next(f for f in findings if f.rule_id == "PD006" and f.target == "C1")
    failed = next(f for f in findings if f.rule_id == "PD006" and f.target == "C2")
    assert passed.status.value == "PASS" and failed.status.value == "FAIL"
    assert "does not print 8" in failed.reason


def test_pd001_reports_an_unlinked_claim_as_untraceable_not_false(findings: list[RuleFinding]) -> None:
    row = next(f for f in findings if f.rule_id == "PD001" and f.target == "C3")
    assert row.status.value == "INCONCLUSIVE"
    assert "untraceable is not false" in row.reason


def test_pd004_is_not_run_because_no_target_carries_a_comparison(findings: list[RuleFinding]) -> None:
    row = next(f for f in findings if f.rule_id == "PD004")
    assert row.status.value == "NOT_RUN"


def test_the_acceptance_used_only_the_declared_link_bases() -> None:
    """§6: no semantic, numeric-nearness or method-name linker is reachable from this workspace."""
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    bases = {link["link_basis"] for link in document["_links"]}
    assert bases and bases <= ALLOWED_BASES
    assert "AUTHOR_REF_IN_SENTENCE" in bases and "AUDITOR_DECLARED" in bases


def test_the_acceptance_declares_no_schema_key_phase_two_does_not_know() -> None:
    """A new manifest key would be an adapter by another name.

    The keys are read off the validator's own frozen vocabulary rather than a list copied here, so
    the assertion says: everything this workspace declares is something Phase 2 already accepted.
    """
    from paper_doctor import manifest as manifest_module

    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert set(document) <= {"schema_version", "_registry", "_claims", "_floats", "_links"}
    claim_keys: set[str] = set()
    for claim in document["_claims"]:
        claim_keys |= set(claim)
    link_keys: set[str] = set()
    for link in document["_links"]:
        link_keys |= set(link)
    assert claim_keys <= set(manifest_module.CLAIM_FIELDS)
    assert link_keys <= set(manifest_module.LINK_FIELDS)


def test_a_scientific_fail_still_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """§16: the exit code tracks the contract, never the findings. This workspace contains FAILs."""
    assert main(["audit", str(_audit_case(tmp_path))]) == EXIT_OK
    printed = capsys.readouterr().out
    assert "FAIL" in printed


def test_the_json_face_is_byte_identical_across_hash_seeds(tmp_path: Path) -> None:
    manifest = _audit_case(tmp_path)
    blobs = []
    for seed in (0, 1, 424242):
        destination = tmp_path / f"report-{seed}.json"
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(REPO / "src"), PYTHONIOENCODING="utf-8")
        subprocess.run(
            [sys.executable, "-c", _CHILD, str(manifest), str(destination)],
            env=env,
            cwd=str(REPO),
            capture_output=True,
            check=True,
        )
        blobs.append(destination.read_bytes())
    assert blobs[0] == blobs[1] == blobs[2]


def test_the_chain_ledger_still_describes_the_artifacts_it_records() -> None:
    """§11: the ledger is a record of declared references, and this test re-verifies those bytes."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    invocations = ledger["layer_invocations"]
    assert invocations["PD"]["findings_sha256"] == _sha256(WORKSPACE / "pd_findings.json")
    assert invocations["RD"]["artifact_sha256"] == _sha256(RD_ARTIFACT)
    assert ledger["layer_invocations"]["PD"]["adapters_written_for_tabm"] == 0
    assert invocations["RD"]["rd_code_modified"] is False and invocations["RD"]["rd_rules_added"] == 0
    assert invocations["ED"]["ed_code_modified"] is False
    assert invocations["DD"]["dd_code_modified"] is False and invocations["DD"]["adapters_written_for_tabm"] == 0
    assert ledger["acceptance_target"]["paper_source"]["entry_point_sha256"] == _registry()["paper"]["sha256"]
    assert [chain["chain_id"] for chain in ledger["chains"]] == [
        "chain-1-adult-four-layers",
        "chain-2-dataset-composition-counts",
        "chain-3-block-addressed-cell",
    ]
    chain_one = ledger["chains"][0]
    assert chain_one["reported_result_id"] == "tabm/adult-seed3/test-score"
    assert chain_one["dataset_id"]
    assert chain_one["experiment_run_id"]


def test_the_ledger_states_every_unknown_left_in_the_chain() -> None:
    """§26: closure is not the default. Each layer's remaining UNKNOWN is named, not smoothed over."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    where = {entry["where"] for entry in ledger["unknowns"]}
    assert any("PD002" in spot for spot in where)
    assert any("ED" in spot for spot in where)
    assert ledger["searched_not_observed"], "a hypothesized-but-unfound failure mode must be recorded"
