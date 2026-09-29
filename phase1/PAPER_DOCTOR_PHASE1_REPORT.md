# Paper Doctor — Phase 1 Report: Minimal Deterministic Core (CLOSED)

Authority: `phase0/PAPER_DOCTOR_PHASE0_REPORT.md` (frozen body, originally 827 lines, now followed
by the dated **ERRATUM A1–A4** issued 2026-09-29, 79 lines) + the Phase 1 brief
(`MINIMAL DETERMINISTIC CORE IMPLEMENTATION`, 1,131 lines). Phase 1 translated the frozen contract
into code and tests; it reopened no scientific decision. Phase 0 history is not rewritten here.

Status line: **all §28 stop conditions are met.** The four items Phase 1 originally reported as
unresolved contradictions are **RESOLVED BY PHASE 0 ERRATUM** — the erratum accepts all four, and in
every case the delivered implementation already matched the corrected statement, so the resolution
required **zero code change**. Details in §14.

Phase 0 Erratum A1–A4: **ACCEPTED / APPLIED**.
GO for Phase 2: **YES**.

---

## 1. Implemented frozen object model (Phase 0 §14: three new objects, nothing more)

`src/paper_doctor/objects.py` — `Claim`, `FloatAnchor`, `EvidenceLink` are the only new objects.
Everything else is reused or derived: `SourceRef`/`Grade` (`evidence.py`), `RuleStatus`/
`UniverseStatus`/`RuleFinding`/`canonical_json` (`status.py`), `ResultArtifact` (upstream shape minus
`produced_by`, which a `.tex` and a findings JSON do not have).

Supporting enumerations, all closed vocabularies taken from the seven real anchors (closes Phase 0
open register **O-1**: ≤ 6 values each):

| vocabulary | values |
|---|---|
| `ClaimForm` | 6 (`NUMERIC_ATTRIBUTION`, `COMPARATIVE`, `SUPERLATIVE`, `SCOPE`, `QUALIFICATION`, `REFERENCE_ATTRIBUTION`) |
| `Quantifier` | 5 (`all`, `most`, `some`, `bare`, `numeric`) |
| `ScopeUnit` | 3 (`aggregation`, `reported_cell`, `comparison_member`) — non-interchangeable, PD002 declares which one it compared |
| `TargetKind` | 3 (`FLOAT`, `RD_TARGET`, `PROSE`) |
| `LinkBasis` | 3 (`AUTHOR_REF_IN_SENTENCE`, `AUTHOR_NAMED_FLOAT`, `AUDITOR_DECLARED`) — §4: nothing else creates a link |
| `PairingBasis` | 2 (`declared`, `suggested`) — §15: a `suggested` pair can only make PD007 INCONCLUSIVE, never satisfy PD001 |

