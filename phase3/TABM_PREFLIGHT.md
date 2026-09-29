# TabM preflight — Paper Doctor Phase 3 §3

Status: **COMPLETE. All five feasibility answers are YES. No STOP triggered.**
Date: 2026-09-29. No production code was changed while this document was being produced; everything
below is measurement on pinned, read-only inputs.

The acceptance target was chosen by the user (Phase 3 §1): *TabM: Advancing Tabular Deep Learning with
Parameter-Efficient Ensembling*, ICLR 2025, `https://github.com/yandex-research/tabm`.

---

## 1. Pinned inputs

| Input | Pin | How it was pinned |
|---|---|---|
| Code + result-artifact repository | commit `28e47ae301c92ec37787dde1ce923a0793f405b4` (commit date 2025-11-10 10:17:57 +0300) | `git rev-parse HEAD` on the read-only clone at `F:/MLResearch/upstream/tabm` |
| Paper source (LaTeX) | arXiv `2410.24210` tarball, `sha256 cdcea2ddbe710fa6e9c19b0e611e0c82dd513491aa6ac680368ed5bc3127db8c` | digest of the downloaded tarball; extracted to `F:/MLResearch/upstream/tabm-arxiv/src` |
| Audited paper entry point | `main.tex`, `sha256 15663553d04fcbb8b3341df5c0d269c7703d4ba279be557fcd77ea4765ab0a62`, 88033 bytes | `sha256sum` / `wc -c`, recorded in the manifest registry |
| Dataset for the DD layer | UCI Adult official copy at `F:/DatasetDoctorWork/realworld/adult` (`raw/adult.data` 3,974,305 B, `raw/adult.test` 2,003,153 B, `prepared/train.csv` 32,562 lines, `prepared/test.csv` 16,282 lines) | read-only; DD's own 0.1.x CLI (`dataset-doctor-audit`) is installed and used unchanged |

**The repository carries no LaTeX source.** `tabm/paper/` holds the paper-related content (run code,
configs, metrics, `figures/`, `environment.yaml`) but not the compilable paper. The arXiv source is
therefore the structured paper input, and it is pinned by digest rather than by "latest". This is
recorded because it changes what "repo SHA" can mean for the paper layer: two pins, not one.

Repository license: Apache-2.0 (`tabm/LICENSE`, 201 lines). No upstream file is vendored into
Paper Doctor; the acceptance workspace references the pinned copies by path.

## 2. Artifact layout (what the repo actually ships)

```
paper/bin/{go.py,train.py,evaluate.py,ensemble.py,tune.py,metrics.py}   generation scripts
paper/environment.yaml                                                  pinned conda environment
paper/exp/<family>/<dataset>/
        0-tuning.toml, 0-tuning/<i>/report.json                         tuning runs
        0-evaluation/<seed>/report.json + <seed>.toml                   one run per seed
        0-ensemble-5/<i>/report.json                                    ensemble members
```

Families present: `tabm`, `tabm-mini`, `tabm-packed`, `tabm-piecewiselinear`,
`tabm-sharetrainingbatches*`, `mlp`, `mlp-periodic`, `mlp-periodiclite`, `mlp-piecewiselinear`.
Datasets per family include `adult`, `churn`, `california`, `house`, `diamond`, `otto`,
`higgs-small`, `black-friday`, `covtype2`, `microsoft`, plus `why/` and `tabred/` sub-groups.

**Metric**: `/metrics/test/score` (accuracy for binclass/multiclass, −RMSE for regression — the sign
convention is recorded so no rule is fed an inverted reading).
**Hyperparameters**: the per-run `.toml` mirrors `report.json.config` (seed, batch_size, patience,
n_epochs, amp, gradient_clipping_norm, `[data] path/num_policy/cat_policy`, `[optimizer]`,
`[model]`, `[model.backbone]`).
**Dataset reference inside the run**: `config.data.path = "data/adult"` — a repo-relative path, i.e. a
*declared* reference, not a fingerprint. The dataset identity must come from the DD layer.

### Worked example used below (all values read, not computed by the tool)

