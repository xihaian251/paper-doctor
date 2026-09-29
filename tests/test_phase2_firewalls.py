r"""Phase 2 §17: the four block firewalls, plus a pointer to the three the CLI already owns.

Block discrimination is an addressing capability, so the failure modes worth forbidding are the ones
where an address appears out of nowhere: a verdict that silently picks one of two printed blocks, a
block that moves because its numbers moved, a block that inherits the caption's subject, or a
manifest that overrules what the source structure states.

Nothing here reads a word of meaning. The two corpora are synthetic and unseen by either pilot paper,
and each is the twin of another: the only thing that differs between the pair is the very signal the
firewall forbids, so a discriminator that keyed on it would change its answer and be caught.

The remaining three Phase 2 firewalls -- a `FAIL` exiting 0, a bad contract exiting 2, and both output
faces staying byte-identical across hash seeds -- are asserted in `test_cli.py`, because they are
properties of the command line rather than of the discriminator.
"""

from __future__ import annotations

import re
from pathlib import Path

from support import audit_manifest_of, claim, document, float_anchor, link, write_case

from paper_doctor.cli import EXIT_OK, main
from paper_doctor.latex_index import parse_table
from paper_doctor.status import RuleStatus

_SENTENCE = r"Ours outperforms Base on every reported metric."
_OFFSET = re.compile(r"offset \d+|:\d+\b")


