# GMMVI Claim Census — Paper Doctor Phase 0 (Paper A)

SOURCE (pinned, read-only): `F:\MLResearch\paper-doctor\phase0\sources\2209.11533v2.tex\arxiv.tex` (1460 lines) + `math_commands.tex`.
Paper identity: arXiv:2209.11533v2, "A Unified Perspective on Natural Gradient Variational Inference with Gaussian Mixture Models" (TMLR 2023).
Method: full line-by-line read. No external knowledge used. All quotes verbatim from source. `UNKNOWN` used where the source does not determine the answer.
Author note: after `\end{document}` (L1458) there is a stray `\\` on L1459 — harmless to LaTeX, but a literal line-count artifact the auditor should not treat as content.

---

## 1. Structural map

### Sections / subsections (verbatim titles, with line)
- L112 `\begin{abstract}` … L123 `\end{abstract}`
- L126 `\section{Introduction}`
- L166 `\section{Two Derivations for the Same Updates}` (L167 `sec:derived_updates`)
  - L171 `\subsection{iBayesGMM: Independently Computing the Natural Gradient}` (L172 `sec:iBayes_decomposition`)
  - L177 `\subsection{VIPS: Independently Maximizing a Lower Bound}` (L178 `sec:vips_decomposition`)
  - L199 `\subsection{The Equivalence of Both Updates}` (L200 `sec:unifcation` — note typo in label)
  - Theorem block L203–212 (L204 `theorem`)
- L215 `\section{A Modular and General Framework}` (L216 `sec:generalizedFramework`)
  - L239 `\subsection{Sample Selection}`
  - L249 `\subsection{Natural Gradient Estimation}` (L250 `sec:NgEstimation`)
  - L315 `\subsection{Natural Gradient based Component Updates}` (L316 `sec:ngbasedupdaer`)
  - L335 `\subsection{Weight Update}`
  - L351 `\subsection{Weight and Component Stepsize Adaptation}`
  - L362 `\subsection{Component Adaptation}`
- L373 `\section{Experiments}` (L392 `sec:Experiments`)
  - L399 `\subsection{Experiment 1: Component Update Stability}`
  - L443 `\subsection{Experiment 2: Weight Update and Exploration}`
  - L468 `\subsection{Experiment 3: Evaluating the Promising Candidates}`
- L629 `\section{Conclusion}`
- L633 `\section*{Acknowledgements}`
- APPENDIX (after L650 `\appendix`, L651 `\onecolumn`):
  - L653 `\section{Limitations}` (L654)
  - L661 `\section{Potential for Negative Societal Impact}` (L662)
  - L667 `\section{Related Work}` (L668)
  - L676 `\section{Background Material}` (L677); L680 `\subsection{Natural Gradient Descent}`; L699 `\subsection{Fisher Information}`; L722 `\subsection{Exponential Family Distributions}`
  - L753 `\section{Proof of Theorem~\ref{theorem}}` (L754); Lemma block L778
  - L810 `\section{Equivalence of the Weight Updates}` (L811); L814, L850 subsections
  - L869 `\section{Comparisons with Reference Implementations}` (L870)
  - L922 `\section{Hyperparameters}` (L923)
  - L975 `\section{Notes On Our Implementations}` (L976)
  - L990 `\section{Test Problems}` (L991)
  - L1009 `\section{Full Table for Experiment 3}` (L1010)
  - L1378 `\section{Learning Curves}` (L1379)
  - L1436 `\section{Tips for the Practitioner}` (L1437); L1440 `\subsection{Exploitation vs. Exploration}`; L1448 `\subsection{Efficiency vs. Stability}`
- No `\paragraph{}` commands exist in the file (grep: 0 hits).

### Floats (verbatim captions truncated to 160 chars, line, LaTeX number)
Counter values follow `\begin{...}` source order (independent of `[t!]`/`[!ht]` page placement). `tab:exp3` also appears as a *commented-out* duplicate table L478–562 (`\label{tab:exp3}` L561 is inert).

- Algorithm 1 — `alg:highlevel_pseudocode` (L225) — caption "Natural Gradient GMM Variational Inference" (L224) — `\begin{algorithm}[h!]` L223
- Table 1 — `table:algorithmicChoices` (L389) — L374 `[t!]` — "We assign a unique letter to every option such that every combination of options can be specified with a 7-letter word (one letter per module)."
- Table 2 — `tab:exp1` (L416) — L400 — "We show optimistic estimates of the best performance (negated ELBO) that we can achieve with every option when optimizing a uniform GMM with a fixed number of components,…"
- Table 3 — `tab:exp1_eval` (L440) — L430 (`NiceTabular`) — "We evaluated the best hyperparameters for the most promising candidates of our experiments for Group 1 on $10$ different seeds with respect to ELBO and a secondary metric…"
- Table 4 — `tab:exp2` (L465) — L446 — "We show optimistic estimates of the best performance (negated ELBO) that we can achieve with every option (updating the components using the design choices identified in…"
- Table 5 — `tab:exp3` (L626) — L565 `[!t]` (`NiceTabular`) — "Along with the negated ELBO, we show the $3\sigma$ confidence intervals based on the standard error of its mean using ten different seeds. The proposed candidate clearly…"
- Table 6 — `tab:vips_comparisons` (L892) — L873 — "We compare the final (negated) ELBO achieved by both implementations. When using the same design choices as VIPS~\citep{Arenz2020}, our implementation and hyperparameters led…"
- Table 7 — `tab:hyperparameters` (L972) — L927 (`NiceTabular`) — "The table lists each hyperparameter that was tuned at any of the experiments."
- Table 8 — `tab:exp3_full` (L1273) — L1014 `[!ht]` — "The full table for our main experiment shows all tested candidates, as well as the secondary metrics."
- Table 9 — `tab:exp3_accuracy` (L1375) — L1276 `[!ht]` — "We reran the experiments on the logistic regression tasks where we also evaluated to accuracy of the Bayesian inference predictions (based on 2000 samples from the learned…"
- Figure 1 — `fig:stm20_marginals` (L904) — L899 — "A representative plot of the 20 marginal distributions of the GMM learned with {\sc Samtron} for the \textit{STM20} experiment is shown in red…"
- Figure 2 — parent `\begin{figure}` L907; subfigures `fig:MatComparisons_stm20` = Fig.2a (L911/L912), `fig:MatComparisons_stm300` = Fig.2b (L916/L917) — parent caption "The learning curves plot the ELBO (in logarithmic scale) over the number of samples for our implementation and the reference implementation, where both use the {\sc Sepyfux}…"
- Figure 3 — `fig:learningCurves` (L1433) — L1382, 12 `subfigure`s (L1384–1431), each `\includegraphics{plots/*.pdf}` — "The learning curves for our main experiment (Experiment 3) show the negated ELBO over time (in seconds). Shaded areas show best and worst performance…"
- Figure note: all figure content is `plots/*.pdf` — **not machine-locatable numerically** from this source.

