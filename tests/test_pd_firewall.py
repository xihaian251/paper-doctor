"""Phase 1 §19: the fourteen firewall rows, one blocking test each.

Phase 0 froze these as the acceptance condition: *"Phase 1 is not accepted unless each line below
is implemented as a test that fails when the forbidden behaviour is introduced."* Each test
therefore asserts the *prohibited* direction explicitly -- that a near value does not become a
link, that a declared link does not become a PASS, that missing evidence does not become a FAIL,
that a validation error never reaches the finding channel -- rather than merely exercising the
happy path. A row is covered by the behaviour being unreachable, so the tests reach for the
forbidden outcome and require it to be absent.

Nothing here adds capability. Rows 10-13 are shape checks over the whole output surface, and row
14 checks that the three out-of-scope capabilities (theorem checking, PDF understanding, LLM cell
topology) have no entry point at all.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from support import (
    audit_manifest_of,
    bundle,
    claim,
    document,
    findings_text,
    float_anchor,
    link,
    one,
    rd,
    write_case,
)

from paper_doctor import rules
from paper_doctor.audit import Bundle, audit_bundle, bundle_from_manifest
from paper_doctor.manifest import MANIFEST_NAME, P_UNRESOLVED_REF, ManifestError, load_manifest
from paper_doctor.objects import LinkBasis, PairingBasis
from paper_doctor.status import RuleFinding, RuleStatus, canonical_json

TABLE = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
Ours & $0.42$ & $0.10$ \\
Base & $0.40$ & $0.12$ \\
\bottomrule
\end{tabular}
\caption{Main results.}\label{tab:main}
\end{table}"""

#: A second float printed immediately after the first: adjacency is what row 4 must not read.
TABLE_ADJACENT = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
Ours & $0.99$ & $0.01$ \\
Base & $0.98$ & $0.02$ \\
\bottomrule
\end{tabular}
\caption{Adjacent ablation.}\label{tab:adjacent}
\end{table}"""

#: A two-level banner header: the subset cannot tell which column a number belongs to.
TABLE_BANNER = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
\multicolumn{2}{c}{Design Choice} & Metric \\
\midrule
A & B & 0.42 \\
\bottomrule
\end{tabular}
\caption{Banner.}\label{tab:banner}
\end{table}"""

ANCHOR = float_anchor("tab:main", float_id="tab-main", quantity_declaration="Acc")
CELL_LINK = link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"})

#: PD001 certifies that a declared link *resolves* and PD006 certifies that a reference points at
#: the float that carries the content. Neither is an agreement claim, and Phase 0 §7.5 bounds the
#: §19.5/§19.6 prohibitions at exactly that: a declaration or an upstream FAIL must not be
#: overwritten by a PASS *about agreement*, and must never be double-reported as a PD FAIL.
AGREEMENT_RULES = ("PD002", "PD003", "PD004", "PD005", "PD007")


def passed(findings: list[RuleFinding]) -> list[RuleFinding]:
    return [f for f in findings if f.status is RuleStatus.PASS and f.rule_id in AGREEMENT_RULES]


def failed(findings: list[RuleFinding]) -> list[RuleFinding]:
    return [f for f in findings if f.status is RuleStatus.FAIL]


def _numeric_case(tmp_path: Path, text: str, *, links: list[dict[str, Any]], paper: str, **fields: Any):
    """One NUMERIC_ATTRIBUTION claim against `paper`, audited end to end."""
    return audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=fields.pop("findings", []),
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="NUMERIC_ATTRIBUTION",
                    links=[link_spec["link_id"] for link_spec in links],
                    **fields,
                )
            ],
            floats=fields.pop("floats", [ANCHOR]),
            links=links,
        )
    )


# ================================================================================================
# 1. LLM semantic guess cannot produce PASS; a heuristic matcher may emit SUGGESTED only.

#: Every way a model could reach the paper's text from this package.
_NETWORK_OR_MODEL_TOKENS = (
    "openai",
    "anthropic",
    "litellm",
    "ollama",
    "huggingface",
    "gpt",
    "claude",
    "transformers",
    "torch",
    "tensorflow",
    "sklearn",
    "numpy",
    "sentence-",
    "embedding",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "subprocess",
)