Nested records carried by a `Claim`: `Qualifier(kind, statement, locator)`, `ScopeDecl(declared_universe,
stated_count, unit, members, universe_status, locator)`, `same_as: ((claim_id, basis), ...)`,
`not_audited_reason` (S7's rhetorical channel).

## 2. Implemented `P_*` validation surface (exactly 12, §7; `P_13` was not invented)

`manifest.py:40-51` freezes `VALIDATION_CODES`; `test_cli.py` re-asserts `len(codes) == 12` and that
the message shape is `"{code} at {where}: {problem}"` with exit 2. Invalid input is never repaired.

| code | what it rejects (observed hazard) |
|---|---|
| `P_YAML` | the file is not parseable YAML |
| `P_TOP_LEVEL` | top level is not a mapping; sections missing/mis-ordered; upstream payload is not the `audit --json` array |
| `P_SCHEMA_VERSION` | `schema_version` is not 1 |
| `P_UNKNOWN_KEY` | any key outside the frozen field list (a manifest cannot smuggle in a new object) |
| `P_TYPE` | wrong field type; unknown enum text; `INFERRED` as a link grade ("a suggestion is not a link"); a claim paired with itself |
| `P_NOT_A_NUMBER` | a count declared as `three` or `null` |
| `P_MISSING_FIELD` | required field absent; empty claim text; an upstream finding lacking an indexed key |
| `P_DUPLICATE_ID` | duplicate `claim_id`/`link_id`/`float_id`; duplicate upstream `(rule_id, target)` |
| `P_UNRESOLVED_REF` | paper/ artifact file absent; declared digest or size ≠ observed; claim text not on the declared line; a locator in the preamble/macro body (FM-P11); unknown `same_as`/`links`/label target; `paper.root` not a directory |
| `P_CONFLICTING_REF` | a declared float number disagrees with the document's own numbering; declared kind ≠ resolved kind; two links of one claim resolving to different floats |
| `P_LOCATOR_KEYS` | a locator's key set is not one of the four frozen families (`[path,column,row]`, `[path,key]`, `[path,line]`, `[path,line,text]`, plus `[path,text]`) |
| `P_PATH_OUTSIDE_ROOT` | any declared path escaping the audit root (`..` or an absolute escape) |

## 3. LaTeX float-index oracle results (exact, §28 condition 1)

`latex_index.py` implements the deterministic subset only: `\input` flattening with absolute line
anchoring, four float environments, label→number by source order, ref sites, caption presence,
unterminated-float detection, nesting depth. `test_latex_index_oracle.py` (15 tests) pins the
frozen oracle against the read-only corpora:

* GMMVI `arxiv.tex`: **9 tables / 3 figures**, nesting depth 1, 0 unterminated, `body_found`,
  `tab:exp1` → **table 2**, `tab:exp1_eval` → **table 3** (`begin_line == 430`), 114 ref sites,
  95 unresolved, `never_referenced_labels == ("tab:exp3_accuracy",)`.
* FM-P11: the 32 `math_commands.tex` macro-definition sites are excluded from claim-eligible body
  text; the remaining 82 sites are all in `arxiv.tex` and none targets a `#`-command.
* C1's mechanism, proved at the index layer: `"78.69" in body(table 2)` and `not in body(table 3)`,
  with the `\ref{tab:exp1_eval}` site at `arxiv.tex:426` resolving to table 3.
* RTDL `main.tex`: **23 tables / 2 figures**, 25 flattened chunks (`data/table_ablation.tex` etc.
  inlined in document order), `tab:neural-networks` → 2, `tab:datasets` → 1, `tab:node` → 3,
  `tab:nn-gbdt` → 4, `tab:ablation` → 5.

## 4. Result Doctor JSON integration contract (Contract I-1)

`rd_findings.py` is the sole reader of the single upstream artifact; `audit.py` is its only caller.

* clause 1 — zero runtime import of `result_doctor`; enforced by test (row 1 of the firewall scans
  every module in the package for model/network tokens and `import result_doctor`).
* clause 2 — declared `sha256` and `size` are verified against the observed bytes **before** a
  finding is read; a mismatch is `P_UNRESOLVED_REF` (exit 2), never a warning.
* clause 3 — findings are indexed by exactly the 8 frozen keys; `SourceRef` keys outside the
  `EVIDENCE_KEYS` list raise `P_LOCATOR_KEYS`.
* clause 4 — a closed measurement **read-list**; asking for a key outside it raises instead of
  silently widening what PD reads from upstream.
* clause 6 — upstream `SourceRef`s propagate into PD evidence, so a finding names the file RD
  actually looked at.
* clause 7 — one-way dependency: PD never calls an RD rule, never rebuilds an RD bundle, never
  re-audits an RD finding.
* derived exclusion universe = `rule_id == "RD002" AND n_exclusions > 0` **read off upstream
  measurements**; over the frozen GMMVI artifact this is exactly **7 targets / 34 exclusions** with
  `n_exclusions_listed == n_exclusions` on all 7 (asserted against the real file, not a fixture).

## 5. NaN handling

RD's canonical JSON is Python-legal and strict-JSON-illegal: a bare `NaN` may appear in a
measurement. `json.loads(..., parse_constant=...)` maps it to the `NonFinite` sentinel — never
coerced to `0.0`, `""` or `False`, never compared numerically, `==` only against another `NonFinite`
with the same literal. A `NonFinite` in a contracted read means UNKNOWN: the rule that would have
used it reports `INCONCLUSIVE` rather than inventing a value. PD never rewrites the upstream file to
make it finite. Covered by `test_rd_findings_contract.py` (16 tests).

## 6. PD001–PD007 implementation

`rules.py` (1,565 lines) holds `RULE_IDS`, frozen `NAME`/`QUESTION` tables, and one `evaluate()` per
rule. Every finding is built by `_f()`, so a PD finding and an RD finding serialize alike.

| rule | question (frozen) | mechanism actually implemented |
|---|---|---|
| PD001 Evidence Traceability | is the declared support reachable? | each link's mechanical existence test (float resolves & is terminated / upstream `(rule_id,target)` present / prose path exists under the root). No link ⇒ INCONCLUSIVE ("untraceable is not false") |
| PD002 Evidence Scope Consistency | does the stated scope match the evidence's scope? | count compared per declared `ScopeUnit` against `_CERTIFYING_RULE` (`aggregation`/`comparison_member`→RD002 `n_members`, `reported_cell`→RD005 `n`); selection by verbatim `spread_label == claim.text`, else the claim's declared `(rule_id,target)` links — never by proximity; PASS requires every bound target upstream PASS **and** universe RECOVERED; PARTIAL ⇒ INCONCLUSIVE; divergence with uncertified upstream ⇒ INCONCLUSIVE |
| PD003 Quantitative Claim Consistency | does the printed value agree with the claimed one? | string-literal comparison of the claim's own numbers against the named cell (`[path,column,row]`) or the referenced float body; requires matching declared quantity identity, and a declared precision semantics for any non-equal closeness |
| PD004 Comparison Consistency | does the stated direction hold column by column? | grid rows addressed by label, columns scoped by the declared `comparison_basis` (`per_column` / `all_columns` / `columns=…` / `named_column=…`), direction from `\textdownarrow`/`\textuparrow` or the float's `quantity_declaration`; universals need zero counterexamples, existentials need one supported column; an unclassified intensifier (`clearly`, `significantly`, …) ⇒ INCONCLUSIVE with no threshold invented |
| PD005 Qualification Consistency | does the qualification cover the evidence? | claim's declared members vs the derived upstream exclusion universe; list valid iff `n_exclusions_listed == n_exclusions` **and** `member_rule_grade ∈ {DIRECT, DERIVED}`; no second exclusion mechanism exists |
| PD006 Reference Consistency | does the reference name the float that carries the value? | `\ref`/`\autoref`/`\eqref` labels resolved through the index; named floats (`Table 2`) checked against numbering; literal-presence test in the referenced body; resolution grade is DERIVED |
| PD007 Cross-Section Consistency | is one claim represented consistently? | pairs by declared `same_as` (target `A|B`); compares predicate, subjects and `_scope_signature`; a `suggested` pairing can only yield INCONCLUSIVE |

`audit.py` adds the entry layer's `NOT_RUN` records from `DRIVING_CLASS`, so "no target of this class
was supplied" is distinct from INCONCLUSIVE (evidence insufficient), NOT_APPLICABLE (no such
relation) and "you did not ask me" (a rule outside the requested set emits nothing at all).

