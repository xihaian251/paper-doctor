# Phase 3 §14 — first-use measurement record (two runs)

Measured 2026-09-29. Two independent first-use runs, each by an agent that had not authored the
documents it was reading, inside a **fresh copy of the repository stripped of every design artifact**
(phase reports, the Phase 3 brief, the preflight, `phase3/tools/`, `phase3/probe-invented-claim/`,
`phase0/`, `phase1/`, `phase2/`, corpora, caches). The observable record of each run is the run's own
log; the numbers below are quoted from those logs, not reconstructed.

- Run 1 log: `F:/MLResearch/onboarding-sim/clone1/ONBOARDING_REPORT.md` (263 lines, 15:06).
- Run 2 log: `F:/MLResearch/onboarding-sim/clone2/MEASUREMENT2.md` (188 lines, 15:39).

Both sandboxes are outside the repository and are scratch. Each log is archived verbatim at
`release/onboarding/RUN1_AGENT_LOG.md` and `release/onboarding/RUN2_AGENT_LOG.md` with one mechanical
edit: the scratch clone root `F:\MLResearch\onboarding-sim\` is replaced by `<scratch>` (seven
occurrences per file). No command, number, quote, verdict or timing was changed.
`release/onboarding/README.md` records the digests at copy time and the reproduction procedure.

## 1. What was measured, and the two verdicts

§14 required commands typed, manual declarations, validation failures, time and steps to the first
successful audit, and ambiguities. Both runs answered in that form.

| Quantity | Run 1 | Run 2 |
| --- | --- | --- |
| Verdict | **COMPLETED AFTER GUESSING** | **COMPLETED AFTER GUESSING** |
| Shell commands to finish | 34 (20 tool calls) | 22 |
| Install start → first successful audit | ~5 min | **65 s** |
| Session start → exported JSON | not measured | 83 s |
| Files opened as a user | 4 | 4 (`README.md`, `pyproject.toml`, `examples/quickstart/`, workspace manifest + `findings.json`) |
| Non-zero exits | 2 × exit 2, **1 × exit 1 with a raw traceback** | 2 × exit 2 (one deliberate probe), **no traceback, no exit 1** |
| Exported JSON byte-identity | matches shipped `pd_findings.json` (`08836ccf…`) | matches shipped `pd_findings.json` (`08836ccf…`) |
| Guesses required | 5 (corpus prerequisite, venv, Windows console-script path, root resolution base, `--json` semantics) | 2, both described as low-risk (corpus prerequisite, non-persisting-shell invocation) |
| Tally read off the workspace | 10 / 2 / 5 / 14 / 1 over 32 findings, exit 0 | identical |

Where the time went, run 1, in its own words: "~10 s install, ~3 min discovering that the TabM paper
source was missing and hunting for the fetcher (README silent, no `INSTALL`/quickstart, error message
misleading), ~1-2 min arXiv download + sha256 verification, **0.45 s the audit itself** … Install and
compute were free; **documentation discovery was the entire cost**."

## 2. Defects found, in the order they were fixed

P0 = the tool cannot be used or produces a wrong claim about itself. P1 = a first user is blocked or
misled and must guess. P2 = friction with a documented workaround. P3 = preference.

### P1-1 `--json` into a non-existent directory crashed with a traceback and exit 1

Run 1, command 27: `audit phase3/tabm --json nope/deep/r.json` →
`FileNotFoundError` traceback through `src/paper_doctor/cli.py:178`, exit 1. Two defects in one: an
ordinary input mistake was charged to Paper Doctor as an internal failure (exit 1 is reserved for that),
and the traceback printed implementation filenames into the user's terminal.

Fixed by making it an input-contract failure: exit 2, one line on stderr
(`paper-doctor: --json cannot write to <path>: its directory <dir> does not exist. Create it, or
choose a destination that already exists; the audit itself was not run.`), nothing on stdout, no
partial file. Pinned by `tests/test_cli.py::test_a_report_path_in_a_missing_directory_exits_two_without_a_traceback`
and its companion `test_a_report_path_with_no_directory_component_still_writes` (a bare filename must
keep working). No `P_*` code was added: the frozen twelve-code set is unchanged and this is not a
manifest problem, so it is not a manifest code.

### P1-2 the missing-paper-root error named the declared string but not the path that was tried

Run 1, validation item 1: the message printed only `..\acceptance-inputs\tabm-arxiv\src is not a
directory`, which read from the repository root points *outside* the repository, and it reused
`P_UNRESOLVED_REF`, a code the README documented for claim-text/line mismatches. Run 1 recorded that
this sent the reader "hunting in the wrong place".

Fixed by quoting the field path, the declared string, the resolved absolute path, and both remedies.
Evidence it worked: run 2, error E1, "Actionable? **Yes, unusually so.** It names the field, quotes the
declared string, shows the absolute path it tried, and gives two remedies… Cost: ~14 s." Pinned by
`tests/test_manifest_validation.py` (the assertion requires the code, both path forms, "not a
directory", and `_registry/paper/root`).

### P1-3 the README's worked example contradicted its own sample manifest

Run 1, ambiguity item 2: "the sample output block sits *before* the sample manifest, so the sentence
points at nothing… `PD001 PASS C1 … form=COMPARATIVE` … while the sample manifest immediately below
declares `C1 … form: NUMERIC_ATTRIBUTION`. The worked example contradicts the example manifest; I could
not tell which one was authoritative."

Fixed structurally, not by prose: `examples/quickstart/` now holds a real three-claim workspace (paper
source, empty RD artifact, manifest) and the README transcript is that directory's actual output. Six
tests in `tests/test_readme_example.py` fail if either the example or the transcript drifts, including
`test_the_readme_manifest_block_is_the_example_file_verbatim` and
`test_the_readme_listing_is_what_the_example_prints`. Run 2, command 9: "output matched the README
listing line-for-line".

### P1-4 rules were unaddressable from the documentation

Run 1, ambiguity item 5: "Rule ids are undocumented… there is no table of what each rule checks, which
statuses each can return, or what manifest content each rule requires. I recovered the questions from
the JSON's `question` field, which the README also never mentions."

Fixed by `## The seven rules`: one row per rule quoting `NAME` and `QUESTION` from `src/paper_doctor/rules.py`
verbatim, plus what the manifest must supply and the statuses the rule can answer, plus the two
properties that hold only by construction (`NOT_RUN` comes from the audit layer; `PD001` has no `FAIL`).
`test_every_rule_row_quotes_the_frozen_question_and_name` pins the quoting.

