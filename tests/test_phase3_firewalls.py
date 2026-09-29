"""Phase 3 §12: the generalization firewalls, as an executable check.

The acceptance target of Phase 3 is a paper this codebase was never written for. That claim is only
worth something if a test can falsify it, so this file asserts the two halves of §12 over `src/`:

* **No project name in code.** A branch, key, literal or identifier named for one audited paper --
  `tabm`, `rtdl`, `gmmvi`, `yandex`, a dataset, a model -- would mean the parser or a rule decided
  something because "TabM looks like RTDL". Names in *prose* (a comment or a docstring explaining
  which corpus a design decision was traced from) are evidence about the design, not behaviour, and
  are permitted; the test separates the two by parsing the file rather than grepping it.
* **No acceptance value anywhere.** Table numbers, split sizes, printed scores, byte sizes and
  sha256 digests of the frozen corpora must not occur in `src/` at all, comments included. A number
  that appears in a comment is one line away from being read as a default.

Tests and fixtures may name projects freely: naming the thing you test is how a test says what it
expects. This file scopes itself to `src/` for exactly that reason.
"""

from __future__ import annotations

import ast
import hashlib
import io
import re
import tokenize
from collections.abc import Iterator
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src" / "paper_doctor"

#: Names of the papers, organizations, datasets and models the four phases audited. A hit in code
#: is a project-specific branch; a hit in prose is a citation of the evidence behind a decision.
PROJECT_NAMES = (
    "tabm",
    "yandex",
    "rtdl",
    "gmmvi",
    "covertype",
    "tabred",
    "adult",
    "xgboost",
    "lightgbm",
    "catboost",
    "randomforest",
    "california_housing",
    "hyscolar",
    "default of credit",
    "maps routing",
    "python blues",
    "georgia road",
    "fried",
    "superconduct",
    "year prediction",
    "seyfux",
    "planarrobot",
    "talos",
    "breastcancer",
)

#: Values that exist only in the frozen corpora. Any of them in `src/` would be a hardcoded answer.
ACCEPTANCE_VALUES = (
    "26048",
    "16281",
    "32561",
    "6513",
    "88033",
    "12392",
    "0.858731036177139",
    "0.8583625084454272",
    "2410.24210",
    "2106.11959",
    "2209.11533",
    "28e47ae301c92ec37787dde1ce923a0793f405b4",
)

_SHA256 = re.compile(r"\b[0-9a-f]{64}\b")


def _modules() -> Iterator[tuple[Path, ast.Module]]:
    for path in sorted(SRC.rglob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"))


def _docstring_spans(tree: ast.Module) -> set[int]:
    """Every line covered by a module, class or function docstring -- prose, not code."""
    spans: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        body = getattr(node, "body", [])
        if not body or not isinstance(body[0], ast.Expr):
            continue
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            spans.update(range(value.lineno, (value.end_lineno or value.lineno) + 1))
    return spans


def _code_surface(tree: ast.Module, docstring_lines: set[int]) -> list[tuple[int, str]]:
    """The parts of a module that change behaviour: names, attributes, keywords and real literals.

    A string constant is a *literal*, not prose, unless it sits in a docstring span -- so a hidden
    `if project == "tabm"` cannot hide behind a leading `#`.
    """
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str) and node.lineno in docstring_lines:
                continue
            out.append((node.lineno, str(node.value)))
        elif isinstance(node, ast.Name):
            out.append((node.lineno, node.id))
        elif isinstance(node, ast.Attribute):
            out.append((node.lineno, node.attr))
        elif isinstance(node, ast.keyword):
            out.append((node.lineno, node.arg or ""))
        elif isinstance(node, ast.arg):
            out.append((node.lineno, node.arg))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            out.append((node.lineno, node.name))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [node.names[0].name] if isinstance(node, ast.Import) else [node.module or ""]
            out.extend((node.lineno, name) for name in names)
            out.extend((alias.lineno, alias.name) for alias in node.names)
    return out


def _comment_lines(text: str) -> set[int]:
    lines: set[int] = set()
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    for token in tokens:
        if token.type == tokenize.COMMENT:
            lines.add(token.start[0])
    return lines


def test_every_module_under_src_parses() -> None:
    """A precondition, stated so a later failure is not mistaken for a broken scanner."""
    count = 0
    for path, _tree in _modules():
        assert path.is_file()
        count += 1
    assert count >= 8, f"expected a package of modules under {SRC}, found {count}"


def test_no_project_name_appears_in_executable_code() -> None:
    """§12, first half: no branch, key, literal or identifier is named for one audited paper."""
    offenders: list[str] = []
    for path, tree in _modules():
        docstrings = _docstring_spans(tree)
        for line, surface in _code_surface(tree, docstrings):
            lowered = surface.lower()
            for name in PROJECT_NAMES:
                if name in lowered:
                    offenders.append(f"{path.relative_to(REPO).as_posix()}:{line}: {name!r} in {surface!r}")
    assert not offenders, "project-specific code found:\n" + "\n".join(sorted(set(offenders)))


