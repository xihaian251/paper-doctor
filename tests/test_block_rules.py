r"""Phase 2 §13, §14, §17: block-addressed rows, judged by the rules that already exist.

Nothing here adds a rule, an object or a validation code. What changes is *which row a rule is
allowed to read* once the source states that a label is printed more than once:

* RTDL Table 4 (`data/table_nn_gbdt.tex`, `tab:nn-gbdt`) prints XGBoost / CatBoost /
  FT-Transformer under two `\multicolumn` group headers, so the sentence at `main.tex:404`
  compares rows each of which is printed twice. Until a block is declared, no cell of that table
  is addressable and PD004 says so instead of picking one.
* The synthetic fixture below was not in Phase 1 and has the same shape on purpose: the block is
  what decides the verdict, and it decides it from `\multicolumn` and `\midrule` alone.

The declaration rides `Qualifier(kind="comparison_block", statement="block=b2")` -- the same free
mechanism `comparison_basis` uses -- because Phase 2 §2 forbids a fourth object and §3 makes the
block key part of the *address*, not of the ontology. A declaration establishes provenance, never
correctness: `block=b9` is a legal string and selects nothing.

Cell values were read off the sources by hand (`data/table_nn_gbdt.tex:9` and `:16`), not taken
from a finding.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from support import audit_manifest_of, claim, document, float_anchor, link, one, write_case, write_real_case

from paper_doctor.audit import audit_manifest
from paper_doctor.status import RuleFinding, RuleStatus

REPO = Path(__file__).resolve().parents[1]
RTDL_ROOT = REPO / "phase0" / "sources" / "2106.11959.tex"
RTDL_ARTIFACT = Path(__file__).resolve().parent / "fixtures" / "rd_findings_rtdl_0.1.0.json"
RTDL_CELLS = "data/table_nn_gbdt.tex"

#: main.tex:404 verbatim. Its own quantifier is "mostly", so the declared claim stays
#: existential: this file is about which row a rule may read, not about strengthening the
#: author's sentence.
TABLE4_SENTENCE = r"the ensemble of \architecture s mostly outperforms the ensembles of GBDT"

TABLE4_ANCHOR = float_anchor("tab:nn-gbdt", float_id="tab-nn-gbdt", quantity_declaration="metrics.test.score")


@pytest.fixture(scope="module")
def rtdl_main() -> str:
    return (RTDL_ROOT / "main.tex").read_text(encoding="utf-8", errors="replace")


def _table4_claims(claim_id: str, block: str) -> list[dict[str, Any]]:
    paper = (RTDL_ROOT / "main.tex").read_text(encoding="utf-8", errors="replace")
    qualifiers: list[dict[str, str]] = [{"kind": "comparison_basis", "statement": "per_column"}]
    if block:
        qualifiers.append({"kind": "comparison_block", "statement": f"block={block}"})
    return [
        claim(
            paper,
            claim_id,
            TABLE4_SENTENCE,
            form="COMPARATIVE",
            path="main.tex",
            fragment_is_text=True,
            predicate="outperforms",
            subjects=["FT-Transformer", "XGBoost"],
            quantifier="most",
            links=[f"L-{claim_id}"],
            qualifiers=qualifiers,
        )
    ]


def _audit_table4(root: Path, claims: list[dict[str, Any]]) -> list[RuleFinding]:
    manifest = write_real_case(
        root,
        audit_root=RTDL_ROOT,
        paper_path="main.tex",
        rd_artifact=RTDL_ARTIFACT,
        claims=claims,
        floats=[TABLE4_ANCHOR],
        links=[link(f"L-{entry['claim_id']}", entry["claim_id"], "FLOAT", "tab-nn-gbdt") for entry in claims],
    )
    return audit_manifest(manifest)


def test_table4_prints_both_subjects_twice_so_no_block_means_no_row(tmp_path: Path) -> None:
    """§17: an ambiguous address is refused, never resolved by "first match" or by nearness."""
    findings = _audit_table4(tmp_path / "noblock", _table4_claims("B1", ""))
    finding = one(findings, "PD004", "B1")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "unit=comparison_member" in finding.reason
    assert "is not an addressable row" in finding.reason
    assert "printed in 2 structural blocks" in finding.reason
    # The reason quotes the structure that separates the two candidate rows.
    assert 'multicolumn group header "Default hyperparameters"' in finding.reason
    assert 'multicolumn group header "Tuned hyperparameters"' in finding.reason


def test_table4_with_a_declared_block_reaches_a_judgment(tmp_path: Path) -> None:
    findings = _audit_table4(tmp_path / "b1", _table4_claims("B2", "b1"))
    finding = one(findings, "PD004", "B2")
    assert finding.status is RuleStatus.PASS
    assert finding.measurements["n_columns_in_scope"] == 11
    # data/table_nn_gbdt.tex:7-9 -- FT-Transformer is better on ten of the eleven columns, and
    # AD (0.860 against XGBoost's 0.874, where up is better) is the one it is not. The paper's own
    # sentence says "mostly", and the existential reading is the one that survives.
    assert finding.measurements["n_supported"] == 10
    assert finding.measurements["n_counterexamples"] == 1
    assert "unit=comparison_member" in finding.reason
    assert "block=b1 [" in finding.reason
    assert 'multicolumn group header "Default hyperparameters" at data/table_nn_gbdt.tex:5' in finding.reason


def test_table4_the_other_block_is_a_different_set_of_cells(tmp_path: Path) -> None:
    """data/table_nn_gbdt.tex:13 prints `--` where XGBoost's AL score would stand. A missing
    value is not a zero, so one of the eleven columns is not decidable and the rule stops."""
    findings = _audit_table4(tmp_path / "b2", _table4_claims("B3", "b2"))
    finding = one(findings, "PD004", "B3")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "1 of 11 columns have no declared direction or no numeric cell" in finding.reason
    assert "block=b2 [" in finding.reason
    assert 'multicolumn group header "Tuned hyperparameters" at data/table_nn_gbdt.tex:11' in finding.reason


def test_table4_a_declared_block_the_source_does_not_print_selects_nothing(tmp_path: Path) -> None:
    findings = _audit_table4(tmp_path / "ghost", _table4_claims("B4", "b9"))
    finding = one(findings, "PD004", "B4")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "block 'b9' prints no row addressed by" in finding.reason


# ---------------------------------------------------------------------------------------------
# An unseen synthetic paper: the block is what decides the verdict
# ---------------------------------------------------------------------------------------------

TWO_BLOCK_TABLE = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
\multicolumn{3}{c}{Untuned configuration}\\
\midrule
Ours & $0.42$ & $0.10$ \\
Base & $0.40$ & $0.12$ \\
\midrule
\multicolumn{3}{c}{Tuned configuration}\\
\midrule
Ours & $0.38$ & $0.14$ \\
Base & $0.41$ & $0.09$ \\
\bottomrule
\end{tabular}
\caption{Two configurations of the same two models.}\label{tab:twoblock}
\end{table}"""

