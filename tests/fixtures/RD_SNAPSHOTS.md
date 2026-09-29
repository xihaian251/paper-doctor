# Frozen upstream snapshots used as test inputs

These files are the bytes of real `result-doctor audit … --json` output from Result Doctor
**0.1.0** (tag `v0.1.0`, released and frozen). Paper Doctor reads them as its single external
input and never imports `result_doctor` to regenerate them (Contract I-1 clause 1).

| file | sha256 | bytes | findings | provenance |
|---|---|---|---|---|
| `rd_findings_gmmvi_0.1.0.json` | `f392709e29e3a9b2d7dddd430f9f942d02f2c0ad87837c7bdb7d17495af6ffce` | 584900 | 538 | GMMVI run directory from Experiment Doctor's GMMVI phase 0 archive, audited with the released RD 0.1.0 API (`load_gmmvi_bundle` + `evaluate` + `canonical_json`), one-off snapshot step run outside the Paper Doctor test suite |
| `rd_findings_rtdl_0.1.0.json` | `2ad02c8fb6ace0af325c2bc50c08eb9f0162e77b25c659e96951df96f694a660` | 13395 | 16 | RTDL project, RD 0.1.0 CLI `audit --json` export; the same digest is recorded in Result Doctor's `release/RELEASE_ARTIFACT_MANIFEST.txt:53` |

Censuses, asserted in `tests/test_rd_findings_contract.py` so that a silent change of bytes
fails the suite instead of drifting:

- GMMVI: PASS 165 / INCONCLUSIVE 293 / NOT_APPLICABLE 69 / FAIL 11; RD002 = 46 findings, all
  INCONCLUSIVE; exclusion universe (`n_exclusions > 0`) = 7 targets, 34 exclusions, all fully
  listed with `member_rule_grade: DIRECT`.
- RTDL: PASS 6 / INCONCLUSIVE 6 / NOT_APPLICABLE 3 / NOT_RUN 1, the NOT_RUN being
  `RD007 / rule:RD007` because the upstream `comparison_sets` section was empty; two
  `RD001.recomputed_dispersion` measurements are bare `NaN`, which is the §9 NaN case.

Regenerating either snapshot is a deliberate, recorded act: run the RD 0.1.0 CLI, copy the
JSON, update this table. A test that imports `result_doctor` is a contract violation.

## One vendored text fixture, and why it is here

| file | sha256 | bytes | provenance |
|---|---|---|---|
| `rtdl_pilot_README.md` | `50f7994f73937093c01412164e07142d198c000fcb69a01041c7404552ca0215` | 13162 | The RTDL pilot transcript written by Result Doctor's own Phase 4 run, copied verbatim out of that project's phase-4 directory. It is not an RD artifact and not paper text; `tests/test_acceptance_rtdl.py` reads two sentences from it (D1's `california_housing   -0.499` line, D2's quantifier sentence), located by line number. |

This file is vendored rather than fetched because it is not on any public host. Before Phase 3's
release audit the test resolved it through a sibling checkout one directory above the repository, which
is why 17 frozen RTDL anchors errored in a fresh clone; `test_every_input_this_test_reads_is_inside_the_repository`
now forbids that, and `test_the_pilot_transcript_is_the_bytes_the_anchors_were_read_from` pins the bytes
so a silent edit fails loudly. Vendoring it changes no anchor: the statuses asserted are the same
because the sentences read are the same bytes.
