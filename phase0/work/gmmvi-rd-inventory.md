# GMMVI × Result Doctor 0.1.0 — 冻结证据清点（Paper Doctor Phase 0 · 只读盘点）

- 日期：2026-09-29。产出者：Paper Doctor 设计阶段证据清点，READ-ONLY。
- 目的：精确记录 Result Doctor（RD）v0.1.0 对 GMMVI（arXiv:2209.11533v2 / TMLR 2023，
  "A Unified Perspective on Natural Gradient Variational Inference with Gaussian Mixture
  Models"，Arenz / Zhang / Peters，OpenReview forum `tLBjsX4tjs`）已经**冻结了什么**，
  使 Paper Doctor（PD）设计不重复 RD、且知道 PD 必须自己补什么。
- 引用记法：`文件:行`；JSON 用 pointer；RD bundle 的运行时事实由本会话在
  `F:\MLResearch\result-doctor` 用 `PYTHONPATH="src;tests" python -X utf8` 实际加载
  `load_gmmvi_bundle(r"F:\MLResearch\experiment-doctor\phase0-gmmvi")` 并 `evaluate/audit_bundle`
  得到（只读计算，不落盘），标记 `(runtime)`；构造代码行号给出其来源。
- 冻结源文件：
  - RD Phase-0 设计报告：`F:\MLResearch\result-doctor\phase0\RESULT_DOCTOR_PHASE0_REPORT.md`（下称 RD-P0）
  - 冻结 loader：`F:\MLResearch\result-doctor\src\result_doctor\loaders\gmmvi.py`（下称 LDR）
  - 冻结验收：`F:\MLResearch\result-doctor\tests\test_gmmvi_acceptance.py`（下称 ACC）
  - schema/rules/bundle/audit：`F:\MLResearch\result-doctor\src\result_doctor\{schema,rules,bundle,audit,evidence,status,compute}.py`
  - ED 侧抄录：`F:\MLResearch\experiment-doctor\phase0-gmmvi\notes\paper_exp3_table_transcription.md`（NOTE-T）、
    `...\evidence\paper_reported_values.json`（JSON-PV）、
    `...\notes\declared_experiment_protocol.md`（NOTE-P）、
    `...\notes\seed_integrity_normal_family.md`（NOTE-S）
  - 发布冻结：`F:\MLResearch\result-doctor\release\RELEASE_FREEZE_0.1.0.md`："State: **RELEASED AND FROZEN.**
    `v0.1.0` is permanent"（RELEASE_FREEZE_0.1.0.md:6）。
- 第 7 项要求（现成 canonical audit JSON）：**不存在**。`find` 全库仅命中
  `/f/MLResearch/result-doctor/src/result_doctor/loaders/gmmvi.py` 与
  `/f/MLResearch/result-doctor/tests/test_gmmvi_acceptance.py`；result-doctor 下无 GMMVI 审计 JSON 快照
  （phase4/5 的 JSON 均属 rtdl/RTDL 项目）。RD-P0:396 规定"数字连同命令冻结、向量随同冻结"，
  向量的可执行载体即 ACC 断言（ACC:30-271）。本文件 §C 的向量是本会话重跑所得 (runtime)。

---

## A. Bundle 清点（由 LDR `load_gmmvi_bundle` LDR:751-760 构建）

### A.0 对象总量 (runtime)

| 类 | 数量 | 构造入口 |
|---|---|---|
| ReportedResult | **59** | LDR:479-489 `_cells` + LDR:729-748（VIPS） |
| Aggregation | **46** | LDR:433-448（同 env/method/column 的 Table5/Table8 双胞胎共用一个 id） |
| AggregationMember | **500**（466 included + 34 excluded）| LDR:372-393（存活）/ LDR:407-431（`.bad`） |
| Exclusion（Aggregation 内嵌记录） | **34** | LDR:394-406 |
| ResultArtifact | **128** | LDR:351-365（29 个 EVAL 目录）/ LDR:517-528（98 个搜索目录）/ LDR:715-728（iBayesLR 1 个） |
| Transformation | **3** | LDR:240-281 `_add_shared_transforms` |
| CandidateSet | **100**（98 hyperopt + 2 grid）| LDR:530-547 / LDR:636-666 |
| SelectionEvent | **98** | LDR:565-595 |
| ComparisonSet | **5**（4 环境 + 1 外部基线）| LDR:678-714 |

Bundle 容器与 id 键控：`bundle.py:24-56`（`add()` 按对象类型入 dict，同 id 覆盖——Table 5/8
双胞胎共用聚合即靠此去重）。

### A.1 ReportedResult × 59 —— 全量清单

rid 模式 `{env}/{method}/{column}/{table}`（LDR:299）。Locus 定义 `schema.py:81-94`
（artifact/page/table/row/column/quoted_text/quantity_key）。value/spread 均为 `direct(...)`
且 path 指向 `paper Table 8 (p.29)` 或 `paper Table 5 (p.12)`（LDR:314-315, 335-336, 468-469），
即**转写后的论文格值**，来源常量 LDR:54-55。metric_name 恒为 `direct(column, SCRIPT, 81)`（LDR:313/334/461）。
除 2 个 N/A 格与 VIPS 格外，comparison_set_ref=`cmp:{env}`；spread_label（有值者 56 个）恒为
LDR:126 的 Table 5 表题片段、grade=DECLARED（LDR:338, 474）。transformation_refs：
`-elbo` 格 = `t:elbo_last_row,t:elbo_format`；secondary 格加 `t:secondary_sum`（LDR:297）。
**selection_refs 在全部 59 个格上都为空**（LDR 从不填 `ReportedResult.selection_refs`，
字段定义 `schema.py:309`）——链 C 的选择事件只挂在 SelectionEvent 侧，不回指单元格。

完整清单（列：rid | quoted_text | value(spr) | agg | cmp；`+S`=含 t:secondary_sum）：

