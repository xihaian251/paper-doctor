"""Bundle assembly: the manifest, the float index and the upstream artifact, joined once.

This layer owns everything mechanical, so the rules stay purely judgmental. It is also the
only place that touches the outside world: it builds the LaTeX index from the declared paper
path, and it is the sole caller of `rd_findings.load_rd_findings`, which is the sole reader of
the upstream artifact (Contract I-1 clauses 1-2). Nothing here judges the paper, and nothing
here imports `result_doctor`.

Three boundaries are enforced mechanically rather than trusted:

* the upstream bytes are tied to the declared digest before a single finding is read;
* a float body is re-derived from the index, never carried as a field on a declared object, so
  a manifest cannot smuggle in text the paper does not print;
* unrecoverable structure yields `None` and the rule reports UNKNOWN-shaped `INCONCLUSIVE`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import SourceRef
from .latex_index import FloatRecord, LatexIndex, TableGrid, body_contains_literal, build_index, parse_table
from .manifest import P_UNRESOLVED_REF, ManifestError, PDManifest, load_manifest
from .objects import Claim, EvidenceLink, FloatAnchor, TargetKind
from .rd_findings import RDBaseline, RDFinding, load_rd_findings
from .rules import NAME, QUESTION, RULE_IDS, evaluate
from .status import RuleFinding, RuleStatus

#: The object classes each rule iterates. Empty means the rule has nothing to say. PD005 reads
#: the claim list *and* the derived exclusion universe, so a claim set with no upstream
#: artifact is a genuinely different situation from no claims at all.
DRIVING_CLASS: dict[str, tuple[str, ...]] = {
    "PD001": ("claims",),
    "PD002": ("claims",),
    "PD003": ("claims", "links"),
    "PD004": ("claims", "links"),
    "PD005": ("claims", "rd"),
    "PD006": ("claims", "index"),
    "PD007": ("claims",),
}


def _class_objects(bundle: Bundle, name: str) -> tuple[Any, ...]:
    """The sized view of a driving class. `rd` and `index` are single artifacts, not lists, so
    they are counted by what they carry."""
    if name == "rd":
        return () if bundle.rd is None else bundle.rd.findings
    if name == "index":
        return () if bundle.index is None else bundle.index.floats
    value = getattr(bundle, name)
    return tuple(value or ())


@dataclass(frozen=True)
class Bundle:
    """The complete read surface PD001-PD007 are allowed to see."""

    manifest: PDManifest
    index: LatexIndex | None = None
    rd: RDBaseline | None = None

    # --- declared objects ---------------------------------------------------------------
    @property
    def root(self) -> Path:
        return self.manifest.root

    @property
    def claims(self) -> tuple[Claim, ...]:
        return self.manifest.claims

    @property
    def links(self) -> tuple[EvidenceLink, ...]:
        return self.manifest.links

    @property
    def floats(self) -> tuple[FloatAnchor, ...]:
        return self.manifest.floats

    def claim_by_id(self, claim_id: str) -> Claim | None:
        return self.manifest.claim_by_id(claim_id)

    def anchor_by_id(self, anchor_id: str) -> FloatAnchor | None:
        return self.manifest.anchor_by_id(anchor_id)

    # --- float side -----------------------------------------------------------------------
    def record_for(self, anchor: FloatAnchor) -> FloatRecord | None:
        """The indexed float a declared anchor names. Labels first, then the resolved number."""
        if self.index is None:
            return None
        for label in anchor.labels:
            record = self.index.resolve_label(label)
            if record is not None:
                return record
        return self.index.float_by_anchor(anchor.anchor_id)

    def body(self, anchor: FloatAnchor) -> str:
        """The float's own text, re-derived from the source. An unterminated float has no body."""
        record = self.record_for(anchor)
        if record is None or not record.terminated or self.index is None:
            return ""
        return self.index.float_body_text(record)

    def grid(self, anchor: FloatAnchor) -> TableGrid | None:
        body = self.body(anchor)
        record = self.record_for(anchor)
        index = self.index
        if not body or record is None or index is None:
            return None
        # The block evidence must name a source line, so the parser is given the offset -> locator
        # mapping instead of being asked to invent one from a bare body string.
        return parse_table(body, locate=lambda offset: index.position_to_source(record.begin_offset + offset))

    def anchor_evidence(self, anchor: FloatAnchor) -> tuple[SourceRef, ...]:
        refs: list[SourceRef] = []
        record = self.record_for(anchor)
        if record is not None:
            refs.append(SourceRef(path=record.source_file, line=record.begin_line))
        if anchor.caption_locator.path:
            refs.append(anchor.caption_locator)
        unique: dict[tuple[str, str, str], SourceRef] = {(r.path, r.key, str(r.line)): r for r in refs}
        return tuple(unique.values())

    def anchors_for(self, claim: Claim) -> tuple[FloatAnchor, ...]:
        """Float anchors the claim's own declared links name, in link order, deduplicated."""
        out: list[FloatAnchor] = []
        seen: set[str] = set()
        for link in claim.link_refs:
            if link.target_kind is not TargetKind.FLOAT:
                continue
            anchor = self.anchor_by_id(str(link.target_ref))
            if anchor is None or anchor.anchor_id in seen:
                continue
            seen.add(anchor.anchor_id)
            out.append(anchor)
        return tuple(out)

    def referenced_anchor_ids(self, claim: Claim) -> tuple[str, ...]:
        return tuple(anchor.anchor_id for anchor in self.anchors_for(claim))

    def referenced_bodies(self, claim: Claim) -> tuple[tuple[str, str], ...]:
        return tuple((anchor.anchor_id, body) for anchor in self.anchors_for(claim) if (body := self.body(anchor)))

    def _prints(self, literal: str, skip: frozenset[str]) -> tuple[str, ...]:
        """Every indexed float whose body prints `literal`, in document order."""
        if self.index is None:
            return ()
        out: list[str] = []
        for record in self.index.floats:
            if not record.terminated or record.anchor_id in skip:
                continue
            if body_contains_literal(self.index.float_body_text(record), literal):
                out.append(record.anchor_id)
        return tuple(out)

    def other_floats_with_literal(self, anchor: FloatAnchor, literal: str) -> tuple[str, ...]:
        return self._prints(literal, frozenset({anchor.anchor_id}))

    def floats_with_literal(self, literal: str, exclude: tuple[str, ...] = ()) -> tuple[str, ...]:
        return self._prints(literal, frozenset(exclude))

    # --- link resolution ------------------------------------------------------------------
    def link_resolves(self, link: EvidenceLink) -> bool:
        return self.link_resolution_failure(link) == ""

    def link_resolution_failure(self, link: EvidenceLink) -> str:
        """Why a declared link does not reach evidence on file. Empty string means it does.

        Resolution is a mechanical existence test on the artifact PD actually read -- never a
        judgment about whether the link is the right one scientifically.
        """
        if link.target_kind is TargetKind.FLOAT:
            anchor = self.anchor_by_id(str(link.target_ref))
            if anchor is None:
                return f"float {link.target_ref!r} is not declared in _floats"
            record = self.record_for(anchor)
            if record is None:
                return f"{anchor.anchor_id} does not resolve to a float in the indexed source"
            if not record.terminated:
                return f"{anchor.anchor_id} is an unterminated float environment in {record.source_file}"
            return ""
        if link.target_kind is TargetKind.RD_TARGET:
            if self.rd is None:
                return "no upstream findings artifact was loaded"
            if not isinstance(link.target_ref, tuple):
                return f"{link.target_ref!r} is not a [rule_id, target] pair"
            if self.rd.get(link.target_ref[0], link.target_ref[1]) is None:
                return f"upstream has no {link.target_ref[0]} finding on {link.target_ref[1]}"
            return ""
        ref = link.target_ref
        if not isinstance(ref, SourceRef) or not ref.path:
            return f"the prose target {ref!r} carries no path"
        if ".." in Path(ref.path).parts:
            return f"{ref.path} leaves the audit root"
        path = self.root / ref.path
        if not path.is_file():
            return f"{ref.path} does not exist under the audit root"
        if ref.line != "":
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) < int(ref.line):
                return f"{ref.path}:{ref.line} is past the end of the file"
        return ""

    def failed_links(self, claim: Claim) -> tuple[str, ...]:
        return tuple(
            self.link_resolution_failure(link) for link in claim.link_refs if self.link_resolution_failure(link)
        )

    # --- upstream side --------------------------------------------------------------------
    def rd_targets_for(self, claim: Claim) -> tuple[tuple[str, str], ...]:
        return tuple(
            link.target_ref
            for link in claim.link_refs
            if link.target_kind is TargetKind.RD_TARGET and isinstance(link.target_ref, tuple)
        )

    def exclusion_universe(self) -> tuple[RDFinding, ...]:
        """PD005's universe, derived mechanically upstream (Contract I-1.7): no new mechanism."""
        if self.rd is None:
            return ()
        return self.rd.exclusion_universe()


