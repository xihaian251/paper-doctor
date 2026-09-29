"""Phase 1 §14 + §22: the frozen RTDL real anchors (arXiv 2106.11959), audited in place.

Same discipline as `test_acceptance_gmmvi.py`: the paper, its `data/*.tex` cells and the pilot
README are read-only; the upstream artifact is the frozen `rd_findings_rtdl_0.1.0.json`; every
status asserted is the one Phase 0 §10 froze as amended by the 2026-09-29 ERRATUM (A2, A3, A4), and
the printed cell values quoted here were read off the corpus by hand (`data/table_neural_networks.tex:14`,
`data/table_node.tex`, `data/table_ablation.tex`, `data/table_datasets.tex:6`) rather than taken from
a finding.

D1 and D8 are the epistemic-boundary cases: a sign disagreement and a +-1 difference must both
stop at INCONCLUSIVE. `result-doctor/phase4/rtdl-revisiting-models/README.md` is a pilot
transcript, not paper text, and is read only as the source of D1's and D2's sentences.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from support import claim, corpus_lines, link, one, write_real_case

from paper_doctor.audit import audit_manifest
from paper_doctor.rules import RULE_IDS
from paper_doctor.status import RuleFinding, RuleStatus

REPO = Path(__file__).resolve().parents[1]
#: No single directory contains both the paper and the pilot README, so the audit root is the
#: workspace and every declared path is written relative to it (see the report's two-root note).
AUDIT_ROOT = REPO.parent
PAPER = "paper-doctor/phase0/sources/2106.11959.tex/main.tex"
README = "result-doctor/phase4/rtdl-revisiting-models/README.md"
CELLS = "paper-doctor/phase0/sources/2106.11959.tex/data/"
ARTIFACT = Path(__file__).resolve().parent / "fixtures" / "rd_findings_rtdl_0.1.0.json"

D3_TEXT = "The metric values averaged over 15 random seeds are reported."
D2_TEXT = "let's compute the test score averaged over all random seeds"


@pytest.fixture(scope="module")
def rows() -> list[dict[str, Any]]:
    if not ARTIFACT.is_file():
        raise FileNotFoundError(f"frozen upstream artifact missing: {ARTIFACT}")
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def main_tex() -> str:
    return corpus_lines(AUDIT_ROOT, PAPER)


@pytest.fixture(scope="module")
def readme() -> str:
    return corpus_lines(AUDIT_ROOT, README)


@pytest.fixture(scope="module")
def findings(tmp_path_factory: Any, main_tex: str, readme: str, rows: list[dict[str, Any]]) -> list[RuleFinding]:
    aggregations = [r["target"] for r in rows if r["rule_id"] == "RD002"]
    claims = [
        # D1: the transcript's -0.499 against Table 2's printed CA/MLP cell.
        claim(
            readme,
            "D1",
            "california_housing   -0.499",
            form="NUMERIC_ATTRIBUTION",
            path=README,
            fragment_is_text=True,
            links=["L-D1F", "L-D1C"],
        ),
        # D2 / D3: "averaged over 15 random seeds", once over the certified subset and once over
        # the whole printed table.
        claim(
            readme,
            "D2",
            D2_TEXT,
            form="SCOPE",
            path=README,
            fragment_is_text=True,
            quantifier="all",
            links=[f"L-D2{c}" for c in "AB"],
            scope={"declared_universe": "every dataset"},
        ),
        claim(
            main_tex,
            "D3-TABLE",
            D3_TEXT,
            form="SCOPE",
            path=PAPER,
            fragment_is_text=True,
            links=[f"L-T{c}" for c in "AB"],
            scope={
                "declared_universe": "the 11 datasets printed in Table 2",
                "stated_count": 15,
                "unit": "aggregation",
                "universe_status": "PARTIAL",
            },
        ),
        claim(
            main_tex,
            "D3-SUBSET",
            D3_TEXT,
            form="SCOPE",
            path=PAPER,
            fragment_is_text=True,
            links=[f"L-S{c}" for c in "AB"],
            qualifiers=[
                {
                    "kind": "subset",
                    "statement": "audited over the two aggregations the upstream artifact models; "
                    "the other nine are unbound",
                }
            ],
            scope={
                "declared_universe": "the datasets the upstream artifact models",
                "stated_count": 15,
                "unit": "aggregation",
                "members": ["adult", "california_housing"],
                "universe_status": "RECOVERED",
            },
        ),
        # D5: the two clauses of main.tex:364 over Table 3.
        claim(
            main_tex,
            "D5A",
            r"in this regime, \architecture\ outperforms NODE",
            form="COMPARATIVE",
            path=PAPER,
            fragment_is_text=True,
            predicate="outperforms",
            subjects=["FT-Transformer", "NODE"],
            links=["L-D5A"],
            qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
        ),
        claim(
            main_tex,
            "D5B",
            "the gap between ResNet and NODE is significantly reduced",
            form="COMPARATIVE",
            path=PAPER,
            fragment_is_text=True,
            predicate="is reduced",
            subjects=["ResNet", "NODE"],
            links=["L-D5B"],
            qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
        ),
        # D6: the ablation sentence, main.tex:465.
        claim(
            main_tex,
            "D6",
            r"reported in \autoref{tab:ablation} and demonstrate both the superiority of the Transformer's backbone "
            r"to that of AutoInt and the necessity of feature biases",
            form="COMPARATIVE",
            path=PAPER,
            fragment_is_text=True,
            predicate="is superior to",
            subjects=["FT-Transformer", "FT-Transformer (w/o feature biases)"],
            links=["L-D6"],
            qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
        ),
        # D7: the existential enumeration over Table 4.
        claim(
            main_tex,
            "D7",
            r"Once hyperparameters are properly tuned, GBDTs start dominating on some datasets "
            r"(California Housing, Adult, Yahoo; see \autoref{tab:nn-gbdt}).",
            form="SCOPE",
            path=PAPER,
            fragment_is_text=True,
            quantifier="some",
            links=["L-D7"],
            scope={
                "declared_universe": "the datasets on which tuned GBDTs dominate",
                "stated_count": 3,
                "unit": "comparison_member",
                "members": ["California Housing", "Adult", "Yahoo"],
                "universe_status": "RECOVERED",
            },
        ),
        # D8: prose 700 against the printed 699.
        claim(
            main_tex,
            "D8",
            "The big difference on the Yahoo dataset is expected because of the large number of features (700).",
            form="NUMERIC_ATTRIBUTION",
            path=PAPER,
            fragment_is_text=True,
            links=["L-D8F", "L-D8C"],
        ),
        # D11: the abstract/conclusion pair that is the same sentence twice over different universes.
        claim(
            main_tex,
            "D11-ABS",
            "which outperforms other solutions on most tasks",
            form="COMPARATIVE",
            path=PAPER,
            fragment_is_text=True,
            predicate="outperforms",
            subjects=["FT-Transformer"],
            quantifier="most",
            same_as=[{"claim": "D11-CON", "basis": "declared"}],
            scope={"declared_universe": "other solutions"},
        ),
        claim(
            main_tex,
            "D11-CON",
            "that outperforms other DL solutions on most of the tasks",
            form="COMPARATIVE",
            path=PAPER,
            fragment_is_text=True,
            predicate="outperforms",
            subjects=["FT-Transformer"],
            quantifier="most",
            same_as=[{"claim": "D11-ABS", "basis": "declared"}],
            scope={"declared_universe": "other DL solutions"},
        ),
    ]
    links = [
        link("L-D1F", "D1", "FLOAT", "tab-neural-networks", quantity_identity="metrics.test.score"),
        link("L-D1C", "D1", "PROSE", {"path": CELLS + "table_neural_networks.tex", "column": "CA", "row": "MLP"}),
        link("L-D5A", "D5A", "FLOAT", "tab-node"),
        link("L-D5B", "D5B", "FLOAT", "tab-node"),
        link("L-D6", "D6", "FLOAT", "tab-ablation", link_basis="AUTHOR_REF_IN_SENTENCE"),
        link("L-D7", "D7", "FLOAT", "tab-nn-gbdt", link_basis="AUTHOR_REF_IN_SENTENCE"),
        link("L-D8F", "D8", "FLOAT", "tab-datasets", quantity_identity="#num. features"),
        link("L-D8C", "D8", "PROSE", {"path": CELLS + "table_datasets.tex", "column": "YA", "row": "#num. features"}),
    ]
    pairs = {"D2": ("L-D2A", "L-D2B"), "D3-TABLE": ("L-TA", "L-TB"), "D3-SUBSET": ("L-SA", "L-SB")}
    for cid, ids in pairs.items():
        links += [link(lid, cid, "RD_TARGET", ["RD002", target]) for lid, target in zip(ids, aggregations, strict=True)]
    floats = [
        {"float_id": "tab-datasets", "label": "tab:datasets"},
        {
            "float_id": "tab-neural-networks",
            "label": "tab:neural-networks",
            "quantity_declaration": "\\textdownarrow ~ RMSE, \\textuparrow ~ accuracy",
            "mark_rule_declaration": "top = the gap to the best score is not statistically significant",
        },
        {
            "float_id": "tab-node",
            "label": "tab:node",
            "quantity_declaration": "\\textdownarrow ~ RMSE, \\textuparrow ~ accuracy",
            "precision_declaration": "due to the limited precision, some different values are "
            "represented with the same figures",
        },
        {"float_id": "tab-nn-gbdt", "label": "tab:nn-gbdt"},
        {
            "float_id": "tab-ablation",
            "label": "tab:ablation",
            "quantity_declaration": "\\textdownarrow ~ RMSE, \\textuparrow ~ accuracy",
        },
    ]
    manifest = write_real_case(
        tmp_path_factory.mktemp("rtdl"),
        audit_root=AUDIT_ROOT,
        paper_path=PAPER,
        rd_artifact=ARTIFACT,
        claims=claims,
        floats=floats,
        links=links,
    )
    return audit_manifest(manifest)


# --- D1: sign disagreement with no declared quantity identity --------------------------------


def test_d1_stays_inconclusive_and_can_never_be_pass_or_fail(findings: list[RuleFinding]) -> None:
    """§14: "This case MUST remain INCONCLUSIVE. Any implementation that turns D1 into PASS or FAIL
    violates the frozen epistemic boundary." The transcript says -0.499, Table 2 prints 0.499 for
    CA/MLP, and the declared quantity identities disagree, so neither agreement nor mismatch is
    assertable."""
    finding = one(findings, "PD003", "D1")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert finding.measurements["claim_value"] == "-0.499"
    assert finding.measurements["cell_value"] == "0.499"
    assert "closeness is not a PASS" in finding.reason
    assert "declared identities disagree" in finding.measurements["identity_basis"]


def test_d1_links_resolve_so_the_evidence_is_on_file(findings: list[RuleFinding]) -> None:
    """D1 is undecidable because of missing semantics, not because of missing evidence."""
    assert one(findings, "PD001", "D1").status is RuleStatus.PASS


# --- D5: the two clauses of one sentence -----------------------------------------------------


def test_d5_clause_one_fails_on_a_counterexample_column(findings: list[RuleFinding]) -> None:
    """main.tex:364 claims FT-Transformer beats NODE per column; `data/table_node.tex` prints
    YE 8.751 (FT-Transformer) against 8.716 (NODE) and YE is a lower-is-better column, so the
    universal reading of the clause is contradicted. AD is a printed tie and is recorded as one."""
    finding = one(findings, "PD004", "D5A")
    assert finding.status is RuleStatus.FAIL
    assert finding.measurements == {
        "n_float_links": 1,
        "n_subjects": 2,
        "quantifier": "bare",
        "n_columns_in_scope": 11,
        "n_supported": 9,
        "n_counterexamples": 1,
        "n_ties": 1,
        "n_undetermined": 0,
    }
    assert "YE" in finding.reason and "AD" in finding.reason


def test_d5_clause_two_is_inconclusive_without_an_invented_margin(findings: list[RuleFinding]) -> None:
    """§14: "Do not invent a margin." 'significantly' has no declared test or threshold, so PD004
    declines to compare gaps at all rather than picking one."""
    finding = one(findings, "PD004", "D5B")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "significantly" in finding.reason and "threshold" in finding.reason
    assert finding.measurements["n_columns_in_scope"] == 0
    assert not [key for key in finding.measurements if "margin" in key or "threshold" in key]


# --- D6: the ablation superiority claim ------------------------------------------------------


def test_d6_fails_on_the_value_and_direction_the_table_prints(findings: list[RuleFinding]) -> None:
    """ERRATUM A3 (accepted 2026-09-29): D6 stays FAIL, and the census is 1 of 8 columns, not 2 of 8
    -- `0.727` is the HI column, not JA, and bold-mark arithmetic is RD007's, so it is not borrowed
    as PD evidence. In `data/table_ablation.tex` FT-Transformer is worse on the lower-is-better YE
    column (8.855 vs 8.843), which contradicts the superiority claim."""
    finding = one(findings, "PD004", "D6")
    assert finding.status is RuleStatus.FAIL
    assert finding.measurements["n_columns_in_scope"] == 8
    assert finding.measurements["n_counterexamples"] == 1
    assert finding.measurements["n_supported"] == 7
    assert "YE" in finding.reason


def test_d6_reference_attribution_is_derived_and_passes(findings: list[RuleFinding]) -> None:
    """The sentence names its own float via `\\autoref{tab:ablation}`; the number PD prints for it
    comes from the document's own numbering, and the resolution is recorded as DERIVED."""
    finding = one(findings, "PD006", "D6")
    assert finding.status is RuleStatus.PASS
    assert "DERIVED" in finding.reason