---

## 2. Claim census (35 substantive empirical claims)

Legend for "evidence": Table N = LaTeX number from §1. Cells cited by their own line numbers.

**C01 — Abstract — L114 — comparative + scope**
> "By updating the individual components using samples from the mixture model, iBayes-GMM often fails to produce meaningful updates to low-weight components, and by using a zero-order method for estimating the natural gradient, VIPS scales badly to higher-dimensional problems."
Numbers: none. Refs: none (method names inline). Qualifiers: "iBayes-GMM", "VIPS", "low-weight components", "higher-dimensional", "often", "badly". Evidence: QUALITATIVE, cross-refers body L354/L251 and Tables 2/5 (MORE N/A on Wine L404; Zamtrux N/A on STM300 L620).

**C02 — Abstract — L115 — comparative + scope**
> "we show that information-geometric trust-regions (used by VIPS) are effective even when using first-order natural gradient estimates, and often outperform the improved Bayesian learning rule (iBLR) update used by iBayes-GMM."
Numbers: none. Qualifiers: "VIPS", "even when using first-order…", "often", "iBLR", "iBayes-GMM". Evidence: Table 5 `tab:exp3` Samtron(T) vs Samyron(Y); Table 8 `tab:exp3_full`.

**C03 — Abstract — L116 — comparative (strong, no test) + number + universal**
> "We systematically evaluate the effects of design choices and show that a hybrid approach significantly outperforms both prior works."
Numbers: none printed. Refs: none. Qualifiers: "both prior works" (VIPS, iBayes-GMM), "significantly", "systematically". Evidence: Table 5 `tab:exp3` (Samtron rows L572–584 vs Sepyfux L598–609, Zamtrux L611–622). See Divergence D-03 ("significantly" with a tie present).

**C04 — Abstract — L116 — number + universal**
> "…which supports $432$ different combinations of design choices, facilitates the reproduction of all our experiments, and may prove valuable for the practitioner."
Numbers verbatim: `432` (`$432$`). Refs: none here (the derivation is L393; the option table is Table 1). Qualifiers: "all our experiments". Evidence: Table 1 `table:algorithmicChoices` option counts (L379–385) and the arithmetic `$2^4 \cdot 3^3 = 432$` at L393.

**C05 — Introduction/contributions — L152 — comparative**
> "We propose a novel combination of design choices and show that it significantly outperforms both prior methods."
Numbers: none. Refs: `Section~\ref{sec:Experiments}`. Qualifiers: "both prior methods", "significantly". Evidence: Table 5 `tab:exp3` (same as C03).

**C06 — Introduction/contributions — L153 — comparative + qualifier present**
> "Our implementation allows each design choice to be set independently and outperforms the reference implementations of iBayes-GMM and VIPS when using their respective design choices."
Numbers: none. Refs: `\link{\gmmvilink}`. Qualifiers: "when using their respective design choices" (CONDITIONAL — survives into body L393, L630, L871). Evidence: Table 6 `tab:vips_comparisons`; Fig 2.

**C07 — Experiments (intro para) — L393 — universal**
> "when comparing our implementation with the reference implementation on their target distributions, we always learn similar or better approximations."
Numbers: none. Refs: `Appendix~\ref{app:comparison_of_implementations}`. Qualifiers: "always", "their target distributions". Evidence: Table 6 `tab:vips_comparisons` (L878–889) enumerates 4 VIPS targets; STM targets only via Fig 2 (no numbers). See Divergence D-07 (scope partly figure-backed → not fully enumerable).

**C08 — Experiments (intro para) — L393 — number (combinatorics)**
> "Our framework allows for $2^4 \cdot 3^3 = 432$ different combinations of options."
Numbers verbatim: `2^4`, `3^3`, `432`. Refs: `Table~\ref{table:algorithmicChoices}`. Evidence: Table 1 L379–385 (option multiplicities 2,2,2,3,3,2,3 = four 2s and three 3s). Arithmetic verified consistent: 16·27=432.

**C09 — Experiment 1 — L419 — number**
> "We evaluate the different options for the \emph{NgEstimator}, \emph{ComponentStepsizeAdaptation} and \emph{NgBasedComponentUpdater} resulting in 18 different combinations."
Numbers verbatim: `18`. Refs: none (Table 2 follows). Evidence: Table 2 `tab:exp1` rows (2 estimator + 3 updater + 3 stepsize = 8 rows, L404–413) = 2·3·3=18. Consistent.

**C10 — Experiment 1 — L421/L422 — dataset + numbers**
> "In the \emph{BreastCancer} experiment~\citet{Arenz2018} we perform Bayesian logistic regression using the full ``Breast Cancer'' datatset~\citep{UCI}." (L421); "we use a batch size of $128$. We use two hidden layer with width $8$, such that the $177$-dimensional posterior distribution is still amenable to GMMs…" (L422)
Numbers verbatim: `64` (minibatch L421), `128`, `8`, `177`. Refs: `Appendix~\ref{sec:app:experiments}`. Qualifiers: dataset names, "minibatches of size 64". Note `177` reappears L997 (consistent).