def not_run_findings(
    bundle: Bundle, findings: Iterable[RuleFinding], rule_ids: Iterable[str] | None = None
) -> list[RuleFinding]:
    """One NOT_RUN record per *requested* rule that was given nothing to judge (Phase 1 §23).

    A rule emits zero findings exactly when it has zero targets. That is a different fact from
    "the evidence does not decide" (INCONCLUSIVE) and from "this target has no such dependency"
    (NOT_APPLICABLE), and unlike those two it is not something the rule can say for itself,
    because it says nothing at all.

    Rules outside the requested set are not reported at all: "you did not ask me" is a fourth
    fact, and putting it in the NOT_RUN channel would corrupt the partial-audit signal.
    """
    ran = {finding.rule_id for finding in findings}
    requested = tuple(rule_ids) if rule_ids is not None else RULE_IDS
    out: list[RuleFinding] = []
    for rule_id in requested:
        if rule_id in ran:
            continue
        classes = DRIVING_CLASS[rule_id]
        objects = [_class_objects(bundle, name) for name in classes]
        populated = [name for name, value in zip(classes, objects, strict=True) if value]
        if populated:
            listed = ", ".join(classes)
            reason = (
                f"no target was supplied for this rule: {listed} is populated, but nothing in it carries the key "
                f"{rule_id} reads"
            )
        else:
            reason = f"no target of this class was supplied ({', '.join(classes)} is empty)"
        out.append(
            RuleFinding(
                rule_id,
                NAME[rule_id],
                f"rule:{rule_id}",
                RuleStatus.NOT_RUN,
                QUESTION[rule_id],
                {
                    "driving_object_class": ",".join(classes),
                    "n_objects": sum(len(value) for value in objects),
                    "n_targets": 0,
                },
                (),
                reason,
            )
        )
    return out