### P1-5 manifest fields the shipped workspaces use were undocumented

Run 1, ambiguity items 6-7: `not_audited_reason` (no example, no resulting status), `scope`,
`universe_status: PARTIAL`, `quantifier` — "precisely what produced `PD002 INCONCLUSIVE C7`".

Fixed by `### Field vocabulary`, one row per field with its values and the status consequence, and by
`test_a_vocabulary_row_lists_exactly_the_frozen_enum` which compares each row's token set against the
enum in `src/`, so a renamed or dropped value fails the suite. The `precision_declaration` row also
documents the measured escape hatch: `round: 0.01` means *zero* decimals to the frozen parser, so a
coarse declaration can make 0.92 and 0.88 agree;
`test_the_declared_precision_really_governs_the_number_comparison` proves that behaviourally rather
than by assertion.

### P1-6 the corpus prerequisite was documented where a first user does not look (the residual gap at run 2)

Run 1's costliest item and run 2's only substantive guess, in run 2's words: "The README presents this
script only under 'Testing the tool', for the acceptance *tests* — never as a step for auditing the
real-paper workspace… a doc that said 'the tabm workspace's paper source is not vendored; run
`python scripts/fetch_acceptance_inputs.py tabm` first' would have removed the leap. This is the main
reason my verdict is COMPLETED AFTER GUESSING."

Fixed now, in two places that a user reaches before or at the failure: `### When the audit exits `2`
because the paper source is not there` (verbatim-shaped message, the two ways out, and the statement
that Paper Doctor will not search, download, or accept a near-miss file), and one sentence in `## Install`
pointing at that section as the checkout's extra step.

### P1-7 `PD006`'s literal-presence limit surprised a reader for two minutes

