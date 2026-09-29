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
| Tests | `python -m pytest -q` | **288 passed** in 10.98 s, 0 failed, 0 skipped, 0 errors |
| Lint | `python -m ruff check .` | All checks passed! |
| Format | `python -m ruff format --check src tests scripts examples` | **32 files already formatted**, 0 to reformat |
| Types | `python -m mypy src` | Success: no issues found in **10 source files** |

The format gate is quoted over the four tracked Python trees rather than `.`: `.` also walks scratch
directories that exist during development but never enter the repository, so its file count is not a
reproducible number. The clean-clone measurement CI will report is in §9.

Scope note, stated because it is a real limit and not a detail: mypy runs over `src/` only. `tests/`,
`scripts/` and `examples/` are linted and formatted but not type-checked, and this was not upgraded into
a release-blocking item mid-freeze.

The 288 includes every frozen anchor from §7 — GMMVI `C1` PD006 FAIL, `C5` PD002 INCONCLUSIVE, `C6`
PD005 FAIL; RTDL `D1` PD003 INCONCLUSIVE, `D5` clause-1 FAIL with clause-2 INCONCLUSIVE, `D6` PD004 FAIL,
`D7` PD001/PD006 PASS with PD002 INCONCLUSIVE, `D8` INCONCLUSIVE, `D11` PD007 FAIL; the Phase 2 Table 4
and Table 8 block oracles; `MULTI_TABLE_PAPER`; and the closed-at-twelve assertion on the `P_*` code
set. A green suite is therefore also the statement that Phase 3 did not move an anchor.

## 2. Distribution artifacts

Built with `python -m build` after the final README edit, from a clean `rm -rf build dist *.egg-info`:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| `dist/paper_doctor-0.1.0-py3-none-any.whl` | 67,770 B | `b03d72766ee3788833b74b58f18b6198d6885c4329b34a03b0338f0efeb5a676` |
| `dist/paper_doctor-0.1.0.tar.gz` | 174,897 B | `71539fa903f59c23cd97500581c9329712766419f3f4d5d5c0775ecc7fccfbee` |

An earlier generation of both artifacts (before the last README paragraph) hashed to `5c36af8a…` and
`d249621a…`. They are superseded; anyone verifying against those digests is verifying a stale file. This
matters concretely: the README is embedded in `METADATA`, so a documentation edit changes the artifact
hashes even though no code changed. §24 anticipates this by requiring the *downloaded* PyPI hashes to be
recorded rather than assumed equal to any local build.

Contents, measured from the archives:

- Wheel: 16 members. `paper_doctor/` 10 modules + `dist-info` with `licenses/LICENSE`, `METADATA`,
  `WHEEL`, `entry_points.txt`, `top_level.txt`, `RECORD`. `entry_points.txt` is exactly
  `paper-doctor = paper_doctor.cli:main`. No `examples/`, no `tests/`, no `phase*/`.
- Sdist: 58 members — `src/`, `tests/` (including `tests/fixtures/`), `examples/quickstart/`,
  `scripts/`, `README.md`, `LICENSE`, `MANIFEST.in`, `pyproject.toml`, `setup.cfg`, and setuptools' own
  `src/paper_doctor.egg-info/`. No `phase*/` directory: the phase reports and the TabM workspace are
  repository evidence, not package content.
- `METADATA`: `Metadata-Version: 2.4`, `Name: paper-doctor`, `Version: 0.1.0`,
  `Summary: Deterministic claim-to-evidence audits of reported results in an ML paper`,
  `License-Expression: Apache-2.0`, `License-File: LICENSE`, `Requires-Python: >=3.11`, `Provides-Extra: dev`,
  `Requires-Dist: PyYAML>=6`, long description 23,712 bytes (the README, current).
- Version has one source: `paper_doctor.__version__`, which `pyproject.toml` reads through
  `dynamic = ["version"]` / `version = {attr = ...}`. `paper-doctor --version` from a fresh wheel install
  printed `paper-doctor 0.1.0`.
- `egg-info/SOURCES.txt` was inspected for path leaks: relative paths only.