def test_row1_no_module_in_the_package_can_reach_a_model_or_the_network(tmp_path: Path) -> None:
    """Row 1: there is no code path from a finding to an inference. The prohibition is enforced
    by absence, not by a flag."""
    source_root = Path(__file__).resolve().parents[1] / "src" / "paper_doctor"
    offenders: list[str] = []
    for module in sorted(source_root.glob("*.py")):
        text = module.read_text(encoding="utf-8").lower()
        offenders += [f"{module.name}:{token}" for token in _NETWORK_OR_MODEL_TOKENS if token in text]
    assert offenders == []


def test_row1_a_suggested_pairing_never_reaches_a_verdict(tmp_path: Path) -> None:
    """Row 1: the most a matcher may contribute is `SUGGESTED`, and PD007 must stop there --
    never PASS, and never FAIL either, because a suggestion is not a link."""
    first = r"We reach 0.42 on the main table."
    second = r"The main table shows 0.42."
    paper = document(TABLE, first, second)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[],
            claims=[
                claim(paper, "C1", first, form="NUMERIC_ATTRIBUTION", same_as=[{"claim": "C2", "basis": "suggested"}]),
                claim(paper, "C2", second, form="NUMERIC_ATTRIBUTION", same_as=[{"claim": "C1", "basis": "suggested"}]),
            ],
            floats=[ANCHOR],
            links=[],
        )
    )
    pd007 = one(findings, "PD007", "C1|C2")
    assert pd007.status is RuleStatus.INCONCLUSIVE
    assert "SUGGESTED only" in pd007.reason
    assert pd007.measurements["pairing_basis"] == ("suggested",)


def test_row1_the_link_origin_vocabulary_has_no_inference_member() -> None:
    """Row 1: an inferred origin cannot even be declared, so it cannot reach any rule."""
    assert {member.value for member in LinkBasis} == {
        "AUTHOR_REF_IN_SENTENCE",
        "AUTHOR_NAMED_FLOAT",
        "AUDITOR_DECLARED",
    }
    assert {member.value for member in PairingBasis} == {"declared", "suggested"}


# 2. Numerical closeness cannot create a link or a PASS. (covered in the two tests below: a near
# value in a *declared* cell is not a match, and a matching value in an *undeclared* float is not
# a link.)


def test_row2_closeness_is_not_a_pass(tmp_path: Path) -> None:
    """Row 2: the claim says 0.421 and the declared cell says 0.42. Nothing about the link is
    missing -- the link is declared and the quantity is declared equal -- so the only thing that
    could make this agree is a tolerance, and none was declared."""
    text = r"Ours reaches 0.421 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = _numeric_case(
        tmp_path,
        text,
        paper=paper,
        links=[
            link("L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc"),
            CELL_LINK,
        ],
    )
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    assert "closeness is not a PASS" in pd003.reason
    assert pd003.measurements["delta"] == pytest.approx(0.001)


def test_row2_a_value_found_by_searching_is_not_a_link(tmp_path: Path) -> None:
    """Row 2: the number the claim states is printed verbatim in the document. PD still has no
    link to it, so the value cannot support a PASS or a mismatch."""
    text = r"Ours reaches 0.42 accuracy."
    paper = document(TABLE, text)
    built = bundle(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=[])],
        floats=[ANCHOR],
        links=[],
    )
    record = one(audit_bundle(built), "PD003", "C1")
    assert record.status is RuleStatus.INCONCLUSIVE
    assert built.index is not None
    # The document *does* print it -- the linker simply is not allowed to look for that.
    assert built.floats_with_literal("0.42") == ("table:1",)
    assert built.anchors_for(_claim_of(built, "C1")) == ()


def _claim_of(built: Bundle, claim_id: str) -> Any:
    found = built.claim_by_id(claim_id)
    assert found is not None
    return found


# 3. Filename/path similarity cannot create a link.


