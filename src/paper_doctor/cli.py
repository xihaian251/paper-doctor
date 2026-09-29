"""The command-line face of Paper Doctor (Phase 1 §22, Phase 2 §11).

`audit` is deliberately thin: it loads the manifest once, runs the same `audit_bundle` the
acceptance tests call, and prints the findings that come back. Nothing here judges anything. There
is no score, no paper verdict and no overall grade; the closing census counts findings and says
nothing about whether they are good.

The human listing is one block per finding: rule id, status, target, then the claim's declared form,
its source locator, its link ids, and the reason in full.

Exit codes keep the two kinds of "bad" apart:

```text
0  the audit ran, whatever the rules said
2  the manifest is not a readable contract (or the command line itself was wrong)
1  the tool failed unexpectedly
```

A `FAIL` or `INCONCLUSIVE` about a claim exits 0. Finding an inconsistency is the tool working,
not the tool breaking.

Two authoring facts the help text repeats, because they are what a new user asks first:

* A directory argument resolves to the one fixed name `paper-doctor.yml` inside it. The CLI
  never searches for a manifest and never picks one up from a file or directory name.
* Paper paths inside a manifest are relative to `_registry.paper.root`, which resolves relative
  to the directory holding the manifest. The upstream findings artifact is relative to the
  manifest itself, because it is a declared input rather than paper text.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from . import __version__
from .audit import Bundle, audit_bundle, bundle_from_manifest
from .manifest import MANIFEST_NAME, ManifestError
from .status import RuleFinding, RuleStatus, write_json

EXIT_OK = 0
EXIT_TOOL_ERROR = 1
EXIT_INPUT_ERROR = 2

STATUS_ORDER = (
    RuleStatus.PASS,
    RuleStatus.FAIL,
    RuleStatus.INCONCLUSIVE,
    RuleStatus.NOT_APPLICABLE,
    RuleStatus.NOT_RUN,
)


def _force_utf8_stdout() -> None:
    """Keep output byte-stable when stdout is redirected.

    On Windows a redirected stream gets the locale codepage, and a finding that quotes a paper
    sentence or a printed cell can then raise on encode. Console output is already UTF-8, so
    this only takes effect for files and pipes.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    encoding = str(getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "")
    if reconfigure is not None and encoding not in ("utf8", "utf16", "utf32"):
        reconfigure(encoding="utf-8")


def _one_line(text: str) -> str:
    return " ".join(text.split())


def claim_columns(bundle: Bundle) -> dict[str, str]:
    """Per-claim presentation text for the human listing (Phase 2 §11).

    The three facts a new user asks for first -- what kind of claim this is, where in the source it
    sits, and which declared links carry its evidence -- are properties of the *manifest*, not of a
    rule, so they are joined here at presentation time. `RuleFinding` keeps Contract I-1's eight keys
    untouched: nothing in this mapping can change what a rule decided or how `--json` serialises it.
    """
    columns: dict[str, str] = {}
    for claim in bundle.claims:
        where = claim.locator.path
        if claim.locator.line:
            where = f"{where}:{claim.locator.line}"
        links = ", ".join(link.link_id for link in claim.link_refs)
        columns[claim.claim_id] = f"form={claim.form.value}  locator={where}  links=[{links}]"
    return columns


def render_text(findings: Sequence[RuleFinding], columns: Mapping[str, str] | None = None) -> str:
    """One line per finding in `(rule_id, target)` order, then the status census.

    A long reason stays on its own indented line rather than being truncated: shortening an
    evidence sentence silently would be a scientific loss, while the table stays scannable
    because rule, status and target sit in fixed columns.
    """
    ordered = sorted(findings, key=lambda f: (f.rule_id, f.target))
    lines: list[str] = []
    for finding in ordered:
        lines.append(f"{finding.rule_id:<6}  {finding.status.value:<14}  {finding.target}")
        declared = (columns or {}).get(finding.target)
        if declared:
            lines.append(f"        claim:  {declared}")
        if finding.reason:
            lines.append(f"        reason: {_one_line(finding.reason)}")
    counts = {status: sum(1 for f in ordered if f.status is status) for status in STATUS_ORDER}
    lines.append("")
    lines.extend(f"{status.value}: {counts[status]}" for status in STATUS_ORDER)
    return "\n".join(lines) + "\n"


def manifest_path(target: str) -> str:
    """A directory means `<dir>/paper-doctor.yml`; anything else is used as given."""
    path = Path(target)
    return str(path / MANIFEST_NAME) if path.is_dir() else target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-doctor",
        description="Audit whether an explicitly linked paper claim is faithful to the reported evidence behind it.",
        epilog=(
            "Rule statuses are exactly PASS | FAIL | INCONCLUSIVE | NOT_APPLICABLE | NOT_RUN.\n"
            "  PASS            this narrow relation agrees with the evidence on file - nothing more\n"
            "  FAIL            one rule found the claim disagree with the evidence for this target"
            " - not a failed experiment or paper\n"
            "  INCONCLUSIVE    the evidence on file is insufficient to decide\n"
            "  NOT_APPLICABLE  this target has no such relation to check\n"
            "  NOT_RUN         no target of the class this rule reads was supplied\n"
            "Paper Doctor never re-audits a Result Doctor finding, never upgrades upstream\n"
            "certainty, and never concludes that a paper is reliable, unreliable, or\n"
            "cherry-picked.\n\n"
            "Exit codes: 0 = the audit ran, whatever it found; 2 = the manifest is not a readable"
            " contract; 1 = the tool failed unexpectedly."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"paper-doctor {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    audit = commands.add_parser(
        "audit",
        help="load a manifest, run PD001-PD007, print the findings",
        description=(
            "Read a `paper-doctor.yml` and print one line per finding. The manifest is evidence"
            " only: the tool reads the artifacts it quotes, it does not look for them."
        ),
        epilog=(
            "Give it the manifest itself, or a directory containing `paper-doctor.yml`.\n"
            "If a manifest cannot be read as a contract the command stops with exit 2 and prints"
            " `{code} at {where}: {problem}` unchanged - the code, the field path, and the fix."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    audit.add_argument("path", help="a paper-doctor.yml, or a directory containing one")
    audit.add_argument(
        "--json",
        metavar="REPORT_JSON",
        help="also write the full findings, as canonical JSON, to this file",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _force_utf8_stdout()
    args = build_parser().parse_args(argv)
    manifest = manifest_path(args.path)
    if args.json:
        # Checked before the audit, not after the listing is printed: an unusable report path is
        # the user's input, so it leaves exit 2 with a sentence, not a traceback after the work.
        destination = Path(args.json)
        parent = destination.parent
        if str(parent) and not parent.is_dir():
            print(
                f"paper-doctor: --json cannot write to {destination}: "
                f"the directory {parent if str(parent) else '.'} does not exist. Create it, or name"
                f" a path inside a directory that does.",
                file=sys.stderr,
            )
            return EXIT_INPUT_ERROR
    try:
        bundle = bundle_from_manifest(manifest)
        findings = audit_bundle(bundle)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INPUT_ERROR
    print(f"# paper-doctor audit {Path(manifest).as_posix()}")
    sys.stdout.write(render_text(findings, claim_columns(bundle)))
    if args.json:
        write_json(list(findings), args.json)
    return EXIT_OK
