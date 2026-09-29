# P0.3 — Paper B (RTDL, arXiv 2106.11959 "Revisiting Deep Learning Models for Tabular Data") claim → evidence reverse trace

AUTHORITATIVE input for `PAPER_DOCTOR_PHASE0_REPORT.md` §9. Re-verified in this session.

Paper identity (OBSERVED-DIRECT, derived from vendored evidence — not from a guess):
- the pinned official repository README `result-doctor/phase4/rtdl-revisiting-models/README.md:6`
  carries `:scroll: [arXiv](https://arxiv.org/abs/2106.11959)`; `main.tex:64`
  `\title{Revisiting Deep Learning Models for Tabular Data}` confirms it.
- e-print `phase0/sources/2106.11959.eprint`, 1185526 B, sha256
  `eebd40f5d9101237b6af85a216bdf70c5a0877592eaa20b2bb1b8a3b68aee8b9`
- `sources/2106.11959.tex/main.tex`, 1158 lines, plus 12 `\input`-separated table files.
- float numbering recomputed by `scripts/float_ref_map2.py` (recursive `\input` flattening)
  → `work/rtdl-float-ref.json`: 23 tables / 2 figures, nesting depth 1, document order
  `tab:datasets`=**Table 1**, `tab:neural-networks`=**Table 2**, `tab:node`=**Table 3**,
  `tab:nn-gbdt`=**Table 4**, `tab:ablation`=**Table 5**, `tab:feature-importances`=Table 6, …
- Downstream: RD's RTDL pilot (`phase4/rtdl-revisiting-models/result-doctor.yml`) yields
  **16 findings (PASS 6 / FAIL 0 / INCONCLUSIVE 6 / NOT_APPLICABLE 3 / NOT_RUN 1)**, canonical
  JSON 13395 B, sha256 `2ad02c8f…` (re-hashed this session, MATCH), `comparison_sets: 0`,
  `artifacts: 0`; both cell `value:` locators point at `README.md:80` and `README.md:82`.

---

## B-1  Real claim ledger

