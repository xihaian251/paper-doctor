# Paper Doctor 0.1.0 — Release Freeze Record

Phase 3 §25. Written after the publish succeeded, from re-measured commands, on 2026-09-29.
Every value below was read from the remote system or from a freshly executed command, not from
this document's own earlier drafts.

## 1. Release identity

| Item | Value | How it was verified |
|---|---|---|
| Release commit | `2a02698637f35bd3fec28d98a8b6e272b8e1fc9a` ("docs: name the condition the tag is actually waiting on") | `git rev-parse HEAD` on a clean `main` |
| Tag | `v0.1.0`, annotated | created with per-command `-c user.name/-c user.email`, git config untouched |
| Tag object | `cd49fcdd705f14a9a03924843c79259909be5db4` | `git for-each-ref refs/tags/v0.1.0 --format='%(objecttype) %(objectname) %(*objectname)'` → `tag cd49fcdd 2a026986` |
| Tag peel | `2a02698637f35bd3fec28d98a8b6e272b8e1fc9a` | `git rev-parse v0.1.0^{}` |
| Remote tag | `refs/tags/v0.1.0` = `cd49fcdd…`, `refs/tags/v0.1.0^{}` = `2a02698…` | `git ls-remote origin 'refs/tags/v*'` after `git push origin refs/tags/v0.1.0` (`* [new tag]`) |
| GitHub Release | id `399044218`, <https://github.com/xihaian251/paper-doctor/releases/tag/v0.1.0>, `draft=false`, `prerelease=false`, `target_commitish=2a02698637f35bd3fec28d98a8b6e272b8e1fc9a` (pinned to the exact SHA, not to a branch name), `published_at=2026-09-29T10:38:21Z`, 0 assets | REST `POST /repos/.../releases` built by Python from a notes file; only derived fields printed; `GET /releases/latest` returns `v0.1.0` and the same id |
| Publishing route | GitHub Actions OIDC trusted publishing. Run `36556801154`, event `release`, on `2a026986`, `conclusion=success`; all 7 job steps success (checkout, setup-python, build, record artifacts, `twine check` metadata, publish with the OIDC token) | Jobs API, step-by-step |
| Trusted publisher | PyPI pending publisher: project `paper-doctor`, GitHub `xihaian251/paper-doctor`, workflow `publish-pypi.yml`, environment `pypi` — created **before** the Release, as §22 requires; it became an ordinary publisher when the first upload created the project | PyPI account page after submit; the project now exists |
| Long-lived credentials | none anywhere. The workflow has no `secrets:` reference; the repository has no PyPI token. The only token handled during this session was a Git Credential Manager token held in a shell variable, used for two authenticated API calls, never printed, then `unset` | `.github/workflows/publish-pypi.yml`; the credential-shape scan in §4 |
| GitHub environment | `pypi` exists (created by the run), `protection_rules: []` | `GET /repos/.../environments/pypi` |
| License metadata | `License-Expression: Apache-2.0`, `License-File: LICENSE` in the published wheel METADATA | read from the **downloaded** wheel |

## 2. Published artifact identity (the real PyPI bytes)

`§24: "Do not assume CI rebuild hashes equal local staged hashes."` They are not equal, and this
section is the reason the published identity must come from the downloaded files.

Downloaded from `files.pythonhosted.org` in this session and hashed from the downloaded bytes:

| File | Bytes | SHA256 of downloaded bytes | SHA256 in the PyPI JSON API | Equal |
|---|---|---|---|---|
| `paper_doctor-0.1.0-py3-none-any.whl` | 67,719 | `10a5fc2cfe28155b6647edb85fd0e74422e814efc7ac1685a436b06226928461` | `10a5fc2cfe28155b6647edb85fd0e74422e814efc7ac1685a436b06226928461` | yes |
| `paper_doctor-0.1.0.tar.gz` | 182,137 | `29b759f815d60dc896901eeec3fa3e125faa2caa1e184d4908dbb4d292a11d2e` | `29b759f815d60dc896901eeec3fa3e125faa2caa1e184d4908dbb4d292a11d2e` | yes |

PyPI carries exactly one version: `0.1.0`. Sizes were asserted equal to the API `size` field, not
taken on trust.

These hashes **differ** from the locally staged artifacts recorded in `release/RC_AUDIT.md` §2
(wheel `6e051f33318518c7…`, sdist `3432437a7867f347…`). Those local hashes are a superseded
staging record; they are not the published identity and must not be quoted as such.

## 3. Content identity between the CI build and the local build

Archive-level hashes differ because `build` stamps tar/zip member metadata; the meaningful
comparison is member-by-member with newline normalisation, run here against the **downloaded**
files:

| Artifact | File members | Names equal | Members whose content differs |
|---|---|---|---|
| wheel | local 16 / PyPI 16 | yes | 2: `paper_doctor-0.1.0.dist-info/METADATA` and `…/RECORD` |
| sdist | local 51 / PyPI 51 | yes | 0 |

