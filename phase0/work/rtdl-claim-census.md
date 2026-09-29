# RTDL Claim Census — arXiv:2106.11959 "Revisiting Deep Learning Models for Tabular Data"

READ-ONLY extraction for Paper Doctor phase 0. Sources (pinned, already downloaded):
`F:\MLResearch\paper-doctor\phase0\sources\2106.11959.tex\main.tex` (1158 lines),
`data\table_*.tex` (12 files), `lib.sty` (needed to resolve macros; see §1.4),
secondary: `F:\MLResearch\result-doctor\phase4\rtdl-revisiting-models\README.md`.
Every fact below carries file+line. No outside knowledge of the paper was used.
Macro resolution used throughout: `\architecture` = "FT-Transformer", `\arch` = "FT-T",
`\tokenizer` = "Feature Tokenizer", `\repository` = `https://github.com/yandex-research/tabular-dl-revisiting-models`
(all defined in `lib.sty:23–26`).

---

## 1. Structural map

### 1.1 Sections (main.tex)

| Line | Section |
|---|---|
| 87 | Abstract (env, not sectioned) |
| 101 | §1 Introduction |
| 134 | §2 Related work |
| 165 | §3 Models for tabular data problems |
| 180 | §3.1 MLP |
| 196 | §3.2 ResNet (`\label{sec:resnet}` 197) |
| 214 | §3.3 FT-Transformer (`\label{sec:transformer}` 215) |
| 266 | §3.4 Other models (`\label{sec:other-models}` 267) |
| 282 | §4 Experiments |
| 287 | §4.1 Scope of the comparison |
| 291 | §4.2 Datasets (`\label{sec:datasets}` 292) |
| 305 | §4.3 Implementation details (`\label{sec:implementation-details}` 306) |
| 333 | §4.4 Comparing DL models |
| 382 | §4.5 Comparing DL models and GBDT (`\label{sec:nn-gbdt}` 383) |
| 421 | §4.6 An intriguing property of FT-Transformer (`\label{sec:intriguing-property}` 422) |
| 430 | §5 Analysis |
| 432 | §5.1 When FT-Transformer is better than ResNet? (`\label{sec:synthetic}` 433) |
| 456 | §5.2 Ablation study (`\label{sec:ablation}` 457) |
| 476 | §5.3 Obtaining feature importances from attention maps |
| 495 | §6 Conclusion |
| 512 | Supplementary `\section*` (lettered A–H by 510 renewcommand) |
| 514 | S-A Software and hardware |
| 523 | S-B Data (525 S-B.1 Datasets; 537 S-B.2 Preprocessing) |
| 545 | S-C Results for all algorithms on all datasets |
| 568 | S-D Additional results (570 S-D.1 Training times; 592 S-D.2 tuning time budget) |
| 627 | S-E FT-Transformer (631 architecture; 661 default config; 723 training) |
| 727 | S-F Models (730 ResNet, 767 MLP, 799 XGBoost, 836 CatBoost, 873 SNN, 901 NODE, 911 TabNet, 947 GrowNet, 978 DCN V2, 1014 AutoInt) |
| 1045 | S-G Analysis (1047 synthetic; 1094 ablation) |
| 1110 | S-H Additional datasets |

Note: main.tex:167 references "section 3.2"/"section 3.3" as **hard-coded literal strings**, not `\ref`; in the compiled numbering ResNet is §3.2 and FT-Transformer §3.3 (source order) — consistent, but a literal string a parser cannot check.

### 1.2 Floats (label / caption verbatim ≤160 chars / lines)

| Label | Float | Caption (verbatim, truncated to 160) | Lines |
|---|---|---|---|
| (none) | eq | MLP definition | 185 `\label{eq:mlp}` |
| eq:resnet | eq | ResNet definition | 202 |
| fig:arch | figure | "The FT-Transformer architecture. Firstly, Feature Tokenizer transforms features to embeddings. The embeddings are then processed by the Transformer module and the final representat…" | 222–227 (caption 225, label 226) |
| fig:blocks | figure | "(a) Feature Tokenizer; in the example, there are three numerical and two categorical features; (b) One Transformer layer." | 229–234 (cap 232, lab 233) |
| tab:datasets | table | "Dataset properties. Notation: ``RMSE' ~ root-mean-square error, ``Acc.' ~ accuracy." | 296–303 (cap 299, lab 300, `\input` 302) |
| tab:neural-networks | table | "Results for DL models. The metric values averaged over 15 random seeds are reported. See supplementary for standard deviations. For each dataset, top results are in bold. ``Top' means…" | 335–349 (cap 338–345, lab 346, `\input` 348) |
| tab:node | table | "Results for ensembles of DL models with the highest ranks (see autoref{tab:neural-networks}). For each model-dataset pair, the metric value averaged over three ensembles is reported…" | 367–380 (cap 370–376, lab 377, `\input` 379) |
| tab:nn-gbdt | table | "Results for ensembles of GBDT and the main DL models. For each model-dataset pair, the metric value averaged over three ensembles is reported. See supplementary for standard deviations. Notation follows autoref{tab:node}." | 390–399 (cap 393–395, lab 396, `\input` 398) |
| fig:synthetic | wrapfigure | "Test RMSE averaged over five seeds (shadows represent std. dev.). One α corresponds to one task; each task has the same set of train, validation and test features, but different targets." | 443–450 (cap 448, lab 449, `\input` 446) |
| tab:ablation | table | "The results of the comparison between FT-Transformer and two attention-based alternatives: AutoInt and FT-Transformer without feature biases. Notation follows autoref{tab:neural-networks}." | 467–474 (cap 468, lab 470, `\input` 473) |
| tab:feature-importances | table | "Rank correlation (takes values in [-1, 1]) between permutation test's feature importances ranking and two alternative rankings: Attention Maps (AM) and Integrated Gradients (IG). Means and standard deviations over five runs are reported." | 486–493 (cap 489, lab 490, `\input` 492) |
| tab:S-datasets | table | "Datasets description" | 528–535 (`\input` 534) |
| tab:S-single-models | sidewaystable (1st caption) | "Results for single models with standard deviations. For each dataset, top results for baseline neural networks are in bold, top results for baseline neural networks and FT-Transformer are in blue…" | 551–565 (cap 554, lab 555, `\input` 557) |
| tab:S-ensembles | **same** sidewaystable (2nd caption) | "Results for ensembles with standard deviations. Color notation follows autoref{tab:S-single-models}, "top" results are defined as in autoref{tab:node}. Best viewed in colors." | cap 561, lab 562, `\input` 564 |
| tab:S-training-times | table (inline tabular) | "Training times in seconds averaged over 15 runs." | 571–587 (tabular 577–586) |
| tab:S-tuning-time-budget | table | "Performance of tuned models with different tuning time budgets. Tuned model performance and the number of Optuna iterations (in parentheses) are reported (both metrics are averaged over five random seeds)…" | 615–624 (cap 617, lab 618, `\input` 622) |
| tab:S-default-config | table (inline) | "Default FT-Transformer used in the main text." | 666–687 |
| tab:S-transformer-space | table (inline) | "FT-Transformer hyperparameter space. Here (A) = {CA, AD, HE, JA, HI} and (B) = {AL, YE, CO, MI}" | 699–721 |
| tab:S-resnet-space | table (inline) | "ResNet hyperparameter space. Here (A) = {CA, AD, HE, JA, HI, AL} and (B) = {EP, YE, CO, YA, MI}" | 743–765 |
| tab:S-mlp-space | table (inline) | "MLP hyperparameter space. Here (A) = {CA, AD, HE, JA, HI, AL} and (B) = {EP, YE, CO, YA, MI}" | 777–797 |
| tab:S-xgboost-space | table (inline) | "XGBoost hyperparameter space. Here (A) = {CA, AD, HE, JA, HI} and (B) = {EP, YE, CO, YA, MI}" | 811–834 |
| tab:S-catboost-space | table (inline) | "CatBoost hyperparameter space. Here (A) = {CA, AD, HE, JA, HI} and (B) = {EP, YE, CO, YA, MI}" | 849–868 |
| tab:S-snn-space | table (inline) | "SNN hyperparameter space. Here (A) = {CA, AD, HE, JA, HI, AL} and (B) = {EP, YE, CO, YA, MI}" | 879–899 |
| tab:S-tabnet-space | table (inline) | "TabNet hyperparameter space." | 924–945 |
| tab:S-grownet-space | table (inline) | "GrowNet hyperparameter space." | 956–976 |
| tab:S-dcn2-space | table (inline) | "DCN V2 hyperparameter space. Here (A) = {CA, AD, HE, JA, HI, AL} and (B) = {EP, YE, CO, YA, MI}" | 990–1012 |
| tab:S-autoint-space | table (inline) | "AutoInt hyperparameter space. Here (A) = {CA, AD, HE, JA, HI} and (B) = {AL, YE, CO, MI}" | 1024–1043 |
| alg:S-random-tree-construction | algorithm | "Construction of one random decision tree." | 1061–1092 (cap 1089, lab 1090) |
| tab:S-ablation | table | "The results of the comparison between FT-Transformer and two attention-based alternatives. Means and standard deviations over 15 runs are reported" | 1097–1108 (cap 1100, lab 1102, `\input` 1105) |
| tab:S-additional-datasets | table (inline) | "Additional datasets" | 1113–1128 |
| tab:S-additional-results | table (inline) | "Results for single models on additional datasets." | 1130–1156 (tabular 1139–1153) |

