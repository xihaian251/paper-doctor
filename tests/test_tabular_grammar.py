r"""The frozen tabular subset (Phase 0 §6, Phase 1 §6) and its recorded boundary.

Row parsing is scoped to the interior of the float's own table environment, the header is the
first row and only when its corner cell is empty -- or, since Phase 2, when a vertical merge in
the first column states that a leading label column exists -- and row decoration is removed in
place. Each test here pins one of those decisions, because each one is a place where a slightly
more convenient parser would have *guessed* a topology the source does not state.

Phase 2 §5 adds the disciplines that block discrimination depends on: a rule or a span only
counts at depth 0, a spanning command only opens a block when it provably spans the full width,
and the offsets in the block evidence are the author's source lines.
"""

from __future__ import annotations

from paper_doctor.latex_index import body_contains_literal, parse_table, plain_text, tabular_interior
from paper_doctor.rules import _number, literals

BODY = r"""
\centering
\begin{tabular}{lccc}
\toprule
{} & Acc\textuparrow & RMSE\textdownarrow & Time \\
\midrule
Ours   & $\mathbf{0.42}$ & $0.10$ & $3$ \\
Base   & $0.40$ & $\mathbf{0.12}$ & $9$ \\
\bottomrule
\end{tabular}
"""

BANNER = r"""
\begin{tabular}{cc|c|c}
\multicolumn{2}{c|}{Design Choice} & BreastCancer & Wine \\
\hline
Component & Estimator & 78.46 & 1431.09 \\
\end{tabular}
"""


def test_the_header_is_the_row_with_an_empty_corner() -> None:
    grid = parse_table(BODY)
    assert grid is not None
    assert grid.columns == ("Acc", "RMSE", "Time")
    assert grid.directions == ("up", "down", "")
    assert [row.label for row in grid.rows] == ["Ours", "Base"]
    assert grid.rows[0].cell(grid.column_index("Acc")) == "0.42"


def test_a_row_decoration_command_does_not_eat_the_row_it_prefixes() -> None:
    r"""`\midrule` sits on the same segment as the row after it. Dropping the segment is what
    made every real booktabs table unreadable."""
    grid = parse_table(BODY)
    assert grid is not None and grid.n_rows_dropped == 0


def test_a_double_backslash_inside_a_cell_is_not_a_row_boundary() -> None:
    body = r"""
\begin{tabular}{lc}
{} & Score \\
\hline
SEPYRUX & \thead{$1042.28$ \\ $\pm 2699.32$} \\
ZAMTRUX & \thead{$81.21$ \\ $\pm 1.13$} \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert [row.label for row in grid.rows] == ["SEPYRUX", "ZAMTRUX"]
    assert "2699.32" in grid.rows[0].cell(0)


def test_a_row_terminator_may_carry_a_spacing_argument() -> None:
    body = "\\begin{tabular}{lc}\n{} & A \\\\\nM & $1$ \\\\[2pt]\nN & $2$ \\\\\n\\end{tabular}"
    grid = parse_table(body)
    assert grid is not None
    assert [row.label for row in grid.rows] == ["M", "N"]


def test_a_two_level_banner_header_is_unrecoverable_not_reparsed() -> None:
    """Choosing a *later* row as the header would silently re-assign every column name."""
    assert parse_table(BANNER) is None


def test_a_body_without_a_table_environment_has_no_grid() -> None:
    assert parse_table(r"\caption{only prose} \input{something.tex}") is None
    assert tabular_interior(r"\caption{only prose}") is None


def test_an_unclosed_table_environment_is_unrecoverable() -> None:
    assert tabular_interior("\\begin{tabular}{lc}\n{} & A \\\\\nM & 1 \\\\\n") is None
    assert parse_table("\\begin{tabular}{lc}\n{} & A \\\\\nM & 1 \\\\\n") is None


def test_a_nested_table_cannot_close_the_outer_one_early() -> None:
    body = r"""
\begin{tabular}{lc}
{} & Value \\
\hline
Outer & \begin{tabular}{cc} X & 1 \\ Y & 2 \end{tabular} \\
Last & $7$ \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert [row.label for row in grid.rows] == ["Outer", "Last"]


def test_plain_text_removes_typesetting_but_never_a_digit() -> None:
    assert plain_text(r"$\mathbf{0.42}\,{\pm}\,0.01$") == "0.42 0.01"
    assert plain_text(r"\textbf{Best}") == "Best"
    # Phase 3 §5 D1: a thin space between digit groups is the thousands separator LaTeX prints,
    # so `1\,000` is one number. Reading it as two fragments made a table that prints `$26\,048$`
    # state that it does not print 26048.
    assert plain_text(r"1\,000") == "1000"
    assert plain_text(r"$26\,048$") == "26048"
    assert plain_text(r"$1\,200\,000$") == "1200000"
    # A comma between digits is NOT collapsed: `[64,512]` is an interval and `{0,1,2}` is a list,
    # and the digits alone do not say which. Ambiguous text keeps its ambiguity.
    assert plain_text(r"$\mathrm{UniformInt}[64,512]$") == "UniformInt [64,512]"
    assert plain_text(r"$0,1,2$") == "0,1,2"


