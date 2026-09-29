# Paper Doctor — Phase 2 report

Date: 2026-09-29
Authority: `phase0/PAPER_DOCTOR_PHASE0_REPORT.md` (body frozen, ERRATUM A1–A5 applied), Phase 1 close report,
and the Phase 2 brief (`GENERIC WORKFLOW + DETERMINISTIC TABLE DISAMBIGUATION + CLI`).
Scope of this round: implementation and generalization only. No claim taxonomy, rule set, object model,
validation namespace, or Result Doctor contract was reopened.

---

## 1. A5 erratum confirmation

A5 was applied before any Phase 2 code was written, and no full Phase 1 rerun was performed for it (as A5
instructs). The executable universe count for the D2/D3 census is **2**, `unit=aggregation`; the superseded
"PARTIAL 3/11" reading is no longer asserted anywhere in the tests, fixtures or source comments.

Verified by re-reading the frozen corpus and by `tests/test_acceptance_rtdl.py` still passing with the A5
expectations (`Phase 1 anchors unchanged`, §10 below).

## 2. Block discriminator design

Block discrimination is an **addressing** capability, not a new scientific object (Phase 2 §2).

* No new object: the block is carried as fields on the existing `TableRow` / `TableGrid` —
  `block_key`, `n_label_columns`, `block_evidence` — plus a parser-internal `_Segment`.
* No new PD rule, no PD008, no `P_13`, no new claim class. Re-verified at close:
  **7 rules** (`PD001`–`PD007`), **12 `P_*` codes**, **5 locator key sets**, **3 link target kinds**
  (`FLOAT`, `RD_TARGET`, `PROSE`), **6 claim forms**, 3 `ScopeUnit` values.
* No new manifest field. A declaration uses the existing free-qualifier mechanism, exactly like
  `comparison_basis`:

  ```yaml
  qualifiers:
    - {kind: comparison_basis, statement: per_column}
    - {kind: comparison_block, statement: block=b2}
  ```

* Signals that open a block (all source-stated, Phase 2 §1):
  1. a full-width `\multicolumn{N}{c}{...}` group header;
  2. a depth-0 rule (`\midrule`, `\hline`, `\cline`, `\cmidrule`, `\bottomrule`) leading a row — rules
     inside a nested group are ignored;
  3. a leading vertical merge (`\Block{R-C}{...}`, `\multirow{R}{...}{...}`) spanning more than one row,
     which additionally states how many label columns the table has.
* Nothing forbidden is used: no LLM, no embedding similarity, no caption reading, no method-name
  guessing, no numeric nearness, no layout inference beyond the source, no per-paper exceptions. A
  source sweep confirms no pilot-corpus filename, label or cell literal appears in `src/` (only
  explanatory comments mention GMMVI/RTDL).
* Identity: `(table_label, block_key, row_key, column_key)`. `block_key` is `b1`, `b2`, … in source
  order, **local to its float** — proven by the two-table fixture in §11.

## 3. RTDL Table 4 oracle (`tests/test_block_oracle.py`)

Frozen corpus `phase0/sources/2106.11959.tex`, `data/table_nn_gbdt.tex`, `tab:nn-gbdt`.

* `n_blocks == 2`; rows in source order:
  `(XGBoost,b1) (CatBoost,b1) (FT-Transformer,b1) (XGBoost,b2) (CatBoost,b2) (ResNet,b2) (FT-Transformer,b2)`.
* `grid.row("XGBoost") is None` while `grid.blocks_for("XGBoost") == ("b1","b2")` — a label printed
  twice resolves to neither until a block is declared. `ResNet` (printed once) stays addressable with
  no declaration.
* Basis strings name the printed group headers and their source lines:
  `b1` ← `multicolumn group header "Default hyperparameters" … data/table_nn_gbdt.tex:5`;
  `b2` ← `… "Tuned hyperparameters" … :11` plus the `midrule` that closes `b1`.
