# Phase 0 evidence inventory — the frozen Result Doctor RTDL pilot

Object of study: what the Result Doctor 0.1.0 real-world generic pilot (paper *Revisiting Deep
Learning Models for Tabular Data*, NeurIPS 2021, arXiv:2106.11959; repo
`yandex-research/rtdl-revisiting-models` @ `e3ed46cac38568785289d8fa16b8cfa585bde27e`) actually
proves, and what it leaves untouched, for the design of **Paper Doctor** (auditing whether *paper
prose claims* faithfully represent reported evidence).

Mode: READ-ONLY. No existing file was modified. New files created by this inventory:
1. `F:\MLResearch\paper-doctor\phase0\work\rtdl-rd-inventory.md` (this file)
2. `F:\MLResearch\paper-doctor\phase0\work\rtdl-audit-from-pylib.json` (the `--json` artifact the task asked for)

All paths below are absolute unless prefixed by a section marker. Shorthand roots:

| shorthand | absolute |
|---|---|
| `PILOT` | `F:\MLResearch\result-doctor\phase4\rtdl-revisiting-models` |
| `SRC` | `F:\MLResearch\result-doctor\src\result_doctor` |
| `RD` | `F:\MLResearch\result-doctor` |

Measured with the frozen tree on 2026-09-29, `result_doctor.__version__ = "0.1.0"`
(`SRC/__init__.py:9`), Python 3.13.1 at `D:\python\python`.

---

## 0. Discrepancy ledger (read this first — four report claims do not match the tree)

These are stated loudly because Paper Doctor will inherit this pilot as its only real-world anchor.

**D-0.1 — `EVIDENCE_NOTES.md:51` quotes a member value that is not in the vendored artifact.**
Worksheet text: "`| 成员数值 = `metrics.test.score` | OBSERVABLE | JSON pointer
`/metrics/test/score`, 例如 `output/adult/mlp/tuned/0/stats.json` ⇒ `0.8519132454581358` |`".
Measured from `PILOT\output\adult\mlp\tuned\0\stats.json` → `/metrics/test/score` =
`0.8519132731404705` (identical to `/metrics/test/accuracy`). Digits agree only to 6 dp
(`0.851913`); the trailing 8 digits differ. Effect on the audit: none (the loader reads the file,
not the worksheet), but the worksheet is *not* a faithful copy of the checkout it cites. Paper
Doctor must treat `EVIDENCE_NOTES.md` as a narrative, not as data.

**D-0.2 — `EVIDENCE_NOTES.md:88` claims `/best_epoch` for adult seed 0 is 24. Measured: 20.**
Full measured `best_epoch` vector, seeds 0..14: `20, 21, 21, 12, 14, 26, 16, 17, 30, 18, 16, 15,
23, 16, 27`. Nothing in the manifest or in RD001–RD008 depends on these numbers (the value is read
only as `SelectionEvent.promoted_ref`, `SRC/manifest.py:985-1005`), so the audit is unaffected — but
the worksheet's own worked example is wrong.

**D-0.3 — `EVIDENCE_NOTES.md:68` states the adult oracle mean as `0.8521753373052433`; the audit and
my independent recomputation both give `0.8521753373052434`** (last ULP). Cause is summation order:
`SRC/compute.py:45-55` `center()` is `sum(vals)/len(vals)`, not a pairwise/Kahan sum. The rendered
string is `0.852` either way, so RD001 still PASSes. `EVIDENCE_NOTES.md:69` claims the
california_housing mean `-0.4985475737517660`; measured `-0.498547573751766` — same number, the
trailing zero is display-only. No discrepancy there.

**D-0.4 — `REAL_WORLD_ONBOARDING_REPORT.md:120` says "引用的不同文件 | 34 (30 stats.json + README.md
+ bin/mlp.py + bin/tune.py + tuning/0.toml + best.toml)". That parenthetical enumerates 35 files.**
Measured: **34** distinct files appear in a `path:` locator position (`30 stats.json + README.md +
bin/mlp.py + bin/tune.py + output/adult/mlp/tuning/0.toml`); `output/adult/mlp/tuning/0/best.toml` is
the **35th** referenced file but it is referenced only as a bare string (candidate member + `chosen:`),
which the loader never opens (see §C-4). `RESULT_DOCTOR_PHASE5_REPORT.md:180` repeats "34" as the
after-value.

**D-0.5 — `EVIDENCE_NOTES.md:34,38` and `REAL_WORLD_ONBOARDING_REPORT.md:80` say the printed value
"只能 `declared:`" (can only be declared). The shipped manifest does not declare it.**
`PILOT\result-doctor.yml:59` and `:85` read `value: {observed: {path: README.md, line: 80/82, text:
"0.852"/"-0.499"}}`, i.e. **DIRECT**. `REAL_WORLD_ONBOARDING_REPORT.md:253` notices this
("打印值本身最终**不是**声明 … ⇒ DIRECT"), so the pilot's own two documents disagree about which
door the printed value went through. The DIRECT reading is the one that shipped.

**D-0.6 — the marginal-cost claim is true for the Phase 4 snapshot and off by one for the shipped
Phase 5 manifest.** See §F for measured numbers (`+25` before, `+24` now; 15 enumeration lines in both).

Nothing else in the reports was contradicted by measurement: the 16-finding status vector, the census,
the object populations, the `path:` counts (73 → 43), the logical-line counts (110 → 98), the average
member-line length (182 chars), and the canonical JSON hash all reproduce exactly.

---

## A. Manifest object inventory and full trace of the two audited cells

### A.1 Inventory of the shipped manifest (`PILOT\result-doctor.yml`, 105 file lines / 98 logical)

Counts measured by loading it with `SRC.manifest.bundle_from_manifest` (not read off the reports):

| object class | count | ids (verbatim from the Bundle) |
|---|---|---|
| artifacts | **0** | — the `artifacts:` section is not written at all; `SRC/manifest.py:453-504` never runs |
| reported cells (`reported_results`) | **2** | `mlp-tuned/adult`, `mlp-tuned/california_housing` (labels are the ids, `SRC/manifest.py:1071-1074`) |
| aggregations | **2** | `agg:mlp-tuned/adult`, `agg:mlp-tuned/california_housing` — auto-named from the cell label, `SRC/manifest.py:1168-1179` |
| members | **30** | `agg:<label>/seed-0 … agg:<label>/seed-14`, `SRC/manifest.py:769-770` |
| transformations | **1** chain, **1** step | chain id `readme-render` (`PILOT\result-doctor.yml:14`), instance id `treadme-render:t:README aggregate column:0`, `SRC/manifest.py:586` |
| candidate sets | **2** | `cand:adult-tuning-trials` (`:20`), `cand:adult-epochs` (`:26`) |
| selection events | **2** | `sel:adult-tuned-config` (`:32`), `sel:per-run-epoch` (`:43`) |
| comparison sets | **0** | the `comparisons:` section is not written (deliberate: `EVIDENCE_NOTES.md:129`) |
| evidence registry entries | **1** | `best-epoch` (`:7`), reused by all 30 member selectors through `selector: {kind: best, via: best-epoch}` (`SRC/manifest.py:324-330`) |
| distinct files reached by a `path:` locator | **34** | 30 × `stats.json`, `README.md`, `bin/mlp.py`, `bin/tune.py`, `output/adult/mlp/tuning/0.toml` |
| `path:` occurrences | **43** | `RESULT_DOCTOR_PHASE5_REPORT.md:177` claims 43 — confirmed by count |

The 8-object Bundle population is confirmed independently by `RESULT_DOCTOR_PHASE5_REPORT.md:209-210`.

### A.2 Cell 1 — `mlp-tuned/adult` = `0.852`

| link | value | source |
|---|---|---|
| printed locus | `README.md` / table `README metrics snippet` / row `adult` / column `metrics.test.score` / quoted_text `adult                 0.852` | `PILOT\result-doctor.yml:57` |
| printed value door | `observed` → **DIRECT** | `PILOT\result-doctor.yml:59`; graded at `SRC/manifest.py:353-354` |
| the locator actually used | `{path: README.md, line: 80, text: "0.852"}` | returns the *fragment*, not the line: `SRC/manifest.py:306-314` |
| README line 80 content | `adult                 0.852` | `PILOT\README.md:80` (verified by `sed -n '80p'`) |
| quantity key | `metrics.test.score/adult` (row-scoped) | `PILOT\result-doctor.yml:58`; required by `SRC/manifest.py:1025-1042` (the G2 guard) |
| aggregation wording | `observed {path: README.md, line: 70, text: "averaged over all random seeds"}` → **DIRECT** | `PILOT\result-doctor.yml:60`; `PILOT\README.md:70` = `Now, for each dataset, let's compute the test score averaged over all random seeds:` |
| transformation chain | `steps: {ref: readme-render}` → `format@render/fixed/digits=3/applied_at=script`, evidence `observed {README.md:73, text:".round(3)"}` → **DIRECT** | `PILOT\result-doctor.yml:14-17,61`; `PILOT\README.md:73` = `print(df.groupby('dataset')['metrics.test.score'].mean().round(3))` |
| member rule | `kind: enumerated`, `declared {value: enumerated, by: "the 15 seed runs listed here"}` → **DECLARED** | `PILOT\result-doctor.yml:64`; `SRC/manifest.py:639-659` |
| selection binding | `[adult-tuned-config]` (the tuning search) | `PILOT\result-doctor.yml:62` |
| spread | **UNKNOWN** — "the printed cell carries no +/-" | `SRC/manifest.py:404-408`, visible in the audit JSON finding 10 |

