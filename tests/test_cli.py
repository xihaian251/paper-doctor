"""Phase 0 §22 + Phase 2 §10-§12: the CLI is the API, not a second implementation.

The one failure mode this file exists to catch is drift: the command line filtering, reordering,
summarising or re-judging what `audit_manifest` returned. So the assertions compare the CLI's two
outputs -- the text face and the `--json` bytes -- against the same `RuleFinding` list the library
API produces, and check that the exit code tracks the *contract*, never the *findings*.

Phase 2 adds three things to hold apart: the listing's declared fields come from the manifest and
must not leak into the payload; a directory argument resolves to one fixed name and is never
searched; and both faces are byte-identical across interpreters with different hash seeds.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from support import claim, document, float_anchor, line_of, link, write_case

from paper_doctor import manifest as manifest_module
from paper_doctor.audit import audit_manifest, bundle_from_manifest
from paper_doctor.cli import EXIT_INPUT_ERROR, EXIT_OK, claim_columns, main, manifest_path, render_text
from paper_doctor.manifest import MANIFEST_NAME
from paper_doctor.rules import RULE_IDS
from paper_doctor.status import RuleStatus, canonical_json

REPO = Path(__file__).resolve().parents[1]

PROSE = "Ours reaches $0.99$ as shown in Table~\\ref{tab:one}."
PAPER = document(
    "\\begin{table}\\caption{First}\\label{tab:one}"
    "\\begin{tabular}{|l|c|}\\hline A & 0.42 \\\\\\hline\\end{tabular}\\end{table}",
    "\\begin{table}\\caption{Second}\\label{tab:two}"
    "\\begin{tabular}{|l|c|}\\hline A & 0.99 \\\\\\hline\\end{tabular}\\end{table}",
    PROSE,
)

CASE = dict(
    paper=PAPER,
    findings=[],
    claims=[claim(PAPER, "C1", PROSE, form="NUMERIC_ATTRIBUTION", links=["L1"])],
    floats=[float_anchor("tab:one", float_id="tab-one"), float_anchor("tab:two", float_id="tab-two")],
    links=[link("L1", "C1", "FLOAT", "tab-one", link_basis="AUTHOR_REF_IN_SENTENCE")],
)


def _api_findings(tmp_path: Path, name: str = "cli"):
    manifest = write_case(tmp_path / name, **CASE)
    return manifest, audit_manifest(manifest)


def test_a_misattributed_reference_fails_and_the_command_still_exits_zero(tmp_path: Path) -> None:
    """Finding an inconsistency is the tool working. Exit 0 means "the audit ran", whatever it said."""
    manifest, findings = _api_findings(tmp_path)
    assert main(["audit", str(manifest)]) == EXIT_OK
    assert [f.status for f in findings if f.rule_id == "PD006"] == [RuleStatus.FAIL]


def test_the_json_report_is_the_api_findings_verbatim(tmp_path: Path) -> None:
    """No drift: `--json` writes exactly `canonical_json(audit_manifest(...))` -- same findings,
    same order, no extra fields, nothing dropped."""
    manifest, findings = _api_findings(tmp_path)
    report = tmp_path / "report.json"
    assert main(["audit", str(manifest), "--json", str(report)]) == EXIT_OK
    assert report.read_bytes().decode("utf-8") == canonical_json(findings) + "\n"
    rows = json.loads(report.read_text(encoding="utf-8"))
    assert [row["rule_id"] for row in rows] == [f.rule_id for f in findings]
    assert [row["target"] for row in rows] == [f.target for f in findings]


def test_the_text_face_prints_one_block_per_finding_in_canonical_order(tmp_path: Path) -> None:
    """The table view may re-sort for readability, but it may not summarise away a finding."""
    _, findings = _api_findings(tmp_path)
    text = render_text(findings)
    header = re.compile(r"^(PD\d{3})\s+(PASS|FAIL|INCONCLUSIVE|NOT_APPLICABLE|NOT_RUN)\s+(\S+)")
    listed = [header.match(line) for line in text.splitlines() if header.match(line)]
    assert len(listed) == len(findings)
    assert [(m.group(1), m.group(3)) for m in listed] == [
        (f.rule_id, f.target) for f in sorted(findings, key=lambda f: (f.rule_id, f.target))
    ]


def test_the_census_counts_findings_and_judges_nothing(tmp_path: Path) -> None:
    """The closing block is a count per status, and no aggregate exists anywhere in the output:
    no score, no paper verdict, no reliability claim."""
    _, findings = _api_findings(tmp_path)
    text = render_text(findings)
    counts = dict(line.split(": ") for line in text.rstrip().splitlines()[-5:])
    assert set(counts) == {s.value for s in RuleStatus}
    assert sum(int(v) for v in counts.values()) == len(findings)
    for forbidden in ("score", "verdict", "reliable", "unreliable", "cherry", "grade", "recommend"):
        assert forbidden not in text.lower()


def test_an_unreadable_contract_exits_two_and_prints_the_frozen_message(tmp_path: Path, capsys) -> None:
    """§7: the only failure channel a bad contract uses is `{code} at {where}: {problem}`, and the
    manifest is never silently repaired."""
    case = tmp_path / "bad"
    manifest = write_case(case, **CASE)
    broken = case / "broken.yml"
    broken.write_text(
        manifest.read_text(encoding="utf-8").replace("schema_version: 1", "schema_version: 99"), encoding="utf-8"
    )
    assert main(["audit", str(broken)]) == EXIT_INPUT_ERROR
    message = capsys.readouterr().err.strip()
    assert re.match(r"^P_[A-Z0-9_]+ at \S+: .+$", message), message
    codes = {value for key, value in vars(manifest_module).items() if key.startswith("P_") and isinstance(value, str)}
    assert len(codes) == 12, "§7 freezes exactly twelve P_ codes; a thirteenth is a contract change"
    assert message.split(" at ")[0] in codes
    assert message.startswith(f"{manifest_module.P_SCHEMA_VERSION} at ")


def test_a_directory_argument_never_searches_for_a_manifest(tmp_path: Path) -> None:
    """The one fixed name, or the path as given -- so a typo can never audit a different file."""
    case = tmp_path / "dir"
    manifest = write_case(case, **CASE)
    assert manifest_path(str(case)) == str(manifest)
    assert manifest_path(str(manifest)) == str(manifest)


def test_the_command_line_exposes_the_seven_rules_and_nothing_else(tmp_path: Path) -> None:
    """The API surface the CLI is allowed to reach: `audit_manifest` with the default rule set."""
    _, findings = _api_findings(tmp_path)
    assert len(RULE_IDS) == 7
    assert {f.rule_id for f in findings} <= set(RULE_IDS)
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0


# --- Phase 2 §10-§12: the listing, the resolution rule, and the two faces' determinism --------

PROSE_LINE = line_of(PAPER, PROSE)[0]


def test_the_listing_names_the_seven_fields_the_phase_2_contract_requires(tmp_path: Path) -> None:
    """§11: claim id, claim type, source locator, rule id, status, reason, linked evidence ids.

    The first three are properties of the manifest rather than of a rule, so the listing joins them
    from the bundle at print time -- which is exactly why this test reads them off the declared
    case: a listing that invented a locator or dropped a link id would disagree with the manifest.
    """
    manifest, findings = _api_findings(tmp_path)
    text = render_text(findings, claim_columns(bundle_from_manifest(manifest)))
    for finding in findings:
        assert finding.rule_id in text
        assert finding.status.value in text
        assert finding.target in text
        if finding.reason:
            assert f"reason: {finding.reason}" in text or f"reason: {' '.join(finding.reason.split())}" in text
    assert "form=NUMERIC_ATTRIBUTION" in text
    assert f"locator=paper.tex:{PROSE_LINE}" in text
    assert "links=[L1]" in text


def test_the_listing_adds_nothing_to_the_record_it_prints(tmp_path: Path) -> None:
    """Presentation stays in the terminal: the claim's form, locator and link ids are not smuggled
    into the finding payload, which keeps Contract I-1's eight keys and the JSON face unchanged."""
    manifest, findings = _api_findings(tmp_path)
    payload = canonical_json(findings)
    assert "form=" not in payload and "locator=" not in payload
    render_text(findings, claim_columns(bundle_from_manifest(manifest)))
    assert canonical_json(audit_manifest(manifest)) == payload