* Cells per block: `FT-Transformer/YE` = `8.727` (b1) vs `8.751` (b2); `XGBoost/AL` = `0.924` (b1) and
  `--` (b2) — a missing value stays missing, is never coerced to 0, and does not drop the row.
  `grid.row("XGBoost","b9") is None`: a name the source does not carry selects nothing.

## 4. GMMVI Table 8 oracle

Frozen corpus `phase0/sources/2209.11533v2.tex:1014`, `tab:exp3_full`, set in `NiceTabular`.

* `n_blocks == 11`, opened by eleven `\Block{2-1}{\thead{…}}` merged leading cells separated by `\hline`.
* `n_label_columns == 2` — read off the merge geometry, and the value columns are the nine model names
  (`Samtrux` … `Zamtrux`); `n_rows_dropped == 0`.
* Row labels per block (transcribed from `arxiv.tex` lines 1031…1261, not from the parser):
  `-ELBO` appears in all eleven blocks (so `grid.row("-ELBO") is None`), `MMD` in `b1`–`b5`,
  `Modes` in `b6`–`b9`, `MSE` only in `b10`, `H(q)` in `b11`.
* Cells per block: `-ELBO/Samtrux` = `78.01` (b1), `79.66` (b2), `585.10` (b3); `MMD/Samtrux` = `1.1e-03` (b1).

**§4 gate: neither table needed a STOP.** Both are deterministically disambiguable from source structure
alone, so PD004 was integrated; no semantic inference was introduced.

## 5. Parser regression results (`tests/test_tabular_grammar.py`, 17 tests)

Phase 1 parser disciplines are re-asserted, each with a test that fails if the discipline is relaxed:
leading negative signs (`$\mathbf{\num{-24.32}}$` → `-24.32`); escaped `&` is not a column boundary;
brace nesting and a rule inside a nested group are not block boundaries; `\multicolumn` boundaries
(partial-width spans open no block, and such a row is counted as dropped rather than re-topologised);
source line anchors (`locate` rebasing yields `midrule at paper.tex:4` / `:6`); `--` stays a missing value;
`\rotatebox{65}{\sc …}` / `\thead{… \\ …}` arguments are not read as cell content. The parser is still a
tabular reader, not a general TeX engine (Phase 2 §5).

## 6. Generic manifest contract (`README.md`, `src/paper_doctor/manifest.py`)