Table 8 `-elbo`（LDR:71-91 ELBO_CELLS，经 LDR:481）：
1.  `PlanarRobot/samtrux/-elbo/Table 8 | "11.47 ±0.05" | 11.47/0.05 | agg:PlanarRobot/samtrux/-elbo | cmp:PlanarRobot`
2.  `PlanarRobot/samtrox/-elbo/Table 8 | "11.47 ±0.04" | … 同上模式`
3.  `PlanarRobot/samtron/-elbo/Table 8 | "11.47 ±0.04"`
4.  `PlanarRobot/samyron/-elbo/Table 8 | "12.93 ±0.13"`
5.  `PlanarRobot/samyrox/-elbo/Table 8 | "12.98 ±0.09"`
6.  `PlanarRobot/samyrux/-elbo/Table 8 | "13.16 ±0.20"`
7.  `PlanarRobot/sepyfux/-elbo/Table 8 | "17.26 ±2.13"`
8.  `PlanarRobot/sepyrux/-elbo/Table 8 | "16.35 ±0.65"`
9.  `PlanarRobot/zamtrux/-elbo/Table 8 | "11.48 ±0.04"`
10. `TALOS/samtrux/-elbo/Table 8 | "−24.32 ±0.22"`（bundle 内为 ASCII `-24.32`）
11. `TALOS/samtrox/-elbo/Table 8 | "−24.30 ±0.10"`
12. `TALOS/samtron/-elbo/Table 8 | "−24.43 ±0.16"`
13. `TALOS/samyron/-elbo/Table 8 | "−24.00 ±0.23"`
14. `TALOS/samyrox/-elbo/Table 8 | "−23.91 ±0.13"`
15. `TALOS/samyrux/-elbo/Table 8 | "−24.13 ±0.14"`
16. `TALOS/sepyfux/-elbo/Table 8 | "−16.64 ±5.26"`
17. `TALOS/sepyrux/-elbo/Table 8 | "−19.00 ±1.07"`
18. `TALOS/zamtrux/-elbo/Table 8 | "−23.69 ±0.16"`
19. `STM300/samtrux/-elbo/Table 8 | "15.00 ±0.38"`
20. `STM300/samtrox/-elbo/Table 8 | "15.24 ±0.36"`
21. `STM300/samtron/-elbo/Table 8 | "14.96 ±0.48"`
22. `STM300/samyron/-elbo/Table 8 | "22.50 ±0.15"`
23. `STM300/samyrox/-elbo/Table 8 | "22.28 ±0.13"`
24. `STM300/samyrux/-elbo/Table 8 | "22.41 ±0.23"`
25. `STM300/sepyfux/-elbo/Table 8 | "26.69 ±0.39"`
26. `STM300/sepyrux/-elbo/Table 8 | "26.87 ±0.45"`
27. `STM300/zamtrux/-elbo/Table 8 | "N/A"`，无 agg，`not_aggregated_reason` 见 LDR:300-321
28. `BreastCancer/samtron/-elbo/Table 8 | "78.00 ±0.02"`
29. `BreastCancer/sepyfux/-elbo/Table 8 | "79.78 ±0.40"`
30. `BreastCancer/sepyrux/-elbo/Table 8 | "79.91 ±0.93"`

Table 8 secondary（LDR:95-106 SECONDARY_CELLS；列名映射 LDR:107：TALOS→`entropy`，
STM300→`num_detected_modes`；均 +S）：
31.-39. `TALOS/{samtrux,samtrox,samtron,samyrux,samyrox,samyron,sepyfux,sepyrux,zamtrux}/entropy/Table 8`
   值依次 `-16.81±0.07, -16.88±0.09, -16.82±0.07, -17.26±0.10, -17.32±0.16, -17.25±0.16,
   -25.03±5.46, -22.34±1.11, -16.91±0.07`
40.-47. `STM300/{同上前 8 法}/num_detected_modes/Table 8`
   值 `13.70±1.80, 14.10±1.50, 14.30±1.53, 9.57±1.73, 9.80±1.58, 9.10±0.99, 0.90±0.89, 0.30±0.43`
48. `STM300/zamtrux/num_detected_modes/Table 8 | "N/A"`，无 agg（LDR:104 与 300-321）

Table 5 孪生 `-elbo` ×10（LDR:111-122 TABLE5_ELBO，经 LDR:483-485；page="12"）：
49. `PlanarRobot/samtron/-elbo/Table 5 | "11.47 ±0.04"`
50. `PlanarRobot/samyron/-elbo/Table 5 | "12.93 ±0.13"`
51. `PlanarRobot/sepyfux/-elbo/Table 5 | "17.26 ±2.13"`
52. `PlanarRobot/zamtrux/-elbo/Table 5 | "11.48 ±0.04"`
53. `TALOS/samtron/-elbo/Table 5 | "−24.43 ±0.16"`
54. `TALOS/samyron/-elbo/Table 5 | "−24.00 ±0.23"`
55. `TALOS/sepyfux/-elbo/Table 5 | "−16.64 ±5.26"`
56. `TALOS/zamtrux/-elbo/Table 5 | "−23.69 ±0.16"`
57. `STM300/sepyfux/-elbo/Table 5 | "26.87 ±0.45"`（FM13 冲突对，LDR:110 注释）
58. `BreastCancer/samtron/-elbo/Table 5 | "78.00 ±0.02"`

外部基线（LDR:729-748）：
59. `VIPS/vipsum/-elbo/Table 8 | locus.quoted_text="external baseline column" | value=UNKNOWN(None),
    spread=UNKNOWN(None) | 无 agg | cmp:external-baselines | not_aggregated_reason="the cell is an
    external baseline converted from a .mat export that is not part of the bundle, so no member of
    this project produces it"`（LDR:742-747）

**逐格例（5 个全字段）**——`TALOS/sepyfux/entropy/Table 8`（chain A 主角）：
rid / Locus(artifact="paper Table 8 (p.29)", page="29", table="Table 8", row="sepyfux",
column="TALOS / entropy", quoted_text="−25.03 ±5.46", quantity_key="TALOS/sepyfux/entropy")；
metric_name=direct("entropy", `repo/evaluations/fetch_exp3.py`, 81)；direction_semantics=
declared("the table prints the negated ELBO; for TALOS entropy the secondary branch is
larger_is_better", SCRIPT, 120)（LDR:462-467）；value=direct("−25.03"→bundle 内 `-25.03`,
paper Table 8)；spread=direct("5.46")；spread_form=K_SEM(k=3.0, ddof=0, n=4, DIRECT)（LDR:470）;
aggregation_ref=`agg:TALOS/sepyfux/entropy`；transformation_refs=(t:elbo_last_row, t:elbo_format,
t:secondary_sum)；selection_refs=()；spread_label=declared(LDR:126 全文, "paper Table 5 (p.12)",
"12", key="caption")（runtime 验证其 sources label 为 `paper Table 5 (p.12):12 [caption]`）。
其余 4 例见 §A.2/A.3/A.5 的对应对象。