`paper/exp/tabm/adult/0-evaluation/{0..14}/report.json` = 15 seed runs.
`/metrics/test/score` over those 15: mean `0.8575`, sample std (ddof = 1) `0.0008`, population std
(ddof = 0) `0.0007`. The ddof is *discriminated* by the rounding, not assumed: the paper-style
`± 0.0008` is reachable only with ddof = 1. One run (`0-evaluation/3`): `seed = 3`,
`batch_size = 256`, `n_epochs = -1`, `patience = 16`, `amp = true`,
`model = {arch_type: tabm, k: 32, share_training_batches: false, backbone: MLP n_blocks 4, d_block
320, dropout 0.3865104245869764}`, `optimizer = {AdamW, lr 0.0009176025148173867, weight_decay 0.0}`,
`gpus = ["NVIDIA A100-SXM4-80GB"]`, `time = 0:00:37.666768`, `n_parameters = 478400`,
`best_step = 6324`, `function = bin.model.main`, `/metrics/test/score = 0.858731036177139`.

## 3. Paper source structure, measured by the generic index

`build_index(root, main.tex)` on the ICLR source: **15 chunks** (from `\input`), **26 floats**,
**136 reference sites**, **55 references that do not resolve to a float** (sections, appendix
figures). Flattening across `\input` works: `table:4`'s body contains the rows of
`tables/app-rtdl-datasets.tex` verbatim.

Float inventory (source-order numbering, the model Phase 0 froze):

| anchor | label | note |
|---|---|---|
| table:1 | `tab:datasets` | benchmark summary; header is a *column-group* row (`\multicolumn{4}{c}{Train size}` …) |
| table:2 | `tab:large` | RMSE + training time on two large datasets; **parses, 2 row-blocks** |
| table:3 | `A:tab:n-params` | **parses, 1 row, 6 columns** — the table is transposed, so the reader takes the first value as the row label |
| table:4 | `A:tab:default-datasets` | 10 dataset rows, **grid unrecoverable** |
| table:5 | `A:tab:tabred-datasets` | 8 dataset rows, **grid unrecoverable** |
| table:6–17 | `A:tab:tabm-space`, `…-emb-space`, `mlp-*`, `mnca-*`, `t2g-space`, `saint-hp`, `excel-space` | hyperparameter spaces, **grid unrecoverable** |
| figure:1–9 | `fig:model`, `fig:performance`, `A:fig:main-comparison`, … | no tabular |

Row-block detection ran cleanly on the unseen corpus: no crash, `table:2` produced
`b1` (`midrule at main.tex:524`; merged cell spanning 2 rows) and `b2` (`hline at main.tex:544`;
merged cell), and `table:3` produced one block. Column-group headers (`table:1`) were **not**
mistaken for row blocks.

## 4. Feasibility answers

### A. Can at least one empirical paper claim be deterministically linkable to a printed table/figure/result? — **YES**

Two claims are literally printed in `main.tex`, each stating a count and naming the float by
`\autoref` in the same sentence:

- line 878: `$10$ datasets from other sources. Their properties are provided in
  \autoref{A:tab:default-datasets}.`
- line 884: `$8$ datasets from the TabReD benchmark \citep{rubachev2024tabred}. Their properties are
  provided in \autoref{A:tab:tabred-datasets}.`