| # | claim (verbatim) | locator | support target | RD object / finding | diverges? | owner | PD rule | verdict |
|---|---|---|---|---|---|---|---|---|
| D1 | "*The output **exactly matches** Table 2 from the paper:*" | `README.md:76` | "Table 2" resolves deterministically to `tab:neural-networks`; its MLP row is `$0.499$&$0.852$&$0.383$&$0.719$&$0.723$&$0.954$&$0.8977$&$8.853$&$0.962$&$0.757$&$0.747$` (`data/table_neural_networks.tex:14`); README transcript lists 11 values, 4 of them negative — exactly the 4 `\textdownarrow` columns | RD models only 2 of these cells and never reads the paper: RD006/RD008 on the wording "…matches Table 2…" return INCONCLUSIVE "wording is not classifiable" (`rules.py:563-567`) | **cannot be decided**: identity unknown (see B-2) | **PD only** | PD003 | **INCONCLUSIVE** (not FAIL — see B-2; this is the case that pins PD's refusal rule) |
| D2 | "for each dataset, let's compute the test score **averaged over all random seeds**" | `README.md:70`, code `README.md:73` `df.groupby('dataset')['metrics.test.score'].mean().round(3)` | vendored census: `output/{adult,aloi,california_housing}/mlp/tuned/*` = **15 runs each**, recomputed means 0.852 / 0.954 / −0.499 | RD's manifest stores the wording verbatim as `spread_label`/`wording` with `observed:{path:README.md,line:70}` (`result-doctor.yml:60,86`); RD005 says "not classifiable" | no contradiction on the recovered subset | PD (scope) / RD (mechanics) | PD002 | **INCONCLUSIVE**: universe is **3 of 11 datasets** (PARTIAL); "all random seeds" cannot bind to a declared universe of 15 |
| D3 | Table 2 caption: "The metric values **averaged over 15 random seeds** are reported" | `main.tex:338` (caption of `tab:neural-networks`) | the same 15-run census, but only for MLP on 3 datasets | RD has no Table-2 aggregation objects at all | unverifiable beyond 3/11 × 1 model × 11 columns | PD | PD002 | **INCONCLUSIVE** with census (the audited part supports 15; 120 of 132 cells unverifiable) |
| D4 | Table 2 caption: "For each dataset, **top** results are in **bold**. ``Top'' means ``the gap … is **not statistically significant**''" | `main.tex:339-341` | `\textbf{}` marks per column in `table_neural_networks.tex`; standard deviations live in a different float (`tab:S-single-models-with-std`) | RD007 (`observed_marks` vs `recomputed_marks`) is the owner of mark consistency | mark rule needs a significance test the bundle cannot express | **RD** for marks / **PD** for the prose definition's cross-float dependency | PD006 (reference integrity: the claim's support requires a *second* table that the caption does not name by label) | **INCONCLUSIVE**; recorded as the boundary case that keeps RD007 out of PD |
| D5 | "in this regime, **\architecture\ outperforms NODE** and **the gap between ResNet and NODE is significantly reduced**" | `main.tex:364` | `data/table_node.tex:5-7` (Table 3): NODE YE `$\mathbf{8.716}$` (bold, ↓) vs FT-T `8.751`, ResNet `8.770`; FT-T beats NODE on 10/11 columns, ties AD `0.860`, loses YE | none — RD's RTDL pilot never touches the paper (`artifacts: 0`) | **YES**: one column (YE) contradicts the unqualified comparative; the "significantly reduced" clause has no comparator baseline | **PD only** | PD004 + PD005 | **FAIL** for the first clause read over Table 3 / **INCONCLUSIVE** for the second (no declared gap measure). Frozen judgment: one claim object per clause; the YE counterexample is a same-universe member ⇒ first clause **FAIL** |
| D6 | "…demonstrate both the superiority of the Transformer's backbone to that of AutoInt and **the necessity of feature biases**" | `main.tex:465` | Table 5 (`tab:ablation`, `\autoref` **in the same sentence**): `w/o feature biases` is **bold-best** on JA `$\mathbf{0.727}$` and YE `$\mathbf{8.843}$` (`data/table_ablation.tex:6`) while full FT-T is `0.732`/`8.855` | none | **YES**: on YE the no-bias variant is better (↓), and both rows carry the "top" bold ⇒ "necessity" is not supported on 2/8 columns | **PD only** | PD004 | **FAIL** (universal-strength claim with an in-table counterexample), with the measurement that JA is a declared tie |
| D7 | "GBDTs start dominating on **some** datasets (California Housing, Adult, Yahoo; see \autoref{tab:nn-gbdt})" | `main.tex:409` | Table 4: CatBoost `$\mathbf{0.741}$` best on MI ⇒ a 4th dataset exists | none | enumeration is **illustrative**, not exhaustive ("some") | **PD only** | PD002 | **PASS** — and the rule must PASS here; a naive exhaustiveness reading would emit a false FAIL (adversarial case S13) |
| D8 | "The big difference on the Yahoo dataset is expected because of the large number of features **(700)**" | `main.tex:590` | `data/table_datasets.tex:6` `\#num. features … 699` for YA | none | **YES**, delta = 1 (0.14 %) | **PD only** | PD003 | **INCONCLUSIVE** — closeness is not a PASS and no precision semantics is declared for prose (Table 3's caption declares a rounding note at `main.tex:373`, **Table 2/1 do not**) |
| D9 | "Due to the limited precision, some \textit{different} values are represented with the same figures" | `main.tex:373` (caption of Table 3, env `:367`) | scope = Table 3 only | none | — | **PD only** | PD003 | OBSERVED as an **author-declared precision semantics** object with a *table scope*; it is the reason PD003 must carry a per-scope declared tolerance rather than a global one |
| D10 | abstract: "which **outperforms other solutions on most tasks**" | `main.tex:95` | Table 2 rank column: FT-T `1.8 (1.2)` best; per-column wins 8/11 bold | none | consistent under "most = ≥ half", undeclared otherwise | PD | PD004 | **INCONCLUSIVE** ("most" undeclared quantifier) |
| D11 | conclusion: "outperforms other **DL** solutions on most of the tasks" | `main.tex:499` | same target, narrower class ("DL") | none | **scope differs from D10** ("solutions" ⊃ "DL solutions") — GBDT results in Table 4 contradict the broader reading | PD | PD007 (cross-section) + PD002 | **FAIL on PD007** as a pair: the two sentences state the same result with different scopes and no reconciliation; note this is exactly the abstract-vs-conclusion drift RD cannot see |
| D12 | "ResNet turns out to be an effective baseline that **none of the competitors can consistently outperform**" | `main.tex:355` | Table 2 ResNet row `$0.499$&$0.852$&$0.383$…`, rank 3.3 (1.8) | none | "consistently" undeclared | PD | PD004 | **INCONCLUSIVE** |
| D13 | MLP row identity used by RD's pilot (values printed at `table_neural_networks.tex:14`) | paper | RD cell locators = `README.md:80/:82` | RD006 INCONCLUSIVE "wording … not classifiable" | — | RD keeps cell↔run; PD owns cell↔prose | — | demonstrates the exact seam |

---

## B-2  Why D1 is INCONCLUSIVE and not FAIL (frozen reasoning)

Evidence assembled this session, all first-hand:
1. README's declared quantity key is `metrics.test.score` (`README.md:73`).
2. The paper's declared quantity for the 4 ↓ columns is **RMSE** (`main.tex:375`
   `\textdownarrow \sim RMSE`, and `data/table_datasets.tex` `metric` row: CA/YE/YA/MI = RMSE,
   the other seven = Acc.).