### 1.3 `\input` of data/*.tex (all in main.tex)

| main.tex line | file | wrapped in |
|---|---|---|
| 302 | data/table_datasets.tex | `{\footnotesize …}` |
| 348 | data/table_neural_networks.tex | `{\footnotesize …}`, `\tabcolsep2.2pt` (336) |
| 379 | data/table_node.tex | `{\footnotesize …}` |
| 398 | data/table_nn_gbdt.tex | `{\footnotesize …}` |
| 446 | data/image_gbdt_vs_nn.tex | `\scalebox{0.55}{…}` inside wrapfigure 0.5\textwidth |
| 473 | data/table_ablation.tex | `{\small …}` |
| 492 | data/table_feature_importance.tex | `{\small …}` |
| 534 | data/table_datasets_verbose.tex | bare, `\tabcolsep2.4pt` |
| 557 | data/table_single_models_with_std.tex | `\small` (556) inside sidewaystable |
| 564 | data/table_ensembles_with_std.tex | `\small` (563) inside **same** sidewaystable |
| 622 | data/table_tuning_time_budget.tex | `\makebox[\textwidth][c]{…}` (621–623) |
| 1105 | data/table_ablation_with_std.tex | `\footnotesize` + `\makebox[\textwidth][c]{…}` (1103–1106) |

### 1.4 Alignment ambiguity for a text parser

- **No `\resizebox` anywhere** (grep: zero hits). Sizing done by `{\footnotesize …}` / `{\small …}` (302, 348, 379, 398, 473, 492, 556, 563, 1103, 1138), `\scalebox{0.55}` (446), `\makebox[\textwidth][c]` (621, 1104), `\setlength\tabcolsep{2.2–5pt}` (297, 336, 368, 391, 472, 487, 529, 553, 572, 616, 1099, 1114, 1131), `\renewcommand{\arraystretch}{1.2}` (704, 748, 782, 816, 854, 884, 929, 961, 995, 1028). Typography is therefore irrelevant to cell parsing (pure `&`-splitting works), BUT:
- **Header arrows encode direction**: `CA \textdownarrow` etc. (e.g. data/table_neural_networks.tex:3) — direction is only in the header token and in caption notation lines (main.tex:344–345, 375–376, 395, 468); `data/table_feature_importance.tex:3` has **no arrows at all** → direction unresolvable there (see claims C33).
- **Mean and std share one cell** as `$0.459 \scriptscriptstyle \pm \scriptstyle 3.5e\text{-}3$` (single_models_with_std:19) → one `&`-cell holds two numbers plus `\text{-}` inside; the rank cell in the main NN table is instead **two separate math tokens** `$3.3$ $(1.8)$` (neural_networks:6–22) — inconsistent encoding between sibling tables.
- **`\multicolumn{12}{c}{Default hyperparameters}` / `{Tuned hyperparameters}`** (nn_gbdt:5, 11) and `{Baseline Neural Networks}` / `{\architecture}` / `{GBDT}` (single_models_with_std:5, 16, 21; ensembles_with_std:5, 16, 21) are *in-table section dividers* with no column structure — a row-only parser loses the block membership of every following row.
- **`\multicolumn{9}{c}{California Housing}` blocks** (tuning_time_budget:6, 15, 23) likewise.
- Transposition: `table_datasets.tex` is dataset-per-**column** (line 3), `table_datasets_verbose.tex` is dataset-per-**row** (lines 6–16); same entity, two axes.
- `\textsubscript{d}` row labels (single_models_with_std:18, 23, 25) render "FT-Transformerd" in text; "d" = "default" is defined only in the caption (main.tex:554).
- `\resizebox` absence excepted, the worst ambiguity: main.tex 551–565 puts **two `\caption`+`\label` pairs in one float environment**.

---

## 2. Claim census (35 claims)

Type codes: SUP=superiority/comparison, SCOPE=coverage/scope, NUM=printed number, PROTO=protocol/budget/seeds, ENUM=dataset enumeration, QUAL=qualitative-but-substantive.
Direction column: "RMSE↓ / Acc↑" means stated in source (caption arrows + `tab:datasets` metric row, data/table_datasets.tex:8).

