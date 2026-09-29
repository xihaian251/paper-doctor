# Paper Doctor 0.1.0 — release-candidate audit (Phase 3 §20)

Measured 2026-09-29 on the tree that becomes the release commit. Every number below was produced by
running the named command in this repository; nothing here is recalled from an earlier run, and where a
gate was measured earlier and re-measured here, the later number is the one printed.

Verdict line: **P0 = 0, P1 = 0, all four quality gates green, both distribution artifacts install clean
and reproduce the frozen TabM acceptance digest.** One §15 gate is **not met** and is disclosed as a
deviation in the last section rather than passed silently. The release therefore stops at the
push/publish boundary, which is the first irreversible external write.

---

## 1. The four quality gates

| Gate | Command | Measured result |
| --- | --- | --- |
| Tests | `python -m pytest -q` | **298 passed** in 17.17 s, 0 failed, 0 skipped, 0 errors |
| Lint | `python -m ruff check .` | All checks passed! |
| Format | `python -m ruff format --check .` | **33 files already formatted**, 0 to reformat |
| Types | `python -m mypy src` | Success: no issues found in **10 source files** |

The format gate is quoted over `.` and gives the same 33-file count a scoped command gave earlier,
because Markdown is now excluded from the formatter (§7, defect P1-9); the 33rd file is the fetch-script
regression suite added with P1-10. The identical four gates run against a clean checkout of the same tree
in §9, and CI re-runs them on push.

Scope note, stated because it is a real limit and not a detail: mypy runs over `src/` only. `tests/`,
`scripts/` and `examples/` are linted and formatted but not type-checked, and this was not upgraded into
a release-blocking item mid-freeze.

The 298 includes every frozen anchor required by the phase brief's §7 (a different numbering from this
file's sections) — GMMVI `C1` PD006 FAIL, `C5` PD002 INCONCLUSIVE, `C6`
PD005 FAIL; RTDL `D1` PD003 INCONCLUSIVE, `D5` clause-1 FAIL with clause-2 INCONCLUSIVE, `D6` PD004 FAIL,
`D7` PD001/PD006 PASS with PD002 INCONCLUSIVE, `D8` INCONCLUSIVE, `D11` PD007 FAIL; the Phase 2 Table 4
and Table 8 block oracles; `MULTI_TABLE_PAPER`; and the closed-at-twelve assertion on the `P_*` code
set. A green suite is therefore also the statement that Phase 3 did not move an anchor.

## 2. Distribution artifacts

Built with `python -m build` after the final README edit, from a clean `rm -rf build dist *.egg-info`:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| `dist/paper_doctor-0.1.0-py3-none-any.whl` | 67,802 B | `6e051f33318518c701318cf49d5c2055449d06ad4c035a4fa490ba339264deb0` |
| `dist/paper_doctor-0.1.0.tar.gz` | 183,797 B | `3432437a7867f347a2c07fa8f386ba369ee56869f86623906c329c7f09acac9a` |

`twine check` on both: PASSED.

Four earlier generations are superseded, and each supersession is a real change to shipped bytes rather
than a re-stamp:

| Generation (wheel / sdist) | Superseded by |
| --- | --- |
| `5c36af8a…` / `d249621a…` | a README paragraph |
| `b03d7276…` / `71539fa9…` | the README's re-measured sdist numbers plus the `pyproject.toml` formatter exclusion |
| `192e3e17…` / `bfd3a87f…` | the release-document commits (see below — content-identical, container-only change) |
| `2fb375a6…` / `3c20fc8b…` | the README's test-count paragraph, which is embedded in `METADATA`, so this one moved the wheel too |

Nothing in `src/` moved in any of the four rebuilds. Anyone verifying against a superseded digest is
verifying a stale file; §24 anticipates this by requiring the *downloaded* PyPI hashes to be recorded
rather than assumed equal to any local build.

**Each rebuild was compared member by member, not by archive hash.** `build` stamps tar and zip entries
with file mtimes, so two builds of one content set hash differently while their members are identical; the
comparison that means something is per-member with newline normalisation, which is also the comparison the
cross-platform case in §24 needs. Measured:

- The two release-document commits (`release/`, `phase3/` only, not in `MANIFEST.in`): wheel 16 members and
  sdist 50 members, 0 added, 0 removed, 0 differing. That is the proof those directories are not package
  content, checked against bytes rather than against a config file.
