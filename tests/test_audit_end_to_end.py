"""The entry layer end to end: manifest -> bundle -> PD001-PD007 -> CLI bytes.

Nothing here re-tests a rule's judgment; Block D owns the frozen status matrix. What this file
pins is the mechanical promises the rules depend on and cannot state for themselves:

* a declared, resolving link really does reach a float body and produce a PASS;
* a rule that was handed nothing reports `NOT_RUN`, which is a different fact from
  `INCONCLUSIVE` (Phase 1 §23) and must never be confused with it;
* the finding list comes back in canonical `(rule_id, target)` order;
* the CLI keeps the two kinds of "bad" apart: an audit that finds something exits 0, a manifest
  that is not a readable contract exits 2.
"""

from __future__ import annotations

import json
from pathlib import Path

from support import audit, claim, document, float_anchor, link, statuses, write_case

from paper_doctor.audit import audit_manifest, bundle_from_manifest
from paper_doctor.cli import main
from paper_doctor.rules import RULE_IDS
from paper_doctor.status import RuleStatus

TABLE = r"""\begin{table}
\centering
\label{tab:main}
\begin{tabular}{lcc}
\toprule
{} & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
Ours & $0.42$ & $0.10$ \\
Base & $0.40$ & $0.12$ \\
\bottomrule
\end{tabular}
\caption{Head to head.}
\end{table}"""

ATTRIBUTION = r"Ours reaches 0.42 accuracy, see Table \ref{tab:main}."

PAPER = document(TABLE, ATTRIBUTION)

RD002_ROW = {
    "rule_id": "RD002",
    "rule_name": "RD002 spread",
    "target": "mlp/adult",
    "status": "PASS",
    "question": "is the reported spread supported",
    "measurements": {"n_exclusions": 3},
    "evidence": [],
    "reason": "",
}


def test_a_resolved_float_link_produces_a_pass(tmp_path: Path) -> None:
    findings = audit(
        tmp_path / "a",
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION", links=["L1"])],
        floats=[float_anchor("tab:main", float_id="tab-main", quantity_declaration="Acc")],
        links=[link("L1", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc")],
    )
    by_rule = statuses(findings)
    assert by_rule["PD001"]["C1"] == "PASS"
    assert by_rule["PD003"]["C1"] == "PASS"
    assert by_rule["PD006"]["C1"] == "PASS"
    pd003 = next(f for f in findings if f.rule_id == "PD003")
    assert pd003.measurements["claim_value"] == "0.42"
    assert "printed verbatim in table:1" in pd003.reason


def test_a_rule_handed_nothing_reports_not_run_never_inconclusive(tmp_path: Path) -> None:
    """Phase 1 §23: zero targets is not the same fact as insufficient evidence."""
    findings = audit(
        tmp_path / "b",
        paper=PAPER,
        findings=[],
        claims=[],
        floats=[float_anchor("tab:main", float_id="tab-main")],
        links=[],
    )
    assert {f.status for f in findings} == {RuleStatus.NOT_RUN}
    assert {f.rule_id for f in findings} == set(RULE_IDS)
    assert all(f.reason.startswith("no target") for f in findings)
    assert all(f.measurements["n_targets"] == 0 for f in findings)


def test_a_populated_class_with_no_readable_key_is_still_not_run(tmp_path: Path) -> None:
    """PD005 reads claims *and* the upstream census. With no claims but a populated artifact, the
    rule still judged nothing, and its reason names the class that was populated."""
    findings = audit(
        tmp_path / "c",
        paper=PAPER,
        findings=[RD002_ROW],
        claims=[],
        floats=[float_anchor("tab:main", float_id="tab-main")],
        links=[],
    )
    pd005 = next(f for f in findings if f.rule_id == "PD005")
    assert pd005.status is RuleStatus.NOT_RUN
    assert "rd is populated" in pd005.reason
    assert pd005.measurements["n_objects"] == 1


def test_findings_come_back_in_canonical_rule_and_target_order(tmp_path: Path) -> None:
    findings = audit(
        tmp_path / "d",
        paper=PAPER,
        findings=[],
        claims=[
            claim(PAPER, "C2", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION"),
            claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION"),
        ],
        floats=[float_anchor("tab:main", float_id="tab-main")],
        links=[],
    )
    keys = [(f.rule_id, f.target) for f in findings]
    assert keys == sorted(keys)
    assert len(keys) == len(set(keys)), "one rule must not emit two findings for one target"


def test_rule_selection_stays_inside_the_requested_rules(tmp_path: Path) -> None:
    manifest = write_case(
        tmp_path / "e",
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION")],
        floats=[float_anchor("tab:main", float_id="tab-main")],
    )
    selected = audit_manifest(manifest, ["PD001"])
    assert [f.rule_id for f in selected] == ["PD001"]
    assert len(RULE_IDS) == 7


def test_the_cli_exits_zero_on_a_finding_and_writes_canonical_bytes(tmp_path: Path) -> None:
    case = tmp_path / "f"
    manifest = write_case(
        case,
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION")],
        floats=[float_anchor("tab:main", float_id="tab-main")],
    )
    report = case / "report.json"
    assert main(["audit", str(manifest), "--json", str(report)]) == 0
    first = report.read_bytes()
    assert main(["audit", str(manifest), "--json", str(report)]) == 0
    assert report.read_bytes() == first, "the same input must produce the same bytes"
    rows = json.loads(first.decode("utf-8"))
    keys = {"rule_id", "rule_name", "target", "status", "question", "measurements", "evidence", "reason"}
    assert all(set(row) == keys for row in rows)
    assert first.endswith(b"\n") and b"\r\n" not in first


def test_a_directory_argument_resolves_to_the_fixed_manifest_name(tmp_path: Path) -> None:
    write_case(
        tmp_path / "g",
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION")],
        floats=[float_anchor("tab:main", float_id="tab-main")],
    )
    assert main(["audit", str(tmp_path / "g")]) == 0


def test_an_unreadable_contract_exits_two(tmp_path: Path) -> None:
    case = tmp_path / "h"
    manifest = write_case(
        case,
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION")],
        floats=[float_anchor("tab:main", float_id="tab-main")],
    )
    (case / "bad.yml").write_text(
        manifest.read_text(encoding="utf-8").replace("schema_version: 1", "schema_version: 2"), encoding="utf-8"
    )
    assert main(["audit", str(case / "bad.yml")]) == 2


def test_the_audit_root_is_the_directory_holding_the_manifest(tmp_path: Path) -> None:
    """`_registry.paper.root` is relative to the manifest, so a paper kept in a subdirectory is
    still indexed -- otherwise every float rule would report INCONCLUSIVE for the wrong reason."""
    sources = tmp_path / "i" / "sources"
    sources.mkdir(parents=True)
    (sources / "paper.tex").write_text(PAPER, encoding="utf-8", newline="\n")
    manifest = write_case(
        tmp_path / "i",
        paper=PAPER,
        findings=[],
        claims=[claim(PAPER, "C1", "Ours reaches 0.42", form="NUMERIC_ATTRIBUTION", links=["L1"])],
        floats=[float_anchor("tab:main", float_id="tab-main")],
        links=[link("L1", "C1", "FLOAT", "tab-main")],
    )
    text = manifest.read_text(encoding="utf-8").replace(
        "    path: paper.tex", "    root: sources\n    path: paper.tex", 1
    )
    manifest.write_text(text, encoding="utf-8")
    bundle = bundle_from_manifest(manifest)
    assert bundle.index is not None
    assert [record.anchor_id for record in bundle.index.floats] == ["table:1"]
    assert bundle.link_resolution_failure(bundle.links[0]) == ""