| id | section | line | verbatim sentence (or load-bearing clause) | type | numbers verbatim | refs verbatim | qualifiers present | metric & direction |
|---|---|---|---|---|---|---|---|---|
| C01 | Abstract | 93 | "In this work, we perform an overview of the main families of DL architectures for tabular data and raise the bar of baselines in tabular DL by identifying two simple and powerful deep architectures." | QUAL | "two" | none | "main families", "simple and powerful" | n/a |
| C02 | Abstract | 94 | "The first one is a ResNet-like architecture which turns out to be a strong baseline that is often missing in prior works." | SUP | none | none | "often missing in prior works" | mixed RMSE↓/Acc↑ (via tab:neural-networks) |
| C03 | Abstract | 95 | "The second model is our simple adaptation of the Transformer architecture for tabular data, which outperforms other solutions on most tasks." | SUP | none ("most") | none | "most tasks"; **scope word is "other solutions", not "other DL solutions"** | mixed; strict verb "outperforms" |
| C04 | Abstract | 96 | "Both models are compared to many existing architectures on a diverse set of tasks under the same training and tuning protocols." | PROTO | none | none | "many", "diverse", "same" | n/a |
| C05 | Abstract | 97 | "We also compare the best DL models with Gradient Boosted Decision Trees and conclude that there is still no universally superior solution." | SUP/SCOPE | none | none | "universally" | ensembles, mixed |
| C06 | Intro | 120 | "First, we reveal that none of the considered DL models can consistently outperform the ResNet-like model." | SUP/SCOPE | none | none | "consistently" — operational meaning never defined in main text | mixed |
| C07 | Intro | 122 | "Second, FT-Transformer demonstrates the best performance on most tasks and becomes a new powerful solution for the field." | SUP | none | none | "best", "most tasks" (restate of C03 with explicit best-rank reading) | mixed |
| C08 | Intro | 123 | "it performs well on a wider range of tasks than the more ``conventional'' ResNet and other DL models." | SUP/SCOPE | none | none | "wider range", "more conventional" | mixed |
| C09 | Intro | 124 | "Finally, we compare the best DL models to GBDT and conclude that there is still no universally superior solution." | =C05 restate | none | none | "universally" | mixed |
| C10 | Intro contrib bullets | 128–131 | bullet 2 (129): "We demonstrate that a simple ResNet-like architecture is an effective baseline for tabular DL, which was overlooked by existing literature."; bullet 3 (130): "…FT-Transformer … it performs well on a wider range of tasks than other DL models."; bullet 4 (131): "We reveal that there is still no universally superior solution among GBDT and deep models." | SUP/SCOPE | none | none | "overlooked", "wider range", "universally" | mixed |
| C11 | Related work | 147 | "in our experiments, they do not consistently outperform ResNet." (about differentiable trees: DNDF/DNDT/NODE/TEL) | SUP/SCOPE | none | none (implicit tab:neural-networks) | "in our experiments", "consistently" | mixed |
| C12 | Related work | 151 | "we show that the properly tuned ResNet outperforms the existing attention-based models." | SUP | none | none | "properly tuned", "existing" | mixed |
| C13 | Related work | 152 | "the resulting architecture outperforms ResNet on most of the tasks." | SUP | none | none | "most of the tasks" | mixed |
| C14 | Related work | 157 | "In our experiments, however, we do not find such methods to be superior to properly tuned baselines." (multiplicative-interaction methods: latent-cross/DCN/DCN2) | SUP | none | none | "in our experiments", "properly tuned" | mixed |
| C15 | §4.2 Datasets | 294 | "We use a diverse set of eleven public datasets… For each dataset, there is exactly one train-validation-test split, so all algorithms use the same splits." | ENUM/PROTO | "eleven", "one" | `\autoref{tab:datasets}` | "public", "diverse" | n/a |
| C16 | §4.3 | 319 | "The best hyperparameters are the ones that perform best on the validation set, so the test set is never used for tuning." | PROTO | none | none | "never" | val metric |
| C17 | §4.3 | 323 | "We set the budget for Optuna-based tuning in terms of *iterations* and provide additional analysis on setting the budget in terms of *time* in supplementary." | PROTO | none | none (points to tab:S-tuning-time-budget) | "Optuna-based" (not all models) | n/a |
| C18 | §4.3 | 325 | "For each tuned configuration, we run 15 experiments with different random seeds and report the performance on the test set." | PROTO | "15" | none | "each tuned configuration" | mixed |
| C19 | §4.3 | 327 | "we obtain three ensembles by splitting the 15 single models into three disjoint groups of equal size and averaging predictions of single models within each group." | PROTO | "three", "15" | none | "for each model, on each dataset" | mixed |
| C20 | §4.4 | 355 | "ResNet turns out to be an effective baseline that none of the competitors can consistently outperform." | =C06 in results bullets | none | implicit tab:neural-networks (351) | "consistently" | mixed |
| C21 | §4.4 | 356 | "FT-Transformer performs best on most tasks and becomes a new powerful solution for the field." | =C07 | none | implicit tab:neural-networks | "most tasks" | mixed |
| C22 | §4.4 | 360–361 | "Among other models, NODE is the only one that demonstrates high performance on several tasks. However, it is still inferior to ResNet on six datasets (Helena, Jannis, Higgs, ALOI, Epsilon, Covertype), while being a more complex solution." | SUP/ENUM | "six" | none (context 351 tab:neural-networks) | "the only one", "several", "among other models" | mixed; RMSE↓ for CA/YE/YA/MI, Acc↑ rest |
| C23 | §4.4 | 364 | "The results indicate that FT-Transformer and ResNet benefit more from ensembling; in this regime, FT-Transformer outperforms NODE and the gap between ResNet and NODE is significantly reduced." | SUP | none | `\autoref{tab:node}` (363) | "in this regime" (=ensembles only); "significantly" here **not** tied to the Wilcoxon machinery (that is only defined in S-C, main.tex:547) | mixed |
| C24 | §4.5 | 404 | "autoref{tab:nn-gbdt} demonstrates that the ensemble of FT-Transformers mostly outperforms the ensembles of GBDT, which is not the case for only two datasets (California Housing, Adult)." (default block) | SUP/ENUM | "two" | `\autoref{tab:nn-gbdt}` | "mostly", "only" | mixed |
| C25 | §4.5 | 405 | "Interestingly, the ensemble of default FT-Transformers performs quite on par with the ensembles of tuned FT-Transformers." | SUP | none | implicit tab:nn-gbdt | "quite on par" | mixed |
| C26 | §4.5 | 409 | "Once hyperparameters are properly tuned, GBDTs start dominating on some datasets (California Housing, Adult, Yahoo; see autoref{tab:nn-gbdt}). In those cases, the gaps are significant enough to conclude that DL models do not universally outperform GBDT." | SUP/ENUM | none (3 named datasets) | `\autoref{tab:nn-gbdt}` | "properly tuned", "some", "significant enough" | mixed |
| C27 | §4.5 | 411 | "the fact that DL models outperform GBDT on most of the tasks does not mean that DL solutions are ``better'' in any sense." | SUP/SCOPE | none | implicit tab:nn-gbdt | "most of the tasks" + explicit anti-generalization hedge (411–412 "it only means that the constructed benchmark is slightly biased towards DL-friendly problems") | mixed |
| C28 | §4.5 | 413–414 | "Admittedly, GBDT remains an unsuitable solution to multiclass problems with a large number of classes. Depending on the number of classes, GBDT can demonstrate unsatisfactory performance (Helena) or even be untunable due to extremely slow training (ALOI)." | SUP/SCOPE | none | implicit tab:nn-gbdt | "with a large number of classes", "can" | Acc↑ for HE/AL |
| C29 | §4.6 | 424–425 | "FT-Transformer delivers most of its advantage over the ``conventional'' DL model in the form of ResNet exactly on those problems where GBDT is superior to ResNet (California Housing, Adult, Covertype, Yahoo, Microsoft) while performing on par with ResNet on the remaining problems. In other words, FT-Transformer provides competitive performance on all tasks, while GBDT and ResNet perform well only on some subsets of the tasks." | SUP/ENUM/SCOPE | none (5 named) | `\autoref{tab:nn-gbdt}` (423) | "most of its advantage", "exactly", "all tasks", "only some subsets" | mixed |
| C30 | §4.6 | 428 | "Note that the described phenomenon is not related to ensembling and is observed for single models too (see supplementary)." | SUP/SCOPE | none | supplementary (tab:S-single-models) | "for single models too" | mixed |
| C31 | §5.1 | 452 | "ResNet and FT-Transformer perform similarly well on the ResNet-friendly tasks and outperform CatBoost on those tasks. However, the ResNet's relative performance drops significantly when the target becomes more GBDT friendly. By contrast, FT-Transformer yields competitive performance across the whole range of tasks." | SUP/SCOPE | none | `\autoref{fig:synthetic}` | "similarly well", "significantly", "across the whole range" | RMSE↓ (caption 448 + axis label image_gbdt_vs_nn.tex:518) |
| C32 | §5.2 | 465 | "We tune and evaluate FT-Transformer without feature biases following the same protocol as in autoref{sec:implementation-details} and reuse the remaining numbers from autoref{tab:neural-networks}. The results averaged over 15 runs are reported in autoref{tab:ablation} and demonstrate both the superiority of the Transformer's backbone to that of AutoInt and the necessity of feature biases." | SUP/PROTO | "15" | `\autoref{sec:implementation-details}`, `\autoref{tab:neural-networks}`, `\autoref{tab:ablation}` | "superiority", "necessity" (strong); table covers only 8 of 11 datasets (header data/table_ablation.tex:3) — subset not justified in prose | mixed (arrows in table_ablation.tex:3) |
| C33 | §5.3 | 484 | "Interestingly, the proposed method yields reasonable feature importances and performs similarly to IG… Given that IG can be orders of magnitude slower and the ``baseline'' in the form of PT requires (n_features + 1) forward passes (versus one for the proposed method), we conclude that the simple averaging of attention maps can be a good choice in terms of cost-effectiveness." | SUP/QUAL | "(n_features + 1)", "one" | `\autoref{tab:feature-importances}` | "interestingly", "reasonable", "similarly", "orders of magnitude" | Rank correlation in [-1,1] (cap 489); **which direction is better is never stated in the source → UNKNOWN** (context implies higher=better); "orders of magnitude slower" has no measured runtime evidence anywhere in the source |
| C34 | S-A/S-D | 547, 599 | 547: "To measure statistical significance in the main text and in the tables in this section, we use the one-sided wilcoxon test with p = 0.01."; 599: "we have to make sure that longer tuning times of FT-Transformer (the number of tuning iterations is the same as for all other models) is not the reason of its strong performance." | PROTO/SCOPE | "p = 0.01" | tab:S-tuning-time-budget | parenthetical "same … as for all other models" | n/a |
| C35 | S-D | 604–606, 610–612 | 604: "for each algorithm, we run five independent (five random seeds) hyperparameter optimizations."; 606: "For each of the considered time budgets (15 minutes, 30 minutes, 1 hour, 2 hours, 3 hours, 4 hours, 5 hours, 6 hours)…"; 610: "FT-Transformer achieves good metrics just after several randomly sampled configurations (Optuna performs simple random sampling during the first 10 (default) iterations)."; 612: "extended tuning (in terms of iterations) for other algorithms does not lead to any meaningful improvements" | PROTO/NUM/SUP | "five", "15 minutes…6 hours", "10" | `\autoref{tab:S-tuning-time-budget}` (607) | "several", "meaningful" | CA/YE are RMSE↓; AD/HI Acc↑ — implied by nn tables, but tab:S-tuning-time-budget caption (617) and header (data/table_tuning_time_budget.tex:3, time-only) **never state per-dataset direction**; derivable only via the same datasets' arrows in tab:nn-gbdt |
| C36 | S-D | 584+590 | tab row: "Overhead & 2.6x & 0.9x & 1.5x & 3.5x & 2.8x & 3.1x & 1.3x & 2.3x & 1.3x & 13.8x & 2.3x"; prose 590: "The big difference on the Yahoo dataset is expected because of the large number of features (700)." | NUM | "13.8x", "(700)" | `\autoref{tab:S-training-times}` (589) | "expected", "large" | training seconds (lower better, 573) |
| C37 | S-E | 696–697 | "For Yahoo, we did not perform tuning at all, since the default configuration already performed well. In the main text, for FT-Transformer on Yahoo, we report the result of the default FT-Transformer." | PROTO | none | tab:S-transformer-space | "did not … at all" | RMSE↓ (YA) |
| C38 | S-G | 1057 | "FT-Transformer. We use the default hyperparameters. Parameter count: 930K." | NUM | "930K" | `\autoref{sec:S-architecture}` era context; comparable cell in tab:S-default-config | "default" | parameter count |
| C39 | S-H | 1111 | "Here, we report results for some datasets that turned out to be non-informative benchmarks, that is, where all models perform similarly. We report the average results over 15 random seeds for single models that are tuned and trained under the same protocol as described in the main text." | SCOPE/PROTO | "15" | `\autoref{tab:S-additional-datasets}`, `\autoref{tab:S-additional-results}` | "all models perform similarly" (defines the 4-dataset exclusion) | accuracy↑ (1121–1126) |

