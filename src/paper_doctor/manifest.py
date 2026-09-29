"""The audit contract: `paper-doctor.yml`.

This module validates *input*, never the paper. A manifest that cannot be read as a
contract raises `ManifestError`, the CLI exits 2, and nothing is reported as a scientific
finding -- the three-channel discipline inherited from Result Doctor (Phase 0 §17).

Twelve validation codes, frozen in Phase 0. Each one corresponds to a hazard observed
while producing the Phase 0 traces; there is no thirteenth, and invalid input is never
silently repaired.
"""

from __future__ import annotations

import hashlib
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .evidence import SourceRef
from .latex_index import LatexIndex
from .objects import (
    Claim,
    ClaimForm,
    EvidenceLink,
    FloatAnchor,
    LinkBasis,
    PairingBasis,
    Qualifier,
    Quantifier,
    ResultArtifact,
    ScopeDecl,
    ScopeUnit,
    TargetKind,
)
from .status import UniverseStatus

P_SCHEMA_VERSION = "P_SCHEMA_VERSION"
P_TOP_LEVEL = "P_TOP_LEVEL"
P_UNKNOWN_KEY = "P_UNKNOWN_KEY"
P_TYPE = "P_TYPE"
P_NOT_A_NUMBER = "P_NOT_A_NUMBER"
P_MISSING_FIELD = "P_MISSING_FIELD"
P_DUPLICATE_ID = "P_DUPLICATE_ID"
P_UNRESOLVED_REF = "P_UNRESOLVED_REF"
P_CONFLICTING_REF = "P_CONFLICTING_REF"
P_LOCATOR_KEYS = "P_LOCATOR_KEYS"
P_PATH_OUTSIDE_ROOT = "P_PATH_OUTSIDE_ROOT"
P_YAML = "P_YAML"

VALIDATION_CODES: tuple[str, ...] = (
    P_SCHEMA_VERSION,
    P_TOP_LEVEL,
    P_UNKNOWN_KEY,
    P_TYPE,
    P_NOT_A_NUMBER,
    P_MISSING_FIELD,
    P_DUPLICATE_ID,
    P_UNRESOLVED_REF,
    P_CONFLICTING_REF,
    P_LOCATOR_KEYS,
    P_PATH_OUTSIDE_ROOT,
    P_YAML,
)

SCHEMA_VERSION = 1
MANIFEST_NAME = "paper-doctor.yml"

#: Frozen section order (Phase 0 §22). Reference resolution happens in a second pass, so
#: declaration order never carries evaluation order -- the same reason RD tolerates a cell
#: naming its comparison set before that set is written.
SECTION_ORDER: tuple[str, ...] = ("_registry", "_claims", "_floats", "_links")

#: The four and only four locator key sets (Phase 0 §7).
LOCATOR_KEY_SETS: tuple[frozenset[str], ...] = (
    frozenset({"path", "column", "row"}),
    frozenset({"path", "key"}),
    frozenset({"path", "line"}),
    frozenset({"path", "line", "text"}),
    frozenset({"path", "text"}),
)

REGISTRY_FIELDS = frozenset({"paper", "rd_findings"})
PAPER_FIELDS = frozenset({"path", "sha256", "size", "root", "note"})
RD_FIELDS = frozenset({"path", "sha256", "size", "rd_version", "note"})
CLAIM_FIELDS = frozenset(
    {
        "claim_id",
        "text",
        "locator",
        "form",
        "predicate",
        "subjects",
        "quantifier",
        "qualifiers",
        "scope",
        "links",
        "same_as",
        "not_audited_reason",
    }
)
FLOAT_FIELDS = frozenset(
    {
        "float_id",
        "label",
        "kind",
        "number",
        "caption_locator",
        "quantity_declaration",
        "precision_declaration",
        "mark_rule_declaration",
    }
)
LINK_FIELDS = frozenset({"link_id", "claim", "target_kind", "target_ref", "link_basis", "quantity_identity", "grade"})
SCOPE_FIELDS = frozenset({"declared_universe", "stated_count", "unit", "members", "universe_status", "locator"})
QUALIFIER_FIELDS = frozenset({"kind", "statement", "locator"})
SAME_AS_FIELDS = frozenset({"claim", "basis"})