def test_digit_grouping_is_read_as_one_number_by_the_literal_extractor() -> None:
    """The separator fix has to reach the numbers the rules compare, not only the display text."""
    assert literals(r"$26\,048$") == ("26048",)
    assert _number(r"$723\,412$") == 723412.0
    assert body_contains_literal(r"Adult & $26\,048$ & 256 \\", "26048")
    assert not body_contains_literal(r"Adult & $26\,048$ & 256 \\", "26")


def test_a_header_that_names_its_row_label_column_is_readable() -> None:
    """Phase 3 §5 D2: `Name & A & B` with no merges is the common layout, and it has one reading.

    The column spec here declares four columns while every row prints three, which is what a
    stray column letter in a real paper looks like; the self-consistent row count, not the spec,
    is what licenses the reading. A table whose rows disagree on cell count stays unreadable.
    """
    body = r"""
\begin{tabular}{llcc}
\toprule
Name & Train & Test \\
\midrule
Adult & $26\,048$ & $16\,281$ \\
Diamond & $34\,521$ & $10\,788$ \\
\bottomrule
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.columns == ("Train", "Test")
    assert grid.n_label_columns == 1
    assert [(row.label, row.cells) for row in grid.rows] == [
        ("Adult", ("26048", "16281")),
        ("Diamond", ("34521", "10788")),
    ]
    assert grid.n_blocks == 1

    # Rows disagree with the header, so the header may be a group-span row after all: refused.
    spanning = r"""
\begin{tabular}{cccc}
\toprule
\multicolumn{2}{c}{Train} & \multicolumn{2}{c}{Test} \\
\cmidrule(lr){1-2} \cmidrule(lr){3-4}
Size & Ratio & Size & Ratio \\
Adult & 0.6 & $26\,048$ & 0.4 \\
\bottomrule
\end{tabular}
"""
    assert parse_table(spanning) is None


def test_a_merged_cell_is_read_as_the_text_it_prints() -> None:
    r"""Phase 3 §5 D6: `\multirow`'s geometry arguments are never printed.

    `\multirow{ 2}{*}{Maps Routing}` puts `Maps Routing` on the page and nothing else, so the row is
    addressable by that name. Before the two parameter groups were dropped the label read
    `2 * Maps Routing` and the value cell `$6.5$M` read as `2 * 6.5 M` -- whose first number is 2,
    which is how a table that prints 6.5 came to be scored against a claim that states 2.
    """
    assert plain_text(r"\multirow{ 2}{*}{Maps Routing}") == "Maps Routing"
    assert plain_text(r"\multirow[t]{3}{1.5cm}{Ours}") == "Ours"
    assert _number(r"\multirow{2}{*}{$6.5$M}") == 6.5

    body = r"""
\begin{tabular}{lcc}
\toprule
 & Objects & Size \\
\midrule
\multirow{ 2}{*}{Maps Routing}
& \multirow{ 2}{*}{$6.5$M}
& $\mathbf{0.1582}$
\\
& & $0.1601$ \\
\bottomrule
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.columns == ("Objects", "Size")
    assert [(row.label, row.cells) for row in grid.rows] == [
        ("Maps Routing", ("6.5 M", "0.1582")),
        ("Maps Routing", ("", "0.1601")),
    ]


def test_a_color_declaration_prints_nothing() -> None:
    r"""Phase 3 §5 D7: a painted header cell is addressed by the name it shows, not by its paint.

    `{\transparent{1.0}\cellcolor[HTML]{C2DAEA}} {\color{black} $\mathrm{XGBoost}$}` prints
    `XGBoost`. Left in, the column name carried the colour model and its hex digits, so an author
    declaring `column=XGBoost` referenced a column the reader claimed the table did not have. A
    command that paints *and* prints its content (`\textcolor`) keeps that content -- and the colour
    name that stays beside it is a word, never a digit, so it cannot be read as the cell's value.
    """
    assert plain_text(r"{\transparent{1.0}\cellcolor[HTML]{C2DAEA}} {\color{black} XGBoost}") == "XGBoost"
    assert plain_text(r"\textcolor{red}{0.42}") == "red 0.42"
    assert _number(r"\textcolor{red}{0.42}") == 0.42


