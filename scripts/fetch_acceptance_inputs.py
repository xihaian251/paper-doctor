"""Fetch and verify the read-only paper corpora the acceptance tests audit.

Paper Doctor itself never reaches the network; this is a development script that lives outside
`src/` and is the documented way to rebuild the corpora the frozen manifests point at, so the
acceptance tests can run in a fresh checkout without vendoring anyone's paper source.

Every artifact carries a pinned sha256. The download is verified before anything is written, and a
target that already exists is checked, never overwritten: a digest mismatch is a refusal (exit 2),
not a silent re-download, because a corpus that drifted mid-acceptance invalidates the freeze.

```text
python scripts/fetch_acceptance_inputs.py --list
python scripts/fetch_acceptance_inputs.py tabm
python scripts/fetch_acceptance_inputs.py            # all of them
```

The three corpora are the papers whose anchors the frozen test suites read:

| name  | arXiv         | used by                                 |
| ----- | ------------- | --------------------------------------- |
| rtdl  | 2106.11959    | Phase 1/2 RTDL anchors D1-D11           |
| gmmvi | 2209.11533v2  | Phase 1 GMMVI anchors C1/C5/C6          |
| tabm  | 2410.24210    | Phase 3 unseen end-to-end acceptance    |
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Corpus:
    """One pinned input: an arXiv e-print tarball, its digest, and where it unpacks."""

    name: str
    arxiv_id: str
    tarball_sha256: str
    target: Path
    main_file: str
    main_sha256: str


CORPORA: dict[str, Corpus] = {
    "rtdl": Corpus(
        name="rtdl",
        arxiv_id="2106.11959",
        tarball_sha256="eebd40f5d9101237b6af85a216bdf70c5a0877592eaa20b2bb1b8a3b68aee8b9",
        target=REPO / "phase0" / "sources" / "2106.11959.tex",
        main_file="main.tex",
        main_sha256="10071f8e34efa1c54db9d6684244b60bd81c39b8f098678b6efa8bd148150c43",
    ),
    "gmmvi": Corpus(
        name="gmmvi",
        arxiv_id="2209.11533v2",
        tarball_sha256="a2496e282bb4bb262e28bac0cd1a542ccb86f3ee93fcfabd6159f6c48db09516",
        target=REPO / "phase0" / "sources" / "2209.11533v2.tex",
        main_file="arxiv.tex",
        main_sha256="08fb26e0680b7e42565b2db839d3e55fccafd1847faf1bf9dbae2bc0a5a2f800",
    ),
    "tabm": Corpus(
        name="tabm",
        arxiv_id="2410.24210",
        tarball_sha256="cdcea2ddbe710fa6e9c19b0e611e0c82dd513491aa6ac680368ed5bc3127db8c",
        target=REPO / "phase3" / "acceptance-inputs" / "tabm-arxiv" / "src",
        main_file="main.tex",
        main_sha256="15663553d04fcbb8b3341df5c0d269c7703d4ba279be557fcd77ea4765ab0a62",
    ),
}


class Blocked(Exception):
    """A pin that the world no longer satisfies. Exit 2: this is a blocker, not a bug."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _main_matches(corpus: Corpus) -> bool:
    """True when the target already holds the exact frozen main file."""
    main = corpus.target / corpus.main_file
    return main.is_file() and _sha256(main) == corpus.main_sha256


def _extract(corpus: Corpus, tarball: Path) -> None:
    """Unpack verified bytes into the target, refusing members that escape it or link elsewhere."""
    target = corpus.target.resolve()
    corpus.target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball, "r:*") as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise Blocked(f"archive member {member.name!r} would land outside {target}")
            if member.issym() or member.islnk():
                raise Blocked(f"archive member {member.name!r} is a link; a corpus is plain files")
            if not (member.isfile() or member.isdir()):
                continue
            destination = (target / name).resolve()
            if destination != target and target not in destination.parents:
                raise Blocked(f"archive member {member.name!r} resolves outside {target}")
            if hasattr(tarfile, "data_filter"):
                archive.extract(member, target, filter="data")
            else:  # Python 3.11.0-3.11.3 have no filter; the explicit guards above do the work.
                archive.extract(member, target)


def fetch(corpus: Corpus, *, keep_tarball: bool) -> str:
    """Ensure the corpus is on disk and matches its pin."""
    if corpus.target.exists():
        if _main_matches(corpus):
            return f"SKIPPED    {corpus.name}: {corpus.target} already carries the frozen {corpus.main_file}"
        raise Blocked(
            f"{corpus.target} exists but its {corpus.main_file} does not match the pinned sha256 "
            f"{corpus.main_sha256}. A corpus that drifted is a blocker, not something to overwrite."
        )
    url = f"https://arxiv.org/e-print/{corpus.arxiv_id}"
    staging = Path(tempfile.mkdtemp(prefix=f"paper-doctor-{corpus.name}-"))
    try:
        tarball = staging / f"{corpus.arxiv_id}.eprint"
        request = urllib.request.Request(url, headers={"User-Agent": "paper-doctor-acceptance-inputs/0.1.0"})
        with urllib.request.urlopen(request, timeout=120) as response, tarball.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        observed = _sha256(tarball)
        if observed != corpus.tarball_sha256:
            raise Blocked(
                f"{url} returned sha256 {observed}, not the pinned {corpus.tarball_sha256}. The upstream "
                f"source changed after the freeze; the acceptance stays blocked until a human re-decides the pin."
            )
        _extract(corpus, tarball)
        if not _main_matches(corpus):
            raise Blocked(
                f"{corpus.target} unpacked but its {corpus.main_file} does not match the pin. The target "
                f"is left in place for inspection."
            )
        if keep_tarball:
            cached = corpus.target.parent / f"{corpus.arxiv_id}.eprint"
            shutil.copyfile(tarball, cached)
            return f"DOWNLOADED {corpus.name}: {corpus.target} (verified tarball kept at {cached})"
        return f"DOWNLOADED {corpus.name}: {corpus.target}"
    except urllib.error.URLError as exc:
        raise Blocked(f"{url} is unreachable ({exc}). Nothing was written.") from exc
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fetch-acceptance-inputs",
        description="Fetch and verify the pinned paper corpora the acceptance tests read.",
    )
    parser.add_argument("names", nargs="*", choices=sorted(CORPORA), help="corpora to fetch (default: all)")
    parser.add_argument("--list", action="store_true", help="print the pins and their state, then exit")
    parser.add_argument(
        "--keep-tarball",
        action="store_true",
        help="also store the verified e-print tarball next to the corpus, so re-extraction needs no network",
    )
    args = parser.parse_args(argv)

    if args.list:
        for corpus in CORPORA.values():
            state = "present" if _main_matches(corpus) else "absent"
            print(f"{corpus.name}\t{corpus.arxiv_id}\t{state}\t{corpus.target.relative_to(REPO).as_posix()}")
        return 0

    try:
        for name in args.names or sorted(CORPORA):
            print(fetch(CORPORA[name], keep_tarball=args.keep_tarball))
    except Blocked as blocked:
        print(f"PAPER DOCTOR FETCH: BLOCKED -- {blocked}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