class ManifestError(ValueError):
    """A manifest that cannot be read as a contract. Never raised for missing evidence."""

    def __init__(self, code: str, where: str, problem: str) -> None:
        super().__init__(f"{code} at {where}: {problem}")
        self.code = code
        self.where = where
        self.problem = problem


@dataclass(frozen=True)
class RdFindingsRef:
    """What the manifest declares about the single upstream artifact (Contract I-1.2).

    `path`/`sha256`/`size` are verified against the file by `rd_findings.load` (OBSERVED);
    `rd_version` cannot be corroborated from a findings array and stays DECLARED.
    """

    path: str = ""
    sha256: str = ""
    size: int = 0
    rd_version: str = ""
    note: str = ""


@dataclass(frozen=True)
class PDManifest:
    path: str = ""
    root: Path = field(default_factory=Path)
    paper: ResultArtifact = field(default_factory=ResultArtifact)
    rd: RdFindingsRef = field(default_factory=RdFindingsRef)
    claims: tuple[Claim, ...] = ()
    floats: tuple[FloatAnchor, ...] = ()
    links: tuple[EvidenceLink, ...] = ()

    def claim_by_id(self, claim_id: str) -> Claim | None:
        return next((c for c in self.claims if c.claim_id == claim_id), None)

    def anchor_by_id(self, anchor_id: str) -> FloatAnchor | None:
        return next((f for f in self.floats if f.anchor_id == anchor_id or f.float_id == anchor_id), None)

    def links_for(self, claim_id: str) -> tuple[EvidenceLink, ...]:
        return tuple(link for link in self.links if link.claim_ref == claim_id)


def _where(section: str, key: str = "") -> str:
    return f"{section}/{key}" if key else section


