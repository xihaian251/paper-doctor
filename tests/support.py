"""Shared harness for the Phase 1 test blocks.

Every synthetic case in Phase 1 is a real audit: a corpus on disk, an upstream findings array,
a `paper-doctor.yml`, and `audit_manifest()` end to end. Nothing here mocks a rule, and no
expectation is computed from the implementation -- the statuses each case requires are the ones
frozen in the Phase 0 report (§18, §19, §14).

`claim()` reads a claim's text *and* its line number off the corpus, so a case cannot silently
declare a locator the source does not carry: that would be a `P_UNRESOLVED_REF` at load time.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from paper_doctor.audit import Bundle, bundle_from_manifest
from paper_doctor.manifest import MANIFEST_NAME
from paper_doctor.status import RuleFinding

PAPER_NAME = "paper.tex"
FINDINGS_NAME = "findings.json"

_PREAMBLE = "\\documentclass{article}\n\\begin{document}\n"


def document(*lines: str) -> str:
    """A minimal LaTeX root: a preamble, a body, and the caller's lines in order."""
    return _PREAMBLE + "\n".join(lines) + "\n\\end{document}\n"


def line_of(paper: str, fragment: str) -> tuple[int, str]:
    """The 1-based line that contains `fragment`, and that line's text."""
    matches = [(index, text) for index, text in enumerate(paper.split("\n"), start=1) if fragment in text]
    if not matches:
        raise AssertionError(f"the synthetic corpus has no line containing {fragment!r}")
    if len(matches) > 1:
        raise AssertionError(f"{fragment!r} appears on {len(matches)} lines; a fragment must name one")
    return matches[0]


def claim(
    paper: str,
    claim_id: str,
    fragment: str,
    *,
    form: str,
    path: str = PAPER_NAME,
    fragment_is_text: bool = False,
    **fields: Any,
) -> dict[str, Any]:
    """One `_claims` entry whose text and locator are read off the corpus itself.

    `fragment_is_text` is for the real corpora, whose source lines are whole paragraphs: the
    claim a Phase 0 trace names is one sentence inside such a line, so the fragment is declared
    as the text and the loader still verifies that it really sits on that line.
    """
    line, text = line_of(paper, fragment)
    declared = fragment if fragment_is_text else text.strip()
    entry: dict[str, Any] = {
        "claim_id": claim_id,
        "text": declared,
        "locator": {"path": path, "line": line, "text": declared},
        "form": form,
    }
    entry.update({key: value for key, value in fields.items() if value is not None})
    return entry


def link(link_id: str, claim_ref: str, target_kind: str, target_ref: Any, **fields: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "link_id": link_id,
        "claim": claim_ref,
        "target_kind": target_kind,
        "target_ref": target_ref,
        "link_basis": fields.pop("link_basis", "AUDITOR_DECLARED"),
    }
    entry.update({key: value for key, value in fields.items() if value is not None})
    return entry


def float_anchor(label: str, **fields: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"label": label}
    entry.update({key: value for key, value in fields.items() if value is not None})
    return entry


