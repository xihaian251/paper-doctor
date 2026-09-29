# Paper Doctor — onboarding report (fresh user, docs-only)

Run of 2026-09-29 on `<scratch>/clone1`. Nothing here is quoted from
`src/`, `tests/`, `phase3/tools/`, `phase3/probe-invented-claim/`, or any design/planning
document — I did not open them. Files I opened: `README.md`, `pyproject.toml`,
`phase3/tabm/paper-doctor.yml`, `scripts/fetch_acceptance_inputs.py`.

## Commands I typed, in order

Bash tool calls: 20. Individual shell commands (some calls chain several): 34.

| # | Command | What happened |
| --- | --- | --- |
| 1 | `ls -la "<scratch>/clone1"` | Saw `README.md`, `pyproject.toml`, `phase3/`, `scripts/`, `src/`, `tests/`. |
| 2 | `ls -la "<scratch>/clone1/phase3"` | Found `tabm/`, `tools/`, `probe-invented-claim/`, `.dl/`. |
| 3 | `ls -la ".../phase3/tabm"` | Found `paper-doctor.yml`, `findings.json`, and pre-baked `pd_audit.txt` / `pd_findings.json`. No paper source. |
| 4 | `cd ".../phase3/tabm" && find . -maxdepth 2 -type f` | Confirmed: workspace has manifest + artifacts, no `.tex` files. |
| 5 | `cd ".../clone1" && ls phase3/` | No `phase3/acceptance-inputs`. |
| 6 | `ls -d phase3/acceptance-inputs` | `No such file or directory` — the manifest's `root` target is absent in a fresh checkout. |
| 7 | `find . -maxdepth 4 -iname "*tabm-arxiv*"` | Nothing. Paper corpus not vendored. |
| 8 | `ls scripts` | Found `fetch_acceptance_inputs.py`. README never mentions `scripts/`. |
| 9 | `ls -la phase3/.dl` | Found `2410.24210.eprint` (2.2 MB) — an unlabelled tarball, no doc says what it is for. |
| 10 | `python --version` | Python 3.13.1 — satisfies `requires-python = ">=3.11"`. |
| 11 | `py --version` | Same interpreter, 3.13.1. |
| 12 | `where python` | Three interpreters on PATH; confirmed I needed a venv to avoid polluting them. |
| 13 | `python -m venv .venv` | OK. `.venv/Scripts/pip.exe` present. |
| 14 | `.venv/Scripts/pip install -e .` | Installed `paper_doctor-0.1.dev0` + `PyYAML-6.0.3`. `paper-doctor` command now exists. |
| 15 | `.venv/Scripts/paper-doctor --help` | Help text is better than the README on some points (it names PD001-PD007 as what `audit` runs). |
| 16 | `.venv/Scripts/paper-doctor audit phase3/tabm` | FAILED, exit 2: missing paper root. First real blocker. |
| 17 | `.venv/Scripts/paper-doctor audit phase3/tabm >out 2>err; echo $?` | Re-ran to see whether the error is stdout or stderr: it is stderr, exit 2. |
| 18 | `.venv/Scripts/python scripts/fetch_acceptance_inputs.py --list` | All three corpora `absent`. Script self-documents `tabm -> phase3/acceptance-inputs/tabm-arxiv/src`. |
| 19 | `.venv/Scripts/python scripts/fetch_acceptance_inputs.py tabm` | `DOWNLOADED tabm: ...\phase3\acceptance-inputs\tabm-arxiv\src` (from arXiv, sha256-verified). |
| 20 | `.venv/Scripts/paper-doctor audit phase3/tabm` | **First successful audit.** Exit 0. 32 findings; `PASS: 10 / FAIL: 2 / INCONCLUSIVE: 5 / NOT_APPLICABLE: 14 / NOT_RUN: 1`. |
| 21 | `.venv/Scripts/paper-doctor audit phase3/tabm/paper-doctor.yml --json tabm-report.json` | JSON exported (17,511 bytes), same listing to stdout. |
| 22 | `sha256sum tabm-report.json phase3/tabm/pd_findings.json` | Identical digests (`08836cc...9aa0`) — README's byte-identical claim holds; also proved my run matched the shipped one. |
| 23 | `.venv/Scripts/python -c "json.load(...)"` (structure peek) | Found undocumented-per-rule fields `rule_name` and `question` in the JSON. |
| 24 | `.venv/Scripts/python -c ...` (rule summary + FAIL/PD004 entries) | Got the seven rule questions; only way I could tell what PD004/PD006 actually check. |
| 25 | `.venv/Scripts/paper-doctor audit phase3/tabmm` | Exit 2, "no readable manifest is present at this path" (good message). |
| 26 | `.venv/Scripts/paper-doctor audit phase3` | Exit 2, names `phase3\paper-doctor.yml` — good. |
| 27 | `.venv/Scripts/paper-doctor audit phase3/tabm --json nope/deep/r.json` | **Raw Python traceback**, exit 1 (`FileNotFoundError`). |
| 28 | `time .venv/Scripts/paper-doctor audit phase3/tabm` | 0.445 s. The audit is instant; the corpus fetch was the slow part. |
| 29 | `ls phase3/acceptance-inputs/tabm-arxiv/src` | `main.tex`, `tables/`(implied), `references.bib`, ICLR style files. |
| 30 | `wc -c < .../main.tex` | 88033 bytes — matches the manifest's pinned `size`, so the pin check is real. |
| 31 | `cd phase3 && "../.venv/Scripts/paper-doctor" audit tabm` | Exit 0 — `root` resolves against the manifest, not the CWD (README never says this). |
| 32 | `... audit tabm 2>&1 \| tail -7` | Same 10/2/5/14/1 totals from a different CWD. Confirmed CWD-independence. |