The 15 member files (all `key: /metrics/test/score`, identity `observed {key: /config/seed}` — the
inherited-path sugar, `SRC/manifest.py:722-739` — selector `best` via `best-epoch`, DECLARED):

| member | path (relative to `PILOT`) | `/config/seed` | `/best_epoch` | `/metrics/test/score` |
|---|---|---|---|---|
| seed-0 | `output/adult/mlp/tuned/0/stats.json` | 0 | 20 | 0.8519132731404705 |
| seed-1 | `output/adult/mlp/tuned/1/stats.json` | 1 | 21 | 0.8523432221608009 |
| seed-2 | `output/adult/mlp/tuned/2/stats.json` | 2 | 21 | 0.8530188563356059 |
| seed-3 | `output/adult/mlp/tuned/3/stats.json` | 3 | 12 | 0.8526503286038941 |
| seed-4 | `output/adult/mlp/tuned/4/stats.json` | 4 | 14 | 0.8532031202014618 |
| seed-5 | `output/adult/mlp/tuned/5/stats.json` | 5 | 26 | 0.8538173330876482 |
| seed-6 | `output/adult/mlp/tuned/6/stats.json` | 6 | 16 | 0.8530802776242246 |
| seed-7 | `output/adult/mlp/tuned/7/stats.json` | 7 | 17 | 0.8527731711811314 |
| seed-8 | `output/adult/mlp/tuned/8/stats.json` | 8 | 30 | 0.8465081997420306 |
| seed-9 | `output/adult/mlp/tuned/9/stats.json` | 9 | 18 | 0.8500706344819114 |
| seed-10 | `output/adult/mlp/tuned/10/stats.json` | 10 | 16 | 0.8539401756648854 |
| seed-11 | `output/adult/mlp/tuned/11/stats.json` | 11 | 15 | 0.8536330692217923 |
| seed-12 | `output/adult/mlp/tuned/12/stats.json` | 12 | 23 | 0.8523432221608009 |
| seed-13 | `output/adult/mlp/tuned/13/stats.json` | 13 | 16 | 0.8535716479331736 |
| seed-14 | `output/adult/mlp/tuned/14/stats.json` | 14 | 27 | 0.8497635280388183 |

Declared at `PILOT\result-doctor.yml:66-80`. The manifest member list lines 66-80 correspond 1:1 to
the table above. There is **no CSV column** in this pilot: the member "column" is the JSON pointer
`/metrics/test/score`, read by `SRC/manifest.py:288-298`. `metrics.test.accuracy` exists in the same
dict with the same value (`EVIDENCE_NOTES.md:52`), but the manifest does not cite it.

Transformation applied: `format(mode=fixed, digits=3)` at stage `render` →
`SRC/compute.py:58-63` returns `f"{value:.3f}"`. `RESULT_DOCTOR_PHASE5_REPORT.md:302-303` flags the
resulting strength ceiling: `text: ".round(3)"` proves README line 73 *contains* that fragment; it
does not prove the pipeline rounded with `round(3)` (nor that pandas' `round` and `:.3f` agree — they
happen to here).

Chain arithmetic as executed (`SRC/rules.py:61-90`): 15 DIRECT values → `sum/15` =
`0.8521753373052434` → `f"{…:.3f}"` = `"0.852"` → compared **as strings** against the DIRECT
`value` fragment `"0.852"` (`SRC/rules.py:169-176`) → `center_matches: true` → RD001 PASS.

### A.3 Cell 2 — `mlp-tuned/california_housing` = `-0.499`

Identical shape; the deltas are:

| link | value | source |
|---|---|---|
| printed locus | row `california_housing`, quoted_text `california_housing   -0.499` | `PILOT\result-doctor.yml:83`; `PILOT\README.md:82` |
| printed value door | `observed {path: README.md, line: 82, text: "-0.499"}` → **DIRECT** | `PILOT\result-doctor.yml:85` |
| quantity key | `metrics.test.score/california_housing` | `PILOT\result-doctor.yml:84` |
| selection binding | **none** (`selection:` absent) | `PILOT\result-doctor.yml:82-105`; hence RD003 `NOT_APPLICABLE` on this cell |
| mean | `-0.498547573751766` → `"−0.499"` | audit JSON finding 2, `recomputed_center` |

The 15 member files are `output/california_housing/mlp/tuned/{0..14}/stats.json`
(`PILOT\result-doctor.yml:91-105`); measured values:

| member | `/config/seed` | `/best_epoch` | `/metrics/test/score` |
|---|---|---|---|
| seed-0 | 0 | 61 | -0.49420855673906827 |
| seed-1 | 1 | 49 | -0.5006588681096609 |
| seed-2 | 2 | 61 | -0.49451899244985204 |
| seed-3 | 3 | 62 | -0.4989870096945739 |
| seed-4 | 4 | 43 | -0.49654744701097997 |
| seed-5 | 5 | 67 | -0.49397467271554046 |
| seed-6 | 6 | 90 | -0.4979784432661168 |
| seed-7 | 7 | 51 | -0.4967865874882563 |
| seed-8 | 8 | 51 | -0.5035519045022604 |
| seed-9 | 9 | 65 | -0.5011451176526394 |
| seed-10 | 10 | 50 | -0.4967998842012205 |
| seed-11 | 11 | 85 | -0.5009417028858154 |
| seed-12 | 12 | 64 | -0.5009139943273807 |
| seed-13 | 13 | 57 | -0.49861079745562586 |
| seed-14 | 14 | 57 | -0.502589627777499 |

This is the negative-score half of the rounding test chosen deliberately
(`EVIDENCE_NOTES.md:25-26`: "一个是正的分数、一个是负的分数, `round(3)` 的渲染行为在两侧都要求值").
`metrics.test.accuracy` does **not** exist here (`None`), so `score` is an unnamed regression
statistic held at UNKNOWN: `metric_name` and `direction_semantics` are both UNKNOWN on both cells
(audit JSON findings 1-2, and `EVIDENCE_NOTES.md:53` "作者只声明…不猜名字").

### A.4 The non-cell objects, traced

- `evidence: best-epoch` — DECLARED statement + `supported_by {path: bin/mlp.py, line: 254, text:
  "best_epoch"}` (`PILOT\result-doctor.yml:6-11`). Measured `PILOT\bin\mlp.py:254` =
  `        stats['best_epoch'] = stream.epoch`.
- `cand:adult-tuning-trials` — `universe: partial`, `declared_size {value: 100, … supported_by
  {output/adult/mlp/tuning/0.toml, line 20, "n_trials = 100"}}`, `surviving_size {value: 1}`
  (`:19-25`). Measured `PILOT\output\adult\mlp\tuning\0.toml:20` = `n_trials = 100`.
- `cand:adult-epochs` — `universe: unknown`, prose `statement` only, no sizes (`:26-29`).
- `sel:adult-tuned-config` — metric/timing DIRECT from `bin/tune.py:131` / `:192`, direction DIRECT
  from `bin/tune.py:178` fragment `"maximize"`, split/scope DECLARED, tie_break UNKNOWN
  (`:31-42`). Measured lines: `131 → "        return stats['metrics'][lib.VAL]['score']"`,
  `178 → "        direction='maximize',"`, `192 → "best_trial_id = study.best_trial.number"`.
