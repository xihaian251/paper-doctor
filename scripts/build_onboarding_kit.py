"""Build the Phase 3 §15 human-onboarding kit from the release tree.

The kit is what a tester who has never seen this project receives: the README, the artifacts to
install, the prepared TabM acceptance workspace, and the one fetch step that workspace needs. Nothing
else, and above all nothing that carries an answer - a tester handed the project's own expected audit
output can produce the right result without using the tool, which would measure nothing.

```text
python scripts/build_onboarding_kit.py          # writes release/onboarding-kit/
```

The directory it writes is not part of the repository: it contains build artifacts, and it is
regenerated on demand. `release/onboarding/README.md` documents the run procedure around it.

The layout is load-bearing. `phase3/tabm/paper-doctor.yml` declares
`root: ../acceptance-inputs/tabm-arxiv/src`, and `fetch_acceptance_inputs.py` resolves its target
against its own parent directory, so putting the script at `<kit>/scripts/` and the workspace at
`<kit>/phase3/tabm/` makes the fetch land exactly where the manifest already points. A kit assembled
any other way would need the manifest edited, and the manifest is what is being tested.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KIT = REPO / "release" / "onboarding-kit"
SOURCES = REPO / "release" / "onboarding"

#: A kit must not contain these under any name: expected outputs of this project, or its design text.
FORBIDDEN = (
    "pd_audit",
    "pd_findings",
    "end_to_end_chain",
    "preflight",
    "brief",
    "erratum",
    "handoff",
    "report",
    "research-log",
    "findings.md",
    "measurement",
    "acceptance-inputs",
    "tools",
)

#: What the workspace needs in order to be a declared, self-describing input.
WORKSPACE_FILES = ("paper-doctor.yml", "findings.json")

#: The two files a human reads and writes.
PEOPLE_FILES = ("TASK_FOR_TESTER.md", "RECORDING_SHEET.md")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Blocked(RuntimeError):
    """The kit as assembled would leak an answer or a design document."""


def _copy(src: Path, dest: Path) -> None:
    if not src.is_file():
        raise Blocked(f"missing source {src.relative_to(REPO).as_posix()}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def assemble() -> list[str]:
    notes: list[str] = []
    _copy(REPO / "README.md", KIT / "README.md")
    notes.append(f"README.md ({(KIT / 'README.md').stat().st_size} bytes)")

    script = REPO / "scripts" / "fetch_acceptance_inputs.py"
    _copy(script, KIT / "scripts" / script.name)
    notes.append("scripts/fetch_acceptance_inputs.py")

    for name in WORKSPACE_FILES:
        _copy(REPO / "phase3" / "tabm" / name, KIT / "phase3" / "tabm" / name)
        notes.append(f"phase3/tabm/{name}")

    for name in PEOPLE_FILES:
        _copy(SOURCES / name, KIT / name)
        notes.append(name)

    artifacts = sorted((REPO / "dist").glob("paper_doctor-0.1.0*"))
    if len(artifacts) != 2:
        raise Blocked(f"expected a wheel and an sdist in dist/, found {len(artifacts)}: {artifacts}")
    for artifact in artifacts:
        _copy(artifact, KIT / "dist" / artifact.name)
        notes.append(f"dist/{artifact.name}")
    return notes


def check_purity() -> list[str]:
    offenders: list[str] = []
    for path in sorted(p for p in KIT.rglob("*") if p.is_file() and p.name != "KIT_MANIFEST.txt"):
        rel = path.relative_to(KIT).as_posix().lower()
        for token in FORBIDDEN:
            if token in rel:
                offenders.append(f"{rel} carries {token!r}")
    return offenders


def write_manifest() -> list[str]:
    header = [
        "# Kit manifest - verify before handing the kit over, and again when it comes back.",
        "",
        "```text",
        "sha256sum -c KIT_MANIFEST.txt   # from inside the kit directory",
        "```",
        "",
        "Only the kit's own files are listed. The paper source is not: it is somebody else's bytes,",
        "and `scripts/fetch_acceptance_inputs.py` verifies it against a pinned digest as it downloads.",
        "",
    ]
    members = sorted(p for p in KIT.rglob("*") if p.is_file() and p.name != "KIT_MANIFEST.txt")
    lines = [f"{_sha256(p)}  {p.relative_to(KIT).as_posix()}" for p in members]
    (KIT / "KIT_MANIFEST.txt").write_text("\n".join(header + lines) + "\n", encoding="utf-8", newline="\n")
    return [p.relative_to(KIT).as_posix() for p in members]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build-onboarding-kit", description=__doc__.splitlines()[0])
    parser.add_argument("--clean", action="store_true", help="remove the kit directory and exit")
    args = parser.parse_args(argv)

    if args.clean:
        shutil.rmtree(KIT, ignore_errors=True)
        print(f"removed {KIT.relative_to(REPO).as_posix()}")
        return 0

    try:
        if KIT.exists():
            shutil.rmtree(KIT)
        KIT.mkdir(parents=True)
        for note in assemble():
            print("BUILD    ", note)
        offenders = check_purity()
        if offenders:
            raise Blocked("kit is not answer-free: " + "; ".join(offenders))
        for member in write_manifest():
            print("MEMBER   ", member)
    except Blocked as blocked:
        print(f"paper-doctor-kit: refused. {blocked}", file=sys.stderr)
        return 2
    total = sum(p.stat().st_size for p in KIT.rglob("*") if p.is_file())
    print(f"READY    {KIT.relative_to(REPO).as_posix()} - {total} bytes, purity clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