Every `.py` module, the LICENSE, and all data files hash-identical between the local wheel and the
published wheel. The METADATA difference is line endings only: the local build serialised METADATA
with CRLF (23,814 B), the CI build on Linux wrote LF (23,372 B); after normalisation the two long
descriptions are byte-equal to each other **and** both equal the 22,935-byte `README.md` on disk
(427 lines in each). `RECORD` differs only because it carries METADATA's hash and size
(`…,23814` locally vs `…,23372` on PyPI). The mechanism that made the Windows build choose CRLF
for this one generated file is **not established here** — recorded as an observation, not an
explanation. It does not touch shipped code, and §4 proves the published wheel produces the frozen
acceptance bytes.

## 4. Fresh install from PyPI (§24, on this machine after publishing)

New venv (`.check/v-pypi`), no editable install, no local artifact, `--no-cache-dir`, installed
**by version**:

| Check | Result |
|---|---|
| `pip install paper-doctor==0.1.0` | rc 0; resolved from PyPI (`Downloading paper_doctor-0.1.0-py3-none-any.whl (67 kB)`), `Successfully installed PyYAML-6.0.3 paper-doctor-0.1.0` |
| `pip check` | rc 0 — `No broken requirements found.` |
| `pip show paper-doctor` | `Name: paper-doctor`, `Version: 0.1.0`, `Requires: PyYAML` |
| `paper-doctor --version` | rc 0 — `paper-doctor 0.1.0` |
| `paper-doctor --help` | rc 0 — `usage: paper-doctor [-h] [--version] {audit} ...` |
| `paper-doctor audit phase3/tabm --json out` | rc 0, 17,511 B written, digest `08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0` → **MATCHES the frozen pre-release acceptance anchor** |
| `paper-doctor audit phase3/tabm` (listing) | rc 0, final line `NOT_RUN: 1`; the scientific verdict is unchanged (`FAIL: 2, INCONCLUSIVE: 5, NOT_APPLICABLE: 14, NOT_RUN: 1, PASS: 10`, 32 findings) |
| `paper-doctor audit` (no path) | rc 2 — `error: the following arguments are required: path` |
| `paper-doctor audit phase3/tabm/nope` | rc 2 — `P_UNRESOLVED_REF at …: no readable manifest is present at this path` |

Scientific output matches the pre-release frozen acceptance exactly. That is the **seventh**
independent route reproducing the same 17,511 bytes: source checkout, wheel install, sdist
install, clean checkout + fresh venv + real corpus fetch, two third-party agent onboarding runs,
the onboarding kit audited outside the repository, and now a PyPI-installed package.

## 5. Gates re-measured on the tagged commit

Run again after the tag, with `HEAD` = the tagged commit and a clean tree:

- `python -m pytest -q` → **298 passed in 11.98 s**
- `python -m ruff check .` → **All checks passed!**
- `python -m ruff format --check .` → **33 files already formatted**
- `python -m mypy` → **Success: no issues found in 10 source files**
- CI on `2a026986`: `gates` matrix green on all four jobs — `ubuntu-latest 3.11`, `ubuntu-latest
  3.13`, `windows-latest 3.11`, `windows-latest 3.13`; each job includes the
  "Frozen TabM acceptance digest" assertion. Run `36554832344`.
- Credential/privacy scan on the pushed tree: 106 files, worktree-vs-blob drift 0, 0 credential
  shapes, 0 account-name hits, 0 hits for the withheld submission title.

## 6. Human onboarding — status

Phase 3 §15 required a real first-use test by a person not involved in Phases 0–3. It was
**waived by the project owner** for this release and is recorded as **NOT OBSERVED**. It is not a
pass, it is not partial credit, and no sentence in this release may read as though a human run
occurred. Two fresh-agent runs and the outside-repository kit audit exist; they measure
self-sufficiency, not human usability. See `release/HUMAN_ONBOARDING_RECORD.md` §7 and
`phase3/ONBOARDING_MEASUREMENT.md`.

## 7. Defect ledger at the tag

- **P0 = 0.**
- **P1 = 0 open.** Ten P1 defects (P1-1 … P1-10) were found and fixed inside Phase 3, before the
  tag. P1-10 was invisible on this machine and was caught only by the Python 3.11 CI leg.
  Details: `release/RC_AUDIT.md` §7.
- **Known P2/P3 (accepted, not swept):** N1 `--dump-floats` (P3), N2 coverage footer (P2),
  N3 dedicated code for a missing paper root (P2), N4 `validate`/`init` subcommands (P2),
  N5 audited-manifest-digest header in the JSON (P2), N6 the test suite inside an unpacked sdist
  reports 205 passed / 23 failed / 70 errors because acceptance inputs are deliberately not
  vendored (P2, documented in the README), N7 64 drive-rooted paths in the design and evidence
  documents (P2), N8 `python -m paper_doctor.cli` is a silent no-op (P2), N9 `NOT_APPLICABLE`
  does not split "correctly absent" from "you forgot to declare it" (P3), N10 mypy scoped to
  `src/` (P3).

## 8. Immutability

`v0.1.0` points at `2a02698637f35bd3fec28d98a8b6e272b8e1fc9a` and **never moves**. No re-tag, no
force push, no history rewrite; the PyPI `0.1.0` files are immutable because PyPI refuses
re-upload of the same filename+version. The only commit that follows this record is the single
docs-only post-release commit §25 prescribes; it changes documentation on `main` and leaves the
tagged commit untouched.