The manifest stays the Phase 1 shape: `schema_version` plus the four frozen sections in order
(`_registry`, `_claims`, `_floats`, `_links`), the five frozen locator key sets, the three link origins,
12 validation codes. The three frozen link origins are unchanged; a declaration establishes provenance,
never correctness. Path resolution: paper paths are relative to `_registry.paper.root` (itself relative
to the manifest's directory); the upstream artifact is resolved relative to the manifest.

## 7. CLI contract

`paper-doctor audit PATH [--json REPORT_JSON]`, `--version`.

`PATH` is a manifest file, or a directory — and a directory means exactly `<dir>/paper-doctor.yml`.
There is no recursive manifest discovery: with the manifest one subfolder deeper, the command reports
the path it tried and exits 2 rather than auditing the tree the user did not point at.

The human listing prints, per finding, the rule id, status and target, then the claim's declared form,
its source locator and its link ids, then the full reason (never truncated). The presentation fields are
joined from the bundle at print time; `RuleFinding` still carries Contract I-1's eight keys, and a test
asserts that the listing adds nothing to the payload it prints.

## 8. Exit codes

| Code | Meaning | Proven by |
| --- | --- | --- |
| `0` | the audit ran, whatever it found — including `FAIL` | `test_a_misattributed_reference_fails_and_the_command_still_exits_zero`, `test_a_block_failure_still_exits_zero` |
| `2` | the manifest is not a readable contract, or the path is wrong | `test_an_unreadable_contract_exits_two_and_prints_the_frozen_message`, `test_a_directory_is_never_searched_for_a_manifest` |
| `1` | Paper Doctor itself failed unexpectedly | `test_an_unexpected_failure_exits_one_and_never_claims_to_have_finished` (real subprocess; no census is printed) |

A missing/unreadable manifest file is an input error, not a crash: it now raises
`P_UNRESOLVED_REF` and exits 2 (the same code the corpus uses for a declared file that is not there).

## 9. Deterministic JSON

Unchanged serialization contract: sorted keys, fixed separators, `ensure_ascii=False`, no timestamps, no
random ids, fixed rule order, `newline="\n"`. Phase 2 extends the proof from the API payload to **both
output faces**: `test_both_output_faces_are_the_same_bytes_under_every_hash_seed` runs the CLI in three
separate interpreters with `PYTHONHASHSEED` 0, 1, 424242 and compares stdout bytes and `--json` bytes.
The listing is the surface assembled from a dict, so it is the one that needed this test.

## 10. Real acceptance regression (Phase 2 §14)

All Phase 1 frozen anchors are unchanged and green: GMMVI `C1` PD006 FAIL, `C5` PD002 INCONCLUSIVE,
`C6` PD005 FAIL; RTDL `D1` PD003 INCONCLUSIVE, `D5` clause 1 FAIL + clause 2 INCONCLUSIVE, `D6` PD004
FAIL with 1/8 counterexample, `D7` PD001 PASS + PD006 PASS + PD002 INCONCLUSIVE, `D8` INCONCLUSIVE,
`D11` PD007 FAIL. 17 RTDL + 12 GMMVI acceptance tests pass, 0 skipped.

New Phase 2 proof (`tests/test_block_rules.py`, 10 tests): the sentence at `main.tex:404`
(`the ensemble of \architecture s mostly outperforms the ensembles of GBDT`) over RTDL Table 4 —

* no block declared → PD004 **INCONCLUSIVE**, reason naming both blocks and what separates them;
* `block=b1` → **PASS** with `n_columns_in_scope=11`, 10 supported, 1 counterexample (AD 0.860 vs 0.874),
  reason quoting `multicolumn group header "Default hyperparameters" at data/table_nn_gbdt.tex:5`;
* `block=b2` → **INCONCLUSIVE**, `1 of 11 columns have no declared direction or no numeric cell` (AL
  prints `--`), reason quoting `"Tuned hyperparameters" … :11`;
* `block=b9` → **INCONCLUSIVE**, `block 'b9' prints no row addressed by …`.

Every reason carries its unit (`unit=comparison_member`, `unit=reported_cell`, `unit=aggregation`) and the
structural clause that selected the block — Phase 2 §13. No verdict depends on which block the parser
reached first.

## 11. Unseen generic workflow test (Phase 2 §15)

Three synthetic, previously unused fixtures — none of them GMMVI, RTDL, or the excluded paper — each
audited end to end through the real manifest, bundle and CLI/library API:

1. **Two `\multicolumn` blocks** (`tab:twoblock`): the same claim is PASS under `b1` and FAIL under `b2`,
   with the counterexamples quoted per column and direction.
2. **NiceTabular `\Block{2-1}` twin** (`tab:merged`): the merged leading cell alone opens the blocks;
   `b1` PASS, `b2` FAIL, undeclared INCONCLUSIVE quoting both merged cells.
3. **Two tables in one paper** (`tab:size`, `tab:budget`): `block=b2` decides the claim PASS in the first
   and FAIL in the second, and each reason names only its own group header — block identity is local to
   the float that states it.
4. **PD003 over a two-block table**: `(column=Acc, row=Ours)` is printed twice, so agreement is only
   decidable per block — `b1` PASS, `b2` INCONCLUSIVE with `0.42 vs the printed 0.38`, undeclared
   INCONCLUSIVE.

## 12. Phase 1 firewall regression

`tests/test_pd_firewall.py` (43 tests) plus the Phase 1 adversarial matrix, manifest-validation, RD-contract,
audit, and both float-oracle suites are all green. Contract I-1 was not expanded: one RD artifact, zero
`result_doctor` import, hash/size verified before read, `NaN` stays NonFinite/UNKNOWN, certainty never
increased, and no historical research-round observation (A1 9/46, A5 3/11) was recovered.

## 13. Phase 2 firewall additions (`tests/test_phase2_firewalls.py`, 6 tests)

| Brief requirement | Test |
| --- | --- |
| repeated row labels cannot be resolved without an explicit structural block | `test_a_repeated_label_carries_no_verdict_until_the_source_structures_it` |
| block identity cannot come from numeric value | `test_replacing_every_number_leaves_the_block_structure_untouched` (two tables with no digit in common share block keys, labels and bases; only the real source offsets shift) |
| block identity cannot come from caption interpretation | `test_the_caption_is_the_only_difference_and_the_basis_names_only_geometry` |
| a manifest declaration cannot override contradictory deterministic structure | `test_declaring_a_block_never_moves_a_row_that_the_source_put_elsewhere`, `test_a_stale_block_declaration_is_used_as_given`, `test_a_statement_that_names_no_block_declares_no_block` |
| CLI scientific FAIL returns exit 0 | `test_a_block_failure_still_exits_zero` |
| validation error returns exit 2 | `test_a_directory_is_never_searched_for_a_manifest` (+ Phase 1 exit-2 test) |
| JSON deterministic across hash seeds | `test_both_output_faces_are_the_same_bytes_under_every_hash_seed` |

No new research taxonomy was created.

## 14. Test count

**235 passed, 0 failed, 0 skipped** (`python -m pytest -q`), up from Phase 1's 196. Phase 2 additions:
block oracle 10, tabular grammar 17 (incl. new cases), block rules 10, Phase 2 firewalls 6, CLI 12
(incl. 5 new), plus the A5-targeted erratum tests.

## 15. Quality gates

`ruff check .` → All checks passed. `ruff format --check .` → 30 files already formatted.
`mypy src` → Success: no issues found in 10 source files. No writes to Dataset Doctor / Experiment Doctor
/ Result Doctor (this round touched only `F:\MLResearch\paper-doctor`). No tag, no push, no release, no PyPI.

## 16. Fresh-user proxy workflow (Phase 2 §19)

A zero-context workspace was built in a clean venv using only the README: `pip install -e .` (installed
`paper-doctor 0.1.dev0` + PyYAML), then a hand-written `paper.tex` (two `\multicolumn` blocks),
`findings.json` (`result-doctor audit … --json` shape, empty array), and `paper-doctor.yml` copied from the
README skeleton, with digests from the README's own `sha256sum` / `wc -c` commands.

`paper-doctor audit .` ran and exited 0, printing PD001 PASS, PD003/PD005 INCONCLUSIVE, PD004 **FAIL**
naming `block=b2 [midrule at paper.tex:15; multicolumn group header "Tuned configuration" at paper.tex:16; …]`,
PD006 PASS/INCONCLUSIVE, PD007 NOT_APPLICABLE, and the five-status census. `--json` wrote the canonical
report. With the block declaration emptied, the same audit produced PD004 INCONCLUSIVE listing both blocks
and their separators. From the README alone the user can determine: how to run the audit, how to request
JSON, what PASS/FAIL/INCONCLUSIVE mean, and that no overall paper verdict exists.

Three findings came out of the dry run and were fixed rather than noted:

1. `block=` (an empty or prose statement) was being read as a block *named* `block=`, producing
   "no row addressed by" where the right answer was "no block is declared". `_declared_block` now treats a
   statement that carries no block name as undeclared; `block=b7` is still honoured literally.
2. The ambiguous-row reason ended "…and no block is declared" while starting "the declared subject…",
   which reads as a contradiction; it now reads "…; the claim declares no block".
3. The README did not say which line a wrapped sentence is declared at, and its output sample was
   invented rather than real; both were corrected, and the form list was fixed to the six frozen forms.

This is a proxy, not human onboarding — which belongs to the release phase.

The workspace is archived at `phase2/dryrun/` (`paper.tex`, `findings.json`, `paper-doctor.yml`, the
no-block variant `no-block.yml`, and the canonical `report.json` it produced), and it still reproduces
against the frozen tree: the declared run exits 0 with PD004 FAIL naming `block=b2`, the no-block variant
exits 0 with PD004 INCONCLUSIVE listing both blocks.

## 17. Limitations

* **Cross-block comparison is not expressible.** One `comparison_block` declaration addresses both
  subjects, so "metric M in setting A vs the same metric in setting B" cannot be judged yet. That is
  exactly the shape GMMVI Table 8's intended comparison has (its rows are metrics, its blocks are
  settings). The oracle therefore proves Table 8's *addressability*; no PD004 verdict is asserted on
  Table 8, because the paper makes no row-level comparative claim there that could be declared without
  inventing one — and an invented claim is not evidence. Per-subject block addressing is a design
  decision for Phase 3, not something this round silently extended.