- The P1-10 fix plus the README count edit: **wheel members unchanged at 16, none differing** (the wheel
  carries only `paper_doctor/` and `dist-info`; it moved solely because `METADATA` embeds the README);
  **sdist 50 → 51 members**, added `tests/test_acceptance_input_fetcher.py`, differing exactly
  `scripts/fetch_acceptance_inputs.py` and setuptools' own `src/paper_doctor.egg-info/SOURCES.txt`.
  A three-item blast radius for a two-file change, listed in full rather than summarised.

Contents, measured from the archives:

- Wheel: 16 members. `paper_doctor/` 10 modules + `dist-info` with `licenses/LICENSE`, `METADATA`,
  `WHEEL`, `entry_points.txt`, `top_level.txt`, `RECORD`. `entry_points.txt` is exactly
  `paper-doctor = paper_doctor.cli:main`. No `examples/`, no `tests/`, no `phase*/`.
- Sdist: 51 files — `src/`, `tests/` (including all four `tests/fixtures/` files, the vendored pilot
  transcript among them), `examples/quickstart/`, `scripts/`, `README.md`, `LICENSE`, `MANIFEST.in`,
  `pyproject.toml`, `setup.cfg`, and setuptools' own `src/paper_doctor.egg-info/`. No `phase*/` entry: the
  phase reports and the TabM workspace are repository evidence, not package content.
- `METADATA`: `Metadata-Version: 2.4`, `Name: paper-doctor`, `Version: 0.1.0`,
  `Summary: Deterministic claim-to-evidence audits of reported results in an ML paper`,
  `License-Expression: Apache-2.0`, `License-File: LICENSE`, `Requires-Python: >=3.11`, `Provides-Extra: dev`,
  `Requires-Dist: PyYAML>=6`, long description 23,362 bytes, which equals `README.md` (22,935 B) byte for
  byte after newline normalisation — checked by comparison, not by eyeball. Current: it carries the
  `205 passed, 23 failed, 70 errors` sdist-suite line and its `199 passed` and `196 passed` predecessors are
  both gone, verified by string search of the wheel.
- Version has one source: `paper_doctor.__version__`, which `pyproject.toml` reads through
  `dynamic = ["version"]` / `version = {attr = ...}`. `paper-doctor --version` from a fresh wheel install
  printed `paper-doctor 0.1.0`.
- `egg-info/SOURCES.txt` was inspected for path leaks: relative paths only.


## 3. Fresh-install verification (§19: "no editable-install-only success is sufficient")

Two new virtualenvs under `.check/` (git-ignored scratch), created with `python -m venv .check/v-wheel` and
`python -m venv .check/v-sdist` from the system interpreter and installed with plain
`pip install <artifact>`:

| Step | From wheel | From sdist |
| --- | --- | --- |
| install | ok | ok |
| `pip check` | `No broken requirements found.` | `No broken requirements found.` |
| `paper-doctor --version` | `paper-doctor 0.1.0` | `paper-doctor 0.1.0` |
| `paper-doctor --help` | usage line + the audit subcommand, exit 0 | same |
| `paper-doctor audit phase3/tabm` | exit 0, tally `PASS: 10 FAIL: 2 INCONCLUSIVE: 5 NOT_APPLICABLE: 14 NOT_RUN: 1` over 32 findings | same |
| `paper-doctor audit phase3/tabm --json out.json` | `08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0` | byte-identical, same digest |

**A third route, with no project files at all.** The table above runs the installed package against this
repository's `phase3/tabm` workspace, so it still leans on the checkout for its inputs. The stronger form of
§19 is to install from an artifact and audit a workspace that came from nothing but the artifact. The
onboarding kit is exactly that (`release/onboarding-kit/`: wheel, sdist, `phase3/tabm/paper-doctor.yml`,
`phase3/tabm/findings.json`, `README.md`, the fetch script, and no `src/`). Copied to a directory
**outside the repository** (`F:\MLResearch\kitdry2`, no `.git`, no project source anywhere in it), `sha256sum
-c KIT_MANIFEST.txt` → 8/8 OK, then in a third fresh venv installing only `dist/*.whl`:

```text
python scripts/fetch_acceptance_inputs.py tabm
  DOWNLOADED tabm: F:\MLResearch\kitdry2\phase3\acceptance-inputs\tabm-arxiv\src   (rc 0)
paper-doctor audit phase3/tabm --json out.json
  rc 0, tally PASS: 10 FAIL: 2 INCONCLUSIVE: 5 NOT_APPLICABLE: 14 NOT_RUN: 1
  08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0  (17,511 bytes)
```

Same bytes out of a tree that never contained the source. This is also the route a reviewer can repeat
without cloning the repository.