def test_project_names_in_src_are_confined_to_comments_and_docstrings() -> None:
    """The same occurrences, checked from the other side: what is left when prose is removed is clean.

    This is the assertion that makes the prose exemption honest. If a name moves out of a comment
    into code, the previous test catches it; if a name appears somewhere neither test's notion of
    prose or code covers -- a raw byte string in an unusual node -- this one catches it.
    """
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        prose = _docstring_spans(tree) | _comment_lines(text)
        for number, line in enumerate(text.split("\n"), start=1):
            lowered = line.lower()
            hits = [name for name in PROJECT_NAMES if name in lowered]
            if hits and number not in prose:
                raise AssertionError(f"{path.relative_to(REPO).as_posix()}:{number}: {hits} outside prose: {line!r}")


def test_no_acceptance_value_or_digest_occurs_anywhere_in_src() -> None:
    """§12, second half: the frozen numbers, identifiers and digests never enter the implementation."""
    offenders: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for value in ACCEPTANCE_VALUES:
            if value in text:
                offenders.append(f"{path.relative_to(REPO).as_posix()}: carries the acceptance value {value!r}")
        for match in _SHA256.finditer(text):
            offenders.append(f"{path.relative_to(REPO).as_posix()}: carries a literal sha256 {match.group()[:12]}...")
    assert not offenders, "hardcoded acceptance evidence found:\n" + "\n".join(offenders)


def test_src_carries_no_path_to_a_corpus_checkout() -> None:
    """The implementation is given corpora by a manifest; it never knows where one lives."""
    offenders = []
    markers = ("f:/", "c:/users", "/mnt/", "upstream/", "phase0/sources", "acceptance-inputs")
    for path, tree in _modules():
        for line, surface in _code_surface(tree, _docstring_spans(tree)):
            lowered = surface.lower().replace("\\", "/")
            for marker in markers:
                if marker in lowered:
                    offenders.append(f"{path.relative_to(REPO).as_posix()}:{line}: {marker!r} in {surface!r}")
    assert not offenders, "src knows a corpus location:\n" + "\n".join(sorted(set(offenders)))


def test_the_package_imports_no_sibling_doctor() -> None:
    """Paper Doctor reads Result Doctor's artifact; it does not import Result Doctor's code."""
    for _path, tree in _modules():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("result_doctor", "experiment_doctor", "dataset_doctor"))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in ("result_doctor", "experiment_doctor", "dataset_doctor")


# --- §20 credential / privacy gate --------------------------------------------------------------
#
# An artifact is a publication. Everything below is checked over the files that MANIFEST.in and
# pyproject.toml actually put into a wheel or sdist, because those are the bytes that leave this
# machine, not the bytes in the design folders that stay here.

#: Top-level files that ship.
SHIP_FILES = (
    REPO / "README.md",
    REPO / "CHANGELOG.md",
    REPO / "LICENSE",
    REPO / "pyproject.toml",
    REPO / "MANIFEST.in",
)

#: Directories that ship, in full.
SHIP_DIRS = ("src", "tests", "scripts", "examples")

#: An absolute path on a developer machine: a drive letter with a folder under it, or a POSIX home
#: two levels deep, or an AppData tree. The drive alternative demands a segment *and* a following
#: separator, so a marker literal such as "c:/users" in another test's tuple is not a leak while a
#: drive-rooted folder path is.
_LOCAL_PATH = re.compile(
    r"""(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\\/\s"'`,)\]]+[\\/]"""
    r"""|[\\/]Users[\\/][^\\/\s"'`,)\]]+[\\/]"""
    r"""|[\\/]home[\\/][^\\/\s"'`,)\]]+[\\/]"""
    r"""|AppData[\\/]"""
)

#: The account name this work was done under, written as escapes so this file cannot itself carry it.
_LOCAL_ACCOUNT = re.compile(r"[\\/]\u5317\u6d77[\\/]")

#: Shapes a real secret takes. A sha256 digest is not one of them and is deliberately not matched.
#: The literals are built so this file never spells a shape it would then have to report.
_SECRET_SHAPE = re.compile(
    "|".join(
        [
            r"ghp_[A-Za-z0-9]{20,}",
            r"github_pat_[A-Za-z0-9_]{20,}",
            r"AKIA[0-9A-Z]{16}",
            r"\-{5}BEGIN [A-Z ]*PRIVATE KEY\-{5}",
            r"x-access-token\x40",
            r"(?i:authorization:\s*bearer\s+[A-Za-z0-9._\-]{30,})",
        ]
    )
)