## Manual decisions I had to make that the docs did not tell me

1. **The paper source is not in the repo and the README never says so.** `paper-doctor.yml` sets
   `root: ../acceptance-inputs/tabm-arxiv/src`, which does not exist in the clone. The README's
   "Install" section is three lines and contains no preparation step. **Resolved by guessing**: I
   listed the repo top level, found `scripts/`, and read `fetch_acceptance_inputs.py` (its own
   docstring says it "is the documented way to rebuild the corpora" — it is documented nowhere a
   first-time user would look).
2. **Which interpreter / whether a venv was needed.** README says only `pip install -e .`. Three
   Pythons are on PATH on this box. **Guessed** (colleague's advice) → `python -m venv .venv`.
3. **Windows path form for the console script.** README's examples are POSIX-flavoured and say
   nothing about `.venv/Scripts/pip` vs `.venv/bin/pip`. **Guessed** `.venv/Scripts/...`; worked.
4. **What `root` is relative to** (manifest dir or CWD?). README: "`root: .  # optional; holds the
   paper's source files`". Nothing about resolution base. **Tested** (commands 31-32) — manifest-relative.
5. **Where to point `--json`.** README shows `--json report.json` but not whether the folder arg or
   the manifest arg is preferred, nor whether the file may live inside the workspace (would it then
   be picked up next run?). I wrote it to the repo root, outside the workspace, to be safe. Guessed.
6. **Whether to trust the pre-baked `pd_audit.txt` / `pd_findings.json` sitting in the workspace.**
   The README does not mention them; a naive user could paste those as "the result". I regenerated
   and compared digests (command 22). Judgement call, undocumented.
7. **What to do about `NOT_RUN` on PD004.** Decided to leave it: I don't know whether the manifest
   *should* have contained a comparative claim. Gave up.
8. **Whether the two `FAIL`s are the paper's fault or the manifest's.** Decided I cannot tell from
   the tool's output alone (see below); the manifest's own comments are the only hint, and reading
   YAML comments is not an audited channel. Gave up.

## Validation or input errors I hit

1. Missing paper corpus (the blocker), on **stderr**, exit **2**:
   ```text
   P_UNRESOLVED_REF at _registry/paper/root: ..\acceptance-inputs\tabm-arxiv\src is not a directory
   ```
   Did it tell me what to do? **Partly.** It names the offending manifest field and the path, but it
   (a) prints the *declared* relative string rather than the absolute path it tried — read from the
   repo root that path points outside the repo, which sent me hunting in the wrong place; (b) reuses
   the code `P_UNRESOLVED_REF`, which the README documents (line 115) as a *claim-text/line-number
   mismatch* error, so I first thought the manifest's claim locators were wrong; and (c) has no row
   in the README's exit-code table, which only offers "manifest is not a readable contract, or the
   path is wrong" for exit 2. No hint that a fetch script exists.
2. Typo'd workspace, exit **2**:
   ```text
   P_UNRESOLVED_REF at <scratch>\clone1\phase3\tabmm: no readable manifest is present at this path
   ```
   Good: absolute path, states the problem, matches README's "a wrong path is reported as a wrong path".
3. Folder with no manifest, exit **2**:
   ```text
   P_UNRESOLVED_REF at <scratch>\clone1\phase3\paper-doctor.yml: no readable manifest is present at this path
   ```
   Good — it shows the implicit `folder/paper-doctor.yml` it used.
4. `--json` into a non-existent directory, exit **1**, unhandled exception:
   ```text
   Traceback (most recent call last):
     File "<frozen runpy>", line 198, in _run_module_as_main
     File "<frozen runpy>", line 88, in _run_code
     File "<scratch>\clone1\.venv\Scripts\paper-doctor.exe\__main__.py", line 7, in <module>
       sys.exit(main())
                ~~~~^^
     File "<scratch>\clone1\src\paper_doctor\cli.py", line 178, in main
       write_json(list(findings), args.json)
     ...
   FileNotFoundError: [Errno 2] No such file or directory: 'nope\\deep\\r.json'
   ```
   Did it tell me what to do? **No.** Correct behaviour per README's exit-code table (1 = tool
   failed), but a one-line "parent directory does not exist" would have saved a traceback. Side
   effect I should flag honestly: the traceback leaked `src/paper_doctor/*.py` filenames into my
   terminal. I did not open those files.