def test_a_directory_is_never_searched_for_a_manifest(tmp_path: Path) -> None:
    """§10: a directory means the one fixed name inside it -- not the nearest yaml below it.

    The case here is the mistake the rule exists to prevent: the manifest is present, one folder
    deeper, and a recursive search would silently audit a *different* tree than the user pointed at.
    """
    case = tmp_path / "unsorted"
    manifest = write_case(case, **CASE)
    nested = case / "run7"
    nested.mkdir()
    manifest.rename(nested / MANIFEST_NAME)
    assert main(["audit", str(case)]) == EXIT_INPUT_ERROR
    assert manifest_path(str(case)) == str(case / MANIFEST_NAME)


_CHILD = """
import sys
from paper_doctor.cli import main
raise SystemExit(main(["audit", sys.argv[1], "--json", sys.argv[2]]))
"""


def _cli_in_a_fresh_interpreter(manifest: Path, destination: Path, seed: int) -> bytes:
    env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(REPO / "src"), PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "-c", _CHILD, str(manifest), str(destination)],
        env=env,
        cwd=str(REPO),
        capture_output=True,
        check=True,
    )
    return result.stdout


def test_both_output_faces_are_the_same_bytes_under_every_hash_seed(tmp_path: Path) -> None:
    """§12 + §17: the human listing and the `--json` report are each byte-identical across separate
    interpreters with different `PYTHONHASHSEED` values. The listing is the new surface this round,
    and it is the one assembled from a dict of claim columns."""
    manifest = write_case(tmp_path / "seeded", **CASE)
    texts, reports = [], []
    for seed in (0, 1, 424242):
        report = tmp_path / f"report-{seed}.json"
        texts.append(_cli_in_a_fresh_interpreter(manifest, report, seed))
        reports.append(report.read_bytes())
    assert texts[0] == texts[1] == texts[2], "the listing depends on set or dict iteration order"
    assert reports[0] == reports[1] == reports[2], "the JSON report depends on the hash seed"