**C11 — Experiment 1 — L424 — comparative + number (unverifiable ratio)**
> "On \emph{Wine}, which uses almost three times as many parameters as have been tested by \citet{Arenz2020}, we could not obtain reasonable performance when using MORE, as this zero-order method requires significantly more samples, resulting in very slow optimization."
Numbers verbatim: `three times`, `18` (candidates), `96` (cores). Refs: `Table~\ref{tab:exp1}`. Qualifiers: "Wine", "MORE", "Arenz2020". Evidence: Table 2 `tab:exp1` MORE/Wine cell = `N/A` (L404). **See Divergence D-09:** "three times" rests on Arenz2020's parameter count, which appears nowhere in this source.

**C12 — Experiment 1 — L426 — comparative + number + WRONG table ref**
> "We expect that using slightly more conservative hyperparameters, {\sc Sepyrux} could reliably achieve a performance that is only slightly worse than the optimistic value provided in Table~\ref{tab:exp1_eval} for \emph{BreastCancer} ($78.69$). However,  the performance of {\sc Septrux} is even in expectation over multiple seeds already better than this optimistic estimate."
Numbers verbatim: `78.69` (`$78.69$`). Refs: `Table~\ref{tab:exp1_eval}`. Qualifiers: "Sepyrux", "Septrux", "BreastCancer", "ten seeds". **See Divergence D-01: 78.69 is NOT in Table 3 (`tab:exp1_eval`); it is the iBLR(Y) optimistic cell of Table 2 (`tab:exp1`, L408).** "Septrux even in expectation better": Table 3 Septrux = `78.53` (L437) < 78.69 ✓ (direction correct: -ELBO lower=better).

**C13 — Experiment 1 — L426 — comparative + qualifier present**
> "Furthermore, also on \emph{WINE}, where {\sc Sepyrux} did not suffer from instabilities, the trust-region updates achieved better performance, albeit not statistically significant."
Numbers: none in this clause. Refs: Table 3 (`tab:exp1_eval`). Qualifiers: "WINE", "albeit not statistically significant". Evidence: Table 3 Wine -ELBO SEPTRUX `1444.01±30.78` (L437) vs SEPYRUX `1462.91±35.70` (L436). Faithful (direction + non-significance both consistent).

**C14 — Experiment 1 — L426 — number (CI convention)**
> "The mean of the final performance and its $99.7\%$ standard error are shown in Table \ref{tab:exp1_eval}."
Numbers verbatim: `99.7\%`, `ten seeds`. Refs: `Table \ref{tab:exp1_eval}`. NOTE: only "%" in the paper (grep). Also note it calls it "standard error" but the ± in Table 3/5 are described as `3\sigma` intervals (Table 5 caption L625) → **terminology inconsistency D-10**.

**C15 — Experiment 1 — Table 3 caption L439 — universal + comparative**
> "{\sc{Septrux}} which uses trust-region updates for the components outperformed {\sc{Sepyrux}} in all experiments, although in \textit{WINE} the advantage is not statistically significant."
Numbers verbatim: `10` seeds. Refs: within caption. Qualifiers: "all experiments" (enumerable = 3 datasets in Table 3), "WINE" exception. Evidence: Table 3 -ELBO BreastCancer 78.53<1042.28 ✓; BreastCancerMB 81.21<1130.81 ✓; Wine 1444.01<1462.91 ✓. Faithful: all three hold, exception stated.

**C16 — Experiment 2 — L444 — comparative + selection**
> "Based on our experiments sampling according to the mixture weights (Option \textbf{P}) seems to be clearly inferior to sampling from the components (Option \textbf{M}), as it was the only option that was not able to solve the \textit{GMM20} experiment."
Numbers verbatim: `24` (candidates, earlier in same paragraph). Refs: `Table~\ref{tab:exp2}`. Qualifiers: "GMM20", "only option", "seems". Evidence: Table 4 `tab:exp2` From Mixture (P)/GMM20 = `0.11` (L454); every other GMM20 best cell = `0.00` (L451,452,455,457,458,460–462). "Only nonzero on GMM20" holds. Faithful (hedged "seems").

**C17 — Experiment 2 — L444 — comparative**
> "Furthermore, adapting the number of components (Option \textbf{A}) and using trust-region updates for the weight update (Option \textbf{O}) seem beneficial for multimodal target distributions."
Numbers: none. Refs: Table 4. Qualifiers: "A", "O", "seem", "multimodal". Evidence: Table 4 Adaptive(A) STM20 `0.05`<Non-Adaptive(E) `0.08` (L451/452), Planar `12.15`<`12.33`; Weight TR(O) STM20 `0.05`<U `0.06` (L457/458). Faithful.

**C18 — Experiment 2 — L444 — universal**
> "All test problems for these experiments were taken from prior work."
Numbers: none. Refs: none. Qualifiers: "All", "these experiments" (= exp2: GMM20, PlanarRobot4, STM20, cited Arenz2020/Lin2020 same line). Faithful for exp2 set; broader "all test problems" would fail (TALOS is new, L472) — but the sentence is scoped to "these experiments".

**C19 — Experiment 3 — L475 — selection ("best-performing")**
> "Table~\ref{tab:exp3} compares the final performance (negated ELBO) of the best-performing candidate ({\sc Samtron}) with the prior methods VIPS~\citep{Arenz2020} and iBayes-GMM~\citep{Lin2020}."
Numbers: none. Refs: `Table~\ref{tab:exp3}`. Qualifiers: "best-performing", "Samtron". **See Divergence D-04: in Table 8 `tab:exp3_full` Samtron is NOT the row-best on GMM100 (-ELBO `0.01` L1161 unbold vs Samtrux/Samtrox `0.00` L1159/1160) and on WINE bolding is not exclusive to Samtron (L1228–1233).**

