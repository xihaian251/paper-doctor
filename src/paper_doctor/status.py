"""Rule status vocabulary and finding record.

Reuses Result Doctor's five states and its canonical serialization contract; adds no score
of any kind. `RuleFinding.to_dict()` keeps exactly the 8 keys that Contract I-1 clause 3
indexes upstream findings by, so a PD finding and an RD finding are readable by the same code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .evidence import SourceRef


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_RUN = "NOT_RUN"


class UniverseStatus(str, Enum):
    """Candidate-set recoverability. UNKNOWN is the default; UNRECOVERABLE requires
    affirmative evidence that the full candidate universe cannot be recovered.
    A smaller surviving artifact count is never such evidence.
    """

    UNKNOWN = "UNKNOWN"
    RECOVERED = "RECOVERED"
    PARTIAL = "PARTIAL"
    DECLARED_ONLY = "DECLARED_ONLY"
    UNRECOVERABLE = "UNRECOVERABLE"


@dataclass(frozen=True)
class RuleFinding:
    rule_id: str
    rule_name: str
    target: str
    status: RuleStatus
    question: str = ""
    measurements: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[SourceRef, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "target": self.target,
            "status": self.status.value,
            "question": self.question,
            "measurements": self.measurements,
            "evidence": [
                {"path": s.path, "key": s.key, "line": s.line, "artifact_id": s.artifact_id, "note": s.note}
                for s in self.evidence
            ],
            "reason": self.reason,
        }


def canonical_json(findings: list[RuleFinding]) -> str:
    """Deterministic serialization: fixed rule order, sorted keys, no timestamps."""
    return json.dumps([f.to_dict() for f in findings], sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(findings: list[RuleFinding], destination: str | Path) -> None:
    """`newline="\\n"` so the byte-identity promise does not depend on the platform."""
    Path(destination).write_text(canonical_json(findings) + "\n", encoding="utf-8", newline="\n")