# --- D7: existential enumeration, never a false FAIL -----------------------------------------


def test_d7_is_never_failed_for_a_missing_dataset_count(findings: list[RuleFinding]) -> None:
    """ERRATUM A2 (accepted 2026-09-29) froze D7 as a rule vector, not a verdict: PD001 PASS + PD006
    PASS + PD002 INCONCLUSIVE, and never a FAIL. D7 is the false-FAIL guard §10 intended -- the
    upstream artifact carries no per-dataset count for a `comparison_member` universe (RD007 is
    NOT_RUN on zero comparison sets), so PD002 stops rather than guessing. The existential PASS
    itself is pinned synthetically in S13."""
    assert one(findings, "PD002", "D7").status is RuleStatus.INCONCLUSIVE
    assert "nothing declares which upstream targets this scope covers" in one(findings, "PD002", "D7").reason
    assert not [f for f in findings if f.rule_id == "PD004" and f.target == "D7"]


def test_d7_reference_and_link_resolve(findings: list[RuleFinding]) -> None:
    assert one(findings, "PD001", "D7").status is RuleStatus.PASS
    assert one(findings, "PD006", "D7").status is RuleStatus.PASS


def test_d7_unit_is_declared_as_a_comparison_member_not_an_aggregation(findings: list[RuleFinding]) -> None:
    """§12: the count unit has to be visible, or the same "3" means two different things."""
    assert one(findings, "PD002", "D7").measurements["unit"] == "comparison_member"


