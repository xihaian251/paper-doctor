"""The corpus fetcher's own argument surface, tested on whatever interpreter runs the suite.

`scripts/fetch_acceptance_inputs.py` is the only documented way to rebuild the corpora the frozen
acceptance anchors read, and it is shipped in the sdist. Its no-name form -- "fetch all three", the
one CI and the README both use -- broke on CPython 3.11 alone: argparse there validated the empty
list produced by `nargs="*"` against the argument's `choices` and refused the invocation with
`invalid choice: []`, while 3.12 and later parsed it fine. The project declares `>=3.11`, so the
support floor was the broken end, and the failure surfaced in CI rather than in the local suite
because it is version-dependent.

These tests pin the behaviour rather than the implementation, so they fail on 3.11 against the
pre-fix script and pass against the fixed one on every supported version.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "fetch_acceptance_inputs.py"

#: The three corpora the frozen anchors read, in the order `sorted(CORPORA)` yields them.
ALL_CORPORA = ["gmmvi", "rtdl", "tabm"]


def _clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    return env


def _fetcher():
    assert SCRIPT.is_file(), SCRIPT
    spec = importlib.util.spec_from_file_location("paper_doctor_fetch_inputs", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before execution: the script's `@dataclass` Corpora resolve their module through
    # sys.modules at class-creation time, and an unregistered module raises AttributeError there.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_the_parser_accepts_the_no_argument_form() -> None:
    """The 3.11 regression: parsing zero names must succeed, not reject `[]` as a choice."""
    args = _fetcher()._build_parser().parse_args([])
    assert args.names == []


def test_naming_no_corpus_selects_every_pinned_corpus() -> None:
    fetcher = _fetcher()
    assert fetcher._selected([], valid=sorted(fetcher.CORPORA)) == ALL_CORPORA


def test_naming_one_corpus_selects_only_that_one() -> None:
    fetcher = _fetcher()
    assert fetcher._selected(["tabm"], valid=sorted(fetcher.CORPORA)) == ["tabm"]
    assert set(fetcher.CORPORA) == set(ALL_CORPORA)


def test_an_unknown_corpus_name_is_refused_with_exit_2() -> None:
    fetcher = _fetcher()
    try:
        fetcher._selected(["tabme"], valid=sorted(fetcher.CORPORA))
    except SystemExit as exit_:
        assert exit_.code == 2, exit_.code
    else:
        raise AssertionError("a corpus that does not exist must not be fetched silently")


def test_the_no_name_invocation_runs_on_this_interpreter(tmp_path: Path) -> None:
    """End to end, no network: `--list` walks the same parser and prints the three pins."""
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=tmp_path,
        env=_clean_env(),
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert [line.split("\t")[0] for line in lines] == ["rtdl", "gmmvi", "tabm"], completed.stdout


def test_the_bad_name_is_refused_through_the_cli_too(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "tabme"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=tmp_path,
        env=_clean_env(),
        check=False,
    )
    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "tabme" in completed.stderr
    assert "invalid choice" not in completed.stderr, "the message must name the bad word, not []"
