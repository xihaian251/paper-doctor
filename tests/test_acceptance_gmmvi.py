"""Phase 1 §14 + §22: the frozen GMMVI real anchors (arXiv 2209.11533v2), audited in place.

The corpus under `phase0/sources/` and the upstream artifact under `tests/fixtures/` are read-only
evidence: this file copies nothing, rewrites nothing, and never re-runs Result Doctor. §16 forbids
regenerating an expectation from the implementation, so every status asserted below is the one
Phase 0 froze (§9 rows C1/C5/C6, §14, §22 -- C5 as amended by the 2026-09-29 ERRATUM A1) and every
count is recomputed in this file straight off the frozen artifact -- not read back out of a finding.

Two §14 guards shape the case construction:

* C5 stays an *aggregation-level* count check (the frozen anchor). The second C5 object declared
  here is an additional `reported_cell` view of the same caption, not a substitute: removing it
  would leave PD002's `reported_cell` unit and PD's strict `spread_label` predicate unexercised on
  real data. The aggregation-level check is present and judged on its own.
* C10/C11/C12 are RD-owned (§15) and are deliberately absent from the claim set; the last test in
  this file asserts that PD re-reports none of them.
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
CORPUS_DIR = REPO / "phase0" / "sources" / "2209.11533v2.tex"
PAPER = "arxiv.tex"
ARTIFACT = Path(__file__).resolve().parent / "fixtures" / "rd_findings_gmmvi_0.1.0.json"

#: The caption sentence Phase 0 traces as C5/C6 (`arxiv.tex:625`).
C5_TEXT = (
    r"we show the $3\sigma$ confidence intervals "
    r"based on the standard error of its mean using ten different seeds"
)
C6_TEXT = (
    r"We observed instabilities for {\sc Sepyfux} on \textit{PlanarRobot} and \textit{TALOS}"
    r" and, thus, removed bad outliers when computing the reported values."
)
C1_TEXT = r"the optimistic value provided in Table~\ref{tab:exp1_eval} for \emph{BreastCancer} ($78.69$)"


def _artifact_rows() -> list[dict[str, Any]]:
    """The frozen upstream findings, read once. A missing artifact is a hard error, never a skip."""
    if not ARTIFACT.is_file():
        raise FileNotFoundError(f"frozen upstream artifact missing: {ARTIFACT}")
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _rd005_with_spread(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r["rule_id"] == "RD005" and r["measurements"].get("spread_label")]


def _excluded(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """§13's PD005 universe predicate, computed here independently of the implementation."""
    return [r for r in rows if r["rule_id"] == "RD002" and (r["measurements"].get("n_exclusions") or 0) > 0]


@pytest.fixture(scope="module")
def tex() -> str:
    return corpus_lines(CORPUS_DIR, PAPER)


@pytest.fixture(scope="module")
def rows() -> list[dict[str, Any]]:
    return _artifact_rows()