def audit_bundle(bundle: Bundle, rule_ids: Iterable[str] | None = None) -> list[RuleFinding]:
    """The seven rules plus the entry layer's NOT_RUN records, in canonical order."""
    ids = tuple(rule_ids) if rule_ids is not None else RULE_IDS
    findings = evaluate(bundle, ids)
    return sorted([*findings, *not_run_findings(bundle, findings, ids)], key=lambda f: (f.rule_id, f.target))


def bundle_from_manifest(path: str | Path) -> Bundle:
    """Read every declared artifact once and join them. Raises `ManifestError` on a bad contract.

    The manifest is validated twice on purpose. The first pass yields the audit root and the
    declared paper path, which is what the LaTeX index needs; the second pass re-validates
    *with* that index, so a declared float number is checked against the document's own numbering
    (P_CONFLICTING_REF) and a claim locator is checked against the document body (FM-P11).
    """
    preliminary = load_manifest(path)
    index = _index_for(preliminary)
    manifest = load_manifest(path, index=index) if index is not None else preliminary
    return _bundle_with(manifest, index)


def _index_for(manifest: PDManifest) -> LatexIndex | None:
    """Index the declared paper. Only a `.tex` root has float numbering to recover; anything
    else yields no index, and the rules say so rather than guessing."""
    paper_file = manifest.root / manifest.paper.path
    if not paper_file.is_file():
        raise ManifestError(
            P_UNRESOLVED_REF,
            "_registry/paper/path",
            f"{manifest.paper.path} is not a readable file under the audit root",
        )
    if paper_file.suffix != ".tex":
        return None
    return build_index(manifest.root, paper_file)


def _bundle_with(manifest: PDManifest, index: LatexIndex | None) -> Bundle:
    rd = load_rd_findings(
        manifest.rd.path,
        expected_sha256=manifest.rd.sha256,
        expected_size=manifest.rd.size,
        declared_rd_version=manifest.rd.rd_version,
    )
    return Bundle(manifest=manifest, index=index, rd=rd)


def build_bundle(manifest: PDManifest) -> Bundle:
    """Join an already-validated manifest with the float index and the upstream artifact."""
    return _bundle_with(manifest, _index_for(manifest))


def audit_manifest(path: str | Path, rule_ids: Iterable[str] | None = None) -> list[RuleFinding]:
    """`paper-doctor.yml` -> bundle -> PD001-PD007.

    Raises `ManifestError` only for a manifest that cannot be read as a contract; a manifest
    thin on evidence audits successfully and says so in statuses.
    """
    return audit_bundle(bundle_from_manifest(path), rule_ids)