## 7. S1–S13 status matrix (`test_adversarial_matrix.py`, 13 tests, all green)

| case | shape | asserted pair of statuses |
|---|---|---|
| S1 | everything supported (numeric + scope + comparison, `\autoref` in sentence, cells string-equal, RD002 PASS) | PD001 PASS · PD002 PASS · PD003 PASS · PD004 PASS · PD006 PASS |
| S2 | prose number ≠ printed cell, same declared quantity, declared precision | PD003 FAIL · PD001 PASS |
| S3 | evidence covers 7 of 9, claim says "all" | PD002 FAIL **and** PD005 FAIL (never one alone) |
| S4 | no resolvable link | PD001 INCONCLUSIVE · every other rule INCONCLUSIVE/NOT_APPLICABLE, never FAIL |
| S5 | value exists but in another float (the C1 shape) | PD006 FAIL · PD003 INCONCLUSIVE |
| S6 | evidence carries an exclusion the wording omits | PD005 FAIL · PD002 PASS (qualification ≠ scope) |
| S7 | rhetorical claim, no object | PD001 NOT_APPLICABLE carrying `not_audited_reason` · no FAIL anywhere |
| S8 | downstream RD001 FAIL for the quoted cell | PD003 INCONCLUSIVE with propagated reason (no PASS, no double FAIL) |
| S9 | two identical printed values, both bold, different rows | PD004 INCONCLUSIVE — RD007 owns marks; PD does not eat RD's work |
| S10 | "improves by 2.1" where the printed accuracy is 85.1 | PD003 FAIL · PD002 PASS |
| S11 | two `same_as` claims with different scopes | PD007 FAIL · PD004 PASS (drift is cross-section, not support) |
| S12 | declares ten seeds, RD002 PASS confirms 10, but 3 excluded | PD002 FAIL **and** PD005 FAIL |
| S13 | "some datasets (A, B, C)" where D also qualifies | PD002 PASS · PD005 PASS (existential enumeration may omit) |