@pytest.fixture(scope="module")
def findings(tmp_path_factory: Any, tex: str, rows: list[dict[str, Any]]) -> list[RuleFinding]:
    """One real end-to-end audit of the three frozen anchors."""
    rd002 = [r["target"] for r in rows if r["rule_id"] == "RD002"]
    rd005 = [r["target"] for r in _rd005_with_spread(rows)]
    excluded = [r["target"] for r in _excluded(rows)]

    claims = [
        claim(
            tex,
            "C1",
            C1_TEXT,
            form="NUMERIC_ATTRIBUTION",
            path=PAPER,
            fragment_is_text=True,
            links=["L-C1"],
        ),
        claim(
            tex,
            "C5",
            C5_TEXT,
            form="SCOPE",
            path=PAPER,
            fragment_is_text=True,
            links=[f"L-AGG{i}" for i in range(len(rd002))],
            scope={
                "declared_universe": "the aggregations this caption covers",
                "stated_count": 10,
                "unit": "aggregation",
                "universe_status": "RECOVERED",
            },
        ),
        claim(
            tex,
            "C5-CELLS",
            C5_TEXT,
            form="SCOPE",
            path=PAPER,
            fragment_is_text=True,
            links=[f"L-CELL{i}" for i in range(len(rd005))],
            scope={
                "declared_universe": "the reported cells this caption covers",
                "stated_count": 10,
                "unit": "reported_cell",
                "universe_status": "RECOVERED",
            },
        ),
        claim(
            tex,
            "C6",
            C6_TEXT,
            form="QUALIFICATION",
            path=PAPER,
            fragment_is_text=True,
            links=[f"L-EXC{i}" for i in range(len(excluded))],
            scope={"declared_universe": "the excluded members", "members": ["sepyfux"], "universe_status": "RECOVERED"},
            qualifiers=[
                {"kind": "exclusion", "statement": "bad outliers were removed for Sepyfux on PlanarRobot and TALOS"}
            ],
        ),
    ]
    links = [link("L-C1", "C1", "FLOAT", "tab-exp1-eval", link_basis="AUTHOR_REF_IN_SENTENCE")]
    links += [link(f"L-AGG{i}", "C5", "RD_TARGET", ["RD002", t]) for i, t in enumerate(rd002)]
    links += [link(f"L-CELL{i}", "C5-CELLS", "RD_TARGET", ["RD005", t]) for i, t in enumerate(rd005)]
    links += [link(f"L-EXC{i}", "C6", "RD_TARGET", ["RD002", t]) for i, t in enumerate(excluded)]
    manifest = write_real_case(
        tmp_path_factory.mktemp("gmmvi"),
        audit_root=CORPUS_DIR,
        paper_path=PAPER,
        rd_artifact=ARTIFACT,
        claims=claims,
        floats=[{"float_id": "tab-exp1-eval", "label": "tab:exp1_eval", "quantity_declaration": "negated ELBO"}],
        links=links,
    )
    return audit_manifest(manifest)


# --- C1: the attribution points at the wrong float -------------------------------------------


def test_c1_reference_attribution_fails(findings: list[RuleFinding]) -> None:
    """§9/§14 C1: PD006 FAIL -- `tab:exp1_eval` is Table 3, which does not print 78.69."""
    finding = one(findings, "PD006", "C1")
    assert finding.status is RuleStatus.FAIL
    assert "table:3" in finding.reason and "78.69" in finding.reason
    assert finding.measurements["resolved"] == ("tab:exp1_eval -> table 3",)


def test_c1_link_itself_resolves_so_pd001_passes(findings: list[RuleFinding]) -> None:
    """The reference is real; only its *target* contradicts the value. PD001 and PD006 say different things."""
    assert one(findings, "PD001", "C1").status is RuleStatus.PASS


def test_c1_value_mismatch_is_not_double_counted_by_pd003(findings: list[RuleFinding]) -> None:
    """PD003 has no cell address to compare against, so it stays INCONCLUSIVE and names the wrong-float
    situation as PD006's finding instead of manufacturing a second FAIL for the same defect."""
    finding = one(findings, "PD003", "C1")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert finding.measurements["cell_value"] is None
    assert "it prints in table:2" in finding.reason


# --- C5: "ten different seeds" against the aggregation evidence ------------------------------


def test_c5_aggregation_divergence_is_counted_on_the_frozen_universe(
    findings: list[RuleFinding], rows: list[dict[str, Any]]
) -> None:
    """The census PD actually compared is the frozen artifact's own: 46 RD002 targets, of which the
    ones that do not compute over ten seeds are counted from the file, not from the finding."""
    aggregations = [r for r in rows if r["rule_id"] == "RD002"]
    divergent = [r for r in aggregations if r["measurements"].get("n_members") != 10]
    finding = one(findings, "PD002", "C5")
    assert finding.measurements["unit"] == "aggregation"
    assert finding.measurements["stated_count"] == 10
    assert finding.measurements["n_targets_compared"] == len(aggregations) == 46
    assert finding.measurements["n_counts_divergent"] == len(divergent) == 2


def test_c5_is_inconclusive_and_never_upgraded(findings: list[RuleFinding]) -> None:
    """ERRATUM A1 (accepted 2026-09-29) freezes C5 as PD002 INCONCLUSIVE: upstream RD002 is
    INCONCLUSIVE on all 46 aggregations on the Contract I-1 surface, so certifying the count either
    way would be an upgrade (preserve or downgrade, never upgrade). The divergence survives as a
    measurement. The research-round "9 of 46" census is NOT asserted here -- it reads
    `spread_form.n`, which is outside the I-1 read-list."""
    finding = one(findings, "PD002", "C5")
    assert finding.status is RuleStatus.INCONCLUSIVE
    assert "2 of 46" in finding.reason
    assert finding.measurements["upstream_statuses"] == ["INCONCLUSIVE"]


