"""Contract I-1 as tests: verification, the measurement read-list, and the NaN policy.

`tests/fixtures/rd_findings_*.json` are frozen snapshots of real `result-doctor audit
--json` output from Result Doctor 0.1.0 (see `tests/fixtures/RD_SNAPSHOTS.md`). They are
the upstream files themselves, not hand-written fixtures: the PD005 exclusion predicate
and the 538-finding baseline must be asserted against them, and Paper Doctor never
imports `result_doctor` to recreate either.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from paper_doctor.manifest import ManifestError
from paper_doctor.rd_findings import (
    MEASUREMENT_READ_LIST,
    NonFinite,
    OutsideReadList,
    is_non_finite,
    load_rd_findings,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
GMMVI = FIXTURES / "rd_findings_gmmvi_0.1.0.json"
RTDL = FIXTURES / "rd_findings_rtdl_0.1.0.json"

#: sha256 recorded when the snapshots were taken from the frozen RD 0.1.0 output.
GMMVI_SHA = "f392709e29e3a9b2d7dddd430f9f942d02f2c0ad87837c7bdb7d17495af6ffce"
RTDL_SHA = "2ad02c8fb6ace0af325c2bc50c08eb9f0162e77b25c659e96951df96f694a660"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"frozen upstream snapshot missing: {path}")
    return path


@pytest.fixture(scope="module")
def gmmvi():  # type: ignore[no-untyped-def]
    path = _require(GMMVI)
    return load_rd_findings(path, expected_sha256=_digest(path), expected_size=path.stat().st_size)


@pytest.fixture(scope="module")
def rtdl():  # type: ignore[no-untyped-def]
    path = _require(RTDL)
    return load_rd_findings(path, expected_sha256=_digest(path), expected_size=path.stat().st_size)


def test_snapshot_digests_match_the_recorded_provenance() -> None:
    assert _digest(GMMVI) == GMMVI_SHA
    assert _digest(RTDL) == RTDL_SHA


def test_hash_mismatch_is_a_validation_error_not_a_finding(tmp_path: Path) -> None:
    path = _require(RTDL)
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(path, expected_sha256="0" * 64)
    assert caught.value.code.startswith("P_")
    assert "sha256" in caught.value.problem
    assert str(caught.value) == f"{caught.value.code} at {caught.value.where}: {caught.value.problem}"


def test_size_mismatch_is_a_validation_error(tmp_path: Path) -> None:
    path = _require(RTDL)
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(path, expected_sha256=_digest(path), expected_size=1)
    assert caught.value.code == "P_UNRESOLVED_REF"


def test_missing_file_is_a_validation_error(tmp_path: Path) -> None:
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(tmp_path / "absent.json")
    assert caught.value.code == "P_UNRESOLVED_REF"


def test_a_non_array_payload_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "not-a-findings-array.json"
    path.write_text(json.dumps({"findings": []}), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(path)
    assert caught.value.code == "P_TOP_LEVEL"


def test_duplicate_rule_target_pair_is_rejected(tmp_path: Path) -> None:
    payload = [
        {"rule_id": "RD001", "target": "t", "status": "PASS", "measurements": {}},
        {"rule_id": "RD001", "target": "t", "status": "FAIL", "measurements": {}},
    ]
    path = tmp_path / "dup.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(path)
    assert caught.value.code == "P_DUPLICATE_ID"


def test_unknown_source_ref_key_is_rejected(tmp_path: Path) -> None:
    payload = [
        {
            "rule_id": "RD001",
            "target": "t",
            "status": "PASS",
            "evidence": [{"path": "a.csv", "column": "score", "row": 3}],
        }
    ]
    path = tmp_path / "bad-evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_rd_findings(path)
    assert caught.value.code == "P_LOCATOR_KEYS"


def test_extra_keys_in_an_upstream_finding_are_ignored(tmp_path: Path) -> None:
    """Clause 3: only the 8 keys are indexed; anything else in the file is ignored, not invented."""
    payload = [{"rule_id": "RD001", "target": "t", "status": "PASS", "confidence": 0.99, "notes": "x"}]
    path = tmp_path / "extras.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    baseline = load_rd_findings(path)
    assert baseline.findings[0].measurements == {}


def test_measurement_read_list_is_closed(gmmvi) -> None:  # type: ignore[no-untyped-def]
    """No rule may widen what PD reads from upstream by asking for another key."""
    finding = gmmvi.findings[0]
    with pytest.raises(OutsideReadList):
        finding.measure("universe_status")
    with pytest.raises(OutsideReadList):
        finding.measure("n_candidates")
    assert {"n_members", "n_exclusions", "member_rule_grade", "n"} <= MEASUREMENT_READ_LIST


def test_nan_measurement_stays_unknown_and_never_becomes_zero(rtdl) -> None:  # type: ignore[no-untyped-def]
    """The real RTDL snapshot carries bare `NaN` in `recomputed_dispersion`."""
    raw = RTDL.read_text(encoding="utf-8")
    assert "NaN" in raw  # strict JSON would refuse this file; Python accepts it
    with pytest.raises(ValueError):
        # A consumer that tries to *decode* the constant as a value gets nothing valid back:
        # the literal is not a JSON token, and PD must not pretend it is a number.
        json.loads(raw, parse_constant=lambda literal: (_ for _ in ()).throw(ValueError(literal)))

    findings = list(rtdl.by_rule("RD001"))
    assert findings, "expected RD001 findings in the RTDL snapshot"
    sentinel = findings[0].measure("recomputed_dispersion")
    assert isinstance(sentinel, NonFinite)
    assert is_non_finite(sentinel)
    assert sentinel != 0.0
    assert not (sentinel == 0)
    assert findings[0].known_measure("recomputed_dispersion") is None
    with pytest.raises(TypeError):
        sentinel + 1.0  # type: ignore[operator]
    with pytest.raises(TypeError):
        1.0 + sentinel  # type: ignore[operator]


def test_nan_is_never_silently_rewritten_in_the_snapshot(rtdl) -> None:  # type: ignore[no-untyped-def]
    """`measure` keeps the sentinel; only the explicit UNKNOWN read drops it."""
    for finding in rtdl.findings:
        for key, value in finding.measurements.items():
            if key in MEASUREMENT_READ_LIST and is_non_finite(value):
                assert finding.measure(key) is value
                assert finding.known_measure(key) is None


def test_gmmvi_baseline_census_is_the_frozen_538(gmmvi) -> None:  # type: ignore[no-untyped-def]
    from paper_doctor.status import RuleStatus

    census = {status: sum(1 for f in gmmvi.findings if f.status is status) for status in RuleStatus}
    assert len(gmmvi.findings) == 538
    assert census[RuleStatus.PASS] == 165
    assert census[RuleStatus.INCONCLUSIVE] == 293
    assert census[RuleStatus.NOT_APPLICABLE] == 69
    assert census[RuleStatus.FAIL] == 11
    assert len(gmmvi.by_rule("RD002")) == 46
    assert all(f.status is RuleStatus.INCONCLUSIVE for f in gmmvi.by_rule("RD002"))


def test_pd005_exclusion_universe_is_seven_targets_and_thirty_four_exclusions(gmmvi) -> None:  # type: ignore[no-untyped-def]
    universe = gmmvi.exclusion_universe()
    assert len(universe) == 7
    assert sum(f.n_exclusions for f in universe) == 34
    assert all(f.listing_is_evidenced for f in universe)
    assert {f.target for f in universe} == {
        "aggregation:agg:PlanarRobot/sepyfux/-elbo",
        "aggregation:agg:PlanarRobot/sepyrux/-elbo",
        "aggregation:agg:PlanarRobot/zamtrux/-elbo",
        "aggregation:agg:TALOS/sepyfux/-elbo",
        "aggregation:agg:TALOS/sepyfux/entropy",
        "aggregation:agg:TALOS/sepyrux/-elbo",
        "aggregation:agg:TALOS/sepyrux/entropy",
    }


def test_rtdl_baseline_keeps_the_not_run_vs_zero_target_distinction(rtdl) -> None:  # type: ignore[no-untyped-def]
    """16 findings from `audit_manifest`, and the single NOT_RUN is RD007 over an empty
    comparison-set section -- an absent class, not absent evidence."""
    from paper_doctor.status import RuleStatus

    assert len(rtdl.findings) == 16
    not_run = [f for f in rtdl.findings if f.status is RuleStatus.NOT_RUN]
    assert [(f.rule_id, f.target) for f in not_run] == [("RD007", "rule:RD007")]
    assert "comparison_sets is empty" in not_run[0].reason
    assert rtdl.get("RD007", "rule:RD007") is not_run[0]


def test_findings_are_indexed_by_rule_id_and_target(gmmvi) -> None:  # type: ignore[no-untyped-def]
    target = "aggregation:agg:PlanarRobot/sepyfux/-elbo"
    finding = gmmvi.get("RD002", target)
    assert finding is not None and finding.n_exclusions == 5
    assert gmmvi.get("RD999", target) is None


def test_upstream_evidence_propagates_one_hop(gmmvi) -> None:  # type: ignore[no-untyped-def]
    """Clause 4: `evidence[]` SourceRefs survive into PD so provenance is not lost."""
    finding = gmmvi.get("RD002", "aggregation:agg:PlanarRobot/sepyfux/-elbo")
    assert finding is not None and finding.evidence
    labels = [ref.label() for ref in finding.evidence]
    assert any("result-doctor.yml" in label or ".csv" in label or ".json" in label for label in labels)
