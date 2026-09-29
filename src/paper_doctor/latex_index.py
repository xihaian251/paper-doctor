"""Deterministic LaTeX float index.

This is the only non-semantic linker Paper Doctor is allowed (Phase 0 contract: a
`\\ref` resolves to a float number by document order, nothing more). It parses the
frozen deterministic subset: `\\input` flattening, the four float environments,
`\\label` inside a float, and `\\ref`/`\\autoref` sites.

Explicitly out of scope, by design: no TeX engine, no macro expansion, no execution
of arbitrary TeX, no resolution of formula/section/appendix references, no value
proximity, no semantic inference. A structure this module cannot resolve stays
unresolved and is reported as such; the caller turns it into UNKNOWN.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

FLOAT_ENVS: tuple[str, ...] = ("table*", "table", "figure*", "figure")

_BEGIN_FLOAT = re.compile(r"\\begin\{(table\*|table|figure\*|figure)\}")
_END_FLOAT = re.compile(r"\\end\{(table\*|table|figure\*|figure)\}")
_ANY_FLOAT = re.compile(r"\\(?:begin|end)\{(?:table\*|table|figure\*|figure)\}")
_LABEL = re.compile(r"\\label\{([^}]*)\}")
_CAPTION = re.compile(r"\\caption\s*(?:\[[^\]]*\])?\{")
_REF = re.compile(r"\\(autoref|ref)\{([^}]*)\}")
_INPUT = re.compile(r"\\input\{([^}]*)\}")
_BEGIN_DOC = re.compile(r"\\begin\{document\}")
_MAX_CHUNKS = 256


def strip_comments(text: str) -> str:
    """Drop unescaped `%` to end-of-line. Blank content is kept so line numbers hold."""
    out = []
    for line in text.split("\n"):
        match = re.search(r"(?<!\\)%", line)
        out.append(line[: match.start()] if match else line)
    return "\n".join(out)


@dataclass(frozen=True)
class Chunk:
    """A contiguous span of the flattened document, anchored to one physical file."""

    file: str
    start_line: int
    text: str


@dataclass(frozen=True)
class FloatRecord:
    """One float environment in document order, with the numbers LaTeX would print."""

    kind: str  # "table" | "figure"
    number: int
    env: str  # exact environment name, e.g. "table*"
    source_file: str
    begin_line: int
    labels: tuple[str, ...]
    caption_present: bool
    in_body: bool
    begin_offset: int
    end_offset: int
    terminated: bool

    @property
    def anchor_id(self) -> str:
        return f"{self.kind}:{self.number}"


@dataclass(frozen=True)
class RefSite:
    """One `\\ref`/`\\autoref` occurrence and what the float index resolves it to."""

    macro: str  # "\ref" | "\autoref"
    target: str
    source_file: str
    line: int
    resolved_kind: str  # "table" | "figure" | "UNRESOLVED"
    resolved_number: int  # 0 when unresolved
    in_body: bool


@dataclass(frozen=True)
class LatexIndex:
    root: str
    main_file: str
    chunks: tuple[Chunk, ...] = ()
    floats: tuple[FloatRecord, ...] = ()
    ref_sites: tuple[RefSite, ...] = ()
    max_float_nesting: int = 0
    unterminated_floats: tuple[str, ...] = ()
    body_found: bool = False
    body_sites: frozenset[tuple[str, int]] = frozenset()
    _document: str = ""
    _chunk_starts: tuple[int, ...] = ()
    _label_index: dict[str, FloatRecord] = field(default_factory=dict, repr=False)

    # --- queries used by the rules -------------------------------------------------
    def position_to_source(self, position: int) -> tuple[str, int]:
        """(file, absolute line) of an offset into the flattened document.

        The block discriminator needs to name the source line of the rule or the merged cell that
        opened a block, so a parser that only holds a float body can still emit a source locator.
        """
        if not self.chunks:
            return "", 0
        low, high = 0, len(self.chunks) - 1
        while low < high:
            mid = (low + high + 1) // 2
            if self._chunk_starts[mid] <= position:
                low = mid
            else:
                high = mid - 1
        chunk = self.chunks[low]
        relative = max(0, position - self._chunk_starts[low])
        return chunk.file, chunk.start_line - 1 + chunk.text[:relative].count("\n") + 1

    def float_body_text(self, record: FloatRecord) -> str:
        """Raw (comment-stripped) text between `\\begin{env}` and its matching `\\end{env}`."""
        return self._document[record.begin_offset : record.end_offset]

    def resolve_label(self, label: str) -> FloatRecord | None:
        return self._label_index.get(label)

    def label_map(self) -> dict[str, FloatRecord]:
        """label -> float, over float bodies only. A label outside a float is absent,
        which is why an unresolved `\\ref` stays unresolved instead of being guessed."""
        return dict(self._label_index)

    def float_by_anchor(self, anchor_id: str) -> FloatRecord | None:
        kind, _, number = anchor_id.partition(":")
        for record in self.floats:
            if record.kind == kind and str(record.number) == number:
                return record
        return None

    @property
    def tables(self) -> tuple[FloatRecord, ...]:
        return tuple(f for f in self.floats if f.kind == "table")

    @property
    def figures(self) -> tuple[FloatRecord, ...]:
        return tuple(f for f in self.floats if f.kind == "figure")

    @property
    def unresolved_refs(self) -> tuple[RefSite, ...]:
        return tuple(s for s in self.ref_sites if s.resolved_kind == "UNRESOLVED")

    @property
    def never_referenced_labels(self) -> tuple[str, ...]:
        referenced = {s.target for s in self.ref_sites}
        return tuple(sorted(set(self._label_index) - referenced))

    def in_body_site(self, source_file: str, line: int) -> bool:
        """Whether a (file, line) locator lies between `\\begin{document}` and the last
        `\\end{document}` in document order. FM-P11: a locator that lands in the preamble is
        a macro definition, and Paper Doctor does not audit macro definitions as claims."""
        return (source_file, line) in self.body_sites

    def claim_sites(self) -> tuple[RefSite, ...]:
        """`\\ref` sites inside the document body.

        Sites in the preamble are macro definitions (GMMVI's `math_commands.tex`
        carries 32 `\\ref{#1}`-style definitions), not paper claims. FM-P11.
        """
        return tuple(s for s in self.ref_sites if s.in_body and not re.fullmatch(r"#\d+", s.target))


def _resolve_input(reference: str, current: Path, root: Path) -> Path | None:
    candidate = reference.strip()
    for name in (candidate, candidate + ".tex"):
        for base in (current.parent, root):
            path = base / name
            if path.is_file():
                return path
    return None


def flatten(main_tex: Path, root: Path) -> tuple[list[Chunk], list[tuple[str, int, str]]]:
    """Recursive `\\input` flattening in document order.

    Returns the chunks plus unresolved-input diagnostics (`file`, `line`, reference).
    A file already inlined is not inlined again (cycle guard); that is a structural
    boundary, recorded rather than guessed at.
    """
    chunks: list[Chunk] = []
    unresolved: list[tuple[str, int, str]] = []
    seen: set[Path] = set()

    def relative(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()

    def walk(current: Path) -> None:
        if current in seen or len(chunks) > _MAX_CHUNKS:
            return
        seen.add(current)
        source = strip_comments(current.read_text(encoding="utf-8", errors="replace"))
        position = 0
        line = 1
        for match in _INPUT.finditer(source):
            if match.start() > position:
                before = source[position : match.start()]
                chunks.append(Chunk(relative(current), line, before))
                line += before.count("\n")
            target = _resolve_input(match.group(1), current, root)
            if target is None:
                unresolved.append((relative(current), line, match.group(1)))
                chunks.append(Chunk(relative(current), line, ""))
            else:
                walk(target)
            position = match.end()
        if position < len(source):
            chunks.append(Chunk(relative(current), line, source[position:]))

    walk(main_tex)
    return chunks, unresolved


def build_index(corpus_root: Path, main_tex: Path) -> LatexIndex:
    """Index one LaTeX root. Read-only, deterministic, no TeX execution."""
    root = Path(corpus_root).resolve()
    main = Path(main_tex).resolve()
    chunks, _unresolved_inputs = flatten(main, root)

    document = "".join(chunk.text for chunk in chunks)
    starts: list[int] = []
    offset = 0
    for chunk in chunks:
        starts.append(offset)
        offset += len(chunk.text)

    def locate(global_pos: int) -> tuple[Chunk, int]:
        low, high = 0, len(chunks) - 1
        while low < high:
            mid = (low + high + 1) // 2
            if starts[mid] <= global_pos:
                low = mid
            else:
                high = mid - 1
        return chunks[low], global_pos - starts[low]

    def absolute_line(chunk: Chunk, rel_pos: int) -> int:
        return chunk.start_line - 1 + chunk.text[:rel_pos].count("\n") + 1

    body = _BEGIN_DOC.search(document)
    last_end_doc = document.rfind("\\end{document}")
    body_start_offset = body.start() if body is not None else -1
    body_found = body_start_offset >= 0 and last_end_doc > body_start_offset

    def in_body(global_pos: int) -> bool:
        if not body_found:
            return False
        return body_start_offset <= global_pos <= last_end_doc

    line_sites: set[tuple[str, int]] = set()
    for chunk, chunk_start in zip(chunks, starts, strict=True):
        position = chunk_start
        for index_in_chunk, text_line in enumerate(chunk.text.split("\n")):
            if in_body(position):
                line_sites.add((chunk.file, chunk.start_line + index_in_chunk))
            position += len(text_line) + 1
    body_sites = frozenset(line_sites)

    depth = 0
    max_depth = 0
    for match in _ANY_FLOAT.finditer(document):
        if match.group(0).startswith("\\begin"):
            depth += 1
            max_depth = max(max_depth, depth)
        else:
            depth -= 1

    floats: list[FloatRecord] = []
    label_index: dict[str, FloatRecord] = {}
    unterminated: list[str] = []
    table_count = figure_count = 0
    for match in _BEGIN_FLOAT.finditer(document):
        env = match.group(1)
        closing = re.search(r"\\end\{" + re.escape(env) + r"\}", document[match.end() :])
        terminated = closing is not None
        end_offset = match.end() + (closing.start() if closing is not None else len(document) - match.end())
        inner = document[match.end() : end_offset]
        chunk, rel_pos = locate(match.start())
        kind = "table" if env.startswith("table") else "figure"
        if kind == "table":
            table_count += 1
        else:
            figure_count += 1
        number = table_count if kind == "table" else figure_count
        record = FloatRecord(
            kind=kind,
            number=number,
            env=env,
            source_file=chunk.file,
            begin_line=absolute_line(chunk, rel_pos),
            labels=tuple(_LABEL.findall(inner)),
            caption_present=_CAPTION.search(inner) is not None,
            in_body=in_body(match.start()),
            begin_offset=match.end(),
            end_offset=end_offset,
            terminated=terminated,
        )
        floats.append(record)
        if not terminated:
            unterminated.append(record.anchor_id)
        for label in record.labels:
            label_index[label] = record

    sites: list[RefSite] = []
    for match in _REF.finditer(document):
        chunk, rel_pos = locate(match.start())
        target = match.group(2)
        resolved = label_index.get(target)
        sites.append(
            RefSite(
                macro="\\" + match.group(1),
                target=target,
                source_file=chunk.file,
                line=absolute_line(chunk, rel_pos),
                resolved_kind=resolved.kind if resolved is not None else "UNRESOLVED",
                resolved_number=resolved.number if resolved is not None else 0,
                in_body=in_body(match.start()),
            )
        )

    return LatexIndex(
        root=root.as_posix(),
        main_file=relative_to_root(main, root),
        chunks=tuple(chunks),
        floats=tuple(floats),
        ref_sites=tuple(sites),
        max_float_nesting=max_depth,
        unterminated_floats=tuple(unterminated),
        body_found=body_found,
        body_sites=body_sites,
        _document=document,
        _chunk_starts=tuple(starts),
        _label_index=label_index,
    )


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


# --- Tabular text inside a float body ------------------------------------------------------
#
# A narrow, explicit subset. Row parsing is scoped to the interior of the float's own
# `tabular`-like environment, so prose that belongs to the caption (`\input`, `\\` line breaks
# inside a caption) can never be mistaken for a row. Inside that environment rows end at `\\`,
# cells at `&`, and the booktabs/`hline` rules are decoration removed anywhere they stand.
# The header is the first row whose leading *corner* cell is empty and whose remaining cells are
# not: that is a structural fact about the source, not an inference about its meaning.
# This is not a TeX engine (Phase 1 §6): a body with no such environment, or with no identifiable
# header row, returns `None`, and the calling rule reports INCONCLUSIVE rather than guessing at a
# topology it cannot recover.

_MACRO_WITH_ARG = re.compile(
    r"\\(?:textbf|mathbf|emph|textit|textmd|texttt|thead|footnotesize|small|multirow|makebox|parbox)"
    r"\s*(?:\[[^\]]*\])*\{([^{}]*)\}"
)
_MACRO_NAME = re.compile(r"\\[a-zA-Z]+\*?")
#: Typesetting macros whose first mandatory group is a parameter (a rotation angle, a scale, a
#: box width, a row count) and not printed content. GMMVI sets its column headers in
#: `\rotatebox{65}{\sc Samtrux}`; leaving the angle in place would put "65" into a column name.
#: `\multirow` is listed separately because it takes *two* parameter groups before its content
#: (`{rows}{fill}`), and a source that spaces them -- `\multirow{ 2}{*}{Maps Routing}` -- is the
#: common case. Leaving either in place would put "2" in front of a cell's value, and a reader that
#: takes the first number it sees would compare the wrong pair.
_PARAMETER_ARG_AT = re.compile(
    r"\\(?:rotatebox|scalebox|resizebox|raisebox|parbox)\s*(?:\[[^\]]*\])*"
    r"\{\s*-?\d+(?:\.\d+)?(?:pt|cm|mm|in|ex|em)?\s*\}"
    r"|\\multirow\s*(?:\[[^\]]*\])*\s*\{\s*\d+\s*\}\s*\{[^{}]*\}"
    r"|\\Block\s*(?:\[[^\]]*\])*\s*\{\d+-\d+\}"
)
#: Color and opacity declarations. Their arguments name a color, never content: `\cellcolor` sets a
#: cell's background and prints no characters of its own, so `{\transparent{1.0}\cellcolor[HTML]
#: {C2DAEA}} {\color{black} XGBoost}` prints `XGBoost` and nothing else. Dropping the whole command
#: is what lets a declared column address match the header the author wrote. A command that paints
#: *and* sets content (`\textcolor`, `\colorbox`) is deliberately absent: its content is printed.
_PRINTS_NOTHING_AT = re.compile(
    r"\\(?:color|pagecolor|cellcolor|rowcolor|columncolor|transparent|arrayrulecolor)"
    r"\s*(?:\[[^\]]*\])?\s*\{[^{}]*\}"
)
_ESCAPED = {"\\#": "#", "\\$": "$", "\\%": "%", "\\&": "&", "\\_": "_"}
#: TeX spacing commands. They set glue, not characters, so they become a space; leaving them in
#: would inject a comma into the cell text that the paper never printed.
_SPACING = {"\\,": " ", "\\;": " ", "\\:": " ", "\\!": " "}
#: LaTeX digit grouping: `$26\,048$` prints one number and separates its thousands with a thin
#: space. TeX uses these three macros for no other purpose between digits, so the group is read as
#: the number it prints instead of as two numbers. A plain comma is *not* collapsed: in
#: `$\mathrm{UniformInt}[64,512]$` it is an interval separator and in `$0,1,2$` a list separator,
#: and no reading of the digits alone says which. Ambiguous text stays ambiguous.
_DIGIT_GROUP = re.compile(r"(?<=\d)\\[,;:](?=\d{3}(?!\d))")


def collapse_digit_groups(text: str) -> str:
    r"""Write a grouped number as the single number it prints, everywhere it occurs.

    Both sides of a numeric comparison go through this: a claim that says `$26\,048$` and a cell
    that prints `$26\,048$` state the same quantity, and an extractor that grouped one side but
    not the other would manufacture a disagreement the paper does not contain.
    """
    return _DIGIT_GROUP.sub("", text)


_CELL_SEP = re.compile(r"(?<!\\)&")
_DIRECTION_MARKS = (("down", ("\\textdownarrow", "↓", "\\downarrow")), ("up", ("\\textuparrow", "↑", "\\uparrow")))

#: Row-decoration commands. They are *not* segments of their own -- `\midrule` prefixes the row
#: that follows it -- so they are removed in place rather than used to discard a whole segment.
_RULE_COMMAND = re.compile(
    r"\\(?:toprule|midrule|bottomrule|hline|cline|cmidrule|addlinespace|arrayrulecolor|noalign)"
    r"\s*(?:\[[^\]]*\])?\s*(?:\{(?:[^{}]|\{[^{}]*\})*\})?"
)
#: The table environments whose interiors this subset reads. A `\\` outside one of these is prose.
#: `NiceTabular` is included because GMMVI's wide tables are set in it; it is read with the same
#: `&`/`\\` grammar as `tabular`, plus the `\Block{rows-columns}{...}` merge this module uses as
#: explicit block structure (Phase 2 §3). Nothing else about it is interpreted.
_TABULAR_BEGIN = re.compile(r"\\begin\{(tabular\*?|tabularx|longtable|array|NiceTabular\*?|NiceMatrix)\}")
_TABULAR_SPEC = re.compile(
    r"\s*(?:\[[^\]]*\])?\s*\{(?:[^{}]|\{[^{}]*\})*\}(?:\s*\{[^{}]*\})?",
)
#: `\\[2pt]` -- the optional spacing argument belongs to the terminator, not to the next cell.
_ROW_OPTION = re.compile(r"\s*\[[^\]]*\]")


def plain_text(text: str) -> str:
    """Cell text with its typesetting markup removed, digits and letters untouched."""
    current = collapse_digit_groups(text)
    current = _PRINTS_NOTHING_AT.sub(" ", current)
    current = _PARAMETER_ARG_AT.sub(" ", current)
    for _ in range(6):
        replaced = _MACRO_WITH_ARG.sub(r"\1", current)
        if replaced == current:
            break
        current = replaced
    for escape, character in _ESCAPED.items():
        current = current.replace(escape, character)
    for spacing in _SPACING:
        current = current.replace(spacing, " ")
    current = _MACRO_NAME.sub(" ", current)
    current = current.replace("$", " ").replace("~", " ")
    return " ".join(current.replace("{", " ").replace("}", " ").replace("\\", " ").split())


def body_contains_literal(body: str, literal: str) -> bool:
    """Digit-boundary containment, so `0.42` never matches inside `20.421`."""
    return re.search(rf"(?<![\d.]){re.escape(literal)}(?![\d.])", plain_text(body)) is not None


def _direction(cell: str) -> str:
    for name, marks in _DIRECTION_MARKS:
        if any(mark in cell for mark in marks):
            return name
    return ""


@dataclass(frozen=True)
class TableRow:
    label: str
    cells: tuple[str, ...]
    #: Which explicit structural block this row sits in, e.g. "b2". "" only for a row of a grid
    #: that was not produced by `parse_table`. Addressing, not ontology: a block is a segment of
    #: one table, identified by the structure that delimits it (Phase 2 §2).
    block_key: str = "b1"

    def cell(self, index: int) -> str:
        return self.cells[index] if 0 <= index < len(self.cells) else ""


@dataclass(frozen=True)
class TableGrid:
    """A parsed tabular: declared column names and directions, plus labelled rows by block."""

    columns: tuple[str, ...] = ()
    directions: tuple[str, ...] = ()
    rows: tuple[TableRow, ...] = ()
    n_rows_dropped: int = 0
    #: How many leading columns of a row are labels rather than values. 1 for the ordinary
    #: "row name, then values" table; larger when a table carries a merge-spanned group column.
    n_label_columns: int = 1
    #: (block_key, structural evidence) in source order. The evidence quotes the structure --
    #: a group header, a rule, a merged cell -- with its source locator, never a reading of it.
    block_evidence: tuple[tuple[str, str], ...] = ()

    @property
    def n_blocks(self) -> int:
        return len(self.block_evidence)

    def column_index(self, name: str) -> int | None:
        wanted = plain_text(name).lower()
        for index, column in enumerate(self.columns):
            if column.lower() == wanted:
                return index
        return None

    def row(self, label: str, block: str | None = None) -> TableRow | None:
        """The row named `label`. A label that occurs in more than one block is not addressable
        without naming the block: returning the first match would be a silent choice of evidence.
        A label that occurs twice *inside* one block is not addressable either -- the source has
        stated no further structure that separates the two."""
        wanted = plain_text(label).lower()
        hits = [row for row in self.rows if plain_text(row.label).lower() == wanted]
        if block is not None:
            hits = [row for row in hits if row.block_key == block]
        return hits[0] if len(hits) == 1 else None

    def blocks_for(self, label: str) -> tuple[str, ...]:
        """Every block that prints `label`, in source order."""
        wanted = plain_text(label).lower()
        seen: list[str] = []
        for row in self.rows:
            if plain_text(row.label).lower() == wanted and row.block_key not in seen:
                seen.append(row.block_key)
        return tuple(seen)

    def block_basis(self, block: str) -> str:
        return dict(self.block_evidence).get(block, "")

    def row_containing(self, label: str, block: str | None = None) -> TableRow | None:
        """Substring row match, used only when an exact label is absent. Ambiguous -> None."""
        wanted = plain_text(label).lower()
        if not wanted:
            return None
        hits = [row for row in self.rows if wanted in plain_text(row.label).lower()]
        if block is not None:
            hits = [row for row in hits if row.block_key == block]
        elif len({row.block_key for row in hits}) > 1:
            return None
        return hits[0] if len(hits) == 1 else None


def _matching_end(text: str, begin_re: re.Pattern[str], end_re: re.Pattern[str], cursor: int) -> tuple[int, int] | None:
    """Where the environment opened before `cursor` closes: `(interior stop, past the \\end)`.

    The two offsets are both reported because a caller that wants the rows cuts at the first,
    while a caller that removes the nested environment wholesale needs the second.
    """
    depth = 1
    interior = cursor
    after = cursor
    while depth:
        next_end = end_re.search(text, cursor)
        if next_end is None:
            return None
        next_begin = begin_re.search(text, cursor)
        if next_begin is not None and next_begin.start() < next_end.start():
            depth += 1
            cursor = next_begin.end()
            continue
        depth -= 1
        interior, after = next_end.start(), next_end.end()
        cursor = after
    return interior, after


def _blank_nested(text: str, env: str) -> str:
    """Replace each nested same-kind environment (markup and all) with spaces of the same length.

    A cell that holds its own `tabular` is not this table's row structure. Blanking it keeps the
    outer arity honest and leaves the cell empty, so a rule reads "no recoverable value" instead
    of reading the nested table's rows as its own. The length is preserved because the block
    discriminator reports the source line of a structure, and re-writing text shorter would move
    every later offset.
    """
    begin_re = re.compile(r"\\begin\{" + re.escape(env) + r"\}")
    end_re = re.compile(r"\\end\{" + re.escape(env) + r"\}")
    current = text
    while True:
        found = begin_re.search(current)
        if found is None:
            return current
        spec = _TABULAR_SPEC.match(current, found.end())
        start = spec.end() if spec is not None else found.end()
        closed = _matching_end(current, begin_re, end_re, start)
        if closed is None:
            tail = " " * (len(current) - found.start())
            return current[: found.start()] + tail
        blanked = " " * (closed[1] - found.start())
        current = current[: found.start()] + blanked + current[closed[1] :]


def _interior_span(body: str) -> tuple[int, str] | None:
    """`(offset of the interior, the interior text)` for the float's first table environment.

    The offset matters: a block's evidence names the source line of the structure that opened it,
    and an offset inside the interior only becomes a locator once the interior's own position in
    the float body is added back.
    """
    found = _TABULAR_BEGIN.search(body)
    if found is None:
        return None
    env = found.group(1)
    begin_re = re.compile(r"\\begin\{" + re.escape(env) + r"\}")
    end_re = re.compile(r"\\end\{" + re.escape(env) + r"\}")
    spec = _TABULAR_SPEC.match(body, found.end())
    start = spec.end() if spec is not None else found.end()
    closed = _matching_end(body, begin_re, end_re, start)
    if closed is None:
        return None
    return start, _blank_nested(body[start : closed[0]], env)


def tabular_interior(body: str) -> str | None:
    """The text between a float body's first table environment and its matching `\\end`.

    Nesting is counted for the same environment name, so an inner table cannot close the outer
    one early. No environment, or an environment that is never closed, is unrecoverable: `None`.
    """
    span = _interior_span(body)
    return span[1] if span is not None else None


def _split_rows(text: str) -> list[tuple[int, str]]:
    """Split a tabular interior at row terminators that sit outside every brace group.

    A `\\\\` inside a cell (the line break in `\\thead{$x$ \\\\ $\\pm y$}`) is cell content, not a row
    boundary. Each segment carries its offset into the interior so a block's evidence can name the
    source line of the structure that opened it.
    """
    rows: list[tuple[int, str]] = []
    depth = 0
    start = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            if text[index : index + 2] == "\\\\":
                if depth == 0:
                    rows.append((start, text[start:index]))
                    index += 2
                    option = _ROW_OPTION.match(text, index)
                    index = option.end() if option is not None else index
                    start = index
                    continue
                index += 2
                continue
            index += 2
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth = max(0, depth - 1)
        index += 1
    rows.append((start, text[start:]))
    return rows


@dataclass(frozen=True)
class _Segment:
    """One row of source, cut into cells, with the depth-0 structure that stands around it."""

    cells: tuple[tuple[int, str], ...] = ()
    rules: tuple[tuple[str, int], ...] = ()
    spans: tuple[tuple[int, int, int, str, int], ...] = ()
    content_offset: int = 0


def _take_brace_group(text: str, cursor: int) -> tuple[int, str, int]:
    """The next brace group at or after `cursor`, as `(offset of its content, content, end)`."""
    index = cursor
    while index < len(text) and text[index] in " \t\n":
        index += 1
    if index >= len(text) or text[index] != "{":
        return cursor, "", cursor
    depth = 0
    start = index + 1
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return start, text[start:index], index + 1
        index += 1
    return cursor, "", cursor


#: A command that spans cells: `\multicolumn{cols}`, `\Block{rows-cols}`, `\multirow{rows}`.
_SPAN_AT = re.compile(r"\\(multicolumn|Block|multirow)\s*(?:\[[^\]]*\])*\{([^{}]*)\}")
#: A rule that separates rows. `addlinespace` sets glue, it does not separate, so it is absent.
_ROW_RULE_AT = re.compile(r"\\(toprule|midrule|bottomrule|hline|cline|cmidrule)\b")


def _span_geometry(name: str, group: str) -> tuple[int, int] | None:
    """`(rows_spanned, columns_spanned)` of a spanning command, read off its own argument."""
    parts = group.strip()
    if name == "Block":
        rows, _, columns = parts.partition("-")
        if not columns.isdigit() or not rows.isdigit():
            return None
        return int(rows), int(columns)
    if not parts.isdigit():
        return None
    if name == "multicolumn":
        return 1, int(parts)
    return int(parts), 1


#: Which brace group of each spanning command holds the printed content. `\multicolumn{cols}{align}`
#: and `\multirow{rows}{width}` take their text third, NiceTabular's `\Block{rows-cols}` second.
#: Reading the wrong group is what once made `{c}` look like a group header's name.
_SPAN_CONTENT_GROUP = {"multicolumn": 3, "multirow": 3, "Block": 2}


def _span_argument(text: str, span: re.Match[str], name: str) -> tuple[str, int, int]:
    """`(printed content, offset of that content, cursor past the command)`."""
    cursor = span.end()
    content, content_offset = "", cursor
    for _ in range(2, _SPAN_CONTENT_GROUP[name] + 1):
        found_at, found, past = _take_brace_group(text, cursor)
        if past == cursor:
            break
        content, content_offset, cursor = found, found_at, past
    return content, content_offset, cursor


def _scan_segment(base_offset: int, text: str) -> _Segment:
    """Cell boundaries, rules and spanning commands that sit outside every brace group."""
    cells: list[tuple[int, str]] = []
    rules: list[tuple[str, int]] = []
    spans: list[tuple[int, int, int, str, int]] = []
    depth = 0
    start = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            rule = _ROW_RULE_AT.match(text, index)
            if rule is not None and depth == 0:
                rules.append((rule.group(1), base_offset + index))
                index = rule.end()
                continue
            span = _SPAN_AT.match(text, index)
            if span is not None and depth == 0:
                geometry = _span_geometry(span.group(1), span.group(2))
                if geometry is not None:
                    argument, argument_offset, cursor = _span_argument(text, span, span.group(1))
                    spans.append((len(cells), geometry[0], geometry[1], argument, base_offset + argument_offset))
                    index = max(cursor, span.end())
                    continue
            index += 2
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth = max(0, depth - 1)
        elif character == "&" and depth == 0:
            cells.append((base_offset + start, text[start:index]))
            start = index + 1
        index += 1
    cells.append((base_offset + start, text[start:]))
    blanked = _RULE_COMMAND.sub(lambda found: " " * (found.end() - found.start()), text)
    content = len(blanked) - len(blanked.lstrip())
    return _Segment(cells=tuple(cells), rules=tuple(rules), spans=tuple(spans), content_offset=base_offset + content)


def _group_header(segment: _Segment, arity: int | None) -> tuple[str, int] | None:
    r"""A row that is one spanning command across the full width: `(merged text, its offset)`.

    This is the `\multicolumn{12}{c}{Tuned hyperparameters}` shape. The text is quoted as the
    author printed it; nothing here decides what the group means.
    """
    filled = [cell for _, cell in segment.cells if plain_text(cell)]
    if len(filled) != 1:
        return None
    for cell_index, rows, columns, argument, offset in segment.spans:
        if cell_index == 0 and rows == 1 and columns >= 2 and (arity is None or columns >= arity):
            return plain_text(argument), offset
    return None


def _leading_merge(segment: _Segment) -> tuple[int, int, str, int] | None:
    """A vertical merge in a row's first cell: `(rows, columns_it_covers, its text, its offset)`."""
    for cell_index, rows, columns, argument, offset in segment.spans:
        if cell_index == 0 and rows > 1:
            return rows, columns, plain_text(argument), offset
    return None