SENTENCE = r"Ours outperforms Base on every reported metric."
SYNTHETIC_ANCHOR = float_anchor("tab:twoblock", float_id="tab-twoblock", quantity_declaration="Acc, RMSE")


def _audit_two_block(root: Path, block: str) -> RuleFinding:
    paper = document(TWO_BLOCK_TABLE, SENTENCE)
    qualifiers: list[dict[str, str]] = [{"kind": "comparison_basis", "statement": "per_column"}]
    if block:
        qualifiers.append({"kind": "comparison_block", "statement": f"block={block}"})
    entry = claim(
        paper,
        "C",
        SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Ours", "Base"],
        links=["L-C"],
        qualifiers=qualifiers,
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=paper,
            findings=[],
            claims=[entry],
            floats=[SYNTHETIC_ANCHOR],
            links=[link("L-C", "C", "FLOAT", "tab-twoblock")],
        )
    )
    return one(findings, "PD004", "C")


def test_the_synthetic_pair_is_judged_differently_in_each_block(tmp_path: Path) -> None:
    untuned = _audit_two_block(tmp_path / "untuned", "b1")
    assert untuned.status is RuleStatus.PASS
    assert "block=b1 [" in untuned.reason
    assert 'multicolumn group header "Untuned configuration"' in untuned.reason

    tuned = _audit_two_block(tmp_path / "tuned", "b2")
    assert tuned.status is RuleStatus.FAIL
    assert "Acc (Ours 0.38 vs Base 0.41, up is better)" in tuned.reason
    assert "RMSE (Ours 0.14 vs Base 0.09, down is better)" in tuned.reason
    assert "block=b2 [" in tuned.reason
    assert 'multicolumn group header "Tuned configuration"' in tuned.reason