Run 2, §5 item 5 and friction #2: nothing said that a claim of "$8$ datasets" whose float lists eight
rows without printing the character `8` will `FAIL`; the reader resolved the surprise by opening the
LaTeX and counting. This is exactly §17's "a FAIL does not mean the paper is wrong", in a case the
documentation had not named.

Fixed by a paragraph in `## The seven rules` stating that `PD006` compares printed strings, that
row-counting and column-summing are outside the audited universe by design, and what the `FAIL` does and
does not mean. No rule behaviour changed.

### P2-8 install route and shell invocation

Run 2, §5 items 2-3: which artifact to trust (PyPI `0.1.0` vs a checkout) and how to call the console
script when the shell does not persist activation. Fixed in `## Install` by one paragraph on choosing
by what you are auditing (both routes print the same version — one source in the package) and one line
naming `.venv/Scripts/paper-doctor` / `.venv/bin/paper-doctor` for non-persisting shells.
Run 1 also saw the checkout install as `paper_doctor-0.1.dev0`; that was a stale clone taken before the
version bump, and it is recorded as a measurement artifact, not a defect.

## 3. Declined, with reasons (P2/P3 — §14 says fix only P0/P1)

| # | Request | Grade | Why declined |
| --- | --- | --- | --- |
| D1 | Run 1 "What would have made this faster" #2b: give the missing-root error **its own `P_*` code** instead of `P_UNRESOLVED_REF` | P2 | The frozen code set is closed at twelve and asserted as closed (`test_the_code_set_is_closed_at_twelve`); adding a thirteenth changes the contract §7 freezes, for a message whose text already names the field and the tried path. |
| D2 | Run 1 #8 and run 2 §5 item 3-4: a coverage footer in the listing ("9 claims declared, N links") | P2 | It changes the frozen output format and the canonical JSON schema, which is byte-pinned by the acceptance digests. The same information is available by reading `_claims`. |
| D3 | Run 1 #10: a `paper-doctor validate` / `init` subcommand | P2 | New CLI surface in the release window; `audit` already separates contract errors (exit 2, no findings printed) from rule findings (exit 0), which is the distinction the request wanted. |
| D4 | Run 2 §10 (a): a `--dump-floats` mode printing the parsed cell/block/label structure | P3 | Genuinely useful, and it is the single biggest remaining readability gap, but it is a new output surface and cannot be designed honestly in a release freeze. **Carried to post-release as the first candidate.** |
| D5 | Run 2 §10 (b): distinguish "not printed" from "contradicted" inside `PD006` reasons | P3 | Rewording rule reasons re-opens frozen Phase 0-2 behaviour; the documentation paragraph (P1-7) carries the same warning at lower risk. |
| D6 | Run 2 §10 (c): an audited-manifest-digest header in the JSON, prompted by the live-edit observation in §4 below | P2 | Same reason as D2 — output schema frozen. Recorded as a real gap, not a non-issue. |
| D7 | Run 1 statuses section: the docs do not distinguish "correctly absent" `NOT_APPLICABLE` from "you forgot to declare it" | P3 | Each reason line states which relation was absent; a machine- readable distinction would be a schema change. |

## 4. Anomaly recorded from run 2: the acceptance workspace changed while a user was in it

Run 2, §7, quoted from its log: at 15:36:42 the reader re-opened `phase3/tabm/paper-doctor.yml` and
found it modified since its 15:34 runs — mtime 15:35, size 7677 (was 7391), a new claim `C10`,
`_registry.paper.root` repointed to `../../phase0/code/paper_text/data/tabm_arxiv/src`, and the
`main.tex` pin changed to `5368b87a…`. That root does not exist in any clone of this repository and that
pin does not match the fetched `main.tex` (`15663553…`), so the file as modified could not have audited.
By the reader's 15:36:57 re-run the file had been reverted byte-for-byte; its diff against the snapshot
it took at 15:33:53 is clean, and its two audit outputs are identical.

What I verified independently afterwards, at 15:5x:

- `phase3/tabm/paper-doctor.yml` is 7391 bytes, sha256
  `7e809014f0fa5019622fcec5280cec2f1d4f0e243f7cd3b156b7ebae3e009377`, nine claims `C1`-`C9`,
  `root: ../acceptance-inputs/tabm-arxiv/src`, mtime 14:43 — i.e. **before** the reported window.