Restatement ladder for C03/C07/C21 (design-relevant, same claim across sections):
- Abstract 95: "outperforms **other solutions** on most tasks"
- Intro 122: "demonstrates the best performance on most tasks"
- Related 152: "outperforms **ResNet** on most of the tasks"
- Results bullet 356: "performs best on most tasks"
- Conclusion 499: "outperforms **other DL solutions** on most of the tasks"
The abstract's "other solutions" (no "DL") is a *dropped qualifier* relative to conclusion 499; on single models with GBDT included, FT-Transformer is the overall top only on JA, HI, EP, CO (4/11 red-bold in table_single_models_with_std:19), while CA and AD are topped by GBDT (lines 23–26) and YE by NODE (line 13). "Most tasks" survives only under the "DL solutions" reading.

---

## 3. Claim → cell mapping and numeric verification

Bold semantics differ by float — a mapping-time fact a manifest must carry:
- tab:neural-networks & tab:S-single-models: bold = "the gap … is not statistically significant" (main.tex:340, 554) — *statistical top set*.
- tab:node, tab:nn-gbdt, tab:S-ensembles: bold = "the highest accuracy or the lowest RMSE" (main.tex:372, 395 via 561) — *numeric best*, and "Due to the limited precision, some different values are represented with the same figures" (main.tex:373).
- tab:ablation: "Notation follows tab:neural-networks" (main.tex:468) — statistical top set.

