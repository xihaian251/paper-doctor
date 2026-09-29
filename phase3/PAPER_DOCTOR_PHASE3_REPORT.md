# Paper Doctor — Phase 3 final report

Phase 3 of 3. Acceptance target: **TabM: Advancing Tabular Deep Learning with Parameter-Efficient
Ensembling** (ICLR 2025), `https://github.com/yandex-research/tabm`. This report covers brief §0–§29.
Every number in it was produced by running the named command; where something was searched for and not
found it says `SEARCHED / NOT OBSERVED`, and where a gate was not met it says so rather than re-scoping it.

Working verdict: **the four-layer chain closes, the generalization claim is proven by construction and by
firewall, and the release stops only at the one precondition this environment cannot supply — a human.**

---

## 0–1. Acceptance target, and the exclusion that frames it

| input | pinned value |
| --- | --- |
| paper | TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembling, ICLR 2025 |
| arXiv | 2410.24210, tarball sha256 `cdcea2ddbe710fa6e9c19b0e611e0c82dd513491aa6ac680368ed5bc3127db8c` |
| entry point | `main.tex`, 88,033 bytes, sha256 `15663553d04fcbb8b3341df5c0d269c7703d4ba279be557fcd77ea4765ab0a62` |
| code repository | `yandex-research/tabm` @ `28e47ae301c92ec37787dde1ce923a0793f405b4`, read-only checkout, paper subdirectory `paper/` |
| external input to PD | `phase3/tabm/findings.json`, 12,392 bytes, sha256 `c56b62623b39ed9a4c311f8bcc6be6de457c1a0f8a4d34d3da99a4b71c7d2774` |
| PD workspace | `phase3/tabm/paper-doctor.yml`, 7,391 bytes, sha256 `7e809014f0fa5019622fcec5280cec2f1d4f0e243f7cd3b156b7ebae3e009377` |

Phase 3 is the acceptance phase, not a design phase. Phase 0–2 were not reopened: no rule, no status
semantics, no `P_*` code, no schema key and no frozen anchor moved. The one paper permanently excluded from
Paper Doctor validation (design, implementation, validation, acceptance, benchmarking and release gating
alike) is the author's own unpublished submission; its title is withheld from every published file, which
`release/RC_AUDIT.md` §5 records as a deliberate redaction made before the first commit, and §4b's scan
confirms it appears nowhere in the published tree.

**The acceptance's real burden (§1): prove that no RTDL-specific hardcode or assumption was required.**
That is the subject of §6 and §12 below. It is answered twice: by construction (zero adapters, one generic
manifest, the same parser) and by tests that fail if a project name, value or digest ever appears in
executable code.

## 2. The chain that had to close

`phase3/tabm/end_to_end_chain.json` (19,875 bytes) records three chains. Chain 1 is the four-layer one and
runs, in order:

```text
paper claim C6/C7/C8 (main.tex / tables/app-rtdl-datasets.tex:8)
  → PD      32 findings, 08836ccf…
  → reported result  tabm/adult-seed3/test-score
  → RD      14 findings over 2 reported results + 1 aggregation, c56b6262…
  → aggregation agg:adult-seed-mean, 15 enumerated members (seed-3 one of them)
  → run     exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json
  → ED      ED001 NOT_APPLICABLE, ED002/ED003 PASS, ED004/ED009/ED010 INCONCLUSIVE, 2de48cc3…
  → dataset ds_05c7465f (official UCI Adult copies at the auditor-declared location)
  → DD      report c1456a7b…, fingerprint 1f0dd1a5… (13,013,232 B), tool_version 0.1.2
```

Four `joins` are recorded between the layers, each with its basis stated — two `AUTHOR_DECLARED`/
`AUDITOR_DECLARED` enumerations and two identity-of-artifact links. **No cross-layer similarity is
computed anywhere**: the ledger never claims the run "looks like" the claim, only that a declared address
points at it. That is the Phase 1 epistemic rule carried into Phase 3 unchanged.

## 3. Pre-flight, done first (§3)

