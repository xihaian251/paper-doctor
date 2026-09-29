# MEASUREMENT2 — first-time user log of Paper Doctor on `phase3/tabm`

Observer: domain researcher (tabular ML), zero prior knowledge of this project.
Environment: Windows, git-bash, Python 3.13.1 on PATH, no NVIDIA GPU (none needed), network available.
Constraints honored: worked only inside `<scratch>\clone2`; did not open `phase0/`, `phase1/`,
`phase2/`, `phase3/tools/`, `phase3/TABM_PREFLIGHT.md`, or any REPORT/BRIEF/ERRATUM/HANDOFF/research-log file;
did not modify any project file. Read as a normal user: `README.md`, `pyproject.toml`,
`scripts/fetch_acceptance_inputs.py`, `examples/quickstart/`, and the workspace's own declared inputs
(`phase3/tabm/paper-doctor.yml`, `findings.json`).

**VERDICT: COMPLETED AFTER GUESSING** (two low-risk guesses; details in §5)

---

## 1. Command log (every command typed, in order, OK/FAIL)

Wall clock noted where it matters. Started 15:32:52.

| # | Time | Command | Result |
|---|------|---------|--------|
| 1 | 15:32:52 | `ls -la <scratch>/clone2` | OK |
| 2 | 15:32:52 | Read `README.md` | OK (fully read; it is the main doc) |
| 3 | ~15:33:00 | `ls phase3 src scripts examples tests` | OK |
| 4 | ~15:33:00 | `python --version; pip --version` | OK — Python 3.13.1 |
| 5 | 15:33:0x | `ls -la phase3/tabm; find phase3/tabm -maxdepth 2 -type f` | OK |
| 6 | 15:33:10 | `date; ls phase3; find . -maxdepth 3 -iname "*acceptance*"; cat pyproject.toml` | OK — noticed manifest root `../acceptance-inputs/tabm-arxiv/src` does not exist yet |
| 7 | 15:33:00→10 | `python -m venv .venv` | OK (10 s) |
| 8 | 15:33:10→32 | `.venv/Scripts/python.exe -m pip install -e .` | OK — installed `paper-doctor-0.1.dev0` + PyYAML 6.0.3 (22 s) |
| 9 | ~15:33:40 | `.venv/Scripts/paper-doctor.exe --version && .venv/Scripts/paper-doctor.exe audit examples/quickstart` | OK exit 0 — output matched the README listing line-for-line |
| 10 | 15:33:53 | diagnostic: move `paper-doctor.yml` aside, `paper-doctor.exe audit phase3/tabm`, move back | FAIL exit 2 (intentional probe), message quoted in §2 |
| 11 | 15:33:53 | `paper-doctor.exe audit phase3/tabm` (first real attempt) | **FAIL exit 2** — `P_UNRESOLVED_REF` on paper root, quoted in §2 |
| 12 | 15:33:43→53 | `.venv/Scripts/python.exe scripts/fetch_acceptance_inputs.py --list` | OK — `tabm 2410.24210 absent` |
| 13 | 15:33:59 | `.venv/Scripts/python.exe scripts/fetch_acceptance_inputs.py tabm` | OK — `DOWNLOADED tabm`, all three digest checks passed (6 s) |
| 14 | 15:34:04→05 | `.venv/Scripts/paper-doctor.exe audit phase3/tabm` | **OK exit 0 — FIRST SUCCESSFUL AUDIT** (1 s wall) |
| 15 | 15:34:15 | `.venv/Scripts/paper-doctor.exe audit phase3/tabm --json audit_report_tabm.json` | OK exit 0 — JSON exported (17,511 B, 32 findings) |
| 16 | 15:34:2x | `sha256sum audit_report_tabm.json phase3/tabm/pd_findings.json` + JSON load | OK — my export is byte-identical to the workspace's pre-existing `pd_findings.json` |
| 17 | 15:34:4x | `sed -n '880,890p' main.tex; grep -rn tabred-datasets ...` | OK — manual check to interpret the PD006 FAIL on C2 |
| 18 | 15:34:5x | `awk/grep` row count in `tables/app-tabred-datasets.tex` | OK — table lists exactly 8 dataset rows but never prints the string "8" as a count |
| 19 | 15:35–36 | `sed -n '1,10p' tables/app-rtdl-datasets.tex; sed -n '526,530p' main.tex` | OK — confirmed C8/C9 story (§6) |
| 20 | 15:36:42 | `date` + re-read of `phase3/tabm/paper-doctor.yml` | OK — **discovered the manifest had been externally modified** (see §7) |
| 21 | 15:36:57 | re-run `paper-doctor.exe audit phase3/tabm --json audit_report_tabm_v2.json` | OK exit 0 — output identical to run #14 (the external edit had already been reverted) |
| 22 | 15:37 | `diff /tmp/pd-backup.yml phase3/tabm/paper-doctor.yml` | OK — manifest currently byte-identical to my pre-run 15:33 snapshot |