* Block names are positional (`b1`, `b2`), so a table edited upstream renumbers them. The manifest's
  paper digest is what pins them to the audited bytes; there is no content-addressed block id.
* A non-`.tex` paper root yields no float index, and the rules say so instead of guessing (unchanged).
* `audit_manifest` accepts a rule subset for partial audits, but the CLI exposes no rule-selection flag;
  every rule runs and reports `NOT_RUN` when its target class is absent. Phase 2 §9 asks for
  independence, not for selection, so this was left as-is.
* The two pilot corpora remain regression fixtures, not validation sources. The excluded paper is
  excluded permanently (§18).

## 18. Excluded-paper rule (Phase 2 §16) — frozen as a project rule

`EXCLUDED PAPER = EXCLUDED FROM PAPER DOCTOR VALIDATION`, for all phases: design, implementation,
validation, acceptance, benchmarking, release gating. It is not used in Phase 2, is not planned for
Phase 3, and is not named as a future acceptance candidate. Final end-to-end acceptance must use an
external third-party paper. Recorded in project memory as well as here.

The excluded paper is one of the author's own unpublished submissions. Its title is withheld from this
public record on purpose: what is frozen here is the *rule*, not the *name*, and the rule is fully
checkable without the name — no design decision, test, fixture, corpus, or acceptance target in this
repository can be traced to it. The name is known to the author and recorded outside this repository.
(Redaction applied before the first public commit; see `release/RC_AUDIT.md`, "Public-surface policy".)