def test_row3_a_similarly_named_file_is_not_the_declared_one(tmp_path: Path) -> None:
    """Row 3: the link names `tables/results.tex`; the corpus carries `tables/result.tex`, which
    prints the very number. Similarity must not close the gap."""
    text = r"Ours reaches 0.42 accuracy."
    paper = document(TABLE, text)
    (tmp_path / "tables").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tables" / "result.tex").write_text("Ours & 0.42 \\\\\n", encoding="utf-8")
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-PROSE"])],
            floats=[ANCHOR],
            links=[
                link(
                    "L-PROSE",
                    "C1",
                    "PROSE",
                    {"path": "tables/results.tex", "line": 1, "text": "0.42"},
                )
            ],
        )
    )
    pd001 = one(findings, "PD001", "C1")
    assert pd001.status is RuleStatus.INCONCLUSIVE
    assert pd001.measurements["target_resolved"] is False
    assert "tables/results.tex does not exist" in pd001.reason
    assert one(findings, "PD003", "C1").status is RuleStatus.INCONCLUSIVE
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []


# 4. Table/float adjacency or column-arrow alignment cannot create a link.


def test_row4_the_float_next_to_the_sentence_is_not_the_support(tmp_path: Path) -> None:
    """Row 4: two floats sit back to back, the claim's number is printed in the first one, and the
    first one is the only table in the vicinity. Adjacency yields nothing: the claim has no anchor,
    and the rule says so instead of judging a relation it was not given."""
    text = r"Ours reaches 0.42 accuracy."
    paper = document(TABLE, TABLE_ADJACENT, text)
    built = bundle(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=[])],
        floats=[ANCHOR, float_anchor("tab:adjacent", float_id="tab-adjacent", quantity_declaration="Acc")],
        links=[],
    )
    findings = audit_bundle(built)
    assert built.anchors_for(_claim_of(built, "C1")) == ()
    assert one(findings, "PD001", "C1").status is RuleStatus.INCONCLUSIVE
    assert one(findings, "PD003", "C1").status is RuleStatus.INCONCLUSIVE
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []
    # The numbering itself is deterministic and document-ordered -- that is the only automation.
    assert built.index is not None
    assert [(f.anchor_id, f.labels) for f in built.index.floats] == [
        ("table:1", ("tab:main",)),
        ("table:2", ("tab:adjacent",)),
    ]


# 5. DECLARED-only support cannot auto-PASS any rule.


def test_row5_an_explicit_link_unlocks_judgment_but_not_agreement(tmp_path: Path) -> None:
    """Row 5: the prose and the printed cell are literally the same string, the float is declared,
    and the link is `AUDITOR_DECLARED` with no quantity identity. That cannot PASS: declaring which
    evidence to look at is not evidence that they agree."""
    text = r"Ours reaches 0.42 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    declared = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[ANCHOR],
            links=[
                link("L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUDITOR_DECLARED"),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
            ],
        )
    )
    pd003 = one(declared, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    assert "quantity identity is undeclared" in pd003.reason
    assert passed(declared) == []
    # What the declaration alone can earn is resolution and attribution -- nothing about agreement.
    assert {f.rule_id for f in declared if f.status is RuleStatus.PASS} <= {"PD001", "PD006"}

    # With the quantity declared on both sides the same case does PASS: the firewall is exactly
    # the declaration, not the link basis.
    identified = audit_manifest_of(
        write_case(
            tmp_path / "identified",
            paper=paper,
            findings=[],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[ANCHOR],
            links=[
                link(
                    "L-ANCHOR",
                    "C1",
                    "FLOAT",
                    "tab-main",
                    link_basis="AUDITOR_DECLARED",
                    quantity_identity="Acc",
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
            ],
        )
    )
    assert one(identified, "PD003", "C1").status is RuleStatus.PASS


# 6. A downstream RD FAIL cannot be ignored, downgraded, or overwritten by a PD PASS.


def test_row6_an_upstream_failure_is_never_overwritten(tmp_path: Path) -> None:
    """Row 6: the cell agrees with the prose string-for-string, and upstream RD001 says that cell
    does not match its own recomputation. PD must neither PASS the relation nor restate RD's FAIL:
    it reports its own inability to decide."""
    text = r"Ours reaches 0.42 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[rd("RD001", "cell/acc-ours", "FAIL", reason="reported center does not match the recomputation")],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL", "L-RD"])],
            floats=[ANCHOR],
            links=[
                link(
                    "L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc"
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
                link("L-RD", "C1", "RD_TARGET", ["RD001", "cell/acc-ours"]),
            ],
        )
    )
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    assert "downstream RD001 on cell/acc-ours is FAIL" in pd003.reason
    assert "PD does not upgrade upstream certainty" in pd003.reason
    assert passed(findings) == []
    # §7.5's boundary stated positively: the only PASSes on this claim are about resolution and
    # attribution, the two relations an upstream cell failure does not touch.
    assert {f.rule_id for f in findings if f.status is RuleStatus.PASS} <= {"PD001", "PD006"}
    assert failed(findings) == []
    # PD never speaks with RD's voice: no finding is filed under an upstream rule id.
    assert [f.rule_id for f in findings if f.rule_id.startswith("RD")] == []