- `sel:per-run-epoch` — metric/timing both DIRECT from `bin/mlp.py:250` fragment
  `"progress.update"`, direction explicitly UNKNOWN ("the comparison lives inside the third-party
  zero.ProgressTracker"), tie_break UNKNOWN (`:43-53`). Measured `bin\mlp.py:250` =
  `    progress.update(metrics[lib.VAL]['score'])`. This event is bound to **no** cell, yet RD003
  still audits it (`REAL_WORLD_ONBOARDING_REPORT.md:185`).
- Extra observable that the manifest does *not* cite: `PILOT\output\adult\mlp\tuning\0\stats.json`
  `/best_stats/metrics/val/score` = `0.8550591125441425` (matches `EVIDENCE_NOTES.md:100`) and
  `/best_stats/trial_id` = `31`.

---

## B. Frozen audit reproduced

### B.1 Command and exact terminal output

```
$ cd /f/MLResearch/result-doctor && PYTHONPATH="src;tests" python -X utf8 -m result_doctor audit phase4/rtdl-revisiting-models
```

Verbatim stdout (16 findings, 2 lines each, then the census; exit code 0):

```text
# result-doctor audit phase4/rtdl-revisiting-models/result-doctor.yml
RD001   PASS            mlp-tuned/adult
        reason: recomputed rendering equals the reported cell
RD001   PASS            mlp-tuned/california_housing
        reason: recomputed rendering equals the reported cell
RD002   PASS            aggregation:agg:mlp-tuned/adult
        reason: membership enumerable and every exclusion bindable
RD002   PASS            aggregation:agg:mlp-tuned/california_housing
        reason: membership enumerable and every exclusion bindable
RD003   NOT_APPLICABLE  reported:mlp-tuned/california_housing
        reason: no selection step is recorded in the production of this cell
RD003   INCONCLUSIVE    selection:sel:adult-tuned-config
        reason: the promoted member cannot be bound to a candidate record, so the declared policy cannot be checked against it (['candidate_values_unrecorded'])
RD003   INCONCLUSIVE    selection:sel:per-run-epoch
        reason: no declared selection policy; the criterion is only implicit in code
RD004   INCONCLUSIVE    candidates:cand:adult-epochs
        reason: candidate universe recoverability is UNKNOWN; this is never inferred from the count of surviving artifacts
RD004   INCONCLUSIVE    candidates:cand:adult-tuning-trials
        reason: candidate universe recoverability is PARTIAL; this is never inferred from the count of surviving artifacts
RD005   NOT_APPLICABLE  mlp-tuned/adult
        reason: the cell carries no dispersion
RD005   NOT_APPLICABLE  mlp-tuned/california_housing
        reason: the cell carries no dispersion
RD006   PASS            reported:mlp-tuned/adult
        reason: the chain applied step by step yields the printed cell
RD006   PASS            reported:mlp-tuned/california_housing
        reason: the chain applied step by step yields the printed cell
RD007   NOT_RUN         rule:RD007
        reason: no target of this class was supplied (comparison_sets is empty)
RD008   INCONCLUSIVE    quantity:metrics.test.score/adult
        reason: the quantity is printed in a single product, so there is nothing to cross-check
RD008   INCONCLUSIVE    quantity:metrics.test.score/california_housing
        reason: the quantity is printed in a single product, so there is nothing to cross-check

PASS: 6
FAIL: 0
INCONCLUSIVE: 6
NOT_APPLICABLE: 3
NOT_RUN: 1
```

Status vector (rule_id, target, status), the order `render_text` sorts by `(rule_id, target)`
(`SRC/../cli.py:72-88`):

| # | rule_id | status | target |
|---|---|---|---|
| 1 | RD001 | PASS | mlp-tuned/adult |
| 2 | RD001 | PASS | mlp-tuned/california_housing |
| 3 | RD002 | PASS | aggregation:agg:mlp-tuned/adult |
| 4 | RD002 | PASS | aggregation:agg:mlp-tuned/california_housing |
| 5 | RD003 | NOT_APPLICABLE | reported:mlp-tuned/california_housing |
| 6 | RD003 | INCONCLUSIVE | selection:sel:adult-tuned-config |
| 7 | RD003 | INCONCLUSIVE | selection:sel:per-run-epoch |
| 8 | RD004 | INCONCLUSIVE | candidates:cand:adult-epochs |
| 9 | RD004 | INCONCLUSIVE | candidates:cand:adult-tuning-trials |
| 10 | RD005 | NOT_APPLICABLE | mlp-tuned/adult |
| 11 | RD005 | NOT_APPLICABLE | mlp-tuned/california_housing |
| 12 | RD006 | PASS | reported:mlp-tuned/adult |
| 13 | RD006 | PASS | reported:mlp-tuned/california_housing |
| 14 | RD007 | NOT_RUN | rule:RD007 |
| 15 | RD008 | INCONCLUSIVE | quantity:metrics.test.score/adult |
| 16 | RD008 | INCONCLUSIVE | quantity:metrics.test.score/california_housing |

Census: `PASS: 6 / FAIL: 0 / INCONCLUSIVE: 6 / NOT_APPLICABLE: 3 / NOT_RUN: 1`. This is byte-equal to
the frozen census constant `RD\tests\test_cli.py:31` (`PILOT_CENSUS`), and the assertion at
`RD\tests\test_cli.py:133-141` pins exactly 16 findings over the pilot. Ordering note: `adult` sorts
before `california_housing`, but `cand:adult-epochs` before `cand:adult-tuning-trials`, and RD003's
`NOT_APPLICABLE` row is target-sorted first — the 16 rows are NOT grouped "rule then cell".

Line-ending note (matters for any byte-level claim about this output): the text stream, when
redirected on this machine, carries CRLF (observed via `cat -A`: every line ends `^M$`), because
`SRC/../cli.py:160-161` writes with `print`/`sys.stdout.write` in Windows text mode. Only `--json`
forces LF (`SRC/../cli.py:97-103`, `newline="\n"`). The report text above is LF-normalised.

### B.2 Canonical JSON artifact

Command: the same audit with `--json F:/MLResearch/paper-doctor/phase0/work/rtdl-audit-from-pylib.json`.

| measured | value |
|---|---|
| path | `F:\MLResearch\paper-doctor\phase0\work\rtdl-audit-from-pylib.json` |
| size | **13,395 B** |
| sha256 | **`2ad02c8fb6ace0af325c2bc50c08eb9f0162e77b25c659e96951df96f694a660`** |
| CR bytes | 0 |
| top level | JSON array of 16 objects; each object's keys are `evidence, measurements, question, reason, rule_id, rule_name, status, target` |

**MATCH: yes.** Both size and full hash equal the frozen reference (13,395 B / `2ad02c8f…`, recorded
at `RD\release\RELEASE_FREEZE_0.1.0.md:84-85`, `RD\release\PYPI_DOWNTIME_STAGING_REPORT.md:48`, and
`RD\HANDOFF_RESULT_DOCTOR_POST_RELEASE_2026-09-28.md:52`). The audit is reproducible from the frozen
tree on this machine, via the v0.1.0 package source, without any drift.

`canonical_json` is `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)`
(`SRC/status.py:64-66`), so key order is fixed and non-ASCII (the `±` inside RD008's `loci` strings,
`SRC/rules.py:741-743`) is written raw UTF-8. Note two determinism caveats for Paper Doctor:
(i) the JSON embeds `NaN` for `recomputed_dispersion` (finding 1/2), which is not strict JSON —
Python parses it, a browser/`json.loads` with `parse_constant` defaults does too, but any other
consumer may choke; (ii) RD008's loci values render `"0.852±None"` — the unrounded `None` of an
UNKNOWN spread leaking into a printed projection (`SRC/rules.py:741-743`).

### B.3 Measurement payload worth reusing

- RD001 finding 1 measurements: `n_members: 15`, `member_values` (rounded to 6 dp by
  `SRC/rules.py:77`), `recomputed_center: 0.8521753373052434`, `rendered_center: "0.852"`,
  `reported_center: "0.852"`, `center_matches: true`, `dispersion_matches: true` (vacuously, spread
  absent), `computable: true`.
- RD003 `sel:adult-tuned-config`: `criterion_grades {metric: DIRECT, direction: DIRECT, timing:
  DIRECT, split: DECLARED, scope: DECLARED, tie_break: UNKNOWN}`, `n_candidates: 0`,
  `candidate_values_unrecorded: true`, `declared_policy_grade: DECLARED` (auto-synthesised from
  direction+chosen by `SRC/manifest.py:989-997` — the author wrote zero bytes for it).
- RD004 `cand:adult-tuning-trials`: `universe_status: PARTIAL`, `declared_size: 100 (DECLARED)`,
  `surviving_size: 1 (DECLARED)`, `sizes_stated_in_same_unit: true`, `promotion_grade: UNKNOWN`.
- RD007: `driving_object_class: comparison_sets`, `n_objects: 0`, `n_targets: 0`, `evidence: []`.
- RD008: `n_loci: 1` on both quantities — no cross-product exists to compare.

---

## C. What the manifest grammar CAN and CANNOT express about a paper

Grounded in `SRC/manifest.py`. The two-door discipline is stated in the module docstring
(`SRC/manifest.py:10-14`): "A fact is either read back through a locator inside the project root
(OBSERVED -> Grade.DIRECT) or asserted by the user in the manifest (DECLARED). Everything else is
UNKNOWN. This module assigns no grade the user did not earn: it never reads a scientific fact out of
a file name, a directory name, a group name or a count of runs."

### C.1 The four locator families (`LOCATOR_KEYS`, `SRC/manifest.py:110`)

Dispatch precedence is fixed at `SRC/manifest.py:258-270`: `column` → `key` → `line` → `text`.

| family | reader | returns | grades | failure codes |
|---|---|---|---|---|
| `{path, column, row}` (CSV) | `_read_csv` `:272-286` | cell string; `row` is 1-based int or the literal `last` (`:283`) | DIRECT | `E_LOCATOR_COLUMN` (header lacks column), `E_LOCATOR_ROW` (header but no rows / index out of range), `E_NOT_A_NUMBER` (non-integer row) |
| `{path, key}` (JSON pointer) | `_read_json` `:288-298` | typed node (dict/list walk, digit list indices allowed) | DIRECT | `E_LOCATOR_KEY` |
| `{path, line[, text]}` (line) | `_read_line` `:300-315` | with `text`: the **fragment** (validated to be a substring of that one line); without: the **whole line, stripped** | DIRECT | `E_LOCATOR_LINE` (out of range), `E_LOCATOR_TEXT` (fragment not on that line) |
| `{path, text}` (whole file) | `read_locator` `:264-269` | the fragment, `SourceRef(key='text:"…"')` | DIRECT | `E_LOCATOR_TEXT` (fragment not in file) |

Every family first passes `under_root` (`:234-248`): relative-only, no absolute / drive-letter / `~` /
`..` / resolved-escape → `E_PATH_OUTSIDE_ROOT`; must be an existing *file* → `E_ARTIFACT_MISSING`;
empty → `E_MISSING_FIELD`. Missing/mis-combined locator keys → `E_LOCATOR_KEYS` (`:252-254, :270`).
Locators are keyed to `root:`, which is resolved relative to the manifest's own directory
(`:180-181`) — the same docstring fact restated in `SRC/cli.py:22-24`.

### C.2 What it CAN express about a paper — measured, not inferred

1. **A paper value printed in a UTF-8 text file under root, exactly as a fragment.** The frozen
   fixtures already do this: `RD\tests\generic_fixtures\g1\result-doctor.yml:16` —
   `value: {observed: {path: paper/table2.txt, line: 7, text: "94.12 ± 0.24"}}` against
   `RD\tests\generic_fixtures\g1\paper\table2.txt:7`. Proven again here: a scratch manifest in a
   scratch dir located `{path: paper/table3.txt, line: 5, text: "91.4"}` and graded DIRECT.
   Because the reader is `read_text(encoding="utf-8")` + `splitlines()`
   (`:266, :302`), a **LaTeX `.tex` source under root is a legal locator target** — line/text
   families work on it unchanged. That is the cheapest bridge available to Paper Doctor.
2. **A printed cell with dispersion.** `_split_cell` (`:163-172`) splits `center ± spread` on `±` or
   `+/-` (`CELL_SEPARATORS`, `:99`), so `"94.12 ± 0.24"` becomes a value field *and* a spread field
   from one fragment. `spread: {kind: std|sem|k_sem, ddof, k}` (`:619-633`) declares the form;
   RD005 (`SRC/rules.py:464-582`) tests it against the six formula families (`_FAMILIES`, `:454-461`).
3. **A prose sentence, located and graded DIRECT — but only in one slot.** `wording:`
   (`PILOT\result-doctor.yml:60,86`; `g1/…:18-22`; `g5/…:16`) lowers to
   `ReportedResult.spread_label` (`SRC/manifest.py:1129`; `SRC/schema.py:311`).
4. **Cross-product agreement of one quantity.** `quantity:` keys are RD008's grouping key
   (`SRC/rules.py:731-745`); the same key may legitimately name a cell in `README.md` and a cell in
   `paper/table.txt` — `RESULT_DOCTOR_PHASE5_REPORT.md:157-158` pins that, and
   `g2/…` and `example_b/…` show both sides. This is the *only* rule whose question is literally
   "does the same quantity agree across the products it appears in?" (`SRC/rules.py:35`).
5. **Presentation dependency of a table** (bold/† marks, peer sets, external origin):
   `comparisons:` with `over/origin/marks/marks_derivation/rule` (`SRC/manifest.py:1224-1282`),
   e.g. `example_b/result-doctor.yml:80-86` quoting `**91.4**` at `paper/table1.txt:5`.
6. **A paper-shaped locus label**: `printed_in {artifact, page, table, row, column, quoted_text}`
   (`SRC/manifest.py:1081-1089`; `SRC/schema.py:81-94` — `Locus` even has a `page` field, and
   `SRC/evidence.py:24-25` says SourceRef is "file:line, artifact, **or paper locus**").

### C.3 What it CANNOT express — with the code that makes it impossible

1. **A binary paper (PDF). At all.** Every reader is `read_text(encoding="utf-8")`
   (`:266, :290, :302`). Measured: locating `{path: paper/binary.pdf, line: 1, text: "PDF-ish"}`
   raises **`UnicodeDecodeError`, not a `ManifestError`**, and `main()` catches only `ManifestError`
   (`SRC/cli.py:157-159`) → the CLI dies with a traceback and exit code **1** ("the tool failed
   unexpectedly", `SRC/cli.py:13`), not the clean exit-2 authoring refusal. Paper Doctor cannot reuse
   the frozen loader for PDFs; it must consume a text/`tex`/extracted projection and keep that
   projection itself under audit.
2. **Any claim about a page, table, row or column that has not been transcribed.** `printed_in` is
   **verified by nothing**: the six fields are `str(printed.get(...))` (`:1085-1089`), never passed to
   `read_locator`, never graded, never opened. Measured: a scratch manifest with
   `quoted_text: "TOTALLY BOGUS NOT IN ANY FILE 999.9"` and `page: "7"` loads, and the false string
   lands in `Locus.quoted_text` verbatim; RD008's loci key is then built from it (`SRC/rules.py:741`).
   Consequence for Paper Doctor: the pilot's *table/row/column/quoted_text* evidence is **ungraded
   metadata**, not evidence — while the same line's `value:` fragment is DIRECT. `Locus`'s docstring
   asserts "FM1/FM13 require the quoted original" (`SRC/schema.py:82-83`); the loader does not enforce
   that. Say it loudly: **the RTDL pilot's `quoted_text` happens to be true, and nothing proves it.**
3. **A free-text claim with a predicate.** There is no `claim`, `sentence`, `assertion` or
   `statement-vs-evidence` object anywhere in the grammar (`SECTIONS`, `:87-96`; the per-section
   allowed-key tuples at `:444, :458, :610, :711, :823-838, :951-955, :1049-1070, :1229`). The only
   place a *sentence* may sit and be read by a rule is `wording:`/`spread_label`, and RD005's reader
   is a hardcoded keyword test: `says_se = "standard error" in lab or lab.strip().startswith("se ") or
   " s.e" in lab`; `says_std = ("standard deviation" in lab) or lab.strip() in ("std", "stdev",
   "standard dev")` (`SRC/rules.py:530-531`), with the else-branch
   `f"wording {label.value!r} is not classifiable against {form_label}"` → INCONCLUSIVE
   (`:563-567`). Everything else prose-shaped — `declared.{by,statement}` (`:362-367`), `note`
   (`:343`), `dispersion_statement` (`:694`), `member_rule.statement` (`:656`), `candidate_sets[].statement`
   (`:823-838`), `comparison.rule.expression` (`:1258`), `aggregate.reason` → `not_aggregated_reason`
   (`:1093, :1130`) — is **carried, quoted into `SourceRef.note`, and never evaluated.** There is no
   code path that compares a sentence to an artifact.
4. **Existence of a referenced-but-not-located file.** Only `path:` inside a locator is opened.
   Candidate `members:` refs (`:848`) and `selection_events[].chosen` (`:985-1005`) are bare strings.
   Measured: a scratch manifest listing `does/not/exist.toml`, `also/missing.json` as candidate
   members and `totally/absent.toml` as `chosen:` loads with no complaint and stores them verbatim.
   In the pilot, `output/adult/mlp/tuning/0/best.toml` (the *surviving* candidate and the promoted
   artifact) is **never read or existence-checked by the loader**, and `surviving_size: 1` is
   DECLARED, not observed (`PILOT\result-doctor.yml:24-25, :35, :45`).
5. **Position-preserving citation.** `{path, text}` proves the fragment occurs *somewhere* in the
   file; `{path, line, text}` proves it occurs *on that line* — nothing proves the fragment is the
   value of the field it is cited for. The pilot's own post-mortem states this limit:
   "`text: "maximize"` 只证明该行含此片段, 不证明它是 `direction=` 的值"
   (`RESULT_DOCTOR_PHASE5_REPORT.md:302-303`). No regex/offset/span/column-range locator exists
   (`LOCATOR_KEYS`, `:110`), and Phase 5 explicitly refused to add one
   (`:134-135` "不新增 substring/regex locator").
6. **Whole-table or multi-cell extraction.** One locator = one fragment per cell; there is no table
   object, no iteration, no wildcard, no directory scan. `read_locator` requires a concrete file
   (`:246-247`) and `_members` requires each member written out (`:741-816`). This is the firewall,
   not an omission: `RESULT_DOCTOR_PHASE5_REPORT.md:17` "新增自动发现 | 0 (无 glob / 目录扫描 / 通配
   成员 / 自动 seed / 自动行身份)" and `EVIDENCE_NOTES.md:45` "契约无目录扫描; 成员必须由作者逐个列出").
7. **Comparative / statistical prose claims** ("on par with or even better than", "reduces the gap",
   "the best average performance" — `PILOT\README.md:22-32`). Nearest grammar: a comparison set with a
   `rule {expression, operator, symmetric, k_factor}` (`:1251-1263`) — but `operator` is only used for
   **presentation marks**, and a mark list can never be OBSERVED
   (`_mark_field`, `:1297-1302` `E_BAD_FIELD` "a mark list cannot be OBSERVED through the manifest").
   A declared mark without a `marks_derivation` is refused with `E_MARK_DERIVATION` (`:1266-1272`).
   There is no significance test, no direction-of-better-than for arbitrary prose.
8. **Rounding that the tool will perform for you.** `round`, `delta`, `best_of_n`, `truncate_window`
   are `STEPS_NOT_APPLIED` → `E_STEP_NOT_APPLIED` (`:107-108, :538-544`) — verified live:
   `{step: round, stage: render}` → "step 'round' is not applied by the computation layer, so
   declaring it here would claim a transformation that never happens". `format` is legal only at
   stage `render`, and nothing else is legal at `render` (`:545-553`, `E_RENDER_STEP`; verified live
   with `format@center`). `STAGES = ("member","center","dispersion","render")` (`SRC/compute.py:19`).
9. **Grade inflation.** The generic path emits only DIRECT / DECLARED / UNKNOWN; `Grade` also has
   `DERIVED` and `INFERRED` (`SRC/evidence.py:16-21`) but they are pinned away by
   `RD\tests\test_generic_firewall.py:363` (`test_the_generic_path_never_emits_INFERRED_or_DERIVED`).
   The error vocabulary is frozen at exactly **26** codes
   (`SRC/manifest.py:121-146`, mirrored at `RD\tests\test_generic_firewall.py:433-460`, asserted by
   `:463-467`); Phase 5 added none (`RESULT_DOCTOR_PHASE5_REPORT.md:18`).

Two refusals that exist *specifically* to stop silent paper-level misjudgement, both newly frozen:

- **G1 guard** `_cell_field` (`:383-396`): a printed-cell `value:` whose `observed:` body has `line`
  but no `text` is rejected with `E_LOCATOR_TEXT` and a message that names the fix. Verified live.
- **G2 guard** `_check_quantity_identity` (`:1025-1042`): one `quantity` key claimed by two cells of
  the same `(artifact, table)` → `E_MISSING_FIELD` with both row names in the message.

### C.4 The one thing the grammar gets *exactly* right for Paper Doctor

`EVIDENCE_NOTES.md:9-11` already codifies a three-state authoring grammar that maps 1:1 onto claim
evidentiality: `OBSERVABLE` = a frozen locator reads it back; `DECLARABLE` = "仓库里没有可解析的数字/
字段位置, 但作者能把这句话写进 `declared:`"; `UNKNOWN` = "作者也无法诚实地给出". `SRC/manifest.py:21-25`
implements it as `observed`/`declared`/`unknown` and adds: "`unknown:` … is a normal thing to write,
not an error." Insufficient evidence is *never* a parse error (`:15-17`), and `FAIL` is defined in the
help text as "one rule found an inconsistency in the evidence for this target — not a failed
experiment or paper" (`SRC/cli.py:113-114`). That is the honesty machinery Paper Doctor should reuse
verbatim rather than re-invent.

---

## D. Does the pilot ever touch the *paper*?

**No. Not one byte of the arXiv e-print, PDF, or LaTeX source is read by the audit.** The pilot's
outermost evidential boundary is the repository README.

Evidence, with citations:

1. **`root:` is the repo.** `PILOT\result-doctor.yml:2-4` — `project: rtdl-revisiting-models`,
   `root: .`; `under_root` (`SRC/manifest.py:234-248`) makes anything outside unreachable, and
   `E_PATH_OUTSIDE_ROOT` refuses `..` (verified live against a path outside the scratch root).
2. **Zero paper references in the whole evidence grammar.** Grepping the pilot manifest for
   `arxiv|arXiv|\.pdf|latex|Table 2` returns nothing; `grep -n "Table" PILOT\result-doctor.yml` → no
   match (the only table token is the lowercase free-text `table: "README metrics snippet"` at
   `:57, :83`, which is an unverified string, §C-3.2). The only `arxiv` strings anywhere in the
   vendored tree are upstream content the audit never opens: `PILOT\README.md:6`
   (`:scroll: [arXiv](https://arxiv.org/abs/2106.11959)`) and `PILOT\package\README.md:219`
   (an unrelated Linformer link).
3. **The pilot says so itself, three times.**
   - `EVIDENCE_NOTES.md:36`: "「这张表等于论文 Table 2」 | DECLARABLE | `README.md:76` 是一句散文宣称;
     **论文 PDF 不在仓库里, 不能 OBSERVED**".
   - `EVIDENCE_NOTES.md:128`: "这 11 行数字与论文 Table 2 的关系 | DECLARABLE | … **PDF 不在 root 内**".
   - `REAL_WORLD_ONBOARDING_REPORT.md:88`: "与论文 Table 2 的关系 | D | `README.md:76` 是散文, **PDF
     不在 root 内**".
   - and the registered gap `G9` (`:324`): "论文/PDF 侧的打印物完全不可达, 「打印值」只能来自仓库内文本".
4. **The single most load-bearing paper claim in this project — `PILOT\README.md:76`
   `*The output exactly matches Table 2 from the paper:*` — is quoted in no manifest field at all.**
   Measured: `grep -c "line: 76" PILOT\result-doctor.yml` → **0**. The claim that ties the README
   column to the NeurIPS table is the pilot's *only* genuine prose-claim-about-a-paper, and the
   pilot deliberately dropped it rather than representing it
   (`EVIDENCE_NOTES.md:129`: "缺对象就让它缺, 交给 NOT_RUN"; `REAL_WORLD_ONBOARDING_REPORT.md:220`
   §12-A-4: "想写「这张表等于论文 Table 2」但 PDF 不在 root 内 ⇒ 只能整段放弃").
   ⇒ RD007 `NOT_RUN` and RD008 `n_loci: 1` are the *measured footprint* of the paper being absent.

### D.1 Every place README wording is used as evidence, and the grade it is held at

| # | README text | where used | locator | grade | does a rule read it? |
|---|---|---|---|---|---|
| 1 | `adult                 0.852` (line 80) | printed value of cell 1 (`:59`) | `{path, line: 80, text: "0.852"}` | **DIRECT** | RD001 (`SRC/rules.py:169-172`), RD006 (`SRC/rules.py:584-653`), RD008 |
| 2 | `california_housing   -0.499` (line 82) | printed value of cell 2 (`:85`) | `{path, line: 82, text: "-0.499"}` | **DIRECT** | same |
| 3 | `print(df.groupby('dataset')['metrics.test.score'].mean().round(3))` (line 73) | render step evidence (`:17`) | `{path, line: 73, text: ".round(3)"}` | **DIRECT** (carried on `Transformation.grade`, not an EvidenceField — `REAL_WORLD_ONBOARDING_REPORT.md:283`) | RD006 chain (`SRC/rules.py:584-653`); also cites the `.mean()` on the same line for the aggregation centre — but see row 6 |
| 4 | `test score averaged over all random seeds` (line 70) | `wording:` on **both** cells (`:60, :86`) | `{path, line: 70, text: "averaged over all random seeds"}` | **DIRECT** | **No.** It lowers to `spread_label` and RD005 short-circuits to `NOT_APPLICABLE` before ever reading it (`SRC/rules.py:466-481`; the audit JSON's RD005 measurements contain only `{"spread": null}`). The pilot's own worksheet calls this "RD005 的 wording 证据" (`EVIDENCE_NOTES.md:60`) — the rule never consumes it. **Held at DIRECT, judged zero times.** |
| 5 | `adult` / `california_housing` row labels, `metrics.test.score` column label, `README metrics snippet` table name, and the hand-typed `quoted_text` strings (`:57, :83`) | `printed_in` | *none* — plain strings | **UNGRADED** (no `Grade` at all; `SRC/schema.py:88-94`) | RD008 builds its loci key from them (`SRC/rules.py:741`); nothing verifies them |
| 6 | `.mean()` (line 73, the centre of the aggregation) | *not cited anywhere* | — | — | The aggregation's centre is a bare enum: `aggregate: {center: mean}` (`:63, :88`) → `SRC/manifest.py:688` `self.enum(...)`, no door, no grade, no locator. `EVIDENCE_NOTES.md:59` marks "center = mean" as OBSERVABLE at `README.md:73`, but the manifest never observes it. **The one place the worksheet promises an observation and the shipped manifest does not take it.** |
| 7 | `*The output exactly matches Table 2 from the paper:*` (line 76) | absent | — | — | see §D.4 |
| 8 | `Path('output').glob('*/mlp/tuned/*/stats.json')` (line 66) — the README's own enumeration of the 15 seeds | absent | — | — | The glob would be exactly the "member rule as evidence" Paper Doctor might want; the contract forbids directory scanning (`EVIDENCE_NOTES.md:45` "OBSERVABLE-但禁止使用"), so `member_rule` stays **DECLARED** (`PILOT\result-doctor.yml:64, 89`) |

**Net:** the README is the *paper substitute*. Its numbers are DIRECT, its sentence about aggregation
is DIRECT-but-unjudged, and its sentence about the paper is unrepresented.

---

## E. Gap register (G1–G9, B1–B3) restated one-line each, with source and paper-side verdict

Source for G1–G9: `RD\phase4\REAL_WORLD_ONBOARDING_REPORT.md:314-324` (§16 "Generic contract gaps").
Source for B1–B3: same file `:330-344` (§17 "Bugs discovered"). Post-Phase-5 disposition:
`RD\phase5\RESULT_DOCTOR_PHASE5_REPORT.md:282-293` (§11) and `:52-56` (§2).

| # | one-line restatement | source | Phase-5 disposition | paper-side? (Paper Doctor's problem) |
|---|---|---|---|---|
| G1 | `{path, line}` returns the whole line, and real table rows always carry a row label, so a printed value read that way silently enters the comparison as `"adult   0.852"` → false RD001 FAIL | `:316` (§16), root cause §11(b)-1 `:197-203` | **closed at authoring time**: `_cell_field` refuses line-without-text with `E_LOCATOR_TEXT` (`SRC/manifest.py:383-396`; `PHASE5:118-136`) | **partly** — Paper Doctor's "locate a claim in a sentence" problem is the same shape; it needs fragment-level anchoring, not whole-line |
| G2 | `quantity:` does not tell the author it must carry row identity, so two rows of one table share a key and RD008 reports a fabricated conflict | `:317` | **closed at authoring time**: `_check_quantity_identity` → `E_MISSING_FIELD` (`SRC/manifest.py:1025-1042`; `PHASE5:140-160`) | **partly** — claim-identity scoping (one claim ↔ one cell ↔ one span) is exactly Paper Doctor's core keying problem |
| G3 | member identity cannot default to the member's own file, so each of 30 paths is written twice (60 of 73 `path:` uses) | `:318` | **partially**: sugar added (`_inherit_member_path` `:722-739`), `path:` 73→43, but full defaulting refused — "整条 identity 默认化会违反 §9/§10 与 Phase 3 防火墙 row 4" (`PHASE5:286, 95-106`) | **no** (authoring ergonomics) |
| G4 | `_size`'s outer `{value, statement}` and inner `declared:{value, statement}` doors cannot see each other; adding `note:` raised `E_BAD_FIELD` | `:319` | **closed** (UX2, `SRC/manifest.py:920-944`; `PHASE5:108-115`) | **no** |
| G5 | `E_UNKNOWN_KEY at .../aggregate` does not say that `members`/`member_rule` belong at cell level | `:320` | **still open** (`PHASE5:287` — "本轮只重写真实踩到的三条文本, 未顺手扩") | **no** |
| G6 | TOML/custom config values can only be quoted as whole lines, so a numeric declaration (`n_trials = 100`) can never be DIRECT — it is stuck at DECLARED | `:321`, worked case `:99, :107` | **still open** (`PHASE5:288` — no new locator family) | **YES, sharply** — a LaTeX/BibTeX/HTML paper value sits in exactly this situation: markup means the number is never alone on a line, so under the frozen grammar a paper number could only ever be DECLARED. Paper Doctor needs its own locator family or it inherits G6 forever |
| G7 | `selection:` can only bind to a cell, but real per-run epoch selection is per-member, so `sel:per-run-epoch` is written as an event bound to nothing | `:322`; visible as the third RD003 row `:162` | **still open** (`PHASE5:289`) | **no** for prose; **YES** in the analogous form "which run does this sentence refer to" (claim→run attribution is per-sentence, not per-table) |
| G8 | nothing points from `round` (banned step) to `format` (the legal render step) before the author hits the error | `:323` | **still open** (`PHASE5:290`) | **no** |
| G9 | **paper/PDF-side printed objects are entirely unreachable; a "printed value" can only come from text inside the repo** | `:324`, §15 last row `:301` | **explicitly still open, and named as such**: "本轮 README 假 FAIL 的修法是把片段写进 `text:`, 不是让工具读 PDF" (`PHASE5:291`) | **YES — this is Paper Doctor's reason to exist.** G9 is the single gap that *defines* the new tool's scope |
| B1 | `_size` + `door_of`: a legal `{value, statement, note}` size was rejected because the companion key alone made a non-empty "door" set, so `field()` saw 0 doors | `:333-336` (judged non-blocking) | fixed by UX2 | **no** |
| B2 | `{path, line}` and `{path, line, text}` return *different things* (whole stripped line vs fragment); existing design, but it is the mechanism of the §11(b)-1 false FAIL | `:337-339` | **closed** by the G1 guard at printed cells (`PHASE5:292`) | **partly** — Paper Doctor must decide, per locator family, what a read-back *is*; a mixed return type is a silent-misjudgement generator |
| B3 | `identity:` goes through the generic `field()`, so it can cite a value from **another file**; nothing in the grammar blocks a cross-file identity, and no test pins it down | `:340-341`; aggravated in `PHASE5:293, 300-301` ("糖衣让 identity 跨文件更易被误用, 但语法上仍无阻拦") | **still open, upgraded to "新增关注"** | **YES in kind** — "a claim located in file A but evidenced by a value read from file B, with no binding between them" is the *default* situation for paper-vs-repo auditing, not an edge case. Paper Doctor must make that edge *the object*, and must ship the firewall test Phase 4 never wrote |

Paper-side gaps, in one line: **G6, G9, B3 are Paper Doctor's problem; G1, G2, B2 are problems whose
shape recurs in Paper Doctor's locator design; G3, G4, G5, G7, G8, B1 are Result Doctor's authoring
ergonomics and can be left where they are.**

Two additions this inventory measured that are *not* in the register and belong to Paper Doctor:
- **The `printed_in` object is unverified (§C-3.2).** No gap entry covers it because no one tried to
  forge a locus. For a tool whose subject is "does the paper's prose match the paper's table", an
  unverified `quoted_text` is a first-order hole, not an ergonomic nit.
- **PDF input raises `UnicodeDecodeError` and exits 1, not `E_*` and not 2 (§C-3.1).** Also
  unregistered, because Phase 4 never attempted a PDF.

---

## F. The 30-member enumeration marginal-cost claim — measured

Claim under test (`REAL_WORLD_ONBOARDING_REPORT.md:131-132`): "每多审一个 cell 的边际成本是刚性的:
**+25 逻辑行**(15 行成员枚举 + 10 行元信息), 实测: 删掉第二个 cell 剩 85 行, 110 − 85 = 25",
restated as "one more cell = +25 logical lines, 15 of which are member enumeration".
Line-count method reused verbatim from `PHASE5:170`: total lines − pure-comment lines − blank lines.

| manifest | file lines | blank | comment | **logical** | cell 1 block | cell 2 block | member lines per cell | meta per cell |
|---|---|---|---|---|---|---|---|---|
| `PILOT\result-doctor.yml` (Phase 5, shipped) | 105 | 6 | 1 | **98** | 25 (`:56-80`) | **24** (`:82-105`) | 15 | 10 / 9 |
| `RD\phase5\rtdl-revisiting-models\result-doctor.phase4-before.yml` (Phase 4 snapshot) | 118 | 7 | 1 | **110** | 26 (`:66-91`) | **25** (`:93-117`) | 15 | 11 / 10 |

Verdict: **the claim is exactly true of the manifest Phase 4 measured, and off by one line for the
manifest that shipped.**

- `+15 member lines` — **confirmed in both versions**, 15 lines per cell, one flow-mapping line per
  seed (`PILOT\result-doctor.yml:66-80, 91-105`).
- `+25 total` on the Phase 4 snapshot — **confirmed**: cell 2 = 25 logical lines (10 meta + 15), and
  the report's own delete-test `110 − 85 = 25` reproduces.
- On the Phase 5 file the marginal second cell is **24** (9 meta + 15), because Phase 5 folded each
  cell's `aggregate:` from two lines into one (`PHASE5:192` "两个 `aggregate:` 由 2 行改 1 行 flow",
  −2 lines total). The `+25` headline was never re-measured after that change.
- The two cells are not symmetric: cell 1 costs one line more than cell 2 because it alone carries a
  `selection:` binding (`PILOT\result-doctor.yml:62`). So the honest marginal cost of "one more cell,
  wired like the second one" is **24**, and of "wired like the first, with a selection event" is **25**.
- Enumeration share of the whole file: 30 / 98 = **30.6%** (matches `PHASE5:299` "30 行 = 全文 30.6%"),
  against Phase 4's 30 / 110 = 27% (`REAL_WORLD_ONBOARDING_REPORT.md:128`). The share *grew* because
  the fixed overhead shrank.
- Average member line length measured **182.17 chars** (matches `PHASE5:178` "182"), longest member
  line 207 in Phase 4's after-state.
- Cost of auditing the whole README column (11 datasets, `PILOT\README.md:80-90`): Phase 4 projected
  `85 + 10 × 25 = 335` logical lines (`:134`). Re-based on the shipped file: `74 + 10 × 24 = 214`, or
  `74 + 10 × 25 = 324` if every cell binds a selection event. Both are far past the 100-line budget;
  the underlying tension the pilot named — "`≤100 逻辑行` 与 `禁止目录扫描决定成员` 互相冲突"
  (`:363`) — is unresolved by design, and Paper Doctor will hit it immediately: one table column of
  prose claims is dozens of objects.

---

## G. What this pilot therefore proves, and what it leaves untouched

**Proves (frozen, re-measurable today):**
1. A project with **no adapter, no fixture, zero code change** enters the 8-object Bundle through one
   YAML + the artifacts it quotes, and RD001–RD008 all produce findings — 6 real PASS from
   re-computation (`PILOT\result-doctor.yml` → 15 DIRECT JSON-pointer reads × 2 cells, mean,
   `format(fixed,3)`, string-equality against the printed fragment).
2. The honesty machinery holds under real pressure: `partial`/`unknown` universes, UNKNOWN direction
   and tie-break, no spread, no comparison set produce INCONCLUSIVE / NOT_APPLICABLE / NOT_RUN —
   10 of 16 findings — and never a fabricated PASS (`REAL_WORLD_ONBOARDING_REPORT.md:172-186`).
3. Two silent-misjudgement failure modes (G1, G2) can be converted into *loading-time refusals*
   without touching any rule (`PHASE5:118-166`), and the conversion is pinned by tests
   (`RD\tests\test_phase5_ux.py`, 13 cases; gate `161 passed`, `PHASE5:265-273`).
4. The output is deterministic and portable: `sha256 = 2ad02c8f…`, 13,395 B, 0 CR, reproduced here
   byte-for-byte (§B.2).
5. `GRADE` semantics are enforceable and cheap to reuse: only DIRECT/DECLARED/UNKNOWN exist on this
   path, `INFERRED`/`DERIVED` are test-pinned to never appear.

**Leaves untouched (Paper Doctor's actual workload):**
1. The paper itself — G9. Not one byte of arXiv 2106.11959 was read; the README stood in for it, and
   the pilot's own strongest paper-facing sentence (`README.md:76`) was dropped rather than modelled.
2. Prose claims of any kind. The grammar has no claim object; the single sentence slot that exists
   (`wording:`/`spread_label`) is (a) semantically forced to mean "what the ± is", and (b) in this
   pilot held at DIRECT and read by zero rules. The README's real claims — "MLP-like models are still
   good baselines" (`PILOT\README.md:15`), "the best average performance among deep models" (`:28`),
   "FT-Transformer reduces (not completely) the gap between GBDT and DL" (`:30-31`) — are
   unrepresentable.
3. Locus verification. `printed_in` is ungraded free text; a forged `quoted_text` and a bogus `page`
   load happily (§C-3.2).
4. Non-UTF-8 input. A PDF raises an uncaught `UnicodeDecodeError` and exit 1 (§C-3.1).
5. Cross-object reachability of referenced files. Candidate members and `chosen:` refs are strings the
   loader never opens (§C-3.4) — so "the promoted artifact exists" is not something Result Doctor ever
   checked, in a pilot whose central selection event is precisely that artifact.
6. Anything beyond one column of one table: 2 cells of 11 datasets, 1 of ~30 tables, 1 of 12 models,
   and per the brief "本轮不评价论文本身" (`REAL_WORLD_ONBOARDING_REPORT.md:354`).

**The sharpest single design constraint this inventory hands to Paper Doctor:** the pilot's only
faithful *prose-claim* representation was `wording: {observed: {path: README.md, line: 70, text:
"averaged over all random seeds"}}` — DIRECT evidence, and then no rule ever looked at it. Locating a
sentence is the easy half; giving a sentence a predicate that a rule can execute is the whole job.