- `paper-doctor audit phase3/tabm --json …` reproduces `08836ccfe17f…dff9aa0` and a listing that
  differs from the frozen `pd_audit.txt` only in the manifest path printed in its first header line.

**Attribution: UNKNOWN.** No agent or process that I directed modified that file; my own background
measurements were read-only by instruction and the run-2 agent states it touched nothing. The
modification and the revert both came from outside my control, and there was no git history at that
moment (`git init` is a later §21 step) to identify it. This is reported rather than explained away, and
nothing here attributes it.

**A second in-place mutation, this one attributed.** Later in the same session a vendored third-party
fixture (`tests/fixtures/rtdl_pilot_README.md`) was found rewritten between two of my own commands:
13,162 bytes / `50f7994f…` became 13,149 bytes / `799726d9…`, with single quotes turned into double quotes
and a wrapped Python comprehension joined onto one line. Unlike the manifest event this one is explained and
reproduced: `ruff format .` formats Python fenced blocks inside Markdown in this toolchain version, so the
project's own gate command was rewriting evidence documents. Re-running it reproduced the byte loss exactly.
The fix and the two tests that hold it are recorded as defect P1-9 in `release/RC_AUDIT.md` §7, and the
privacy gate's digest-conditional skip is what surfaced it (§4c there). The material difference between the
two events is knowledge, not severity: one has a mechanism, the other does not.

Why it matters for the product, and it is the run's own point: the digest pins verify the *bytes the
manifest declares*, so they catch a drifted corpus, but they cannot catch a drifted **manifest** — a
user auditing inside that window would have audited different declarations and gotten exit 2 rather
than a warning about the file having changed. That is D6, and it is a real limitation of 0.1.0.

## 5. Post-fix verification of the fixes themselves

Not claimed on the strength of the edits alone:

- Four gates green after every documentation and CLI change: **288 passed** through the onboarding window
  (292 at the release boundary, the four extra being the clean-checkout and vendoring firewalls of
  `release/RC_AUDIT.md` §9), `ruff check` clean, `ruff format --check` clean, `mypy src` clean. The format
  gate's file count is *not* stable across this session — it read 42 files here and 32 at the release
  boundary — because the command was counting Markdown until Markdown was excluded (P1-9).
- Every P1 fix above names the test that pins it; each was also mutation-checked by breaking the
  condition and watching that test die, then restoring the file byte-for-byte.
- The privacy gate added in this block (`tests/test_phase3_firewalls.py`, §20) was mutation-checked
  with four reintroduced leaks — a drive-rooted path in a shipped fixture, an account name in the
  README, a contiguous `ghp_…` token in a shipped script, a `-----BEGIN … PRIVATE KEY-----` header —
  all four died, and the restored baseline passed. It caught one real leak while being written:
  `tests/fixtures/RD_SNAPSHOTS.md` carried `F:\MLResearch\experiment-doctor\phase0-gmmvi`, which is
  now described without a local path.
- Run 2 is itself the post-fix measurement of P1-1 through P1-5: traceback gone, missing-root error
  actionable, quickstart transcript reproduced, rules and fields found in the README. P1-6, P1-7 and
  P2-8 were fixed after run 2 and are **not** re-measured by a third run; they are documentation-only
  additions whose content is pinned by `tests/test_readme_example.py`.

## 6. §15, the real human test

§15 requires a tester who did not participate in Paper Doctor Phase 0-3, on a machine and environment of
their own, given only the README, the install instructions and the prepared TabM workspace, with no
coaching. That condition cannot be satisfied on this machine: every interactive session here has been
this project's own author-agent, and no second human has been present in the environment. The two runs
above are agent runs inside sandboxed clones of this repository — they are a strong *documentation*
test (the reader had zero context and read only user-facing files) and they are recorded as such, but
they are **not** the human observation §15 asks for and are not written up as if they were.

Status of §15: `release/HUMAN_ONBOARDING_RECORD.md` records the kit that is prepared for it, the exact
procedure, and `UNKNOWN` for every unobserved quantity. See the blocker statement in that file.