`08836ccf…` is the digest the TabM acceptance asserts, and it is the same digest produced from the source
checkout, from the wheel, from the sdist, by both onboarding measurement runs, by the onboarding kit's
self-contained dry run, and by a clean checkout of the tree (§9). Six independent routes, one byte string.
The artifact rebuilds in §2 moved the *archive* hashes and did not move this one, which is the distinction
that matters: the scientific output is stable across the documentation churn.

## 4. Credential and privacy scan

Two layers, because they answer different questions.

**4a. The committed gate** — `tests/test_phase3_firewalls.py` scans the *shipped* surface (`README.md`,
`CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `MANIFEST.in`, and everything under `src/`, `tests/`,
`scripts/`, `examples/`) for local filesystem shapes and credential shapes, and asserts that its own
patterns still detect a synthetic leak. It passed inside the 298.

**4b. The pre-publication scan of the whole tracked surface**, run against exactly what `git` would
publish (`git ls-files`), from `.check/pubscan.py` (scratch, not tracked):

```text
files=106                 (106 tracked files at this scan: this file, the Phase 3 report, the two workflow
                           files, and tests/test_acceptance_input_fetcher.py, the P1-10 regression suite)
blob_vs_worktree_drift=0  credential_shapes=0  account_name=0  withheld_paper_name=0
binary_files=0            local_paths=65  ->  phase0 25, phase1 2, phase2 1, phase3 32, release 4, tests 1
largest tracked file: tests/fixtures/rd_findings_gmmvi_0.1.0.json, 584,900 B
```

The tree's total byte count is deliberately not quoted here: this file is part of what it would measure,
so the number moves every time the report is edited. The scan prints it; the invariants above do not.

Reading of each line:

- **106 tracked files, no vendored corpus.** A clone is cheap; the paper sources a reviewer needs are
  fetched from pinned digests rather than committed. The one third-party text file that *is* committed is
  the pilot transcript in §4c, vendored because frozen anchors quote it by line number, and it is committed
  under a digest pin rather than under an editing licence.
- **blob/worktree drift = 0.** Every staged blob hashes the same as the file on disk. This is not a
  nicety: without `.gitattributes` (`* -text`) git's EOL conversion rewrites LF to CRLF on Windows
  checkouts, and then the bytes the pinned digests were taken over are not the bytes a reviewer gets,
  while `git status` still looks clean. The `.gitattributes` file exists to prevent exactly that, and
  this line is its proof.
- **0 credential shapes** across the entire published surface — GitHub token patterns, AWS key ids, PEM
  private-key headers, the GitHub Actions token username in a remote URL, bearer tokens, `password =`
  assignments, and personal email addresses. (This paragraph first spelled one of those patterns out in
  full and was rewritten after the scan flagged its own file; the scanner detecting the report is the
  scanner working.)
- **0 occurrences of the machine account name.** The 65 path-shaped lines split as 64 drive-rooted workspace
  paths of the form `<drive>:/<project>/…` — 60 of them inside the phase design and evidence documents, 4 of
  them added to `release/` by the §3/§9 re-measurements, which name the scratch directories the verification
  actually ran in — plus one line of somebody else's documentation in the vendored transcript of §4c. None
  carries a username. None appears in `src/`, `scripts/`, `examples/` or `README.md`; the single hit under
  `tests/` is exactly the file the shipped-surface gate in 4a skips by digest, which is the reason that skip
  is digest-conditional rather than a path whitelist. The 60 in the phase documents are provenance a reviewer
  needs (which RD snapshot, which captured run, which dataset tree). Accepted as a P2, listed as N7 in §8.
- **0 binary files.**
- **The withheld paper's title appears nowhere in the published tree** — see §5.

Mutation evidence for 4a, from the same session (harness kept in scratch): a drive-rooted path planted in
`tests/fixtures/RD_SNAPSHOTS.md`, an account name planted in `README.md`, a contiguous `ghp_…` token
planted in `scripts/fetch_acceptance_inputs.py`, and a PEM header planted in the same script — four
mutations, **all four killed**; the restored baseline **survived**; every mutated file was restored
byte-identically (verified by digest, using binary reads and writes so Windows could not rewrite endings
 underneath). The same gate caught two real, self-inflicted leaks while it was being written: an upstream
project path inside `tests/fixtures/RD_SNAPSHOTS.md` (that file ships in the sdist), and a path in a
comment I had just typed into the gate itself. Both were reworded, not whitelisted.

**4c. The gate has exactly one skip, and the skip cannot be widened by editing.** `tests/fixtures/` gained
a vendored third-party file (`rtdl_pilot_README.md`, the RTDL pilot transcript the frozen RTDL anchors quote
by line number; see §9 and `tests/fixtures/RD_SNAPSHOTS.md`). Its upstream prose contains a commented
example `PROJECT_DIR` assignment pointing at a checkout under a POSIX home directory, which is precisely the
shape the privacy gate reports, so a
naive scan of the shipped surface fails on somebody else's documentation, and scrubbing that documentation
would destroy the evidence the anchors depend on. The resolution is not a whitelist of paths: the gate skips
that one file **only while its sha256 equals the pinned digest of the bytes the anchors were read from**.
Two tests hold it open: `test_vendored_third_party_bytes_are_still_what_they_were_pinned_as` and
`test_the_vendored_skip_is_narrow_and_widens_to_nothing_else` (the pin table has exactly one entry, and the
entry's key is that one file).

This is not theoretical. When the fixture was silently rewritten during this session, the digest stopped
matching, the skip stopped applying, and the privacy gate reported the upstream example path itself — a
would-be exemption turning into a failure the moment somebody changed the evidence. That is the behaviour
the design was for; the cause of the rewrite is defect P1-9 in §7.


## 5. Public-surface policy

What the repository excludes, and why each exclusion is a decision rather than an oversight
(`.gitignore` carries the same reasoning next to each entry):

| Excluded | Why |
| --- | --- |
| `phase0/sources/`, `phase3/acceptance-inputs/` | Somebody else's paper bytes, rebuildable from pinned digests by `scripts/fetch_acceptance_inputs.py`. Vendoring them would ship a third-party e-print inside our release. |
| `phase3/tabm/dd/fingerprint.json` (13,013,232 B) | Regenerable bulk evidence: 48,842 per-row hashes of a public dataset. Pinned by digest in `phase3/tabm/end_to_end_chain.json` **and** `phase3/tabm/dd/README.md`, which records the command. That command was re-run during this audit and reproduced the pinned digest and byte count exactly. |
| `phase3/.ed-workdir/` | The 174 MB upstream clone Experiment Doctor captured provenance from. The capture in `phase3/tabm/ed-captured/` is the evidence. |
| `release/onboarding-kit/` | Stages the wheel and sdist; regenerated by `scripts/build_onboarding_kit.py`. |
| `phase3/PHASE3_BRIEF.md` | The user's instructions, kept verbatim. Not published, because verbatim fidelity and withholding one unpublished submission title are incompatible; the brief's substance is reproduced throughout the Phase 3 report and this file with that one name withheld. |
| `dist/`, `build/`, `*.egg-info/`, caches, virtualenvs, `**/.dl/` | Build products. |

**The one redaction made before the first commit.** `phase2/PAPER_DOCTOR_PHASE2_REPORT.md` §18 stated the
exclusion rule using the actual title of one of the author's own unpublished submissions. The section now
reads `EXCLUDED PAPER = EXCLUDED FROM PAPER DOCTOR VALIDATION` and explains that the frozen thing is the
rule, not the name. Nothing else changed in that report: the rule's scope (design, implementation,
validation, acceptance, benchmarking, release gating), its permanence, and the requirement that final
acceptance use an external third-party paper are all still stated. The title is known to the author and
recorded outside this repository. The scan in §4b confirms it appears in no published file, including the
wheel, the sdist and this audit.

**A second, quieter leak closed the same way:** `tests/fixtures/RD_SNAPSHOTS.md` line 9 used to carry an
absolute path into another project's phase archive. It now names the provenance in words
("Experiment Doctor's GMMVI phase 0 archive") without a filesystem location, since that file ships.

## 6. README and metadata claims audit (§17)

Checked against the text, not against intention:

- The README states what the tool audits and what it does **not** judge: whole-paper truth, fraud or
  misconduct, novelty, accept/reject, theorem or proof correctness, whether a result reproduces, and
  meaning in prose. Present, in a section titled "What this is not".
- `FAIL` is documented as a disagreement between a declared sentence and the address it points at, never
  as "the paper is false" or "unreliable". Present, including the sentence that a FAIL does not localize
  which side is wrong.
- `PD006` is described as the literal-presence test it is, including the case that started this: a table
  that enumerates eight rows without printing the string `8` FAILs `PD006`, and that FAIL does not mean
  the count is wrong. Counting rows and summing columns are stated as outside the audited universe.
- No aggregate score, no confidence number, no verdict about the paper. The README says so and the code
  has no such output path; `--json` emits findings, and the only tally is a status count.
- Exit codes: 0 = contract satisfied (findings may include scientific FAILs), 2 = input contract error,
  1 = tool failure. Verified in this session by the acceptance run (0 with two FAILs), by the missing-root
  probe (2), and by the fixed `--json` parent-directory case, which used to raise a traceback and now
  exits 2 with a one-line message.
- The missing-paper-root message quoted in the README is the measured message shape, not a paraphrase.

## 7. Blocking register

**P0 = 0. P1 = 0** — at the moment of the release decision, after the ten P1 defects below were found and
fixed. The count is a statement about the boundary, not about the process: ten items were open at some point.

Seven P1 usability defects were found by the two measured onboarding runs and all seven were fixed inside
Phase 3; the before/after numbers, the fix for each, and the test that pins each fix are in
`phase3/ONBOARDING_MEASUREMENT.md` §2 (P1-1 … P1-7, plus the residual P2-8). The headline measurement:
time from install to the first successful TabM audit went from ~5 minutes (run 1, with a traceback) to
**65 s** (run 2, no traceback), and the guessed steps from 8 to 2.

Three further P1s were found after the onboarding runs, by mechanisms onboarding cannot see — one by running
the suite somewhere that is not this workspace, one by checking a digest, one by running CI on the lowest
Python the project claims to support:

| # | Defect | How it was caught | Fix | Pinned by |
| --- | --- | --- | --- | --- |
| P1-8 | `tests/test_acceptance_rtdl.py` resolved the paper corpus **and** the pilot transcript against `REPO.parent`, i.e. a sibling checkout outside the repository. In a clean checkout 17 frozen RTDL anchors errored (`FileNotFoundError: read-only corpus fixture missing: …\phase0\sources\2106.11959.tex\main.tex`). Locally green, permanently red for every other user and for CI. | four gates run against a clean checkout (§9) | paths made repository-relative; the transcript vendored as a byte-pinned fixture; the corpus left to the fetch script, which was run in the checkout | `test_every_input_this_test_reads_is_inside_the_repository` (containment + existence) and `test_the_pilot_transcript_is_the_bytes_the_anchors_were_read_from` |
| P1-9 | The project's own formatter rewrites Python fenced blocks inside Markdown. `ruff format .` silently changed a vendored third-party fixture from `50f7994f…` (13,162 B) to `799726d9…` (13,149 B) between two commands: single quotes became double quotes and a wrapped comprehension was joined. Same mechanism can edit any quoted transcript or evidence report in this repository. | the digest pin test failed, and the privacy gate reported the fixture's own upstream example path because the skip is digest-conditional (§4c) | `**/*.md` added to `[tool.ruff] extend-exclude` with the reason recorded in `pyproject.toml`; verified by re-running `ruff format .` and re-hashing the fixture plus three other evidence documents | `test_the_pilot_transcript_is_the_bytes_the_anchors_were_read_from`; the firewalls' digest-conditional skip |

| P1-10 | `python scripts/fetch_acceptance_inputs.py` with **no corpus name** — the documented default form, and the exact command CI runs — died on Python 3.11 with `error: argument names: invalid choice: []` and exit 2. On 3.12+ the same command works. CPython below 3.12 validates the empty list that `nargs="*"` produces against the argument's `choices`, so the no-argument form was rejected by membership-testing nothing. Declared support floor is `>=3.11`, so every advertised installation path was broken on the floor version. | the first CI push: both `3.11` jobs failed at the corpus-fetch step with every later step skipped, both `3.13` jobs passed including the digest assertion (§11, run `36549615962`). Not detectable locally on this machine's 3.13 interpreter | `choices=` removed from the positional; the membership check moved after parsing into `_selected()`, where the message names the offending word instead of an empty list; refusal now exits 2 like the rest of the tool | `tests/test_acceptance_input_fetcher.py` (6 tests), incl. a subprocess `--list` run that asserts the no-argument form executes on the interpreter under test |

All ten were fixed before the first public commit rather than after it, and none touched Paper Doctor's
scientific design: no rule, status, code, schema key or asserted anchor status changed. P1-9 in particular
was **not** fixed by loosening the privacy gate, and P1-10 was **not** fixed by raising the support floor to
3.12 — the fix makes the declared floor true rather than making the claim smaller.

One correction belongs here rather than in §8: the earlier text of this file quoted the format gate as
`ruff format --check src tests scripts examples` because `.` was reporting a drifting file count. That
count was not scratch directories — it was Markdown files being counted and, in one case, rewritten. With
Markdown excluded the repo-wide command is the honest one. It reported 32 files at the RC boundary; the
P1-10 fix added a thirteenth test file and the count became 33, which §1 re-measures locally and §9
re-measures in a clean checkout.

## 8. Non-blocking register (recorded, deliberately not fixed)

| # | Item | Class | Why it stays open |
| --- | --- | --- | --- |
| N1 | `--dump-floats`: print the parser's own cell/block/label structure | P3 | Biggest remaining readability gap; new output surface, cannot be designed honestly during a freeze. First post-release candidate. |
| N2 | Coverage footer ("9 claims declared of an unstated N") | P2 | Changes the frozen listing format and the byte-pinned canonical JSON. |
| N3 | Its own `P_*` code for a missing paper root | P2 | The set is closed at twelve and asserted closed; the current message already names the field, the tried path and two remedies. |
| N4 | `validate` / `init` subcommands | P2 | New CLI surface in the release window; exit 2 already separates contract failure from findings. |
| N5 | Audited-manifest-digest header in the JSON | P2 | Output schema frozen. Prompted by a real observation (see `phase3/ONBOARDING_MEASUREMENT.md` §4) and recorded as a real gap. |
| N6 | Test suite inside an unpacked sdist: **205 passed, 23 failed, 70 errors** because the corpora and the `phase*/` workspaces are not vendored (re-measured on the artifact that will be published: current sdist unpacked into a fresh directory, run by a venv that installed only that sdist with `[dev]`; the superseded numbers were 196/22/70, then 199/23/70 — the three extra passes in between are the vendored transcript and its two pinning tests, the six after that are P1-10's) | P2 | Documented in the README's testing section with the measured numbers. It is *not* fixed by making those tests skip: a silently missing acceptance input is precisely what a release gate must not permit. |
| N7 | 64 drive-rooted workspace paths in the phase design/evidence documents and in §3/§9 of this file | P2 | Scrubbing them would cost provenance specificity and is the kind of P2 sweep the phase brief forbids; none carries a username or a credential. |
| N8 | `python -m paper_doctor.cli` exits 0 printing nothing (the module has no `__main__` guard) | P2 | The documented entry point is the `paper-doctor` console script; `python -m paper_doctor` fails loudly. No measured user hit this, so it was not allowed to reopen `src/` after the artifact scan. |
| N9 | `NOT_APPLICABLE` does not distinguish "correctly absent" from "you forgot to declare it" | P3 | Each reason line already says which relation was absent; a machine-readable split is a schema change. |
| N10 | mypy scoped to `src/` | P3 | Widening it mid-freeze would be a new gate, not a pass on an existing one. |

## 9. Clean-checkout verification

Everything above §9 was measured inside the workspace where the code was written, which is the weakest
place to test portability: a workspace contains sibling projects, cached corpora and scratch directories
that a reviewer's clone will not. This section runs the same gates outside it.

**Procedure, and then the same thing done twice.** First as a content test: the staged tree was
materialised into an empty directory with `git checkout-index -a -f --prefix=.check/clone-tree/`, so that
directory contained exactly the tracked paths and nothing else — no `.git`, no `dist/`, no `.check/`, no
corpus, no `phase0/sources/`, no `phase3/acceptance-inputs/`. Then, after that tree was committed, as a
real clone: `git clone --no-local file:///…` of commit `7bdf47f`, which is 104 files. Both got a fresh
virtualenv from the system interpreter, `pip install -e ".[dev]"`, `python scripts/fetch_acceptance_inputs.py`,
the four gates, and the console script. Both produced the same numbers:

```text
fetch    DOWNLOADED gmmvi / rtdl / tabm            (three pinned digests verified, no cache reuse)
tests    292 passed in 13.22 s, 0 failed, 0 errors
lint     All checks passed!
format   32 files already formatted
types    Success: no issues found in 10 source files
audit    paper-doctor audit phase3/tabm --json -> exit 0
         08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0  (17,511 bytes)
```

**Re-run after the P1-10 fix, on the tree this section ends up describing.** The fetch script changed and a
thirteenth test file was added, so the whole procedure was repeated against a clean tree materialised the
same way (`git checkout-index` of the staged index; the fetched corpora carried over, nothing else did), with
the same venv. Every number moved except the two that must not:

```text
tests    298 passed in 15.36 s, 0 failed, 0 errors
lint     All checks passed!
format   33 files already formatted
types    Success: no issues found in 10 source files
audit    paper-doctor audit phase3/tabm --json -> exit 0
         08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0  (17,511 bytes)
```

The six extra passes are the six tests that pin P1-10; the one extra format file is the same test module.
The audit digest and its byte length are unchanged, which is the required result: a release-blocking
usability fix in a fetch script must not move the scientific output.

Two further clone measurements are worth stating because they are the ones a reviewer can repeat by mistake
or on purpose:

- **Clone before the fetch:** 204 passed, 18 failed, 70 errors at the RC boundary; **210 passed, 18 failed,
  70 errors** after the P1-10 fix, measured on the clean tree above. Nothing skips in either case. The suite
  refuses to be green without its inputs, which is the behaviour N6 and the README both document. The delta
  is exactly the six new P1-10 tests (204 + 6 = 210); the failure and error counts did not move.
- **Digest survival across a real clone.** `tests/fixtures/rtdl_pilot_README.md` came out at 13,162 bytes /
  `50f7994f…` (it is a CRLF file, and `.gitattributes` `* -text` is what kept it byte-identical),
  `rd_findings_rtdl_0.1.0.json` at 13,395 / `2ad02c8f…`, and `phase3/tabm/paper-doctor.yml` at
  7,391 / `7e809014…`. Every pin named in the published documents is the byte string a clone actually
  yields.

The same procedure run against the previous commit's tree (`976bf0d`, extracted with `git archive` into an
empty directory, corpora fetched) gave **271 passed, 17 errors**, every error in
`tests/test_acceptance_rtdl.py` and every one naming a path under
`.check\paper-doctor\phase0\sources\…`. The pre-fix constants resolved the corpus against `REPO.parent`
(`paper-doctor/phase0/sources/…`) and read the pilot transcript straight out of the sibling
`result-doctor/phase4/…` directory. Both worked here, because this repository sits in a workspace directory
beside those two trees; neither path exists inside a clone. The 271 + 17 lands on exactly the 288 this
workspace reported, which is the point: the anchors were genuinely passing locally, and would have been red
for every reviewer and for CI.

