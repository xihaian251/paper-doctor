# Changelog

## 0.1.0

First public release. Everything below exists and is tested; nothing else does.

* **What it audits** - one declared relation between one LaTeX paper claim and the reported evidence
  it points at: `paper claim -> reported evidence consistency`. Not the paper's truth, not fraud,
  not novelty, not acceptance, not theorem correctness, not the world.
* **Three objects, one contract** - `Claim`, `FloatAnchor`, `EvidenceLink`, written by a human in
  `paper-doctor.yml`. Links are only ever `AUTHOR_REF_IN_SENTENCE`, `AUTHOR_NAMED_FLOAT` or
  `AUDITOR_DECLARED`: Paper Doctor never infers that two names, numbers or methods refer to the same
  thing.
* **PD001-PD007** - seven rules, one per claim-to-evidence question, each reporting per target as
  `PASS | FAIL | INCONCLUSIVE | NOT_APPLICABLE | NOT_RUN`. No score, no verdict, no aggregation.
* **Upstream evidence from one place** - a `result-doctor audit --json` artifact, read verbatim,
  hash-verified, and never re-audited. An uncertain upstream finding cannot be promoted here.
* **Table structure, not table semantics** - repeated rows are addressed by the source structure that
  separates them (`\multicolumn` group headers, midrules, vertically merged leading cells) and numbers
  are compared as printed, at the precision the author declares.
* **Manifest as contract** - a manifest that is not readable as a contract is refused with one of 12
  frozen `P_*` codes, a field path, and the smallest fix. Nothing is repaired silently.
* **CLI** - `paper-doctor audit PATH` prints one block per finding in canonical order with a status
  census; `--json` writes the same findings as byte-deterministic canonical JSON. Exit `0` whenever
  the audit ran (including on a `FAIL`), `2` for an unreadable contract or an unusable path, `1` for
  a tool failure.
* **Packaging** - Python >= 3.11, one runtime dependency (PyYAML), Apache-2.0, console script
  `paper-doctor`, importable package `paper_doctor`. No network access, no PDF input, no bibliography
  verification.
* **Validated on** - an unseen end-to-end acceptance on TabM (ICLR 2025) across all four layers
  (Paper Doctor -> Result Doctor -> Experiment Doctor -> Dataset Doctor) with zero project-specific
  adapters, plus the two Phase 1 research archives (RTDL, GMMVI) whose frozen anchors still hold.
  Paper-source corpora are not vendored: `scripts/fetch_acceptance_inputs.py` rebuilds them from
  arXiv against pinned digests.