3. Raw artifacts: `output/california_housing/mlp/tuned/0/stats.json` carries **both**
   `metrics.test.rmse = 0.49420855673906827` and `metrics.test.score = -0.49420855673906827`
   (identical magnitude, opposite sign). Mean over the 15 runs: `score = -0.499`, i.e.
   `|mean score| = 0.499` = the printed `CA $0.499$`.
4. The sign convention that makes `score` a maximisation objective is implemented in
   **`lib.py`, which is NOT part of the vendored slice** (`phase4/rtdl-revisiting-models/bin/`
   contains only `mlp.py` and `tune.py`; `mlp.py:195` merely writes `{'score': -999999999.0}`
   as a failure sentinel). So the identity `score ≡ ±RMSE` / `score ≡ accuracy` is
   **UNKNOWN**, not OBSERVED and not DECLARED.

Consequence frozen as a rule property: when two loci declare different quantity keys and no
declared identity connects them, PD003 emits **INCONCLUSIVE** carrying the measured
relationship (here `abs(-0.499) == 0.499`) as a *measurement*, never as a verdict. Numerical
closeness, sign patterns, column-arrow alignment and filename similarity are recorded as
measurements only. This single case is what forces PD to reuse RD's
`Locus.quantity_key` discipline (`schema.py:81-94`: "two printed cells are only comparable
once they are declared to be the same quantity") instead of inventing a parallel notion.

## B-3  Hypothesised but NOT OBSERVED

| hypothesis | search | outcome |
|---|---|---|
| RTDL prints a ± for Table 2 that RD could audit | read caption `:338` "See supplementary for standard deviations" | Table 2 has no dispersion column ⇒ RD001/RD005 NOT_APPLICABLE by construction; **not** a PD finding |
| Table 2 bold marks inconsistent with values | `table_neural_networks.tex` rows: AD `0.859` bold in AutoInt **and** FT-T (tie); `0.857/0.858` also bold | RD007 owns it; PD excluded by tribunal |
| `\ref` target errors | `float_ref_map2.py` unresolved list = only `eq:*`/`sec:*` labels (float refs all resolve) | **NOT OBSERVED** for tables/figures in this paper → PD006's positive motivation comes from GMMVI C1 only |
| 15-seed claim verifiable for all cells | `output/` census = 3 datasets, `mlp` only | PARTIAL universe, recorded as such (D2/D3) |
| README↔paper divergence count "4 sign flips + 1 rounding" | recomputed | **corrected**: within the recovered universe only 3 datasets exist (2 exact, 1 sign); the remaining 8 comparisons are UNKNOWN, so no count over 11 may be published. Prior draft's "6/11 exact" figure is superseded and must not be cited. |