Special §16 guards S1, S7, S9, S13 all hold as frozen.

## 8. 14 firewall results (`test_pd_firewall.py`, 43 tests, all green)

Rows 1–14 of Phase 0 §19 are each a failing-if-broken test, none weakened:
row 1 (no model/network import anywhere in the package; a `suggested` pairing never reaches a verdict;
the link-basis vocabulary has no inference member) · row 2 (closeness is not a PASS; a value found by
searching is not a link; an artifact with nothing in it creates no links) · row 3 (a similarly named
file is not the declared one) · row 4 (the float next to the sentence is not the support) ·
row 5 (an explicit link unlocks judgment, not agreement) · row 6 (an upstream failure is never
overwritten) · row 7 (an undecided upstream count supports neither PASS nor FAIL) · row 8 (every shape
of missing evidence stays INCONCLUSIVE) · row 9 (a broken contract exits 2 instead of emitting
findings; the CLI keeps the two kinds of "bad" apart) · row 10 (no number about the paper as a whole
anywhere in the output surface) · row 11 (no decision about the paper itself — parametrized forbidden
vocabulary) · row 12 (no novelty or literature-truth judgment) · row 13 (no accusation anywhere;
PD006 keeps its frozen referential name) · row 14 (a PDF root gets no index and no guess; no surface
exists for a theorem or a proof; an unreadable cell topology is UNKNOWN, not assigned).

## 9. GMMVI real acceptance (`test_acceptance_gmmvi.py`, 12 tests, all green)

Audited in place: `paper-doctor.yml` points at the read-only corpus `phase0/sources/2209.11533v2.tex`
and the frozen artifact `tests/fixtures/rd_findings_gmmvi_0.1.0.json`; nothing was copied or rewritten.

| anchor | rule | status | what the output says |
|---|---|---|---|
| C1 `arxiv.tex:426` | PD006 | **FAIL** | "the reference resolves to table:3, which does not print 78.69; it is printed in table:2" |
| C1 | PD001 | PASS | the in-sentence reference resolves (the link is real; its target is the contradiction) |
| C1 | PD003 | INCONCLUSIVE | no cell address declared; the mismatch is reported once, by PD006 — no double FAIL |
| C5 `arxiv.tex:625` (unit=aggregation) | PD002 | **INCONCLUSIVE** | "2 of 46 compared targets differ from the stated 10 … but upstream is INCONCLUSIVE, so the count is not certified" |
| C5 (additional unit=reported_cell view) | PD002 | INCONCLUSIVE | "12 of 56 compared targets differ from the stated 10"; selection fell back to declared links because `spread_label` ≠ the paper's sentence |
| C6 | PD005 | **FAIL** | names `sepyrux` **and** `zamtrux` next to the declared `sepyfux`; universe = 7 targets / 34 exclusions |
| C6 | PD002 | NOT_APPLICABLE | "the claim states no count … its enumeration of 1 member(s) is PD005's relation" |
| C10 / C11 / C12 | — | not emitted | RD-owned (§15); the test asserts no `RD*` rule id and no C10–C12 target appears anywhere |

Every censused number above was recomputed inside the test file straight off the frozen artifact
(46 RD002 targets, 2 with `n_members ≠ 10`; 56 RD005 targets with a `spread_label`, 12 with
`n ≠ 10`; 7 RD002 targets with `n_exclusions > 0`, 34 exclusions listed) — not read back from a
finding.

## 10. RTDL real acceptance (`test_acceptance_rtdl.py`, 17 tests, all green)

Audit root is `F:/MLResearch` because D1/D2 quote the pilot README, which lies outside the paper
directory; the paper, its `data/*.tex` cells and the README remain read-only.

