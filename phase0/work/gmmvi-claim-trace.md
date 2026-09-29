# P0.2 — Paper A (GMMVI, arXiv 2209.11533v2) claim → evidence reverse trace

AUTHORITATIVE input for `PAPER_DOCTOR_PHASE0_REPORT.md` §8. Every row was re-verified in
this session against the vendored source; nothing here is copied from a handoff summary.

Paper identity (OBSERVED-DIRECT):
- e-print `phase0/sources/2209.11533v2.eprint`, 844305 B, sha256
  `a2496e282bb4bb262e28bac0cd1a542ccb86f3ee93fcfabd6159f6c48db09516`
- unpacked main source `sources/2209.11533v2.tex/arxiv.tex`, 1460 lines, `\title` at :72
- float numbering recomputed by `scripts/float_ref_map2.py` → `work/gmmvi-float-ref.json`
  (nesting depth 1; 9 tables, 3 figures; `tab:exp1` = **Table 2**, `tab:exp1_eval` = **Table 3**,
  `tab:exp3` = **Table 5**, `tab:exp3_full` = **Table 8**, `tab:exp3_accuracy` = **Table 9**)

Downstream authority (OBSERVED-DIRECT, re-run this session with the frozen v0.1.0 API):
`load_gmmvi_bundle(r'F:\MLResearch\experiment-doctor\phase0-gmmvi')` + `evaluate(bundle)` →
**538 findings**: PASS 165 / INCONCLUSIVE 293 / NOT_APPLICABLE 69 / FAIL 11.
Bundle: 59 ReportedResult, 46 Aggregation (44 declare 10 members, 2 declare 30), 500 members
(466 included / 34 excluded), 128 ResultArtifact, 3 Transformation, 100 CandidateSet,
98 SelectionEvent, 5 ComparisonSet.

---

## A-1  Real claim ledger

`grade` column = the grade of the *link* between claim and evidence, not of the number.

