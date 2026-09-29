"""Phase 3 §14 + §17: the README is a specification of behaviour, so it is tested as one.

The fresh-user measurement found the worked example contradicting its own sample manifest -- a
`form=COMPARATIVE` listing under a `NUMERIC_ATTRIBUTION` manifest, and a "from the manifest above"
that pointed below. Hand-written terminal output rots the moment a reason string changes, and a
reader cannot tell. So `examples/quickstart/` is a real runnable workspace and this file pins the
three claims the README makes about its own content:

- the manifest block is that file, byte for byte;
- the listing block is what `paper-doctor audit examples/quickstart` prints, byte for byte;
- every rule row quotes the frozen question the rule actually asks.

A fourth test holds the §17 boundary sentences in place, because "what a FAIL does not mean" is the
part of the documentation a reader is most likely to skim away.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from paper_doctor import __version__
from paper_doctor.cli import EXIT_OK, main
from paper_doctor.objects import ClaimForm, LinkBasis, Quantifier, TargetKind
from paper_doctor.rules import NAME, QUESTION, RULE_IDS
from paper_doctor.status import RuleStatus, UniverseStatus

REPO = Path(__file__).resolve().parents[1]
README = (REPO / "README.md").read_text(encoding="utf-8")
EXAMPLE_DIR = REPO / "examples" / "quickstart"
EXAMPLE_MANIFEST = (EXAMPLE_DIR / "paper-doctor.yml").read_text(encoding="utf-8")


def _blocks(language: str) -> list[str]:
    """Every fenced block body of `language`, in document order."""
    pattern = re.compile(rf"```{language}\n(.*?)```", re.DOTALL)
    return [match.group(1) for match in pattern.finditer(README)]


def _listing() -> str:
    """The README's terminal transcript of the quickstart run."""
    blocks = [block for block in _blocks("text") if block.startswith("# paper-doctor audit ")]
    assert len(blocks) == 1, f"the README must carry exactly one audit transcript, found {len(blocks)}"
    return blocks[0]


def test_the_readme_manifest_block_is_the_example_file_verbatim() -> None:
    yaml_blocks = [block for block in _blocks("yaml") if block.startswith("schema_version: 1")]
    assert len(yaml_blocks) == 1, "the README must show one complete manifest"
    assert yaml_blocks[0] == EXAMPLE_MANIFEST, "the documented manifest drifted from the runnable one"


def test_the_readme_listing_is_what_the_example_prints(tmp_path: Path, capsys) -> None:
    """Run the documented command for real and diff the transcript against the README."""
    # The path in the header is the argument as given, so the audit is run from the repo root and the
    # report lands in `tmp_path`; the example workspace itself is never written to.
    assert main(["audit", "examples/quickstart"]) == EXIT_OK
    printed = capsys.readouterr().out
    assert printed == _listing(), "the documented terminal output drifted from the tool's"
    assert printed.endswith("NOT_RUN: 2\n")
    assert "PAPER_DOCTOR" not in printed


def test_the_example_is_self_consistent_and_carries_the_three_lesson_statuses() -> None:
    """C1 agrees with its cell, C2 does not, C3 declares no link -- PASS, FAIL, INCONCLUSIVE in one run."""
    listing = _listing()
    rows = re.findall(r"^(PD\d{3})\s+(\S+)\s+(\S+)$", listing, re.MULTILINE)
    assert ("PD003", "PASS", "C1") in rows
    assert ("PD003", "FAIL", "C2") in rows
    assert ("PD001", "INCONCLUSIVE", "C3") in rows
    assert ("PD004", "NOT_RUN", "rule:PD004") in rows
    # The FAIL must be quoted with the address it used, or the reader cannot check which side is wrong.
    fail_reason = re.search(r"PD003   FAIL            C2\n(?:.*\n)*?        reason: (.*)", listing)
    assert fail_reason is not None
    assert "column=Accuracy, row=B" in fail_reason.group(1)
    assert "round:2.0" in fail_reason.group(1), "the reason must name the declared precision it judged at"


def test_every_rule_row_quotes_the_frozen_question_and_name() -> None:
    """The README may paraphrase nothing: the rule table repeats `rules.QUESTION` verbatim."""
    for rule_id in RULE_IDS:
        assert QUESTION[rule_id] in README, f"{rule_id} question drifted"
        assert NAME[rule_id] in README, f"{rule_id} name missing from the rule table"
    assert len(RULE_IDS) == 7
    assert README.count("| `PD0") == 7, "the rule table must carry exactly seven rows"


def test_the_documented_commands_exist(tmp_path: Path, capsys) -> None:
    """`--version`, `--help` and the `--json` form all behave as the README says."""
    for argument in ("--version", "--help"):
        with pytest.raises(SystemExit) as caught:
            main([argument])
        assert caught.value.code == 0
    printed = capsys.readouterr().out
    assert f"paper-doctor {__version__}" in printed
    assert "usage: " in printed

    report = tmp_path / "report.json"
    assert main(["audit", "examples/quickstart", "--json", str(report)]) == EXIT_OK
    assert report.read_bytes().startswith(b"[")
    assert "# paper-doctor audit" in capsys.readouterr().out, "the listing still goes to stdout"