def test_a_row_label_carried_by_a_merge_makes_that_row_unaddressable() -> None:
    """A merge that covers two quantity rows states one label for both -- so neither is chosen.

    This is the shape of a table whose caption says "RMSE (upper rows) and training times (lower
    rows)". Returning the first candidate would let a claim about training times be scored against
    the RMSE cell, which is a false FAIL dressed up as a finding. The honest answer is that the
    evidence on file does not decide which row the claim speaks about.
    """
    body = r"""
\begin{tabular}{lcc}
\toprule
 & A-and-B & Third \\
\midrule
\multirow{2}{*}{Maps Routing} & \multirow{2}{*}{$6.5$M} & $\mathbf{0.1582}$ \\
& & $28$m \\
\bottomrule
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert len(grid.rows) == 2
    assert grid.row("Maps Routing") is None
    assert grid.row("Maps Routing", block="b1") is None
    assert grid.blocks_for("Maps Routing") == ("b1",)


# --- Phase 2 §5: the disciplines block discrimination is built on -----------------------------


def test_a_leading_minus_sign_is_never_read_as_decoration() -> None:
    r"""GMMVI Table 8's TALOS block prints negative ELBOs. Dropping the sign would turn a
    worst-value row into a best-value row while leaving every digit intact."""
    body = r"""
\begin{tabular}{lcc}
{} & A \textdownarrow & B \\
TALOS & $\mathbf{\num{-24.32}}$ & $-0.5$ \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.rows[0].cells == ("-24.32", "-0.5")


def test_an_escaped_ampersand_is_not_a_column_boundary() -> None:
    body = r"""
\begin{tabular}{lcc}
{} & A & B \\
X \& Y & $1$ & $2$ \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.rows[0].label == "X & Y"
    assert grid.n_rows_dropped == 0


def test_a_double_dash_stays_a_missing_value_and_is_never_coerced() -> None:
    body = r"""
\begin{tabular}{lcc}
{} & A & B \\
\hline
XGBoost & $0.924$ & -- \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.rows[0].cells == ("0.924", "--")


def test_a_partial_width_multicolumn_does_not_open_a_block() -> None:
    r"""Only a span that provably covers the whole row is a group header. A two-column span in a
    four-column table is a merged *cell*; its row cannot be given a label and value columns at
    the same time, so it is counted as dropped instead of silently re-topologised."""
    body = r"""
\begin{tabular}{lccc}
{} & A & B & C \\
\midrule
\multicolumn{2}{c}{Paired} & 1 & 2 \\
Real & $3$ & $4$ & $5$ \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.n_blocks == 1
    assert [row.label for row in grid.rows] == ["Real"]
    assert grid.n_rows_dropped == 1
    assert grid.block_basis("b1").startswith("midrule at ")


def test_a_rule_inside_a_nested_group_is_not_a_block_boundary() -> None:
    r"""The inner table's `\hline` belongs to the nested environment, not to the outer grid."""
    body = r"""
\begin{tabular}{lc}
{} & Value \\
Outer & \begin{tabular}{cc} X & 1 \\ \hline Y & 2 \end{tabular} \\
Last & $7$ \\
\end{tabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.n_blocks == 1
    assert [row.label for row in grid.rows] == ["Outer", "Last"]


def test_a_nicetabular_block_states_the_label_columns() -> None:
    r"""`\Block{2-1}` is NiceTabular's own statement that the first column groups two rows.
    Two label columns are read off that geometry; nothing about the words is consulted."""
    body = r"""
\begin{NiceTabular}{llc}
Experiment & Metric & Value \\
\Block{2-1}{Alpha} & m1 & $1$ \\
 & m2 & $2$ \\
\end{NiceTabular}
"""
    grid = parse_table(body)
    assert grid is not None
    assert grid.n_label_columns == 2
    assert grid.columns == ("Value",)
    assert [row.label for row in grid.rows] == ["m1", "m2"]
    assert grid.n_blocks == 1
    basis = grid.block_basis("b1")
    assert 'merged cell spanning 2 rows = "Alpha"' in basis
    assert "(1 label column)" in basis


def test_a_typesetting_command_argument_is_not_read_as_cell_content() -> None:
    r"""`\rotatebox{65}{\sc Samtrux}` names a column; the angle is an argument. Taking the first
    brace group after a typesetting command produced "65 Samtrux"."""
    assert plain_text(r"\rotatebox{65}{\sc Zamtrux}") == "Zamtrux"
    assert plain_text(r"\thead{$\mathbf{\num{78.01}}$ \\ $\pm \num{0.02}$}") == "78.01 0.02"


def test_block_evidence_points_at_the_authors_own_source_lines() -> None:
    """The float body is not the file: offsets must be rebased through the body's own newline
    count, or a reason would cite a line the author never wrote."""
    body = "\n".join(
        [
            r"\caption{Repeats}",
            r"\begin{tabular}{lc}",
            r"{} & Score \\",
            r"\midrule",
            r"A & $1$ \\",
            r"\midrule",
            r"B & $2$ \\",
            r"\end{tabular}",
        ]
    )
    grid = parse_table(body, locate=lambda offset: ("paper.tex", body.count("\n", 0, offset) + 1))
    assert grid is not None
    assert grid.n_blocks == 2
    assert grid.block_basis("b1") == "midrule at paper.tex:4"
    assert grid.block_basis("b2") == "midrule at paper.tex:6"
    assert [row.label for row in grid.rows] == ["A", "B"]