Two honest limits on this section are folded into the CI account below.

**The GitHub Actions run, observed.** `.github/workflows/gates.yml` encodes exactly the commands above across
ubuntu/windows × Python 3.11/3.13 and additionally fails if the audit JSON's sha256 is not `08836ccf…`. The
first push (commit `d954e22`, run `36549615962`, 2026-09-29T09:30:29Z) came back **red**, and it was red for a
reason no local measurement could have produced:

| Job | Result | Where |
| --- | --- | --- |
| `gates (ubuntu-latest, 3.13)` | success | every step, through the frozen-digest assertion |
| `gates (windows-latest, 3.13)` | success | every step, through the frozen-digest assertion |
| `gates (ubuntu-latest, 3.11)` | **failure** | step "Fetch and verify the pinned paper corpora"; Ruff/Mypy/Test/digest skipped |
| `gates (windows-latest, 3.11)` | **failure** | same step, same four skips |

```text
fetch-acceptance-inputs: error: argument names: invalid choice: [] (choose from 'gmmvi', 'rtdl', 'tabm')
##[error]Process completed with exit code 2.
```

This machine runs Python 3.13, so P1-10 (§7) was unobservable here at any depth of local testing; the
matrix being on 3.11 is what turned it from a latent support-floor claim into a failed step. It failed at
the fetch, before a single test ran, which is why the four local gates stayed green right up to the push.
The fix is in §7 and is pinned by `tests/test_acceptance_input_fetcher.py`. **CI is therefore part of the
evidence for this release rather than a badge claimed in advance.**