def test_an_unexpected_failure_exits_one_and_never_claims_to_have_finished(tmp_path: Path) -> None:
    """§10: exit 1 is reserved for the tool breaking, and exit 0 for the tool finishing.

    A real subprocess is the only honest way to read that contract: `main` deliberately does not
    catch unexpected exceptions, so an uncaught one leaves the interpreter's own code 1.
    """
    manifest = write_case(tmp_path / "broken", **CASE)
    child = f"""
import sys
import paper_doctor.cli as cli
def explode(bundle, rule_ids=None):
    raise RuntimeError("the rules crashed")
cli.audit_bundle = explode
raise SystemExit(cli.main(["audit", {str(manifest)!r}]))
"""
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, "-c", child, str(manifest)], env=env, cwd=str(REPO), capture_output=True)
    assert result.returncode == 1
    assert b"RuntimeError" in result.stderr
    assert result.stdout == b"", "a crashed audit must not print a census"


def test_a_report_path_in_a_missing_directory_exits_two_without_a_traceback(tmp_path: Path, capsys) -> None:
    """Phase 3 §14: the fresh user typed `--json reports/findings.json` before creating `reports/`.

    That is their input, so it belongs on the exit-2 channel with a sentence that says which
    directory to create -- not a `FileNotFoundError` after the audit has already run. Checking the
    destination before the audit is what keeps stdout empty: no census for a report that cannot
    exist, so the run cannot be half-done.
    """
    manifest = write_case(tmp_path / "jsondir", **CASE)
    destination = tmp_path / "missing" / "report.json"
    assert main(["audit", str(manifest), "--json", str(destination)]) == EXIT_INPUT_ERROR
    captured = capsys.readouterr()
    assert captured.out == "", "an audit that never ran must not print a listing"
    assert "Traceback" not in captured.err
    message = captured.err.strip()
    assert message.startswith("paper-doctor: --json cannot write to "), message
    assert "does not exist" in message and "Create it" in message, message
    assert not destination.exists()


def test_a_report_path_with_no_directory_component_still_writes(tmp_path: Path, monkeypatch) -> None:
    """The guard must not reject a bare filename, whose parent is the (existing) working directory."""
    manifest = write_case(tmp_path / "bare", **CASE)
    monkeypatch.chdir(tmp_path)
    assert main(["audit", str(manifest), "--json", "report.json"]) == EXIT_OK
    assert (tmp_path / "report.json").read_text(encoding="utf-8").startswith("[")