def test_the_readme_states_what_a_fail_does_not_mean() -> None:
    """§17 boundaries, phrased as the README promises them."""
    lowered = re.sub(r"\s+", " ", README.replace("*", "").lower())
    for forbidden_claim in ("fraud", "novelty", "accepted or rejected", "theorem", "misconduct"):
        assert forbidden_claim in lowered, f"§17 boundary missing: {forbidden_claim}"
    assert "what it does not say: that the paper is false, unreliable, fraudulent, or rejected" in lowered
    assert "paper doctor cannot tell which" in lowered, "the FAIL-localization limit must be stated"
    assert "untraceable is not false" in lowered
    assert "pd006 in particular asks whether the referenced float actually prints" in lowered
    for code, meaning in (
        ("0", "the audit ran"),
        ("2", "a **declared input path that does not resolve**"),
        ("1", "failed unexpectedly"),
    ):
        assert f"| `{code}` |" in README and meaning in README, f"exit code {code} row missing"
    assert "`--json` destination whose directory does not exist" in README
    assert "twelve `p_*` validation codes are frozen" in README.lower()


def test_the_prerequisites_section_names_the_one_dependency_and_the_python_floor() -> None:
    """The first thing the measurement found missing: what a fresh environment needs before it can
    install at all. This reads `pyproject.toml`, so it cannot drift from what packaging declares."""
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    requires = re.search(r'requires-python = "([^"]+)"', text).group(1)
    floor = re.search(r"\d+\.\d+", requires).group(0)
    assert floor in README, f"the README must state the Python floor the package enforces ({requires})"
    assert "only runtime dependency is pyyaml" in re.sub(r"\s+", " ", README.lower())
    dependencies = re.findall(r'"([A-Za-z0-9_.\-]+)', text.split("dependencies = [")[1].split("]")[0])
    assert [name.lower() for name in dependencies if not name.startswith(("#",))][:1] == ["pyyaml"], dependencies
    assert "pip install paper-doctor==" in README


def test_the_example_directory_is_the_only_thing_a_first_time_user_needs_to_trust() -> None:
    """No hidden state: the example is three files, and nothing in it names a project or a corpus."""
    assert sorted(path.name for path in EXAMPLE_DIR.iterdir()) == [
        "findings.json",
        "paper-doctor.yml",
        "paper.tex",
    ]
    assert EXAMPLE_DIR.joinpath("findings.json").read_text(encoding="utf-8") == "[]\n"
    blobs = [path.read_text(encoding="utf-8") for path in EXAMPLE_DIR.iterdir()]
    for marker in ("tabm", "yandex", "rtdl", "gmmvi", "acceptance-inputs", "upstream"):
        assert all(marker not in blob.lower() for blob in blobs), f"the quickstart example names {marker}"


def _vocabulary_row(field: str) -> str:
    lines = [line for line in README.split("\n") if line.startswith(f"| `{field}` |")]
    assert len(lines) == 1, f"the README must carry exactly one `{field}` vocabulary row"
    return lines[0]


def _tokens(row: str) -> set[str]:
    """Backticked ALL_CAPS tokens -- the shape an enum member has.

    Rule/finding ids (`PD003`, `RD002`) and the status names are excluded because they legitimately
    appear in prose about a field; every other capitalised token in a vocabulary row is a claim that
    the value exists in the enum that row documents.
    """
    statuses = {status.value for status in RuleStatus}
    return {
        token
        for token in re.findall(r"`([A-Z][A-Z0-9_]*)`", row)
        if not re.fullmatch(r"(?:PD|RD)\d+", token) and token not in statuses
    }


@pytest.mark.parametrize(
    ("field", "enum"),
    [
        ("form", ClaimForm),
        ("target_kind", TargetKind),
        ("link_basis", LinkBasis),
        ("quantifier", Quantifier),
        ("universe_status", UniverseStatus),
    ],
)
def test_a_vocabulary_row_lists_exactly_the_frozen_enum(field: str, enum: type) -> None:
    """Every member must be documented, and nothing that is not a member may be documented.

    The second half is what matters: the fresh user's confusion was about which values are legal, and
    a row that names a plausible-looking value the loader rejects is worse than no row.
    """
    row = _vocabulary_row(field)
    values = {member.value for member in enum}
    for value in values:
        assert f"`{value}`" in row, f"the {field} row omits {value}"
    assert _tokens(row) - values == set(), f"the {field} row invents {sorted(_tokens(row) - values)}"


def test_the_status_section_lists_exactly_the_five_frozen_statuses() -> None:
    section = README.split("## Statuses", 1)[1].split("\n##", 1)[0]
    documented = {token for line in section.split("\n") for token in re.findall(r"^\| `([A-Z_]+)` \|", line)}
    assert documented == {status.value for status in RuleStatus}, sorted(documented)


def test_the_readme_keeps_the_two_promises_that_only_hold_by_construction() -> None:
    """Both faces of one run, and the tolerance a `PASS` was judged at, are documented promises."""
    assert "the listing still goes to stdout" in README
    assert "PD003 compares at the declared precision" in re.sub(r"\s+", " ", README.replace("*", ""))
    assert "a test pins it" in README, "the README must tell the reader the example is checked"


def test_the_declared_precision_really_governs_the_number_comparison(tmp_path: Path, capsys) -> None:
    """The README's escape hatch is real: at `round: 0` the example's 0.92 and 0.88 both round to 1.

    Proved by copying the example workspace and changing only that one declaration, so the `PASS` is
    caused by the declaration and not by a different paper.
    """
    workspace = tmp_path / "coarse"
    workspace.mkdir()
    for name in ("paper.tex", "findings.json", "paper-doctor.yml"):
        shutil.copyfile(EXAMPLE_DIR / name, workspace / name)
    text = (workspace / "paper-doctor.yml").read_text(encoding="utf-8").replace("round: 2", "round: 0")
    (workspace / "paper-doctor.yml").write_text(text, encoding="utf-8")
    assert main(["audit", str(workspace)]) == EXIT_OK
    listing = capsys.readouterr().out
    assert "PD003   PASS            C2" in listing, listing
    assert "round:0.0" in listing, "the reason must name the precision it judged at"