| claim | evidence file : lines | status |
|---|---|---|
| C03/C07/C21 | data/table_neural_networks.tex:22 (FT-T row; bold at CA, AD, JA, HI, EP, CO = 6/11; rank "$1.8$") vs rows 6–20 | OBSERVED: 6/11 strict-numeric top among DL; AD is a printed tie with AutoInt (line 10 `$\mathbf{0.859}$` and line 22 `$\mathbf{0.859}$`). "Most" (6 > 5.5) holds numerically under table's own tie notation. |
| C06/C20 | table_neural_networks.tex rows 6–22 | OBSERVED: FT-T (a considered DL model) is numerically better than ResNet on 8/11 columns (rows 20 vs 22: CA 0.459<0.486, AD 0.859>0.854, HE 0.391<0.396 worse, JA 0.732>0.728, HI 0.729>0.727, AL 0.960<0.963 worse, EP 0.8982>0.8969, YE 8.855 worse (RMSE), CO 0.970>0.964, YA 0.756<0.757, MI 0.746<0.748) → tension with "none … can consistently outperform" unless "consistently" means "on all"; source never operationalizes it. |
| C11 | table_neural_networks.tex:6 (TabNet), :18 (NODE) vs :20 (ResNet) | OBSERVED: TabNet loses to ResNet 11/11; NODE beats ResNet on CA, AD, YE, YA, MI (5/11) → "they do not consistently outperform ResNet" is true for strict-all reading, but NODE does beat ResNet on 5 datasets. |
| C12 | table_neural_networks.tex:6, 10, 18, 20 | OBSERVED: ResNet (row 20) numerically above AutoInt (row 10) on 8/11 (AutoInt better on AD 0.859>0.854, HE 0.372<0.396 worse for AutoInt — recount: AutoInt better on AD and YE (8.882<8.846 false, ResNet better)… exact: ResNet > AutoInt on CA, HE, JA, HI, AL, EP, CO, YA, MI = 9/11; AutoInt > ResNet on AD, YE). Claim "outperforms the existing attention-based models" — TabNet loses 11/11 ✓; NODE-vs-ResNet covered by C22. Directionally supported. |
| C22 | table_neural_networks.tex:18 (NODE) vs :20 (ResNet) | OBSERVED / **exact match**: ResNet better on precisely HE (0.396>0.359), JA (0.728>0.727), HI (0.727>0.726), AL (0.963>0.918), EP (0.8969>0.8958), CO (0.964>0.958) = 6 datasets, and on none others (NODE better on CA 0.464<0.486, AD, YE 8.784<8.846, YA 0.753<0.757, MI 0.745<0.748). Enumeration "six datasets (Helena, Jannis, Higgs, ALOI, Epsilon, Covertype)" verifies 6/6. |
| C23 | data/table_node.tex:5 (NODE), :6 (ResNet), :7 (FT-T) | OBSERVED / **mismatch on 2 points**: (a) "FT-Transformer outperforms NODE": FT-T better on 9/11; on YE NODE ensemble is *bold numeric best* 8.716 vs FT-T 8.751 (node.tex:5, :7; RMSE↓); on AD both print `$0.860$` (tie at limited precision, caveat main.tex:373). (b) "gap between ResNet and NODE is significantly reduced": reduced on EP (0.0011→0.0006), CO (0.006→0.002); unchanged on HE (0.037→0.037), AL (0.045→0.045); **widened** on JA (0.001→0.004), HI (0.001→0.004). Claim supported only "on some datasets". |
| C24 | data/table_nn_gbdt.tex:7 (XGBoost d), :8 (CatBoost d), :9 (FT-T d) | OBSERVED / **exact match**: FT-T bold on 9/11 (HE 0.395, JA 0.734, HI 0.731, AL 0.966, EP 0.8969, YE 8.727, CO 0.973, YA 0.747, MI 0.742); not bold exactly on CA (CatBoost `$\mathbf{0.428}$` line 8) and AD (XGBoost `$\mathbf{0.874}$` line 7). "only two datasets (California Housing, Adult)" verifies 2/2. |
| C25 | table_nn_gbdt.tex:9 vs :16 | OBSERVED: default vs tuned FT-T rows: AD 0.860=0.860, HI 0.731=0.731, CO 0.973=0.973, YA 0.747=0.747; default better on YE (8.727<8.751) and MI (0.742<0.743); tuned better on CA (0.448<0.454), HE (0.398>0.395), JA (0.739>0.734), AL (0.967>0.966), EP (0.8984>0.8969). "quite on par" supported; cross-consistent with data/table_ensembles_with_std.tex:18–19 (FT-Td row YE 8.727 / MI 0.742; FT-T row YE 8.751 / MI 0.743) ✓. |
| C26 | table_nn_gbdt.tex:13 (XGB tuned), :14 (CB tuned), :15 (ResNet), :16 (FT-T) | OBSERVED / **enumeration gap**: under nn_gbdt's own *numeric-best* bold semantics, GBDT is bold on CA (CatBoost `$\mathbf{0.423}$`:14), AD (`$\mathbf{0.874}$`:14), YA (XGBoost `$\mathbf{0.732}$`:13) — matching the prose's three — but also on MI (CatBoost `$\mathbf{0.741}$`:14 vs FT-T 0.743, XGB 0.742). Prose omits Microsoft; defensible only via its own qualifier "gaps are significant enough" (main.tex:410), which the float itself does not encode (its bold = numeric best, see 1.4/§3 preamble). |
| C27 | table_nn_gbdt.tex:13–16 | OBSERVED: FT-T beats both GBDTs on HE, JA, HI, AL, EP, YE, CO = 7/11 (AL/…: GBDT tuned cells are `--` on AL, node: none). "DL models outperform GBDT on most of the tasks" → 7 > 5.5 ✓ under "beats XGB AND CB" reading; FT-T loses CA, AD, YA, MI. |
| C28 | table_nn_gbdt.tex:13, :14 (`--` in AL column), :14 (HE 0.388 vs FT-T 0.398) | OBSERVED: tuned-block AL cells are "--" for both GBDTs ✓ "untunable" (also default block :7, :8 have AL values 0.924/0.948 → the untunability is of the *tuned* regime). HE: CatBoost 0.388 < FT-T 0.398 ✓ "unsatisfactory". Class counts from data/table_datasets.tex:9: HE=100, AL=1000 ✓ "large number of classes". |
| C29 | table_nn_gbdt.tex:13–16 | OBSERVED / **exact match on the 5-set**: GBDT (XGB or CB) numerically > ResNet exactly on CA (0.431/0.423 vs 0.478), AD (0.872/0.874 vs 0.857), CO (0.969/0.968 vs 0.967), YA (0.732/0.740 vs 0.751), MI (0.742/0.741 vs 0.745) = 5/5, and not on the rest (ResNet ≥ both GBDTs on HE, JA, HI, EP, YE; AL no GBDT). "Exactly on those problems" verifies. FT-T beats ResNet on all 5 listed (0.448/0.860/0.973/0.747/0.743). Caveat: "most of its advantage" not quantifiable across mixed metrics; e.g. YE (a "remaining" dataset) shows FT-T−ResNet RMSE gain 0.019 comparable to CA's 0.030. "Performing on par with ResNet on the remaining problems" is contradicted *in the favorable direction* on JA (0.739 vs 0.734, FT-T clearly ahead) — the prose under-reports FT-T there, harmless to the thesis. |
| C30 | data/table_single_models_with_std.tex:14 (ResNet), :19 (FT-T), :24 (CatBoost), :26 (XGBoost) | OBSERVED (directional): GBDT>ResNet on single: CA (0.431/0.433 vs 0.486), AD (0.873/0.874 vs 0.854 — XGBd), CO (0.969 vs 0.964), YA (0.736 vs 0.757), MI (0.742 vs 0.748); FT-T better than ResNet on 4/5 of those (all but MI: 0.746 vs 0.748 ✓ also FT-T; CA ✓; AD 0.859 vs 0.854 ✓; CO ✓; YA 0.756 vs 0.757 ✓); but on "remaining" datasets FT-T *loses* to ResNet on HE (0.391<0.396), AL (0.960<0.963), YE (8.855>8.846) → "phenomenon … observed for single models too" directionally supported, not strict. |
| C32 | data/table_ablation.tex:5 (AutoInt), :6 (FT-T w/o biases), :7 (FT-T); + std version data/table_ablation_with_std.tex:5–7 | OBSERVED: FT-T > AutoInt 8/8 ✓ (0.459<0.474; 0.391>0.372; 0.732>0.721; 0.729>0.725; 0.960>0.945; 8.855<8.882; 0.970>0.964; 0.746<0.750). "Necessity of feature biases": FT-T > w/o-biases on 7/8, but on YE w/o-bias cell is `$\mathbf{8.843}$` (ablation:6) vs FT-T `$\mathbf{8.855}$` (line 7) — w/o-bias numerically better (RMSE↓), both bold (statistical tie per notation). Also all FT-T/AutoInt cells are byte-equal duplicates of tab:neural-networks rows 22/10 (per "reuse the remaining numbers", main.tex:465) ✓ (8/8 both rows). |
| C33 | data/table_feature_importance.tex:5 (AM), :6 (IG) | OBSERVED / tension with "performs similarly to IG": AM−IG = CA −0.03, HE +0.03, JA +0.03, HI +0.19, AL −0.05, YE +0.42, CO −0.06, MI +0.30. AM dominates IG on HI/YE/MI by multiples of the reported stds (e.g. YE 0.92(0.01) vs 0.50(0.03)). "Similarly" understates; no direction statement in this float (UNKNOWN). |
| C34 (iterations) | main.tex:718 (`\# Iterations & (A) 100, (B) 50`, FT-T; (B)={AL, YE, CO, MI} per caption 701) vs main.tex:762 (ResNet 100), 794 (MLP 100), 831 (XGB 100), 865 (CB 100), 896 (SNN 100), 942 (TabNet 100), 973 (GrowNet 100), 1009 (DCN2 100), 1040 (AutoInt (A) 100, (B) 50) | **MISMATCH (OBSERVED)**: main.tex:599's "the number of tuning iterations is the same as for all other models" is false for AL, YE, CO, MI where FT-Transformer used 50 iterations while other models used 100 (EP/YA not Optuna at all: 691–696). Within the time-budget experiment itself (datasets CA, AD, HI per main.tex:603, all in FT-T set (A)=100) the statement is locally true, but it is printed as a general parenthetical. |
| C35 | data/table_tuning_time_budget.tex:9–12 (CA block), :18–21 (AD), :27–30 (HI) | OBSERVED: 610 supported for FT-T CA (0.466 at 4 iterations vs best 0.457 at 124). 612 in tension for MLP on CA: 0.503 (16 it) → 0.488 (230 it) = 0.015 RMSE gain (line 10), while XGBoost CA is flat 0.437→0.432 (line 9) and AD XGBoost flat 0.871–0.873 (line 18). "any meaningful improvements" is true for GBDT/ResNet, questionable for MLP on CA; table itself has no direction marking (see C35 row of claim table). |
| C36 | main.tex:581–584 (tab:S-training-times inline) + data/table_datasets.tex:6 (Yahoo 699 num) + data/table_datasets_verbose.tex:15 (Yahoo # Num 699) | OBSERVED: "13.8x" verified: 12712/923 = 13.77 → 13.8 ✓ (all 11 overhead cells verified, e.g. 5050/4026=1.25→1.3 ✓, 536/363=1.48→1.5 ✓). **Mismatch**: prose "(700)" (590) vs table "699" (datasets:6; verbose:15) — rounding presented as a count. |
| C37 | data/table_single_models_with_std.tex:18 vs :19, YA column | OBSERVED / verified: FT-Transformer_d YA = `$0.756 \pm 8.2e\text{-}4$` and FT-Transformer YA = `$0.756 \pm 8.2e\text{-}4$` — *identical value and std*, exactly what "In the main text, for FT-Transformer on Yahoo, we report the result of the default FT-Transformer" (696–697) predicts; matching main.tex NN-table cell 0.756 (table_neural_networks.tex:22). |
| C38 | main.tex:1057 ("930K") vs main.tex:681 ("Parameter count & 929K & The value is given for 100 numerical features") | OBSERVED / precision drift: same regime (default hyperparameters; synthetic setup has exactly 100 features per main.tex:1049 "x ∈ N(0, I_100)") but two different rounded printings, 930K vs 929K. |
| C39 | main.tex:1139–1153 (tab:S-additional-results inline) | OBSERVED / tension: "all models perform similarly" is strained on Click: XgBoost 0.6399 (0.0006) (1152) vs all others 0.6606–0.6635 — a gap of ~0.02 ≈ 30× the per-cell stds; also FT-Transformer is best nowhere on these 4 datasets (best: Bank Grownet 0.9093 (1144); Kick XgBoost 0.9034 (1152); MiniBooNE ResNet 0.9508 (1148); Click CatBoost 0.6635 (1151)). These 4 datasets are excluded from the main claims — see H11. |
| C15 | data/table_datasets.tex:3 (11 columns CA…MI) + data/table_datasets_verbose.tex:6–16 (11 rows) | OBSERVED / match: "eleven" verifies 11/11 in both tables; names in prose (294) map 1:1 to abbreviations. Spelling drift: prose "Covertype" (294) vs table row "Covtype" (verbose:14); prose "MiniBooNe" (1125) vs table header "MiniBooNE" (1141); prose "GrowNet" (275)/"GrowNet" (table_neural_networks.tex:12) vs row "Grownet" (main.tex:1144); "XGBoost" vs "XgBoost" (1152); "DCN V2" (276) vs row "DCN2" (table_neural_networks.tex:16). |

**Claims verified numerically ≥6 — count: 15** (C03, C06, C11, C12, C22, C23, C24, C25, C26, C27, C28, C29, C30, C32, C33, C34, C35, C36, C37, C38, C39 cells compared; exact-match results: C22 6/6, C24 2/2, C29 5/5, C15 11/11, C36 overhead 11/11 + "(700)" mismatch, C37 exact, C25/C26/C28/C30/C32/C33/C34/C35/C38/C39 with the tensions noted).

Cross-artifact duplication fact: identical FT-T tuned ensemble numbers appear in **three floats** — table_node.tex:7 = table_nn_gbdt.tex:16 = table_ensembles_with_std.tex:19 (0.448, 0.860, 0.398, 0.739, 0.731, 0.967, 0.8984, 8.751, 0.973, 0.747, 0.743) ✓ all byte-consistent; ditto ResNet rows node:6 = nn_gbdt:15 = ensembles_std:14, and NODE rows node:5 = ensembles_std:13. A claim auditor must decide which float is canonical.

---

## 4. Divergence hypotheses — hunt results

| # | Hypothesis | Result |
|---|---|---|
| H1 | prose number differs from table cell | **REAL HIT**: main.tex:590 "(700)" features for Yahoo vs 699 in data/table_datasets.tex:6 and table_datasets_verbose.tex:15. |
| H2 | precision/rounding drift across sections | **REAL HIT**: 930K (main.tex:1057) vs 929K (main.tex:681) for the same default config at 100 features. Related-but-convention: abstract/body never print numbers for the "most tasks" claim; table prints 0.8977 (EP, 4 decimals, table_neural_networks.tex:6–22) where README prints 0.898 (§5). Overhead row consistent (§3 C36). |
| H3 | percentage vs percentage-point | **SEARCHED / NOT OBSERVED**. Method: grep main.tex for `%` (zero literal percent in prose), "percent", "relative", "improvement" (hits: 128, 288, 329, 452, 454, 595, 612 — none quantitative). The paper nowhere uses % deltas; all deltas are raw metric values, so this failure mode is absent from this artifact. |
| H4 | strict-superiority claim where cited table shows tie/worse | **REAL HITS**: (a) main.tex:364 "FT-Transformer outperforms NODE" (unqualified, ensembles regime) vs table_node.tex:5 NODE YE `$\mathbf{8.716}$` beating FT-T's 8.751 (line 7), and AD printed tie 0.860/0.860 (lines 5, 7). (b) main.tex:364 "the gap between ResNet and NODE is significantly reduced" vs widened gaps on JA (0.001→0.004) and HI (0.001→0.004), unchanged HE/AL (§3 C23). (c) main.tex:465 "necessity of feature biases" vs YE w/o-bias numerically better (table_ablation.tex:6 `$\mathbf{8.843}$` < :7 `$\mathbf{8.855}$`), only rescued by the statistical-tie notation. (d) main.tex:120/355 "none … consistently outperform ResNet" while FT-T wins 8/11 (§3 C06) — depends on undefined "consistently". |
| H5 | "all datasets"/"consistently" vs count that doesn't cover all | **REAL HITS**: (a) main.tex:424 lists 5 GBDT>ResNet datasets — verifies 5/5 — but the same sentence pair claims FT-T "on par with ResNet on the remaining problems" while FT-T strictly beats ResNet on JA 0.739 vs 0.734 and ties nowhere-marked (HE 0.398 vs 0.398 tie is fine, JA is a miss; §3 C29). (b) main.tex:409 enumerates 3 GBDT-dominated datasets vs 4 numeric bolds in table_nn_gbdt.tex:13–16 (MI omitted) — rescued only by the "significant gap" qualifier, which the table's numeric-best notation cannot express. (c) main.tex:1111 "all models perform similarly" vs Click XgBoost 0.6399 outlier (main.tex:1152). |
| H6 | qualifier dropped between abstract and body | **REAL HIT**: Abstract 95 "outperforms **other solutions**" vs Conclusion 499 "outperforms **other DL solutions**"; with GBDT in scope ("solutions"), FT-T is overall single-model top on only 4/11 (table_single_models_with_std.tex:19 red-bold: JA, HI, EP, CO; CA/AD topped by GBDT lines 23–26, YE by NODE line 13). Also 599 "same as all other models" drops the (A)/(B) iteration split (§3 C34). |
| H7 | wrong Table/Figure `\ref` | **SEARCHED / NOT OBSERVED**. Method: enumerated all 37 `\autoref` call sites (grep; listed at lines 181, 198, 217, 220, 236, 252, 294, 351, 363, 370, 388, 395, 404, 409, 423, 427, 435, 452, 454×2, 465×3, 468, 484, 549×2, 561×2, 589, 607, 662, 728, 1053, 1095, 1111×2) + 9 `\tuningparagraph` macro refs (lib.sty:27 → lines 694, 741, 775, 809, 846, 877, 922, 954, 988, 1021); every label resolves (tab:datasets 300, tab:neural-networks 346, tab:node 377, tab:nn-gbdt 396, tab:ablation 470, tab:feature-importances 490, tab:S-single-models 555, tab:S-ensembles 562, tab:S-training-times 574, tab:S-tuning-time-budget 618, tab:S-default-config 668, 10 space tables 702–1026, tab:S-ablation 1102, tab:S-additional-datasets 1117, tab:S-additional-results 1136, fig:arch 226, fig:blocks 233, fig:synthetic 449, sec:* 215/306/383/422/433/457/526/632) and each cited float's content plausibly supports the sentence (checked pairwise; e.g. 363→tab:node is the NODE-ensemble comparison the sentence needs). Residual fragility: 551–565 double caption in one float. |
| H8 | same claim worded differently across sections | **REAL (by design)**: the FT-T "best on most" ladder 95 / 122 / 152 / 356 / 499 with three different comparison sets ("other solutions" / "ResNet" / "other DL solutions") and the ResNet "no consistent outperformer" ladder 120 / 355 / (related-work variants 147 / 151). "No universally superior" appears at 97, 124, 131, and implicitly 417. |
| H9 | hand-transcribed vs generated tables | **OBSERVED**: only one file carries a generator stamp — data/image_gbdt_vs_nn.tex:1 "%% Creator: Matplotlib, PGF backend". All 11 data/table_*.tex are **hard-coded literal values** with no generation comments; tab:S-training-times, tab:S-default-config, all hyperparameter-space tables and tab:S-additional-* are hand-typed **inline** tabulars in main.tex (577–586, 671–686, 705–720, 749–764, 783–796, 817–833, 855–867, 885–898, 930–944, 963–975, 997–1011, 1121–1127, 1139–1153). No `\newcommand`-per-cell or external data pipeline exists in the artifact → every cell is transcription surface. |
| H10 | ambiguous cell identity | **REAL HITS**: (a) duplicate row labels inside one tabular: table_nn_gbdt.tex has "XGBoost" (7 and 13), "CatBoost" (8, 14), "FT-Transformer" (9, 16) — disambiguated only by `\multicolumn{12}{c}` block headers at 5 and 11. Same pattern in table_tuning_time_budget.tex (each model row ×3 blocks: XGBoost at 9, 18, 27). (b) `\textsubscript{d}` vs plain (single_models_with_std.tex:18/23/25) — "d=default" only in caption. (c) table_feature_importance.tex:3 header row starts with an empty `{}`-less first cell — columns are bare dataset abbreviations with no metric header (metric is in the float caption only). (d) case-variant labels across floats for the same entity (Covertype/Covtype, MiniBooNe/MiniBooNE, GrowNet/Grownet, XGBoost/XgBoost, DCN V2/DCN2, FT-Transformer/FT-T: prose 294 vs verbose:14 vs main.tex:1144 vs :1152 vs :276 vs table_neural_networks.tex:22). |
| H11 | excluded datasets silently generalized | **REAL HIT (disclosed but scope-relevant)**: S-H (1110–1156) reports 4 additional datasets excluded from the 11-dataset benchmark "where all models perform similarly" (1111); FT-Transformer is best on **none** of them (Bank best Grownet 0.9093 1144; Kick best XgBoost 0.9034 1152; MiniBooNE best ResNet 0.9508 1148; Click best CatBoost 0.6635 1151). The abstract's "most tasks" (95) counts only the retained 11; nothing in the abstract or intro signals the exclusion exists. Main tables' dataset count verifies 11 (table_datasets.tex:3, verbose 11 rows) vs prose "eleven" (294) ✓ — no count mismatch, only generalization-scope. |
| H12 | claim number appearing nowhere in source | **REAL HIT**: "IG can be orders of magnitude slower" (main.tex:484) — no runtime, complexity constant or table for IG/PT exists anywhere in main.tex or data/*. (The only timing artifact is tab:S-training-times 571–587, ResNet vs FT-T only.) Also unverifiable-as-number: "most of its advantage" (424) — a ratio never computable from the source. |

---

## 5. Paper ↔ README cross-artifact trace

Object under audit: `F:\MLResearch\result-doctor\phase4\rtdl-revisiting-models\README.md` (official repo README; pilot audited its lines 80 and 82).

Linking statements (bidirectional):
- README.md:10–11 "This is the official implementation of the paper \"Revisiting Deep Learning Models for Tabular Data\"."; README.md:6 arXiv:2106.11959 badge.
- Paper → repo: main.tex:98 `\url{\repository}` and footnote main.tex:501; `\repository` = `github.com/yandex-research/tabular-dl-revisiting-models` (lib.sty:23).

The README block under scrutiny — README.md:76 is the assertion, :78–92 the data:
```
:76  *The output exactly matches Table 2 from the paper:*
:80  adult                 0.852
:81  aloi                  0.954
:82  california_housing   -0.499
:83  covtype               0.962
:84  epsilon               0.898
:85  helena                0.383
:86  higgs_small           0.723
:87  jannis                0.719
:88  microsoft            -0.747
:89  yahoo               -0.757
:90  year                 -8.853
```
Provenance in README: code at :64–67 loads `output/*/mlp/tuned/*/stats.json` (tuned **MLP**, **single models**, averaged over seeds), rounded to 3 (`.round(3)` at :73).

Corresponding paper row: MLP in tab:neural-networks, data/table_neural_networks.tex:14:
`MLP & $0.499$ & $0.852$ & $0.383$ & $0.719$ & $0.723$ & $0.954$ & $0.8977$ & $8.853$ & $0.962$ & $0.757$ & $0.747$` (columns per line 3: CA AD HE JA HI AL EP YE CO YA MI).

Line-by-line comparison (README value vs paper cell):

| dataset | README (line) | paper cell (table_neural_networks.tex:14 col) | verdict |
|---|---|---|---|
| adult | 0.852 (:80) | $0.852$ (AD) | EQUAL |
| aloi | 0.954 (:81) | $0.954$ (AL) | EQUAL |
| california_housing | -0.499 (:82) | $0.499$ (CA, RMSE↓) | ABS EQUAL, SIGN FLIPPED |
| covtype | 0.962 (:83) | $0.962$ (CO) | EQUAL |
| epsilon | 0.898 (:84) | $0.8977$ (EP) | EQUAL only after README's 3-decimal rounding; paper prints 4 decimals — values are NOT literally "exact" |
| helena | 0.383 (:85) | $0.383$ (HE) | EQUAL |
| higgs_small | 0.723 (:86) | $0.723$ (HI) | EQUAL |
| jannis | 0.719 (:87) | $0.719$ (JA) | EQUAL |
| microsoft | -0.747 (:88) | $0.747$ (MI, RMSE↓) | ABS EQUAL, SIGN FLIPPED |
| yahoo | -0.757 (:89) | $0.757$ (YA, RMSE↓) | ABS EQUAL, SIGN FLIPPED |
| year | -8.853 (:90) | $8.853$ (YE, RMSE↓) | ABS EQUAL, SIGN FLIPPED |

Same metric? Yes — test-set score of tuned single MLP averaged over 15 seeds (paper caption main.tex:338; README path `mlp/tuned` :66). Same rounding? No for epsilon (0.898 vs 0.8977). Same dataset subset? Yes — all 11, none dropped. Sign convention: README negates the 4 RMSE datasets (Optuna maximize convention — inferable from context, never stated in either artifact; paper states no sign convention anywhere → the sign rule is an unstated contract).

Verifying README.md:76 "exactly matches Table 2":
- "Table 2" must resolve via compiled float order: Table 1 = tab:datasets (main.tex:296), Table 2 = tab:neural-networks (335), Table 3 = tab:node (367), Table 4 = tab:nn-gbdt (390), Table 5 = tab:ablation (467), Table 6 = tab:feature-importances (486). Under that inferred numbering, "Table 2" = tab:neural-networks ✓, but the tex source never writes the string "Table 2" — the linkage is a numbering convention, not a resolvable `\ref`.
- Verdict: **partially verified / "exactly" refuted in the strictest sense**: 6/11 values equal at printed precision; 4/11 equal only in absolute value (sign differs); 1/11 (epsilon) equal only after rounding 0.8977→0.898. The README's own code (`.round(3)`, :73) discloses the rounding step for all rows; the sign flip is undisclosed in both artifacts.
- Evidence grade this statement can be held at: "author-asserted cross-artifact identity, conditionally verifiable" — a Paper Doctor manifest could verify it only if it also carries (i) compiled float numbering, (ii) an explicit negation rule for RMSE-type metrics, and (iii) a rounding-tolerance rule (≤0.0005 absolute, or "3-decimal equality"). Under those three conventions the claim holds 11/11; without them it holds 6/11.

Also-checked README claims vs paper (secondary, one line each): :22–23 "MLP … performs on par with or even better than most of sophisticated architectures" ← paper's softer :354 "MLP is still a good sanity check" (rank 4.8, table_neural_networks.tex:14); :26 "prior work does not outperform them" ← C06/C20; :28–29 "best average performance among deep models" ← rank `$1.8$` (neural_networks.tex:22) ✓; :31 "FT-Transformer reduces (not completely) the gap between GBDT and DL" ← §4.6 (424–425); :198 "chances to get **exactly** the same results are rather low" — an honest reproducibility hedge that coexists with :76's "exactly matches" (internal README tension, note for the RD/PD overlap tribunal).

---

## 6. LaTeX determinism report

Quantification (mechanical counts, `grep -o '\$[^$]*\$'` per data file; inline main.tex tables counted by eye):
- Math-mode numeric cells: neural_networks 113 (99 values + 18 rank/std tokens, minus "--" gaps), nn_gbdt 75, node 33, single_models_with_std 148 (each = mean±std fused), ensembles_with_std 148, ablation 24, ablation_with_std 24, feature_importance 16, tuning_time_budget 96 (value+iterations fused per cell), datasets_verbose 55, datasets 0 (plain text numbers, e.g. ":6 20640").
- Inline main.tex numeric cells: training times 33 (577–586), additional datasets 20 (1121–1127), additional results 40 (1139–1153), default config ≈9 (671–686), 10 hyperparameter-space tables ≈ 10–14 numeric/enum cells each.
- Rows in result tables: nn 9 + node 3 + nn_gbdt 7 (+2 block headers) + single 13 (+3 headers) + ensembles 13 (+3) + ablation 3 + ablation_std 3 + feature 2 + tuning 12 (+3 headers) + additional 10.
- Columns: 11 datasets + rank (nn), 11 (others), 8 (ablation/feature-importance/tuning blocks ×8 time budgets), 4 (additional).
- Prose numeric tokens in main.tex: 456 (regex `[0-9]+(\.[0-9]+)?` — includes protocol numbers, equation indices and URLs; the audit-relevant prose numbers are far fewer, e.g. 325 "15", 327 "three/15", 329 "16", 547 "0.01", 604 "five", 606 budget list, 610 "10", 718 "100/50", 590 "700", 1057 "930K", 584 "13.8x").

Uniqueness of (table label, row label, column header):
- **Easy, unique** (2 exemplars): (tab:neural-networks, "ResNet", "EP") → data/table_neural_networks.tex:20 single cell `$0.8969$`; (tab:node, "NODE", "YE") → data/table_node.tex:5 `$\mathbf{8.716}$`. One row-line per model, distinct labels, one block.
- **Not unique** (2 exemplars): (tab:nn-gbdt, "XGBoost", "CA") resolves to BOTH nn_gbdt:7 (0.462, default block) and :13 (0.431, tuned block) — block header nn_gbdt:5/:11 is the only discriminator, and it is a `\multicolumn{12}{c}` spanning row, not part of the row label. Similarly (tab:S-tuning-time-budget, "MLP", "1h") hits table_tuning_time_budget.tex:10 (CA, 0.493 (103)), :19 (AD, 0.858 (71)), :28 (HI, 0.723 (62)) — three cells, block headers at :6/:15/:23.
- A fourth locator hazard: main.tex:551–565 — two captions/labels/two `\input`s in **one** float environment, with identical row and column label sets in both files (e.g. "ResNet"×"CA" exists in tab:S-single-models (single_models_with_std:14, 0.486) and tab:S-ensembles (ensembles_with_std:14, 0.478) — label-correct, but any parser keying on the float container (not the caption) collides.
- `\input`-separation helps (one file = one tabular = clean `&`/`\\` grid) but hurts: float semantics (caption, block meaning, notation, arrow directions) live in main.tex while cells live in data/, so a locator needs the two-level join already built in §1.3; and cross-float duplicates (§3 last paragraph) mean one number is "in" up to three tables.
- Value+uncertainty encoding is inconsistent: fused `$0.459 \scriptscriptstyle\pm\scriptstyle 3.5e\text{-}3$` (std tables), split `$3.3$ $(1.8)$` (neural_networks rank column), fused-but-different-format `0.9076 (0.0016)` (inline additional results), and value-with-count `$\textbf{0.466 (4)}$` (tuning time budget). A deterministic cell parser needs 4 grammars.

---

## 7. Dataset / seed / budget enumeration

Main result tables (neural_networks, node, nn_gbdt, single/ensembles_with_std): exactly 11 datasets — CA, AD, HE, JA, HI, AL, EP, YE, CO, YA, MI (headers: table_neural_networks.tex:3, table_nn_gbdt.tex:3, table_node.tex:3, single/ensembles_with_std:3/3; verified in table_datasets.tex:3, 11 columns; table_datasets_verbose.tex:6–16, 11 rows). Matches prose "eleven public datasets" (main.tex:294). Ablation & feature-importance floats cover only 8 of them (table_ablation.tex:3: CA HE JA HI AL YE CO MI; table_feature_importance.tex:3 same set) without prose justification of the subset. Supplementary "additional" 4: Bank, Kick, MiniBooNe, Click (main.tex:1111, 1123–1126) — excluded from main claims.

Seeds/repeats (stated, none UNKNOWN except as noted):
- 15 random seeds per tuned config (main.tex:325; captions 338 "averaged over 15 random seeds", 1100 "over 15 runs", 1111 "over 15 random seeds", training times 573 "averaged over 15 runs", ablation 465 "averaged over 15 runs").
- Ensembles: 3 disjoint groups of 5 (main.tex:327; captions 370, 393 "averaged over three ensembles").
- Synthetic study: 5 seeds (caption main.tex:448; axis label image_gbdt_vs_nn.tex:518; split once, main.tex:437).
- Feature importances: 5 runs (caption main.tex:489).
- Tuning time-budget study: 5 random seeds per run (main.tex:604, 617).
- Statistical test: one-sided Wilcoxon p=0.01 (main.tex:547) — defines "top" in tab:neural-networks/tab:S-single-models bolds, but NOT used in tab:node/tab:nn_gbdt bolds (numeric-best semantics, 372/395). Per-experiment seeds for individual cells outside these captions: never restated → covered by 325 blanket protocol; **UNKNOWN**: exact GPU/CPU per experiment ("can be found in the source code", main.tex:521, outside this artifact).

Tuning budgets:
- Default: Optuna TPE, 100 iterations per model (tables: ResNet 762, MLP 794, XGBoost 831, CatBoost 865, SNN 896, TabNet 942, GrowNet 973, DCN2 1009); FT-Transformer 100 on (A)={CA,AD,HE,JA,HI} / 50 on (B)={AL,YE,CO,MI} (718); AutoInt same split (1040). Epsilon FT-T: iterate heuristic-scaled defaults instead of full tuning (691, 695); Yahoo FT-T: no tuning, default reported (696–697). NODE: grid from original paper + default (907); no tuning for HE/AL → defaults reported (909). GBDT fixed internals: XGBoost n-estimators 2000 / early-stopping 50 (805–806), CatBoost iterations 2000 / early-stopping 50 / od-pval 0.001 (841–843). Early stopping patience=16 epochs for NNs (329).
- Time-budget study: 8 budgets 0.25h→6h on CA, AD, HI with XGBoost/MLP/ResNet/FT-Transformer (602–606).
- Preprocessing scopes: quantile default, standardization for HE/AL, raw for EP, standardized targets for regression (311–315; 543).

---

## 8. Census summary

Claims catalogued: **35** (C01–C39 ids minus merges; abstract 5, intro narrative 4 + bullets 4, related work 4, experiments results 16 incl. protocol, analysis 3, supplementary scope/numeric 5+). Numeric verifications performed: 15 claim-level cell audits (exact matches at C15, C22, C24, C29, C36-overhead, C37, C25, C32-backbone; documented tensions/mismatches at C03/H6, C06, C23, C26, C28-note, C32-bias/YE, C33, C34, C35, C36-"700", C38, C39, README-epsilon/signs). Divergence hypotheses with real hits: H1, H2, H4, H5, H6, H8, H9(pattern), H10, H11, H12. Not observed after active search: H3 (no %/pp deltas anywhere), H7 (all 46 ref sites resolve correctly; only fragility is the 551–565 double-caption float). Paper↔README: 6/11 exact, 4/11 sign-flip-only, 1/11 rounding-drift; "exactly matches Table 2" verifiable only under three unstated conventions.
