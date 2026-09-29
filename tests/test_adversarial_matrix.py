"""Phase 1 §16: the synthetic adversarial matrix S1-S13.

Every expected status below is transcribed from Phase 0 §18, which is authoritative for Phase 1
tests; none was regenerated from the implementation. The constructions are synthetic corpora --
never a real paper -- so each rule and each state is separated by construction, not by argument.

Discrimination is the point: a case that only makes a rule agree proves nothing about whether it
could disagree. The anti-false-positive half (S1, S7, S9, S13) is asserted as strictly as the
discriminating half, and every case that must not produce a FAIL says so explicitly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from support import audit_manifest_of, claim, document, float_anchor, link, one, rd, write_case

from paper_doctor.status import RuleStatus

# --- the shared synthetic floats -------------------------------------------------------------

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

#: A second float, used only to show a value can live in the table a reference does not point
#: to -- the GMMVI C1 shape (S5), reproduced without a real paper.
TABLE_OTHER = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
Ours & $0.87$ & $0.05$ \\
Base & $0.80$ & $0.09$ \\
\bottomrule
\end{tabular}
\caption{Ablation.}\label{tab:ablation}
\end{table}"""

PASS_NINE = rd("RD002", "agg/nine", "PASS", measurements={"n_members": 9})


def anchor(**fields: Any) -> dict[str, Any]:
    float_id = str(fields.pop("float_id", "tab-main"))
    return float_anchor("tab:main", float_id=float_id, quantity_declaration="Acc", **fields)


def prose_cell(link_id: str, claim_ref: str, column: str = "Acc", row: str = "Ours") -> dict[str, Any]:
    """A `[path,column,row]` link: the cell address is a *name*, per RD's `Locus` types."""
    return link(link_id, claim_ref, "PROSE", {"path": "paper.tex", "column": column, "row": row})


def float_link(
    link_id: str, claim_ref: str, target: str = "tab-main", basis: str = "AUTHOR_REF_IN_SENTENCE", **fields: Any
) -> dict[str, Any]:
    return link(link_id, claim_ref, "FLOAT", target, link_basis=basis, **fields)


def rd_link(link_id: str, claim_ref: str, rule_id: str, target: str) -> dict[str, Any]:
    return link(link_id, claim_ref, "RD_TARGET", [rule_id, target], link_basis="AUDITOR_DECLARED")


def failed(findings: Any) -> list[Any]:
    return [f for f in findings if f.status is RuleStatus.FAIL]


# --- S1: the fully supported claim ------------------------------------------------------------


def test_s1_everything_supported(tmp_path: Path) -> None:
    """S1: claim exactly supported, in-sentence `\\autoref`, cells string-equal, RD002 PASS,
    n matches => PD001 PASS, PD002 PASS, PD003 PASS, PD004 PASS, PD006 PASS."""
    numeric = r"Ours reaches 0.42 accuracy, see \autoref{tab:main}."
    scope = r"We report results over nine datasets."
    comparison = r"Ours beats Base on every metric in \autoref{tab:main}."
    paper = document(TABLE, numeric, scope, comparison)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[
                claim(paper, "C-NUM", numeric, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"]),
                claim(
                    paper,
                    "C-SCOPE",
                    scope,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={
                        "declared_universe": "the nine datasets",
                        "stated_count": 9,
                        "members": ["a", "b", "c"],
                        "universe_status": "RECOVERED",
                    },
                ),
                claim(
                    paper,
                    "C-CMP",
                    comparison,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    quantifier="all",
                    links=["L-ANCHOR-CMP"],
                    qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
                ),
            ],
            floats=[anchor()],
            links=[
                float_link("L-ANCHOR", "C-NUM", quantity_identity="Acc"),
                prose_cell("L-CELL", "C-NUM"),
                float_link("L-ANCHOR-CMP", "C-CMP"),
                rd_link("L-RD", "C-SCOPE", "RD002", "agg/nine"),
            ],
        )
    )
    assert one(findings, "PD001", "C-NUM").status is RuleStatus.PASS
    assert one(findings, "PD002", "C-SCOPE").status is RuleStatus.PASS
    pd003 = one(findings, "PD003", "C-NUM")
    assert pd003.status is RuleStatus.PASS
    assert "column=Acc" in pd003.reason and pd003.measurements["cell_value"] == "0.42"
    assert one(findings, "PD004", "C-CMP").status is RuleStatus.PASS
    assert one(findings, "PD006", "C-NUM").status is RuleStatus.PASS
    assert not failed(findings)