#: Third-party bytes that ship as pinned test inputs, and the digest they were vendored at. The privacy
#: scan skips a file here ONLY while its digest still matches, so the skip cannot be widened into an
#: exemption: replace or edit one line and the file is scanned again and its contents are reported.
#: Vendored upstream prose carries example paths that are nobody's machine, ours included; a fixture is
#: not a leak, and a fixture that could be edited without failing is.
VENDOR_BYTES = {
    "tests/fixtures/rtdl_pilot_README.md": "50f7994f73937093c01412164e07142d198c000fcb69a01041c7404552ca0215",
}


def _shipped_text() -> Iterator[tuple[str, str]]:
    """Yield (relative posix path, text) for every file that goes into an artifact."""
    paths = list(SHIP_FILES)
    for name in SHIP_DIRS:
        paths += [p for p in sorted((REPO / name).rglob("*")) if p.is_file()]
    for path in paths:
        try:
            data = path.read_bytes()
        except OSError:
            continue
        relpath = path.relative_to(REPO).as_posix()
        if _pinned_vendored(relpath, data):
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        yield relpath, text


def _pinned_vendored(relpath: str, data: bytes) -> bool:
    """True only while an allowlisted third-party file is still byte-identical to what was pinned."""
    want = VENDOR_BYTES.get(relpath)
    return want is not None and hashlib.sha256(data).hexdigest() == want


def _lines_matching(pattern: re.Pattern[str]) -> list[str]:
    offenders: list[str] = []
    for relpath, text in _shipped_text():
        for number, line in enumerate(text.split("\n"), start=1):
            if pattern.search(line):
                offenders.append(f"{relpath}:{number}: {line.strip()[:120]}")
    return offenders


def test_no_shipped_file_describes_this_machines_filesystem() -> None:
    """§20: a public artifact must not disclose the local folder layout it was built in."""
    offenders = _lines_matching(_LOCAL_PATH) + _lines_matching(_LOCAL_ACCOUNT)
    assert not offenders, "shipped files carry a local path:\n" + "\n".join(sorted(set(offenders)))


def test_no_shipped_file_carries_a_credential_shape() -> None:
    """§20: no token, key material or keyed URL may reach an artifact."""
    offenders = _lines_matching(_SECRET_SHAPE)
    assert not offenders, "shipped files carry a credential shape:\n" + "\n".join(sorted(set(offenders)))


def test_the_privacy_patterns_themselves_detect_a_leak() -> None:
    """A gate that matches nothing is a gate that was never closed.

    The two scans above are only evidence if the patterns fire on the shapes they name. Every string
    here is synthetic and built with escapes, so naming a shape cannot make this file the leak the
    gate is looking for.
    """
    assert _LOCAL_PATH.search("read the paper from \x44:\\checkout\\src\\main.tex")
    assert _LOCAL_PATH.search("audit /home/" + "someone/paper/main.tex")
    assert _LOCAL_PATH.search("C:\\App" + "Data\\Roaming\\anything")
    assert _LOCAL_PATH.search("F:\\" + "SomeRoot\\project\\phase0-x")
    assert _LOCAL_ACCOUNT.search("/some/where/\u5317\u6d77/inside")
    assert _SECRET_SHAPE.search("ghp_" + "a" * 36)
    assert _SECRET_SHAPE.search("\x2d" * 5 + "BEGIN OPENSSH PRIVATE KEY" + "\x2d" * 5)
    assert _SECRET_SHAPE.search("Author" + "ization: Bearer " + "x" * 40)
    assert _SECRET_SHAPE.search("git@github.com\x3ax-access-token" + "@" + "/some/private.git")
    # And the tolerances are real: a marker literal and a frozen digest must not trip it.
    assert not _LOCAL_PATH.search('markers = ("f:/", "c:/users", "/mnt/")')
    assert not _LOCAL_PATH.search("sha256 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570")
    assert not _LOCAL_PATH.search("pip install -e .[dev]")
    assert not _SECRET_SHAPE.search("sha256: 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570")


def test_vendored_third_party_bytes_are_still_what_they_were_pinned_as() -> None:
    """The privacy scan's only skip is a digest match, so the skip has to be checked in its turn."""
    assert VENDOR_BYTES, "the allowlist is empty while a vendored file exists, or vice versa"
    for relpath, want in VENDOR_BYTES.items():
        path = REPO / relpath
        assert path.is_file(), f"allowlisted file is gone: {relpath}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == want, relpath


def test_the_vendored_skip_is_narrow_and_widens_to_nothing_else() -> None:
    """Exactly two facts, both falsifiable: a pinned file is skipped, an unpinned one is scanned."""
    pinned = list(VENDOR_BYTES)
    assert _pinned_vendored(pinned[0], (REPO / pinned[0]).read_bytes())
    assert not _pinned_vendored(pinned[0], b"one edited line of somebody else's prose")
    assert not _pinned_vendored("tests/support.py", (REPO / "tests" / "support.py").read_bytes())
    scanned = {rel for rel, _ in _shipped_text()}
    assert pinned[0] not in scanned
    assert "tests/support.py" in scanned and "README.md" in scanned