**C20 — Experiment 3 — L475 — comparative**
> "According to these experiments, we can clearly improve upon {\sc Zamtrux} by using Stein's Lemma for estimating the natural gradient (in particular for higher-dimensional problems), and upon {\sc Sepifux}, by sampling from the components and adapting their number during optimization."
Numbers: none. Refs: Table 5. Qualifiers: "clearly", "Zamtrux", "higher-dimensional", "Sepifux" (typo for Sepyfux — **D-11**), "components", "adapting their number". Evidence: Table 5 Samtron vs Zamtrux on high-dim STM300 `14.96`(L581) vs `N/A`(L620), Wine `1423.12`(L582) vs `16503.38`(L621); Samtron vs Sepyfux Planar `11.47` vs `17.26`. Faithful except GermanCredit ties (see C23).

**C21 — Experiment 3 — L475 — scope ("consistent") + comparative**
> "Interestingly, trust-region constraints seem to be beneficial also when using first-order estimates of the natural gradient, and showed a slight but consistent advantage compared to the iBLR update~\citep{Lin2020} in our experiments."
Numbers: none. Refs: Table 5. Qualifiers: "slight but consistent", "iBLR", "in our experiments". **See Divergence D-02: "consistent" advantage vs Samtron(TR)/Samyron(iBLR) TIES — GermanCreditMB both `585.12±0.00` (L576, L589) and GMM20 both `0.00/-0.00` (L578, L591).**

**C22 — Experiment 3 — Table 5 caption L625 — comparative (strong)**
> "The proposed candidate clearly outperforms the prior methods {\sc VIPS}~\citep{Arenz2020} and {\sc iBayes-GMM}~\citep{Lin2020}."
Numbers: none. Qualifiers: "clearly", "both prior methods". **See Divergence D-03: on GermanCredit Samtron `585.10±0.00` (L575) and VIPS/Zamtrux `585.10±0.00` (L614) are both bold = tie; on GMM20 Samtron `-0.00` (L578) and Zamtrux `-0.00` (L617) both bold = tie.** "Clearly outperforms" overstated vs those ties.

**C23 — Experiment 3 — Table 5 caption L625 — comparative (hedged)**
> "First-order natural gradient estimates with trust-region constraints (\textbf{T}) seem preferable over the iBLR update (\textbf{Y})."
Numbers: none. Qualifiers: "seem preferable", "T", "Y". Evidence: Table 5 / Table 8. Hedged → mostly faithful.

**C24 — Experiment 3 — Table 5 caption L625 — selection / silent data processing**
> "We observed instabilities for {\sc Sepyfux} on \textit{PlanarRobot} and \textit{TALOS} and, thus, removed bad outliers when computing the reported values."
Numbers: none. Refs: Table 5. Qualifiers: "Sepyfux", "PlanarRobot", "TALOS", "removed bad outliers". Evidence: the reported Sepyfux Planar `17.26±2.13` (L603) and TALOS `-16.64±5.26` (L609) are post-trim. **Caveat D-08: this outlier-removal qualifier appears only in the caption; the body comparison claims (C20/C22, L475) invoke Sepyfux values without restating the trim.**

**C25 — Experiment 3 — L472 — dataset dimension (contradicts Appendix)**
> "\textit{GermanCredit}~\citep{Arenz2020} and \textit{GermanCreditMB} are similar to the \textit{BreastCancer} experiment, but use the $25$-dimensional \textit{GermanCredit} dataset~\citep{UCI}"
Numbers verbatim: `25` (as GermanCredit dim). Refs: none. **See Divergence D-05: L995 states GermanCredit dimension = `31` ("The dimensions are $25$ and $31$, respectively" → BreastCancer=25, GermanCredit=31). Direct internal contradiction on the dataset-scope qualifier.**

**C26 — Experiment 3 — L472 — number (TALOS dim)**
> "The target distribution is 34 dimensional (7 joint configurations for each leg, 6 joint angles for each arm and 6 additional parameters…"
Numbers verbatim: `34`, `7`, `6`, `6`. Refs: none. Evidence: TALOS results in Tables 5/8 (L583, L1250–1270). Arithmetic note: 7·2=14 (legs) + 6·2=12 (arms) + 6 (torso) = 32, not 34 → **the decomposition shown sums to 32, not the stated 34 (D-12).**

**C27 — Conclusion — L630 — comparative**
> "…by releasing our modular framework for natural gradient GMM-based variational inference, which is well-documented and easy to use and outperforms the reference implementations by~\citet{Arenz2020} and \citet{Lin2020} when using the respective design choices."
Numbers: none. Refs: none (citations). Qualifiers: "when using the respective design choices" (condition preserved from C06). Evidence: Table 6, Fig 2. Conclusion restates the conditional → NOT a dropped-qualifier case here.

**C28 — Conclusion — L630 — scope (theoretical)**
> "we showed that both algorithms only differ in design choices" and "we can derive approximate natural gradient descent algorithms also for mixtures of non-Gaussian components"
Numbers: none. Type: theoretical universal (not empirical evidence). Record as SCOPE claim with no table evidence; faithfulness rests on Theorem (L203), out of Paper-Doctor's empirical-evidence scope → mark theory.

**C29 — Comparisons appendix — L871 — universal-with-exception**
> "For all environments that have been tested in both works, the final ELBO performances published in this work are better than the results published in the original work, except for \textit{GermanCredit} were, we could not measure any difference between both implementations."
Numbers: none printed. Refs: `Table~\ref{tab:vips_comparisons}`, `Table~\ref{tab:exp3}`. Qualifiers: "all environments tested in both works", explicit "except GermanCredit". Evidence: Table 6 ours vs theirs — BreastCancer `78.14`(L885)<`78.20`(L879) ✓; GMM20 `-0.00`(L887)<`0.01`(L881) ✓; PlanarRobot4 `11.48`(L888)<`12.02`(L882) ✓; GermanCredit `585.10`=`585.10` (exception). Faithful; note GMM20 margin `0.01` is within noise ("better" is weak, not wrong).