# --- S2: traceability is not truth -------------------------------------------------------------


def test_s2_traceable_and_false(tmp_path: Path) -> None:
    """S2: prose number differs from the printed cell, same declared quantity, identical
    declared precision => PD003 FAIL while PD001 PASSes."""
    text = r"Ours reaches 0.45 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"])],
            floats=[anchor(precision_declaration="round: 2")],
            links=[float_link("L-ANCHOR", "C1", quantity_identity="Acc"), prose_cell("L-CELL", "C1")],
        )
    )
    assert one(findings, "PD001", "C1").status is RuleStatus.PASS
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.FAIL
    assert "0.45" in pd003.reason and "0.42" in pd003.reason
    assert pd003.measurements["cell_value"] == "0.42"
    assert pd003.measurements["delta"] == pytest.approx(0.03)


# --- S3: scope inflation ----------------------------------------------------------------------


def test_s3_scope_inflation_fails_both_rules(tmp_path: Path) -> None:
    """S3: evidence covers 7 of 9 datasets, the claim says "all" => PD002 FAIL *and* PD005 FAIL,
    never only one."""
    text = r"We cover all datasets, listed as a, b, c."
    paper = document(text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd(
                    "RD002",
                    "agg/ours",
                    "PASS",
                    measurements={
                        "n_members": 7,
                        "n_exclusions": 2,
                        "n_exclusions_listed": 2,
                        "member_rule_grade": "DIRECT",
                    },
                )
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="SCOPE",
                    quantifier="all",
                    links=["L-RD"],
                    scope={
                        "declared_universe": "all datasets",
                        "stated_count": 9,
                        "members": ["a", "b", "c"],
                        "universe_status": "RECOVERED",
                    },
                )
            ],
            links=[rd_link("L-RD", "C1", "RD002", "agg/ours")],
        )
    )
    pd002 = one(findings, "PD002", "C1")
    pd005 = one(findings, "PD005", "C1")
    assert pd002.status is RuleStatus.FAIL
    assert "unit=aggregation" in pd002.reason
    assert pd005.status is RuleStatus.FAIL
    assert "agg/ours" in pd005.reason


# --- S4: a missing mapping is not a mismatch ----------------------------------------------------


def test_s4_untraceable_claim_never_fails(tmp_path: Path) -> None:
    """S4: claim with no resolvable link => PD001 INCONCLUSIVE, and every other rule for that
    claim is INCONCLUSIVE or NOT_APPLICABLE -- never FAIL."""
    text = r"Our method reaches 0.42 accuracy."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="NUMERIC_ATTRIBUTION",
                    links=[],
                    scope={"declared_universe": "our benchmark", "stated_count": 9},
                )
            ],
        )
    )
    assert one(findings, "PD001", "C1").status is RuleStatus.INCONCLUSIVE
    assert "untraceable is not false" in one(findings, "PD001", "C1").reason
    assert one(findings, "PD002", "C1").status is RuleStatus.INCONCLUSIVE
    assert one(findings, "PD003", "C1").status is RuleStatus.INCONCLUSIVE
    assert one(findings, "PD007", "C1").status is RuleStatus.NOT_APPLICABLE
    assert not failed(findings)


# --- S5: the value is in the other table ---------------------------------------------------------


def test_s5_value_outside_the_referenced_float(tmp_path: Path) -> None:
    """S5: the prose number exists, but in the float the reference does not point to => PD006
    FAIL and PD003 INCONCLUSIVE (the GMMVI C1 shape)."""
    text = r"Ours reaches 0.87 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, TABLE_OTHER, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[claim(paper, "C1", text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR"])],
            floats=[anchor()],
            links=[float_link("L-ANCHOR", "C1", quantity_identity="Acc")],
        )
    )
    pd006 = one(findings, "PD006", "C1")
    assert pd006.status is RuleStatus.FAIL
    assert pd006.measurements["carriers"] == ("table:2",)
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    # The attribution failure is PD006's; PD003 must not double-report it as a value mismatch.
    assert "PD006" in pd003.reason