`phase3/TABM_PREFLIGHT.md` (260 lines) precedes any acceptance work and answers the five feasibility
questions, all **YES**: A deterministic linkability (two counts in `main.tex` naming their float by
`\autoref` in the same sentence, resolved by the generic index, including the negative case where PD refuses
to count rows); B a reported result traceable for RD (15 per-seed `report.json` artifacts, aggregation
exactly reconstructible); C run/config/seed/environment traceable for ED; D dataset identity and split
traceable for DD; E doable with no RTDL-specific assumption.

It also records the caveat that shaped the whole phase: TabM's per-dataset metric values live in
`\begin{longtable}` inclusions with a caption and **no `\label`**, outside any `table`/`figure` float. The
frozen float set cannot address them, so **there is no paper-side printed locus for the Adult accuracy that
PD can audit**. PD's design was not extended to reach it (§13); the gap is in the ledger's `unknowns` as
`NOT REACHABLE`, and the value 0.8575 was deliberately *not* turned into a claim.

## 4. No large-scale reproduction (§4)

Zero training runs were executed. Experiment Doctor was run in `init`/`audit` mode over the shipped
artifacts with `--command` recorded but not invoked, and `n_runs_discovered_by_generic = 0` (measured twice,
below). The paper's numbers were not re-derived; the acceptance is about traceability, not reproduction.

## 5–6. Claim selection and the generic workflow (§5, §6)

Nine claims `C1`–`C9` were selected against the brief's criteria (printed value or count in the sentence, a
float or artifact addressable by the generic index, at least one in each of the three claim forms). The
selection uses **Phase 2's generic workflow only**:

- `adapters_written_for_tabm = 0` for PD, RD and DD; the ED layer used ED's own declared `captured` adapter.
- Link bases used: `AUTHOR_REF_IN_SENTENCE` and `AUDITOR_DECLARED` only (plus `AUTHOR_NAMED_FLOAT` where a
  sentence names its float). No new basis was invented for TabM.
- The manifest is the same four-section shape Phase 2's README documents; a test asserts the TabM workspace
  declares no schema key Phase 2 does not already know (`test_the_acceptance_declares_no_schema_key_phase_two_does_not_know`).
- `src/` was not modified during Phase 3 acceptance at all. The two Phase 3 code changes in this repository
  are `scripts/`-and-`tests`-level (fetch + onboarding), and the only `src/` edits in the release window
  were the seven documentation-surface P1 fixes recorded in `phase3/ONBOARDING_MEASUREMENT.md` §2.

## 7. Frozen anchors: unchanged (§7)

All of them, asserted in the suite that is green at 292: GMMVI `C1` PD006 FAIL, `C5` PD002 INCONCLUSIVE,
`C6` PD005 FAIL; RTDL `D1` PD003 INCONCLUSIVE, `D5` clause-1 FAIL with clause-2 INCONCLUSIVE, `D6` PD004
FAIL, `D7` PD001/PD006 PASS with PD002 INCONCLUSIVE, `D8` INCONCLUSIVE, `D11` PD007 FAIL; the Phase 2 Table 4
and Table 8 block oracles; `MULTI_TABLE_PAPER`; the closed-at-twelve `P_*` code set.

One anchor needed a *portability* fix, not a scientific one, and it is the phase's most consequential bug
(§14/RC_AUDIT P1-8): `tests/test_acceptance_rtdl.py` resolved its two inputs against `REPO.parent`, reading
the corpus through a workspace-relative path and the pilot transcript straight out of a sibling repository.
Locally green; in a clean checkout **17 frozen RTDL anchors errored** (measured: 271 passed, 17 errors).
Fixed by repository-relative paths plus vendoring the transcript as a byte-pinned fixture. No asserted
status changed — the same 17 anchors now pass for the same reasons.

## 8. Result Doctor layer (§8)