_SPEC_TOKENS = "lcrXpmb"


def _spec_arity(body: str) -> int | None:
    """How many columns the tabular column spec declares. None when the spec uses a shape
    this subset does not read, which keeps the arity a stated fact rather than a guess."""
    begin = _TABULAR_BEGIN.search(body)
    if begin is None:
        return None
    cursor = begin.end()
    option = re.match(r"\s*\[[^\]]*\]", body[cursor : cursor + 16])
    if option is not None:
        cursor += option.end()
    spec = _take_brace_group(body, cursor)[1]
    if not spec:
        return None
    count, index = 0, 0
    while index < len(spec):
        character = spec[index]
        if character in "| @{}}":
            index += 1
            continue
        if character in "!><":
            past = _take_brace_group(spec, index + 1)[2]
            if past <= index:
                return None
            index = past
            continue
        if character == "*":
            repeat = _take_brace_group(spec, index + 1)
            if not repeat[1].isdigit() or repeat[2] <= index:
                return None
            past = _take_brace_group(spec, repeat[2])[2]
            if past <= repeat[2]:
                return None
            index = past
            continue
        if character in _SPEC_TOKENS:
            count += 1
            if character in "pmb":
                past = _take_brace_group(spec, index + 1)[2]
                if past <= index:
                    return None
                index = past
                continue
            index += 1
            continue
        return None
    return count if count else None