def test_c5_cell_view_declares_its_own_unit(findings: list[RuleFinding], rows: list[dict[str, Any]]) -> None:
    """§12: a count without a declared unit must fail a test. The same caption audited at cell
    granularity has to say so, and its 56/12 census has to come from RD005's own `n`."""
    cells = _rd005_with_spread(rows)
    divergent = [r for r in cells if r["measurements"].get("n") != 10]
    finding = one(findings, "PD002", "C5-CELLS")
    assert finding.measurements["unit"] == "reported_cell"
    assert finding.measurements["n_targets_compared"] == len(cells) == 56
    assert finding.measurements["n_counts_divergent"] == len(divergent) == 12
    assert finding.status is RuleStatus.INCONCLUSIVE


def test_c5_selection_is_by_declared_links_because_spread_label_keys_are_not_equal(
    findings: list[RuleFinding],
) -> None:
    """PD's only automatic caption-to-evidence binding is verbatim key equality. The artifact's
    `spread_label` is Result Doctor's normalised rendering (`3σ ...`), which is not the paper's
    sentence (`$3\\sigma$ ...`), so PD refuses to fuzzy-match and reports the declared links."""
    assert one(findings, "PD002", "C5-CELLS").measurements["selection_basis"] == (
        "the claim's declared (rule_id, target) links"
    )


# --- C6: the enumeration is narrower than the evidence ---------------------------------------


def test_c6_qualification_fails_and_names_the_unlisted_methods(
    findings: list[RuleFinding], rows: list[dict[str, Any]]
) -> None:
    """§14/§22 C6: PD005 FAIL, and the reason must name `sepyrux` **and** `zamtrux` -- the point of
    the rule is that the reader can see which members the sentence left out."""
    universe = _excluded(rows)
    finding = one(findings, "PD005", "C6")
    assert finding.status is RuleStatus.FAIL
    assert "sepyrux" in finding.reason and "zamtrux" in finding.reason
    assert "sepyfux" in finding.reason
    assert finding.measurements["n_universe_targets"] == len(universe) == 7


def test_c6_universe_comes_from_upstream_exclusion_records_only(
    findings: list[RuleFinding], rows: list[dict[str, Any]]
) -> None:
    """§13: "If you create an independent exclusion mechanism: Phase 1 FAILS." The universe PD005
    enumerates is exactly RD002's own `n_exclusions` records -- 7 targets, 34 listed exclusions --
    reached through the declared links, with no PD-side recomputation."""
    universe = _excluded(rows)
    total = sum(r["measurements"]["n_exclusions"] for r in universe)
    listed = sum(r["measurements"]["n_exclusions_listed"] for r in universe)
    assert (len(universe), total, listed) == (7, 34, 34)
    finding = one(findings, "PD005", "C6")
    assert finding.measurements["n_rd002_findings"] == len([r for r in rows if r["rule_id"] == "RD002"])
    assert finding.measurements["n_in_scope"] == 7


def test_c6_count_relation_belongs_to_pd005_not_pd002(findings: list[RuleFinding]) -> None:
    """The sentence states no count, so PD002 declines rather than inventing one, and points at the
    rule that does own the enumeration."""
    finding = one(findings, "PD002", "C6")
    assert finding.status is RuleStatus.NOT_APPLICABLE
    assert "PD005's relation" in finding.reason


# --- ownership: RD's rows stay RD's ----------------------------------------------------------


def test_pd_reports_only_pd_rules(findings: list[RuleFinding]) -> None:
    assert {f.rule_id for f in findings} <= set(RULE_IDS)
    assert not any(f.rule_id.startswith("RD") for f in findings)


def test_rd_owned_claims_c10_c11_c12_are_not_re_reported(findings: list[RuleFinding]) -> None:
    """§15: C10/C11/C12 are already ruled on by RD001/RD005/RD008 and were deleted from PD's claim
    universe. PD emits nothing addressed to them, and no PD finding re-states an upstream verdict."""
    targets = {f.target for f in findings}
    assert not targets & {"C10", "C11", "C12"}
    assert not targets & {"quantity:STM300/sepyfux/-elbo", "BreastCancer/samtron/-elbo/Table 5"}
    for finding in findings:
        assert finding.rule_id in RULE_IDS
