"""Frozen oracle for the LaTeX float index (Phase 1 brief, section 5).

The numbers below are transcribed from the Phase 0 artifacts
`phase0/work/gmmvi-float-ref.json` and `phase0/work/rtdl-float-ref.json`, which were
produced against the read-only checkouts under `phase0/sources/`. They are the
acceptance criterion for C1's linking mechanism: if an assertion here fails, the
float-index implementation is wrong, and no downstream rule may be patched to
compensate.

Fixtures are real corpora, read-only. A missing corpus is a hard error, never a skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_doctor.latex_index import LatexIndex, build_index

REPO = Path(__file__).resolve().parents[1]
GMMVI_ROOT = REPO / "phase0" / "sources" / "2209.11533v2.tex"
RTDL_ROOT = REPO / "phase0" / "sources" / "2106.11959.tex"


def _load(root: Path, main: str) -> LatexIndex:
    if not root.is_dir():
        raise FileNotFoundError(f"read-only corpus fixture missing: {root}")
    return build_index(root, root / main)


@pytest.fixture(scope="module")
def gmmvi() -> LatexIndex:
    return _load(GMMVI_ROOT, "arxiv.tex")


@pytest.fixture(scope="module")
def rtdl() -> LatexIndex:
    return _load(RTDL_ROOT, "main.tex")


# --------------------------------------------------------------------------- GMMVI

GMMVI_TABLES = [
    (1, 374, ("table:algorithmicChoices",)),
    (2, 400, ("tab:exp1",)),
    (3, 430, ("tab:exp1_eval",)),
    (4, 446, ("tab:exp2",)),
    (5, 565, ("tab:exp3",)),
    (6, 873, ("tab:vips_comparisons",)),
    (7, 927, ("tab:hyperparameters",)),
    (8, 1014, ("tab:exp3_full",)),
    (9, 1276, ("tab:exp3_accuracy",)),
]

GMMVI_FIGURES = [
    (1, 899, ("fig:stm20_marginals",)),
    (2, 907, ("fig:MatComparisons_stm20", "fig:MatComparisons_stm300")),
    (3, 1382, ("fig:learningCurves",)),
]


def test_gmmvi_float_counts(gmmvi: LatexIndex) -> None:
    assert len(gmmvi.tables) == 9
    assert len(gmmvi.figures) == 3
    assert gmmvi.max_float_nesting == 1
    assert gmmvi.unterminated_floats == ()
    assert gmmvi.body_found is True


def test_gmmvi_numbering_in_document_order(gmmvi: LatexIndex) -> None:
    assert [(f.number, f.begin_line, f.labels) for f in gmmvi.tables] == GMMVI_TABLES
    assert [(f.number, f.begin_line, f.labels) for f in gmmvi.figures] == GMMVI_FIGURES
    assert all(f.source_file == "arxiv.tex" for f in gmmvi.floats)
    assert all(f.caption_present for f in gmmvi.floats)


def test_gmmvi_label_resolution(gmmvi: LatexIndex) -> None:
    tab_exp1 = gmmvi.resolve_label("tab:exp1")
    tab_exp1_eval = gmmvi.resolve_label("tab:exp1_eval")
    assert tab_exp1 is not None and (tab_exp1.kind, tab_exp1.number) == ("table", 2)
    assert tab_exp1_eval is not None and (tab_exp1_eval.kind, tab_exp1_eval.number) == ("table", 3)
    assert tab_exp1_eval.begin_line == 430


def test_gmmvi_input_flattening_is_absolute_line_anchored(gmmvi: LatexIndex) -> None:
    assert [(c.file, c.start_line, len(c.text)) for c in gmmvi.chunks] == [
        ("arxiv.tex", 1, 66),
        ("math_commands.tex", 1, 10738),
        ("arxiv.tex", 10, 135887),
    ]


def test_gmmvi_ref_sites_total(gmmvi: LatexIndex) -> None:
    assert len(gmmvi.ref_sites) == 114
    assert len(gmmvi.unresolved_refs) == 95


def test_fm_p11_macro_definition_sites_are_not_claims(gmmvi: LatexIndex) -> None:
    """The 32 `\\ref{#1}`-style sites live in the preamble `\\input` of math_commands.tex."""
    preamble = [s for s in gmmvi.ref_sites if not s.in_body]
    assert len(preamble) == 32
    assert {s.source_file for s in preamble} == {"math_commands.tex"}

    claims = gmmvi.claim_sites()
    assert len(claims) == 82
    assert {s.source_file for s in claims} == {"arxiv.tex"}
    assert not [s for s in claims if s.target.startswith("#")]


def test_c1_reference_attribution_mechanism(gmmvi: LatexIndex) -> None:
    """`arxiv.tex:426` attributes 78.69 to Table~\\ref{tab:exp1_eval} (Table 3), but the
    value is printed at :408 inside the float labelled tab:exp1 (Table 2).

    This is the deterministic fact PD006 needs. The index supplies resolution plus
    literal presence in the resolved float; it draws no conclusion.
    """
    table2 = gmmvi.resolve_label("tab:exp1")
    table3 = gmmvi.resolve_label("tab:exp1_eval")
    assert table2 is not None and table3 is not None

    assert "78.69" in gmmvi.float_body_text(table2)
    assert "78.69" not in gmmvi.float_body_text(table3)

    sites = [s for s in gmmvi.claim_sites() if s.line == 426 and s.target == "tab:exp1_eval"]
    assert sites, "expected a \\ref{{tab:exp1_eval}} site at arxiv.tex:426"
    assert all(s.resolved_kind == "table" and s.resolved_number == 3 for s in sites)


def test_gmmvi_never_referenced_label(gmmvi: LatexIndex) -> None:
    assert gmmvi.never_referenced_labels == ("tab:exp3_accuracy",)


# ----------------------------------------------------------------------------- RTDL

RTDL_TABLES = [
    (1, 296, ("tab:datasets",)),
    (2, 335, ("tab:neural-networks",)),
    (3, 367, ("tab:node",)),
    (4, 390, ("tab:nn-gbdt",)),
    (5, 467, ("tab:ablation",)),
    (6, 486, ("tab:feature-importances",)),
    (7, 528, ("tab:S-datasets",)),
    (8, 571, ("tab:S-training-times",)),
    (9, 615, ("tab:S-tuning-time-budget",)),
    (10, 666, ("tab:S-default-config",)),
    (11, 699, ("tab:S-transformer-space",)),
    (12, 743, ("tab:S-resnet-space",)),
    (13, 777, ("tab:S-mlp-space",)),
    (14, 811, ("tab:S-xgboost-space",)),
    (15, 849, ("tab:S-catboost-space",)),
    (16, 879, ("tab:S-snn-space",)),
    (17, 924, ("tab:S-tabnet-space",)),
    (18, 956, ("tab:S-grownet-space",)),
    (19, 990, ("tab:S-dcn2-space",)),
    (20, 1023, ("tab:S-autoint-space",)),
    (21, 1097, ("tab:S-ablation",)),
    (22, 1113, ("tab:S-additional-datasets",)),
    (23, 1130, ("tab:S-additional-results",)),
]

RTDL_FIGURES = [
    (1, 222, ("fig:arch",)),
    (2, 229, ("fig:blocks",)),
]

RTDL_NEVER_REFERENCED = (
    "tab:S-autoint-space",
    "tab:S-catboost-space",
    "tab:S-datasets",
    "tab:S-dcn2-space",
    "tab:S-grownet-space",
    "tab:S-mlp-space",
    "tab:S-resnet-space",
    "tab:S-snn-space",
    "tab:S-tabnet-space",
    "tab:S-transformer-space",
    "tab:S-xgboost-space",
)

RTDL_UNRESOLVED_TARGETS = [
    "alg:S-random-tree-construction",
    "eq:mlp",
    "eq:resnet",
    "fig:synthetic",
    "sec:S-architecture",
    "sec:ablation",
    "sec:implementation-details",
    "sec:intriguing-property",
    "sec:synthetic",
    "tab:S-ensembles",
    "tab:S-single-models",
]


def test_rtdl_float_counts(rtdl: LatexIndex) -> None:
    assert len(rtdl.tables) == 23
    assert len(rtdl.figures) == 2
    assert rtdl.max_float_nesting == 1
    assert rtdl.unterminated_floats == ()
    assert rtdl.body_found is True


def test_rtdl_numbering_in_document_order(rtdl: LatexIndex) -> None:
    assert [(f.number, f.begin_line, f.labels) for f in rtdl.tables] == RTDL_TABLES
    assert [(f.number, f.begin_line, f.labels) for f in rtdl.figures] == RTDL_FIGURES
    assert all(f.caption_present for f in rtdl.floats)


def test_rtdl_cross_file_inlining_keeps_floats_in_document_order(rtdl: LatexIndex) -> None:
    assert len(rtdl.chunks) == 25
    assert [(c.file, c.start_line) for c in rtdl.chunks[:6]] == [
        ("main.tex", 1),
        ("data/table_datasets.tex", 1),
        ("main.tex", 302),
        ("data/table_neural_networks.tex", 1),
        ("main.tex", 348),
        ("data/table_node.tex", 1),
    ]
    inlined = {c.file for c in rtdl.chunks}
    assert "data/table_ablation.tex" in inlined
    assert "data/table_ablation_with_std.tex" in inlined


def test_rtdl_float_body_text_reaches_inlined_table_files(rtdl: LatexIndex) -> None:
    """D8 and D6 depend on a `\\input`-separated table being part of its float's text."""
    datasets = rtdl.resolve_label("tab:datasets")
    assert datasets is not None and datasets.number == 1
    assert "699" in rtdl.float_body_text(datasets)

    ablation = rtdl.resolve_label("tab:ablation")
    assert ablation is not None and (ablation.number, ablation.begin_line) == (5, 467)
    # RTDL marks best-in-column with `$\mathbf{...}$`, not with `\textbf{...}` (GMMVI's
    # form). The index reports the literal float text; it does not normalize marks.
    assert "$\\mathbf{" in rtdl.float_body_text(ablation)

    node = rtdl.resolve_label("tab:node")
    assert node is not None and node.number == 3
    body = rtdl.float_body_text(node)
    assert "8.716" in body and "8.751" in body


def test_rtdl_ref_sites_are_all_in_body(rtdl: LatexIndex) -> None:
    assert len(rtdl.ref_sites) == 37
    assert len(rtdl.claim_sites()) == 37
    assert {s.source_file for s in rtdl.ref_sites} == {"main.tex"}


def test_rtdl_unresolved_and_dangling_reference_surface(rtdl: LatexIndex) -> None:
    assert sorted({s.target for s in rtdl.unresolved_refs}) == RTDL_UNRESOLVED_TARGETS
    assert len(rtdl.unresolved_refs) == 13
    assert rtdl.never_referenced_labels == RTDL_NEVER_REFERENCED


def test_unresolved_refs_are_reported_not_guessed(rtdl: LatexIndex) -> None:
    """A `\\ref` to a non-float (section/equation/algorithm) resolves to nothing here.

    The index does not resolve formula/section/appendix references merely because the
    macro exists; the caller must treat UNRESOLVED as a boundary, not as a value.
    """
    for site in rtdl.ref_sites:
        if site.target.startswith(("sec:", "eq:", "alg:", "fig:synthetic")):
            assert site.resolved_kind == "UNRESOLVED"
            assert site.resolved_number == 0