# --- D8: numeric nearness is not identity ----------------------------------------------------


def test_d8_close_is_not_equal_and_stays_inconclusive(findings: list[RuleFinding]) -> None:
    """§14: "numeric nearness != identity, 699 ~ 700 is NOT PASS." Table 1 prints 699 for
    YA/#num. features while the prose says 700; with no declared rounding semantics PD cannot call
    that either faithful or unfaithful."""
    finding = one(findings, "PD003", "D8")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert finding.measurements["claim_value"] == "700"
    assert finding.measurements["cell_value"] == "699"
    assert finding.measurements["delta"] == 1.0
    assert finding.measurements["identity_basis"] == "undeclared"
    assert "closeness is not a PASS" in finding.reason


# --- D2/D3: the same 15-seed claim at two universe statuses ----------------------------------


def test_d3_passes_on_the_certified_subset(findings: list[RuleFinding], rows: list[dict[str, Any]]) -> None:
    """§10/§22 PASS-on-subset, subset sized on the admissible surface. The frozen artifact models two
    RD002 aggregations, both PASS with `n_members = 15`, so a RECOVERED universe over exactly those
    two is certifiable (`unit = aggregation`). §10's research-round list names three datasets, but its
    third (`aloi`) is known only from re-computed raw runs, which is not a Contract I-1 surface --
    ERRATUM A5 freezes the executable count at 2, exactly as A1 relabelled the 9/46 census."""
    upstream = [r for r in rows if r["rule_id"] == "RD002"]
    assert [r["measurements"]["n_members"] for r in upstream] == [15, 15]
    finding = one(findings, "PD002", "D3-SUBSET")
    assert finding.status is RuleStatus.PASS
    assert finding.measurements["n_targets_compared"] == len(upstream) == 2
    assert finding.measurements["universe_status"] == "RECOVERED"