## 3. Fresh-install verification (§19: "no editable-install-only success is sufficient")

Two new virtualenvs under `.check/` (git-ignored scratch), created with `python -m venv .check/wheel` and
`python -m venv .check/sdist` from the system interpreter and installed with plain
`pip install <artifact>`:

| Step | From wheel | From sdist |
| --- | --- | --- |
| install | ok | ok |
| `pip check` | `No broken requirements found.` | `No broken requirements found.` |
| `paper-doctor --version` | `paper-doctor 0.1.0` | `paper-doctor 0.1.0` |
| `paper-doctor --help` | usage line + the audit subcommand, exit 0 | same |
| `paper-doctor audit phase3/tabm` | exit 0, tally `PASS: 10 FAIL: 2 INCONCLUSIVE: 5 NOT_APPLICABLE: 14 NOT_RUN: 1` over 32 findings | same |
| `paper-doctor audit phase3/tabm --json out.json` | `08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0` | byte-identical, same digest |

`08836ccf…` is the digest the TabM acceptance asserts, and it is the same digest produced from the source
checkout, from the wheel, from the sdist, and by both onboarding measurement runs. Nothing in the release
window moved it.

## 4. Credential and privacy scan

Two layers, because they answer different questions.

**4a. The committed gate** — `tests/test_phase3_firewalls.py` scans the *shipped* surface (`README.md`,
`CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `MANIFEST.in`, and everything under `src/`, `tests/`,
`scripts/`, `examples/`) for local filesystem shapes and credential shapes, and asserts that its own
patterns still detect a synthetic leak. It passed inside the 288.

**4b. The pre-publication scan of the whole tracked surface**, run against exactly what `git` would
publish (`git ls-files`), from `.check/pubscan.py` (scratch, not tracked):

```text
files=103                 (103 tracked files at this scan, this one and the two workflow files included)
blob_vs_worktree_drift=0  credential_shapes=0  account_name=0  withheld_paper_name=0
binary_files=0            local_paths=60  ->  phase0 25, phase1 2, phase2 1, phase3 32
largest tracked file: tests/fixtures/rd_findings_gmmvi_0.1.0.json, 584,900 B
```

The tree's total byte count is deliberately not quoted here: this file is part of what it would measure,
so the number moves every time the report is edited. The scan prints it; the invariants above do not.

Reading of each line:

- **103 tracked files, no vendored corpus.** A clone is cheap; the paper sources a reviewer needs are
  fetched from pinned digests rather than committed.
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
- **0 occurrences of the machine account name.** The 60 local paths are all drive-rooted workspace paths
  of the form `<drive>:/<project>/…`; none carries a username, and none appears in `src/`, `tests/`,
  `scripts/`, `examples/` or `README.md` — which is what the shipped-surface gate in 4a asserts. They
  live only in the phase design and evidence documents, where they are part of the provenance a reviewer
  needs (which RD snapshot, which captured run, which dataset tree). Accepted as a P2, listed in §7.
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

**P0 = 0. P1 = 0.**

Seven P1 usability defects were found by the two measured onboarding runs and all seven were fixed inside
Phase 3; the before/after numbers, the fix for each, and the test that pins each fix are in
`phase3/ONBOARDING_MEASUREMENT.md` §2 (P1-1 … P1-7, plus the residual P2-8). The headline measurement:
time from install to the first successful TabM audit went from ~5 minutes (run 1, with a traceback) to
**65 s** (run 2, no traceback), and the guessed steps from 8 to 2.

## 8. Non-blocking register (recorded, deliberately not fixed)

| # | Item | Class | Why it stays open |
| --- | --- | --- | --- |
| N1 | `--dump-floats`: print the parser's own cell/block/label structure | P3 | Biggest remaining readability gap; new output surface, cannot be designed honestly during a freeze. First post-release candidate. |
| N2 | Coverage footer ("9 claims declared of an unstated N") | P2 | Changes the frozen listing format and the byte-pinned canonical JSON. |
| N3 | Its own `P_*` code for a missing paper root | P2 | The set is closed at twelve and asserted closed; the current message already names the field, the tried path and two remedies. |
| N4 | `validate` / `init` subcommands | P2 | New CLI surface in the release window; exit 2 already separates contract failure from findings. |
| N5 | Audited-manifest-digest header in the JSON | P2 | Output schema frozen. Prompted by a real observation (see `phase3/ONBOARDING_MEASUREMENT.md` §4) and recorded as a real gap. |
| N6 | Test suite inside an unpacked sdist: 196 passed, 22 failed, 70 errors because the corpora are not vendored | P2 | Documented in the README's testing section with the measured numbers. It is *not* fixed by making those tests skip: a silently missing acceptance input is precisely what a release gate must not permit. |
| N7 | 60 drive-rooted workspace paths in the phase design/evidence documents | P2 | Scrubbing them would cost provenance specificity and is the kind of P2 sweep the phase brief forbids; none carries a username or a credential. |
| N8 | `python -m paper_doctor.cli` exits 0 printing nothing (the module has no `__main__` guard) | P2 | The documented entry point is the `paper-doctor` console script; `python -m paper_doctor` fails loudly. No measured user hit this, so it was not allowed to reopen `src/` after the artifact scan. |
| N9 | `NOT_APPLICABLE` does not distinguish "correctly absent" from "you forgot to declare it" | P3 | Each reason line already says which relation was absent; a machine-readable split is a schema change. |
| N10 | mypy scoped to `src/` | P3 | Widening it mid-freeze would be a new gate, not a pass on an existing one. |

## 9. Gate deviations — stated plainly

**§15 (one real human first-use test) is NOT OBSERVED, and cannot be observed from inside this
environment.** The requirement is met in every part except the part that requires a person:

- The kit exists, is reproducible, contains no answer and no expected output, and is integrity-verified:
  `release/onboarding-kit/` with `KIT_MANIFEST.txt`, 298,788 bytes, purity check clean, built from the
  artifacts in §2 above.
- Two fresh-agent measurements were run and recorded (`release/onboarding/RUN1_AGENT_LOG.md`,
  `RUN2_AGENT_LOG.md`) and they produced the fixes in §7. Those are **agent** runs. They demonstrate the
  kit is walkable; they do not demonstrate a human can walk it, and they are not offered as §15 evidence.
- What is missing is a tester who did not participate in Paper Doctor Phases 0–3, on a machine that is not
  this one, uncoached, filling in `RECORDING_SHEET.md`. That is 30–45 minutes of a stranger's time plus one
  2.2 MB download. `release/HUMAN_ONBOARDING_RECORD.md` lists all thirteen §15 quantities as `UNKNOWN` and
  names the procedure that would fill them.

Per §23 this is a release condition ("human onboarding complete"), and per §20 a gate that is not met is
either P0/P1 or a disclosed deviation. It is disclosed, and it is the reason the release halts here for a
decision that belongs to the user: nominate a human tester, or waive §15 for 0.1.0.

Two further deviations, smaller:

- **The §14/§15 kit was dry-run by an agent**, not by a person, before being handed over. The dry run
  checked the layout is load-bearing (the manifest resolves `root` against the manifest, so the kit's
  directory shape must match) and that the fetch script materialises the missing corpus. It verified the
  kit is *self-consistent*, not that it is *usable*.
- **`.check/` is scratch and is not committed**, so the fresh-install evidence in §3 is reproducible only
  by re-running the commands, not by checking out a script. It is recorded here as commands and outputs,
  which is what §19 asks for.

## 10. Release decision

Everything the machine can check is green and everything the freeze allows to be pinned is pinned:
288 tests, three lint/type gates, two artifacts, two fresh installs, one byte-identical acceptance digest
across four routes, zero credential shapes, zero blob/worktree drift, zero published mention of the
withheld submission, P0 = 0, P1 = 0.

The single unmet condition is a human. Therefore: commit and tag locally, prepare the repository and the
publishing workflow — and stop before the push and before the PyPI publish, where §23's precondition is
not satisfied and where the action cannot be undone by us alone.