**C30 — Comparisons appendix — L895 — comparative, FIGURE evidence + external ref**
> "Figure~\ref{fig:stm20_marginals}…demonstrates that even without pre-training, we can learn higher-quality approximations with our implementation \citep[cf.][Fig.3]{Lin2020}."
Numbers: none. Refs: `Figure~\ref{fig:stm20_marginals}` (Fig 1). Qualifiers: "without pre-training", "Samtron" (same para). **Evidence = a figure (no numeric cell in source) AND the comparison baseline is Lin2020 Fig.3 (external, absent from source) → D-06 / UNKNOWN.**

**C31 — Comparisons appendix — L897 — comparative, FIGURE evidence**
> "Our hyperparameters achieve better final ELBO even on the original implementation." and "using the same hyperparameters, the learning curves of both implementations do not differ significantly, but our implementation performed slightly better."
Numbers: none. Refs: `Figure~\ref{fig:MatComparisons_stm20}` (Fig 2a). Qualifiers: "STM20", "same hyperparameters", "slightly". Evidence = figure only → no cell.

**C32 — Comparisons appendix — L897 — comparative, FIGURE evidence**
> "The respective learning curves are shown in Figure~\ref{fig:MatComparisons_stm300} and very similar for both implementations."
Refs: Fig 2b. Evidence = figure only.

**C33 — Tips appendix — L1453 — comparative + number that appears nowhere**
> "Exploiting first-order information by using Stein's lemma for estimating the natural gradient (design choice \textbf{S}) is often around one order of magnitude more efficient than use the zero-order method MORE."
Numbers verbatim: `one order of magnitude` (verbal number). Refs: none. Qualifiers: "S", "MORE", "often". **Divergence D-13: "one order of magnitude" (efficiency/sample-count) is not backed by ANY numeric cell in the source — no efficiency table exists; only qualitative support L424.**

**C34 — Accuracy table caption — L1374 — comparative + number + wrong-setup claim**
> "These experiments use the same hyperparameters and seeds that were used for the experiments reported in Table~\ref{tab:exp3_full}. For these tasks, slightly better approximations of the posterior, did not result in significant differences in the prediction accuracy." (also "based on 2000 samples")
Numbers verbatim: `2000`. Refs: `Table~\ref{tab:exp3_full}`. **Divergence D-14: the -ELBO column of Table 9 (`tab:exp3_accuracy`, L1282–1372) differs from the SAME candidate/experiment -ELBO in Table 8 (`tab:exp3_full`, L1020–1270) despite the caption asserting identical hyperparameters+seeds. Examples: BreastCancer/Samtrux `78.00`(L1283) vs `78.01`(L1021); BreastCancer/Samtron `78.01±0.01`(L1285) vs `78.00±0.02`(L1023); BreastCancer/Sepyfux `79.68`(L1289) vs `79.78`(L1027); BreastCancerMB/Zamtrux `85.88±3.41`(L1314) vs `83.65±0.97`(L1052).**

**C35 — Limitations appendix — L657 — qualifier / secondary-metric caveat**
> "…please recall that the hyperparameter optimization was performed only with respect to the ELBO. …for each method, the performance with respect to the secondary metric could potentially be better, if the hyperparameters were chosen correspondingly."
Type: scope/qualifier claim constraining the MMD/MSE/accuracy columns of Tables 8/9. Refs: `Table~\ref{tab:exp3_full}`. No printed number. Important for faithful representation of the secondary-metric evidence.

### NOT_APPLICABLE population — purely rhetorical (recorded, excluded from evidence mapping)
- R1 L143: "Gaussian mixture models are a simple yet powerful choice for a model family since they can approximate arbitrary distributions…" (evaluative "simple yet powerful"; the "arbitrary" clause is a known-theory restatement, not a paper result).
- R2 L213: "This deep connection between both methods was previously not understood and has several implications." (rhetorical framing of the Theorem).
- R3 L150: "By connecting these two previously separated lines of research, we improve our theoretical understanding of GMM-based VI." ("improve theoretical understanding" = non-empirical).

---

## 3. Claim → evidence candidate mapping (this source only)