5. No validation or manifest-schema errors otherwise: my run never touched `sha256`/`size` mismatch
   paths, and I did not try to make the manifest invalid on purpose.

## Steps and time to my first successful audit

- Shell commands: **34** across 20 tool calls (commands 1-19 are pre-first-audit; 16 is the failing attempt).
- Files opened: **4** (`README.md`, `pyproject.toml`, `phase3/tabm/paper-doctor.yml`,
  `scripts/fetch_acceptance_inputs.py`), plus ~8 directory listings and 2 `--help`/JSON inspections.
- Wall clock: **~9 minutes**. The first successful audit was reached after ~5 minutes.
- Where the time actually went: **~10 s** install (`pip install -e .`), **~3 min** discovering that the
  TabM paper source was missing and hunting for the fetcher (README silent, no `INSTALL`/quickstart,
  error message misleading), **~1-2 min** arXiv download + sha256 verification, **0.45 s** the audit
  itself, and the remaining ~3 min reading the listing and poking the JSON to work out what PD004-PD006
  even check. Install and compute were free; **documentation discovery was the entire cost**.

## My understanding of the five statuses

- **`PASS`** — this one rule, on this one claim, found the declared link and the narrow relation it
  checks in agreement with the evidence already on file. It says nothing about the sentence being
  true, well-supported, or the table being correct; e.g. `PD001 PASS C6` only means "C6's declared
  links point at things that exist". Action: nothing; move on. **Stated in docs** (README table +
  `--help`), and the "nothing more" wording is honest.