def test_d3_is_inconclusive_on_the_whole_printed_table(findings: list[RuleFinding]) -> None:
    """§22 INCONCLUSIVE-on-table: nine of Table 2's eleven datasets have no upstream aggregation,
    and a PARTIAL universe cannot be PASSed even though every bound target agrees."""
    finding = one(findings, "PD002", "D3-TABLE")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert finding.measurements["universe_status"] == "PARTIAL"
    assert finding.measurements["n_counts_divergent"] == 0
    assert "PARTIAL" in finding.reason


def test_d2_states_no_count_so_pd002_declines_but_the_link_resolves(findings: list[RuleFinding]) -> None:
    """The README sentence is a quantifier with no number in it: PD002 reports NOT_APPLICABLE
    instead of inventing a count, while PD001 still certifies that its evidence is on file."""
    assert one(findings, "PD002", "D2").status is RuleStatus.NOT_APPLICABLE
    assert one(findings, "PD001", "D2").status is RuleStatus.PASS


# --- D11: one claim, two declared scopes -----------------------------------------------------


def test_d11_cross_section_pair_fails_on_unreconciled_scopes(findings: list[RuleFinding]) -> None:
    """§14/§22 D11 PD007 FAIL: the abstract and the conclusion state the same relation over what
    they declare as different universes, with no declared reconciliation."""
    finding = one(findings, "PD007", "D11-ABS|D11-CON")
    assert finding.status is RuleStatus.FAIL
    assert finding.measurements["pairing_basis"] == ("declared",)
    assert finding.measurements["scope_a"] != finding.measurements["scope_b"]


def test_d11_is_untraceable_not_false(findings: list[RuleFinding]) -> None:
    """Neither half declares a support link, and no float is referenced: PD001 must stop at
    INCONCLUSIVE, because an unlinked claim is not thereby wrong."""
    for target in ("D11-ABS", "D11-CON"):
        assert one(findings, "PD001", target).status is RuleStatus.INCONCLUSIVE
        assert one(findings, "PD004", target).status is RuleStatus.NOT_APPLICABLE


# --- ownership -------------------------------------------------------------------------------


def test_only_pd_rules_are_emitted(findings: list[RuleFinding]) -> None:
    assert {f.rule_id for f in findings} <= set(RULE_IDS)
    assert not any(f.rule_id.startswith("RD") for f in findings)


def test_upstream_pass_is_never_promoted_to_a_paper_level_verdict(findings: list[RuleFinding]) -> None:
    """Contract I-1: PD may preserve or downgrade upstream certainty, never upgrade it, and it never
    speaks for the paper as a whole."""
    assert not any(f.rule_id == "PD002" and f.status is RuleStatus.PASS and f.target == "D3-TABLE" for f in findings)
    targets = {f.target for f in findings}
    assert not targets & {"paper", "document", "overall", "score"}
