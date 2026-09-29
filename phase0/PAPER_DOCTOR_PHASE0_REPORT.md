# PAPER DOCTOR — PHASE 0: CLAIM / EVIDENCE DESIGN

Date: 2026-09-29 · Status: **CLOSED — GO** · Author: Phase 0 macro-cycle
Location: `F:\MLResearch\paper-doctor\phase0\PAPER_DOCTOR_PHASE0_REPORT.md`
Authority marks used below: **AUTHORITATIVE** (defines the frozen design), **SUPPORTING**
(first-hand evidence), **TEMPORARY** (may be revised by Phase 1 without reopening Phase 0).

---

## 1. Verdict

**GO.** Paper Doctor has a real, non-redundant function that no released layer performs, that
function is expressible as deterministic rules over explicitly declared links, and the design
is frozen below to the point where Phase 1 can be implemented without re-running this research.

Six facts carry the verdict, all first-hand in this session:

1. Result Doctor's frozen v0.1.0 source models *printed result loci* but has **no claim object,
   no prose object, and no reference resolver**. `schema.py` defines 8 objects; none of them
   can state "sentence S of the paper attributes value V to Table N".
2. In the GMMVI pilot RD reads the paper only as a *transcription source*: `loaders/gmmvi.py:126`
   stores the Table 5 caption clause as `spread_label`, grade DECLARED, applied to 56 cells.
   That single string is the whole paper prose inside the bundle.
3. In the RTDL pilot RD never reads the paper at all: both cell `value:` locators point at
   `README.md:80` and `README.md:82`; the RTDL bundle is 2 reported results / 2 aggregations /
   30 members / **0 artifacts** / 1 transformation / 2 candidate sets / 2 selection events /
   **0 comparison sets** (`artifacts: 0` because the pilot manifest references only the README,
   not the run tree). `evaluate(bundle)` yields 15 findings and `audit_manifest(path)` yields
   **16** — the extra line is `RD007 / rule:RD007 / NOT_RUN`, appended because RTDL has zero
   comparison sets, which is exactly the partial-audit channel Contract I-1 must preserve
   (`work/rtdl-audit-from-pylib.json`, re-hashed this session, MATCH `2ad02c8f…`).
4. A deterministic paper-level defect exists that no rule in RD001–RD008 can express
   (§9 C1): `arxiv.tex:426` attributes the value `78.69` to `Table~\ref{tab:exp1_eval}`
   (= Table 3), while `78.69` occurs exactly once in the file, at `:408`, inside the float
   labelled `tab:exp1` (= Table 2).
5. Five further claim-level divergences were reproduced from primary sources across the two
   papers (§9, §10), including one where the paper's own exclusion enumeration is narrower
   than the exclusion records in the audited evidence.
6. Every divergence found is *judged by evidence already on file*, so the auditor needs no
   new experiment, no retraining, and no model.

## 2. The question Paper Doctor answers — and nothing else

**AUTHORITATIVE.** Paper Doctor answers exactly one question:

> Which evidence supports a substantive empirical claim in a paper, and does that claim
> faithfully represent the reported evidence with respect to **value, comparison direction,
> scope, qualification, and reference**?

It closes the last edge of the provenance chain:

```
dataset (Dataset Doctor 0.1.2, FROZEN)
  → runs / experiment context (Experiment Doctor 1.0.0, FROZEN)
    → reported result R vs. producing evidence (Result Doctor 0.1.0, FROZEN/VERIFIED)
      → paper claim C vs. reported evidence R        ← Paper Doctor (this design)
```

Paper Doctor is **not** an AI reviewer. It never outputs: paper quality, credibility, an
accept/reject prediction, a novelty judgment, a misconduct accusation, a cherry-picking
detection, or a global score. `PASS` means only "on this one narrow relation the claim agrees
with the evidence"; it never means "the claim is true in the world".

## 3. Frozen upstream baseline (P0.0) — SUPPORTING

Verified before anything was designed, so this report is not built on memory:

| item | value |
|---|---|
| Result Doctor release tag | `v0.1.0` → tag object `5b87cba` peeled to `bec3ab9`; docs commit `1a7bc18` |
| PyPI artifacts | wheel 57,593 B `54b3ddd9…`, sdist 78,008 B `e054b57c…` (same commit, two builds; Windows vs ubuntu differ only in METADATA/RECORD) |
| content identity | `2ad02c8fb6ace0af325c2bc50c08eb9f0162e77b25c659e96951df96f694a660` |
| test suite | 170 passed (re-run this session, background) |
| Dataset Doctor | 0.1.2 RELEASED / FROZEN — accepted, not re-proved |
| Experiment Doctor | 1.0.0 RELEASED / FROZEN (release `fb3a242`, HEAD `3d1adc2`) — accepted |
| Paper Doctor | was NOT STARTED; this phase is the first artifact |

The historical GitHub OAuth-token-in-transcript incident is treated as **RESOLVED** and is not
listed as a blocker anywhere in this report.

## 4. The Result Doctor contract, frozen from v0.1.0 source (P0.1) — AUTHORITATIVE

Read from source, not from any handoff summary. Files: `src/result_doctor/{schema,evidence,
status,bundle,audit,rules,manifest,cli}.py`.

**8 objects** (`schema.py`, 313 lines): `ResultArtifact`, `Aggregation`, `AggregationMember`,
`Exclusion`, `MemberRule`, `ProducedBy`, `Transformation`, `CandidateSet`, `SelectionCriterion`,
`SelectionEvent`, `ComparisonSet`, `PresentationRule`, `SpreadForm`, `RunRef`, `Locus`,
`ReportedResult` (the object-level grouping is 8 top-level collections; the dataclasses above
are the field vocabulary).

**Evidence grammar** (`evidence.py`): `Grade{DIRECT, DERIVED, DECLARED, INFERRED, UNKNOWN}`,
`SourceRef(path, key, line, artifact_id, note)`, `EvidenceField(value, grade, sources, note)`.

**Statuses** (`status.py`): `RuleStatus{PASS, FAIL, INCONCLUSIVE, NOT_APPLICABLE, NOT_RUN}`,
`UniverseStatus{UNKNOWN, RECOVERED, PARTIAL, DECLARED_ONLY, UNRECOVERABLE}`,
`RuleFinding(rule_id, rule_name, target, status, question, measurements, evidence, reason)`,
`canonical_json(findings)` = `json.dumps(..., sort_keys=True, separators=(",",":"),
ensure_ascii=False)` with no timestamps.

**Locator families** — exactly 4, branched by key set: `{path,column,row}`, `{path,key}`,
`{path,line[,text]}` (no `text` ⇒ whole stripped line, with `text` ⇒ fragment), `{path,text}`.

**Error codes** — exactly 26, extracted from `manifest.py` this session:
`E_ARTIFACT_MISSING E_BAD_DIRECTION E_BAD_ENUM E_BAD_FIELD E_CONFLICTING_REF E_DUPLICATE_ID
E_LOCATOR_COLUMN E_LOCATOR_KEY E_LOCATOR_KEYS E_LOCATOR_LINE E_LOCATOR_ROW E_LOCATOR_TEXT
E_MARK_DERIVATION E_MISSING_FIELD E_NOT_A_NUMBER E_PATH_OUTSIDE_ROOT E_RENDER_STEP E_ROOT
E_SCHEMA_VERSION E_STEP_NOT_APPLIED E_TOP_LEVEL E_TYPE E_UNIVERSE_EVIDENCE E_UNKNOWN_KEY
E_UNRESOLVED_REF E_YAML`.

**Driving classes** (`audit.py:~40`): RD001/RD005/RD006/RD008 read `reported_results`
(RD008 also `artifacts`/quantity groups), RD002 `aggregations`, RD003 `selection_events`,
RD004 `candidate_sets`, RD007 `comparison_sets`; `NOT_RUN` is supplied by the entry layer when
a class is empty.

**CLI** (`cli.py:142-149`, verified this session): `result-doctor audit <path|dir> [--json
REPORT_JSON]`; exit codes 0 = audit ran whatever it found, 2 = manifest is not a readable
contract, 1 = tool failure. `write_json()` uses `newline="\n"` so the byte-identical report is
platform-independent.

**Reuse is mandatory, re-invention is forbidden.** PD reuses `SourceRef`, `EvidenceField`,
`Grade`, `RuleFinding`, `canonical_json`, `RuleStatus`, `UniverseStatus`, `ResultArtifact`,
`Locus.quantity_key` and the 4 locator families verbatim.

## 5. Where Result Doctor structurally stops — SUPPORTING, and it is the whole justification

First-hand gaps, each tied to source:

| gap | evidence |
|---|---|
| No claim/prose object of any kind | `schema.py`: `ReportedResult` = rid + `Locus` + value/spread + refs; there is no field that can hold a sentence, a quantifier, or a comparison predicate |
| Never resolves `\ref`/`\autoref`; no float numbering | `rules.py` (835 lines, read in full) contains no LaTeX reference logic; `manifest.py`'s `E_UNRESOLVED_REF` validates *manifest* id references, not paper cross-references |
| Does not verify `quoted_text` / `printed_in` | `manifest.py:1081-1089` — ungraded plain strings; a forged locus loads silently |
| Wording is only ever *classified*, never *judged against a claim* | `rules.py:563-567` fallthrough: `wording {label!r} is not classifiable against {form}` → INCONCLUSIVE. This is exactly what RD005 emits for RTDL's "averaged over all random seeds" |
| States a *number* in prose is invisible to it | `rules.py` RD005 computes `n = len(values)` and emits it as a measurement, but compares only wording **families** (se vs std), never a stated count ("ten different seeds") |
| Cannot read a PDF | `UnicodeDecodeError` → exit 1; it reads `.tex` only |

**Consequence frozen:** PD consumes RD's verdicts and measurements as *evidence*; it never
recomputes what RD already decided, and it never treats RD's DECLARED wording as proof.

