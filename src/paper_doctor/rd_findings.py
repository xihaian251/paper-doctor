"""Contract I-1: the only reader of upstream Result Doctor output.

Paper Doctor consumes exactly one external artifact -- the JSON array emitted by
`result-doctor audit <project> --json <file>` -- and never imports `result_doctor` at
runtime (clause 1), never calls an RD rule, never rebuilds an RD bundle, and never
re-audits an RD finding (clause 7 keeps the dependency one-way).

Two policies live here because they belong to the consumer, not to upstream:

* the frozen measurement read-list (clause 4). A key outside it is a programming error and
  raises, rather than quietly widening what PD reads from upstream;
* the `NaN` policy (clause 5). RD's canonical JSON is Python-legal and strict-JSON-illegal:
  a bare `NaN` can appear in a measurement. It parses to a sentinel that is never coerced to
  0.0 / `""` / `False`, and never compares numerically. It means UNKNOWN, and PD does not
  touch upstream to change it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .evidence import SourceRef
from .manifest import (
    P_DUPLICATE_ID,
    P_LOCATOR_KEYS,
    P_MISSING_FIELD,
    P_TOP_LEVEL,
    P_TYPE,
    P_UNRESOLVED_REF,
    ManifestError,
)
from .status import RuleStatus

#: Clause 3: the only keys PD indexes an upstream finding by. Anything else is ignored.
FINDING_KEYS = ("rule_id", "rule_name", "target", "status", "question", "measurements", "evidence", "reason")
REQUIRED_FINDING_KEYS = ("rule_id", "target", "status")
EVIDENCE_KEYS = ("path", "key", "line", "artifact_id", "note")

#: Clause 4, frozen: what PD may read out of `measurements`, plus the exclusion census.
MEASUREMENT_READ_LIST = frozenset(
    {
        "n_members",
        "reported_center",
        "reported_dispersion",
        "rendered_center",
        "rendered_dispersion",
        "recomputed_center",
        "recomputed_dispersion",
        "families_matching_published_spread",
        "declared_form",
        "spread_label",
        "spread_label_grade",
        "n",
        "n_exclusions",
        "n_exclusions_listed",
        "n_exclusions_unlisted",
        "n_exclusions_unbound_to_members",
        "exclusion_criterion_recomputable",
        "member_rule_grade",
        "member_rule_kind",
    }
)

_LISTED_GRADES = frozenset({"DIRECT", "DERIVED"})


class OutsideReadList(KeyError):
    """A rule asked for an upstream measurement Paper Doctor is not contracted to read."""


class NonFinite:
    """Sentinel for a bare `NaN`/`Infinity` in upstream JSON.

    Any arithmetic on it raises, so a non-finite measurement cannot silently behave like a
    number and cannot compare equal to 0.0.
    """

    __slots__ = ("literal",)

    def __init__(self, literal: str) -> None:
        self.literal = literal

    def __repr__(self) -> str:
        return f"<UNKNOWN non-finite:{self.literal}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NonFinite) and other.literal == self.literal

    def __hash__(self) -> int:
        return hash(("NonFinite", self.literal))

    def __add__(self, other: object) -> None:  # type: ignore[override]
        raise TypeError("a non-finite upstream measurement is UNKNOWN; it cannot be used arithmetically")

    __radd__ = __add__
    __sub__ = __add__
    __rsub__ = __add__
    __mul__ = __add__
    __rmul__ = __add__
    __truediv__ = __add__
    __rtruediv__ = __add__


def _parse_constant(literal: str) -> NonFinite:
    return NonFinite(literal)


def is_non_finite(value: Any) -> bool:
    return isinstance(value, NonFinite)


@dataclass(frozen=True)
class RDFinding:
    """One upstream finding, held exactly as emitted. No field is added, none is derived."""

    rule_id: str
    rule_name: str
    target: str
    status: RuleStatus
    question: str = ""
    measurements: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[SourceRef, ...] = ()
    reason: str = ""

    def measure(self, key: str) -> Any:
        """Read a contracted measurement. Absent -> None; non-finite -> the `NonFinite` sentinel."""
        if key not in MEASUREMENT_READ_LIST:
            raise OutsideReadList(key)
        return self.measurements.get(key)

    def known_measure(self, key: str) -> Any:
        """The `NaN`-safe read: a non-finite measurement is UNKNOWN, so it reads as absent."""
        value = self.measure(key)
        return None if is_non_finite(value) else value

    @property
    def n_exclusions(self) -> int:
        value = self.known_measure("n_exclusions")
        return int(value) if isinstance(value, int) else 0

    @property
    def listing_is_evidenced(self) -> bool:
        """PD005: a listing counts only when fully listed and the member rule is DIRECT/DERIVED."""
        listed = self.known_measure("n_exclusions_listed")
        grade = self.known_measure("member_rule_grade")
        return (
            self.n_exclusions > 0
            and isinstance(listed, int)
            and listed == self.n_exclusions
            and isinstance(grade, str)
            and grade in _LISTED_GRADES
        )


@dataclass(frozen=True)
class RDBaseline:
    """The verified upstream artifact plus the two indexes PD is allowed to build over it."""

    path: str = ""
    sha256: str = ""
    size: int = 0
    declared_rd_version: str = ""
    findings: tuple[RDFinding, ...] = ()
    by_rule_target: dict[tuple[str, str], RDFinding] = field(default_factory=dict)

    def get(self, rule_id: str, target: str) -> RDFinding | None:
        return self.by_rule_target.get((rule_id, target))

    def by_rule(self, rule_id: str) -> tuple[RDFinding, ...]:
        return tuple(f for f in self.findings if f.rule_id == rule_id)

    def targets_for(self, rule_id: str) -> tuple[str, ...]:
        return tuple(f.target for f in self.findings if f.rule_id == rule_id)

    def exclusion_universe(self) -> tuple[RDFinding, ...]:
        """PD005's universe, derived mechanically: `{target : RD002 and n_exclusions > 0}`.

        There is no upstream `exclusions` collection to iterate -- the frozen RD bundle has
        exactly 8 sections and exclusions hang off `Aggregation` objects -- so this predicate
        is the only way the census is visible across the JSON boundary.
        """
        return tuple(f for f in self.by_rule("RD002") if f.n_exclusions > 0)


def _to_finding(raw: Any, where: str) -> RDFinding:
    if not isinstance(raw, dict):
        raise ManifestError(P_TYPE, where, f"expected a finding mapping, got {type(raw).__name__}")
    for key in REQUIRED_FINDING_KEYS:
        if key not in raw:
            raise ManifestError(P_MISSING_FIELD, f"{where}/{key}", "upstream finding lacks a key PD indexes by")
    try:
        status = RuleStatus(str(raw["status"]))
    except ValueError as error:
        raise ManifestError(P_TYPE, f"{where}/status", f"unknown upstream status {raw['status']!r}") from error
    measurements = raw.get("measurements") or {}
    if not isinstance(measurements, dict):
        raise ManifestError(P_TYPE, f"{where}/measurements", "expected a mapping")
    evidence: list[SourceRef] = []
    for index, ref in enumerate(raw.get("evidence") or []):
        ref_where = f"{where}/evidence[{index}]"
        if not isinstance(ref, dict):
            raise ManifestError(P_TYPE, ref_where, "expected a SourceRef mapping")
        extra = sorted(set(ref) - set(EVIDENCE_KEYS))
        if extra:
            raise ManifestError(P_LOCATOR_KEYS, ref_where, f"unknown SourceRef key(s): {', '.join(extra)}")
        evidence.append(
            SourceRef(
                path=str(ref.get("path", "")),
                key=str(ref.get("key", "")),
                line=ref.get("line", ""),
                artifact_id=str(ref.get("artifact_id", "")),
                note=str(ref.get("note", "")),
            )
        )
    return RDFinding(
        rule_id=str(raw["rule_id"]),
        rule_name=str(raw.get("rule_name", "")),
        target=str(raw["target"]),
        status=status,
        question=str(raw.get("question", "")),
        measurements=dict(measurements),
        evidence=tuple(evidence),
        reason=str(raw.get("reason", "")),
    )


def load_rd_findings(
    path: str | Path,
    *,
    expected_sha256: str = "",
    expected_size: int = 0,
    declared_rd_version: str = "",
) -> RDBaseline:
    """Read and verify the single upstream artifact.

    A missing file or a hash/size mismatch is a VALIDATION ERROR (exit 2), never a scientific
    finding: PD refuses to audit prose against evidence it cannot tie to the declared bytes.
    """
    file = Path(path)
    where = file.name
    if not file.is_file():
        raise ManifestError(P_UNRESOLVED_REF, where, "the declared upstream findings file does not exist")
    payload = file.read_bytes()
    observed_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 and expected_sha256 != observed_sha256:
        raise ManifestError(
            P_UNRESOLVED_REF,
            f"{where}/sha256",
            f"declared sha256 {expected_sha256} does not match the observed {observed_sha256}",
        )
    if expected_size and expected_size != len(payload):
        raise ManifestError(
            P_UNRESOLVED_REF, f"{where}/size", f"declared size {expected_size} != observed {len(payload)}"
        )

    try:
        document = json.loads(payload.decode("utf-8"), parse_constant=_parse_constant)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ManifestError(P_TOP_LEVEL, where, f"upstream findings are not readable JSON: {error}") from error
    if not isinstance(document, list):
        raise ManifestError(P_TOP_LEVEL, where, "expected the findings array emitted by `audit --json`")

    findings = tuple(_to_finding(raw, f"{where}[{index}]") for index, raw in enumerate(document))
    index: dict[tuple[str, str], RDFinding] = {}
    for finding in findings:
        key = (finding.rule_id, finding.target)
        if key in index:
            raise ManifestError(P_DUPLICATE_ID, where, f"duplicate upstream (rule_id, target): {key}")
        index[key] = finding

    return RDBaseline(
        path=str(file),
        sha256=observed_sha256,
        size=len(payload),
        declared_rd_version=declared_rd_version,
        findings=findings,
        by_rule_target=index,
    )