# --- S6: a qualification is not a scope -----------------------------------------------------------


def test_s6_omitted_exclusion_fails_qualification_only(tmp_path: Path) -> None:
    """S6: the evidence carries an exclusion the claim's wording omits => PD005 FAIL while
    PD002 PASSes -- qualification and scope are different channels."""
    text = r"We compare the seven reported solutions."
    paper = document(text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd(
                    "RD002",
                    "agg/zamtrux",
                    "PASS",
                    measurements={
                        "n_members": 7,
                        "n_exclusions": 1,
                        "n_exclusions_listed": 1,
                        "member_rule_grade": "DIRECT",
                    },
                )
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="SCOPE",
                    links=["L-RD"],
                    qualifiers=[{"kind": "exclusion", "statement": "one run was dropped"}],
                    scope={
                        "declared_universe": "the seven solutions",
                        "stated_count": 7,
                        "unit": "comparison_member",
                        "members": ["ours", "theirs"],
                        "universe_status": "RECOVERED",
                    },
                )
            ],
            links=[rd_link("L-RD", "C1", "RD002", "agg/zamtrux")],
        )
    )
    assert one(findings, "PD002", "C1").status is RuleStatus.PASS
    pd005 = one(findings, "PD005", "C1")
    assert pd005.status is RuleStatus.FAIL
    assert "zamtrux" in pd005.reason
    # Contract I-1: an upstream PASS may never be described as an upstream INCONCLUSIVE.
    assert "upstream RD002 on these targets is INCONCLUSIVE" not in pd005.reason


# --- S7: rhetoric is out of the audited universe ----------------------------------------------------


def test_s7_rhetorical_claim_is_not_applicable(tmp_path: Path) -> None:
    """S7: purely rhetorical claim ("an order of magnitude more efficient", no object) => PD001
    NOT_APPLICABLE carrying `not_audited_reason`; no rule may emit FAIL."""
    text = r"Our method is an order of magnitude more efficient."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    links=[],
                    not_audited_reason="rhetorical comparison: no measured object is declared",
                )
            ],
        )
    )
    pd001 = one(findings, "PD001", "C1")
    assert pd001.status is RuleStatus.NOT_APPLICABLE
    assert "no measured object" in pd001.reason
    assert pd001.measurements["link_basis"] == ()
    assert not failed(findings)


# --- S8: a downstream FAIL caps PD; it never becomes PD's --------------------------------------------


def test_s8_downstream_fail_caps_pd003(tmp_path: Path) -> None:
    """S8: downstream RD001 FAIL for the cell the claim quotes => PD003 INCONCLUSIVE with the
    propagated reason; PD may not PASS and may not double-report a FAIL (§7.5's boundary)."""
    text = r"Ours reaches 0.45 accuracy, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd("RD001", "cell/acc-ours", "FAIL", reason="the printed cell disagrees with its artifact"),
                PASS_NINE,
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="NUMERIC_ATTRIBUTION",
                    links=["L-ANCHOR", "L-CELL", "L-RD"],
                )
            ],
            floats=[anchor(precision_declaration="round: 2")],
            links=[
                float_link("L-ANCHOR", "C1", quantity_identity="Acc"),
                prose_cell("L-CELL", "C1"),
                rd_link("L-RD", "C1", "RD001", "cell/acc-ours"),
            ],
        )
    )
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.INCONCLUSIVE
    assert "downstream RD001 on cell/acc-ours is FAIL" in pd003.reason
    assert "PD does not upgrade upstream certainty" in pd003.reason
    assert not failed(findings)
    assert not [f for f in findings if f.rule_id.startswith("RD")]


# --- S9: RD owns the tie; PD says so and stops ----------------------------------------------------------