def _shape(evidence: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    r"""Block bases with their source anchors blanked: the structure, minus where it sits."""
    return tuple((key, _OFFSET.sub("offset N", basis)) for key, basis in evidence)


def _body(group_a: str, group_b: str, ours: tuple[str, str], base: tuple[str, str]) -> str:
    r"""One tabular, two full-width group headers, four reported cells.

    `group_a`/`group_b` are the printed headers; the two pairs are the numbers under `Score`.
    """
    return (
        "\\begin{table}[t]\n"
        "\\begin{tabular}{lcc}\n"
        "\\toprule\n"
        " & Acc\\textuparrow & RMSE\\textdownarrow \\\\\n"
        "\\midrule\n"
        f"\\multicolumn{{3}}{{c}}{{{group_a}}}\\\\\n"
        "\\midrule\n"
        f"Ours & ${ours[0]}$ & ${ours[1]}$ \\\\\n"
        f"Base & ${base[0]}$ & ${base[1]}$ \\\\\n"
        "\\midrule\n"
        f"\\multicolumn{{3}}{{c}}{{{group_b}}}\\\\\n"
        "\\midrule\n"
        f"Ours & ${ours[0]}$ & ${ours[1]}$ \\\\\n"
        f"Base & ${base[0]}$ & ${base[1]}$ \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\caption{Two configurations.}\\label{tab:firewall}\n"
        "\\end{table}"
    )


def _audit(root: Path, body: str, block: str) -> RuleStatus:
    """PD004 on one claim over `body`, with `block` declared (empty means undeclared)."""
    paper = document(body, _SENTENCE)
    qualifiers: list[dict[str, str]] = [{"kind": "comparison_basis", "statement": "per_column"}]
    if block:
        qualifiers.append({"kind": "comparison_block", "statement": f"block={block}"})
    entry = claim(
        paper,
        "F",
        _SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Ours", "Base"],
        links=["L-F"],
        qualifiers=qualifiers,
    )
    findings = audit_manifest_of(
        write_case(
            root,
            paper=paper,
            findings=[],
            claims=[entry],
            floats=[float_anchor("tab:firewall", float_id="tab-firewall", quantity_declaration="Acc, RMSE")],
            links=[link("L-F", "F", "FLOAT", "tab-firewall")],
        )
    )
    return next(f for f in findings if f.rule_id == "PD004").status


# --- firewall 1: a repeated label is unaddressable until a block is declared -------------------


def test_a_repeated_label_carries_no_verdict_until_the_source_structures_it(tmp_path: Path) -> None:
    r"""`Ours` and `Base` are each printed twice, once per block, so the pair is not a pair.

    The same body, the same claim, the same numbers: the only difference is whether a block was
    declared. Without one the audit says INCONCLUSIVE -- it may not resolve the pair by choosing a
    block, because either choice is a verdict the source does not license.
    """
    body = _body("Untuned configuration", "Tuned configuration", ("0.42", "0.10"), ("0.40", "0.12"))
    grid = parse_table(body)
    assert grid is not None
    assert grid.row("Ours") is None
    assert grid.blocks_for("Ours") == ("b1", "b2")

    undeclared = _audit(tmp_path / "undeclared", body, "")
    assert undeclared is RuleStatus.INCONCLUSIVE
    assert _audit(tmp_path / "declared", body, "b1") is not RuleStatus.INCONCLUSIVE


# --- firewall 2: block identity never comes from a numeric value --------------------------------


def test_replacing_every_number_leaves_the_block_structure_untouched(tmp_path: Path) -> None:
    r"""Two tables with identical geometry and no digit in common share one block structure.

    A discriminator that keyed on values -- the numeric-nearness matching Phase 2 §1 forbids --
    would open or move a block here. The rows, the block keys and every recorded basis must be the
    same objects' positions in the source, which no number can change.
    """
    left = parse_table(_body("Default settings", "Tuned settings", ("0.42", "0.10"), ("0.40", "0.12")))
    right = parse_table(_body("Default settings", "Tuned settings", ("9.81", "0.003"), ("1.25", "44.0")))
    assert left is not None and right is not None
    assert [row.block_key for row in left.rows] == [row.block_key for row in right.rows]
    assert [row.label for row in left.rows] == [row.label for row in right.rows]
    # The anchors are real source offsets, so a longer number moves them by its own length; the
    # block *structure* -- which rule, which printed header, which key -- must not move with it.
    assert _shape(left.block_evidence) == _shape(right.block_evidence)
    assert left.columns == right.columns
    assert [row.cells for row in left.rows] != [row.cells for row in right.rows]


# --- firewall 3: block identity never comes from the caption ------------------------------------


def test_the_caption_is_the_only_difference_and_the_basis_names_only_geometry(tmp_path: Path) -> None:
    r"""Two tables whose captions disagree about what they measure share one block structure.

    Every clause of a block basis is a rule, a span or a printed group header at a source line, so
    no word of the caption can enter it. Both halves are asserted: the addressing is the same for two
    differently-titled tables, and each basis is made only of geometry.
    """
    ablative = _body("Section A", "Section B", ("0.42", "0.10"), ("0.40", "0.12"))
    titled = ablative.replace(
        "\\caption{Two configurations.}", "\\caption{Ablation over every hyperparameter, sorted by cost.}"
    )
    left, right = parse_table(ablative), parse_table(titled)
    assert left is not None and right is not None
    assert [row.block_key for row in left.rows] == [row.block_key for row in right.rows]
    assert left.block_evidence == right.block_evidence
    for key in ("b1", "b2"):
        basis = right.block_basis(key)
        assert "multicolumn group header" in basis and "midrule at" in basis
        for forbidden in ("caption", "Ablation", "hyperparameter", "sorted by cost"):
            assert forbidden not in basis


# --- firewall 4: a manifest cannot overrule the deterministic structure -------------------------


def test_declaring_a_block_never_moves_a_row_that_the_source_put_elsewhere(tmp_path: Path) -> None:
    r"""Declaration establishes provenance, not correctness (Phase 2 §6).

    `block=b2` is a real block that prints `Ours`; `block=b9` prints nothing. Both are honoured
    literally: the audit addresses only what the declaration names, and a name the source does not
    carry yields no row rather than falling back to the one that exists.
    """
    body = _body("Untuned configuration", "Tuned configuration", ("0.42", "0.10"), ("0.40", "0.12"))
    grid = parse_table(body)
    assert grid is not None
    assert grid.n_blocks == 2
    assert _audit(tmp_path / "b2", body, "b2") is RuleStatus.PASS
    ghost = _audit(tmp_path / "b9", body, "b9")
    assert ghost is RuleStatus.INCONCLUSIVE
    assert grid.n_blocks == 2, "a declared block name cannot add structure to the table"


def test_a_stale_block_declaration_is_used_as_given(tmp_path: Path) -> None:
    r"""The same sentence, audited against the block the author pointed at, even when it disagrees.

    Under the first block the pair supports the claim; under the second it contradicts it. Auditing
    with the other declaration flips the verdict accordingly, which is only possible because the tool
    obeys the declaration instead of selecting whichever block agrees with the sentence.
    """
    body = (
        "\\begin{table}[t]\n"
        "\\begin{tabular}{lcc}\n"
        "\\toprule\n"
        " & Acc\\textuparrow & RMSE\\textdownarrow \\\\\n"
        "\\midrule\n"
        "\\multicolumn{3}{c}{Untuned configuration}\\\\\n"
        "\\midrule\n"
        "Ours & $0.42$ & $0.10$ \\\\\n"
        "Base & $0.40$ & $0.12$ \\\\\n"
        "\\midrule\n"
        "\\multicolumn{3}{c}{Tuned configuration}\\\\\n"
        "\\midrule\n"
        "Ours & $0.31$ & $0.44$ \\\\\n"
        "Base & $0.52$ & $0.09$ \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\caption{Two configurations.}\\label{tab:firewall}\n"
        "\\end{table}"
    )
    assert _audit(tmp_path / "one", body, "b1") is RuleStatus.PASS
    assert _audit(tmp_path / "two", body, "b2") is RuleStatus.FAIL


def test_a_block_failure_still_exits_zero(tmp_path: Path) -> None:
    r"""§10 again, on the new surface: a FAIL produced by block addressing is a finished audit."""
    body = _body("Untuned configuration", "Tuned configuration", ("0.42", "0.10"), ("0.40", "0.41"))
    paper = document(body, _SENTENCE)
    entry = claim(
        paper,
        "F",
        _SENTENCE,
        form="COMPARATIVE",
        fragment_is_text=True,
        predicate="outperforms",
        subjects=["Ours", "Base"],
        links=["L-F"],
        qualifiers=[
            {"kind": "comparison_basis", "statement": "per_column"},
            {"kind": "comparison_block", "statement": "block=b1"},
        ],
    )
    manifest = write_case(
        tmp_path / "exit",
        paper=paper,
        findings=[],
        claims=[entry],
        floats=[float_anchor("tab:firewall", float_id="tab-firewall", quantity_declaration="Acc, RMSE")],
        links=[link("L-F", "F", "FLOAT", "tab-firewall")],
    )
    assert main(["audit", str(manifest)]) == EXIT_OK
