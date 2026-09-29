# ML Research — Final State

Phase 3 §26. Produced after Paper Doctor 0.1.0 was published, 2026-09-29.
This document is committed inside `paper-doctor/release/` because that is the only repository this
phase was permitted to write; its **content** is program-level, not tool-level.

Every remote fact below was re-read on 2026-09-29 from PyPI's JSON API and GitHub's tags API rather
than recalled from an earlier phase's notes. Nothing here closes a gap that is still open.

## 1. The complete stack

| Layer | PyPI package | Version | GitHub tag → commit | Status |
|---|---|---|---|---|
| Dataset Doctor | `dataset-doctor-audit` | 0.1.2 (wheel 146,928 B `3d7c73572d099857…`, sdist 440,442 B `d785c10a2f5f6f04…`) | `v0.1.2` → `107504ed` | **RELEASED / FROZEN** |
| Experiment Doctor | `experiment-doctor` | 1.0.0 (wheel 132,523 B `2bf8aa04a3b1ee8f…`, sdist 144,788 B `6c4606aeb278949c…`) | `v1.0.0` → `fb3a2420` | **RELEASED / FROZEN** |
| Result Doctor | `result-doctor` | 0.1.0 (wheel 57,593 B `54b3ddd9a9831cbf…`, sdist 78,008 B `e054b57cf1c3f12e…`) | `v0.1.0` → `bec3ab98` | **RELEASED / VERIFIED / FROZEN** |
| Paper Doctor | `paper-doctor` | 0.1.0 (wheel 67,719 B `10a5fc2cfe28155b6647edb85fd0e74422e814efc7ac1685a436b06226928461`, sdist 182,137 B `29b759f815d60dc896901eeec3fa3e125faa2caa1e184d4908dbb4d292a11d2e`) | `v0.1.0` → `2a02698637f35bd3fec28d98a8b6e272b8e1fc9a` | **RELEASED / VERIFIED / FROZEN** |

For Paper Doctor the hashes are of the bytes downloaded from PyPI in this session and are the
published identity; `release/RELEASE_FREEZE.md` §2-3 explains why they differ from the locally
staged archive hashes and shows the member-level content identity.

Verification that the four layers actually work **together**, and not merely each in isolation, is
the TabM chain in §2: it invokes the released Dataset Doctor 0.1.2, Experiment Doctor 1.0.0 and
Result Doctor 0.1.0 packages as installed tools, over read-only upstream artifacts, and modifies
none of them.

## 2. TabM end-to-end chain (chain-1 of `phase3/tabm/end_to_end_chain.json`)

Acceptance target: **TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembling**,
ICLR 2025. Code repository `yandex-research/tabm` pinned at commit
`28e47ae301c92ec37787dde1ce923a0793f405b4`; paper source from arXiv `2410.24210`, entry point
`main.tex`, 88,033 B, sha256 `15663553d04fcbb8b3341df5c0d269c7703d4ba279be557fcd77ea4765ab0a62`
(declared by the corpus and verified equal). The chain's statement:
*"the paper's printed Adult split size, the seed aggregation behind the Adult accuracy, the shipped
run that is one member of it, and the official dataset copy that fed it."*

