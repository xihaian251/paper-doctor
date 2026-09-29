"""The frozen object model (Phase 0 §14): three claim-side objects, everything else reused.

Each field exists because a real failure mode required it; the reverse-derivation comment
on each field names that failure mode. `Locus.quantity_key` semantics are not re-implemented
here — quantity identity enters Paper Doctor only through a declaration on a `FloatAnchor`
or an `EvidenceLink`, and two cells are comparable solely once both declare the same quantity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .evidence import Grade, SourceRef
from .status import UniverseStatus


class ClaimForm(str, Enum):
    """The six and only six claim classes (Phase 0 §13)."""

    NUMERIC_ATTRIBUTION = "NUMERIC_ATTRIBUTION"
    COMPARATIVE = "COMPARATIVE"
    SUPERLATIVE = "SUPERLATIVE"
    SCOPE = "SCOPE"
    QUALIFICATION = "QUALIFICATION"
    REFERENCE_ATTRIBUTION = "REFERENCE_ATTRIBUTION"


class Quantifier(str, Enum):
    """FM-P07 / S13: whether a claim enumerates or merely asserts existence."""

    ALL = "all"
    MOST = "most"
    SOME = "some"
    BARE = "bare"
    NUMERIC = "numeric"


class TargetKind(str, Enum):
    FLOAT = "FLOAT"
    RD_TARGET = "RD_TARGET"
    PROSE = "PROSE"


class LinkBasis(str, Enum):
    """The only three origins a link may have (Phase 0 §4). Nothing else creates a link."""

    AUTHOR_REF_IN_SENTENCE = "AUTHOR_REF_IN_SENTENCE"
    AUTHOR_NAMED_FLOAT = "AUTHOR_NAMED_FLOAT"
    AUDITOR_DECLARED = "AUDITOR_DECLARED"


class PairingBasis(str, Enum):
    """Encoding of §15's "INFERRED is at most SUGGESTED" for PD007's `same_as` pairs.

    A `SUGGESTED` pairing is not an `EvidenceLink` and cannot satisfy PD001; it can only
    make PD007 INCONCLUSIVE.
    """

    DECLARED = "declared"
    SUGGESTED = "suggested"


class ScopeUnit(str, Enum):
    """The three non-interchangeable count units (PD002 unit discipline)."""

    AGGREGATION = "aggregation"
    REPORTED_CELL = "reported_cell"
    COMPARISON_MEMBER = "comparison_member"


@dataclass(frozen=True)
class ResultArtifact:
    """Reused from upstream without change, minus `produced_by` (a run-production concept
    that a `.tex` file and a findings JSON do not have)."""

    path: str = ""
    sha256: str = ""
    size: int = 0
    columns: tuple[str, ...] = ()
    superseded_from: tuple[str, ...] = ()
    superseded_by: tuple[str, ...] = ()
    required_columns: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class Qualifier:
    """FM-P03 / FM-P05: a data-removal, precision, or subset statement carried by a claim."""

    kind: str = ""
    statement: str = ""
    locator: SourceRef = field(default_factory=SourceRef)


@dataclass(frozen=True)
class ScopeDecl:
    """FM-P02: the universe the claim speaks about, plus the unit any count in it is in."""

    declared_universe: str = ""
    stated_count: int | None = None
    unit: ScopeUnit = ScopeUnit.AGGREGATION
    members: tuple[str, ...] = ()
    universe_status: UniverseStatus = UniverseStatus.UNKNOWN
    locator: SourceRef = field(default_factory=SourceRef)


@dataclass(frozen=True)
class Claim:
    """One audited sentence fragment, verbatim, at a verified locator."""

    claim_id: str
    paper_id: ResultArtifact = field(default_factory=ResultArtifact)
    text: str = ""  # OBSERVED verbatim, verified against the corpus line
    text_grade: Grade = Grade.DIRECT
    locator: SourceRef = field(default_factory=SourceRef)
    form: ClaimForm = ClaimForm.NUMERIC_ATTRIBUTION
    predicate: str = ""  # FM-P04/05/06: the comparison/superlative/adverb verb
    subjects: tuple[str, ...] = ()  # FM-P04
    quantifier: Quantifier = Quantifier.BARE
    qualifiers: tuple[Qualifier, ...] = ()
    scope: ScopeDecl = field(default_factory=ScopeDecl)
    link_refs: tuple[EvidenceLink, ...] = field(default_factory=tuple)  # PD001
    same_as: tuple[tuple[str, str], ...] = ()  # (claim_id, PairingBasis.value); PD007 target set
    not_audited_reason: str = ""


@dataclass(frozen=True)
class FloatAnchor:
    """A float as the paper's own numbering resolved it, plus the author's declarations."""

    float_id: str = ""
    kind: str = ""  # "table" | "figure"
    number: int = 0
    source_file: str = ""  # provenance of the numbering
    begin_line: int = 0
    labels: tuple[str, ...] = ()
    caption_locator: SourceRef = field(default_factory=SourceRef)
    quantity_declaration: str = ""  # RTDL D9 / GMMVI C10: "the negated ELBO", "Acc."
    precision_declaration: str = ""  # FM-P06: per-float tolerance
    mark_rule_declaration: str = ""  # RTDL D4: "top = not statistically significant"
    referenced_by: tuple[int, ...] = ()  # orphan detection, measurement only
    number_grade: Grade = Grade.DERIVED

    @property
    def anchor_id(self) -> str:
        return f"{self.kind}:{self.number}"


@dataclass(frozen=True)
class EvidenceLink:
    """The only edge Paper Doctor is allowed to judge across: claim -> one named target."""

    link_id: str = ""
    claim_ref: str = ""
    target_kind: TargetKind = TargetKind.FLOAT
    #: `float_id` for FLOAT, `(rule_id, target)` for RD_TARGET, `SourceRef` for PROSE.
    target_ref: str | SourceRef | tuple[str, str] = ""
    link_basis: LinkBasis = LinkBasis.AUDITOR_DECLARED
    quantity_identity: str = ""  # RTDL §10.1: without an explicit identity, PD003 is INCONCLUSIVE
    grade: Grade = Grade.DERIVED