| ID | Evidence table/figure (LaTeX #) | specific cells (own line numbers) | determinability |
|----|--------------------------------|-----------------------------------|-----------------|
| C01 | Table 2 `tab:exp1`; Table 5 `tab:exp3` | L404 MORE/Wine `N/A`; L620 Zamtrux/STM300 `N/A` | QUALITATIVE — no single cell encodes "fails on low-weight components"; body mechanism L354/L244 |
| C02 | Table 5 `tab:exp3` | Samtron(T) rows L572–584 vs Samyron(Y) rows L585–596 | partial (comparison direction per cell) |
| C03/C05 | Table 5 `tab:exp3` | Samtron L572–584 vs Sepyfux L598–609 vs Zamtrux L611–622 | determinable per cell; ties at L575/614, L578/617 break "significantly" |
| C04/C08 | Table 1 `table:algorithmicChoices` | option counts L379–385; arithmetic L393 | fully determinable |
| C09 | Table 2 `tab:exp1` | rows L404–413 | fully determinable |
| C10 | (dataset spec, no table) | L421/422; repeated L995/997 | prose-only |
| C11 | Table 2 `tab:exp1` | L404 `N/A` | "three times" = UNKNOWN (Arenz2020 param count absent) |
| C12 | Table 3 `tab:exp1_eval` (cited) / Table 2 (actual) | 78.69 actually at L408 (Table 2, iBLR/Y, BreastCancer); Table 3 has NO 78.69 | **WRONG REF (D-01)** |
| C13 | Table 3 `tab:exp1_eval` | L436 (1462.91±35.70), L437 (1444.01±30.78) | determinable |
| C14 | Table 3 `tab:exp1_eval` | L436–437 all cells ± | determinable; terminology mismatch vs Table 5 "3σ" |
| C15 | Table 3 `tab:exp1_eval` | L436–437 (all 3 -ELBO pairs) | determinable |
| C16 | Table 4 `tab:exp2` | P/GMM20 `0.11` L454 vs all-zero L451–462 | determinable |
| C17 | Table 4 `tab:exp2` | A L452, E L451, O L458, U L457 | determinable |
| C18 | prose (dataset sourcing) | L444 names Arenz2020/Lin2020 | determinable for exp2 set |
| C19 | Table 8 `tab:exp3_full` | GMM100 L1159–1161; WINE bolding L1228–1233 | "best-performing" NOT the unique best → **D-04** |
| C20 | Table 5 `tab:exp3` | high-dim L581/620, L582/621; Sepyfux L603 | determinable; GermanCredit tie L575/614 |
| C21 | Table 5 `tab:exp3` | GermanCreditMB L576 vs L589 (`585.12` both); GMM20 L578 vs L591 (`0.00`) | **D-02 ties contradict "consistent"** |
| C22 | Table 5 `tab:exp3` | GermanCredit L575/L614 (both bold); GMM20 L578/L617 (both bold) | **D-03 "clearly outperforms" vs ties** |
| C23 | Table 5 / Table 8 | see C21 | hedged |
| C24 | Table 5 caption | Sepyfux L603 (Planar), L609 (TALOS) | trim disclosed in caption only |
| C25 | prose (dataset spec) | L472 (`25`) vs L995 (`31`) | **D-05 contradiction** |
| C26 | prose (TALOS spec) | L472 (`34 = 7+6+6`) | **D-12 sums to 32** |
| C27 | Table 6 `tab:vips_comparisons`; Fig 2 | ours-vs-theirs rows L878–889 | conditional preserved |
| C28 | Theorem (L203) | non-empirical | out of scope |
| C29 | Table 6 `tab:vips_comparisons` | L879–882 (theirs), L885–888 (ours) | determinable |
| C30 | Fig 1 `fig:stm20_marginals` | no cell (PDF) | **figure + external (D-06)** |
| C31 | Fig 2a `fig:MatComparisons_stm20` | no cell (PDF) | figure-only |
| C32 | Fig 2b `fig:MatComparisons_stm300` | no cell (PDF) | figure-only |
| C33 | (none) | no numeric efficiency cell exists | **D-13 number absent** |
| C34 | Table 9 vs Table 8 | L1283/1021; L1285/1023; L1289/1027; L1314/1052 | **D-14 -ELBO mismatch under identical-setup claim** |
| C35 | Table 8 / Table 9 secondary rows | MMD/MSE/ACCURACY rows L1031–1270, L1293–1371 | caveat claim, no single cell |

---

## 4. Divergence hypothesis hunt

**D-01 (prose cites wrong table) — REAL HIT.**
L426 text: "the optimistic value provided in Table~\ref{tab:exp1_eval} for \emph{BreastCancer} ($78.69$)". Conflict: `tab:exp1_eval` (Table 3, L430–441) contains no `78.69`; BreastCancer column there = `1042.28` (L436) and `78.53` (L437). The value `78.69` is the iBLR(Y)/BreastCancer optimistic cell of Table 2 `tab:exp1` at L408 (the SAME paragraph L426 even earlier calls the *optimistic* values "in Table~\ref{tab:exp1}"). Wrong cross-reference to Table 3.

**D-02 ("all/consistently" scope exceeding evidence / tie contradicts strict superiority) — REAL HIT.**
L475 "slight but consistent advantage compared to the iBLR update" vs Table 5 where Samtron(TR) and Samyron(iBLR) tie on GermanCreditMB (both `585.12±0.00`, L576 and L589) and on GMM20 (`-0.00` L578 vs `0.00` L591). "Consistent" over-claims a strict ordering across all experiments.

**D-03 (comparison direction overstated: tie present but "clearly/significantly outperforms") — REAL HIT.**
L116/L152 "significantly outperforms both prior works" and L625 caption "clearly outperforms the prior methods" vs Table 5 GermanCredit where Samtron `585.10±0.00` (L575, bold) equals VIPS/Zamtrux `585.10±0.00` (L614, bold) — a tie, and GMM20 both `-0.00` bold (L578, L617). No significance test is reported anywhere to license "significantly".

**D-04 ("best" selection claim not supported by the full evidence) — REAL HIT.**
L475 "the best-performing candidate ({\sc Samtron})" vs Table 8 `tab:exp3_full` where Samtron is not row-best on GMM100 -ELBO (`0.01` L1161, unbold, behind Samtrux `0.00` L1159 and Samtrox `0.00` L1160) and WINE -ELBO bolding is non-exclusive (L1228–1233 bold six Sam* cells while min `1423.12` L1230). "Best-performing" holds on some rows only.

**D-05 (dataset-scope number contradicted across sections) — REAL HIT.**
L472 "the $25$-dimensional GermanCredit dataset" vs L995 "The dimensions are $25$ and $31$, respectively." applied to "\textit{BreastCancer} and \textit{GermanCredit}" → GermanCredit = `31` there. Direct contradiction on GermanCredit dimensionality (25 vs 31).

**D-06 (prose referencing a figure that has no numeric cell / wrong-type evidence) — REAL HIT.**
L895/C30 and L897/C31,C32 lean on Fig 1/Fig 2 (`plots/*.pdf`) for "higher-quality approximations" and "better final ELBO"; no numeric evidence exists in-source (figures are opaque). C30 additionally compares against `\citep[cf.][Fig.3]{Lin2020}` — an external figure absent from the source → UNKNOWN.

**D-07 (qualifier present in body but scope "always" broader than enumerable set) — REAL HIT (partial).**
L393 "we always learn similar or better approximations" enumerates VIPS targets via Table 6 (4 rows, determinable), but the STM20/STM300 targets it also relies on are supported only by Fig 2 (no cells) → the "always" set is not fully enumerable from source → **UNKNOWN remainder**.

**D-08 (qualifier dropped between abstract and body) — NOT OBSERVED as a clean case; note found.**
The conditional "when using their respective design choices" is *preserved* in abstract L153, body L393, and conclusion L630 (so no drop). The opposite pattern IS present: the Sepyfux outlier-removal qualifier (Table 5 caption L625) is NOT carried into the prose superiority claims (L475, L116) that use those same trimmed values. Recorded as a body-vs-caption qualifier asymmetry rather than an abstract-vs-body drop.

**D-09 (claim rests on a number absent from source) — REAL HIT.**
L424 "almost three times as many parameters as have been tested by \citet{Arenz2020}": `177` is given (L422), but Arenz2020's parameter count appears nowhere → the `three times` ratio is unverifiable from source.

**D-10 (precision/terminology drift for error bars) — REAL HIT (minor).**
L426 calls the Table 3 ± values "$99.7\%$ standard error"; L625 (Table 5 caption) calls the same-style ± "the $3\sigma$ confidence intervals based on the standard error". Same numeric convention, inconsistent naming across sections.

**D-11 (transcription/typo in a method name used in a comparison) — REAL HIT (minor).**
L475 "upon {\sc Sepifux}" — the codeword used elsewhere is `Sepyfux` (L439, L598, L1018); "Sepifux" (and earlier variants `IBayesGMM`/`iBayes-GMM`, `Sepyfux`/`Sepifux`) is a name inconsistency in a sentence making a comparative claim.

**D-12 (arithmetic stated in prose does not sum) — REAL HIT (minor).**
L472 TALOS "34 dimensional (7 … each leg, 6 … each arm and 6 additional)": 7·2+6·2+6 = 32 ≠ 34 printed. Either the parenthetical decomposition or the 34 is wrong.

**D-13 (efficiency magnitude with no supporting cell) — REAL HIT.**
L1453 "around one order of magnitude more efficient" (Stein vs MORE). Grep: no table of runtimes/sample-counts exists; nearest support is qualitative L424. Number appears nowhere.

**D-14 (same result reported differently across tables under an identical-setup claim) — REAL HIT.**
Table 9 caption (L1374) asserts Table 9's runs "use the same hyperparameters and seeds that were used for the experiments reported in Table~\ref{tab:exp3_full}", yet the -ELBO values differ, e.g. BreastCancer/Samtron `78.01±0.01`(L1285) vs `78.00±0.02`(L1023); BreastCancer/Sepyfux `79.68`(L1289) vs `79.78`(L1027); BreastCancerMB/Zamtrux `85.88±3.41`(L1314) vs `83.65±0.97`(L1052).

**D-15 (printed table number differs from the source-of-truth table) — REAL HIT.**
Table 5 `tab:exp3` reports iBayes-GMM (Sepyfux)/STM300 = `26.87±0.45` (L607), but Table 8 `tab:exp3_full` reports Sepyfux/STM300 = `26.69±0.39` (L1211) while `26.87±0.45` is the **Sepyrux** value (L1212). The main table appears to have taken the neighbouring column's value (off-by-one-column transcription).

**Rounding/precision drift (6.53 vs 6.5 style) — SEARCHED / NOT OBSERVED as drift**, but two near-duplicate collisions exist: `1431.09` recurs as the best of three rows in Table 2 (L405 Stein, L408 iBLR, L413 Adaptive) — an *ambiguous reverse-lookup* value; and Table 2 "optimistic" Wine best `1431.09` (L405) is numerically beaten (lower) by Table 5 Samtron Wine `1423.12` (L582), so the "optimistic estimate" label (L424) is not an actual upper bound once the full pipeline (different hyperparameters) is used — flag as a comparison-scope caveat (comparability UNKNOWN, since exp1 fixes weights/components).

**Percentage vs percentage-point confusion — SEARCHED / NOT OBSERVED.** Grep for `\%` returns a single hit (L426 `99.7\%`); no "% improvement"/"gain"/"reduction" phrasing exists anywhere, so there is no %-vs-pp target to confuse. Strategy: `grep -n '\\%'` and `grep` for `percent`.

**Prose referencing the wrong table/figure — REAL HIT** = D-01 (L426 → Table 3 for a Table-2 value).

**Excluded dataset/run silently generalized — SEARCHED / PARTIAL.** STM300/VIPS is `N/A` (L620, L1213): prose C29/C07 "all environments tested in both works" and "always similar or better" *carve this out correctly* (they say "tested in both works"). No silent generalization of an N/A run observed. The closest is Sepyfux outlier removal (D-08) which is disclosed in the caption, not silent.

---

## 5. LaTeX determinism report

**Numeric location:** All result values are **inline in `arxiv.tex`**, hand-typed. The only `\input{}` is `math_commands.tex` (L10, pure notation macros). No results live in `\input` files.

**Macros carrying result values:** NONE. `math_commands.tex` defines only notation (0 numeric-result macros; grep `\newcommand` returns symbol defs only). Result cells use `siunitx` `\num{…}` inline (e.g. `\num{78.00}` L573). `\num{` occurs 708 times in the file total; ~311 of those lines are active (uncommented); the remainder sit in the commented-out draft `tab:exp3` (L478–562) and commented abstract/contributions (L118–163).

**Tables hand-typed?** Yes — 100%. No generator/CSV inclusion. This makes every cell a manual-transcription dependency; the two column-shift/mismatch bugs (D-15 Sepyfux STM300; D-14 Table 9 vs Table 8) are exactly the failure mode manual typing produces.

**Cell identity recoverability from (table label, row label, column header):** mostly YES for Tables 2/4/5/6/9, harder for the two `NiceTabular` mega-tables.
- Table 5 `tab:exp3`: rows = `\sc Samtron`(L572), `Samyron`(L585), `iBayes-GMM (\sc Sepyfux)`(L598), `VIPS (\sc Zamtrux)`(L611); columns = `\rotatebox` experiment headers (L569–570). A cell = (tab:exp3, Samtron row L572, header "BreastCancer" L569) → value `78.00±0.02` at L573. **Deterministic example.**
- Table 8 `tab:exp3_full`: identity requires the (Experiment, Metric) PAIR because each experiment spans two rows via `\Block{2-1}` (e.g. BreastCancer -ELBO at L1020, MMD at L1031), and candidate names live only in the rotated header (L1018). Two-level key needed.
- **Ambiguous locators:** (a) value-based reverse lookup — `1431.09` maps to 3 different rows in Table 2 (L405,408,413); `585.10`/`585.12` recur across many cells/tables. (b) Row label "BreastCancer" exists as a column in Tables 2,3,5,6,8,9 (L402,433,569,876,1020,1282) — a prose phrase "on BreastCancer" with no table ref (e.g. L426) is table-ambiguous. (c) In Table 5 the label `iBayes-GMM (Sepyfux)` (L598) vs Table 8 `Sepyfux` (L1018) vs Table 2 letter-codewords `Y/Z/S` — the SAME method has three different row identities across tables, so cross-table equality checks (D-14, D-15) need a codeword alias table.

**Quantification (from structure, deterministic where countable):**
- Table 2 `tab:exp1`: 8 data rows (L404–413) × 3 dataset cols; ~23 numbers + 1 `N/A`.
- Table 3 `tab:exp1_eval`: 2 rows (L436–437) × 6 sub-columns × (value±err) = ~24 numbers.
- Table 4 `tab:exp2`: 9 rows (L451–462) × 3 cols = 27 numbers.
- Table 5 `tab:exp3`: 4 candidate rows × 11 experiment cols × (value±err) = ~86 numbers (+1 `N/A`).
- Table 6 `tab:vips_comparisons`: 2 rows × 4 cols × 2 = 16 numbers.
- Table 7 `tab:hyperparameters`: 15 module/design-choice rows, **no numeric results** (symbolic only).
- Table 8 `tab:exp3_full`: 11 experiments × 2 metrics = 22 data rows × 9 candidates × 2 (val±err) ≈ ~392 numbers (+2 `N/A`) — dominates the numeric mass.
- Table 9 `tab:exp3_accuracy`: 4 experiments × 2 metrics = 8 data rows × 9 candidates × 2 ≈ ~144 numbers.
- Total numeric table cells: roughly **700+ printed numbers** across 8 result-bearing tables; **0** in Table 1/Table 7.
- Prose numbers (printed in narrative sentences, not in a float): approximately **35–45** (dataset dims 25/31/177/34/100/20/300; counts 432/18/24/10 seeds/96 cores/64/128/8/1000/569/2000; constants β=1, 0.2, 0.1, 0.01, 0.05, Σ_init=300; CI 99.7%; ranges [-50,50]/[-20,20]/[-25,25]; verbal numbers "three times"/"one order of magnitude"). Full list dominated by Appendix `Test Problems` (L994–1007) and Experiment setup (L419–426).

---

## 6. Claim population counts (over full source, active text only)

- Sentences containing ≥1 printed numeric value: **~38** (concentrated at L116, L393, L419–426, L444, L472, L995–1005; note the many numbers in `Test Problems` L994–1007 are dataset-specification, not results).
- Comparative claims (outperform / better / worse / inferior / improve / preferable / equivalent / "more efficient"): **~22** — includes C01,C02,C03,C05,C06,C11,C13,C15,C16,C17,C20,C21,C22,C23,C27,C29,C30,C31,C32,C33,C34 plus L147, L213 theory-adjacent.
- Universal-scope claims (all / every / any / always / consistently / in general / only / best): **~13** — L116 "all our experiments", L393 "always", L439 "all experiments", L444 "only option"/"All test problems", L472 "all", L475 "consistent", L630 "all", L655 "not competitive", L659 "consistent", L871 "all…except", L1443, L1452–1453 "always", plus C18,C21.
- Selection-flavored claims (best / chosen / selected / we report / removed outliers): **~7** — L475 "best-performing", L419/L424/L464 "best performance reported", L625 "removed bad outliers", L895 "which performed best", L1011 "all tested candidates", C24, C19.
- Claims whose evidence is a FIGURE rather than a table: **5** — C30 (Fig 1), C31 (Fig 2a), C32 (Fig 2b), plus the learning-curve efficiency/stability caveat L657 (Fig 3), and the abstract-vs-body "scales badly to higher-dimensional problems" whose only direct readout on STM300/WINE is partly Table + partly Fig 3. The STM comparison claims (C30–C32) have **no numeric cell at all** in-source.
- Claims resting on a number absent from source: **3** — C11/D-09 ("three times"), C33/D-13 ("one order of magnitude"), C30/D-06 (Lin2020 Fig.3 baseline).

---

## Appendix: key line-number index for the load-bearing conflicts
- L426 wrong-table ref (78.69 → tab:exp1_eval, actually tab:exp1 L408) = D-01
- L475 "consistent advantage" vs ties L576/589, L578/591 = D-02
- L116/L152/L625 "significantly/clearly outperforms both" vs GermanCredit tie L575/614 & GMM20 tie L578/617 = D-03
- L475 "best-performing Samtron" vs exp3_full GMM100 L1159–1161 = D-04
- L472 GermanCredit=25 vs L995 GermanCredit=31 = D-05
- L895 figure-only + external Fig.3 = D-06
- L393 "always" partly figure-backed (Fig 2) = D-07 (UNKNOWN remainder)
- L424 "three times" unverifiable = D-09
- L426 "99.7% standard error" vs L625 "3σ confidence intervals" = D-10
- L475 "Sepifux" typo = D-11
- L472 "34 = 7+6+6" sums to 32 = D-12
- L1453 "one order of magnitude" no cell = D-13
- L1374 identical-setup vs Table9/Table8 -ELBO diffs (L1285/1023, L1289/1027, L1314/1052) = D-14
- L607 Sepyfux STM300 26.87 vs L1211 26.69 (and L1212 Sepyrux 26.87) = D-15