### A.2 Aggregation × 46（LDR:433-448；完整计数，逐条压缩）

公共字段：center="mean"；member_rule=BY_PATTERN "include run_{i}.csv, exclude run_{i}.csv.bad"
grade=DIRECT source=`repo/evaluations/fetch_exp3.py:96-104`（LDR:439-444）；dispersion 表达式
`np.std(ddof=0) * 3 / sqrt(n)`，spread_form=K_SEM k=3 ddof=0 n=存活数，grade=DIRECT（LDR:437-438）。

成员账目（included/total/exclusions）(runtime)：
- `agg:BreastCancer/{samtron,sepyfux,sepyrux}/-elbo`：各 10/10/0，n=10
- `agg:PlanarRobot/` 9 个 `-elbo`：samtron/samtrox/samtrux/samyron/samyrox/samyrux = 10/10/0；
  sepyfux = 5/10/5；sepyrux = 7/10/3；zamtrux = 8/10/2（剔除数与 README 声明 5/3/2 对应，NOTE-P:132-137）
- `agg:STM300/` 8 法 × 2 列 = 16 个：均 10/10/0，**唯 samyrux 两列 = 30/30/0, n=30**（README 声明
  OOM 后加核重跑 30 run，RD-P0:211；LDR 无 exclusions——30 全计入）
- `agg:TALOS/` 9 法 × 2 列 = 18 个：均 10/10/0，**唯 sepyfux/sepyrux 各列 = 4/10/6, n=4**
 （对应 README "SEPYFUX on TALOS: 6 bad / SEPYRUX on TALOS: 6 bad"，NOTE-P:134-135）
- Table 5 的 10 个孪生格**复用**同 id 聚合（LDR:366 agg_id 不含表名），故 56 有 agg 的格 → 46 个聚合。

Exclusion 记录 ×34（LDR:394-406）：每条 `listed=direct(len(bads), rel_dir, key="run_*.csv.bad")`、
`reason_grade=DECLARED`、`criterion_recomputable=False`、note="the exclusion is executed from a
hand-written run-id list, and the surviving final values of excluded runs lie inside the retained
range"（FM4）。分布：PlanarRobot 5+3+2=10，TALOS (6+6)×2 列=24。
**注意**：`reason_grade=DECLARED` 但未携带 README 理由文本或论文 "removed bad outliers" 句的
SourceRef——理由字符串不在 bundle 内（见 §B/§E）。

被剔除成员同样建为 AggregationMember（excluded=True，LDR:407-431），故 chain A 聚合可按需
产出反事实值（ACC:58-72：全体 10 成员重算 = `-45.32` ± `42.91`，但 RD001 只用 included 4 名）。

### A.3 AggregationMember × 500（LDR:366-431）

字段模板：`run_ref=RunRef(project="gmmvi-exp3", family_key="{method}{suffix}", run_name="run_i",
artifact_ref=相对目录, external_id=unknown_field("the run-index <-> wandb run-id binding is not
in the artifacts"))`（LDR:374-381；FM3）；selector=LAST_ROW、column=指标名、grade=DIRECT、
source=`fetch_exp3.py:98`（存活，LDR:382-384）或 `:96-104`（.bad，LDR:419-421）；
observed_value=direct(该行末值, `{rel_dir}/{file}`, key=column)（LDR:385-390）。
计数 = 56 个有 agg 的格按目录成员数求和：included 466 + excluded 34 = 500 (runtime)。

**全例（chain A 的 10 名成员）** `agg:TALOS/sepyfux/entropy` (runtime)：
| member | excluded | observed_value (entropy 末行) | 源文件 |
|---|---|---|---|
| run_0 | False | −29.456941604614258 | `extracted/evaluations/results/TALOS_EVAL/sepyfux_talos/run_0.csv` |
| run_3 | False | −21.497114181518555 | run_3.csv |
| run_5 | False | −27.786344528198242 | run_5.csv |
| run_8 | False | −21.370389938354492 | run_8.csv |
| run_1 | True | −24.836875915527344 | run_1.csv.bad |
| run_2 | True | −27.371644973754883 | run_2.csv.bad |
| run_4 | True | −178.5177001953125 | run_4.csv.bad |
| run_6 | True | −31.485546112060547 | run_6.csv.bad |
| run_7 | True | −39.14060974121094 | run_7.csv.bad |
| run_9 | True | −51.74639129638672 | run_9.csv.bad |
全部 external_id.grade=UNKNOWN（LDR:380/417）。RD001 的 member_values（included、render 前）=
[-29.456942, -21.497114, -27.786345, -21.37039]，与 ACC:90-95 冻结一致。

### A.4 CandidateSet × 100

**(a) 98 个 hyperopt 组**（LDR:530-548），id=`candidates:hyperopt/{family}/{group}`，每族 9 组，
唯 STM300 族 8 组（无 `zamtrux_stm300` 目录）→ 9×10+8=98 (runtime)。字段：
kind=HYPERPARAMETER；universe_status=**PARTIAL**（LDR:534）；declared_size=surviving_size=
组内存活 run 数（多数 24，与 README "exactly 24 different parameter-settings" NOTE-P:87 对应，
但 declared 的口径是"surviving search runs"，LDR:535-536）；generation="adopted"；
unobservable_sources=("fetch filter: get_runs() drops runs by name and by hand-written id list",
direct, SCRIPT:11)（LDR:538-543）；promotion_evidence=**direct(False, SCRIPT, 44, key="print only",
note="the champion is printed, never written to a file")**（LDR:544-546；FM8 后半）。

**(b) 2 个 grid 普查**（LDR:598-666）：
- `candidates:exp3-adopted-grid`：RECOVERED，declared=surviving=**1074** parameter points，
  generation="adopted"（LDR:636-648；ACC:193）
- `candidates:exp3-discarded-grid`：PARTIAL，**1152** points，generation="discarded"，
  superseded_by="adopted"（LDR:636-651；ACC:193-195）；promotion_evidence=declared("the discarded
  generation was abandoned after an accidental optimum at 300 components and re-run from scratch",
  README:135)（LDR:658-664）