# A second unseen shape: blocks opened by a vertically merged leading cell, the NiceTabular
# form GMMVI Table 8 uses. Same rule, different stated structure -- and the reason must name the
# merged cell, not a rule or a group header.
MERGED_TABLE = r"""\begin{table}[t]
\centering
\begin{NiceTabular}{llc}
\toprule
Setting & Estimator & Score\textuparrow \\
\midrule
\Block{2-1}{Default} & Alpha & $0.42$ \\
 & Beta & $0.40$ \\
\Block{2-1}{Tuned} & Alpha & $0.38$ \\
 & Beta & $0.41$ \\
\bottomrule
\end{NiceTabular}
\caption{Two settings of the same two estimators.}\label{tab:merged}
\end{table}"""

MERGED_SENTENCE = r"Alpha outperforms Beta on every reported metric."
MERGED_ANCHOR = float_anchor("tab:merged", float_id="tab-merged", quantity_declaration="Score")


def _audit_merged(root: Path, block: str) -> RuleFinding:
    paper = document(MERGED_TABLE, MERGED_SENTENCE)
    qualifiers: list[dict[str, str]] = [{"kind": "comparison_basis", "statement": "per_column"}]
    if block:
        qualifiers.append({"kind": "comparison_block", "statement": f"block={block}"})
    entry = claim(
        paper,
        "M",
        MERGED_SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Alpha", "Beta"],
        links=["L-M"],
        qualifiers=qualifiers,
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=paper,
            findings=[],
            claims=[entry],
            floats=[MERGED_ANCHOR],
            links=[link("L-M", "M", "FLOAT", "tab-merged")],
        )
    )
    return one(findings, "PD004", "M")


def test_a_merged_leading_cell_opens_blocks_the_same_way(tmp_path: Path) -> None:
    """Two label columns and one value column: the merge itself states that `Alpha` is printed
    once per setting, so the address needs (block, row, column) exactly as the group-header form
    does -- and the reason quotes the merged cell as the boundary."""
    default = _audit_merged(tmp_path / "default", "b1")
    assert default.status is RuleStatus.PASS
    assert "block=b1 [" in default.reason
    assert 'merged cell spanning 2 rows = "Default"' in default.reason

    tuned = _audit_merged(tmp_path / "tuned", "b2")
    assert tuned.status is RuleStatus.FAIL
    assert "merged cell spanning 2 rows = " in tuned.reason
    assert "Score (Alpha 0.38 vs Beta 0.41, up is better)" in tuned.reason

    unnamed = _audit_merged(tmp_path / "unnamed", "")
    assert unnamed.status is RuleStatus.INCONCLUSIVE
    assert "printed in 2 structural blocks" in unnamed.reason
    assert 'merged cell spanning 2 rows = "Tuned"' in unnamed.reason


def test_without_a_declared_block_the_same_subject_pair_is_unaddressable(tmp_path: Path) -> None:
    """No verdict at all may depend on which of two blocks the parser happened to reach first."""
    finding = _audit_two_block(tmp_path / "none", "")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "printed in 2 structural blocks" in finding.reason
    assert 'multicolumn group header "Untuned configuration"' in finding.reason
    assert 'multicolumn group header "Tuned configuration"' in finding.reason


VALUE_SENTENCE = r"Ours reaches 0.42 on Acc."


def _audit_pd003(root: Path, block: str) -> RuleFinding:
    paper = document(TWO_BLOCK_TABLE, VALUE_SENTENCE)
    entry = claim(
        paper,
        "V",
        VALUE_SENTENCE,
        form="NUMERIC_ATTRIBUTION",
        fragment_is_text=True,
        subjects=["Ours"],
        links=["L-V", "L-VC"],
        qualifiers=[{"kind": "comparison_block", "statement": f"block={block}"}] if block else [],
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=paper,
            findings=[],
            claims=[entry],
            floats=[SYNTHETIC_ANCHOR],
            links=[
                link("L-V", "V", "FLOAT", "tab-twoblock", quantity_identity="Acc, RMSE"),
                link("L-VC", "V", "PROSE", {"path": "paper.tex", "column": "Acc", "row": "Ours"}),
            ],
        )
    )
    return one([f for f in findings if f.rule_id == "PD003"], "PD003", "V")