## 6. Integration options compared (P0.1b) — SUPPORTING

Scored on the nine required axes. 1 = worst, 3 = best.

| axis | A: import RD Python API | B: RD canonical JSON file | C: manifest cross-reference | D: minimal stable interface (`audit_manifest()` returning findings objects) |
|---|---|---|---|---|
| coupling | 1 — pins PD to RD internals (`schema.py` dataclasses, `loaders/`) | 3 — zero import; the 8-key finding dict is the contract | 2 — needs both file path and id convention | 2 — pins PD to a function signature and to RD's installed package |
| version stability | 1 — any v0.1.1 field rename breaks PD silently | 3 — `canonical_json` is byte-frozen by RD's own tests | 3 — ids are stable | 2 — public but not byte-frozen |
| provenance preservation | 3 | 3 — each finding carries `evidence[]` SourceRefs | 2 | 3 |
| determinism | 2 (depends on RD import-time state) | 3 (byte-identical, re-hashed) | 3 | 2 |
| third-party onboarding | 1 (must install RD) | 3 (one JSON file + a schema doc) | 2 | 1 |
| standalone usability | 1 | 3 — PD runs on a findings file from any producer | 2 | 1 |
| circular-dependency risk | 3 | 3 | 3 | 2 (PD→RD import; RD must never import PD) |
| future compatibility (ED/other producers) | 1 | 3 — the finding shape is producer-agnostic | 2 | 2 |
| risk of tempting RD modification | 3 (highest: convenience pushes edits) | 1 | 2 | 2 |

Two observed facts decide it:
* **NaN hazard (first-hand).** `work/rtdl-audit-from-pylib.json` contains
  `"recomputed_dispersion": NaN` — a bare `NaN`, legal to Python's `json.loads`, **illegal in
  strict JSON**. Any non-Python consumer of Option B fails. This is not a reason to touch RD
  (its bytes are frozen and hash-verified); it is a reason for PD to define a parsing policy.
* **Option B is already a shipped, tested contract.** `result-doctor audit --json` is covered by
  RD's own 9 CLI↔API non-drift assertions in `tests/test_cli.py`. Choosing B means PD depends
  on something RD already guarantees, not on something new.

## 7. Frozen integration contract — AUTHORITATIVE (Contract I-1)

```
PD consumes exactly one upstream artifact:
  rd_findings.json  :=  output of `result-doctor audit <project> --json <file>`
```

1. PD **never imports `result_doctor` at runtime** and never modifies it. RD 0.1.0 is read-only.
2. PD's manifest records, as OBSERVED-DIRECT: the file path, its sha256, its byte size, and the
   RD version string (`result-doctor --version`). A missing or mismatched hash is a
   **VALIDATION ERROR**, never a scientific finding.
3. PD indexes findings by the pair `(rule_id, target)`, using only the 8 keys
   `rule_id rule_name target status question measurements evidence reason`. Anything else in
   that file is ignored; nothing may be invented to fill a gap.
4. PD reads `measurements` for: `n_members`, `reported_center`, `reported_dispersion`,
   `rendered_center`, `rendered_dispersion`, `recomputed_center`, `recomputed_dispersion`,
   `families_matching_published_spread`, `declared_form`, `spread_label`,
   `spread_label_grade`, `n`, and the exclusion census `n_exclusions`,
   `n_exclusions_listed`, `n_exclusions_unlisted`, `n_exclusions_unbound_to_members`,
   `exclusion_criterion_recomputable`, `member_rule_grade`, `member_rule_kind` (all present in
   the frozen GMMVI output; re-read from `work/rd002-exclusion-visibility.txt`).
   `evidence[]` SourceRefs are propagated into PD's own findings so provenance survives one hop.
5. **Status propagation is not optional.** PD maps a downstream status into its own verdict and
   never upgrades it: RD `FAIL` → PD may not PASS the claim that depends on it (PD emits
   `INCONCLUSIVE` with the propagated reason); RD `INCONCLUSIVE` → PD `INCONCLUSIVE`;
   RD `NOT_RUN`/`NOT_APPLICABLE` → PD records "no downstream judgment exists" and may still
   judge relations RD cannot see (e.g. prose↔prose).
6. `NaN` policy (frozen): a `NaN` measurement is treated as **UNKNOWN**, never coerced to 0.0,
   never compared numerically, and named in the finding's reason. PD parses with
   `json.loads(..., parse_constant=...)` only for the purpose of detecting it.
7. One-way dependency: RD has no knowledge of PD. No RD file is edited. If a genuine RD P0/P1
   defect is ever found, it is documented → reproduced → classified, and never fixed in passing.

## 8. Method — SUPPORTING

Internal ledger P0.0 → P0.13, executed as large blocks: `真实 claim → locator → evidence →
RD object → mismatch opportunity → responsibility owner → proposed rule → counterexample`.

* Every number in §9–§10 was re-derived from the primary artifact in this session. Handoff
  narrative numbers are treated as **UNVERIFIED**; where they disagreed with a tool output the
  tool output won (see the correction in §10 B-3: the "6/11 exact, 4 sign-flipped" figure from an
  earlier draft is **superseded and must not be cited**, because only 3 of 11 datasets are
  vendored).
* Grades: OBSERVED-DIRECT / DECLARED / DERIVED-from-explicit / INFERRED / UNKNOWN. **INFERRED is
  never promoted to fact**; any heuristic linker emits at most `SUGGESTED`.
* Two paper sources vendored with sha256 (§9, §10 headers). Float numbering recomputed by
  `scripts/float_ref_map2.py` (recursive `\input` flattening, source-order numbering, nesting
  depth verified = 1) → `work/gmmvi-float-ref.json`, `work/rtdl-float-ref.json`.
* Read-only research was parallelised; every subagent hit was re-verified by the lead before
  entering this report ("agent understood it" is not evidence).

## 9. Paper A — GMMVI (arXiv 2209.11533v2) reverse trace

Full ledger: `work/gmmvi-claim-trace.md`. Headline rows:

| # | claim | locator | evidence | RD can see it? | owner | rule | verdict |
|---|---|---|---|---|---|---|---|
| C1 | "the optimistic value provided in **Table~\ref{tab:exp1_eval}** for BreastCancer (**$78.69$**)" | `arxiv.tex:426` | `78.69` occurs once, `:408`, in the float whose label `tab:exp1` is at `:416` ⇒ **Table 2**; `tab:exp1_eval` ⇒ **Table 3** | no | **PD** | PD006+PD003 | **FAIL** |
| C2 | "summarized in Table~\ref{tab:exp1} … **optimistic** … best ELBO" | `:424` | Table 2 caption `:415` "We show optimistic estimates of the best performance (negated ELBO)" | no | PD | PD006 | PASS (and it is C1's own antecedent — the paper contradicts itself within one paragraph) |
| C5 | "3σ confidence intervals based on the standard error of its mean **using ten different seeds**" | `:625` | `SpreadForm` census: n=10 ×37, **n=4 ×4, n=5 ×1, n=7 ×1, n=8 ×1, n=30 ×2** | RD emits `n` as a measurement, judges only se-vs-std family | **PD** | PD002 | **FAIL** (declared caption scope covers all 56 cells via `spread_label`; 9 of 46 aggregations do not compute over ten seeds) |
| C6 | "instabilities for **Sepyfux** on PlanarRobot and TALOS … removed bad outliers" | `:625` | exclusion records: PlanarRobot/sepyfux(5), PlanarRobot/**sepyrux**(3), PlanarRobot/**zamtrux**(2), TALOS/sepyfux(6), TALOS/**sepyrux**(6) + two entropy twins | RD002/RD004 see the mechanics only | **PD** | PD005 | **FAIL** — the enumeration names one method; the evidence excludes members for three |
| C7 | "**clearly outperforms** the prior methods VIPS and iBayes-GMM" | `:625` | 5 ComparisonSets; per-column best marks recomputable | RD007 owns marks | PD | PD004 | **INCONCLUSIVE** — "clearly" has no declared threshold/test |
| C10 | Table 5 `26.87 ±0.45` (`:607`) vs Table 8 `26.69 ±0.39` (`:1211`) for the same quantity | `:607`,`:1211` | **`RD008 FAIL quantity:STM300/sepyfux/-elbo`**, `RD001 INCONCLUSIVE …/Table 5` (rep 26.87/0.45 vs rec 26.69/0.39), `RD005 FAIL …/Table 5` | **yes — RD already rules on it** | **RD** | (duplicate ⇒ deleted) | n/a |
| C11 | BreastCancer/samtron Table 5 `78.00 ±0.02` vs recomputed `78.01 ±0.01` | `:573` | `RD001 INCONCLUSIVE BreastCancer/samtron/-elbo/Table 5` | yes | RD | deleted | n/a |
| C12 | dispersion `0.93` reproduced by no family | Table 8 row | `RD005 FAIL` with `families_matching_published_spread: []` | yes | RD | deleted | n/a |

Baseline re-run this session: **538 findings** = PASS 165 / INCONCLUSIVE 293 / NOT_APPLICABLE 69
/ **FAIL 11**. The 11 FAILs are RD003 ×4 (promoted config is not the champion), RD005 ×2, RD008
×5 (1 quantity + 4 artifact-identity). RD002 is INCONCLUSIVE on **all 46** aggregations
("member(s) cannot be bound to an external run id") — so PD cannot lean on RD002 here, which is
why PD002 must degrade to INCONCLUSIVE rather than FAIL when the scope claim depends on an
unbound universe.

**Unit note for C5 (matters for Phase 1).** The census `n=10 ×37, n=4 ×4, n=5 ×1, n=7 ×1, n=8 ×1,
n=30 ×2` is over the **46 aggregations** (`spread_form.n`, captured in
`work/agg-n-census.txt`); the 9 aggregations whose declared `n` ≠ 10 are the 7 exclusion carriers
plus `STM300/samyrux/{-elbo,num_detected_modes}`. The same field read over the **59 RD005 findings**
gives a different histogram — `{10: 44, 4: 5, 5: 2, 7: 1, 8: 2, 30: 2, None: 3}`
(`work/rd005-n-census.txt`) — because several aggregations feed several printed cells and 3 cells
carry no spread form at all. PD002 must state which unit it compared against in the reason string;
"9 of 46" and "12 of 56 labelled cells" are both true and are not the same statement. The
`spread_label` itself is a single string on **56** findings
("3σ confidence intervals … using ten different seeds"), 3 findings have none — which is why the
caption's declared scope reaches all 56 cells and C5's FAIL is a scope contradiction rather than a
missing-evidence case.

Hypothesised and **rejected by evidence** (recorded so nobody re-raises them): Table 5 mixes
metrics across columns — REJECTED, `:625` declares "the negated ELBO" for the whole table; the
magnitudes track posterior dimensionality. Prose arithmetic "34 = 2·7 + 2·6 + 6" (`:472`) is
real (32 ≠ 34) but needs semantic parsing ⇒ **non-goal**, `SEARCHED / NOT OBSERVED as
deterministically checkable`. Orphan float `tab:exp3_accuracy` (Table 9, never referenced) is a
measurement, not a finding.

## 10. Paper B — RTDL (arXiv 2106.11959) reverse trace

Full ledger: `work/rtdl-claim-trace.md`. Float numbering recomputed: `tab:datasets`=Table 1,
`tab:neural-networks`=**Table 2**, `tab:node`=Table 3, `tab:nn-gbdt`=Table 4,
`tab:ablation`=Table 5.

| # | claim | locator | evidence | owner | rule | verdict |
|---|---|---|---|---|---|---|
| D1 | "*The output **exactly matches** Table 2 from the paper:*" | `README.md:76` | Table 2 MLP row `data/table_neural_networks.tex:14`; README transcript 11 values, negatives exactly on the 4 `\textdownarrow` columns | PD | PD003 | **INCONCLUSIVE** — see §10.1; deliberately *not* a FAIL |
| D5 | "in this regime, **FT-Transformer outperforms NODE** and the gap between ResNet and NODE is **significantly reduced**" | `main.tex:364` | `table_node.tex:5-7`: NODE YE `$\mathbf{8.716}$` (bold, ↓) vs FT-T `8.751`; FT-T wins 10/11, ties AD `0.860`, loses YE | PD | PD004 / PD005 | clause 1 **FAIL** (bare comparative over the referenced set with an in-set counterexample); clause 2 **INCONCLUSIVE** (no declared gap measure, and "significantly" is defined operationally only in Table 2's caption `:339-341`) |
| D6 | "…the **necessity of feature biases**" | `main.tex:465` (same sentence `\autoref`s `tab:ablation`) | `table_ablation.tex:6`: w/o-biases is **bold-best** on JA `0.727` and YE `8.843` | PD | PD004 | **FAIL** on 2/8 columns, with JA recorded as a declared tie |
| D7 | "GBDTs start dominating on **some** datasets (California Housing, Adult, Yahoo; see Table 4)" | `main.tex:409` | Table 4: CatBoost `$\mathbf{0.741}$` best on MI (a 4th) | PD | PD002 | **PASS** — "some" is existential; a naive exhaustiveness reading would be a false FAIL (adversarial case S13) |
| D8 | "…large number of features **(700)**" | `main.tex:590` | `table_datasets.tex:6` YA `#num. features = 699` | PD | PD003 | **INCONCLUSIVE** — closeness is not a PASS and no precision semantics covers prose |
| D9 | "Due to the limited precision, some *different* values are represented with the same figures" | `main.tex:373`, inside Table 3's caption | per-float, author-declared precision semantics **with float scope** | PD | PD003 | OBSERVED object; the reason `precision_declaration` is a FloatAnchor field, not a global flag |
| D11 | abstract "outperforms other **solutions** on most tasks" (`:95`) vs conclusion "outperforms other **DL solutions** on most of the tasks" (`:499`) | `:95`, `:499` | Table 4 shows GBDTs beating FT-T | PD | PD007 | **FAIL** as a pair — identical predicate, different declared comparison class, no reconciliation |
| D2/D3 | "averaged over **all** random seeds" (`README.md:70`) / "averaged over **15** random seeds" (Table 2 caption) | `README.md:70,73`; `main.tex:338` | re-computed raw artifacts: `output/{adult,aloi,california_housing}/mlp/tuned/*` = **15 runs each**, means `0.852 / 0.954 / -0.499`; RD's RTDL bundle `RD002 PASS … n_members=15` | PD | PD002 | adult/aloi/CA **PASS on the declared universe of 15**; the other 8 datasets **UNKNOWN** ⇒ whole-table claim INCONCLUSIVE with census (universe PARTIAL 3/11) |

### 10.1 Why D1 is INCONCLUSIVE and not FAIL — the rule that pins PD's honesty

1. README declares its quantity key `metrics.test.score` (`README.md:73`).
2. The paper declares, in Table 2's caption `main.tex:375-376`, `\textdownarrow ~ RMSE` /
   `\textuparrow ~ accuracy`, and Table 1 carries an explicit `metric` row
   (`table_datasets.tex`: CA/YE/YA/MI = RMSE, the rest = Acc.).
3. The artifact carries **both** keys at the same path
   (`output/california_housing/mlp/tuned/0/stats.json`: `metrics.test.rmse = 0.49420855673906827`,
   `metrics.test.score = -0.49420855673906827`). Mean over 15 runs: score `-0.499`, and
   `|−0.499| = 0.499` = the printed `CA $0.499$`.
4. The rule that produces `score` lives in `lib.py`, which **is not in the vendored slice**
   (`bin/` holds only `mlp.py`, `tune.py`; `mlp.py:195` only writes a `{'score': -999999999.0}`
   sentinel). So the identity `score ≡ ±RMSE` is **UNKNOWN** — observed only as numerical
   equality, which the firewall forbids as a link.

**Frozen:** when two loci declare different quantity keys with no declared identity, PD003 emits
INCONCLUSIVE and records the measured relationship as a measurement only. This is also the proof
that PD must reuse RD's `Locus.quantity_key` discipline (`schema.py:81-94`: "two printed cells
are only comparable once they are declared to be the same quantity") rather than invent a
parallel notion. The actionable output for the author is "declare the identity or vendor
`lib.py`" — not "the paper is wrong".

## 11. Failure-mode catalogue and saturation (P0.4)

| FM | description | real anchor | deterministic? | RD covers? |
|---|---|---|---|---|
| FM-P01 | attributed value is in a different float than the reference resolves to | GMMVI C1 | yes (label→number + literal search) | no |
| FM-P02 | stated evidence-generation scope (n seeds / #splits / #datasets) ≠ declared member universe | GMMVI C5; RTDL D2/D3 | yes (RD measurements + manifest census) | no (RD005 ignores stated counts) |
| FM-P03 | exclusion/limitation enumeration narrower than the exclusion records | GMMVI C6 | yes (`Exclusion` records vs named set) | no |
| FM-P04 | bare comparative treated as universal over a referenced set | RTDL D5, D6; GMMVI C7 | yes, given the author's in-sentence `\autoref` | no |
| FM-P05 | absolutive adverb ("exactly", "clearly", "significantly") without declared semantics | RTDL D1; GMMVI C7; RTDL D5 clause 2 | partially — the adverb is observable, the tolerance must be declared | no |
| FM-P06 | numeric paraphrase drift between prose and a declared table cell | RTDL D8 (700 vs 699) | yes (equality/declared tolerance) | no |
| FM-P07 | abstract/conclusion or §A/§B drift on the same predicate with different scope | RTDL D11 | yes (claim-pair comparison) | no |
| FM-P08 | quantity identity across two loci undeclared ⇒ comparison impossible | RTDL §10.1 | yes (key comparison) | partially: RD *models* `quantity_key` but only between bundle cells |
| FM-P09 | printed value ≠ recomputation from its runs | GMMVI C10/C11/C12 | yes | **YES — RD001/RD005/RD008** ⇒ reassigned, deleted from PD |
| FM-P10 | best-marks inconsistent with the values in the same column | GMMVI C8 (585.12 bold twice) | yes | **YES — RD007** ⇒ reassigned, deleted from PD |
| FM-P11 | reference machinery abused: `\ref` inside macro definitions counted as claims | GMMVI `math_commands.tex` (32 false sites: 21 `\ref{#1}` + 11 `\ref{#2}`-style; re-counted from `work/gmmvi-float-ref.json` this pass) | yes (scope to after `\begin{document}`) | n/a — validation, not finding |
| FM-P12 | prose arithmetic decomposition ("34 = 7/6/6") | GMMVI `:472` | **no** — needs semantic parsing | no ⇒ non-goal |

**Saturation: reached at two papers.** Papers A and B are different communities (variational
GMM optimisation vs tabular deep learning), different evidence regimes (GMMVI: RD models 59
paper cells with runs behind them; RTDL: RD models 2 README cells and never reads the paper),
and between them they produced 11 distinct failure modes plus 2 that RD already owns and 1 that
is deterministically uncheckable. No new FM class appeared in Paper B that was not already
hypothesised before Paper B was read; Paper B's contribution was *confirming* FM-P04/P05/P06/P07
and supplying the refusal case (§10.1) that shapes the rules more than any new defect.

**TorchSSL decision — NOT admitted.** Written justification required by the brief: *GMMVI + RTDL
are insufficient because …* — this test **fails**. Both papers already exhibit every FM class
that a third paper was asked to look for (wrong reference, scope, qualification, comparative,
numeric drift, cross-section drift, quantity identity, validation hazards), and the two papers
also supply the two structurally different integration situations PD needs (a bundle that models
paper cells and rules on them, and a bundle that ignores the paper entirely). Adding TorchSSL
would only add instances of FM-P02/P05, i.e. sample collection for apparent rigour, which the
brief forbids. TorchSSL's real value is elsewhere: RD already runs a frozen TorchSSL oracle
(31 findings byte-stable), so it is a **Phase 1 regression asset, not a Phase 0 design source.**

## 12. RD / PD overlap tribunal (P0.5) — AUTHORITATIVE boundary

Test applied to every candidate FM and every candidate rule: *"Could Result Doctor already
answer this?"* → YES ⇒ **DELETE or REASSIGN**.

| candidate | tribunal outcome | why |
|---|---|---|
| "printed 26.87 vs recomputed 26.69" (PD003-style) | **REASSIGNED to RD** | `RD008 FAIL quantity:STM300/sepyfux/-elbo` + `RD001 INCONCLUSIVE` already exist in the frozen output |
| "±0.93 reproduced by no family" | **REASSIGNED to RD** | `RD005 FAIL` |
| "double bold on 585.12" | **REASSIGNED to RD** | `RD007` compares `observed_marks` vs `recomputed_marks` |
| "± semantics / std vs SE wording family" | **REASSIGNED to RD** | `RD005 rules.py:529-567` |
| "is the reported cell supported by its runs" | **REASSIGNED to RD** | RD001/RD002/RD006 |
| candidate `PaperDoctorReportedResult` | **DELETED** | duplicates `ReportedResult`; PD references RD targets by id |
| candidate `PaperDoctorComparisonSet` | **DELETED** | duplicates `ComparisonSet` |
| candidate `PaperDoctorArtifact` | **DELETED** | `ResultArtifact` already carries path/sha256/size and fits a `.tex` file verbatim |
| candidate "evidence dependency completeness" rule | **MERGED into PD001** | the dependency is exactly the link; a second rule would re-derive the same state |
| candidate "prose arithmetic" rule | **DELETED (non-goal)** | FM-P12 not deterministically checkable |
| wrong-float attribution (C1) | **KEPT** | no RD rule can express a sentence→float attribution |
| stated-scope vs member universe (C5, D2/D3) | **KEPT** | RD emits `n` but never compares it to a number stated in prose |
| exclusion enumeration (C6) | **KEPT** | RD judges exclusion *mechanics*, not whether prose named all of them |
| comparative/superlative support (D5/D6/C7) | **KEPT** | RD has no claim object |
| abstract↔conclusion drift (D11) | **KEPT** | prose↔prose is below RD's contract entirely |
| reference-integrity + validation hazards (FM-P11) | **KEPT** | RD's `E_UNRESOLVED_REF` is about manifest ids, not paper cross-references |

**Frozen canonical distinction.**
RD: *"Is reported result R supported by the evidence that produced it?"* (cell ↔ runs/aggregation/
selection/comparison). PD: *"Does paper claim C faithfully represent reported evidence R?"*
(claim ↔ float/cell/RD finding, and claim ↔ claim). PD reads R's verdicts; it never re-audits them.

## 13. Frozen claim universe and non-goals (P0.6) — AUTHORITATIVE

**In scope (6 forms).** A claim is in the universe only if its text, its locator, and its
support target can all be stated explicitly in `paper-doctor.yml`:

| form | mechanical signature | real anchor |
|---|---|---|
| `NUMERIC_ATTRIBUTION` | a numeric literal in a sentence that also contains a float reference or a named "Table N" | GMMVI C1 |
| `COMPARATIVE` | a comparison predicate from a closed vocabulary + two named systems | RTDL D5, D6 |
| `SUPERLATIVE` | best/top/leading/state-of-the-art + a declared or absent scope | GMMVI C8 |
| `SCOPE` | a count/unit/universe statement about how the evidence was produced | GMMVI C5, RTDL D2/D3 |
| `QUALIFICATION` | a statement naming which results had data removed/limited/omitted | GMMVI C6 |
| `REFERENCE_ATTRIBUTION` | "see Table X" / "provided in Table X" with no number | RTDL D7, D10 |

**Explicit non-goals (v0.1)** — each is a refusal, recorded so Phase 1 cannot drift into it:
theoretical theorem correctness; proof checking; novelty/priority claims; causal or world-truth
claims; any paper-quality judgment; rhetorical/persuasive claims with no support target
(GMMVI `:1453` "around one order of magnitude more efficient" is the archetype: the *object* of
the comparison is never stated, so there is nothing to link); verification of references in the
literature (citation truthfulness belongs to a different problem and to a different tool — §20);
cherry-picking detection; misconduct inference; prose arithmetic decomposition (FM-P12);
equation/section/appendix cross-reference auditing (no observed defect in either pilot; float
references only).

## 14. Frozen object model (P0.7) — AUTHORITATIVE

Reverse-derived: each retained field answers *"which real failure mode requires this field?"*,
otherwise it was deleted. **3 new objects, everything else reused.**

```
Claim
  claim_id                      id discipline (PD's analogue of RD's _collect_ids)
  paper_id                      -> ResultArtifact (reused; path+sha256+size of the .tex)
  text                          OBSERVED fragment, verbatim
  locator            SourceRef   reused verbatim: {path, line, key: 'text:"…"'}
  form               enum        the 6 forms of §13   (needed by: every FM)
  predicate          declared    comparison/superlative/adverb verb (needed by: FM-P04/05/06)
  subjects           [str]       the systems being compared (needed by: FM-P04)
  quantifier         enum        all | most | some | bare | numeric (needed by: FM-P07, S13)
  qualifiers         [Qualifier] data-removal / precision / subset statements (FM-P03, FM-P05)
  scope              ScopeDecl   declared universe + unit (FM-P02)
  link_refs          [EvidenceLink]  (PD001)
  not_audited_reason  optional   why a claim is out of universe (prevents silent universe shrinkage)

FloatAnchor
  float_id / kind / number       FM-P01 requires label→number resolution
  source_file / begin_line       provenance of the numbering
  labels             [str]       `\label{}` inside the float
  caption_locator     SourceRef  FM-P02/P05: captions carry the author's declarations
  quantity_declaration           "↓ ~ RMSE", "Acc.", "the negated ELBO" (RTDL D9/GMMVI C10)
  precision_declaration          FM-P06: per-float tolerance (RTDL D9 proves scope matters)
  mark_rule_declaration          "top = not statistically significant" (RTDL D4)
  referenced_by        [int]     orphan detection — measurement only

EvidenceLink
  link_id / claim_ref
  target_kind          enum: FLOAT | RD_TARGET | PROSE
  target_ref           float_id, or (rule_id,target) pair, or SourceRef
  link_basis           AUTHOR_REF_IN_SENTENCE | AUTHOR_NAMED_FLOAT | AUDITOR_DECLARED
                       (FM-P01 needs the first two; the firewall forbids anything else)
  quantity_identity    optional explicit identity statement (RTDL §10.1: without it → INCONCLUSIVE)
  grade                reused Grade; basis-derived, never INFERRED
```

Reused without change: `SourceRef`, `EvidenceField`, `Grade`, `RuleFinding`, `canonical_json`,
`RuleStatus`, `UniverseStatus`, `ResultArtifact`, `Locus.quantity_key` semantics, the 4 locator
families, and RD's manifest section-order discipline
(`_registry → _collect_ids → _artifacts → … → _comparisons` becomes
`_registry → _collect_ids → _artifacts → _floats → _claims → _links`).

## 15. Frozen evidence model (P0.8) — AUTHORITATIVE

Fact doors, inherited verbatim from RD and never loosened:

| door | grade | may support |
|---|---|---|
| `observed: {locator}` | DIRECT | PASS, FAIL, INCONCLUSIVE |
| `declared: {value|statement}` | DECLARED | unlocks a judgment; **never proves consistency** |
| `unknown:` / field absent | UNKNOWN | INCONCLUSIVE only |
| derived from an explicit structure (float numbering, `\ref` resolution, key equality) | DERIVED | PASS/FAIL, with the derivation recorded |
| anything else | INFERRED | **at most `SUGGESTED`; never a verdict** |

The following are **measurements, never evidence for a PASS**: semantic similarity, LLM matching,
numerical closeness, filename similarity, table adjacency, column-arrow alignment, sign
coincidence. (RTDL §10.1 is the concrete case where all of them point the same way and PD still
must not PASS.)

LaTeX/source first. PDF is a read-only fallback with a recorded locator confidence, and when a
cell's identity is unrecoverable the verdict is INCONCLUSIVE — **never an LLM guess about cell
topology.**

## 16. Frozen rule set (P0.9) — AUTHORITATIVE. **7 rules, not 8.**

`PD008 Evidence Dependency Completeness` was **merged into PD001** (§12) and the candidate
"prose arithmetic" rule was deleted; keeping 8 for the sake of numbering was explicitly
forbidden. Common narrowing clause for every rule: `PASS` means "on this narrow relation the
claim agrees with the evidence" — nothing more.

**PD001 — Claim Traceability**
Question: does this claim have at least one explicitly based support link?
Target: every `Claim`. Required: `EvidenceLink.link_basis` ∈ {AUTHOR_REF_IN_SENTENCE,
AUTHOR_NAMED_FLOAT, AUDITOR_DECLARED} + a resolvable target.
PASS: link exists and resolves. FAIL: **never** (untraceable is not false). INCONCLUSIVE: no link,
or link only `SUGGESTED`. NOT_APPLICABLE: claim is in the out-of-universe class recorded in
`not_audited_reason`. NOT_RUN: no `claims` section.
Evidence: claim locator, link, target. Measurements: `n_links`, `link_basis`, `target_resolved`.
Motivation: RTDL D5/D6 (in-sentence `\autoref` = strongest link). Positive: D5. Negative/unknown:
GMMVI `:1453`. Non-duplication: RD has no claim concept.

**PD002 — Evidence Scope Consistency**
Question: does the scope the claim states match the scope of the evidence as declared/recovered
downstream? Target: `SCOPE` claims + `Claim.scope`. Required: claim text OBSERVED; RD measurement
`n_members` and/or declared `member_ids` size; RD002 status for that aggregation;
`UniverseStatus`.
PASS: stated count equals the declared universe and RD002 is PASS. FAIL: stated count differs from
a declared universe that RD002 certified. INCONCLUSIVE: RD002 INCONCLUSIVE (e.g. all 46 GMMVI
aggregations), or universe PARTIAL/UNKNOWN. NOT_APPLICABLE: claim states no count. NOT_RUN: no
`aggregations` in the upstream file.
Motivation: GMMVI C5 (n=4/5/7/8 against a caption claiming ten seeds). Positive: RTDL adult/CA
(15 = 15, `RD002 PASS`). Negative: GMMVI C5. Non-duplication: RD005 looks only at family.

**PD003 — Quantitative Claim Consistency**
Question: does the number the claim states equal the number printed at the locus the claim
resolves to, under the declared quantity identity and declared precision?
Target: `NUMERIC_ATTRIBUTION` claims. Required: float resolution (PD006) + identical declared
quantity key + declared precision semantics (cell digits, caption tolerance, or claim-stated
rounding).
PASS: string-equal printed cells under identical declared quantity, or equal at a declared
tolerance. FAIL: both sides declare the same quantity and equality fails at declared precision.
INCONCLUSIVE: quantity identity undeclared (RTDL §10.1), or tolerance undeclared and values
differ (RTDL D8 700/699), or the locus is unrecoverable. NOT_APPLICABLE: the claim states no
number. NOT_RUN: no floats parsed.
Measurements: `claim_value`, `cell_value`, `delta`, `identity_basis`.
Non-duplication: RD001 compares cell↔runs; PD003 compares prose↔cell. Different edges.

**PD004 — Comparative Claim Support**
Question: over the comparison set the claim resolves to, does the stated relation hold for every
member, under a declared aggregation basis?
Target: `COMPARATIVE`/`SUPERLATIVE` claims. Required: link to a `FloatAnchor` (or an RD
`ComparisonSet`), the two subject names as they appear in that float, and either a declared basis
(per-column / mean rank / named column) or the claim's own quantifier.
PASS: declared basis + support for all members. FAIL: quantifier is universal or bare and ≥1
counterexample exists inside the referenced set (RTDL D5 clause 1, D6). INCONCLUSIVE: basis
undeclared, or "clearly"/"consistently"/"significantly" has no declared test (GMMVI C7, RTDL D10,
D12), or downstream RD007 is FAIL/INCONCLUSIVE. NOT_APPLICABLE: no comparison target exists.
Non-duplication: RD007 checks the marks; PD004 checks the sentence.

**PD005 — Qualification Preservation**
Question: does the claim carry every qualification that the evidence carries?
Target: claims with `qualifiers`, incl. absolutive adverbs ("exactly", "all", "always").
Required — the exclusion universe is **not** a top-level upstream collection (the frozen RD
`Bundle` has exactly 8 sections and none of them is `exclusions`; exclusions are per-`Aggregation`
objects, `schema.py:139`). PD derives the universe mechanically from `rd_findings.json` as
`{target : rule_id == "RD002" and measurements["n_exclusions"] > 0}`, and a listing counts as
evidence only when `n_exclusions_listed == n_exclusions` with `member_rule_grade` ∈
{DIRECT, DERIVED}. In the frozen GMMVI output this predicate yields exactly **7 targets / 34
exclusion objects, all fully listed**: `PlanarRobot/{sepyfux,sepyrux,zamtrux}/-elbo` and
`TALOS/{sepyfux,sepyrux}/{-elbo,entropy}` (re-read this pass into
`work/rd002-exclusion-targets.txt`).
**Frozen interaction with RD002 status:** all 7 findings are `INCONCLUSIVE`, and that does *not*
disable PD005 — the inconclusiveness concerns binding members to external run ids and criterion
recomputability, neither of which is the relation PD005 tests (the claim's enumeration ↔ the
author's own listed exclusion set). PD005 must still copy RD's limitation into its reason string so
the author sees what remains undecided. Firewall line 7 forbids presenting an INCONCLUSIVE as
certainty in either direction; it does not forbid judging a different, evidence-backed relation.
PASS: every exclusion/limitation in the referenced evidence is named or covered by a declared
generic statement. FAIL: the evidence contains a qualified case the claim's wording excludes —
GMMVI C6: prose names Sepyfux only, evidence also excludes members for `sepyrux` and `zamtrux`;
RTDL D1: "exactly" while a recovered cell differs in sign with no declared identity.
INCONCLUSIVE: the adverb has no declared semantics and the divergence is unresolvable
(never silently promoted to PASS). NOT_APPLICABLE: no qualifiers on either side, or the upstream
file has RD002 findings but every one has `n_exclusions == 0`. NOT_RUN: the upstream file contains
**no** RD002 finding at all (absence of the judgment is not absence of exclusions).
Non-duplication: `Exclusion` objects exist in RD but no RD rule reads prose.

**PD006 — Result Reference Integrity**
Question: does the reference in the claim resolve to the float that actually carries the
attributed content?
Target: `REFERENCE_ATTRIBUTION` claims and any claim containing `\ref`/`\autoref`/a named "Table N".
Required: float numbering from source order (DERIVED), label index, and a deterministic content
check (the literal, or the named row/column, exists inside the referenced float).
PASS: resolves and the content is present in that float. FAIL: resolves to a float that does not
contain it while another float does (GMMVI C1, deterministic). INCONCLUSIVE: the label does not
resolve, or the content is ambiguous across floats. NOT_APPLICABLE: no reference in the claim.
Guard: sites inside macro definitions (`\newcommand` bodies) are **not claims** — FM-P11, the 32
`math_commands.tex` false positives (21 `\ref{#1}` + 11 other `#N`); this belongs to the
validation channel, not to PD006.
Non-duplication: RD has no float resolver.

**PD007 — Cross-Section Claim Consistency**
Question: do two claims with the same predicate and subjects state the same proposition?
Target: claim pairs linked by an explicit `same_as` declaration in the manifest (never by
similarity). Required: identical predicate + subjects declared equal; scopes compared
string-wise.
PASS: identical or reconciled scopes. FAIL: different declared scope with no reconciliation
(RTDL D11 `:95` "other solutions" vs `:499` "other DL solutions"). INCONCLUSIVE: pairing is
`SUGGESTED` only. NOT_APPLICABLE: singleton claim.
Non-duplication: prose↔prose is under RD's contract, not in it.

## 17. State semantics, partial audits, validation errors (P0.9) — AUTHORITATIVE

Three channels, non-interchangeable, inherited from RD:

1. **UNKNOWN** — a field the evidence does not supply. Surfaced inside INCONCLUSIVE; never a
   finding about the paper.
2. **INCONCLUSIVE** — the rule ran and the evidence on file cannot decide. *Records missing
   evidence, not a problem found.* This is the correct home for "the artifact that would settle
   it (`lib.py`) is not vendored".
3. **VALIDATION ERROR** — the audit contract itself is malformed: bad locator, duplicate ids,
   unknown key, unresolved manifest reference, unverifiable upstream hash. Text form frozen as
   RD's: `"{code} at {where}: {problem}"`, exit code 2, **and it is never reported as a
   scientific result.**

Frozen PD validation codes (12 — each justified by a hazard observed in this session):
`P_SCHEMA_VERSION` `P_TOP_LEVEL` `P_UNKNOWN_KEY` `P_TYPE` `P_NOT_A_NUMBER` `P_MISSING_FIELD`
`P_DUPLICATE_ID` `P_UNRESOLVED_REF` (claim → unknown float/rd target) `P_CONFLICTING_REF`
(two links for one claim resolving to different floats — GMMVI C1 vs C2) `P_LOCATOR_KEYS`
(illegal locator key set — RD's `E_LOCATOR_KEYS` lesson) `P_PATH_OUTSIDE_ROOT` (the `..`-escape
class RD guards) `P_YAML`. `P_UNRESOLVED_REF` also covers the FM-P11 case when a `text:` locator
lands inside a macro definition.

**Partial-audit semantics (frozen).** Missing sections → `NOT_RUN` for the rules whose driving
class is empty, computed exactly as RD's `DRIVING_CLASS`/`not_run_findings` do: PD001/PD002
drive on `claims`, PD003/PD004/PD006/PD007 on `claims`+`links`, PD005 on `claims` + the derived
exclusion universe (`RD002` findings whose `measurements.n_exclusions > 0`; see §16 PD005).
**No PD rule drives on an upstream `exclusions` collection — there is none** (frozen RD `Bundle`
has 8 sections; exclusions are attached to `Aggregation`, `schema.py:139`). A partial audit is
legitimate and *is not* downgraded to INCONCLUSIVE — a `NOT_RUN`
line states which class was absent. Listed members are never the complete universe: PD prints
the universe status per claim set, and `not_audited_reason` prevents an unlisted claim from
being read as "no claim".

## 18. Synthetic adversarial matrix (P0.10) — AUTHORITATIVE for Phase 1 tests

Every case must discriminate at least two rules or two states. Cases S1–S7 are mandatory;
S8–S13 are the judged additions.

| id | construction | required discriminating outcome |
|---|---|---|
| S1 | claim exactly supported, in-sentence `\autoref`, cells string-equal, RD002 PASS, n matches | PD001 PASS, PD002 PASS, PD003 PASS, PD004 PASS, PD006 PASS |
| S2 | prose number differs from the printed cell, same declared quantity, declared precision identical | PD003 **FAIL**, PD001 PASS (proves traceability ≠ truth) |
| S3 | scope inflation: evidence covers 7 of 9 datasets, claim says "all" | PD002 **FAIL** *and* PD005 **FAIL** (never only one) |
| S4 | claim with no resolvable link | PD001 **INCONCLUSIVE**, and every other rule for that claim must be INCONCLUSIVE or NOT_APPLICABLE — **never FAIL** (missing mapping is not a mismatch) |
| S5 | prose number exists, but in the float the reference does **not** point to | PD006 **FAIL**, PD003 INCONCLUSIVE (GMMVI C1 shape, reproduced synthetically so the rule is testable without a real paper) |
| S6 | evidence carries an exclusion the claim's wording omits | PD005 **FAIL**, PD002 PASS-or-INCONCLUSIVE (proves qualification ≠ scope) |
| S7 | purely rhetorical claim ("an order of magnitude more efficient", no object) | PD001 **NOT_APPLICABLE** with `not_audited_reason`; no rule may emit FAIL |
| S8 | downstream RD001 FAIL for the cell the claim quotes | PD003 **INCONCLUSIVE** + propagated reason; PD may not PASS and may not double-report a FAIL (discriminates the boundary rule of §7.5) |
| S9 | two identical printed values, both bold, different rows | RD007 owns it ⇒ PD004 **INCONCLUSIVE** "no downstream-free judgment possible"; proves PD does not eat RD's work |
| S10 | claim states "+2.1%" where evidence shows a 2.1 **percentage-point** difference under a declared accuracy quantity | PD003 **FAIL** (unit), PD002 PASS — discriminates value-vs-scope |
| S11 | two `same_as`-declared claims, scopes "solutions" vs "DL solutions" | PD007 **FAIL**, PD004 PASS (the drift is not a support failure) |
| S12 | author declares "ten seeds" and RD002 PASS confirms 10 members, but 3 are excluded ⇒ effective n=7 | PD002 **FAIL** and PD005 **FAIL**; the reason must name both (GMMVI C5/C6 shape) |
| S13 | existential enumeration: "some datasets (A, B, C)" where D also qualifies | PD002 **PASS** and PD005 **PASS** — the false-positive guard, modelled on RTDL D7 |

S13 is required because a tool that only ever finds problems is not an auditor. Cases S1, S7,
S9, S13 are the anti-false-positive half; S2–S6, S8, S10–S12 are the discriminating half.

## 19. Phase 1 firewall spec (P0.11) — AUTHORITATIVE, blocking

Phase 1 is not accepted unless each line below is implemented as a *test that fails* when the
forbidden behaviour is introduced.

1. LLM semantic guess ⇒ **cannot** produce PASS. Heuristic matchers may emit `SUGGESTED` only.
2. Numerical closeness ⇒ **cannot** create a link or a PASS (RTDL §10.1 is the named case).
3. Filename/path similarity ⇒ **cannot** create a link.
4. Table/float adjacency or column-arrow alignment ⇒ **cannot** create a link.
5. DECLARED-only support ⇒ **cannot** auto-PASS any rule; declaration unlocks judgment, it does
   not prove consistency.
6. A downstream RD `FAIL` ⇒ **cannot** be ignored, downgraded, or overwritten by a PD PASS.
7. A downstream RD `INCONCLUSIVE` ⇒ **cannot** be presented as certainty in either direction.
8. Missing evidence ⇒ **cannot** become FAIL. It is INCONCLUSIVE/UNKNOWN.
9. A validation error ⇒ **cannot** be reported as a scientific finding.
10. No paper score, no composite index, no ranking of papers.
11. No accept/reject or "would this survive review" prediction.
12. No novelty judgment; no literature-truth verification.
13. No misconduct, cherry-picking, or integrity accusation anywhere in output text or enum names.
14. No theorem/proof verification; no automatic full-PDF semantic understanding; no LLM
    inference about cell topology — PDF is read-only fallback with recorded locator confidence,
    and unrecoverable identity ⇒ INCONCLUSIVE.

## 20. Prior art and differentiation — SUPPORTING (all IDs re-verified against the arXiv API this session)

Verified-existing, arXiv: **2604.08501** `sciwrite-lint: Verification Infrastructure for the Age
of Science Vibe-Writing` (2026) — its abstract states a citation-verification pipeline
(reference existence, metadata accuracy, retraction status, claim support, per-reference
**reliability scores**, one hop into cited bibliographies) that "also extends to internal
consistency: numbers in text vs. tables, abstract vs. body, figure captions vs. content,
statistical results vs. their verbal interpretation, plus structural cross-references", and
proposes a composite "SciLint Score". Tier 1.
**This is the closest prior art and the sharpest risk to the GO decision.** Overlap is real on
the *check list*; the difference is structural: sciwrite-lint is an authoring-time linter whose
claim validation and consistency reasoning run on **local open-weights models**, and whose output
is a **reliability score**. PD is a downstream auditor whose links must be explicitly declared,
whose verdicts are per-relation and never aggregated, which consumes an upstream provenance
verdict chain instead of re-deriving one, and which is contractually forbidden from emitting any
score or integrity signal. §19 lines 1–5 and 10–13 exist precisely because that is the design
axis where a neighbouring tool took the other branch.

Also verified: **2502.10003** SciClaimHunt (numeric claim subset, Tier 1); **2408.14317**
"Claim Verification in the Age of Large Language Models: A Survey" (Tier 1); **2506.21745**
"(Fact) Check Your Bias" (LLM-judge bias, Tier 1); **2504.01848** PaperBench (replication ≈20 %
of metric credit — evidence that recomputation is too costly/noisy to be the audit mechanism,
Tier 1); **1803.05355** FEVER *(the subagent reported `1803.05357`; corrected here after API
lookup)*; **2210.13777** SciFact-Open. Non-arXiv, venue-cited: Wadden et al., *Fact or Fiction:
Verifying Scientific Claims*, EMNLP 2020 (arXiv id **NOT OBSERVED** — title search did not
return it, so it is cited without one); Magnusson, Smith & Dodge, *Reproducibility in NLP: What
Have We Learned from the Checklist?*, Findings of ACL 2023, whose finding that acceptance rate
rises with more "Yes" answers is the strongest argument for unaudited self-reports needing a
downstream auditor; ACM Artifact Review & Badging policy; Baker, *1,500 scientists lift the lid
on reproducibility*, Nature 2016. **NOT OBSERVED within budget:** the ALLELUIA claim–result
alignment dataset and the Stimmling et al. numeric-claims line — do not cite them until a primary
source is retrieved.

## 21. GO / NO-GO tribunal (P0.12) — nine criteria, no default to GO

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | Is there territory no released layer covers? | **YES** | §5, §9 C1/C5/C6, §10 D5/D6/D8/D11; §12 reassigned 5 of 12 candidates to RD and still had ≥6 left |
| 2 | Is the evidence for that territory obtainable deterministically? | **YES** | `float_ref_map2.py` resolved 23 tables / 9 tables with nesting depth 1; C1 adjudicated by one grep + one numbering pass |
| 3 | Does it require modifying frozen upstream? | **NO** | Contract I-1 needs only `audit --json`, a shipped, test-pinned surface |
| 4 | Is the integration contract stable and provenance-preserving? | **YES with one documented hazard** | the `NaN` finding (§6) forces a parsing policy, which I-1.7 supplies |
| 5 | Can the rules be discriminated by synthetic cases? | **YES** | §18, 13 cases each separating ≥2 rules/states |
| 6 | Have the failure modes saturated? | **YES at 2 papers** | §11; a third paper would add instances, not classes — and the brief forbids collecting papers for apparent rigour |
| 7 | Is the design achievable without LLM-as-judge? | **YES** | every verdict in §9/§10 came from equality, enumeration, count, or resolution |
| 8 | Can a fresh agent implement Phase 1 without re-researching? | **YES** | §22 names files, fields, rules, tests, and prohibitions |
| 9 | Does prior art make this redundant? | **NO, but it changes the framing** | sciwrite-lint (§20) covers an overlapping checklist with LLM+scores; PD's deterministic/declared/no-score position is still open, and its binding to a provenance chain is absent from all retrieved work |

**Decision: GO, with two named risks carried into Phase 1.**
R1 — *overlap risk*: a reviewer may say sciwrite-lint already does "numbers vs tables".
Mitigation frozen: PD's differentiator is the declared-link firewall plus the upstream verdict
binding; Phase 1 must ship S5/S8/S9 as tests to prove the difference mechanically, not rhetorically.
R2 — *universe risk*: PD is only as good as the audited universe. RTDL's 3-of-11 dataset vendoring
turns most of Table 2 into UNKNOWN. Mitigation frozen: every finding must carry a universe status
and a census; a claim over an unlisted universe cannot be PASSed, and the tool must say so plainly.

## 22. PHASE 1 IMPLEMENTATION CONTRACT — AUTHORITATIVE

Target: a minimal, deterministic core. Nothing in Phase 1 may add capability beyond this list.

**Files / modules** (new project `paper-doctor`, version 0.1.0)
```
src/paper_doctor/evidence.py      # re-exports/derives from RD's shape: Grade, SourceRef, EvidenceField
src/paper_doctor/status.py        # RuleStatus, UniverseStatus, RuleFinding, canonical_json
src/paper_doctor/objects.py       # Claim, Qualifier, ScopeDecl, FloatAnchor, EvidenceLink  (§14 ONLY)
src/paper_doctor/latex_index.py   # float numbering, label index, ref sites, `\input` flattening
src/paper_doctor/rd_findings.py   # Contract I-1 reader: path+sha256 verify, (rule_id,target) index, NaN policy
src/paper_doctor/manifest.py      # paper-doctor.yml loader, section order, 12 P_ codes, ManifestError text
src/paper_doctor/rules.py          # PD001-PD007, QUESTION/NAME dicts, one evaluate() per rule
src/paper_doctor/audit.py          # DRIVING_CLASS, not_run_findings, audit_bundle, audit_manifest
src/paper_doctor/cli.py            # `paper-doctor audit [--json]`, exit 0/2/1, columns rule/status/target/reason
```
**Manifest fields** — sections in order `_registry → _claims → _floats → _links`, with
`registry.paper` / `registry.rd_findings` carrying path+sha256+size+RD version. A claim must
state `form`; a link must state `link_basis`; a float may state `quantity_declaration`,
`precision_declaration`, `mark_rule_declaration`.

**Rules** — exactly PD001–PD007 as narrowed in §16. No eighth rule.

**Tests** — `test_rules_unit.py` (per-rule PASS/FAIL/INCONCLUSIVE/NOT_APPLICABLE/NOT_RUN),
`test_adversarial_matrix.py` (S1–S13, one test per cell of §18, asserting *pairs* of statuses),
`test_pd_firewall.py` (the 14 lines of §19 as failing tests),
`test_latex_index_oracle.py` (GMMVI: 9 tables/3 figures, `tab:exp1`→2, `tab:exp1_eval`→3;
RTDL: 23 tables/2 figures, `tab:neural-networks`→2; `math_commands.tex` sites excluded),
`test_rd_findings_contract.py` (hash mismatch ⇒ exit 2; `NaN` ⇒ UNKNOWN, never 0.0; and the
derived exclusion universe over the frozen GMMVI output is **exactly 7 targets / 34 exclusions**
with `n_exclusions_listed == n_exclusions` on all 7 — this is the §16 PD005 predicate, and it must
be asserted against the real upstream file, not a fixture),
`test_acceptance_gmmvi.py` (C1 FAIL, C5 FAIL, C6 FAIL — C6's reason string must name `sepyrux`
**and** `zamtrux` — C10/C11/C12 **not** re-reported),
`test_acceptance_rtdl.py` (D1 INCONCLUSIVE, D5 clause-1 FAIL, D6 FAIL, D7 PASS, D8 INCONCLUSIVE,
D11 FAIL, D2/D3 PASS-on-subset + INCONCLUSIVE-on-table), `test_cli.py` (CLI↔API non-drift),
`test_canonical_bytes.py` (two runs byte-identical; `b"\r" not in bytes`; explicit `newline="\n"`).

**Acceptance cases** = the 7 real anchors of §9/§10 plus S1/S7/S13.
**Explicit prohibitions for Phase 1** = §19 in full, plus: no new object beyond the 3 in §14; no
modification of dataset-doctor / experiment-doctor / result-doctor; no network access at runtime;
no dependency on `result_doctor` at runtime; no publishing, tagging, or PyPI work without explicit
user authorization.

## 23. Self-audit, limitations, open registers

**Final re-verification pass (same session, after the report was written).** Every load-bearing
number was re-derived from the artifacts rather than from notes:
* C1 re-checked against `arxiv.tex`: `78.69` occurs exactly once, `:408`, inside the `table`
  environment beginning `:400` whose `\label{tab:exp1}` is at `:416`; `tab:exp1_eval` is Table 3
  (env begins `:430`). The claim at `:426` attributes the value to Table 3 ⇒ FAIL stands.
* Oracle counts re-read from `work/gmmvi-float-ref.json` / `work/rtdl-float-ref.json`: GMMVI 9
  tables / 3 figures, nesting depth 1, 114 ref sites, 95 unresolved, 1 never-referenced label;
  RTDL 23 tables / 2 figures, nesting depth 1, 37 ref sites, 13 unresolved, 11 never-referenced
  labels. `tab:neural-networks`→2, `tab:datasets`→1, `tab:node`→3, `tab:nn-gbdt`→4,
  `tab:ablation`→5 — the §22 oracle-test expectations match the artifacts.
* RD baseline re-run read-only against the frozen GMMVI archive
  (`F:\MLResearch\experiment-doctor\phase0-gmmvi`, via `result_doctor.audit.evaluate`, captured in
  `work/rd-baseline-recheck.txt`): **538 findings** = PASS 165 / INCONCLUSIVE 293 /
  NOT_APPLICABLE 69 / **FAIL 11**; per rule RD001 59, RD002 46, RD003 157, RD004 100, RD005 59,
  RD006 59, RD007 5, RD008 53; the 11 FAILs are RD003 ×4 + RD005 ×2 + RD008 ×5 (1 quantity +
  4 artifact-identity); **RD002 is INCONCLUSIVE on all 46**. Every number in §9 matches.
  Bundle census also re-derived: 59 reported results, 46 aggregations, 500 members, 128 artifacts,
  3 transformations, 100 candidate sets, 98 selection events, 5 comparison sets, 34 exclusions.
* **One design hole found and closed by this pass.** PD005 was specified to drive on "upstream
  exclusions", but the frozen RD `Bundle` has **no `exclusions` collection** — exclusions are
  per-`Aggregation` objects (`schema.py:139`) that reach `rd_findings.json` only as RD002
  *measurements*. §7.4, §16 PD005 and §17 now state the exact extraction predicate
  (`rule_id == "RD002" and measurements.n_exclusions > 0`, listing valid only when
  `n_exclusions_listed == n_exclusions`), which in the frozen output yields exactly 7 targets /
  34 exclusions covering `sepyfux`, `sepyrux` **and** `zamtrux` — i.e. C6's FAIL is computable
  through Contract I-1 alone, with no second read of the archive. Without this patch Phase 1 would
  have had to invent the mechanism, which is precisely what a "directly implementable" contract
  must not leave open.
* RTDL raw-artifact means re-computed from `output/*/mlp/tuned/*/stats.json`: 15 runs each for
  adult / aloi / california_housing; `metrics.test.score` means **0.852 / 0.954 / −0.499**, and
  CA also carries `metrics.test.rmse` mean **0.4985** — the two-key fact §10.1 point 3 rests on is
  real, and this session's re-run of RD over the RTDL pilot (`work/rtdl-audit-from-pylib.json`,
  16 findings = `evaluate()` 15 + the appended `RD007 NOT_RUN`) shows
  `RD002 PASS` on exactly 2 aggregations with `n_members = 15` and `n_exclusions = 0`. RTDL's
  bundle has **no** unbound-exclusion case, so D1's refusal is a quantity-identity refusal, not a
  membership refusal — the two pilots exercise different refusers.
* **One correction issued by this pass:** FM-P11 / PD006 stated "23 `math_commands.tex` false
  sites"; the artifact shows **32** (21 `\ref{#1}` + 11 other `#N`). Both places corrected here and
  in `work/gmmvi-claim-trace.md`. The class of failure is unchanged; only the census was wrong.
  Recorded rather than silently fixed, because a PD design report that mis-counts its own evidence
  is exactly the defect PD exists to catch.

**19-item checklist** (✓ satisfied, ✗ not, with reason):
1 ✓ core question stated and nothing else (§2) · 2 ✓ RD contract frozen from source, not memory (§4)
· 3 ✓ four integration options scored and one frozen (§6, §7) · 4 ✓ both papers reverse-traced to
primary artifacts (§9, §10) · 5 ✓ every number re-verified; handoff numbers treated as UNVERIFIED
and one earlier figure explicitly superseded (§10 B-3) · 6 ✓ saturation declared with a written
reason for excluding TorchSSL (§11) · 7 ✓ tribunal applied to every FM and rule, 5 candidates
reassigned, 4 deleted, 1 merged (§12) · 8 ✓ minimal claim universe with named non-goals (§13)
· 9 ✓ object model reverse-derived, 3 new objects, duplication candidates deleted (§14)
· 10 ✓ evidence doors kept at OBSERVED/DECLARED/DERIVED-else-UNKNOWN, INFERRED ≤ SUGGESTED (§15)
· 11 ✓ 7 rules, each with motivation + positive + negative/unknown case + ownership + non-duplication
proof (§16) · 12 ✓ rule semantics narrowed; PASS defined per-relation (§16) · 13 ✓ UNKNOWN vs
INCONCLUSIVE vs VALIDATION ERROR separated (§17) · 14 ✓ adversarial matrix with 4 anti-false-positive
cases (§18) · 15 ✓ firewall spec, 14 blocking lines, no LLM-as-judge (§19) · 16 ✓ LaTeX-first, PDF
fallback with recorded confidence, no cell-topology guessing (§15) · 17 ✓ GO tribunal run on 9
criteria with 2 risks recorded, not defaulted (§21) · 18 ✓ Phase 1 contract implementable without
re-research (§22) · 19 ✓ single authoritative report at the mandated path (§0 header).

**Limitations (honest).**
* Only 3 of 11 RTDL datasets and 1 of 9 models are vendored, so most of RTDL's Table 2 is UNKNOWN
  rather than audited; PD must publish censuses, not coverage it does not have.
* RD002 is INCONCLUSIVE on all 46 GMMVI aggregations (members unbindable), so PD002 can only
  reach FAIL via the declared caption scope in Paper A, never via run-level verification.
* PD003's PASS requires an author-declared quantity identity that neither pilot paper supplies
  outside a table caption; the first PASS-capable instance found was RTDL's MLP/adult cell via
  RD002 PASS + 15-member universe.
* `sciwrite-lint` overlap is a rhetorical risk that only Phase 1's mechanical tests (S5/S8/S9)
  answer.
* No third-paper confirmation of FM saturation; the claim is "no new class appeared", not "no new
  class exists".

**Open registers for Phase 1.** O-1 define the `Qualifier`/`ScopeDecl` enum vocabulary from the
7 anchors (keep it ≤6 values each). O-2 decide whether `FloatAnchor` parsing lives in PD or is
shared (answer must be PD — RD is frozen). O-3 measure the authoring cost of a PD manifest per
claim, using RTDL's 12 claims as the sample, before Phase 2 generalises the workflow. O-4 decide
whether an eighth validation code `P_UNIVERSE_MISMATCH` is needed once RD002 PASS instances
accumulate (do not add it now).

**Single next step:** implement Phase 1 exactly as specified in §22, starting with
`latex_index.py` + `test_latex_index_oracle.py`, because C1 — the deterministic wrong-table
attribution — is the one finding whose entire feasibility argument rests on float numbering being
provably correct, and it is the cheapest thing to falsify.

---
*Phase 0 is frozen. Production development stops here until Phase 1 is started deliberately.*

---

# ERRATUM — 2026-09-29 (Phase 0 design authority, issued after the Phase 1 report)

**Status: ERRATUM A1–A5 ACCEPTED / APPLIED.** Scope: five statements in the frozen body above are
superseded — A1–A4 issued after the Phase 1 report, **A5 issued with the Phase 2 brief**.
**Nothing in §§1–25 is rewritten or erased** — every line cited here keeps its original
text as the historical record of the research round, and this section is the correction that
supersedes it. Where a superseded statement is a *census*, the census survives below with its
evidence surface labelled, because Phase 1's `PD002` counts must continue to state their unit
(§12) and a reader must be able to tell which surface produced which number.

No erratum adds a rule, a `P_*` code, an object, a schema field, or a Result Doctor change. For all
five, **the delivered Phase 1 implementation already matched the new statement**, so the code change
count is zero; what changes is the authority of the prose expectation.

## A1 — C5's expected status, and the `9 of 46` census

| | |
|---|---|
| **Old statement** | line 225 (§9, C5 row): "**FAIL** (declared caption scope covers all 56 cells via `spread_label`; 9 of 46 aggregations do not compute over ten seeds)"; reinforced at line 249 ("C5's FAIL is a scope contradiction") and mandated as an oracle at line 728 (§22, "`test_acceptance_gmmvi.py` (C1 FAIL, **C5 FAIL**, C6 FAIL …)"). |
| **New statement** | **PD002 on C5 = `INCONCLUSIVE`.** The divergence is reported as measurements with their unit, never as a determinate FAIL. |
| **Reason** | Contract I-1 admits exactly one evidence surface: the frozen `result-doctor audit --json` snapshot. On that surface all 46 `RD002` aggregation findings are `INCONCLUSIVE`, and PD's frozen certainty-monotonicity clause forbids upgrading upstream uncertainty into a determinate verdict. A FAIL would have been an upgrade. |
| **Semantic impact** | **Material, and it tightens the design.** It fixes, in prose, the rule that a `PD002` count whose upstream basis is `INCONCLUSIVE` is capped at `INCONCLUSIVE` by the `_downstream` gate — i.e. `PD002` can FAIL only when the divergence is visible on admissible evidence *and* the upstream basis is certifying. Enforced by the existing certainty-monotonicity firewall row, not by new code. |
| **Implementation changed** | **No.** Delivered as `INCONCLUSIVE` from the first run; Phase 1 had reported this as a contradiction (its register item A1). |

**Re-labelled measurement, kept for the record.** The `9 / 46` figure is a **RESEARCH-ROUND
OBSERVATION**, not an executable Phase 1 oracle. Its surface is `phase0/work/agg-n-census.txt`, a
direct scan of RD's `SpreadForm` records (`spread_form.n`: 10 ×37, 30 ×2, 4 ×4, 5 ×1, 7 ×1, 8 ×1);
`spread_form.n` is **not** on the frozen Contract I-1 measurement read-list, so no downstream rule
may compute it. The numbers PD002 actually emits on the admissible surface are **2 of 46**
(`unit=aggregation`, from `RD002.measurements.n_members`) and **12 of 56** (`unit=reported_cell`,
from `RD005.measurements.n`) — different keys, different unit, and therefore different counts. Both
carry their unit in the finding. **I-1 is NOT extended to recover the old verdict.**

## A2 — D7's expectation

| | |
|---|---|
| **Old statement** | line 270 (§10, D7 row): "PD002 | **PASS** — 'some' is existential…", and line 730 (§22) mandating "`test_acceptance_rtdl.py` (…, **D7 PASS**, …)" as a single PASS expectation. |
| **New statement** | The frozen expectation is a **rule vector, not a verdict**: `PD001` Traceability = **PASS** · `PD006` Result Reference Integrity = **PASS** · `PD002` Evidence Scope = **INCONCLUSIVE**. |
| **Reason** | The claim→reference relation is genuinely traceable (the sentence carries `\ref` to Table 4, and the numbering resolves), but no admissible upstream target carries a per-dataset count for a `comparison_member` universe, so the scope relation cannot be proved. `RD007` is `NOT_RUN` on zero comparison sets in the frozen RTDL artifact. |
| **Semantic impact** | **Clarifying.** D7 remains the false-FAIL guard §10 intended — the old row was right that a naive exhaustiveness reading is wrong, wrong that the residual is PASS. It also restates in oracle form the standing prohibition on collapsing a rule vector into an overall claim verdict: there is no "D7 = PASS" and no paper-level score, only per-rule findings. The *existential PASS* itself is not lost; it is pinned synthetically where the counts are admissible (adversarial row S13, line 613, unchanged). |
| **Implementation changed** | **No.** The delivered audit already emitted exactly this vector, and asserted "no `PD004` finding for D7". |

## A3 — D6's counterexample census

| | |
|---|---|
| **Old statement** | line 269 (§10, D6 row): "w/o-biases is **bold-best** on JA `0.727` and YE `8.843` … **FAIL** on **2/8 columns**, with JA recorded as a declared tie". |
| **New statement** | **1 of 8 columns** is a counterexample (`YE`: 8.855 vs 8.843), 7 supported, 0 ties, 0 undetermined. **The scientific rule status stays `FAIL`.** |
| **Reason** | `0.727` is in the **HI** column, not JA — a mis-read of the row's cell-to-header alignment. Bold-mark arithmetic is RD-owned (`RD007` / FM-P10), so PD must not consume it as evidence to raise its own count; and PD004's reading is value + declared direction, which yields the `YE` violation only. |
| **Semantic impact** | **None.** A census correction. `PD004` semantics are explicitly **not** changed: no new mark handling, no RD evidence borrowed, no threshold invented. The status the design cared about is unchanged. |
| **Implementation changed** | **No.** Delivered `n_counterexamples == 1`, `n_supported == 7`, `n_columns_in_scope == 8`, status `FAIL`. |

## A4 — RTDL caption locator / table number

| | |
|---|---|
| **Old statement** | line 279 (§10.1): "The paper declares, in **Table 2's caption `main.tex:375-376`**, `\textdownarrow ~ RMSE` / …". Repeated in `phase0/work/rtdl-claim-trace.md:47`. |
| **New statement** | `main.tex:375-376` is inside **Table 3's** caption (`tab:node`, which begins at `main.tex:367`). Table 2 (`tab:neural-networks`) begins at `main.tex:335` and carries its own notation at `main.tex:344-345`. |
| **Reason** | A locator/numbering slip in prose. The machine oracle `test_latex_index_oracle.py::RTDL_TABLES` — which pins `(2, 335, tab:neural-networks)` and `(3, 367, tab:node)` against the read-only corpus — already produced the correct numbering, so the index preceded the prose. |
| **Semantic impact** | **None.** No rule semantics change. Both notation lines genuinely exist, so every trace that depended on "the paper declares a direction in a caption" still holds; only the table number attached to those two lines was wrong. |
| **Implementation changed** | **No.** `latex_index.py` numbers by source order and was already correct. |

## A5 — D2/D3 universe census denominator

| | |
|---|---|
| **Old statement** | line 274 (§10, D2/D3 row): "re-computed raw artifacts: `output/{adult,aloi,california_housing}/mlp/tuned/*` = **15 runs each** … adult/aloi/CA **PASS on the declared universe of 15**; the other 8 datasets **UNKNOWN** ⇒ whole-table claim INCONCLUSIVE with census (**universe PARTIAL 3/11**)". Repeated at line 771. |
| **New statement** | The **Contract-I-1 executable universe count is 2**, with `unit = aggregation`. `PD002` may certify a `RECOVERED` universe over exactly the two aggregations the frozen RTDL artifact models, and `PARTIAL` over the printed table. |
| **Reason** | The `3/11` denominator counted `aloi`, which has **no admissible I-1 target** — it was known only from re-computed raw runs, i.e. from the research-round surface, not from `result-doctor audit --json`. This is the identical surface distinction A1 makes normative, applied to the second ledger. |
| **Semantic impact** | **None beyond A1's own rule, restated for D2/D3.** No rule change and no new read: `n_members` on `RD002` findings is already on the read-list, and every `PD002` count keeps declaring its unit (§12). I-1 is **not** expanded to recover `3/11`. |
| **Implementation changed** | **No.** `test_d3_passes_on_the_certified_subset` already asserts `n_targets_compared == 2` with `universe_status == "RECOVERED"`, and `test_d3_is_inconclusive_on_the_whole_printed_table` asserts `PARTIAL` — both from the first Phase 1 run. |

## Consequences for the frozen body

1. §§9, 10, 22 above are read **as amended by this erratum**. Where this section and a line above
   disagree, this section governs for A1–A5 only; every other frozen statement — the object model,
   the three link bases, the 12 `P_*` codes, PD001–PD007, the five states, Contract I-1, the §17
   firewall, §13's PD005 universe predicate — stands unamended.
2. The `9 / 46` line in §9's unit note (line 239-241) is **not** retracted; it is relabelled by A1
   as a research-round census on a non-I-1 surface, and is therefore not evidence PD may act on.
   The same applies to the `3 / 11` denominator of §10's D2/D3 row and its raw-run means at line 771,
   which A5 relabels identically.
3. **No oracle was weakened to obtain green tests.** A1 and A2 *reduce* what PD is permitted to
   assert; A3 changes only a count; A4 changes only a locator; A5 relabels a denominator that was
   never on the admissible surface. §28's "report the minimal
   contradiction, do not silently redesign" is what produced this erratum, and this section is where
   that report was answered.

*End of erratum. The Phase 0 body above it is unchanged from its frozen state.*