```
paper claim
  C6 `$26\,048$` (main.tex:8, NUMERIC_ATTRIBUTION)  → PD001 PASS, PD003 PASS
  C7 the 15-random-seed sentence (main.tex:981, SCOPE) → PD001 PASS, PD002 INCONCLUSIVE
  C8 `$16\,281$` (main.tex:8, NUMERIC_ATTRIBUTION)  → PD001 PASS, PD003 **FAIL**
      │   locators: main.tex, FLOAT `default-datasets` (table:4), PROSE cells; every link base here is
      │   AUDITOR_DECLARED — declared by the auditor in the manifest, never a similarity heuristic
      ▼
PD (paper-doctor 0.1.0, 0 adapters written for TabM)
      │   command: paper-doctor audit phase3/tabm --json phase3/tabm/pd_findings.json
      │   32 findings — PASS 10, FAIL 2, INCONCLUSIVE 5, NOT_APPLICABLE 14, NOT_RUN 1
      │   findings sha256 08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0 (17,511 B)
      ▼
reported result
      │   tabm/adult-seed3/test-score   and   the aggregation target agg:adult-seed-mean
      ▼
RD (result-doctor 0.1.0, 0 RD rules added, RD source untouched)
      │   command: result-doctor audit phase3/tabm/result-doctor.yml --json > phase3/tabm/findings.json
      │   14 findings — PASS 1, INCONCLUSIVE 6, NOT_APPLICABLE 6, NOT_RUN 1
      │   artifact sha256 c56b62623b39ed9a4c311f8bcc6be6de457c1a0f8a4d34d3da99a4b71c7d2774 (12,392 B)
      │   aggregation/selection/transformation surface: RD002 over `aggregation:agg:adult-seed-mean` = PASS,
      │   members enumerated by the author in result-doctor.yml (15 of them)
      ▼
run
      │   exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json — the shipped evaluation run
      │   exp/tabm/adult/0-evaluation/3.toml, seed 3, one of the 15 enumerated aggregation members
      ▼
ED (experiment-doctor 1.0.0, captured adapter on its declared surface only, ED source untouched)
      │   command: experiment-doctor init … --command 'python bin/model.py exp/tabm/adult/0-evaluation/3.toml
      │            --force' --seed 3 --config … --dataset <official adult copies>
      │            && experiment-doctor audit … --adapter captured -o phase3/tabm/ed-captured
      │   ED002 PASS, ED003 PASS, ED001 NOT_APPLICABLE, ED004 / ED009 / ED010 INCONCLUSIVE
      │   report sha256 2de48cc368f13fc3fbd0e9582adc659f712382067d45b142740a6e14ae35e170
      │   lock sha256   fb27c5eeada88d7a9d471e09464d7c60e444ea7743c66cd0433bdbc883e51cf8
      │   generic discovery (no adapter at all) also ran: phase3/tabm/ed-generic-adult-runs/,
      │   phase3/tabm/ed-generic-whole-repo/
      ▼
dataset
      │   ds_05c7465f — the official Adult copies at F:\DatasetDoctorWork\realworld\adult\prepared
      │   train.csv sha256 ceb601e84db1fa01a57ae1e501e7137566297c1bc7e29b5b3605fe562d36ada1
      │   test.csv  sha256 23c3baa9db371c20612ec9696aaa95ce6d512d4171669beb97037e430e72a9bd
      ▼
DD (dataset-doctor-audit 0.1.2, 0 adapters written for TabM, DD source untouched)
          command: dataset-doctor audit F:/DatasetDoctorWork/realworld/adult/prepared
          fingerprint sha256 1f0dd1a5785fafde2627c9e47de94ebf436bbed551e11ac1200ad0804c63c9df
          report sha256    c1456a7bf602d4c3b4cda5f316a1fdb9e04ed15b7149ec2eb393046428c82f5f
          split sizes train 32,561 / test 16,281; config hash cfg_091fd33c9ce94a35;
          manifest hash 9bf9cea8ee536e96483be1e5a0efef44; eval safety FORMAL_EVAL_INVALID
```

The four joins that connect the layers are recorded in `phase3/tabm/end_to_end_chain.json`
(`joins`), and every one of them is a **declared** relation: a manifest field, an author-declared
member enumeration, the declared source file of a run, or a dataset the auditor declared and both
ED and DD then agreed on by digest. **No cross-layer similarity was computed anywhere in this
chain.** That is the point of the chain, not an omission.

Two further chains in the same ledger deliberately stop at the PD layer, and say why instead of
being padded downward:

- `chain-2-dataset-composition-counts` — three counts the paper states about its own dataset
  composition plus one derived count it never prints. These claims are about the paper's own tables;
  no reported result, run or dataset is what they assert. C1 PASSes PD006, C2 **FAILs** PD006, C3 is
  INCONCLUSIVE at PD001.
- `chain-3-block-addressed-cell` — `$0.1601$` in a transposed table whose row label is carried by a
  vertical merge. The declared cell address has two readings and the source separates neither, so PD
  stops at INCONCLUSIVE and never reaches a value that could be joined downstream.

### The two FAIL findings, stated exactly

- **PD003 @ C8** — the manifest declares C8 (`$16\,281$`) as evidenced by
  `tables/app-rtdl-datasets.tex` cell `(column='# Train', row='Adult')`; that cell prints `26048`.
  PD compares the claim's literal against the number printed at the locus the claim resolves to, gets
  16,281 vs 26,048 (delta 9,767) and reports FAIL. The same source row —
  `Adult & $26\,048$ & $6\,513$ & $16\,281$ & …` at `app-rtdl-datasets.tex:8`, header
  `Name / # Train / # Validation / # Test / …` — shows that `# Test` is the column that actually
  prints 16,281. So the FAIL is precisely what PD003 exists to catch: **the claim was pointed at the
  wrong cell of the right table.** It is a verdict about the claim↔anchor pair, not a claim that the
  paper misprinted anything, and not a claim about the paper's Adult split arithmetic.