def test_pd003_agreement_is_measured_against_one_blocks_cell(tmp_path: Path) -> None:
    """The address (column=Acc, row=Ours) is printed twice in this table, at 0.42 and at 0.38.
    Declaring the block is what makes "the prose agrees with the cell" decidable at all."""
    ambiguous = _audit_pd003(tmp_path / "ambiguous", "")
    assert ambiguous.status is RuleStatus.INCONCLUSIVE
    assert "unit=reported_cell" in ambiguous.reason
    assert "printed in 2 structural blocks" in ambiguous.reason

    same_block = _audit_pd003(tmp_path / "b1", "b1")
    assert same_block.status is RuleStatus.PASS
    assert "unit=reported_cell" in same_block.reason
    assert "column=Acc, row=Ours, block=b1 [" in same_block.reason
    assert 'multicolumn group header "Untuned configuration"' in same_block.reason

    other_block = _audit_pd003(tmp_path / "b2", "b2")
    assert other_block.status is RuleStatus.INCONCLUSIVE
    assert "0.42 vs the printed 0.38" in other_block.reason
    assert "block=b2 [" in other_block.reason
    assert 'multicolumn group header "Tuned configuration"' in other_block.reason


# A third unseen shape: two tables in one paper, each with its own blocks. The block key is local to
# the float that states it -- `b1` is not a global namespace, and a declaration may not reach across
# a float boundary.
MULTI_TABLE_PAPER = r"""\documentclass{article}
\begin{document}
\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
\multicolumn{3}{c}{Small model}\\
\midrule
Ours & $0.42$ & $0.10$ \\
Base & $0.40$ & $0.12$ \\
\midrule
\multicolumn{3}{c}{Large model}\\
\midrule
Ours & $0.46$ & $0.08$ \\
Base & $0.45$ & $0.11$ \\
\bottomrule
\end{tabular}
\caption{Accuracy by model size.}\label{tab:size}
\end{table}
\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
\multicolumn{3}{c}{One epoch}\\
\midrule
Ours & $0.30$ & $0.20$ \\
Base & $0.35$ & $0.18$ \\
\midrule
\multicolumn{3}{c}{Ten epochs}\\
\midrule
Ours & $0.52$ & $0.07$ \\
Base & $0.54$ & $0.06$ \\
\bottomrule
\end{tabular}
\caption{Accuracy by training budget.}\label{tab:budget}
\end{table}
Ours outperforms Base on every reported metric.
\end{document}"""

MULTI_SENTENCE = "Ours outperforms Base on every reported metric."
SIZE_ANCHOR = float_anchor("tab:size", float_id="tab-size", quantity_declaration="Acc, RMSE")
BUDGET_ANCHOR = float_anchor("tab:budget", float_id="tab-budget", quantity_declaration="Acc, RMSE")


def _audit_two_floats(root: Path, target: str, block: str) -> RuleFinding:
    """One claim, one link to one of the two tables, and a block declared in that table only."""
    entry = claim(
        MULTI_TABLE_PAPER,
        "T",
        MULTI_SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Ours", "Base"],
        links=["L-T"],
        qualifiers=[
            {"kind": "comparison_basis", "statement": "per_column"},
            {"kind": "comparison_block", "statement": f"block={block}"},
        ],
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=MULTI_TABLE_PAPER,
            findings=[],
            claims=[entry],
            floats=[SIZE_ANCHOR, BUDGET_ANCHOR],
            links=[link("L-T", "T", "FLOAT", target.replace(":", "-"))],
        )
    )
    return one(findings, "PD004", "T")


def test_a_block_name_is_local_to_the_table_that_states_it(tmp_path: Path) -> None:
    r"""`b2` of the first table is not `b2` of the second, and each prints `Ours` twice.

    With no block declared the pair is unaddressable. Declared, the same words `block=b2` decide the
    claim one way in the size table and the opposite way in the budget table, because a block is a
    position inside one float rather than a name shared by the paper. Each reason quotes only its own
    group header, and the counterexamples in the second case are that table's own printed cells.
    """
    undeclared = _audit_two_floats(tmp_path / "none", "tab:size", "")
    assert undeclared.status is RuleStatus.INCONCLUSIVE
    assert "printed in 2 structural blocks" in undeclared.reason
    assert 'multicolumn group header "Small model"' in undeclared.reason
    assert 'multicolumn group header "Large model"' in undeclared.reason

    size = _audit_two_floats(tmp_path / "size", "tab:size", "b2")
    assert size.status is RuleStatus.PASS
    assert 'multicolumn group header "Large model"' in size.reason
    assert "One epoch" not in size.reason
    assert "Ten epochs" not in size.reason

    budget = _audit_two_floats(tmp_path / "budget", "tab:budget", "b2")
    assert budget.status is RuleStatus.FAIL
    assert 'multicolumn group header "Ten epochs"' in budget.reason
    assert "Acc (Ours 0.52 vs Base 0.54, up is better)" in budget.reason
    assert "RMSE (Ours 0.07 vs Base 0.06, down is better)" in budget.reason
    assert "Small model" not in budget.reason
    assert "Large model" not in budget.reason


