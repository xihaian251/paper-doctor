# §15 Human onboarding record — Paper Doctor 0.1.0

Status: **NOT OBSERVED — blocked on a person, not on the tool.** Recorded 2026-09-29 16:0x.
Updated 2026-09-29 after §7: the owner waived this gate and released anyway. **The status is unchanged by
that decision — still zero human observations** — and this file stays the authority for what was and was
not measured.

## 1. What §15 requires, verbatim from the brief

> after the generic workflow is stable, perform one real human first-use test. Tester must not have
> participated in Paper Doctor Phase 0-3. Use another computer/environment if practical; give only
> README + installation instructions + prepared TabM acceptance workspace; do not coach; record only
> observed facts; create `release/HUMAN_ONBOARDING_RECORD.md`, UNKNOWN for unobserved details.

## 2. Why it was not performed here

The requirement is an observation of a human who was not part of this project's phases. This machine
has exactly one human participant in the sessions that built Paper Doctor, and that person authored the
Phase 0-3 briefs, so they are excluded by the second sentence of the requirement. There is no second
person, and no second physical machine, available to me in this environment, and I will not fabricate a
test report or present an agent run as a human observation.

**What would unblock it, concretely:** one person who has not read this repository, on their own
computer, with the kit described in §3 below handed to them as a folder, and no explanation beyond the
kit's own task card. Estimated effort on their side: the two agent runs took 83 s and ~9 min
respectively to a first audit; a human reading every section slowly should budget 30-45 min including
writing the sheet. Their side needs: Python 3.11+, a network connection for one 2.2 MB arXiv download
(or the corpus already on disk), and a terminal. Nothing else.

## 3. The kit that is ready to hand over

Built by `python scripts/build_onboarding_kit.py` into `release/onboarding-kit/` (git-ignored: it
stages build artifacts). Contents at 2026-09-29, from `KIT_MANIFEST.txt`:

| path | sha256 | why it is in the kit |
| --- | --- | --- |
| `README.md` | `689b7a19f3614f66a97f00f5b8d427a8243dce2e64cf665e305a8cf4d7e6a076` | the only documentation the tester is given |
| `TASK_FOR_TESTER.md` | `d46d765aa46144d8a26b5fdb601f8713dfc1c3bcced0e884707b619a324b3c88` | four neutral instructions; names no prerequisite and no answer |
| `RECORDING_SHEET.md` | `47294aeeb067ff47a6dbf749100978d7a3ff04a842fe3bac3576dfc82d858627` | the observation template; `UNKNOWN` explicitly allowed |
| `phase3/tabm/paper-doctor.yml` | `7e809014f0fa5019622fcec5280cec2f1d4f0e243f7cd3b156b7ebae3e009377` | the prepared acceptance workspace, byte-identical to the frozen one |
| `phase3/tabm/findings.json` | `c56b62623b39ed9a4c311f8bcc6be6de457c1a0f8a4d34d3da99a4b71c7d2774` | the workspace's declared Result Doctor input |
| `scripts/fetch_acceptance_inputs.py` | `25344877d3d8786cb7480f84143355d2e2ec1eb3b8e1890c645f8a6382a52da3` | so the workspace's paper root can be materialised; the tester is not told to run it |
| `dist/paper_doctor-0.1.0-py3-none-any.whl` | `192e3e17d7e405738632a5b222ca4610a35e0c55aae5a995fb91eccdab9a1887` | install route that needs no PyPI |
| `dist/paper_doctor-0.1.0.tar.gz` | `bfd3a87f7c7b20f73277bfb3bbd7223c208b3c9e2cfa208e45829d9cbcd0e30a` | same, from source |

Both staged artifacts were rebuilt at 16:42 on 2026-09-29, after the RTDL anchors were made
self-contained and the README's sdist numbers re-measured against the new artifact, and the kit was
regenerated from them (`305,805 bytes`, purity clean). Two earlier generations are therefore stale:
`5c36af8a…` / `d249621a…` and `b03d7276…` / `71539fa9…`. Neither appears in the table above, so nobody can
verify against a superseded artifact. Recording the superseded digests at all is deliberate — a tester who
downloaded an earlier kit can now tell that their copy is not this one.

Deliberately absent, enforced by the builder's purity check (which refuses and exits `2`): the project's
own `pd_audit.txt`, `pd_findings.json`, `end_to_end_chain.json`, every phase report/brief/preflight, and
the paper corpus itself. A kit that shipped the expected output would measure nothing.

Kit layout is load-bearing rather than cosmetic: the workspace declares
`root: ../acceptance-inputs/tabm-arxiv/src`, and the fetch script resolves its target from its own
location, so the fetch lands exactly where the declaration points. The manifest is never edited.