Public artifacts only; RD never imported by PD's tests (Contract I-1). `result-doctor audit
phase3/tabm/result-doctor.yml --json` produced **14 findings** over 2 reported results and 1 aggregation:
`INCONCLUSIVE 6, NOT_APPLICABLE 6, NOT_RUN 1, PASS 1`; per rule RD001 2, RD002 1, RD003 2, RD004 2, RD005 2,
RD006 2, RD007 1, RD008 2. `rd_code_modified = false`, `rd_rules_added = 0`, RD version 0.1.0.

## 9. Experiment Doctor layer (§9)

ED 1.0.0 over run `exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json`
(`phase3/tabm/ed-captured/`, report sha256 `2de48cc3…`): ED002/ED003 PASS, ED001 NOT_APPLICABLE,
ED004/ED009/ED010 INCONCLUSIVE.

`Do not pretend missing upstream experiment metadata exists` was honoured literally. The repository ships no
run-side bundle for the published runs — no effective configuration, no termination cause, no runtime
environment — so ED's environment rules stay INCONCLUSIVE. Two further statements the capture makes about
itself are recorded rather than smoothed over: the captured adapter **records no metric by design** and no
execution was performed, so the metric of record remains in the RD layer; and ED's `dirty = False` plus its
python/package fields **describe this capture machine (3.13.1, Windows-11), not the published run** —
`THEY DESCRIBE THE CAPTURE, NOT THE PUBLISHED RUN` is the ledger's own wording.

The generic discovery path was also tested, and it is a negative result: ED's generic mode found
**0 runs** in the TabM repository layout (`phase3/tabm/ed-generic-adult-runs/report.json`,
`phase3/tabm/ed-generic-whole-repo/report.json`). `SEARCHED / NOT OBSERVED: a run-side artifact inside exp/
that records the environment a published run executed under — none`, only `paper/environment.yaml`, which
states a requirement, not a fact. Reporting the zero is the point: the acceptance does not credit a
discovery mechanism that did not discover.

## 10. Dataset Doctor layer (§10)

DD's own CLI, unmodified, against the official prepared Adult files: `dataset_id ds_05c7465f`,
`config_hash cfg_091fd33c9ce94a35`, `manifest_hash 9bf9cea8ee536e96483be1e5a0efef44`,
`report.json` 56,359 B / `c1456a7b…`, `report.md` 35,308 B / `927c5ea5…`, `fingerprint.json`
13,013,232 B / `1f0dd1a5…`, `tool_version 0.1.2`, `eval_safety FORMAL_EVAL_INVALID`. Split sizes measured:
train 32,561 / test 16,281.

The 13 MB fingerprint is not committed; it is pinned by digest in the ledger and in
`phase3/tabm/dd/README.md`, whose regeneration command was re-run during the RC audit and reproduced both
the digest and the byte count exactly.

**The cross-layer arithmetic is an auditor observation, not a PD verdict.** `26,048 + 6,513 = 32,561`: the
paper's `# Train` column prints a hold-out of the official training file, not that file's record count. PD
compares a declared sentence against the address it points at and issues no verdict across DD and the paper,
so nothing here says the paper is wrong; the ledger records it as `AUDITOR OBSERVATION, NOT A PD VERDICT`.

## 11. The ledger is a document, not a model (§11)

`kind = paper-doctor/phase3-end-to-end-chain`, `ledger_version 1`, with two id conventions
(`<rule_id>@<claim_id>` for PD, `<rule_id>@<RD target string>` for RD), 8 `unknowns`, 2
`searched_not_observed` entries. No new runtime object model was created from it: PD's data model is
Phase 1's, the validator does not read this file, and the one test that consumes it
(`test_the_chain_ledger_still_describes_the_artifacts_it_records`) only re-checks the digests and statuses
it quotes.

## 12. Generalization firewalls (§12)

Eleven tests in `tests/test_phase3_firewalls.py`, all green, all mutation-checked:

| test | what it forbids |
| --- | --- |
| `test_every_module_under_src_parses` | the corpus of the rest |
| `test_no_project_name_appears_in_executable_code` | `tabm`, `rtdl`, `gmmvi`, `yandex` in any executable statement |
| `test_project_names_in_src_are_confined_to_comments_and_docstrings` | same, positively stated |
| `test_no_acceptance_value_or_digest_occurs_anywhere_in_src` | a frozen result value or corpus digest inside the tool |
| `test_src_carries_no_path_to_a_corpus_checkout` | any filesystem route from `src/` to an evidence tree |
| `test_the_package_imports_no_sibling_doctor` | importing `result_doctor` / `experiment_doctor` / `dataset_doctor` |
| `test_no_shipped_file_describes_this_machines_filesystem` | local path shapes in the shipped surface |
| `test_no_shipped_file_carries_a_credential_shape` | tokens, key material, keyed URLs |
| `test_the_privacy_patterns_themselves_detect_a_leak` | the gate's own efficacy (self-check, not a claim) |
| `test_vendored_third_party_bytes_are_still_what_they_were_pinned_as` | a silent edit to the one vendored fixture |
| `test_the_vendored_skip_is_narrow_and_widens_to_nothing_else` | that pin table growing |

Plus the Phase 1/2 firewalls, unchanged: closed 12-code set, no aggregate score, no LLM-as-judge anywhere,
canonical byte-deterministic JSON across hash seeds, `exit 0` on scientific FAIL.

Two of these firewalls earned their keep during this phase rather than in the abstract. The privacy gate's
skip is **digest-conditional**: when a vendored upstream fixture was silently rewritten (defect P1-9, the
project's own `ruff format` re-editing Python inside Markdown fences), the digest stopped matching, the skip
stopped applying, and the gate immediately reported the file it had been exempting. A whitelist would have
been edited into silence; a pin turns an exemption into a failure the moment the evidence moves.

## 13. No schema redesign inside final acceptance (§13)

Unstated changes were declined on evidence, not taste. The longtable-without-a-label gap (§3) and the
`# Train` arithmetic (§10) are exactly the places where a new schema key or a new rule would have "fixed"
the acceptance; both were recorded as UNKNOWN boundaries instead. `test_the_acceptance_declares_no_schema_key_phase_two_does_not_know`
is the mechanical form of that decision.

## 14–15. Onboarding, measured honestly (§14, §15)

Two fresh-agent walkthroughs of the release kit are recorded in `release/onboarding/RUN1_AGENT_LOG.md` and
`RUN2_AGENT_LOG.md`, with the analysis in `phase3/ONBOARDING_MEASUREMENT.md`. Seven P1 usability defects were
found and fixed; time from install to first successful TabM audit went from ~5 minutes (with a traceback) to
**65 s**, guessed steps from 8 to 2. Two more P1s (P1-8 clone portability, P1-9 the formatter rewriting
evidence) were found by mechanisms onboarding cannot see and are recorded in `release/RC_AUDIT.md` §7.

**§15 — one real human first-use test — is NOT OBSERVED.** `release/HUMAN_ONBOARDING_RECORD.md` lists all
thirteen §15 quantities as `UNKNOWN` and names the procedure that would fill them. Nothing substitutes for
it: the agent runs prove the kit is walkable by an agent, and the kit's own integrity dry-run (twice, most
recently against the current 305,805-byte generation at 16:5x) proves it is self-sufficient. Neither proves
a person can use it. This is the single unmet §23 precondition and it is why the release pauses at the
push/publish boundary for the user's decision, stated in `release/RC_AUDIT.md` §10.

## 16–17. CLI and README (§16, §17)

Package `paper-doctor`, import `paper_doctor`, version `0.1.0` from one source
(`paper_doctor.__version__`, read through `dynamic = ["version"]`). `audit PATH`, `--json`, `--version`,
`--help`; exit `0` = contract satisfied (a scientific FAIL exits 0 — verified by the TabM run, which prints
two FAILs and exits 0), `2` = input contract error, `1` = tool failure.

The README states what the tool does **not** judge (whole-paper truth, fraud, novelty, accept/reject, proof
correctness, whether a result reproduces, meaning in prose), states that `FAIL` is a disagreement between a
declared sentence and its address and never "the paper is false", and describes `PD006` as the
literal-presence test it is — including the case that motivated it, where a table enumerating eight rows
without printing the string `8` FAILs and that FAIL does not mean the count is wrong. The README's measured
numbers are current: its sdist-suite figures were re-measured against the final artifact (199 passed,
23 failed, 70 errors) and the wheel's embedded `METADATA` was checked to contain the new line and not the
old one.