- 两者共享同一 `IdentityCollision(key_type="wandb.group", collision_count=35, samples=35 条, note=…)`
 （LDR:625-635）：note 逐字含 "…neither 'the same grid' nor 'an unrelated grid' is available as a
 conclusion"（FM9 防火墙）。1074/1152/35/35 与 RD-P0:16、§15.2（RD-P0:394）冻结一致。

### A.5 SelectionEvent × 98（LDR:565-595；一族 9 + STM300 族 8）

模板字段（runtime 抽样验证）：kind=HYPERPARAMETER；criterion =
- metric=direct("-elbo" 或 "elbo_fb:", SCRIPT:38)
- **split=declared("no held-out split: the search objective is the run's own ELBO bound", SCRIPT:30)**
 （LDR:572-577；DECLARED 是 RD003 永远无法 PASS 的根因，见 §C）
- direction=direct("minimize", SCRIPT:41)；scope=direct("one search group ({group})", SCRIPT:48)；
  tie_break=direct("strict <, so the earliest run reaching the value wins", SCRIPT:41)；
  timing=direct("fetch time, over the runs surviving in the archive", SCRIPT:36)
candidate_values=组内 (run, objective) 全表；promoted_ref=由评测目录 `run_0_config.yml` 与搜索
config 的**共有键匹配 + 取最优**推得（LDR:551-564；匹配不到则为 ""）；
declared_policy=declared("the best run's parameters are printed and copied into the 10-seed
evaluation config", README:162)（LDR:585-590；对应 NOTE-P:111-115）；tie_tolerance=1e-3（LDR:591）;
is_recorded=direct(False, SCRIPT:44)（LDR:592）；effect_on_report="decides which parameters the
reported 10-seed cell is computed from"（LDR:593）。

**全例（chain C 主 FAIL）** `sel:hyperopt/GMM100/sepyrux_gmm100` (runtime)：n_candidates=24、
promoted='run_20'、champion_ref='run_14'、champion_value=0.675964、promoted_value=1.138794、
gap=0.46283、gap_within_declared_precision=False → RD003 FAIL（ACC:154-160 同值冻结）。
其余例：`BC/samyrox_bc` promoted='run_23'（FAIL）；`GC/samtrux_gc` gap=0.000916 判近并列
（ACC:163-167）；`TALOS/zamtrux_talos`、`WINE/zamtrux_WINE` promoted=''（unrecorded，INCONCLUSIVE，
ACC:170-175）。

### A.6 ComparisonSet × 5（LDR:678-714）

- `cmp:PlanarRobot`(9 成员) / `cmp:TALOS`(9) / `cmp:STM300`(8，剔 N/A) / `cmp:BreastCancer`(3，仅转写格)：
  members=(rid, method)（LDR:681-687）；external_origin=direct("every member is computed inside
  this project", README:132)（LDR:688）；presentation_rule=PresentationRule(expression="bold iff a
  row's mean ± 3·SE interval does not overlap the best row's, using >= on the larger-is-better
  branch and < on the other", operator=">= / <", symmetric=False, k_factor=3.0,
  source="fetch_exp3.py:55-63")（LDR:689-696；FM12）；**observed_marks=unknown_field("the printed
  marks are not in the frozen text")**，注释明说"printed bold spans live in the PDF layout and were
  never transcribed"（LDR:697-699）。
- `cmp:external-baselines`：1 成员 `VIPS/vipsum/-elbo/Table 8`；external_origin=declared("converted
  from an external .mat export by a script whose input path is hardcoded to a machine that is not
  part of the bundle", `repo/evaluations/iBayesLR_results/mat_to_csv.py:6`)（LDR:702-714；FM14）；
  无 presentation_rule → RD007 NOT_APPLICABLE。

### A.7 Transformation × 3（全量；LDR:240-281）

1. `t:elbo_last_row` step=identity, applied_at=code, target="-elbo", params={stage:member,
   selector:"last row of the history"}, condition=declared("always", SCRIPT, 98),
   sources=[`fetch_exp3.py:98 [to_numpy()[-1]]` note "the last row, not the best row"]
2. `t:secondary_sum` step=sum_of_part, code, target="secondary metric", params={stage:member,
   parts:()}, condition=declared("secondary_metrics are always summed", SCRIPT, 102),
   sources=[`:103 np.sum(this_secondaries)` note "one-element list here, so the sum is the identity"]
3. `t:elbo_format` step=format, code, target="table cell", params={stage:render, mode:fixed,
   digits:2}, condition=declared('format == "elbo_format"', SCRIPT, 64), sources=[`:68 elbo_format`
   note "mean and ± are rounded by separate %.2f conversions"]

**链 C 的 "manual" 誊抄没有 Transformation 对象**（AppliedAt.MANUAL 已定义 `schema.py:73-77`，
LDR 未使用；誊抄事实只以 SelectionEvent.declared_policy(README:162) 形式存在）。取负/×100 的
分支变换（FM11）也未建对象——`fetch_exp3.py` 的分支语义只进了上表 condition/note。

### A.8 ResultArtifact × 128（LDR:351-365 / 517-528 / 715-728）

- **29 个 EVAL 目录**（Table 8/5 涉及的 env×method 目录，含 BC 3 个）：produced_by=
  ProducedBy(script=fetch_exp3.py, call_site="fetch_exp3_eval", invocation_args="the call whose
  output matches this directory is commented out at HEAD; the only live call (:271-275) writes BCMB
  with bi_accuracy", **grade=UNKNOWN**)；columns=CSV 首行列名 (runtime)；note="two different calls
  in the script write the same directory name"（LDR:351-365；FM2）。
  `required=("MMD:",)` 仅当 family=BC_EVAL（LDR:350）→ BC 3 个目录**实测缺 `MMD:` 列**
  （列含 `bi_accuracy:`，runtime），与 RD-P0:124 断点定位一致。
- **98 个搜索组目录**：produced_by grade=**DERIVED**，call_site="fetch_exp3_hyperopt"（LDR:517-528）。
- **1 个 `repo/evaluations/iBayesLR_results`**：produced_by=mat_to_csv.py `__main__`,
  invocation_args="reads /home/oleg/... which is not in the bundle", grade=DECLARED;
  required_columns=("track_elbos","track_n_fevals") 且 columns=() → RD008 FAIL（LDR:715-728）。
- producer grade 分布 (runtime)：UNKNOWN 29 / DERIVED 98 / DECLARED 1。sha256/size 字段存在
  （`schema.py:169-178`）但 loader 未填（LDR 构造时无一传 sha256）。supersession 字段亦未填
  （superseded_from/by 全空，runtime；FM2 只以 note + 缺列证据存在）。

---

## B. 论文侧内容：表达了什么、没表达什么

1. **Bundle 中唯一一段论文散文**：`SPREAD_LABEL`（LDR:126），逐字为
   `3σ confidence intervals based on the standard error of its mean using ten different seeds`
   ——它是 Table 5 表题（p.12）的**一个从句**，不是完整句子。它以 DECLARED 挂在 56 个
   ReportedResult.spread_label 上（N/A×2 与 VIPS×1 无，LDR:338/474；runtime 验证 56/59）。
   完整表题（含 "The proposed candidate clearly outperforms…" 与 "removed bad outliers…" 两句）
   只存在于 ED 侧笔记：NOTE-T:34（逐字）、JSON-PV `/table_provenance/plus_minus_semantics_verbatim`
   与 `/table_provenance/exclusion_rule_verbatim`（:21, :23）。**Bundle 里没有。**
2. **每个格子的 locus.quoted_text 只是数字串**（如 `"−25.03 ±5.46"`，LDR:458），
   即单元格值转写，**不是任何论文句子**。59 个格中除 VIPS 的占位
   `"external baseline column"`（LDR:738）外，无散文。
3. **格 locus 与论文表/图的对应**：LDR:54-55 把 `PAPER8="paper Table 8 (p.29)"`、
   `PAPER5="paper Table 5 (p.12)"` 作为 locus artifact 字符串；页码在 Locus.page（LDR:306/454）。
   映射证据链：NOTE-T:24（Table 8=附录 K，p.29；附录 K 正文句 "The complete table for Experiment
   3 … can be found in Table 8."）；NOTE-T:23 与 JSON-PV `/table_provenance/main_text_counterpart`
   （Table 5 p.12 仅 Samtron/Samyron/Sepyfux/Zamtrux 4 行、仅 -ELBO）；NOTE-T:19 /
   JSON-PV `/source_files/versions_agreement`（camera-ready 与 arXiv v2 的 Table 8 逐格一致，
   唯一差异 GMM20 `-0.00` vs `0.00`，不在冻结环境）。两版 PDF 的 sha256 冻结于
   JSON-PV `/source_files/*/sha256`（:8, :12）与 NOTE-T:11-12。
4. **论文行标签 vs bundle 列名**：论文 secondary 行标签 `H(q)`/`Modes`/`MMD` 与表头方法名
   只在 loader 注释（LDR:93-94 "TALOS `H(q)` = `entropy`, STM300 `Modes` = `num_detected_modes`"、
   LDR:107）与 NOTE-T:53/69/85 中建立对应；Locus.column 存的是 **CSV 列名**（"TALOS / entropy"），
   论文标签映射不是 schema 字段。`MMD` secondary（PlanarRobot 列）完全未冻结进 bundle
   （SECONDARY_CELLS 无 PlanarRobot，LDR:95-106；NOTE-T:57-65 有抄录但未用）。
5. **图**：Figure 3（p.28 学习曲线，"Shaded areas show best and worst performance"，NOTE-T:116）
   与 Table 9（p.30 重跑声明，JSON-PV `/per_seed_appendix/detail`）在 bundle 中**零表达**。
6. **loci 指向哪里**：ReportedResult 的 locus/source 指 `paper Table 5/8 (p.12/29)`（人工转写后
   的文本冻结，RD-P0:434 明确 Phase 1 不解析 PDF）；而**成员、artifact、candidate set、selection
   event 全部指向 repo 盘上产物**（`extracted/evaluations/results/...` CSV/YAML、
   `repo/evaluations/fetch_exp3.py`、`repo/README.rst`）。即：RD 冻结 bundle 是"论文格值转写 +
   仓库产物重算"的对接件；论文本身只以 59 个数字串 + 1 个从句进入证据图。

---

## C. RD 对 GMMVI 的运行时判定（本会话重跑，audit_bundle 全量）

命令形态：`cd /f/MLResearch/result-doctor && PYTHONPATH="src;tests" python -X utf8` 加载
`load_gmmvi_bundle(r"F:\MLResearch\experiment-doctor\phase0-gmmvi")` 后 `audit_bundle`
（构造方式取自 ACC:14-22；`evaluate` 538 条，NOT_RUN 层追加 0 条——8 条规则全部有靶，
`audit.py:33-67`）。规则实现 `rules.py:115-834`。

### C.0 状态向量 (runtime)

| | PASS | FAIL | INCONCLUSIVE | NOT_APPLICABLE | NOT_RUN | 合计 |
|---|---|---|---|---|---|---|
| RD001 | 51 | 0 | 5 | 3 | 0 | 59 |
| RD002 | 0 | 0 | 46 | 0 | 0 | 46 |
| RD003 | 0 | 4 | 94 | 59 | 0 | 157 |
| RD004 | 0 | 0 | 100 | 0 | 0 | 100 |
| RD005 | 54 | 2 | 0 | 3 | 0 | 59 |
| RD006 | 51 | 0 | 5 | 3 | 0 | 59 |
| RD007 | 0 | 0 | 4 | 1 | 0 | 5 |
| RD008 | 9 | 5 | 39 | 0 | 0 | 53 |
| **总** | **165** | **11** | **293** | **69** | **0** | **538** |

与 ACC 逐条一致：18/18 TALOS RD001 PASS（ACC:39-44）、chain A PASS/counterfactuals
（ACC:30-72）、chain B INCONCLUSIVE + artifact FAIL（ACC:107-121）、chain C 98 事件
(91 exact/4 FAIL/1 near/2 unbound)（ACC:137-151）、RD004 INCONCLUSIVE（ACC:189-213）、
RD007/RD008/RD005/NA 向量（ACC:217-261）。

### C.1 全部 FAIL × 11（reason 逐字）

1. `RD003 | selection:sel:hyperopt/BC/samyrox_bc` — "the promoted member is not the champion under the declared policy, beyond the declared precision"
2. `RD003 | selection:sel:hyperopt/BC/zamtrux_bc` — 同上
3. `RD003 | selection:sel:hyperopt/GMM100/sepyrux_gmm100` — 同上（champion 0.675964 vs promoted 1.138794）
4. `RD003 | selection:sel:hyperopt/Planar4/samyrox_planar_4` — 同上
5. `RD005 | BreastCancer/sepyrux/-elbo/Table 8` — "no formula family reproduces the published dispersion"（published 0.93；六族给 0.83/0.88/0.26/0.28/0.79/0.83，runtime）
6. `RD005 | STM300/sepyfux/-elbo/Table 5` — 同上（FM13 孪生格的 spread 无一族复现，runtime）
7. `RD008 | artifact:extracted/evaluations/results/BC_EVAL/samtron_bc` — "a declared producer writes these column(s) here and the surviving file does not carry them; the surviving file is therefore not the artifact that produced the cell"（missing `["MMD:"]`，ACC:117-121）
8. `RD008 | artifact:extracted/evaluations/results/BC_EVAL/sepyfux_bc` — 同上
9. `RD008 | artifact:extracted/evaluations/results/BC_EVAL/sepyrux_bc` — 同上
10. `RD008 | artifact:repo/evaluations/iBayesLR_results` — 同上（missing `["track_elbos","track_n_fevals"]`，ACC:252-254）
11. `RD008 | quantity:STM300/sepyfux/-elbo` — "the same quantity is printed with different values in two products; which one is intended, and why they differ, is not determined here"（loci: Table5=26.87±0.45 / Table8=26.69±0.39，runtime；FM13）

### C.2 全部 INCONCLUSIVE × 293（按 reason 分组，逐 target 列出）

**RD001 × 5**，reason="mismatch, and member identity is not determined: producer of … is not recorded"（LDR producer grade=UNKNOWN，`rules.py:99-100`）：
- `BreastCancer/samtron/-elbo/Table 5`、`BreastCancer/samtron/-elbo/Table 8`（…/BC_EVAL/samtron_bc）
- `BreastCancer/sepyfux/-elbo/Table 8`（…/sepyfux_bc）、`BreastCancer/sepyrux/-elbo/Table 8`（…/sepyrux_bc）
- `STM300/sepyfux/-elbo/Table 5`（…/STM300_EVAL/sepyfux_stm300）
（chain B 的判定纪律：RD-P0:305 "链 B 当前正确状态：**不是 FAIL**"；ACC:107-113 冻结
 rendered 78.01±0.01 vs reported 78.00±0.02 且 reason 含 "identity"。）

**RD002 × 46**（`rules.py:234-270`），reason 两型：
- A 型 "10 member(s) cannot be bound to an external run id"（37 个聚合）/ "30 member(s) …"
 （2 个：`agg:STM300/samyrux/-elbo`、`agg:STM300/samyrux/num_detected_modes`）——即除 B 型外全部 40 个：
  `agg:BreastCancer/{samtron,sepyfux,sepyrux}/-elbo`；`agg:PlanarRobot/{samtron,samtrox,samtrux,samyron,samyrox,samyrux}/-elbo`；
  `agg:STM300/{samtrux,samtrox,samtron,samyron,samyrox,sepyfux,sepyrux}/{-elbo,num_detected_modes}`（14）；
  `agg:TALOS/{samtrux,samtrox,samtron,samyron,samyrox,samyrux,zamtrux}/{-elbo,entropy}`（14）；
  `agg:PlanarRobot/samtron...` 已计入。
- B 型 "… cannot be bound … ; an exclusion criterion is not recomputable"（7 个）：
  `agg:PlanarRobot/{sepyfux,sepyrux,zamtrux}/-elbo`、`agg:TALOS/{sepyfux,sepyrux}/{-elbo,entropy}`。
（ACC:75-81 冻结 sepyfux/entropy 为 INCONCLUSIVE、10/4/6 账目、unbound=0。）

**RD003 × 94**，三型（`rules.py:349-363`）：
- 型 1（92 个，全部 hyperopt 事件除去 4 FAIL + 2 unbound）：reason="criterion fields not all
  direct: {'metric': 'DIRECT', 'split': 'DECLARED', 'direction': 'DIRECT', 'scope': 'DIRECT',
  'tie_break': 'DIRECT', 'timing': 'DIRECT'}"。根因是 LDR:572-577 把 split 记为 DECLARED，
  而 PASS 要求六字段全 DIRECT（`rules.py:358-360`）→ **RD003 在 GMMVI 上恒 0 PASS**，即使
  91/98 组 promoted==champion 也不升级。targets=全部 `selection:sel:hyperopt/…` 中除下列外的 92 个
  （族清单同 §A.5 计数：BC9/BC_MB9/GC9/GC_MB9/GMM100 9/GMM20 9/Planar4 9/STM20 9/STM300 8/TALOS 9/WINE 9）。
- 型 2（2 个）：`selection:sel:hyperopt/TALOS/zamtrux_talos`、`selection:sel:hyperopt/WINE/zamtrux_WINE`
  reason="the promoted member cannot be bound to a candidate record, so the declared policy cannot
  be checked against it (['promoted_ref_unrecorded'])"（ACC:170-175）。
- （4 FAIL 见 C.1；NOT_APPLICABLE ×59 为逐格 "reported:{rid}"，
  reason="no selection step is recorded in the production of this cell"——selection_refs 全空所致，
  `rules.py:365-379`。）

**RD004 × 100**（`rules.py:423-445`）：
- 型 1（98 个 `candidates:candidates:hyperopt/…` 全清单同 §A.5 族×组）：reason="candidate
  universe recoverability is PARTIAL; this is never inferred from the count of surviving artifacts"
 （ACC:207-213 冻结措辞）。
- 型 2（2 个）：`candidates:candidates:exp3-adopted-grid`、`candidates:candidates:exp3-discarded-grid`
  reason="35 identity key(s) of type wandb.group are reused across search generations; declared and
  surviving sizes are both reported, and no judgment is made here about what relationship the two
  generations have"（ACC:189-205，含防火墙断言 "混淆" 不得出现）。

**RD006 × 5**：`reported:BreastCancer/samtron/-elbo/Table 5`、`/Table 8`、
`reported:BreastCancer/sepyfux/-elbo/Table 8`、`reported:BreastCancer/sepyrux/-elbo/Table 8`、
`reported:STM300/sepyfux/-elbo/Table 5`，reason="the recorded chain does not yield the printed cell;
an unrecorded step cannot be excluded"（`rules.py:644-648`）——与 RD001 同五格。

**RD007 × 4**：`comparison:cmp/{BreastCancer,PlanarRobot,STM300,TALOS}`，reason="the rule and the
peer values are recovered, but the marks actually shown in the product are not; the recomputed set
is reported without a judgment"（LDR:699 observed_marks=UNKNOWN；ACC:217-225）。

**RD008 × 39**：**全部 39 条**为同一 reason="the quantity is printed in a single product,
so there is nothing to cross-check"（`rules.py:749-760`；即凡 quantity_key 只有一个 loci 的格），
targets (runtime)：
`quantity:BreastCancer/{sepyfux,sepyrux}/-elbo`（2）；
`quantity:PlanarRobot/{samtrox,samtrux,samyrox,samyrux,sepyrux}/-elbo`（5）；
`quantity:STM300/`：9 法的 `-elbo`（除 sepyfux 为 FAIL 外 8 个）+ 9 法的 `num_detected_modes`（9 个）
（17）；
`quantity:TALOS/`：`samtrux/-elbo`、`samtrux/entropy`、`samtrox/-elbo`、`samtrox/entropy`、
`samtron/entropy`、`samyron/entropy`、`samyrox/-elbo`、`samyrox/entropy`、`samyrux/-elbo`、
`samyrux/entropy`、`sepyfux/entropy`、`sepyrux/-elbo`、`sepyrux/entropy`、`zamtrux/entropy`（14）；
`quantity:VIPS/vipsum/-elbo`（1）。合计 2+5+17+14+1=39 ✓。
（RD008 的 artifact 分支：BC×3 + iBayesLR 为 FAIL，见 C.1；其余 required_columns 为空的
artifact 不产 RD008 target。）

### C.3 RD001 PASS 的边界（对 PD 重要）

51 PASS = TALOS 18（ACC:39-44）+ PlanarRobot 9(T8)+4(T5 孪生共用重算同值) + STM300 15(T8) +
TALOS 4(T5 孪生) + …——凡成员齐、公式族复现者。BC 与 FM13-T5 是仅有的 5 个不一致格。
counterfactuals 冻结于 ACC：ddof=1 → `6.31`（ACC:51-52）、含 .bad → `-45.32 ± 42.91`（ACC:58-72）、
std_ddof0=`3.64`/sem_ddof0=`1.82`（ACC:53-54）(runtime 复现一致：family renderings
{k_sem_ddof0_k3:'5.46', k_sem_ddof1_k3:'6.31', std_ddof0:'3.64', sem_ddof0:'1.82', …})。

---

## D. 三条 GMMVI 故事线：在冻结 Bundle/RD 里的承载

### D(i) TALOS H(q) Sepyfux −25.03 ± 5.46

- 承载对象：`ReportedResult TALOS/sepyfux/entropy/Table 8`（LDR:99 值、LDR:449-476 构建）、
  `agg:TALOS/sepyfux/entropy`（4 included/6 excluded，LDR:366-448）、
  `t:elbo_last_row/t:elbo_format/t:secondary_sum`（LDR:240-281）、
  ResultArtifact `extracted/evaluations/results/TALOS_EVAL/sepyfux_talos`（producer UNKNOWN，LDR:351-365）。
- 承载规则：RD001 **PASS**（rendered −25.03/5.46 == reported，runtime + ACC:30-37）；
  RD005 **PASS**（唯一复现族 `k_sem_ddof1` 给 6.31、只有 `k_sem_ddof0_k3` == 5.46，ACC:47-55；
  spread_label 措辞说 "standard error of its mean"，公式族是 k·SE → 一致，`rules.py:543-544`）；
  RD002 **INCONCLUSIVE**（10 名成员匿名 + 剔除准则不可重算，ACC:75-81）；RD008 quantity
  `TALOS/sepyfux/-elbo` PASS 孪生同值，但 `TALOS/sepyfux/entropy` 单产地 INCONCLUSIVE（runtime）。
- 关联论文句子：**仅 spread_label 从句**（LDR:126）。"removed bad outliers when computing the
  reported values"（NOTE-T:34 / JSON-PV `/table_provenance/exclusion_rule_verbatim`）**不在 bundle**；
  bundle 里 exclusion 只有 reason_grade=DECLARED 与自由文本 note（LDR:394-406），无 SourceRef 指向论文。

### D(ii) BC 链：0/9 复现的 artifact 身份失败

- Phase-0 叙述"9 个数字没有一个能重算"（RD-P0:15、§5.2 RD-P0:116-129；FM1/FM2）。
- 冻结 bundle 实际只转写了 **3 个 BC 格**（LDR:87-90 注释 "Phase 0 §5.2 froze these three BC cells
  in text; the remaining six need the PDF"）→ "0/9" 中其余 6 格无对象；就这 3 格：
  RD001 全 **INCONCLUSIVE**（不是 FAIL，理由含 producer 未记录，`rules.py:99-100` + runtime），
  RD006 同 5 格之一 INCONCLUSIVE；RD008 对 3 个 BC artifact **FAIL**（missing `MMD:`，
  reason "…not the artifact that produced the cell"，ACC:107-121）；RD005：samtron 的 spread 0.02
  可被 3 族复现（k_sem_ddof1_k3/std_ddof0/std_ddof1，ACC:124-134）→ PASS（措辞是 SE 而复现族含
  ddof=1·k·SE 与 std —— 见 `rules.py:543` 分支），sepyfux PASS，**sepyrux FAIL**（0.93 无一族复现）。
- 论文句子关联：无任何 BC 相关散文在 bundle；断链叙事（`logregacc` 项目导出、`:191-195` vs
  `:256-260` 两调用同名目录）只存于 RD-P0:124 与 LDR:358-359 的 invocation_args 文本。

### D(iii) 选择图：85/99 精确冠军、6/99 非冠军、4/99 无匹配；GMM100/sepyrux 1.139 vs 0.676

- Phase-0 叙述：RD-P0:17、§5.3 表（RD-P0:136-141）——85/6/4（99 组）。
- 冻结实现**改写了分账口径**：LDR:551-564 用"评测 `run_0_config.yml` 与搜索 config 共有键全等 +
  组内 argmin"重绑，事件数 98（STM300 无 zamtrux 组，runtime），ACC:137-151 冻结
  **91 exact(gap=0) / 4 FAIL / 1 near-tie / 2 unbound**：
  FAIL = BC/samyrox、**BC/zamtrux**、GMM100/sepyrux、**Planar4/samyrox**（runtime C.1）；
  near = GC/samtrux（gap 0.000916，ACC:163-167）；unbound = TALOS/zamtrux、WINE/zamtrux（ACC:170-175）。
  与 Phase-0 的 6/99-4/99 名单不重合（Phase-0 名单含 GC/samtrux 近并列与 GMM100/{samtrox,sepyfux}
  无匹配，RD-P0:139-140；冻结版把 GC/samtrux 判并列、把 GMM100/samtrox/sepyfux 绑上了候选）。
  此差异是 PD 必须知道的事实：`file:line` = RD-P0:136-141 vs ACC:137-175 (runtime)。
- GMM100/sepyrux 数字：champion_ref='run_14'=0.675964、promoted 'run_20'=1.138794、gap=0.46283
  （runtime；ACC:154-160 冻结 "not the champion"）。
- 论文句子关联：SelectionEvent.declared_policy 引 **README:162**（LDR:585-590），非论文句子；
  "冠军只 print 不落盘"= promotion_evidence/is_recorded DIRECT False @fetch_exp3.py:44
  （LDR:544/592）。**论文正文没有任何一句宣称"取最优超参"**被绑定到这些事件（论文侧的对应散文
  UNKNOWN——本会话未在 bundle 及其引用文件中找到指向论文方法章节的选择声明句子；RD-P0:133 只
  说机制是 DECLARED via README）。

---

## E. Paper Doctor 缺口清单（RD 因无论文文本对象而不能答的问题）

逐条给出"为什么 RD 答不了"的对象级证据（全部指向 §B 的缺席事实）：

1. **主张覆盖度**：论文摘要/结论/§12 正文宣称（如 Table 5 caption 的 "clearly outperforms the
   prior methods VIPS and iBayes-GMM"，NOTE-T:34）是否有对应 ReportedResult？——bundle 的对象
   只有 59 个表格 + 1 个从句（LDR:126），无 claim/sentence 对象；RD schema 明确排除 `ClaimRef`
   （RD-P0:290 "属 Paper Doctor"）。
2. **"ten different seeds" 对散文的一致性**：spread_label 从句声称 ten seeds（LDR:126），但
   TALOS/sepyfux 实际 n=4、PlanarRobot n=5/7/8、TALOS/sepyrux n=4（§A.2 runtime）。RD005 只比对
   "措辞 vs 公式族"（`rules.py:521-567`），n 与措辞的矛盾**不在其判定面**；RD 也不检查论文
   正文其它 seed 宣称。NOTE-S:10-13 已证 seed 值本身不可恢复（UNKNOWN）。
3. **"removed bad outliers" 句 ↔ 34 条 Exclusion 的绑定**：论文剔离句只存在于 ED 笔记
   （NOTE-T:34 / JSON-PV `/table_provenance/exclusion_rule_verbatim`），bundle Exclusion 无指向
   论文的 SourceRef（LDR:394-406）——论文说的"bad outliers 发生在 Sepyfux on PlanarRobot and
   TALOS"能否被剔离记录支持（注意 bundle 里 TALOS/sepyrux 也有 6 剔离，而该句只点名 Sepyfux 与
   PlanarRobot/TALOS；README 则列 5 项，NOTE-P:131-137），RD 无对象可判。
4. **"clearly outperforms / seems preferable / performed worst overall"（NOTE-T:34, RD-P0:216 引
   README:156）这类比较级散文**：RD007 只能对"加粗标记"这一种呈现主张工作，且 observed_marks
   恒 UNKNOWN（LDR:699；§C.2 RD007×4 INCONCLUSIVE）。论文文字比较主张与 ComparisonSet 成员值
   之间无任何链接对象。
5. **Table 8 之外的一切论文内容**：Table 8 的 11 个环境中 7 个（BCMB/GC/GCMB/GMM20/GMM100/STM20/
   WINE）、PlanarRobot 的 `MMD` secondary 列（NOTE-T:57-65 有转写未入 bundle）、Table 3（p.11，
   NOTE-T:43）、Figure 3（p.28，NOTE-T:116）、Table 9（p.30，JSON-PV `/per_seed_appendix/detail`）
   均无 ReportedResult（59 格的构造面 LDR:71-122 白名单）。PD 若要审计"论文说过的每个数字"，
   需自建论文侧全量对象。
6. **列/行标签对应**：locus.column 用 CSV 列名而非论文行标签（§B.4）；"H(q)=entropy"、
   "Modes=num_detected_modes" 的映射只活在代码注释（LDR:93-94/107）。论文若用不同名称引述同一
   指标，RD 无法核对。
7. **相机就绪版 vs arXiv v2**：两版 Table 8 一致性只有 ED 笔记的一句结论（NOTE-T:19 /
   JSON-PV `/source_files/versions_agreement`），bundle 不携带任何 PDF 解析证据对象；
   RD-P0:421（O7）把"相机就绪版与 arXiv v2 完全等价"列为 UNKNOWN/Open。PD 审计"论文宣称"时
   必须选定版本并自带该版本全文证据。
8. **选择政策的论文措辞**：README:162 进入 declared_policy（LDR:585-590），论文正文若有任何
   "we selected the best configuration"式句子，与 98 个 SelectionEvent 无字段可连
   （SelectionEvent 无 paper-prose 引用面，`schema.py:237-254`）。
9. **"同一量两处不同"的因果与归属**：RD008 已冻结 FM13 冲突对存在（C.1 #11），但"哪个值被论文
   正文引用/哪张表是权威"是纯散文问题，RD 无对象（防火墙也禁止归因，`rules.py:772-777`）。
10. **RD001/005/006 恒不引用论文正文**：其 evidence sources 仅到 value/spread/label 的转写串
    （`rules.py:119, 576`）——论文主张层面（claim-level）的"重算不一致意味着哪句论文话失效"
    完全开放给 PD。

### 附：本会话核对过但无结论的项（UNKNOWN）

- 论文正文是否存在其它提及 "25.03"、"5.46"、"bad outliers"、"best hyperparameters" 的句子：
  未核验（bundle 与两份 notes 之外无全文检索面；本次未运行 PDF 文本提取，因超范围）。
- 6 个未转写 BC 格的逐格判定：无对象，见 D(ii)。
- RD 是否有 GMMVI canonical audit JSON：无（见开头第 7 项）。

（完 · 本文件是 Paper Doctor phase0 work 产物，不属于 RD 冻结面；未修改任何既有文件。）