The generic index resolves `A:tab:default-datasets` → `table:4` and `A:tab:tabred-datasets` →
`table:5`; the reference site is recorded at the claim's own line (`main.tex:879`, `main.tex:885`).
The first audit run (`phase3/tabm/`, zero adapter, zero PD code change) produced PD001 PASS for both,
PD001 INCONCLUSIVE for an unlinked claim (line 874, "$28$ datasets from Grinsztajn — see the original
paper"), PD005 INCONCLUSIVE for the derived-count sentence at line 1046, PD006 PASS on `table:4`, a
PD006 FAIL on `table:5`, and PD002/PD003/PD004/PD007 in their documented not-applicable / not-run
states. Deterministic linkability is demonstrated, including the *negative* case: PD refuses to
count rows or do the arithmetic a claim omits.

### B. Is at least one reported result traceable for Result Doctor? — **YES**

`tabm/adult` has 15 per-seed `report.json` artifacts; the aggregation is exactly reconstructible
(§2). No RD rule, schema, or code is touched: the RD layer is a `result-doctor.yml` written over
public artifacts, and `result-doctor audit --json` output is the only PD input (Contract I-1).

**Caveat recorded, not hidden**: the *printed* per-dataset metric values live in
`tables/per-dataset-{default,why,tabred}.tex`, which are `\begin{longtable}` inclusions with a
`\caption` and **no `\label`**, included bare at `main.tex:1424–1426` — not inside a `table`/`figure`
float. The frozen float set (`table*`, `table`, `figure*`, `figure`) cannot address them, so there is
**no paper-side printed locus for the adult metric that PD can audit**. This is a documented boundary
(§13: do not silently extend). `tab:large` and `A:tab:n-params` are addressable but are not
reconstructible from the shipped artifacts (they report Maps Routing/Delivery ETA RMSE and mean
parameter counts over a 46-dataset population whose unit is under-determined) — so no chain is built
on them.

### C. Is at least one run / config / seed / environment traceable for Experiment Doctor? — **YES**

`0-evaluation/3` gives seed, full config, tuned hyperparameters, metric, `best_step` (selection
provenance), `n_parameters`, GPU model, wall time; `paper/environment.yaml` pins the conda
environment; `pyproject.toml` + `uv.lock` pin the package; the repo commit pins the code version.
UNKNOWN remains valid where upstream genuinely states nothing (no separate checkpoint URI, no
per-run git SHA inside `report.json`); the ED layer will record those as UNKNOWN rather than
manufacturing them. ED's own contract has no arbitrary-JSON-by-reference input, so the ED layer is
built from ED's declared surface, not by extending ED.

### D. Is at least one dataset's identity and split traceable for Dataset Doctor? — **YES**

Table 4's Adult row states `26\,048 / 6\,513 / 16\,281` and task type Binclass; `26\,048 + 6\,513 =
32\,561`, which is the official UCI `adult.data` record count, and `16\,281` is `adult.test`. The
local official copy is present (§1) and DD's CLI runs unchanged against `prepared/train.csv` +
`prepared/test.csv`, producing its own fingerprint, split identity and verdict per DD's contract.
No DD code changes; no new adapter unless DD's own contract requires one for CSV layout.

### E. Is this doable without any RTDL-specific hardcode or assumption? — **YES (to be proven by §12)**

Nothing above uses the RTDL corpus, its paths, its method names, or its table numbering. TabM's
tables were read by the same `build_index`/`parse_table` code as the pilots, the manifest uses the
same four sections as Phase 2's README, and the RD snapshot uses the same `--json` artifact shape.
The firewall tests (Phase 3 §12) will assert that `src/` contains no `tabm`, `yandex`, `rtdl`, or
`GMMVI` branch, no hardcoded table numbers, metric values, or dataset names.

---

## 5. Defects the unseen paper exposed (measured, with disposition)

These are findings *of* the preflight. None of them is a change of scientific design; each is either
a documentation boundary or a reader-fidelity fix, and each is backed by a measured input.

### D1 (P0, reader fidelity) — LaTeX digit grouping fragments numbers

`plain_text` turns the spacing macros `\,`, `\;`, `\:` into a space, so the cell `$26\,048$` becomes
`26 048`, and the literal extractor returns `26` and leaves `048` unextracted. Measured:

```
'$26\,048$' -> '26 048' -> number 26.0        (the cell states twenty-six thousand forty-eight)
'$723\,412$' -> '723 412' -> number 723.0
row 'Adult & $26\,048$ & …' -> "the claim states 7 numeric literals (26, 6, 16, 6, 1, 8, 256)"
```

Consequence, reachable today: a claim that states `26048` against a float that prints `$26\,048$`
is reported as *the float does not print it* (false FAIL), and a row quoted verbatim is reported as
stating seven unrelated numbers (false INCONCLUSIVE). Neither verdict is a design judgement; both are
a tokenizer losing a separator that LaTeX uses for no other purpose between digits.
**Disposition**: recognize a digit-group separator written as a LaTeX thin-space macro
(`\,`, `\;`, `\:`) between digits, so `26\,048` reads as one number. **Not** extended to the plain
comma: `phase0/sources/2106.11959.tex/main.tex:710` prints `$\mathrm{UniformInt}[64,512]$`, where the
comma is an interval separator, and `$0,1,2$` lists values — a comma between digits is genuinely
ambiguous in this corpus pair, and PD will not guess. A generic regression fixture (no project name,
no TabM-specific branch) accompanies the fix.

### D2 (P1, reader coverage) — a header that names its row-label column is unreadable

`parse_table` accepts an empty header corner, or a non-empty corner *licensed* by a vertically merged
leading cell; otherwise it returns `None`. TabM prints the ordinary academic layout —
`Name & \# Train & \# Validation & … ` with no merges — and **15 of its 17 tables (table:1, 4–17)
therefore have no addressable cells at all**. Measured corner/arity per float in §3. RTDL and GMMVI
never exposed this because their audited tables use empty corners or merge columns, so the gap was
invisible to both pilot acceptances.
**Disposition**: license the reading when it is the *only* reading — a header row that contains no
multi-column group span and a table whose rows all carry the same cell count. The spec arity is then
redundant (TabM's `table:4` declares 10 columns and prints 9 in every row; LaTeX renders the extra
column empty), and self-consistency replaces arity-matching as the guard. When the table is *not*
self-consistent, the reader still returns `None` and PD still cannot address it — the failure mode is
preserved, only the ambiguity is removed.

### D3 (boundary, no code change) — counts realized by row multiplicity

PD006 asks whether the numeral a claim states is printed inside the float the claim points at.
`table:4` prints `10` (Covertype's `# Num`) so C1 PASSes; `table:5` prints no standalone `8` and FAILs,
with the reason listing the eight floats that do print `8`. Both verdicts are literally true about the
bytes and neither is a claim about whether the table lists eight datasets — PD does not count rows and
Phase 0 froze that. **Disposition**: no design change; the README must state PD006's check as the
literal-presence test it is, so a PASS is not read as "the table carries the attributed content" and a
FAIL is not read as "the paper is wrong". Verified as part of §17.

### D4 (boundary, no code change) — macro-defined numbers

`lib.sty:40` defines `\newcommand{\ndatasets}{46}`, `\nrandomsplits{37}`,
`\ndomainawaresplits{9}` and the paper writes `\ndatasets` in both prose and `table:1`. PD does not
expand macros (it reads source text, not a compiled document), so the headline number of the paper's
own benchmark table is unreadable, and any claim about it is INCONCLUSIVE.
**Disposition**: documented limitation. Adding a macro expander is new machinery and is not done in
final acceptance (Phase 3 §13).

### D5 (observation, no change) — transposed table and unlabelled longtables

`A:tab:n-params` is transposed (model names across the header, values in one row), and the reader
takes the first value as the row label — a wrong-looking but *unused* reading, since no claim
addresses it; recorded rather than fixed. The per-dataset metric tables are unlabelled `longtable`s
and cannot be addressed at all (§4.B). Neither is extended.

### Anti-fabrication, verified as a property, not assumed

A claim whose text is not the paper's own bytes is rejected at load time:

```
P_UNRESOLVED_REF at main.tex:878: declared claim text is not present in the source file   (exit 2)
```

so the acceptance cannot be "passed" by declaring a sentence TabM never wrote — the failure mode
Phase 2 hit on GMMVI Table 8 is structurally closed at the manifest layer, on an unseen paper.

## 6. Chains Phase 3 will build (selected against §5 criteria)

**Chain 1 — Adult, four layers.** Paper claim: `table:4`'s Adult row, the paper's own bytes at
`tables/app-rtdl-datasets.tex:8`, asserting Adult's split sizes, feature counts and task type
(PD, after D1/D2). RD: the 15-seed `tabm/adult` aggregation, mean `0.8575` with sample spread
`± 0.0008` and a render step at 4 decimals. ED: run `0-evaluation/3` — seed, config, tuned
hyperparameters, `best_step` selection provenance, GPU and pinned `environment.yaml`, with UNKNOWN
where the repo states nothing. DD: the official Adult copy, its fingerprint and split identity.
The layers are joined by *declared* references recorded in the ledger; PD computes no cross-layer
similarity.

**Chain 2 — dataset-composition counts, PD only.** Claims at `main.tex:878` and `main.tex:884`
(PD001/PD006), plus the unlinked claim at `main.tex:874` and the derived-count sentence at
`main.tex:1046`, which must come out traceable-and-inconclusive, demonstrating that PD refuses to
invent the arithmetic.

**Chain 3 — block addressing on an unseen table.** `tab:large` (`table:2`) genuinely has two row
blocks opened by a `midrule`/`hline` plus a 2-row merged leading cell; the block reader produces
`b1`/`b2` with quoted structural evidence. Claim candidate: `main.tex:1001` ("The two datasets used
in \autoref{tab:large} are the *full* versions of the 'Weather' and 'Maps Routing' datasets from the
TabReD benchmark") as a real, author-written reference to that float. No metric value is asserted
from `tab:large`, because §4.B says its values are not reconstructible from the shipped artifacts.

## 7. What this preflight does not claim

No PD verdict has been asserted on Chain 1 or Chain 3 yet — the claims are selected, not yet judged.
Nothing here says TabM is right, wrong, reliable, or fraudulent; it says which of its statements can
be reached by the machinery as frozen, and which cannot.