def _locator(locate: Callable[[int], tuple[str, int]] | None, offset: int) -> str:
    if locate is None:
        return f"float body offset {offset}"
    path, line = locate(offset)
    return f"{path}:{line}" if path else f"float body offset {offset}"


def _add_clause(clauses: list[str], clause: str) -> None:
    r"""`\hline \hline` is one boundary stated twice in the source; it is reported once."""
    if clause not in clauses:
        clauses.append(clause)


def parse_table(body: str, *, locate: Callable[[int], tuple[str, int]] | None = None) -> TableGrid | None:
    """Parse the tabular in a float body into block-addressed rows. `None` when unrecoverable.

    A block is opened only by structure the source states: a full-width group header, a rule
    between two groups of data rows, or a vertically merged leading cell. Which block a row sits
    in is therefore answerable without reading what any of it means.
    """
    interior = _interior_span(body)
    if interior is None:
        return None
    interior_offset, interior_text = interior
    arity = _spec_arity(body)
    segments: list[_Segment] = []
    for offset, text in _split_rows(interior_text):
        scanned = _scan_segment(interior_offset + offset, text)
        if any(plain_text(cell) for _, cell in scanned.cells):
            segments.append(scanned)
    if not segments:
        return None

    head = segments[0]
    head_raw = tuple(cell for _, cell in head.cells)
    if len(head_raw) < 2 or not any(plain_text(cell) for cell in head_raw[1:]):
        return None
    n_label_columns = 1
    #: True only for the reading licensed below: the header corner names the row-label column.
    #: It waives the column-spec arity check, which is why it is tracked rather than inlined.
    corner_names_labels = False
    if plain_text(head_raw[0]):
        # The corner is not empty, so the header only names columns rather than hiding behind an
        # empty cell. That reading is licensed when a data row carries a vertical merge in its
        # first column -- an explicitly stated group column -- and not otherwise.
        merges = [merged for segment in segments[1:] if (merged := _leading_merge(segment)) is not None]
        if merges:
            n_label_columns = merges[0][1] + 1
            if arity is not None and len(head_raw) != arity:
                return None
        else:
            # The ordinary academic layout: `Name & Col A & Col B` with no merges and no group
            # spans. Nothing states which reading applies, *except* the table itself: a header
            # row with a group span has fewer cells than the rows under it, so a table that
            # prints the same cell count in every row states that its header row is the column
            # names and its first column is labelled by its own corner. Then the column spec is
            # decorative -- LaTeX renders a declared column it never uses as blank -- and the
            # self-consistent count replaces it as the guard. A table that is not self-consistent
            # is still refused, so only the ambiguity is removed, never a guess added.
            if any(len(segment.cells) != len(head_raw) for segment in segments[1:]):
                return None
            if len(head_raw) < 2:
                return None
            corner_names_labels = True
        if len(head_raw) <= n_label_columns:
            return None
    columns = tuple(plain_text(cell) for cell in head_raw[n_label_columns:])
    if not any(columns) or (arity is not None and not corner_names_labels and len(columns) + n_label_columns != arity):
        return None
    directions = tuple(_direction(cell) for cell in head_raw[n_label_columns:])

    rows: list[TableRow] = []
    evidence: list[tuple[str, str]] = []
    ordinal = 1
    clauses: list[str] = []
    rows_in_block = 0
    dropped = 0
    #: A leading vertical merge states that the row label below it covers several source rows.
    #: The continuation rows print no label of their own, so they carry the merged one -- which is
    #: precisely what makes a label that occurs twice in a block unaddressable by `row()`. Dropping
    #: them instead would leave the merge's first row as the only candidate, and a claim about the
    #: quantity the *other* row prints would be scored against the wrong cell.
    carry_label = ""
    carry_rows = 0

    def close_block() -> None:
        evidence.append((f"b{ordinal}", "; ".join(clauses)))

    for segment in segments[1:]:
        opened_by: list[str] = []
        leading = [rule for rule in segment.rules if rule[1] < segment.content_offset]
        for name, offset in leading:
            if name != "toprule":
                _add_clause(opened_by, f"{name} at {_locator(locate, offset)}")
        group = _group_header(segment, arity)
        if group is not None:
            _add_clause(opened_by, f'multicolumn group header "{group[0]}" at {_locator(locate, group[1])}')
        merge = _leading_merge(segment)
        if merge is not None:
            _add_clause(
                opened_by,
                f'merged cell spanning {merge[0]} rows = "{merge[2]}" at {_locator(locate, merge[3])}'
                f" ({merge[1]} label column{'s' if merge[1] != 1 else ''})",
            )
        if opened_by and rows_in_block:
            close_block()
            ordinal += 1
            clauses = opened_by
            rows_in_block = 0
            carry_label, carry_rows = "", 0
        elif opened_by:
            clauses = clauses + opened_by
        if group is not None and len(segment.cells) == 1:
            continue  # the row is the group header itself, not a measurement

        label_cells = [cell for _, cell in segment.cells]
        if len(label_cells) < n_label_columns:
            dropped += 1
            continue
        label = plain_text(_RULE_COMMAND.sub(" ", label_cells[n_label_columns - 1]))
        if not label and carry_rows > 0:
            label, carry_rows = carry_label, carry_rows - 1
        elif merge is not None and label:
            carry_label, carry_rows = label, merge[0] - 1
        if not label:
            continue
        values = tuple(plain_text(_RULE_COMMAND.sub(" ", cell)) for cell in label_cells[n_label_columns:])
        if len(values) != len(columns):
            dropped += 1
            continue
        rows.append(TableRow(label=label, cells=values, block_key=f"b{ordinal}"))
        rows_in_block += 1

    close_block()
    if not rows:
        return None
    return TableGrid(
        columns=columns,
        directions=directions,
        rows=tuple(rows),
        n_rows_dropped=dropped,
        n_label_columns=n_label_columns,
        block_evidence=tuple(evidence),
    )