- **PD006 @ C2** — the claim's `\citep{rubachev2024tabred}` reference resolves to `table:5`, and
  `table:5` does not print `8`; `8` is printed in `table:4, 7, 9, 11, 14, 15, 16, 17`. FAIL.

Both were reported with exit code 0: the exit code tracks the contract, never the findings.

### Generalization evidence in the same acceptance

Zero TabM-specific adapters were written for PD, RD-side use, ED (beyond its documented `captured`
adapter on the declared surface) or DD; no PD/RD/ED/DD source was modified; the only schema-shaped
input was the ordinary author manifest. The acceptance therefore had to be achievable with the
generic workflow alone, and it was.

## 3. Every UNKNOWN remaining in the chain

These are the gaps as they stand. None is closed by prose; each is a state the tools themselves
produced.

| # | Where | State | Why |
|---|---|---|---|
| U1 | C7 / PD002 | INCONCLUSIVE | the seed universe is declared PARTIAL; an unlisted universe cannot be PASSed |
| U2 | chain-1 / PD003 over the Adult accuracy | NOT REACHABLE | the paper prints per-dataset accuracies in longtables whose source gives no reference name for the printed cell, so no claim can address the mean; the value 0.8575 was not turned into a claim |
| U3 | chain-1 / ED004, ED009, ED010 | INCONCLUSIVE | the repository ships no run-side bundle for the published runs: no effective configuration, no termination cause and no runtime environment is recorded in any artifact |
| U4 | chain-1 / ED `code.dirty` and ED environment fields | THEY DESCRIBE THE CAPTURE, NOT THE PUBLISHED RUN | ED computes the working-tree state before it writes `experiment.lock.json`, so `dirty = False` was true of the cloned tree at capture time and the lock itself is now its one untracked file; the recorded python version and package list (3.13.1, Windows-11) are this machine's, and ED says so itself |
| U5 | chain-1 / DD split sizes vs the printed `# Train` | AUDITOR OBSERVATION, NOT A PD VERDICT | DD measures the official files as train 32,561 / test 16,281 while the paper prints `# Train` 26,048 and `# Validation` 6,513; 26,048 + 6,513 = 32,561, i.e. the printed number is a hold-out of the official train file. PD does not compare across those layers and issues no verdict on it |
| U6 | chain-2 / C2 and C4 | PD006 FAIL / INCONCLUSIVE | the referenced float does not print the counted number, and two of the labels in C4 resolve to no float in the source at all |
| U7 | chain-3 / C9 | INCONCLUSIVE | the merged leading cell makes the declared row address have two readings and the source states nothing that separates them |
| U8 | PD004 across the workspace | NOT_RUN | no claim in this workspace declares a comparative relation over a block-addressed cell, so the rule has no key to read |

Recorded as **SEARCHED / NOT OBSERVED** (hypothesised, looked for, not found — not "absent by proof"):

- a TabM table that both names its float in a sentence and prints a metric value the shipped
  artifacts reconstruct: none found in `main.tex` or `tables/`;
- a run-side artifact inside `exp/` that records the environment a published run executed under:
  none — only `paper/environment.yaml`, which states a requirement, not a fact.

## 4. What this final state does **not** claim

- It does not claim Paper Doctor's findings are scientifically correct in any absolute sense. PD's
  verdicts are mechanical relations between a claim and the anchors in the paper's own artifact;
  `FAIL` ≠ false, unreliable, or fraudulent, and the README says so.
- It does not claim the TabM paper's Adult numbers are wrong. U5 is an auditor observation about
  layers that PD is not designed to compare.
- It does not claim §15 was satisfied. The real human first-use test was waived by the owner and is
  **NOT OBSERVED**; §6 of `release/RELEASE_FREEZE.md` records that as a deviation, never as a pass.
- It does not claim the three P2/P3-class output-schema gaps (N2, N5, N9) are solved; they are
  accepted and listed.
- It does not claim the local wheel/sdist hashes equal the published ones; they do not, and §3 of
  the freeze record shows what does and does not match member by member.

## 5. Closure

Dataset Doctor RELEASED / FROZEN. Experiment Doctor RELEASED / FROZEN. Result Doctor
RELEASED / VERIFIED / FROZEN. Paper Doctor RELEASED / VERIFIED / FROZEN. At least one TabM chain
reaches all four layers with its provenance gaps named rather than papered over.

**Unique next step: stop feature development and observe real external usage.**
