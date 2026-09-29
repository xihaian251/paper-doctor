"""Phase 1 §12/§14/§9/§6 unit-level guards on the rule machinery.

These are the invariants the S1-S13 matrix cannot see because they live below the rule boundary:
a count must always name its unit, a reference's float number must never be read as an attributed
value, a sign must never be dropped from a value, a non-finite upstream measurement must never
compare as a number, and an unreadable tabular stays unrecoverable. Each test is written so that
removing the behaviour it protects turns it red.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from support import audit_manifest_of, claim, document, findings_text, one, rd, write_case

from paper_doctor import rules
from paper_doctor.latex_index import TableGrid, TableRow, parse_table
from paper_doctor.objects import ClaimForm, Qualifier, Quantifier, ScopeDecl, ScopeUnit
from paper_doctor.status import RuleStatus

GRID = TableGrid(
    columns=("Acc", "RMSE"),
    directions=("up", "down"),
    rows=(
        TableRow(label="Ours", cells=("0.42", "0.10")),
        TableRow(label="Base", cells=("0.40", "0.12")),
    ),
)


# --- the count unit is never silent (Phase 1 §12) -----------------------------------------------


def test_every_count_unit_is_declared_from_the_objects_it_belongs_to() -> None:
    """The three units are non-interchangeable, and the declaration is a pure function of the unit."""
    for unit in (ScopeUnit.AGGREGATION, ScopeUnit.REPORTED_CELL, ScopeUnit.COMPARISON_MEMBER):
        record = rules.Claim("C", form=ClaimForm.SCOPE, scope=ScopeDecl(stated_count=3, unit=unit))
        assert rules._unit_of(record) is unit
        assert rules._declare_unit(rules._unit_of(record)) == f"unit={unit.value}"


def test_every_pd002_reason_that_counts_declares_its_unit(tmp_path: Path) -> None:
    """A rule that emits a count without declaring its unit must fail a test -- across all four
    statuses PD002 can reach, not just the one the matrix happens to exercise."""
    pass_text = r"We report nine datasets."
    fail_text = r"We report eight datasets."
    na_text = r"We report several datasets."
    paper = document(pass_text, fail_text, na_text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[rd("RD002", "agg/nine", "PASS", measurements={"n_members": 9})],
            claims=[
                claim(
                    paper,
                    "C-PASS",
                    pass_text,
                    form="SCOPE",
                    links=["L-1"],
                    scope={"stated_count": 9, "universe_status": "RECOVERED"},
                ),
                claim(
                    paper,
                    "C-FAIL",
                    fail_text,
                    form="SCOPE",
                    links=["L-2"],
                    scope={"stated_count": 8, "universe_status": "RECOVERED"},
                ),
                claim(paper, "C-NA", na_text, form="SCOPE", links=["L-3"]),
            ],
            links=[
                {
                    "link_id": "L-1",
                    "claim": "C-PASS",
                    "target_kind": "RD_TARGET",
                    "target_ref": ["RD002", "agg/nine"],
                    "link_basis": "AUDITOR_DECLARED",
                },
                {
                    "link_id": "L-2",
                    "claim": "C-FAIL",
                    "target_kind": "RD_TARGET",
                    "target_ref": ["RD002", "agg/nine"],
                    "link_basis": "AUDITOR_DECLARED",
                },
                {
                    "link_id": "L-3",
                    "claim": "C-NA",
                    "target_kind": "RD_TARGET",
                    "target_ref": ["RD002", "agg/nine"],
                    "link_basis": "AUDITOR_DECLARED",
                },
            ],
        )
    )
    by_target = {f.target: f for f in findings if f.rule_id == "PD002"}
    assert {t: f.status.value for t, f in by_target.items()} == {
        "C-PASS": "PASS",
        "C-FAIL": "FAIL",
        "C-NA": "NOT_APPLICABLE",
    }
    for finding in by_target.values():
        assert "unit=aggregation" in finding.reason
        assert finding.measurements["unit"] == "aggregation"


# --- attributed values vs reference furniture -----------------------------------------------------


def test_literals_excludes_the_referenced_floats_own_number() -> None:
    """`\autoref{tab:3}` and "Table 3" name an object; they do not state a value."""
    assert rules.literals(r"Table 2 shows 0.42 EM, see \autoref{tab:x} and \ref{tab:3}.") == ("0.42",)
    assert rules.literals(r"see \autoref{tab:2} and Table 3") == ()
    assert "main" not in rules.attribution_text(r"see \autoref{tab:main}")
    assert rules.named_float_numbers(r"Tables 3 and 2, Fig. 4") == (3,)
    assert rules.named_float_numbers(r"Table 3 and Table 2 report it") == (3, 2)
    assert rules.ref_labels(r"\autoref{tab:a} \ref{fig:b} \cite{x}") == ("tab:a", "fig:b")


def test_literals_keeps_the_sign_of_a_value() -> None:
    """A dropped minus would make `-0.499` and `0.499` the same string, and PD003 would PASS a
    sign error. A typographic minus is canonicalised rather than treated as a different number,
    which would FAIL a claim whose cell agrees with it."""
    assert rules.literals("the correlation is -0.499 and the mirror reads \u22120.480") == ("-0.499", "-0.480")
    assert rules._number("$-0.499$") == pytest.approx(-0.499)
    assert rules._number("\u22120.499") == pytest.approx(-0.499)
    assert rules._number("Best") is None
    assert rules._number(r"$\mathbf{0.42}\,(\pm 0.01)$") == pytest.approx(0.42)


def test_signed_claim_against_unsigned_cell_is_never_pass(tmp_path: Path) -> None:
    """The end-to-end shape of the defect: the prose prints -0.499, the declared cell prints
    0.499, the quantity identity is declared and the precision is declared => FAIL, not PASS."""
    grid = r"""\begin{table}[t]