| anchor | rule | status | evidence |
|---|---|---|---|
| D1 README `:82` (`-0.499` vs Table 2 CA/MLP `0.499`) | PD003 | **INCONCLUSIVE** | `delta 0.998`, `identity_basis = declared identities disagree (['metrics.test.score'] vs '\textdownarrow ~ RMSE, \textuparrow ~ accuracy')`, "closeness is not a PASS". Never PASS, never FAIL — §14's frozen epistemic boundary holds |
| D1 | PD001 | PASS | the cell and the float are both on file; only the semantics are missing |
| D2 README `:70` (quantifier `all`, no number) | PD002 / PD001 | NOT_APPLICABLE / PASS | PD refuses to invent a count |
| D3-SUBSET (`RECOVERED` over the 2 modeled aggregations) | PD002 | **PASS** | both upstream RD002 PASS with `n_members = 15` |
| D3-TABLE (`PARTIAL` over Table 2's 11 datasets) | PD002 | **INCONCLUSIVE** | "the counts agree … but the universe is PARTIAL: an unlisted universe cannot be PASSed" |
| D5 clause 1 `main.tex:364` | PD004 | **FAIL** | 11 columns in scope, 9 supported, 1 counterexample (YE 8.751 vs 8.716, down is better), 1 printed tie (AD 0.86 = 0.86) |
| D5 clause 2 ("significantly reduced") | PD004 | **INCONCLUSIVE** | "'significantly' has no declared test or threshold"; no margin invented, `n_columns_in_scope = 0` |
| D6 `main.tex:465` | PD004 | **FAIL** | 8 columns, 7 supported, 1 counterexample (YE 8.855 vs 8.843) |
| D7 `main.tex:409` | PD002 | INCONCLUSIVE (**never FAIL**) | "nothing declares which upstream targets this scope covers" — §10's false-FAIL guard |
| D7 | PD001, PD006 | PASS | `\autoref{tab:nn-gbdt}` resolves by the document's own numbering (DERIVED) |
| D8 `main.tex:590` (700 vs printed 699) | PD003 | **INCONCLUSIVE** | `delta 1.0`, `identity_basis = undeclared`, "closeness is not a PASS" |
| D11 abstract `:95` vs conclusion `:499` | PD007 | **FAIL** | target `D11-ABS|D11-CON`, `pairing_basis = ('declared',)`, scopes `universe=other solutions;…` vs `universe=other DL solutions;…` |
| D11 | PD001 / PD004 | INCONCLUSIVE / NOT_APPLICABLE | unlinked, so untraceable — not false |

## 11. RD/PD non-overlap verification (§15)

Ownership tests rather than duplicated rules: the acceptance suites assert that PD's output contains
only `PD001`–`PD007` ids; that C10/C11/C12 (and RD's `quantity:STM300/sepyfux/-elbo`,
`BreastCancer/samtron/-elbo/Table 5`) appear in no PD target; that PD005's exclusion universe equals
RD002's own `n_exclusions` records (no PD-side recomputation); that S9/S6 keep marks (RD007) and
mechanics (RD001/RD004) out of PD's reach; and that an upstream FAIL/INCONCLUSIVE caps a downstream
PD rule at INCONCLUSIVE instead of being overwritten (rows 6–7, S8). Runtime import count of
`result_doctor` = **zero** (§28 condition 10), machine-checked by row 1.

## 12. Deterministic output check (`test_canonical_bytes.py`, 8 tests, all green)

* Two audits of one manifest → identical `canonical_json`; the written file has no `b"\r"`, ends in
  exactly one `\n` (`write_json(..., newline="\n")`).
* The payload is a fixed point of its own canonicaliser (sorted keys at every depth, `(",", ":")`,
  `ensure_ascii=False`).
* Exactly the 8 finding keys; no volatile key (`timestamp`, `date`, `pid`, `seed`, `host`, …) at any
  depth; the same paper from two different checkout directories produces identical bytes.
* Non-ASCII stays literal UTF-8 (a typographic minus appears as `−`, not `\u2212`).
* Cross-process: the same manifest audited in three fresh interpreters with `PYTHONHASHSEED` 0, 1 and
  424242 yields identical bytes — no finding text depends on `set` iteration order.
* `render_text` (the CLI face) is stable too, and the CLI's `--json` bytes equal
  `canonical_json(audit_manifest(...))` verbatim (no CLI/API drift).

## 13. Quality gates (§26)

```
pytest -q                196 passed, 0 failed, 0 skipped, 0 xfail   (7.0 s)
ruff check .             All checks passed!
ruff format --check .    25 files already formatted
mypy                     Success: no issues found in 10 source files
```

Per file: acceptance_gmmvi 12 · acceptance_rtdl 17 · adversarial_matrix 13 · audit_end_to_end 9 ·
canonical_bytes 8 · cli 7 · latex_index_oracle 15 · manifest_validation 35 · pd_firewall 43 ·
rd_findings_contract 16 · rules_unit 12 · tabular_grammar 9.

Required-fixture loading is fail-fast, never skipped: `support.corpus_lines()` raises
`FileNotFoundError` for a missing read-only corpus and the fixtures module raises for a missing
frozen artifact, so a silently absent pilot paper cannot turn a test green.

### 13.1 Erratum reconciliation closure pass (2026-09-29, same day, after ERRATUM A1–A4)

Targeted run over the eight adjudicated surfaces — C5, D7, D6, the table-numbering/locator oracle,
D1, C1, PD005's 7-target/34-exclusion universe, and the certainty-monotonicity firewall rows 6 and 7
— **28 passed**. Then exactly one full closure pass, unchanged from the numbers above:
**196 passed / 0 failed / 0 skipped**, `ruff check` **All checks passed!**, `ruff format --check`
**25 files already formatted**, `mypy` **Success: no issues found in 10 source files**.

Machine-verified frozen invariants, re-checked after the erratum rather than asserted from memory:

| Invariant | Measured |
|---|---|
| exactly 7 PD rules | `RULE_IDS == PD001…PD007` → 7 |
| exactly 12 `P_*` codes | 12 module constants, set-equal to `VALIDATION_CODES`; no `P_13` |
| S1–S13 green | 13 row tests collected and passing (`test_s1`…`test_s13`) |
| 14 firewall rows green | 14 distinct `test_row1…test_row14` across 43 passing firewall tests |
| D1 remains INCONCLUSIVE | asserted `never PASS or FAIL`, passing |
| C1 remains a deterministic PD006 FAIL | asserted with `resolved == ("tab:exp1_eval -> table 3",)`, passing |
| PD005 remains 7 targets / 34 exclusions | `n_universe_targets == 7`, `n_in_scope == 7`, listed total 34, passing |
| runtime `result_doctor` imports = 0 | regex census over all 10 `src/paper_doctor/*.py` import statements → **0** |
| canonical output deterministic | 8 `test_canonical_bytes` tests, incl. 3 subprocesses at `PYTHONHASHSEED` 0/1/424242 → identical bytes |
| no oracle weakened for green tests | **`src/` has zero writes this round** — newest source file is `rules.py` at 04:28, while the erratum edits landed at 10:38–10:42 and touched only the two reports plus four test docstrings; test count identical (196) before and after |

The last row is the load-bearing one: A1 and A2 retired *expectations that were stricter than the
frozen evidence surface can support*, and the delivered implementation was already the conservative
behaviour. Applying the erratum therefore removed no assertion and lowered no status ceiling.

## 14. Deviations from Phase 0 — register (A: RESOLVED BY PHASE 0 ERRATUM · B: implementation disclosures)

Phase 1 filed ten items under §28 — four oracle-text contradictions (A) and six implementation
observations (B) — under the instruction "report the minimal contradiction; do not silently
redesign". The Phase 0 design authority has since ruled on the four oracle-text items: the dated
ERRATUM appended to `phase0/PAPER_DOCTOR_PHASE0_REPORT.md` (2026-09-29) **accepts A1–A4**. They are
therefore no longer unresolved contradictions. In all four cases the delivered code already matched
the corrected statement, so **applying the erratum changed no source line and no test assertion** —
only the stale *prose* expectations and the six test docstrings that quoted them (reconciliation task
§3: remove stale expectations, no broader cleanup). None was resolved by weakening a scientific oracle.

**A. RESOLVED BY PHASE 0 ERRATUM — accepted and applied; zero implementation change.**

1. **A1 · C5 = PD002 `INCONCLUSIVE` (was: expected FAIL).** Confirmed on the reason Phase 1 gave and
   the erratum adopted: RD002 is INCONCLUSIVE on **all 46** aggregations on the frozen Contract I-1
   surface, and certainty monotonicity forbids upgrading that to a determinate FAIL. The old
   "9 / 46 aggregations with n ≠ 10" is now labelled a **RESEARCH-ROUND OBSERVATION** — its surface is
   `phase0/work/agg-n-census.txt` reading `spread_form.n`, a key **not** on the I-1 read-list, so no
   downstream rule may compute it. I-1 was **not** extended to recover the old verdict. The numbers
   PD002 emits stay unit-labelled as they always were: **2 of 46** (`unit=aggregation`, from
   `RD002.measurements.n_members`) and **12 of 56** (`unit=reported_cell`, from
   `RD005.measurements.n`).
2. **A2 · D7 = PD001 PASS + PD006 PASS + PD002 `INCONCLUSIVE` (was: a single "D7 PASS").** A rule
   vector, not a verdict, and it is not collapsed into an overall claim judgement. No admissible
   target carries a per-dataset `comparison_member` count and RD007 is NOT_RUN on zero comparison
   sets; the existential PASS remains pinned synthetically in S13.
3. **A3 · D6 `FAIL` on 1 of 8 columns, 7 supported (was: "2/8"; status FAIL unchanged).**
   `0.727` is the **HI** column, not JA; bold-mark arithmetic is RD-owned (FM-P10/RD007) and was not
   borrowed to restore the old count. PD004 semantics unchanged, as the erratum requires.
4. **A4 · `main.tex:375-376` is Table 3's caption (was: labelled Table 2).** Locator/numbering only,
   no rule semantics change. The machine oracle `RTDL_TABLES` already pins
   `(2, 335, tab:neural-networks)` and `(3, 367, tab:node)`, and Table 4 begins at 390, so 375–376
   lies inside Table 3 by the deterministic index — the index, not the prose, was right; the
   Phase 1 table-numbering test needed no edit.

**RESOLVED BY PHASE 0 ERRATUM — A5, issued with the Phase 2 brief.** Phase 0 §10's D2/D3 row
(line 274) expected "adult/aloi/CA PASS … universe PARTIAL **3/11**", while the frozen RTDL
artifact models **2** aggregations (`aloi` has no upstream `RD002` target). This is the same evidence
surface class as A1 — re-computed raw `output/{...}/mlp/tuned/*` runs, not a Contract I-1 key. A5
now freezes the executable statement as **Contract-I-1 universe count = 2, `unit = aggregation`**,
relabelling `3/11` as a research-round census exactly as A1 relabelled `9/46`, and expands I-1 for
neither. Zero implementation change, as A5 records: the delivered tests already asserted
`n_targets_compared == 2` with `universe_status == "RECOVERED"` on the subset and `"PARTIAL"` on the
whole printed table.

**B. Implementation deviations, disclosed.**

5. `PD004`'s FAIL reason now quotes the declared predicate instead of conjugating it
   ("the declared relation 'outperforms' fails: FT-Transformer vs NODE on 1 of 11 columns …"), because
   the frozen `"{first} does not {predicate} {second}"` template printed "does not outperforms" /
   "does not is superior to" on both synthetic and real corpora. Text-only; no status changed; no test
   asserted the old string.
6. `PD001`'s PASS reason prints **distinct** link bases; `measurements["link_basis"]` still records
   one entry per link (46 × `AUDITOR_DECLARED` rendered as one repeated word otherwise). Text-only.
7. A second claim object (`C5-CELLS`) was added for the same caption at `unit=reported_cell`. §14 says
   "Do not convert this to a cell-level census"; the aggregation-level anchor is present and judged on
   its own, so the cell view is additive, not substitutive. Recorded as an interpretation, with the
   stricter reading noted here for the human to overrule.
8. PD005's `_unnamed_exclusions` label picks a boilerplate token ("aggregation") out of real target
   ids, so the reason's headline word is weak; the mandated names (`sepyrux`, `zamtrux`) are present in
   the appended `target (n)` list. Token selection was **not** redesigned (§16 forbids regenerating
   expectations from the implementation).
9. Two-root input: D1/D2 need `_registry.paper.root = F:/MLResearch`, since no directory contains both
   `main.tex` and the pilot `README.md`. README locators are not LaTeX chunks, so FM-P11's
   preamble rule does not apply to them — an observation about the contract, not a change to it.
10. `pyproject.toml` `[tool.ruff] extend-exclude` still names the non-existent
    `tests/generic_fixtures`; harmless, stale, left untouched to keep the diff minimal.

## 15. Unresolved limitations

* Neither pilot exercises PD002's `spread_label == claim.text` binding: upstream normalises the
  sentence (`3σ confidence intervals …`) while the paper writes `$3\sigma$ …`, so caption→cell binding
  must be declared as explicit `RD_TARGET` links. That is the conservative behaviour §4 wants, but it
  means real authors must hand-enumerate targets (46/56 in the GMMVI case).
* PD004 cannot judge RTDL's Table 4 uniquely: repeated row labels (`FT-Transformer`, `XGBoost`,
  `CatBoost` appear in both the default and tuned blocks) and dropped `\multicolumn` group headers
  leave no addressable row key. D7's comparison therefore goes through PD002/PD006 only.