def _mapping(value: Any, where: str, expect: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(P_TYPE, where, f"expected {expect}, got {type(value).__name__}")
    return value


def _sequence(value: Any, where: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        raise ManifestError(P_TYPE, where, f"expected a list, got {type(value).__name__}")
    return tuple(value)


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str):
        raise ManifestError(P_TYPE, where, f"expected a string, got {type(value).__name__}")
    return value


def _integer(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestError(P_NOT_A_NUMBER, where, f"expected an integer, got {value!r}")
    return value


def _require_keys(entry: dict[str, Any], allowed: frozenset[str], where: str, required: tuple[str, ...] = ()) -> None:
    for key in required:
        if key not in entry:
            raise ManifestError(P_MISSING_FIELD, _where(where, key), "required field is absent")
    unknown = sorted(set(entry) - allowed)
    if unknown:
        raise ManifestError(P_UNKNOWN_KEY, where, f"unknown key(s): {', '.join(unknown)}")


def _enum(value: Any, choices: dict[str, Any], where: str, label: str) -> Any:
    text = _string(value, where)
    if text not in choices:
        raise ManifestError(P_TYPE, where, f"{label} must be one of {', '.join(sorted(choices))}, got {text!r}")
    return choices[text]


def _locator(raw: Any, where: str, root: Path) -> SourceRef:
    entry = _mapping(raw, where, "a locator mapping")
    keys = frozenset(entry)
    if keys not in LOCATOR_KEY_SETS:
        raise ManifestError(
            P_LOCATOR_KEYS,
            where,
            f"locator key set {sorted(keys)} is not one of the four families "
            "[path,column,row] / [path,key] / [path,line] / [path,line,text] / [path,text]",
        )
    path = _string(entry.get("path", ""), _where(where, "path"))
    _within_root(Path(path), root, _where(where, "path"))
    line = entry.get("line", "")
    if line != "":
        line = _integer(line, _where(where, "line"))
    if "column" in keys or "row" in keys:
        # RD's `Locus` types `row`/`column` as strings holding the *named* row label and column
        # header (schema.py:91-92), and Phase 0 §7 keeps that semantics. PD reuses RD's
        # `SourceRef` verbatim (§14), so the cell address is encoded into `key` with a fixed,
        # reversible spelling rather than given a new object.
        column = _string(entry.get("column", ""), _where(where, "column"))
        row = _string(entry.get("row", ""), _where(where, "row"))
        return SourceRef(path=path, key=f"column={column},row={row}", line=line)
    return SourceRef(path=path, key=_string(entry.get("key", ""), _where(where, "key")), line=line)


def _within_root(candidate: Path, root: Path, where: str) -> Path:
    resolved = (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ManifestError(P_PATH_OUTSIDE_ROOT, where, f"{candidate} resolves outside the audit root {root_resolved}")
    return resolved


def _load_yaml(path: Path) -> Any:
    """`safe_load` only, so no manifest can construct an arbitrary Python object (Contract I-1.6).

    A manifest that is not there at all is a contract problem, not a tool crash: Phase 2 §10 gives
    "the command line pointed at the wrong file" exit 2, the same channel as a malformed one. The
    CLI resolves a directory to the one fixed name, so this is the branch a typo lands in -- and the
    message names the exact path it tried, which a recursive search would have hidden.
    """
    if not path.is_file():
        raise ManifestError(P_UNRESOLVED_REF, str(path), "no readable manifest is present at this path")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ManifestError(P_YAML, path.name, str(error).replace("\n", " ")) from error
    except OSError as error:
        raise ManifestError(P_UNRESOLVED_REF, str(path), f"the manifest could not be read: {error.strerror}") from error


def _normalize(text: str) -> str:
    return " ".join(text.split())


class _Corpus:
    """Line-addressed read-only view of the paper source, for OBSERVED text verification."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._cache: dict[str, tuple[list[str], list[int], str]] = {}

    def _file(self, rel: str) -> tuple[list[str], list[int], str]:
        cached = self._cache.get(rel)
        if cached is not None:
            return cached
        path = self.root / rel
        if not path.is_file():
            raise ManifestError(P_UNRESOLVED_REF, rel, "declared source file does not exist under the audit root")
        lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
        normalized = [_normalize(line) for line in lines]
        flat = " ".join(normalized)
        starts: list[int] = []
        position = 0
        for text in normalized:
            starts.append(position)
            position += len(text) + 1
        cached = (normalized, starts, flat)
        self._cache[rel] = cached
        return cached

    def verify_text(self, rel: str, line: int, text: str) -> int:
        """Return the line where `text` starts. Raises when the declared locator is wrong."""
        _lines, starts, flat = self._file(rel)
        needle = _normalize(text)
        if not needle:
            raise ManifestError(P_MISSING_FIELD, rel, "claim text is empty")
        offset = flat.find(needle)
        if offset < 0:
            raise ManifestError(
                P_UNRESOLVED_REF, f"{rel}:{line}", "declared claim text is not present in the source file"
            )
        found = bisect_right(starts, offset) - 1
        if found + 1 != line:
            raise ManifestError(
                P_UNRESOLVED_REF,
                f"{rel}:{line}",
                f"declared claim text starts at line {found + 1}, not {line}",
            )
        return line


def load_manifest(
    path: str | Path,
    *,
    index: LatexIndex | None = None,
    verify_claim_locators: bool = True,
) -> PDManifest:
    """Read `paper-doctor.yml` as a contract. Never judges the paper."""
    manifest_path = Path(path).resolve()
    raw = _load_yaml(manifest_path)
    if not isinstance(raw, dict):
        raise ManifestError(P_TOP_LEVEL, manifest_path.name, f"top level must be a mapping, got {type(raw).__name__}")
    document = raw
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(
            P_SCHEMA_VERSION,
            manifest_path.name,
            f"schema_version must be {SCHEMA_VERSION}, got {document.get('schema_version')!r}",
        )

    declared = [key for key in document if key.startswith("_")]
    expected_order = [section for section in SECTION_ORDER if section in declared]
    if declared != expected_order:
        raise ManifestError(
            P_TOP_LEVEL,
            manifest_path.name,
            f"sections must appear in the frozen order {list(SECTION_ORDER)}, got {declared}",
        )
    extra = sorted(key for key in document if not key.startswith("_") and key != "schema_version")
    if extra:
        raise ManifestError(P_UNKNOWN_KEY, manifest_path.name, f"unknown top-level key(s): {', '.join(extra)}")

    registry = _mapping(document.get("_registry") or {}, "_registry", "a mapping")
    _require_keys(registry, REGISTRY_FIELDS, "_registry")
    root = manifest_path.parent
    paper_entry = _mapping(registry.get("paper") or {}, "_registry/paper", "a mapping")
    _require_keys(paper_entry, PAPER_FIELDS, "_registry/paper", required=("path",))
    if "root" in paper_entry:
        # The audit root is declared, not discovered. Paths *inside* it stay contained;
        # the root itself may live anywhere the read-only corpus happens to be.
        declared_root = Path(_string(paper_entry["root"], "_registry/paper/root"))
        resolved_root = declared_root if declared_root.is_absolute() else (root / declared_root)
        if not resolved_root.resolve().is_dir():
            # The declared string alone is not actionable: read from anywhere else it points to
            # nothing, so the message quotes the absolute location the reader actually tried.
            raise ManifestError(
                P_UNRESOLVED_REF,
                "_registry/paper/root",
                f"declared root {declared_root.as_posix()} resolves to {resolved_root.resolve().as_posix()},"
                f" which is not a directory: restore the paper source there, or point"
                f" _registry/paper/root at the checkout that holds it",
            )
        root = resolved_root.resolve()
    paper_path = _string(paper_entry["path"], "_registry/paper/path")
    _within_root(Path(paper_path), root, "_registry/paper/path")
    paper = ResultArtifact(
        path=paper_path,
        sha256=_string(paper_entry.get("sha256", ""), "_registry/paper/sha256"),
        size=_integer(paper_entry.get("size", 0), "_registry/paper/size"),
        note=_string(paper_entry.get("note", ""), "_registry/paper/note"),
    )
    if paper.sha256:
        payload = (root / paper_path).read_bytes()
        observed = hashlib.sha256(payload).hexdigest()
        if observed != paper.sha256:
            raise ManifestError(
                P_UNRESOLVED_REF,
                "_registry/paper/sha256",
                f"declared sha256 {paper.sha256} does not match the observed {observed}",
            )
        if paper.size and paper.size != len(payload):
            raise ManifestError(
                P_UNRESOLVED_REF, "_registry/paper/size", f"declared size {paper.size} != observed {len(payload)}"
            )
    rd_entry = _mapping(registry.get("rd_findings") or {}, "_registry/rd_findings", "a mapping")
    _require_keys(rd_entry, RD_FIELDS, "_registry/rd_findings", required=("path", "sha256"))
    rd_declared = _string(rd_entry["path"], "_registry/rd_findings/path")
    # The upstream artifact is a declared input, resolved against the manifest directory; the
    # escape guard protects the *audited corpus* (paths PD reads as paper text), not this edge.
    rd_resolved = Path(rd_declared)
    if not rd_resolved.is_absolute():
        rd_resolved = (manifest_path.parent / rd_declared).resolve()
    rd = RdFindingsRef(
        path=rd_resolved.as_posix(),
        sha256=_string(rd_entry["sha256"], "_registry/rd_findings/sha256"),
        size=_integer(rd_entry.get("size", 0), "_registry/rd_findings/size"),
        rd_version=_string(rd_entry.get("rd_version", ""), "_registry/rd_findings/rd_version"),
        note=_string(rd_entry.get("note", ""), "_registry/rd_findings/note"),
    )
    # Existence is checked here; the declared hash and size are verified by `rd_findings.load`,
    # which is the only reader of the artifact. Reading a 585 KB findings array twice -- once to
    # check the digest and once to parse it -- would make the contract slower for no extra safety.
    if not rd_resolved.is_file():
        raise ManifestError(P_UNRESOLVED_REF, "_registry/rd_findings/path", f"{rd_declared} is not a readable file")

    corpus = _Corpus(root)
    floats = tuple(_float(entry, index, root) for entry in _sequence(document.get("_floats") or [], "_floats"))
    # `anchor_id` is `kind:number`, and only the float index can supply it: in the pre-index pass
    # every declared anchor still reads `:0`, so requiring uniqueness there would reject any
    # manifest with two floats. Uniqueness is therefore checked on the two identities the
    # declaration itself carries -- `float_id` and `label` -- plus `anchor_id` once it is resolved.
    _check_unique((f.float_id for f in floats if f.float_id), "_floats")
    _check_unique((label for entry in floats for label in entry.labels), "_floats")
    _check_unique((f.anchor_id for f in floats if f.number), "_floats")
    links = tuple(_link(entry, root, floats) for entry in _sequence(document.get("_links") or [], "_links"))
    _check_unique((link.link_id for link in links), "_links")
    claims = tuple(
        _claim(entry, root, corpus if verify_claim_locators else None, links, index)
        for entry in _sequence(document.get("_claims") or [], "_claims")
    )
    _check_unique((claim.claim_id for claim in claims), "_claims")
    _check_same_as(claims)

    return PDManifest(
        path=manifest_path.name,
        root=root,
        paper=paper,
        rd=rd,
        claims=claims,
        floats=_merge_referenced(floats, index),
        links=links,
    )


def _check_unique(ids: Any, where: str) -> None:
    seen: set[str] = set()
    for value in ids:
        if value in seen:
            raise ManifestError(P_DUPLICATE_ID, where, f"duplicate id {value!r}")
        seen.add(value)


def _check_same_as(claims: tuple[Claim, ...]) -> None:
    """A `same_as` partner is a reference like any other: an unknown id is P_UNRESOLVED_REF,
    and a claim paired with itself is a degenerate contract, not a one-element proposition."""
    ids = {claim.claim_id for claim in claims}
    for claim in claims:
        unknown = sorted({partner for partner, _ in claim.same_as} - ids)
        if unknown:
            raise ManifestError(
                P_UNRESOLVED_REF,
                f"_claims/{claim.claim_id}/same_as",
                f"claim id(s) not declared in _claims: {', '.join(unknown)}",
            )
        for partner, _basis in claim.same_as:
            if partner == claim.claim_id:
                raise ManifestError(P_TYPE, f"_claims/{claim.claim_id}/same_as", "a claim cannot be paired with itself")


def _merge_referenced(floats: tuple[FloatAnchor, ...], index: LatexIndex | None) -> tuple[FloatAnchor, ...]:
    """Attach `referenced_by` (orphan detection, a measurement only) from the float index."""
    if index is None:
        return floats
    by_label = index.label_map()
    out: list[FloatAnchor] = []
    for anchor in floats:
        lines: tuple[int, ...] = ()
        for label in anchor.labels:
            record = by_label.get(label)
            if record is None:
                continue
            lines = tuple(sorted({*lines, *(s.line for s in index.claim_sites() if s.target == label)}))
        out.append(
            FloatAnchor(
                float_id=anchor.float_id,
                kind=anchor.kind,
                number=anchor.number,
                source_file=anchor.source_file,
                begin_line=anchor.begin_line,
                labels=anchor.labels,
                caption_locator=anchor.caption_locator,
                quantity_declaration=anchor.quantity_declaration,
                precision_declaration=anchor.precision_declaration,
                mark_rule_declaration=anchor.mark_rule_declaration,
                referenced_by=lines,
                number_grade=anchor.number_grade,
            )
        )
    return tuple(out)


def _float(entry: Any, index: LatexIndex | None, root: Path) -> FloatAnchor:
    item = _mapping(entry, "_floats", "a float mapping")
    _require_keys(item, FLOAT_FIELDS, "_floats", required=("label",))
    label = _string(item["label"], "_floats/label")
    record = index.resolve_label(label) if index is not None else None
    if index is not None and record is None:
        raise ManifestError(P_UNRESOLVED_REF, f"_floats/{label}", "label does not resolve to any float in the source")
    if record is None:
        return FloatAnchor(
            float_id=_string(item.get("float_id", ""), "_floats/float_id"),
            kind=_string(item.get("kind", ""), "_floats/kind"),
            number=_integer(item.get("number", 0), "_floats/number"),
            labels=(label,),
            caption_locator=_locator(item["caption_locator"], "_floats/caption_locator", root)
            if "caption_locator" in item
            else SourceRef(),
            quantity_declaration=_string(item.get("quantity_declaration", ""), "_floats/quantity_declaration"),
            precision_declaration=_string(item.get("precision_declaration", ""), "_floats/precision_declaration"),
            mark_rule_declaration=_string(item.get("mark_rule_declaration", ""), "_floats/mark_rule_declaration"),
        )
    if "number" in item and _integer(item["number"], "_floats/number") != record.number:
        raise ManifestError(
            P_CONFLICTING_REF,
            f"_floats/{label}",
            f"manifest declares number {item['number']} but the document order resolves "
            f"{label} to {record.kind} {record.number}",
        )
    if "kind" in item and _string(item["kind"], "_floats/kind") != record.kind:
        raise ManifestError(
            P_CONFLICTING_REF, f"_floats/{label}", "declared kind disagrees with the resolved float kind"
        )
    return FloatAnchor(
        float_id=_string(item.get("float_id", ""), "_floats/float_id"),
        kind=record.kind,
        number=record.number,
        source_file=record.source_file,
        begin_line=record.begin_line,
        labels=record.labels,
        caption_locator=_locator(item["caption_locator"], "_floats/caption_locator", root)
        if "caption_locator" in item
        else SourceRef(path=record.source_file, line=record.begin_line),
        quantity_declaration=_string(item.get("quantity_declaration", ""), "_floats/quantity_declaration"),
        precision_declaration=_string(item.get("precision_declaration", ""), "_floats/precision_declaration"),
        mark_rule_declaration=_string(item.get("mark_rule_declaration", ""), "_floats/mark_rule_declaration"),
    )


def _link(entry: Any, root: Path, floats: tuple[FloatAnchor, ...]) -> EvidenceLink:
    item = _mapping(entry, "_links", "a link mapping")
    _require_keys(item, LINK_FIELDS, "_links", required=("link_id", "claim", "target_kind", "target_ref", "link_basis"))
    kind = _enum(item["target_kind"], {k.value: k for k in TargetKind}, "_links/target_kind", "target_kind")
    basis = _enum(item["link_basis"], {b.value: b for b in LinkBasis}, "_links/link_basis", "link_basis")
    grade = _enum(
        item.get("grade", "DERIVED"),
        {"DIRECT": "DIRECT", "DERIVED": "DERIVED", "DECLARED": "DECLARED"},
        "_links/grade",
        "grade",
    )
    if grade == "INFERRED":
        raise ManifestError(
            P_TYPE, "_links/grade", "INFERRED is not a permitted link grade; a suggestion is not a link"
        )
    raw_ref = item["target_ref"]
    target_ref: str | SourceRef | tuple[str, str]
    if kind is TargetKind.FLOAT:
        target_ref = _string(raw_ref, "_links/target_ref")
        anchor = next((f for f in floats if f.anchor_id == target_ref or f.float_id == target_ref), None)
        if anchor is None:
            raise ManifestError(
                P_UNRESOLVED_REF, f"_links/{item['link_id']}", f"float target {target_ref!r} is not declared in _floats"
            )
    elif kind is TargetKind.RD_TARGET:
        pair = _sequence(raw_ref, "_links/target_ref")
        if len(pair) != 2:
            raise ManifestError(P_TYPE, "_links/target_ref", "an RD_TARGET reference must be a [rule_id, target] pair")
        target_ref = (_string(pair[0], "_links/target_ref/0"), _string(pair[1], "_links/target_ref/1"))
    else:
        target_ref = _locator(raw_ref, "_links/target_ref", root)
    return EvidenceLink(
        link_id=_string(item["link_id"], "_links/link_id"),
        claim_ref=_string(item["claim"], "_links/claim"),
        target_kind=kind,
        target_ref=target_ref,
        link_basis=basis,
        quantity_identity=_string(item.get("quantity_identity", ""), "_links/quantity_identity"),
        grade=grade,
    )


def _claim(
    entry: Any,
    root: Path,
    corpus: _Corpus | None,
    links: tuple[EvidenceLink, ...],
    index: LatexIndex | None,
) -> Claim:
    item = _mapping(entry, "_claims", "a claim mapping")
    _require_keys(item, CLAIM_FIELDS, "_claims", required=("claim_id", "text", "locator", "form"))
    claim_id = _string(item["claim_id"], "_claims/claim_id")
    where = f"_claims/{claim_id}"
    locator = _locator(item["locator"], f"{where}/locator", root)
    text = _string(item["text"], f"{where}/text")
    if corpus is not None and locator.line != "":
        corpus.verify_text(locator.path, int(locator.line), text)
    if index is not None and locator.line != "" and locator.path in {chunk.file for chunk in index.chunks}:
        # FM-P11: inside the flattened source, a locator in the preamble lands in a macro
        # definition. That is an input-contract fault, never a PD006 finding. Prose outside
        # the LaTeX root (a README) is not covered by the index and is not judged here.
        if not index.in_body_site(locator.path, int(locator.line)):
            raise ManifestError(
                P_UNRESOLVED_REF,
                f"{where}/locator",
                f"{locator.path}:{locator.line} is outside the document body (macro definition or preamble)",
            )
    form = _enum(item["form"], {f.value: f for f in ClaimForm}, f"{where}/form", "form")
    quantifier = _enum(
        item.get("quantifier", "bare"), {q.value: q for q in Quantifier}, f"{where}/quantifier", "quantifier"
    )

    qualifiers: list[Qualifier] = []
    for raw in _sequence(item.get("qualifiers") or [], f"{where}/qualifiers"):
        entry_map = _mapping(raw, f"{where}/qualifiers", "a qualifier mapping")
        _require_keys(entry_map, QUALIFIER_FIELDS, f"{where}/qualifiers", required=("kind", "statement"))
        qualifiers.append(
            Qualifier(
                kind=_string(entry_map["kind"], f"{where}/qualifiers/kind"),
                statement=_string(entry_map["statement"], f"{where}/qualifiers/statement"),
                locator=_locator(entry_map["locator"], f"{where}/qualifiers/locator", root)
                if "locator" in entry_map
                else SourceRef(),
            )
        )

    scope = ScopeDecl()
    if "scope" in item:
        scope_map = _mapping(item["scope"], f"{where}/scope", "a scope mapping")
        _require_keys(scope_map, SCOPE_FIELDS, f"{where}/scope")
        stated = scope_map.get("stated_count")
        scope = ScopeDecl(
            declared_universe=_string(scope_map.get("declared_universe", ""), f"{where}/scope/declared_universe"),
            stated_count=None if stated is None else _integer(stated, f"{where}/scope/stated_count"),
            unit=_enum(
                scope_map.get("unit", "aggregation"), {u.value: u for u in ScopeUnit}, f"{where}/scope/unit", "unit"
            ),
            members=tuple(
                _string(m, f"{where}/scope/members")
                for m in _sequence(scope_map.get("members") or [], f"{where}/scope/members")
            ),
            universe_status=_enum(
                scope_map.get("universe_status", "UNKNOWN"),
                {u.value: u for u in UniverseStatus},
                f"{where}/scope/universe_status",
                "universe_status",
            ),
            locator=_locator(scope_map["locator"], f"{where}/scope/locator", root)
            if "locator" in scope_map
            else SourceRef(),
        )

    link_ids = tuple(
        _string(raw_id, f"{where}/links") for raw_id in _sequence(item.get("links") or [], f"{where}/links")
    )
    unknown = sorted(set(link_ids) - {link.link_id for link in links})
    if unknown:
        raise ManifestError(
            P_UNRESOLVED_REF, f"{where}/links", f"link id(s) not declared in _links: {', '.join(unknown)}"
        )

    same_as: list[tuple[str, str]] = []
    for raw in _sequence(item.get("same_as") or [], f"{where}/same_as"):
        pair = _mapping(raw, f"{where}/same_as", "a same_as mapping")
        _require_keys(pair, SAME_AS_FIELDS, f"{where}/same_as", required=("claim", "basis"))
        basis = _enum(pair["basis"], {b.value: b for b in PairingBasis}, f"{where}/same_as/basis", "basis")
        same_as.append((_string(pair["claim"], f"{where}/same_as/claim"), basis.value))

    link_refs = tuple(link for link in links if link.link_id in set(link_ids))
    _check_conflicting_float_claims(where, claim_id, link_refs, index)

    return Claim(
        claim_id=claim_id,
        text=text,
        locator=locator,
        form=form,
        predicate=_string(item.get("predicate", ""), f"{where}/predicate"),
        subjects=tuple(
            _string(s, f"{where}/subjects") for s in _sequence(item.get("subjects") or [], f"{where}/subjects")
        ),
        quantifier=quantifier,
        qualifiers=tuple(qualifiers),
        scope=scope,
        link_refs=link_refs,
        same_as=tuple(same_as),
        not_audited_reason=_string(item.get("not_audited_reason", ""), f"{where}/not_audited_reason"),
    )


def _check_conflicting_float_claims(
    where: str,
    claim_id: str,
    links: tuple[EvidenceLink, ...],
    index: LatexIndex | None,
) -> None:
    """P_CONFLICTING_REF: two links for one claim that resolve to different floats (C1 vs C2)."""
    if index is None:
        return
    anchors = {
        link.target_ref for link in links if link.target_kind is TargetKind.FLOAT and isinstance(link.target_ref, str)
    }
    if len(anchors) > 1:
        raise ManifestError(
            P_CONFLICTING_REF,
            f"{where}/links",
            f"claim {claim_id} carries float targets {sorted(anchors)}; PD resolves one claim to one float per rule",
        )