**Kit integrity check performed (an agent, not the human test).** Re-run on the current kit generation in
the minutes before 16:57 on 2026-09-29: a fresh virtualenv, `pip install dist/paper_doctor-0.1.0-py3-none-any.whl`
from inside the kit, the kit's own `scripts/fetch_acceptance_inputs.py` run from the kit root (it reported
`DOWNLOADED gmmvi / rtdl / tabm` and placed the TabM source exactly where the workspace manifest declares
`root`), then `paper-doctor audit phase3/tabm --json dryrun2.json` → exit 0 and
`08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0`, 17,511 bytes - the frozen acceptance
digest. An earlier generation of this check ran against a kit whose corpus directory was already populated
and therefore reported `SKIPPED ... already carries the frozen main.tex`; both outcomes are correct behaviour
and the second one proves the location coincides. This shows the kit is self-sufficient. It does **not** show
a human can use it.

The scratch products of that check (`phase0/sources/`, `phase3/acceptance-inputs/`, `dryrun2.json`) were
removed again; the kit as handed over is the eight files of `KIT_MANIFEST.txt`, and the builder's purity
check is what guarantees nothing else was staged into it.

## 4. Observed facts

None. Zero human observations exist for this release. Every quantity §15 asks to record is below as
`UNKNOWN`, with the one column that is not a guess: how it will be obtained.

| §15 quantity | Value | How it gets filled |
| --- | --- | --- |
| Tester identity / participation status | UNKNOWN | the person who accepts the kit confirms they have not read this repository |
| Computer and environment used | UNKNOWN | recording sheet §0 |
| Whether another machine was used ("if practical") | UNKNOWN | recording sheet §0 |
| Files opened, in order | UNKNOWN | recording sheet §1 |
| Commands typed, in order, with exit codes | UNKNOWN | recording sheet §2 |
| Steps and time to first successful audit | UNKNOWN | recording sheet §2 |
| Error messages met, verbatim | UNKNOWN | recording sheet §3 |
| Manual declarations the tester made | UNKNOWN | recording sheet §5 |
| Ambiguities and guesses | UNKNOWN | recording sheet §4 |
| Whether the tester understood the five statuses | UNKNOWN | recording sheet §6 |
| What the tester could not determine from output | UNKNOWN | recording sheet §7 |
| Whether the tester trusted the printed numbers | UNKNOWN | recording sheet §8 |
| Verdict (without guessing / after guessing / did not complete) | UNKNOWN | recording sheet §9 |

## 5. What the two agent runs are, and what they are not

`phase3/ONBOARDING_MEASUREMENT.md` records two first-use runs by readers with zero project context
inside a stripped clone (`release/onboarding/RUN1_AGENT_LOG.md`, `release/onboarding/RUN2_AGENT_LOG.md`,
scratch root normalised to `<scratch>` and nothing else changed). They are a legitimate test of the
documentation as a *dependency-free instruction sequence*: they found and forced the fixes for the
traceback-on-missing-`--json`-directory, the uninformative missing-root message, the README's
self-contradictory worked example, the undocumented rule table and field vocabulary, and (in the second
run) the corpus prerequisite.

They are not §15's human test. The readers were agents, they had indirect access to project vocabulary
through the file names they were told not to open, and no human reading behaviour, typing habits, or
tolerance for ambiguity is represented. Where the record above says UNKNOWN it stays UNKNOWN; nothing
from the agent runs was promoted into a human observation.

## 6. Consequence for the release gate

§23 lists "human onboarding complete" among the conditions for automatic publication. That condition
is **not met and cannot be met by me**. How the release proceeds under that deviation is stated in
`release/RC_AUDIT.md`, §"Gate deviations", and raised for the user's decision rather than resolved
silently here.

## 7. The decision, as given

The decision was put to the project owner on 2026-09-29 with three options: supply an external tester and
hold the release; publish GitHub only and hold PyPI; or waive §15 and publish 0.1.0 now. The answer was
**waive §15 and release now**.

What that decision does and does not establish:

- It is an **owner's risk acceptance**, which is a real thing a project owner is entitled to grant. It is
  not an observation, and it does not convert any `UNKNOWN` in §4 into a fact.
- §15's evidence state after the release is exactly what it was before it: **zero human first-use
  observations**. The release commit, the tag, the GitHub Release notes and PyPI metadata must not, and
  do not, claim a human test.
- The exclusion in §2 still applies to the person who made this decision: they authored the Phase 0–3
  briefs, so they cannot later serve as §15's tester for 0.1.0 either. §15 remains open for 0.1.x.
- Practical consequence for anyone who runs the kit: if a real first-use failure appears after the
  release, it is a normal bug report against 0.1.0, not a violated gate.