## 19. Phase 3 exact scope (proposal; not started)

Phase 2 does not decide Phase 3. What Phase 3 would consist of, in one line each:

1. Final end-to-end acceptance on one **external third-party paper** selected by the user, as a full
   claim-universe pass with frozen anchors written before the run.
2. The open addressing decision from §17: whether per-subject block declaration enters the existing
   `comparison_block` qualifier mechanism, or cross-block comparison stays out of scope.
3. Release-phase work owned by the frozen Phase 2 exclusions: real fresh-user onboarding, packaging,
   and distribution — none of which is Paper Doctor science and none of which was done here.

## Close conditions (Phase 2 §22)

| Condition | State |
| --- | --- |
| A5 applied | MET (§1) |
| block discriminator deterministic | MET (§2, §13) |
| RTDL Table 4 uniquely addressable | MET (§3) |
| GMMVI Table 8 uniquely addressable | MET (§4) |
| no semantic linker introduced | MET (§2, §13) |
| generic manifest works | MET (§6, §11, §16) |
| CLI works | MET (§7, §16) |
| `--json` deterministic | MET (§9) |
| exit codes correct | MET (§8) |
| Phase 1 anchors unchanged | MET (§10) |
| Phase 1 firewalls unchanged | MET (§12) |
| new block/CLI firewalls green | MET (§13) |
| unseen generic fixture succeeds | MET (§11, §16) |
| quality gates green | MET (§14, §15) |
| deterministic addressing impossible → STOP | NOT TRIGGERED |

## Verdict

**GO for Phase 3** — with Phase 3 scope, and the choice of acceptance paper, left to the user.

STOP after this report: no Phase 3 code, no repository, no publication, no PyPI.