**Run `36553848745`, commit `095c020`, 2026-09-29T10:09:57Z: green on all four jobs.**

| Job | Fetch corpora | Ruff | Mypy | Test suite | Frozen digest |
| --- | --- | --- | --- | --- | --- |
| `gates (ubuntu-latest, 3.11)` | success | success | success | success | **success** |
| `gates (windows-latest, 3.11)` | success | success | success | success | **success** |
| `gates (ubuntu-latest, 3.13)` | success | success | success | success | **success** |
| `gates (windows-latest, 3.13)` | success | success | success | success | **success** |

This is the measurement the local machine cannot make, twice over: it runs on the support-floor interpreter,
and the two ubuntu jobs assert the same `08836ccf…` from a checkout that never passed through Windows EOL
handling. One workflow, four OS/Python combinations, one byte string — which is the cross-platform half of
§24 obtained before the release rather than assumed by it.

One limit survives this section: the checkout venv carried newer tools than CI's (`ruff 0.16.9` vs `0.16.3`,
`mypy 2.3.1`, `pytest 9.1.1`). The format count is identical across both because the Markdown exclusion is in
`pyproject.toml`, not because a particular ruff version happens to leave the fixture alone. And
`fetch_acceptance_inputs.py` needs the network, so the clone test was run with it; Paper Doctor itself made
no network calls during the audit, which is what the tool-side firewall asserts.