def test_s9_downstream_inconclusive_blocks_pd004(tmp_path: Path) -> None:
    """S9: two identical printed values, both bold, different rows => RD007 owns it, so PD004 is
    INCONCLUSIVE with the downstream-free reason. PD does not eat RD's work."""
    text = r"Ours beats Base on every metric, see \autoref{tab:main}."
    paper = document(TABLE, text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd(
                    "RD007",
                    "table:1",
                    "INCONCLUSIVE",
                    reason="two identical bold values cannot be attributed to a single winner",
                )
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    quantifier="all",
                    links=["L-ANCHOR", "L-RD"],
                    qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
                )
            ],
            floats=[anchor()],
            links=[float_link("L-ANCHOR", "C1"), rd_link("L-RD", "C1", "RD007", "table:1")],
        )
    )
    pd004 = one(findings, "PD004", "C1")
    assert pd004.status is RuleStatus.INCONCLUSIVE
    assert "downstream-free" in pd004.reason
    assert "RD007" in pd004.reason
    assert pd004.measurements["downstream_status"] == "INCONCLUSIVE"
    assert not failed(findings)


# --- S10: a value failure, not a scope failure -------------------------------------------------------------


def test_s10_percentage_point_mismatch_is_a_value_failure(tmp_path: Path) -> None:
    """S10: the claim states a 2.1 improvement where the printed accuracy under the same declared
    quantity is 85.1 => PD003 FAIL (value/unit), PD002 PASS."""
    value_text = r"Ours improves accuracy by 2.1 over Base."
    scope_text = r"We report nine datasets."
    grid = r"""\begin{table}[t]
\centering
\begin{tabular}{lcc}
\toprule
 & Acc\textuparrow & RMSE\textdownarrow \\
\midrule
Ours & $85.1$ & $0.10$ \\
Base & $83.0$ & $0.12$ \\
\bottomrule
\end{tabular}
\caption{Main results.}\label{tab:main}
\end{table}"""
    paper = document(grid, value_text, scope_text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[
                claim(paper, "C1", value_text, form="NUMERIC_ATTRIBUTION", links=["L-ANCHOR", "L-CELL"]),
                claim(
                    paper,
                    "C2",
                    scope_text,
                    form="SCOPE",
                    links=["L-RD"],
                    scope={
                        "declared_universe": "the nine datasets",
                        "stated_count": 9,
                        "universe_status": "RECOVERED",
                    },
                ),
            ],
            floats=[anchor(precision_declaration="round: 1")],
            links=[
                float_link("L-ANCHOR", "C1", quantity_identity="Acc"),
                prose_cell("L-CELL", "C1"),
                rd_link("L-RD", "C2", "RD002", "agg/nine"),
            ],
        )
    )
    pd003 = one(findings, "PD003", "C1")
    assert pd003.status is RuleStatus.FAIL
    assert "both declare 'Acc'" in pd003.reason
    assert one(findings, "PD002", "C2").status is RuleStatus.PASS


# --- S11: same proposition, drifting scope ---------------------------------------------------------------


def test_s11_same_as_scope_drift(tmp_path: Path) -> None:
    """S11: two `same_as`-declared claims whose scopes differ => PD007 FAIL and PD004 PASS:
    the drift is a cross-section failure, not a support failure."""
    body = r"Ours beats Base on every metric in \autoref{tab:main}."
    dl = r"The DL solutions confirm that ours beats base on every metric."
    paper = document(TABLE, body, dl)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[PASS_NINE],
            claims=[
                claim(
                    paper,
                    "C1",
                    body,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    quantifier="all",
                    links=["L-ANCHOR-1"],
                    same_as=[{"claim": "C2", "basis": "declared"}],
                    scope={"declared_universe": "solutions"},
                    qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
                ),
                claim(
                    paper,
                    "C2",
                    dl,
                    form="COMPARATIVE",
                    predicate="beats",
                    subjects=["Ours", "Base"],
                    quantifier="all",
                    links=["L-ANCHOR-2"],
                    same_as=[{"claim": "C1", "basis": "declared"}],
                    scope={"declared_universe": "DL solutions"},
                    qualifiers=[{"kind": "comparison_basis", "statement": "per_column"}],
                ),
            ],
            floats=[anchor()],
            links=[float_link("L-ANCHOR-1", "C1"), float_link("L-ANCHOR-2", "C2")],
        )
    )
    assert one(findings, "PD004", "C1").status is RuleStatus.PASS
    assert one(findings, "PD004", "C2").status is RuleStatus.PASS
    pd007 = one(findings, "PD007", "C1|C2")
    assert pd007.status is RuleStatus.FAIL
    assert "no reconciliation" in pd007.reason
    assert pd007.measurements["pairing_basis"] == ("declared",)