def _audit_statement(root: Path, statement: str) -> RuleFinding:
    """The same claim with a `comparison_block` whose statement is arbitrary text."""
    entry = claim(
        MULTI_TABLE_PAPER,
        "T",
        MULTI_SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Ours", "Base"],
        links=["L-T"],
        qualifiers=[
            {"kind": "comparison_basis", "statement": "per_column"},
            {"kind": "comparison_block", "statement": statement},
        ],
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=MULTI_TABLE_PAPER,
            findings=[],
            claims=[entry],
            floats=[SIZE_ANCHOR, BUDGET_ANCHOR],
            links=[link("L-T", "T", "FLOAT", "tab-size")],
        )
    )
    return one(findings, "PD004", "T")


def test_a_statement_that_names_no_block_declares_no_block(tmp_path: Path) -> None:
    r"""A half-written declaration is read as undeclared, not as a block called `block=`.

    The two readings differ downstream: undeclared reports which blocks the source prints, while a
    name the table does not carry reports that the name selects nothing. Silently turning prose into
    a block key would produce the second message for what was really the first case.
    """
    for index, statement in enumerate(("", "block=", "the second group of rows", "block = ")):
        finding = _audit_statement(tmp_path / f"undeclared{index}", statement)
        assert finding.status is RuleStatus.INCONCLUSIVE, statement
        assert "printed in 2 structural blocks" in finding.reason, statement

    named = _audit_statement(tmp_path / "named", "b2")
    assert named.status is RuleStatus.PASS
    assert "block=b2 [" in named.reason

    uncarried = _audit_statement(tmp_path / "uncarried", "block=b7")
    assert uncarried.status is RuleStatus.INCONCLUSIVE
    assert "block 'b7' prints no row addressed by" in uncarried.reason


SHARED_LABEL_TABLE = r"""\begin{table}[t]
\centering
\begin{tabular}{llc}
\toprule
 & Estimator & Score \\
\midrule
\multirow{2}{*}{Shared} & Alpha & $0.42$ \\
 & Beta & $0.38$ \\
\bottomrule
\end{tabular}
\caption{One leading label that a merge carries onto a second row.}\label{tab:sharedlabel}
\end{table}"""

SHARED_LABEL_ANCHOR = float_anchor("tab:sharedlabel", float_id="tab-shared", quantity_declaration="Score")


def _audit_shared_label(root: Path, row: str) -> RuleFinding:
    paper = document(SHARED_LABEL_TABLE, r"Shared reaches 0.42 on Score.")
    findings = audit_manifest_of(
        write_case(
            root,
            paper=paper,
            findings=[],
            claims=[
                claim(
                    paper,
                    "S",
                    r"Shared reaches 0.42 on Score.",
                    form="NUMERIC_ATTRIBUTION",
                    fragment_is_text=True,
                    links=["L-S", "L-SC"],
                )
            ],
            floats=[SHARED_LABEL_ANCHOR],
            links=[
                link("L-S", "S", "FLOAT", "tab-shared", quantity_identity="Score"),
                link("L-SC", "S", "PROSE", {"path": "paper.tex", "column": "Score", "row": row}),
            ],
        )
    )
    return one(findings, "PD003", "S")


def test_an_ambiguous_address_says_so_instead_of_claiming_the_label_is_absent(tmp_path: Path) -> None:
    r"""Two readings and no reading are different facts, and the reader must report the one it measured.

    A leading cell merged over two rows prints one label twice inside a single block. Addressing that
    label is refused -- choosing either row would be a silent choice of evidence -- but reporting it as
    "no row is addressed" tells the reader the table never prints the label, which the table does.
    """
    carried = _audit_shared_label(tmp_path / "carried", "Shared")
    assert carried.status is RuleStatus.INCONCLUSIVE
    assert "printed by 2 rows of b1" in carried.reason
    assert "more than one reading" in carried.reason

    absent = _audit_shared_label(tmp_path / "absent", "NeverPrinted")
    assert absent.status is RuleStatus.INCONCLUSIVE
    assert absent.reason.count("no row is addressed by 'NeverPrinted'") == 1
    assert "more than one reading" not in absent.reason
