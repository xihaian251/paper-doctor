r"""Phase 2 §4: the cheapest falsifiable artifact is the real-corpus block oracle.

Two real tables print the same row label more than once:

* RTDL Table 4 (`data/table_nn_gbdt.tex`, `tab:nn-gbdt`) repeats XGBoost / CatBoost /
  FT-Transformer under two `\multicolumn{12}{c}{...}` group headers separated by `\midrule`.
* GMMVI Table 8 (`arxiv.tex:1014`, `tab:exp3_full`) repeats `-ELBO` eleven times under eleven
  `\Block{2-1}{\thead{Experiment}}` merged cells separated by `\hline`; the merged cell's second
  row names a different metric per experiment (`MMD` five times, `Modes` four, then `MSE`, `H(q)`).

Every expectation below was transcribed from those source files, not from the parser. If an
assertion here fails, the block discriminator is wrong and no downstream rule may be patched to
compensate -- the same discipline as the Phase 1 float oracle.

The oracle asserts *addressability only*: which structural block a row sits in, and what that
block's structural evidence is. It asserts no meaning for a block.
"""

from __future__ import annotations

from pathlib import Path

from paper_doctor.latex_index import LatexIndex, build_index, parse_table

REPO = Path(__file__).resolve().parents[1]
GMMVI_ROOT = REPO / "phase0" / "sources" / "2209.11533v2.tex"
RTDL_ROOT = REPO / "phase0" / "sources" / "2106.11959.tex"


def _grid(index: LatexIndex, label: str):
    """Parse the float's own body with the index supplying absolute (file, line) for every offset."""
    record = index.resolve_label(label)
    assert record is not None, f"{label} is not in the frozen float index"
    body = index.float_body_text(record)
    return parse_table(body, locate=lambda offset: index.position_to_source(record.begin_offset + offset))


def test_rtdl_tables_are_indexed_by_the_frozen_corpus() -> None:
    assert RTDL_ROOT.is_dir(), RTDL_ROOT
    assert GMMVI_ROOT.is_dir(), GMMVI_ROOT


# --------------------------------------------------------------------- RTDL Table 4

RTDL_COLUMNS = ("CA", "AD", "HE", "JA", "HI", "AL", "EP", "YE", "CO", "YA", "MI")
RTDL_DIRECTIONS = ("down", "up", "up", "up", "up", "up", "up", "down", "up", "down", "down")


def rtdl_table4() -> LatexIndex:
    return build_index(RTDL_ROOT, RTDL_ROOT / "main.tex")


def test_rtdl_table4_topology_is_recovered() -> None:
    grid = _grid(rtdl_table4(), "tab:nn-gbdt")
    assert grid is not None
    assert grid.columns == RTDL_COLUMNS
    assert grid.directions == RTDL_DIRECTIONS
    assert grid.n_label_columns == 1
    # The two group headers are structure, not rows that failed to parse.
    assert grid.n_rows_dropped == 0


def test_rtdl_table4_repeated_labels_are_two_blocks_not_one_ambiguous_row() -> None:
    grid = _grid(rtdl_table4(), "tab:nn-gbdt")
    assert grid.n_blocks == 2
    assert [(row.label, row.block_key) for row in grid.rows] == [
        ("XGBoost", "b1"),
        ("CatBoost", "b1"),
        ("FT-Transformer", "b1"),
        ("XGBoost", "b2"),
        ("CatBoost", "b2"),
        ("ResNet", "b2"),
        ("FT-Transformer", "b2"),
    ]
    # An unqualified lookup of a label that lives in two blocks resolves to neither.
    assert grid.row("XGBoost") is None
    assert grid.blocks_for("XGBoost") == ("b1", "b2")
    # A label that occurs once is still addressable without a block.
    assert grid.row("ResNet") is not None and grid.row("ResNet").block_key == "b2"


def test_rtdl_table4_block_identity_comes_from_the_multicolumn_group_headers() -> None:
    grid = _grid(rtdl_table4(), "tab:nn-gbdt")
    first = grid.block_basis("b1")
    second = grid.block_basis("b2")
    assert 'multicolumn group header "Default hyperparameters"' in first
    assert "data/table_nn_gbdt.tex:5" in first
    assert 'multicolumn group header "Tuned hyperparameters"' in second
    assert "data/table_nn_gbdt.tex:11" in second
    assert "midrule" in second  # the rule that closes b1 and opens b2
    assert first != second


def test_rtdl_table4_cells_are_addressable_per_block() -> None:
    grid = _grid(rtdl_table4(), "tab:nn-gbdt")
    ye = grid.column_index("YE")
    al = grid.column_index("AL")
    assert ye is not None and al is not None
    assert grid.row("FT-Transformer", "b1").cell(ye) == "8.727"
    assert grid.row("FT-Transformer", "b2").cell(ye) == "8.751"
    assert grid.row("XGBoost", "b1").cell(al) == "0.924"
    # The tuned block prints `--` for AL. A missing value is not a zero and not a row drop.
    assert grid.row("XGBoost", "b2").cell(al) == "--"
    assert grid.row("XGBoost", "b9") is None