\centering
\begin{tabular}{lc}
\toprule
 & Corr\textuparrow \\
\midrule
Ours & $0.499$ \\
\bottomrule
\end{tabular}
\caption{Correlation.}\label{tab:corr}
\end{table}"""
    text = r"Ours reaches -0.499 correlation, see \autoref{tab:corr}."
    paper = document(grid, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[
                {
                    "float_id": "tab-corr",
                    "label": "tab:corr",
                    "quantity_declaration": "Corr",
                    "precision_declaration": "round: 3",
                }
            ],
            links=[
                {
                    "link_id": "L-ANCHOR",
                    "claim": "C1",
                    "target_kind": "FLOAT",
                    "target_ref": "tab-corr",
                    "link_basis": "AUTHOR_REF_IN_SENTENCE",
                    "quantity_identity": "Corr",
                },
                {
                    "link_id": "L-CELL",
                    "claim": "C1",
                    "target_kind": "PROSE",
                    "target_ref": {"path": "paper.tex", "column": "Corr", "row": "Ours"},
                    "link_basis": "AUTHOR_REF_IN_SENTENCE",
                },
            ],
        )
    )
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.FAIL
    assert pd003.measurements["cell_value"] == "0.499"
    assert pd003.measurements["claim_value"] == "-0.499"
    assert pd003.measurements["delta"] == pytest.approx(0.998)


# --- declared precision semantics -------------------------------------------------------------------


def test_precision_reads_only_what_was_declared() -> None:
    assert rules._precision("round: 2") == ("round", 2.0)
    assert rules._precision("precision = 3") == ("round", 3.0)
    assert rules._precision("\u00b1 0.05") == ("tolerance", 0.05)
    assert rules._precision("tolerance: 0.01") == ("tolerance", 0.01)
    # A number that is not a declared precision must never be inferred as one.
    assert rules._precision("two decimal places of confidence") is None
    assert rules._precision("") is None


# --- comparison machinery ----------------------------------------------------------------------------


def _basis_claim(statement: str) -> Any:
    return rules.Claim("C", qualifiers=(Qualifier(kind="comparison_basis", statement=statement),))


def test_column_scope_is_read_from_the_declaration_only() -> None:
    assert rules._columns_in_scope(_basis_claim("per_column"), GRID) == (0, 1)
    assert rules._columns_in_scope(_basis_claim("named_column: RMSE"), GRID) == (1,)
    assert rules._columns_in_scope(_basis_claim("columns: Acc, RMSE"), GRID) == (0, 1)
    # A basis naming a column that does not exist yields no scope, never a nearest match.
    assert rules._columns_in_scope(_basis_claim("named_column: F1"), GRID) == ()
    assert rules._columns_in_scope(_basis_claim("somehow better"), GRID) is None
    assert rules._columns_in_scope(rules.Claim("C"), GRID) is None


def test_direction_comes_from_the_column_arrow_not_from_the_value() -> None:
    assert rules._beats(0.42, 0.40, "up") is True
    assert rules._beats(0.42, 0.40, "down") is False
    # Without a declared direction there is no judgment, not a guess.
    assert rules._beats(0.42, 0.40, "") is None


def test_declared_direction_reads_the_quantity_declaration() -> None:
    assert rules._declared_direction(rules.FloatAnchor(quantity_declaration="RMSE\\textdownarrow")) == "down"
    assert rules._declared_direction(rules.FloatAnchor(quantity_declaration="Acc \u2191")) == "up"
    assert rules._declared_direction(rules.FloatAnchor(quantity_declaration="score")) == ""


def test_universal_and_existential_quantifiers_are_distinguished() -> None:
    assert rules._universally_quantified(rules.Claim("C", quantifier=Quantifier.ALL)) is True
    assert rules._universally_quantified(rules.Claim("C", quantifier=Quantifier.BARE)) is True
    assert rules._universally_quantified(rules.Claim("C", quantifier=Quantifier.SOME)) is False
    assert rules._universally_quantified(rules.Claim("C", quantifier=Quantifier.MOST)) is False


# --- the non-finite boundary (Phase 1 §9) ---------------------------------------------------------------


def test_a_non_finite_upstream_count_is_unknown_never_zero(tmp_path: Path) -> None:
    """RD's canonical JSON can print a bare `NaN`. It parses to a sentinel, must not compare as a
    number, and must not turn the claim into a FAIL."""
    text = r"We report nine datasets."
    paper = document(text)
    payload = findings_text([rd("RD002", "agg/nine", "INCONCLUSIVE", measurements={"n_members": float("nan")})])
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=payload,
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
            links=[
                {
                    "link_id": "L-RD",
                    "claim": "C1",
                    "target_kind": "RD_TARGET",
                    "target_ref": ["RD002", "agg/nine"],
                    "link_basis": "AUDITOR_DECLARED",
                }
            ],
        )
    )
    pd002 = one(findings, "PD002", "C1")
    assert pd002.status is RuleStatus.INCONCLUSIVE
    assert pd002.measurements["n_counts_unknown"] == 1
    assert pd002.measurements["n_counts_divergent"] == 0
    assert "nan" not in pd002.reason.lower() and "0.0" not in pd002.reason


# --- the tabular subset stays a subset -------------------------------------------------------------------


def test_a_two_level_banner_header_is_unrecoverable_not_reparsed() -> None:
    """Phase 1 §6: unresolvable structure is UNKNOWN, never a guess about which column a number
    belongs to."""
    banner = r"""\begin{tabular}{lcc}
\toprule
\multicolumn{2}{c}{Design Choice} & Metric \\
\midrule
A & B & 0.42 \\
\bottomrule
\end{tabular}"""
    assert parse_table(banner) is None
    assert parse_table(r"\begin{tabular}{lc} a & 0.42 \end{tabular}") is None