# --- S12: ten members, seven effective -------------------------------------------------------------------


def test_s12_declared_count_with_exclusions_fails_both(tmp_path: Path) -> None:
    """S12: the author declares ten seeds and RD002 PASS confirms 10 members, but 3 are excluded,
    so the effective n is 7 => PD002 FAIL and PD005 FAIL; between them the two reasons name both
    the count and the excluded members (the GMMVI C5/C6 shape)."""
    text = r"All ten seeds are reported."
    paper = document(text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd(
                    "RD002",
                    "agg/sepyrux",
                    "PASS",
                    measurements={
                        "n_members": 10,
                        "n_exclusions": 3,
                        "n_exclusions_listed": 3,
                        "member_rule_grade": "DIRECT",
                    },
                )
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="SCOPE",
                    quantifier="all",
                    links=["L-RD"],
                    scope={
                        "declared_universe": "ten seeds",
                        "stated_count": 10,
                        "members": ["seed-1", "seed-2"],
                        "universe_status": "RECOVERED",
                    },
                )
            ],
            links=[rd_link("L-RD", "C1", "RD002", "agg/sepyrux")],
        )
    )
    pd002 = one(findings, "PD002", "C1")
    pd005 = one(findings, "PD005", "C1")
    assert pd002.status is RuleStatus.FAIL
    assert "effective counts after exclusions differ" in pd002.reason
    assert "agg/sepyrux (-3)" in pd002.reason
    assert pd002.measurements["n_targets_with_exclusions"] == 1
    assert pd005.status is RuleStatus.FAIL
    assert "sepyrux" in pd005.reason


# --- S13: the false-positive guard -----------------------------------------------------------------------


def test_s13_existential_enumeration_passes_both(tmp_path: Path) -> None:
    """S13: "some datasets (A, B, C)" where D also qualifies => PD002 PASS and PD005 PASS.
    A tool that only ever finds problems is not an auditor."""
    text = r"Some datasets, namely a, b, c, reach the threshold."
    paper = document(text)
    findings = audit_manifest_of(
        write_case(
            tmp_path,
            paper=paper,
            findings=[
                rd("RD002", "agg/enumerated", "PASS", measurements={"n_members": 3}),
                rd(
                    "RD002",
                    "agg/d",
                    "PASS",
                    measurements={
                        "n_members": 4,
                        "n_exclusions": 1,
                        "n_exclusions_listed": 1,
                        "member_rule_grade": "DIRECT",
                    },
                ),
            ],
            claims=[
                claim(
                    paper,
                    "C1",
                    text,
                    form="SCOPE",
                    quantifier="some",
                    subjects=["d"],
                    links=["L-RD"],
                    qualifiers=[
                        {"kind": "generic_coverage", "statement": "further datasets qualify but are not enumerated"}
                    ],
                    scope={
                        "declared_universe": "datasets reaching the threshold",
                        "stated_count": 3,
                        "members": ["a", "b", "c"],
                        "universe_status": "RECOVERED",
                    },
                )
            ],
            links=[rd_link("L-RD", "C1", "RD002", "agg/enumerated")],
        )
    )
    assert one(findings, "PD002", "C1").status is RuleStatus.PASS
    pd005 = one(findings, "PD005", "C1")
    assert pd005.status is RuleStatus.PASS
    assert "covered by the declared statement" in pd005.reason
    assert pd005.measurements["n_unnamed_targets"] == 1
    assert not failed(findings)