Totals: 22 distinct commands/actions; **2 non-zero exits**, both `exit=2` input-contract errors (#10 intentional,
#11 the one real blocker). No traceback, no crash, no exit-1.

## 2. Error messages verbatim — did they tell me what to do?

**E1 (real blocker, exit 2):**
```text
P_UNRESOLVED_REF at _registry/paper/root: declared root ../acceptance-inputs/tabm-arxiv/src resolves to <scratch>/clone2/phase3/acceptance-inputs/tabm-arxiv/src, which is not a directory: restore the paper source there, or point _registry/paper/root at the checkout that holds it
```
Actionable? **Yes, unusually so.** It names the field, quotes the declared string, shows the absolute path it
tried, and gives two remedies. What I did next: searched the repo for anything that could "restore the paper
source there", found `scripts/fetch_acceptance_inputs.py` (its docstring table maps `tabm` → arXiv 2410.24210 →
exactly `phase3/acceptance-inputs/tabm-arxiv/src`, matching the missing root character-for-character), ran it,
and the audit worked on the very next try. **Cost: ~14 s.** But note the guessing component in §5.

**E2 (diagnostic probe, exit 2):**
```text
P_UNRESOLVED_REF at <scratch>\clone2\phase3\tabm\paper-doctor.yml: no readable manifest is present at this path
```
Actionable? Yes (I had deliberately moved the manifest; it confirmed the workspace directory arg resolves to
`paper-doctor.yml` inside it — something the README only implies via `# paper-doctor audit examples/quickstart/paper-doctor.yml`).

## 3. Manual declarations / environment preparations before the first audit worked