def rd(
    rule_id: str,
    target: str,
    status: str,
    *,
    measurements: dict[str, Any] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    """One upstream finding, in exactly the shape `result-doctor audit --json` emits."""
    return {
        "rule_id": rule_id,
        "rule_name": f"{rule_id} (synthetic)",
        "target": target,
        "status": status,
        "question": "what the upstream rule asked",
        "measurements": dict(measurements or {}),
        "evidence": list(evidence or []),
        "reason": reason,
    }


def findings_text(rows: list[dict[str, Any]]) -> str:
    """`json.dumps` with its default `allow_nan`, so a non-finite measurement is a bare `NaN`."""
    return json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n"


def write_case(
    root: Path,
    *,
    paper: str,
    findings: list[dict[str, Any]] | str,
    claims: list[dict[str, Any]],
    floats: list[dict[str, Any]] | None = None,
    links: list[dict[str, Any]] | None = None,
    extra_files: dict[str, str] | None = None,
    paper_digest: bool = True,
) -> Path:
    """Write the corpus, the upstream artifact and the manifest. Returns the manifest path."""
    root.mkdir(parents=True, exist_ok=True)
    payload = findings if isinstance(findings, str) else findings_text(findings)
    (root / FINDINGS_NAME).write_text(payload, encoding="utf-8", newline="\n")
    paper_fields: dict[str, Any] = {"path": PAPER_NAME}
    if paper_digest:
        paper_fields["sha256"] = hashlib.sha256(paper.encode("utf-8")).hexdigest()
        paper_fields["size"] = len(paper.encode("utf-8"))
    (root / PAPER_NAME).write_text(paper, encoding="utf-8", newline="\n")
    for name, text in (extra_files or {}).items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    document = {
        "schema_version": 1,
        "_registry": {
            "paper": paper_fields,
            "rd_findings": {
                "path": FINDINGS_NAME,
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                "size": len(payload.encode("utf-8")),
                "rd_version": "0.1.0",
            },
        },
        "_claims": claims,
        "_floats": floats or [],
        "_links": links or [],
    }
    manifest = root / MANIFEST_NAME
    manifest.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest


def audit(root: Path, **case: Any) -> list[RuleFinding]:
    return audit_manifest_of(write_case(root, **case))


def audit_manifest_of(manifest: Path, rule_ids: list[str] | None = None) -> list[RuleFinding]:
    from paper_doctor.audit import audit_manifest

    return audit_manifest(manifest, rule_ids)


def corpus_lines(corpus_root: Path, rel: str) -> str:
    """Read one read-only corpus file verbatim. A missing corpus is a hard error, never a skip."""
    path = corpus_root / rel
    if not path.is_file():
        raise FileNotFoundError(f"read-only corpus fixture missing: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def write_real_case(
    root: Path,
    *,
    audit_root: Path,
    paper_path: str,
    rd_artifact: Path,
    claims: list[dict[str, Any]],
    floats: list[dict[str, Any]] | None = None,
    links: list[dict[str, Any]] | None = None,
) -> Path:
    """Point a manifest at a read-only corpus and a frozen upstream artifact, in place.

    Nothing is copied and nothing is rewritten: the paper keeps its own bytes and sha256, and the
    upstream findings file is referenced where it lies. This is the only way the real-anchor tests
    can audit GMMVI and RTDL without manufacturing a synthetic stand-in for either.
    """
    root.mkdir(parents=True, exist_ok=True)
    paper_bytes = (audit_root / paper_path).read_bytes()
    rd_bytes = rd_artifact.read_bytes()
    document = {
        "schema_version": 1,
        "_registry": {
            "paper": {
                "root": audit_root.resolve().as_posix(),
                "path": paper_path,
                "sha256": hashlib.sha256(paper_bytes).hexdigest(),
                "size": len(paper_bytes),
            },
            "rd_findings": {
                "path": rd_artifact.resolve().as_posix(),
                "sha256": hashlib.sha256(rd_bytes).hexdigest(),
                "size": len(rd_bytes),
                "rd_version": "0.1.0",
            },
        },
        "_claims": claims,
        "_floats": floats or [],
        "_links": links or [],
    }
    manifest = root / MANIFEST_NAME
    manifest.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest


def bundle(root: Path, **case: Any) -> Bundle:
    return bundle_from_manifest(write_case(root, **case))


def statuses(findings: list[RuleFinding]) -> dict[str, dict[str, str]]:
    """`{rule_id: {target: status.value}}`, the shape every matrix assertion reads."""
    out: dict[str, dict[str, str]] = {}
    for finding in findings:
        out.setdefault(finding.rule_id, {})[finding.target] = finding.status.value
    return out


def one(findings: list[RuleFinding], rule_id: str, target: str) -> RuleFinding:
    matches = [f for f in findings if f.rule_id == rule_id and f.target == target]
    if not matches:
        raise AssertionError(f"no {rule_id} finding on {target!r}; got {[(f.rule_id, f.target) for f in findings]}")
    return matches[0]