# --------------------------------------------------------------------- GMMVI Table 8

GMMVI_MODELS = (
    "Samtrux",
    "Samtrox",
    "Samtron",
    "Samyrux",
    "Samyrox",
    "Samyron",
    "Sepyfux",
    "Sepyrux",
    "Zamtrux",
)

# Transcribed from arxiv.tex lines 1031, 1054, 1077, 1100, 1123, 1146, 1169, 1192, 1215, 1238,
# 1261: the second row of each of the eleven merged-cell blocks.
GMMVI_METRIC_SEQUENCE = (
    "-ELBO",
    "MMD",
    "-ELBO",
    "MMD",
    "-ELBO",
    "MMD",
    "-ELBO",
    "MMD",
    "-ELBO",
    "MMD",
    "-ELBO",
    "Modes",
    "-ELBO",
    "Modes",
    "-ELBO",
    "Modes",
    "-ELBO",
    "Modes",
    "-ELBO",
    "MSE",
    "-ELBO",
    "H(q)",
)


def gmmvi_index() -> LatexIndex:
    return build_index(GMMVI_ROOT, GMMVI_ROOT / "arxiv.tex")


def test_gmmvi_table8_topology_is_recovered_from_nicetabular() -> None:
    grid = _grid(gmmvi_index(), "tab:exp3_full")
    assert grid is not None
    # Column 1 is carried by a two-row merge and column 2 names the metric, so the value
    # columns start at 3. That is read off the merge structure, not off the words.
    assert grid.n_label_columns == 2
    assert grid.columns == GMMVI_MODELS
    assert grid.n_rows_dropped == 0


def test_gmmvi_table8_metric_labels_are_eleven_blocks_not_one_ambiguous_row() -> None:
    grid = _grid(gmmvi_index(), "tab:exp3_full")
    assert grid.n_blocks == 11
    assert [row.block_key for row in grid.rows] == [f"b{i}" for i in range(1, 12) for _ in (0, 1)]
    assert tuple(row.label for row in grid.rows) == GMMVI_METRIC_SEQUENCE
    # Every block's first row prints the same label, so the bare lookup resolves to neither.
    assert grid.blocks_for("-ELBO") == tuple(f"b{i}" for i in range(1, 12))
    assert grid.row("-ELBO") is None
    # The second label is only repeated inside its own family of experiments.
    assert grid.blocks_for("MMD") == tuple(f"b{i}" for i in range(1, 6))
    assert grid.blocks_for("Modes") == tuple(f"b{i}" for i in range(6, 10))
    assert grid.row("MMD") is None
    assert grid.row("MSE") is not None and grid.row("MSE").block_key == "b10"


def test_gmmvi_table8_block_identity_comes_from_the_merged_cells() -> None:
    grid = _grid(gmmvi_index(), "tab:exp3_full")
    basis1 = grid.block_basis("b1")
    basis2 = grid.block_basis("b2")
    assert "merged cell spanning 2 rows" in basis1
    assert "BreastCancer" in basis1
    assert "arxiv.tex:1020" in basis1
    assert "BreastCancer (minibatches)" in basis2
    assert "arxiv.tex:1043" in basis2
    assert "hline" in basis2


def test_gmmvi_table8_cells_are_addressable_per_block() -> None:
    grid = _grid(gmmvi_index(), "tab:exp3_full")
    samtrux = grid.column_index("Samtrux")
    assert samtrux is not None
    assert "78.01" in grid.row("-ELBO", "b1").cell(samtrux)
    assert "79.66" in grid.row("-ELBO", "b2").cell(samtrux)
    assert "585.10" in grid.row("-ELBO", "b3").cell(samtrux)
    assert "1.1e-03" in grid.row("MMD", "b1").cell(samtrux)


def test_block_discrimination_does_not_touch_single_block_tables() -> None:
    """A table with no group header and no merge keeps exactly the Phase 1 shape."""
    grid = _grid(rtdl_table4(), "tab:node")
    assert grid is not None and grid.n_blocks == 1
    assert [row.label for row in grid.rows] == ["NODE", "ResNet", "FT-Transformer"]
    assert [row.block_key for row in grid.rows] == ["b1", "b1", "b1"]
    assert grid.row("FT-Transformer") is grid.rows[2]
    assert grid.row("FT-Transformer", "b1") is grid.rows[2]
    # The only structure that delimits b1 is the rule under the header, and it says so.
    assert grid.block_basis("b1") == "midrule at data/table_node.tex:4"