## 10. Gate deviations — stated plainly

**§15 (one real human first-use test) is NOT OBSERVED, and cannot be observed from inside this
environment.** The requirement is met in every part except the part that requires a person:

- The kit exists, is reproducible, contains no answer and no expected output, and is integrity-verified:
  `release/onboarding-kit/` with `KIT_MANIFEST.txt`, 309,142 bytes, purity check clean, built from the
  artifacts in §2 above.
- Two fresh-agent measurements were run and recorded (`release/onboarding/RUN1_AGENT_LOG.md`,
  `RUN2_AGENT_LOG.md`) and they produced the fixes in §7. Those are **agent** runs. They demonstrate the
  kit is walkable; they do not demonstrate a human can walk it, and they are not offered as §15 evidence.
- What is missing is a tester who did not participate in Paper Doctor Phases 0–3, on a machine that is not
  this one, uncoached, filling in `RECORDING_SHEET.md`. That is 30–45 minutes of a stranger's time plus one
  2.2 MB download. `release/HUMAN_ONBOARDING_RECORD.md` lists all thirteen §15 quantities as `UNKNOWN` and
  names the procedure that would fill them.

Per §23 this is a release condition ("human onboarding complete"), and per §20 a gate that is not met is
either P0/P1 or a disclosed deviation. It is disclosed, and it was raised for a decision that belongs to the
user: nominate a human tester, or waive §15 for 0.1.0.