- **`FAIL`** — a specific rule found a specific mismatch between what the claim states and what the
  linked evidence prints. Action: go read that claim and that cell and decide yourself who is wrong
  (the paper, or the manifest's declaration) — the tool will not say. Example: `PD003 FAIL C8` tells
  me the sentence says 16281 while the cell it was pointed at says 26048, and the manifest's own
  comment says that link was *deliberately* pointed at the wrong column. **Stated in docs** that
  FAIL ≠ "the paper is false", but the "is the declaration at fault?" half is **still unclear**.
- **`INCONCLUSIVE`** — the tool could not decide with what is on file, usually because the author
  declared nothing, or because the address has more than one legitimate reading. Action: add the
  missing declaration (a link, a `block=` qualifier, a resolved label) and re-run; not an error and
  not a clean result. Example: `PD003 INCONCLUSIVE C9` — 'Maps Routing' is printed on two rows and
  nothing in the source separates them. **Stated in docs**, and README's `qualifiers` section does
  tell you the remedy for the block case.
- **`NOT_APPLICABLE`** — this rule was pointed at a target that has no such relation to check, e.g.
  every `PD007` line here because no claim declares a `same_as` pairing. Action: usually none, unless
  you expected the relation to exist. **Stated in docs**; the 14 occurrences made me briefly wonder
  if I had mis-declared something — the docs don't distinguish "correctly absent" from "you forgot".
- **`NOT_RUN`** — the rule had nothing of the class it reads to iterate over at all: `PD004 NOT_RUN
  rule:PD004`, "claims, links is populated, but nothing in it carries the key PD004 reads". Action:
  unknown — is it "your paper has no comparative claims" or "you failed to declare them"? The JSON
  shows `n_objects: 20, n_targets: 0` but not *what key* was missing. **Still unclear**; README's
  one-liner is the only definition available, and `P_...`-style guidance is absent.

## Ambiguities and places I had to guess

1. **"Install: `pip install -e .`"** — three lines, no venv advice, no Windows note, no "this repo
   needs a paper corpus fetched before any workspace will audit". The single missing prerequisite
   cost me the whole blocker.
2. **README line 34: "From the manifest above:"** — the sample output block sits *before* the sample
   manifest, so the sentence points at nothing. Worse, the sample output shows
   `PD001 PASS C1 ... form=COMPARATIVE ... links=[L1]` and a `PD004 FAIL C1`, while the sample
   manifest immediately below declares `C1 ... form: NUMERIC_ATTRIBUTION`. The worked example
   contradicts the example manifest; I could not tell which one was authoritative.
3. **`root: .  # optional; holds the paper's source files`** — no statement of what the path is
   relative to, and no example of a non-`.` root (the TabM manifest uses a `../../..`-style root that
   lands outside the workspace, which feels unusual enough that I questioned whether the manifest was
   broken).
4. **"a `NaN` upstream stays undetermined here"** and **"`upstream reports 1 RD002 findings and no
   exclusions on any of them`"** (`PD005 NOT_APPLICABLE C4`) — I could not map "undetermined" onto
   any of the five statuses; `NOT_APPLICABLE`'s reason reads like a fact, not like a judgement about
   the claim. Also `RD002` appears in the output and in the manifest's `target_ref` but is nowhere
   explained in the README.
5. **Rule ids are undocumented.** The README names PD001-PD007 only in passing (`--help` says "run
   PD001-PD007"); there is no table of what each rule checks, which statuses each can return, or what
   manifest content each rule requires. I recovered the questions from the JSON's `question` field,
   which the README also never mentions.
6. **`not_audited_reason`** — README: "A sentence Paper Doctor must not judge is declared with
   `not_audited_reason` instead of a form." No example, no allowed values, no statement of which
   status it produces.
7. **`quantifier: numeric` and `scope:`** (used by C7 in the TabM manifest) — the manifest schema
   section documents `form`, `target_kind`, `qualifiers`, `locator`, but not the `scope` block or
   `universe_status: PARTIAL`, which is precisely what produced `PD002 INCONCLUSIVE C7`.
8. **Exit-code table vs reality** — "2 = the manifest is not a readable contract, or the path is
   wrong" does not cover "a registry entry points at a missing file", which is the single most likely
   first-run error in this repo.
9. **`--json` semantics** — does it suppress the human listing? (No.) Does it create parent dirs?
   (No — it crashes.) Is `report.json` relative to CWD or the workspace? (CWD; undocumented.)
10. **No `paper-doctor validate` / `init` subcommand mentioned** — the only way to sanity-check a
    manifest is to audit it, which conflates manifest problems with claim problems.

## What I could not tell from the output

- **Is the TabM paper trustworthy? No signal, and I think that's by design rather than a gap.** The
  README is explicit: "It produces no score and no verdict about the paper" / "What it will not do:
  No aggregate score, no 'the paper is unreliable'". My totals — 10 PASS, 2 FAIL, 5 INCONCLUSIVE,
  14 NOT_APPLICABLE, 1 NOT_RUN out of 32 findings — are a count over **9 hand-declared claims** in
  one manifest, not over the paper. The paper has hundreds of sentences; nothing in the output says
  how many were declared, so 2/32 could equally describe a paper with 2 problems or a paper with 200.
  I genuinely cannot distinguish "this paper is solid" from "this manifest audited 9 sentences of a
  40-page paper".
- **Whether a `FAIL` blames the paper or the manifest.** `PD003 FAIL C8` compares `16281` against the
  `# Train` cell of row `Adult`. `16281` is Adult's *test* size, so either the paper mislabels or the
  declaration deliberately points at the wrong column. Only a YAML comment in `paper-doctor.yml`
  (lines 83-85, "Negative control ... declared against the WRONG column") tells me the second — and
  that's the author's comment, not evidence the tool checked. `PD006 FAIL C2`
  ("`8` ... is printed in table:4, table:7, table:9, table:11, table:14, table:15, table:16,
  table:17") is, to me, indistinguishable from a false alarm: the numeral exists in eight other
  tables, and the rule is essentially "does the referenced float print this literal".
- **Coverage.** No statement of what was *not* declared; `C3` (`$28$ datasets from \cite{...}`) with
  `links: []` gets `INCONCLUSIVE` — fine — but there is no "9 of an estimated N claim-bearing
  sentences were declared" figure, so I cannot tell an audit from a sample.
- **Whether `NOT_RUN` on PD004 means the paper contains no comparative claims**, or this manifest
  contains none. TabM plainly contains comparative sentences; so a `NOT_RUN` here tells me about the
  manifest, not the paper — but the output never says so.
- **Whether `findings.json` is itself sound.** README: "never re-audits it", "cannot raise the
  certainty of an upstream finding". So `PD001 PASS C7` inherits Result Doctor's authority, and the
  Paper Doctor output gives me no way to see that dependency as a caveat on the printed status.
- **Upstream/downstream identity.** `PD005`/`PD006` mention `table:4`, `table:5`, `RD002` — opaque
  ids with no crosswalk printed. I could not map `table:4` back to a `\autoref` label name from the
  output alone.

Honest reaction: as an ML engineer deciding whether to cite TabM, this run tells me the *wiring* of
9 declared claims is mostly consistent, and that two of them disagree with the cells they were
pointed at. That is a documentation-integrity check on a manifest, not a correctness verdict on the
paper — and the docs say so repeatedly, which I respect. But it means I still have to read the paper
myself, and the tool offers me nothing that ranks or prioritises what to read next.

## What would have made this faster

1. **A "prepare the workspaces" section in the README, before "Use"**, saying: a fresh checkout has
   no paper source; run `python scripts/fetch_acceptance_inputs.py <name>` (or `--list` to see state)
   before auditing `phase3/tabm`. This one block is the difference between 5 minutes and 1.
2. **Fix the missing-root error to name the resolved absolute path and the remedy**, e.g.
   `...\src is not a directory — run python scripts/fetch_acceptance_inputs.py tabm`, and give it its
   own exit-code row instead of reusing `P_UNRESOLVED_REF`, which the README already assigns to
   claim-text/line mismatches.
3. **A rule table (PD001-PD007): question, what manifest content it reads, which statuses it can
   return.** Today the only route is `--json` and its undocumented `rule_name`/`question` fields.
4. **Correct the worked example** at README lines 34-45: the manifest it refers to is *below*, and its
   `form=COMPARATIVE` / `PD004 FAIL` for `C1` contradicts the sample manifest's
   `form: NUMERIC_ATTRIBUTION`. Add a real, runnable example workspace instead.
5. **Document `--json` edge cases** (CWD-relative output, no parent-dir creation, listing still goes
   to stdout) and turn the `FileNotFoundError` traceback into a one-line exit-2 input error.
6. **Document the manifest fields the shipped workspaces actually use**: the `scope:` block
   (`stated_count`, `unit`, `universe_status: PARTIAL`), `quantifier`, `not_audited_reason` values,
   and what `RD002`/`table:N` id forms mean.
7. **Windows/venv install commands** (`.venv\Scripts\pip install -e .`, `.venv\Scripts\paper-doctor`)
   and a `paper-doctor --version`-style "you are on 0.1.dev0, this is not a released artifact" note.
8. **A coverage footer in the listing** — "9 claims declared, N links, 1 rule not run for lack of
   targets" — so a reader cannot mistake a manifest audit for a paper verdict.

## Verdict

**COMPLETED AFTER GUESSING**

Install, audit, JSON export and the five statuses all landed, and the deterministic byte-identical
output held, but only because I found an undocumented fetch script by listing `scripts/` after a
misleading exit-2 error; nothing in the README told me the TabM corpus had to be downloaded first.
I also guessed at Windows venv paths and had to reverse-engineer the rules from undocumented JSON
fields, and I am still left unable to say whether the two `FAIL`s indict the paper or the manifest.