**Three**, plus one guess:
1. Create virtualenv (`python -m venv .venv`) — 10 s.
2. Editable install (`pip install -e .`) — 22 s. (I chose the checkout over the README's PyPI route; §5.)
3. Fetch the pinned paper corpus (`python scripts/fetch_acceptance_inputs.py tabm`) — 6 s.
- No manifest editing, no environment variables, no file renames were needed. Zero declarations by me — the
  workspace shipped fully declared (`_registry` pins, 9 claims, 11 links) and every pin matched the bytes on disk
  (findings.json sha `c56b6262…` verified equal by hand).

## 4. Wall-clock timings

- First command: 15:32:52. Install start→done: 15:33:00→15:33:32 (**32 s**).
- Install start → **first successful tabm audit: 15:34:05 (65 s)**.
- Install start → **exported JSON: 15:34:15 (75 s)**. Start-of-session → JSON: **83 s**.
- Audit itself ~1 s; JSON export ~1 s. Corpus download ~6 s (network).

## 5. Things the documentation did NOT say that I had to infer or guess

1. **That `scripts/fetch_acceptance_inputs.py tabm` is how you prepare the `phase3/tabm` workspace for use.**
   The README presents this script only under "Testing the tool", for the acceptance *tests* — never as a step
   for auditing the real-paper workspace. HOW I GUESSED: the P_UNRESOLVED_REF remedy said "restore the paper
   source there"; I greped for anything that writes to `acceptance-inputs`, read the script's docstring, and
   matched its target path to the manifest's root string. Confidence was high because the paths coincide
   exactly, but a doc that said "the tabm workspace's paper source is not vendored; run
   `python scripts/fetch_acceptance_inputs.py tabm` first" would have removed the leap. This is the main reason
   my verdict is COMPLETED AFTER GUESSING.
2. **Invocation style under git-bash.** README shows `.venv/Scripts/activate`; my shell does not persist state
   between commands, so I guessed direct call `.venv/Scripts/paper-doctor.exe ...`. Worked; zero-risk guess.
3. **Which artifact to trust: PyPI `paper-doctor==0.1.0` vs this checkout (`0.1.dev0`).** README offers both, no
   guidance on which matches a shipped workspace. I chose the checkout because the workspace and its pinned
   digests live in the same repo; I did not test the PyPI build. Unresolved by documentation.
4. **`--json` destination**: README says the *directory* must already exist. Writing to the existing cwd
   (`clone2/`) was my inference; no error encountered, but I had to read "destination whose directory does not
   exist" (in the exit-code table) carefully to know cwd counts as "exists".
5. **PD006's treatment of enumeration evidence.** Nothing says that a claim like "8 datasets" whose float lists
   8 rows *without printing the string "8"* will FAIL PD006. The README comes closest with "asks whether the
   referenced float actually *prints* the attributed content", but does not warn that counting rows is out of
   scope. I resolved the surprise by opening `tables/app-tabred-datasets.tex` myself and counting (§6).

## 6. Findings of the first audit (what it printed)

Tally: `PASS: 10  FAIL: 2  INCONCLUSIVE: 5  NOT_APPLICABLE: 14  NOT_RUN: 1` (32 findings, exit 0).

- **PD003 FAIL C8** — `the claim states 16281 but the printed cell at (column=# Train, row=Adult, block=b1 [...]) of table:4 states 26048`. Verified by hand: `tables/app-rtdl-datasets.tex` line 8 (Adult row) prints `$26\,048$` under # Train and `$16\,281$` under # Test. The claim text is *real paper bytes* pointed at the wrong column. This is a manifest-side error, not a paper error — exactly what the README's "a FAIL does not localize" paragraph promises, and I confirmed both sides are quoted so a user can check.
- **PD006 FAIL C2** — `the reference resolves to table:5, which does not print 8; it is printed in table:4, table:7, ...`. Verified by hand: the referenced TabReD table lists exactly 8 dataset rows but never prints "8" as a count. So the paper's claim is (by manual inspection) TRUE of its table, and PD006 still FAILs because its rule is literal printing, not row-counting. A FAIL here does NOT mean the paper is wrong — a live demonstration of "what a FAIL does not tell you".
- **PD002 INCONCLUSIVE C7** — `the counts agree (unit=aggregation, 1 targets) but the universe is PARTIAL: an unlisted universe cannot be PASSed` (the "15 random seeds" scope statement).
- **PD003 INCONCLUSIVE C9** — `'Maps Routing' is printed by 2 rows of b1; the source states no structure that separates them, so the declared address has more than one reading` (a `\multirow`-merged label; verified in `main.tex:526-530`). The tool refused to pick a reading.
- **PD001 INCONCLUSIVE C3**, **PD004 NOT_RUN**, seven PD007 NOT_APPLICABLE — all with reasons.

## 7. Anomaly I must record honestly: the workspace changed under me

At 15:36:42 I re-read `phase3/tabm/paper-doctor.yml` (a permitted declared input) and found it had been
**externally modified** since my 15:34 runs: mtime 15:35, size 7677 (was 7391), a new claim **C10** added, the
paper root repointed to `../../phase0/code/paper_text/data/tabm_arxiv/src`, and main.tex's pin changed to
`5368b87a…`. That root does not exist in this clone and the new pin does not match the fetched main.tex
(`15663553…`), so that version could not have audited as-is. By my 15:36:57 re-run (and by diff against the
backup snapshot `/tmp/pd-backup.yml` I took at 15:33:53), the manifest had been **reverted byte-for-byte** to
the original. I did not modify any project file; my audits (#14, #15, #21) all ran against the original 9-claim
manifest, which is why run #21's output equals run #14's. Recorded because "shared live workspace" is
operationally relevant: the digest pins caught nothing here (the change was reverted before my run), but a user
auditing *during* such a window would silently audit different bytes.

## 8. What each status means, in my own words

- **PASS** — this one declared relation agrees with the one declared evidence address, at the declared
  precision; nothing more. Not "the claim is true", not "the table proves the sentence in general".
- **FAIL** — the sentence and the declaration's target disagree *as strings/structure at that address*. It
  tells me: one of {the sentence, the declaration} is wrong, and it quotes both sides plus the address so I can
  check which. It does NOT tell me: which side is wrong; whether the paper is false, unreliable, or sloppy;
  whether some other table or a row-count would actually support the claim (live example: PD006 FAIL C2 where
  the table supports "8" by enumeration, not by printing).
- **INCONCLUSIVE** — evidence on file cannot decide; first-class answer ("untraceable is not false"), remedy is
  usually a better declaration (e.g., `universe_status: RECOVERED`, `block=` qualifier), not a rerun.
- **NOT_APPLICABLE** — this target has no such relation declared to check (e.g., no `same_as` pairing); no
  information about the paper.
- **NOT_RUN** — the whole workspace supplied nothing this rule reads (here: no COMPARATIVE/SUPERLATIVE claims
  → PD004); a statement about the manifest's coverage, not the paper.

## 9. Could I tell, from output alone, what the tool refuses to judge?

Yes, mostly, from the reason lines themselves. Sentences I relied on:
- "the claim carries no declared support link; **untraceable is not false**" (PD001/C3);
- "**an unlisted universe cannot be PASSed**" (PD002/C7);
- "so the declared address has more than one reading" (PD003/C9 — refusal to disambiguate a merged label);
- "no target was supplied for this rule: ... nothing in it carries the key PD004 reads" (PD004 NOT_RUN).
The README's "What this is not" section ("It does **not** judge: fraud or misconduct; novelty; ... theorem or
proof correctness; whether a result reproduces ...") covers the rest; from *output alone* I could not tell that
row-counting is outside PD006's refusal list (§5 item 5) — I inferred that by hand-checking the table.

## 10. Do I trust the numbers printed?

Moderately-high, more than expected for a first run, because:
- quickstart output reproduced the README verbatim (documentation pinned to behavior);
- my JSON export is **byte-identical** (sha256 `08836cc...`) to the workspace's pre-existing `pd_findings.json`,
  and two independent runs in-session agreed;
- inputs are sha256+size pinned and verified before reading; corpus fetch verified tarball and main-file digests;
- both FAIL/INCONCLUSIVE structural findings I spot-checked by hand in the .tex matched the tool's quoted
  addresses (`26\,048` at # Train/Adult; `\multirow{2}` at main.tex:526).
What would raise trust further: (a) a `--dump-floats` mode printing what the parser thinks each table's
cells/blocks/labels are — I had to open raw LaTeX to interpret "table:5 does not print 8"; (b) a note in PD006
reasons distinguishing "not printed" from "contradicted" (row-counting); (c) an explicit "audited manifest
digest" header in the JSON given §7's live-editing observation.

## 11. Verdict and friction ranking

**COMPLETED WITHOUT GUESSING?** No — I completed, but only after the inference in §5.1 (fetch script is the
workspace's setup step) and the invocation guesses. **Verdict: COMPLETED AFTER GUESSING.** Both guesses were
low-risk and forced by an error message that told me exactly what to fix.

3 costliest friction points (all time in seconds of the whole 83 s run, which was otherwise exceptionally
smooth):
1. Missing paper corpus with no workspace-setup doc (14 s + the only guess in the flow) — E1 above.
2. Interpreting PD006 FAIL C2 required hand-reading the paper source (~2 min, post-audit) — enumeration vs
   printed-count is undocumented.
3. Ambiguous install route (PyPI 0.1.0 vs checkout 0.1.dev0) and git-bash venv activation — resolved by
   judgment calls, untested alternative branch.

Deliverables:
- JSON report: `<scratch>\clone2\audit_report_tabm.json` (32 findings, sha256
  `08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0`; duplicate in `audit_report_tabm_v2.json`).
- Fetched corpus (script-created): `<scratch>\clone2\phase3\acceptance-inputs\tabm-arxiv\src\`.
- This file: `<scratch>\clone2\MEASUREMENT2.md`.