## 18–19. License and artifacts (§18, §19)

Apache-2.0 after the dependency check (only runtime dependency PyYAML, MIT). Both artifacts built from the
final tree: wheel 67,768 B `192e3e17d7e405738632a5b222ca4610a35e0c55aae5a995fb91eccdab9a1887`; sdist
181,916 B `bfd3a87f7c7b20f73277bfb3bbd7223c208b3c9e2cfa208e45829d9cbcd0e30a`. Two earlier generations are
superseded and named as such in `release/RC_AUDIT.md` §2.

"No editable-install-only success is sufficient": each artifact was installed into its own fresh virtualenv
with plain `pip install`, checked with `pip check`, and run — both produced
`08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0` on `phase3/tabm`.

## 20. RC audit (§20)

`release/RC_AUDIT.md`. Four gates green (`292 passed`; `ruff check .`; `ruff format --check .` → 32 files;
`mypy src` → 10 files), reproduced in **two independent clean checkouts** of the same tree (§9 there), plus
the acceptance digest from a fifth route. Pre-publication scan of exactly what git would publish: 105
tracked files (re-run with this report in the tracked set), `blob_vs_worktree_drift=0`, 0 credential shapes,
0 account-name occurrences, 0 mentions of the withheld title, 0 binary files. **P0 = 0, P1 = 0**;
non-blocking register N1–N10. No global software quality score is computed anywhere, by tool or by this
report.

## 21–23. Repository, publishing, and the release decision (§21–§23)

`main` branch: the boundary commit `976bf0d`, the portability fix `7bdf47f`, and the docs commits that
record the RC audit measurements and this report. `release/` and `.github/workflows/` are tracked.
`.github/workflows/publish-pypi.yml` publishes on `release.published` with
`permissions: {contents: read, id-token: write}` and a `pypi` environment — **no long-lived token exists
or is stored**, per §22; the Pending Trusted Publisher must be created on PyPI before the public Release.
No tag exists yet: §21 makes the release commit immutable, so `v0.1.0` is created only once the decision
below is settled.

§23 authorises automatic release once its six conditions hold. Five hold: P0 = 0, P1 = 0, CI-equivalent
gates green in a clean checkout, the four-layer TabM acceptance complete, fresh wheel and sdist clean.
**One does not: human onboarding complete.** §27's stop list does not include "no human available", and §15
permits `UNKNOWN`, so this is a disclosed deviation rather than a fabricated closure — but it is also the
first irreversible external write, and the choice between *nominate a tester* and *waive §15 for 0.1.0*
belongs to the user. The release therefore halts here.

## 24–25. Executed after this report

`pip install paper-doctor==0.1.0` in a new venv, `pip check`, the frozen TabM acceptance run, and the
**actual downloaded** PyPI wheel/sdist SHA256 (not assumed equal to any local build) will be recorded in
`release/RELEASE_FREEZE.md`, together with the release commit, tag, tag peel, GitHub Release and the human
onboarding status as it stands. `v0.1.0` is never moved. §26's `ML_RESEARCH_FINAL_STATE.md` follows the
release, and §25's one docs-only post-release commit is that document plus this report's release section.

## 26–29. Scope statements

- Nothing in Phase 3 was measured on the excluded paper, and no benchmark, validation or release gate used
  it. It is not proposed as a future candidate.
- The four tools' statuses and the chain's remaining UNKNOWNs are enumerated in `ML_RESEARCH_FINAL_STATE.md`
  at release time; eight ledger UNKNOWNs and two `SEARCHED / NOT OBSERVED` entries are the Phase 3 list,
  quoted in §2, §3, §9 and §10 above.
- Paper Doctor does not judge the paper. On TabM it reports 32 findings — 10 PASS, 2 FAIL, 5 INCONCLUSIVE,
  14 NOT_APPLICABLE, 1 NOT_RUN — and the two FAILs (`C2` PD006, `C8` PD003) are disagreements between a
  declared sentence and the address it names. Neither is a claim that TabM is wrong, and this report does
  not make one.