* PD003 PASS has never been observed on a real paper: it needs an author-declared quantity identity
  that neither pilot supplies outside a caption (Phase 0 §23 said the same). Both real numeric anchors
  (D1, D8) stop at INCONCLUSIVE by design.
* Authoring cost (Phase 0 open register **O-3**, measured on RTDL's 8 anchors → 11 claim objects):
  per claim 1 locator + 1 form + 0–2 links, and for the two cell-level anchors a hand-typed
  `[column,row]` address read off the `.tex` by eye. The 46-link C5 case is pure key enumeration and
  cannot be written by hand — it was generated in the test from the frozen artifact.
* No CLI-side authoring help exists (a manifest is written by hand, §22 forbade polish).
* Scope honesty: the tool's output is per-rule findings and a status census. There is still no way to
  answer "how trustworthy is this paper", and §10 forbids inventing one.

## 16. Phase 2 exact scope recommendation

One sentence: **complete the claim universes of the two pilot papers with the machinery as frozen, and
fix the single addressing gap that blocked a real table.** Concretely, and nothing else:

1. Addressable row identity for repeated row labels — a deterministic block discriminator taken from
   the table's own group structure (`\multicolumn` headers / rule-separated blocks), so RTDL Table 4
   and GMMVI Table 8 become judgeable by PD004. No new object, no new rule, no new `P_` code.
2. Audit the **remaining ledger rows** of both pilots (GMMVI C2–C9 and RTDL's other 12 claim rows from
   the Phase 0 traces) through the same acceptance harness, and publish the authoring-cost census per
   claim class. This closes O-3 properly and is the evidence for whether a manifest drafting aid is
   justified — which Phase 2 must **not** build before that measurement exists.
3. Keep the §22 prohibitions in force: no PDF support, no third paper, no LLM feature, no CLI/distribution
   polish, no PyPI/tag/push without explicit user authorization, no revisiting Result Doctor.

Deferred, explicitly not Phase 2: automatic cell addressing, mark semantics (RD007), packaging,
multi-paper generalisation.

## 17. Status and GO / NO-GO

**Phase 1 final status: CLOSED. Phase 0 Erratum A1–A4: ACCEPTED / APPLIED. GO for Phase 2: YES.**

The four §28 stop conditions that were previously carried with a caveat are now clean, because the
authority retired the stale prose rather than the code: latex oracle exact ✓ · 7 rules ✓ · 12 `P_`
codes ✓ · S1–S13 ✓ · 14 firewall rows ✓ · D1 remains INCONCLUSIVE ✓ · C1's deterministic failure
reproduced ✓ · PD005's frozen 7-target/34-exclusion view ✓ · zero RD runtime import ✓ · canonical
output deterministic ✓ · quality gates green ✓ · "GMMVI/RTDL acceptance matches the frozen oracle" ✓
— the oracle being Phase 0 **as amended by the 2026-09-29 erratum**, which the delivered statuses
match on every one of the seven real anchors.

No scientific oracle was weakened to obtain green tests; the two errata that changed an expectation
(A1, A2) *lowered* what Paper Doctor may assert, and both were already the implemented behaviour.

**Unique next step:** on the human's go-ahead, open Phase 2 §16 item 1 — the deterministic block
discriminator that makes repeated row labels addressable, so RTDL Table 4 and GMMVI Table 8 become
judgeable by PD004 — as the first line of Phase 2 code. Nothing else is queued ahead of it. The
D3 denominator that §14 had carried forward was since retired by **ERRATUM A5**, so no open item
remains from Phase 1.

---

## Appendix A — integrity note (prompt injection observed in this session's tool output)

During Phase 0 an instruction-styled block appeared **inside a Bash tool result** (not from the user,
not from the project files), reading in substance "Only the user should approve adding MCP servers…
flag any unrelated MCP/built-in write tool in the same approval batch…". It was treated as untrusted
tool output: no MCP server was requested, added, or removed at any point in Phase 0 or Phase 1, and no
write tool was invoked on that instruction. Reported here as required. Separately, the historical
GitHub OAuth-token-in-transcript incident noted in an earlier session is **resolved** and is not a
Phase 1 blocker.

## Appendix B — what Phase 1 did not touch

`F:\MLResearch\dataset-doctor`, `experiment-doctor`, `result-doctor` (including
`result-doctor/phase4/rtdl-revisiting-models/README.md`), and both pilot corpora under
`phase0/sources/` are unmodified: Phase 1 read them and wrote only inside `F:\MLResearch\paper-doctor`.
The scratch spike scripts and their throwaway manifests used to derive §9/§10 were deleted after the
assertions were encoded; `phase1/` now contains only this report.