# 7. A downstream RD INCONCLUSIVE cannot be presented as certainty in either direction.


def test_row7_an_undecided_upstream_count_supports_neither_pass_nor_fail(tmp_path: Path) -> None:
    """Row 7: upstream RD002 is INCONCLUSIVE and its member count differs from the stated nine.
    A disagreement over uncertified evidence cannot become a FAIL, and cannot become a PASS."""
    text = r"We report nine datasets."
    paper = document(text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[rd("RD002", "agg/nine", "INCONCLUSIVE", measurements={"n_members": 8}, reason="binding unknown")],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={"stated_count": 9, "universe_status": "RECOVERED"},
                )
            ],
            links=[link("L-RD", "C1", "RD_TARGET", ["RD002", "agg/nine"])],
        )
    )
    assert one(findings, "PD002", "C1").status is RuleStatus.INCONCLUSIVE
    assert "upstream is INCONCLUSIVE" in one(findings, "PD002", "C1").reason
    # Neither direction: on an undecided count no substantive rule certifies or condemns.
    assert passed(findings) == []
    assert failed(findings) == []


# 8. Missing evidence cannot become FAIL.


def test_row8_every_shape_of_missing_evidence_stays_inconclusive(tmp_path: Path) -> None:
    """Row 8: four different ways the evidence can be absent -- no link at all, a locator past the
    end of the file, a float that never closes, an upstream artifact that carries no such finding.
    None of them is a mismatch, so none of them may print FAIL."""
    text = r"Ours reaches 0.42 accuracy."
    shapes: list[tuple[str, str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]] = [
        ("no link", document(TABLE, text), [ANCHOR], [], []),
        (
            "locator past the end of the file",
            document(TABLE, text),
            [ANCHOR],
            [link("L-PROSE", "C1", "PROSE", {"path": "paper.tex", "line": 9999, "text": "0.42"})],
            ["L-PROSE"],
        ),
        (
            "unterminated float",
            document(TABLE.replace(r"\end{table}", ""), text),
            [float_anchor("tab:main", float_id="tab-open", quantity_declaration="Acc")],
            [link("L-OPEN", "C1", "FLOAT", "tab-open", quantity_identity="Acc")],
            ["L-OPEN"],
        ),
    ]
    for name, paper, floats, links, spec_ids in shapes:
        findings = audit_manifest_of(
            write_case(
                tmp_path / name,
                paper=paper,
                findings=[],
                claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=spec_ids)],
                floats=floats,
                links=links,
            )
        )
        assert failed(findings) == [], name
        assert one(findings, "PD001", "C1").status is RuleStatus.INCONCLUSIVE, name
        assert one(findings, "PD003", "C1").status is RuleStatus.INCONCLUSIVE, name

    # An upstream artifact that carries no RD002 finding at all: the scope cannot be bound.
    scope_text = r"We report nine datasets."
    empty_paper = document(scope_text)
    findings = audit_manifest_of(
        write_case(
            tmp_path / "empty-artifact",
            paper=empty_paper,
            findings=[],
            claims=[
                claim(
                    empty_paper,
                    "C1",
                    scope_text,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={"stated_count": 9, "universe_status": "RECOVERED"},
                )
            ],
            links=[link("L-RD", "C1", "RD_TARGET", ["RD002", "agg/absent"], link_basis="AUDITOR_DECLARED")],
        )
    )
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []
    assert one(findings, "PD001", "C1").status is RuleStatus.INCONCLUSIVE
    assert one(findings, "PD002", "C1").status is RuleStatus.INCONCLUSIVE

    # A claim whose declared cell address is not in the table: the address is wrong, the paper
    # is not.
    banner_text = r"Ours reaches 0.42 accuracy, see \autoref{tab:banner}."
    banner_paper = document(TABLE_BANNER, banner_text)
    findings = audit_manifest_of(
        write_case(
            tmp_path / "banner",
            paper=banner_paper,
            findings=[],
            claims=[claim(banner_paper, "C1", banner_text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[float_anchor("tab:banner", float_id="tab-banner", quantity_declaration="Metric")],
            links=[
                link(
                    "L-ANCHOR",
                    "C1",
                    "FLOAT",
                    "tab-banner",
                    link_basis="AUTHOR_REF_IN_SENTENCE",
                    quantity_identity="Metric",
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Metric", "row": "A"}),
            ],
        )
    )
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []
    assert "unrecoverable" in one(findings, "PD003", "C1").reason


# 9. A validation error cannot be reported as a scientific finding.


def test_row9_a_broken_contract_exits_rather_than_findings(tmp_path: Path) -> None:
    """Row 9: the declared paper digest does not match the bytes on disk. That is not a fact about
    the paper; it is a manifest that cannot be read. No RuleFinding may be produced."""
    text = r"Ours reaches 0.42 accuracy."
    paper = document(TABLE, text)
    manifest = write_case(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=[])],
        floats=[ANCHOR],
        links=[],
    )
    document_manifest = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    document_manifest["_registry"]["paper"]["sha256"] = "0" * 64
    manifest.write_text(yaml.safe_dump(document_manifest, sort_keys=False), encoding="utf-8")

    with pytest.raises(ManifestError) as raised:
        audit_manifest_of(manifest)
    error = raised.value
    assert isinstance(error, ManifestError)
    assert not isinstance(error, RuleFinding)
    assert error.code == P_UNRESOLVED_REF
    assert str(error).startswith(f"{P_UNRESOLVED_REF} at _registry/paper/sha256: ")
    assert "does not match the observed" in str(error)


def test_row9_the_cli_keeps_the_two_kinds_of_bad_apart(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Row 9 again, at the only user-facing edge: a scientific FAIL exits 0 while a manifest that
    cannot be read exits 2 and never prints a finding."""
    from paper_doctor.cli import EXIT_INPUT_ERROR, EXIT_OK, main

    ok_text = r"We report nine datasets."
    good = write_case(
        tmp_path / "good",
        paper=document(ok_text),
        findings=[rd("RD002", "agg/nine", "PASS", measurements={"n_members": 3})],
        claims=[
            claim(
                document(ok_text),
                "C1",
                ok_text,
                form="SCOPE",
                links=["L-RD"],
                scope={"stated_count": 9, "universe_status": "RECOVERED"},
            )
        ],
        links=[link("L-RD", "C1", "RD_TARGET", ["RD002", "agg/nine"])],
    )
    assert main(["audit", str(good)]) == EXIT_OK
    printed = capsys.readouterr().out
    assert "FAIL" in printed and "PD002" in printed

    bad = tmp_path / "bad" / MANIFEST_NAME
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("schema_version: 1\n", encoding="utf-8")
    assert main(["audit", str(bad)]) == EXIT_INPUT_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert " at " in captured.err


# 10. No paper score, no composite index, no ranking of papers.


def test_row10_the_output_surface_has_no_number_about_the_paper_as_a_whole(tmp_path: Path) -> None:
    """Row 10: every number in the output is a measurement about one target of one rule. There is
    no aggregate key, no total, no ranking -- and the record shape cannot carry one."""
    numeric = r"Ours reaches 0.45 accuracy, see \autoref{tab:main}."
    scope = r"We report nine datasets."
    paper = document(TABLE, numeric, scope)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[rd("RD002", "agg/nine", "PASS", measurements={"n_members": 9})],
            claims=[
                claim(paper, "C1", numeric, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"]),
                claim(
                    paper,
                    "C2",
                    scope,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={"stated_count": 9, "universe_status": "RECOVERED"},
                ),
            ],
            floats=[ANCHOR],
            links=[
                link(
                    "L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc"
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
                link("L-RD", "C2", "RD_TARGET", ["RD002", "agg/nine"]),
            ],
        )
    )
    assert {key for finding in findings for key in finding.to_dict()} == {
        "rule_id",
        "rule_name",
        "target",
        "status",
        "question",
        "measurements",
        "evidence",
        "reason",
    }
    payload = canonical_json(findings)
    for forbidden in ("score", "rank", "total", "aggregate", "sum", "mean", "confidence", "weight"):
        assert f'"{forbidden}' not in payload, forbidden
    # The census in the text renderer counts findings; it does not grade the paper.
    from paper_doctor.cli import render_text

    lines = render_text(findings).rstrip().splitlines()
    assert lines[-5].startswith("PASS:") and all(": " in line for line in lines[-5:])


# 11-13. No accept/reject prediction, no novelty or literature-truth judgment, no accusation of
# anything. The scan is over every string the tool can emit, from a battery that touches all
# seven rules and the states in between.


def _battery(tmp_path: Path) -> list[RuleFinding]:
    numeric = r"Ours reaches 0.45 accuracy, see \autoref{tab:main}."
    scope = r"We report results over nine datasets."
    comparison = r"Ours beats Base on every metric in \autoref{tab:main}."
    qualification = r"All aggregations keep every member, see \autoref{tab:main}."
    reference = r"Table 3 reports the ablation."
    paper = document(TABLE, numeric, scope, comparison, qualification, reference)
    return audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[rd("RD002", "agg/nine", "PASS", measurements={"n_members": 9, "n_exclusions": 0})],
            claims=[
                claim(paper, "C1", numeric, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"]),
                claim(
                    paper,
                    "C2",
                    scope,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={"stated_count": 9, "universe_status": "RECOVERED", "members": ["a"]},
                ),
                claim(
                    paper,
                    "C3",
                    comparison,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    quantifier="all",
                    links=["L-ANCHOR-3"],
                    qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
                ),
                claim(paper, "C4", qualification, form="QUALIFICATION", links=["L-RD-4", "L-ANCHOR-4"]),
                claim(paper, "C5", reference, form="REFERENCE_ATTRIBUTION", links=["L-ANCHOR-5"]),
            ],
            floats=[ANCHOR],
            links=[
                link(
                    "L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc"
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
                link("L-RD", "C2", "RD_TARGET", ["RD002", "agg/nine"]),
                link("L-ANCHOR-3", "C3", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE"),
                link("L-RD-4", "C4", "RD_TARGET", ["RD002", "agg/nine"]),
                link("L-ANCHOR-4", "C4", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE"),
                link("L-ANCHOR-5", "C5", "FLOAT", "tab-main", link_basis="AUTHOR_NAMED_FLOAT"),
            ],
        )
    )


def _emittable_strings() -> list[str]:
    out = [status.value for status in RuleStatus]
    out += [member.value for member in PairingBasis] + [member.value for member in LinkBasis]
    out += list(rules.NAME.values()) + list(rules.QUESTION.values()) + list(rules.RULE_IDS)
    return out


@pytest.mark.parametrize(
    "forbidden",
    ["accept", "reject", "publishable", "survive review", "would this survive", "recommend", "verdict"],
)
def test_row11_no_decision_about_the_paper_itself(tmp_path: Path, forbidden: str) -> None:
    """Row 11: PD judges one relation at a time. It never speaks about whether the paper should be
    accepted, and the word does not appear in anything it can emit."""
    findings = _battery(tmp_path)
    assert [forbidden in f.reason.lower() for f in findings].count(True) == 0
    assert [forbidden in text.lower() for text in _emittable_strings()].count(True) == 0


@pytest.mark.parametrize("forbidden", ["novel", "novelty", "prior art", "first to", "literature", "bibliograph"])
def test_row12_no_novelty_or_literature_truth_judgment(tmp_path: Path, forbidden: str) -> None:
    """Row 12: citation strings are removed from the auditable text, never verified. A claim whose
    only citation key resolves to nothing is still judged only on its declared evidence."""
    text = r"As \citet{smith2020} showed, ours reaches 0.42 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = _numeric_case(
        tmp_path,
        text,
        paper=paper,
        links=[
            link("L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc"),
            CELL_LINK,
        ],
    )
    assert one(findings, "PD003", "C1").status is RuleStatus.PASS
    assert [f for f in findings if forbidden in f.reason.lower()] == []
    assert [forbidden in text.lower() for text in _emittable_strings()] == [False] * len(_emittable_strings())


#: Accusation vocabulary. The bare word "integrity" is deliberately *not* in this list: PD006's
#: frozen Phase 0 name is "Result Reference Integrity", which is about whether a `\ref` points at
#: the float that carries the content -- a relation, not a claim about the authors. The scan
#: therefore uses the accusation phrases, and a separate assertion below pins the frozen name so a
#: future edit cannot turn it into a research-integrity signal.
ACCUSATION_TOKENS = (
    "misconduct",
    "cherry",
    "fraud",
    "plagiar",
    "dishonest",
    "fabricat",
    "p-hack",
    "integrity violation",
    "data integrity",
    "research integrity",
    "breach",
)


@pytest.mark.parametrize("forbidden", ACCUSATION_TOKENS)
def test_row13_no_accusation_anywhere_in_the_output_surface(tmp_path: Path, forbidden: str) -> None:
    """Row 13: not in a reason, not in a question, not in a rule name, not in an enum member."""
    findings = _battery(tmp_path)
    for finding in findings:
        for field in (finding.rule_id, finding.rule_name, finding.target, finding.question, finding.reason):
            assert forbidden not in str(field).lower()
    for text in _emittable_strings():
        assert forbidden not in text.lower()
    # Enum *names* too: an integrity signal cannot be a state of this tool.
    names = [member.name for member in RuleStatus] + [member.name for member in PairingBasis]
    names += [member.name for member in LinkBasis]
    assert [forbidden in name.lower() for name in names] == [False] * len(names)


def test_row13_pd006_keeps_its_frozen_referential_name() -> None:
    """Row 13, the other side: the one place this tool says "integrity" is PD006's name, and it is
    the Phase 0 string, not a watermark on the authors."""
    assert rules.NAME["PD006"] == "Result Reference Integrity"
    assert rules.QUESTION["PD006"] == (
        "does the reference in the claim resolve to the float that actually carries the attributed content?"
    )
    assert not any(token in rules.NAME["PD006"].lower() for token in ACCUSATION_TOKENS)


# 14. No theorem/proof verification; no automatic full-PDF semantic understanding; no LLM
# inference about cell topology. Unrecoverable identity is INCONCLUSIVE.


def test_row14_a_pdf_root_gets_no_index_and_no_guess(tmp_path: Path) -> None:
    """Row 14: a non-`.tex` root has no float numbering to recover. The index is None, the rules
    say so, and nothing about the document is inferred from the file name or from a rendered page."""
    text = r"Ours reaches 0.42 accuracy."
    paper = document(TABLE, text)
    manifest = write_case(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR"])],
        floats=[ANCHOR],
        links=[
            link("L-ANCHOR", "C1", "FLOAT", "tab-main", link_basis="AUTHOR_REF_IN_SENTENCE", quantity_identity="Acc")
        ],
    )
    raw = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.7\n")
    raw["_registry"]["paper"] = {"path": "paper.pdf"}
    manifest.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    built = bundle_from_manifest(manifest)
    assert built.index is None
    findings = audit_bundle(built)
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    assert "not recoverable" in pd003.reason
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []


def test_row14_there_is_no_surface_for_a_theorem_or_a_proof(tmp_path: Path) -> None:
    """Row 14: the contract cannot even express the request. A theorem field is an unknown key,
    so it is a validation error rather than a rule that quietly does nothing."""
    text = r"Theorem 1 proves the bound."
    paper = document(text)
    manifest = write_case(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", theorem="the bound holds")],
        floats=[],
        links=[],
    )
    with pytest.raises(ManifestError) as raised:
        load_manifest(manifest)
    assert "unknown key(s): theorem" in str(raised.value)
    assert rules.RULE_IDS == ("PD001", "PD002", "PD003", "PD004", "PD005", "PD006", "PD007")


def test_row14_an_unreadable_cell_topology_is_unknown_not_assigned(tmp_path: Path) -> None:
    """Row 14: a two-level banner header makes the column of a number undecidable. PD reports the
    grid as unrecoverable instead of guessing which column 0.42 sits in."""
    from paper_doctor.latex_index import parse_table, tabular_interior

    assert tabular_interior(TABLE_BANNER) is not None
    assert parse_table(TABLE_BANNER) is None

    text = r"A reaches 0.42 metric, see \autoref{tab:banner}."
    paper = document(TABLE_BANNER, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[float_anchor("tab:banner", float_id="tab-banner", quantity_declaration="Metric")],
            links=[
                link(
                    "L-ANCHOR",
                    "C1",
                    "FLOAT",
                    "tab-banner",
                    link_basis="AUTHOR_REF_IN_SENTENCE",
                    quantity_identity="Metric",
                ),
                link("L-CELL", "C1", "PROSE", {"path": "paper.tex", "column": "Metric", "row": "A"}),
            ],
        )
    )
    assert one(findings, "PD003", "C1").status is RuleStatus.INCONCLUSIVE
    assert [f for f in findings if f.status is RuleStatus.FAIL] == []


# --- the shape of an empty artifact, reused by rows 2 and 8 ----------------------------------------


def test_row2_an_upstream_artifact_with_nothing_in_it_creates_no_links(tmp_path: Path) -> None:
    """Row 2 (the artifact side): `findings.json` present and empty is not a set of upstream
    targets to be near."""
    text = r"We report nine datasets."
    paper = document(text)
    built = bundle(
        tmp_path,
        paper=paper,
        findings=findings_text([]),
        claims=[
            claim(
                paper,
                "C1",
                text,
                form="SCOPE",
                links=["L-RD"],
                scope={"stated_count": 9, "universe_status": "RECOVERED"},
            )
        ],
        links=[link("L-RD", "C1", "RD_TARGET", ["RD002", "agg/nine"])],
    )
    assert built.rd is not None and built.rd.findings == ()
    assert built.exclusion_universe() == ()
    assert audit_bundle(built) and one(audit_bundle(built), "PD002", "C1").status is RuleStatus.INCONCLUSIVE


def test_row9b_the_declared_paper_size_is_verified_through_the_manifest(tmp_path: Path) -> None:
    """Row 9's size clause measured through the manifest, not only through the loader.

    Phase 3's mutation audit deleted the declared-size comparison in `_registry/paper` and the
    whole Phase 1-2 suite stayed green: the clause was enforced but unobserved. The bytes audited
    must be the bytes committed to, so a manifest that names the right digest and the wrong byte
    count is not a contract at all and may not produce a single finding.
    """
    text = r"We report nine datasets."
    paper = document(text)
    manifest = write_case(
        tmp_path,
        paper=paper,
        findings=[],
        claims=[claim(paper, "C1", text, form="SCOPE", links=[])],
        floats=[],
        links=[],
    )
    declared = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    declared["_registry"]["paper"]["size"] += 1
    manifest.write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")

    with pytest.raises(ManifestError) as raised:
        audit_manifest_of(manifest)
    assert raised.value.code == P_UNRESOLVED_REF
    assert raised.value.where == "_registry/paper/size"
    assert "declared size" in raised.value.problem


def test_row9c_the_declared_upstream_size_reaches_the_reader(tmp_path: Path) -> None:
    """Row 9's other half: the wiring that carries the declared upstream size into the reader.

    `load_rd_findings` checks its own argument, so a test that calls it directly cannot see the
    manifest value being dropped on the way in. Here the artifact keeps its correct digest and
    only the manifest lies about its length, which is catchable at exactly one place.
    """
    text = r"We report nine datasets."
    paper = document(text)
    manifest = write_case(
        tmp_path,
        paper=paper,
        findings=[rd("RD002", "agg/nine", "PASS", measurements={"n_members": 3})],
        claims=[
            claim(
                paper,
                "C1",
                text,
                form="SCOPE",
                links=["L-RD"],
                scope={"stated_count": 9, "universe_status": "RECOVERED"},
            )
        ],
        links=[link("L-RD", "C1", "RD_TARGET", ["RD002", "agg/nine"])],
    )
    declared = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    declared["_registry"]["rd_findings"]["size"] += 1
    manifest.write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")

    with pytest.raises(ManifestError) as raised:
        audit_manifest_of(manifest)
    assert raised.value.code == P_UNRESOLVED_REF
    assert raised.value.where.endswith("/size")
    assert "declared size" in raised.value.problem