| # | claim (verbatim fragment) | locator | support target (evidence) | RD object / finding | diverges? | owner | PD rule | verdict |
|---|---|---|---|---|---|---|---|---|
| C1 | "the optimistic value provided in **Table~\ref{tab:exp1_eval}** for BreastCancer (**$78.69$**)" | `arxiv.tex:426` | `78.69` occurs exactly once in the file: `:408`, inside the env opened at `:400` whose `\label{tab:exp1}` is at `:416` ⇒ Table **2**, not Table 3 | none — RD never resolves `\ref`; `tab:exp1_eval` is not a bundle object | **YES, deterministic** | **PD only** | PD006 | **FAIL** |
| C2 | "The results … are summarized in **Table~\ref{tab:exp1}**, where we report the **best ELBO** … optimistic" | `arxiv.tex:424` | `tab:exp1` caption `:415` "We show optimistic estimates of the best performance (negated ELBO)" | n/a | no (C1's own antecedent) | PD | PD006 | PASS-anchor (and proves C1 contradicts C2) |
| C3 | "The values in **Table~\ref{tab:exp1}** give an optimistic estimate" | `arxiv.tex:426` (1st) | caption `:415` | n/a | no | PD | PD006 | PASS |
| C4 | "evaluated the performance **over ten seeds**. The mean … and its **$99.7\%$ standard error** are shown in Table~\ref{tab:exp1_eval}" | `arxiv.tex:426` (2nd) | manifest: 44/46 aggregations declare `member_ids` of size 10; spread_form `k_sem(k=3.0, ddof=0)` | RD002 = INCONCLUSIVE ×46 ("cannot be bound to an external run id"); RD005 consumes the wording as `spread_label` (DECLARED) | no contradiction at declared level; **unverifiable at member level** | PD (scope) + RD (mechanics) | PD002 | **INCONCLUSIVE** (declared 10, RD cannot bind members to runs) |
| C5 | "3σ confidence intervals based on the standard error of its mean **using ten different seeds**" | `arxiv.tex:625` (Table 5 caption) | `spread_form` census: n=10 ×37, **n=4 ×4, n=5 ×1, n=7 ×1, n=8 ×1, n=30 ×2** | RD005 emits `n` as a *measurement* (`rules.py:513`) but only judges family se-vs-std (`rules.py:529-567`); it never compares the *number stated in wording* with the recomputed `n` | **YES for 9 aggregations** | **PD only** (RD is frozen and structurally cell-scoped) | PD002 + PD005 | **FAIL-grade divergence recorded as INCONCLUSIVE→FAIL boundary case** (see §note-1) |
| C6 | "We observed instabilities for **{\sc Sepyfux} on** *PlanarRobot* and *TALOS* and, thus, removed bad outliers when computing the reported values" | `arxiv.tex:625` | exclusion census (OBSERVED-DIRECT from bundle): `PlanarRobot/sepyfux`(5), `PlanarRobot/sepyrux`(3), **`PlanarRobot/zamtrux`(2)**, `TALOS/sepyfux`(6), `TALOS/sepyrux`(6), `TALOS/sepyfux/entropy`(6), `TALOS/sepyrux/entropy`(6) | `Exclusion.listed` DIRECT, `reason_grade`=DECLARED, `criterion_recomputable`=False; RD002 reason adds "an exclusion criterion is not recomputable" | **YES: removals were applied to `sepyrux` and `zamtrux`, which the sentence does not name** | **PD only** | PD005 | **FAIL** (qualification under-scoped vs evidence) |
| C7 | "The proposed candidate **clearly outperforms** the prior methods {\sc VIPS} and {\sc iBayes-GMM}" | `arxiv.tex:625` | `ComparisonSet` ×5 (`cmp:{env}`), `external_origin` carries VIPS/iBayes-GMM rows; per-column best marks recomputable by RD007 | RD007 targets **marks**, not prose; `STM300/zamtrux` and `TALOS`-side N/A cells exist | "clearly" has no declared threshold, direction, or test | PD | PD004 | **INCONCLUSIVE** (bare comparative, undeclared margin) |
| C8 | "best-performing candidate (**{\sc Samtron}**)" + "aim to better compare … resulting in six candidates" | `arxiv.tex:475` | Table 5 col-wise best marks: `{\\sc Samtron}` bold on GermanCredit 585.10, PlanarRobot 11.47; **GermanCreditMB 585.12 is bold for BOTH Samtron (`:576`) and Sepyfux (`:602`)** with `±\\num{0.00}` on both | RD007 (`observed_marks` vs `recomputed_marks`) owns the double-bold | tie not acknowledged in prose | RD (marks) / PD (superlative) | PD004 | **INCONCLUSIVE** — RD007 is the authority on whether the marks are consistent; PD must consume, not recompute |
| C9 | "First-order natural gradient estimates with trust-region constraints (**T**) seem preferable over the iBLR update (**Y**)" | `arxiv.tex:625` | Table 2 rows `Direct (I)` / `iBLR (Y)` / `Trust-Region (T)` at `:407-409` | not modelled (Table 2 is a design-choice ablation, no runs vendored for it) | unknown | PD | PD004 | **INCONCLUSIVE** (target artifact not in the audited universe) |
| C10 | "the same quantity printed twice" STM300/sepyfux `-elbo`: Table 5 `26.87 ± 0.45` (`:607`) vs Table 8 `26.69 ± 0.39` (`:1211`) | `arxiv.tex:607`, `:1211` | RD **already rules on it**: `RD008 | quantity:STM300/sepyfux/-elbo | the same quantity is printed with different values in two products` = **FAIL**; `RD001 …/Table 5` = INCONCLUSIVE (rep 26.87/0.45 vs rec 26.69/0.39); `RD005 …/Table 5` = FAIL | RD001/RD005/RD008 | YES — **owned by RD** | **RD** | (PD would duplicate ⇒ deleted candidate) | n/a |
| C11 | BreastCancer/samtron `-elbo` Table 5 `78.00 ± 0.02` (`:1023` area) vs recomputation from its 10 members `78.01 ± 0.01` | `arxiv.tex:573` | `RD001 INCONCLUSIVE BreastCancer/samtron/-elbo/Table 5` (measured above) | RD001 | YES — **owned by RD** | **RD** | (duplicate ⇒ deleted) | n/a |
| C12 | `BreastCancer/sepyrux/-elbo/Table 8` dispersion `0.93` — no family reproduces it | `:1285`-area row | `RD005 FAIL` with `families_matching_published_spread: []` (renderings std .83/.88, sem .26/.28, k_sem .79/.83) | RD005 | YES — **owned by RD** | **RD** | (duplicate ⇒ deleted) | n/a |
| C13 | "around one order of magnitude more efficient" | `arxiv.tex:1453` | no artifact, no table, no declared measurement | none | unmeasurable | PD | PD004/PD007 | **NOT_APPLICABLE→INCONCLUSIVE** boundary; v0.1 = INCONCLUSIVE, "no support target declared" |
| C14 | GermanCredit "is $25$-dimensional" vs the same appendix text listing per-dataset dimensions "The dimensions are $25$ and $31$, respectively" | `:472` vs `:995` | paper-internal; no artifact | none | **consistent for GermanCredit (25)** | PD | PD007 | PASS on the checked pair (recorded to prove the rule can PASS) |
| C15 | TALOS "target distribution is **34** dimensional (7 joint configurations for each leg, 6 joint angles for each arm and 6 additional parameters…" | `arxiv.tex:472` | arithmetic 2·7 + 2·6 + 6 = 32 ≠ 34 | none | apparent, **but requires prose arithmetic parsing** | **non-goal v0.1** | — | **SEARCHED / NOT OBSERVED as rule-coverable** — see §note-2 |

note-1 — C5 boundary decision (frozen in §12 of the report): the wording "using ten different
seeds" is a *procedure* statement. RD's `SpreadForm.n` is DERIVED from the surviving member
count and RD001 PASSes with it (e.g. `TALOS/sepyfux` n=4 reproduces `−16.64 ± 5.26`
digit-for-digit). So the evidence says the printed dispersion is a 4-member statistic while
the caption states a 10-seed procedure. PD's verdict is **FAIL on PD002 scope** *only if* the
author declares the caption applies to every cell of Table 5; RD's loader applies the caption
clause to all 56 cells as `spread_label` (LDR:126 → grade DECLARED), which is exactly such a
declared scope. Hence FAIL is supported; the finding is "caption-scoped procedure statement
does not hold for 9 of 46 aggregations", not "the paper is wrong".

note-2 — C15 was tested as a candidate PD rule ("prose arithmetic decomposition"). It is
rejected for v0.1 because checking it needs to bind "each leg/each arm" to multiplicands,
i.e. semantic parsing, which the firewall forbids. Recorded as `SEARCHED / NOT OBSERVED
as a deterministically checkable relation`.

---

## A-2  Claims hypothesised but NOT OBSERVED

| hypothesis | search performed | outcome |
|---|---|---|
| Table 5 mixes metrics (accuracy vs RMSE vs negated ELBO) across columns | read `:569-570` header + `:625` caption + Table 8 `Metric` column | **REJECTED**: caption declares "the negated ELBO" for the whole table; magnitudes are consistent with dimensionality, not with two metrics. Cited as evidence that a suspicion is not a finding. |
| `tab:exp1_eval` (Table 3) values are never cross-checked | `grep 78\\.69` | only `:408`; Table 3 rows use different values — supports C1 |
| bold-mark inconsistency inside Table 8 rows | `:575/:576/:601/:602` | exists ⇒ **RD007 owns it**, excluded from PD scope |
| figure reference errors | `float_ref_map2.py` unresolved-ref scan | none for tables/figures; 32 bogus `\ref{#N}` sites (21 `#1` + 11 `#2`-style) come from `math_commands.tex` macro **definitions**, not claims ⇒ validation-taxonomy input (§13). Total unresolved = 95 (32 in `math_commands.tex`, 63 in `arxiv.tex`, the latter mostly `eq:`/`app:` targets which are out of universe by §13 non-goals) |
| `\ref{tab:exp3_accuracy}` orphan | never_referenced = `['tab:exp3_accuracy']` | OBSERVED: Table 9 is never referenced by any prose. Recorded as a measurement, **not a finding** (absence of a claim is not a claim-evidence mismatch) |