**Decision, 2026-09-29: the owner waived §15 and directed the release to proceed.** That is recorded in full
in `release/HUMAN_ONBOARDING_RECORD.md` §7. It changes the release's *authority*, not its *evidence*: the
thirteen §15 quantities remain `UNKNOWN`, the two agent runs remain agent runs, and nothing in the tag, the
GitHub Release notes, the PyPI metadata, this file or `release/RELEASE_FREEZE.md` may state or imply that a
human first-use test was performed. §15 stays open for the 0.1.x line, and the person who granted the waiver
cannot close it (they authored the Phase 0–3 briefs).

Two further deviations, smaller:

- **The §14/§15 kit was dry-run by an agent**, not by a person, before being handed over. The dry run
  checked the layout is load-bearing (the manifest resolves `root` against the manifest, so the kit's
  directory shape must match) and that the fetch script materialises the missing corpus. It verified the
  kit is *self-consistent*, not that it is *usable*.
- **`.check/` is scratch and is not committed**, so the fresh-install evidence in §3 is reproducible only
  by re-running the commands, not by checking out a script. It is recorded here as commands and outputs,
  which is what §19 asks for.

## 11. Release decision

What was green before the one unmet condition was raised:

Everything the machine can check is green and everything the freeze allows to be pinned is pinned:
298 tests, four gates reproduced in a clean checkout of the tree, two artifacts, two fresh installs, one
byte-identical acceptance digest across six routes, zero credential shapes, zero blob/worktree drift, zero
published mention of the withheld submission, P0 = 0, P1 = 0 (ten P1s found and fixed inside Phase 3, the
tenth of them only because CI ran on the declared support floor).

The first push to the public repository was **red** on both Python 3.11 jobs (§9). This record does not
round that off: run `36549615962` on `d954e22` failed, P1-10 was fixed, and run `36553848745` on the fix
commit `095c020` is green on all four jobs including the frozen-digest assertion on both operating systems.
§27 lists CI failure as a stop condition; it was hit, honoured, and cleared. `v0.1.0` is cut only at or after
`095c020`, the first commit whose four-job matrix is green, and its exact SHA is recorded in
`release/RELEASE_FREEZE.md`.

The release was held at the RC boundary — committed locally, untagged, unpushed, unpublished — and the choice
was put to the owner, because the next two actions (a public repository and a permanent name on PyPI) cannot
be undone by us alone and §23's sixth condition was not satisfied. **The owner waived §15 and directed the
release to proceed on 2026-09-29.** With that authority granted, the remaining §21–§25 steps are executed in
order and their outcomes, including every digest that only PyPI can produce, are recorded in
`release/RELEASE_FREEZE.md`. The §15 evidence state is unchanged by the waiver and is restated there as
NOT OBSERVED.
