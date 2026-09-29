"""PD001-PD007: deterministic claim-to-evidence judgments, one `evaluate` per rule.

Nothing here aggregates. There is no paper score, no composite index and no overall verdict
(Phase 0 §19 lines 10-13), and no rule re-audits an upstream Result Doctor finding: an RD
verdict is *read* as evidence about the evidence, and it can only ever preserve or downgrade
Paper Doctor's certainty, never upgrade it (Contract I-1 clause 5).

Three things are common to every rule and stated once here rather than seven times:

* `PASS` means "on this narrow relation the claim agrees with the evidence" -- nothing more.
* Missing evidence is `INCONCLUSIVE`, never `FAIL` (a gap is not a contradiction).
* A judgment needs a witness that is OBSERVED, or DERIVED from an explicit structure (float
  numbering, `\ref` resolution, key equality, parsed cell text). A declaration *unlocks* a
  comparison; on its own it never produces a `PASS`.

The declared-qualifier kinds this module reads (`precision`, `comparison_basis`, `comparison_block`,
`threshold`, `generic_coverage`, `reconciliation`) reuse §14's `Qualifier(kind, statement, locator)`
instead of adding a field or an object: Phase 1 may not create a fourth object, and `kind` is a free
string by construction.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from .evidence import SourceRef
from .latex_index import (
    TableGrid,
    TableRow,
    body_contains_literal,
    collapse_digit_groups,
    plain_text,
)
from .objects import Claim, ClaimForm, EvidenceLink, FloatAnchor, PairingBasis, Quantifier, ScopeUnit, TargetKind
from .rd_findings import RDFinding
from .status import RuleFinding, RuleStatus, UniverseStatus

if TYPE_CHECKING:
    from .audit import Bundle

RULE_IDS: tuple[str, ...] = ("PD001", "PD002", "PD003", "PD004", "PD005", "PD006", "PD007")

QUESTION = {
    "PD001": "does this claim have at least one explicitly based support link?",
    "PD002": "does the scope the claim states match the scope of the evidence as declared or recovered?",
    "PD003": "does the number the claim states equal the number printed at the locus the claim resolves to?",
    "PD004": "over the comparison set the claim resolves to, does the stated relation hold for every member?",
    "PD005": "does the claim carry every qualification that the evidence carries?",
    "PD006": "does the reference in the claim resolve to the float that actually carries the attributed content?",
    "PD007": "do two claims with the same predicate and subjects state the same proposition?",
}

NAME = {
    "PD001": "Claim Traceability",
    "PD002": "Evidence Scope Consistency",
    "PD003": "Quantitative Claim Consistency",
    "PD004": "Comparative Claim Support",
    "PD005": "Qualification Preservation",
    "PD006": "Result Reference Integrity",
    "PD007": "Cross-Section Claim Consistency",
}

UNIT_ORDER = ("aggregation", "reported_cell", "comparison_member")

#: Closed vocabularies. Membership is a string test on the claim's own verbatim text; nothing
#: here is a semantic classifier, and an unmatched intensifier simply stays unclassified.
_ABSOLUTIVES = frozenset({"exactly", "all", "always", "every", "never", "solely", "only", "fully"})
_INTENSIFIERS = frozenset(
    {"clearly", "significantly", "consistently", "substantially", "notably", "dramatically", "considerably", "markedly"}
)

_CITE = re.compile(r"\\(?:cite[a-zA-Z]*|label|includegraphics|ref|autoref|eqref)\s*(?:\[[^\]]*\])?\{[^{}]*\}")
_NAMED_FLOAT = re.compile(r"\b(?:Tables?|Figures?|Tab\.|Fig\.)\s*~?\s*\d+")
_REF_MACROS = re.compile(r"\\(?:auto)?ref\{([^}]*)\}")
_NAMED_FLOAT_NUMBER = re.compile(r"\b(?:Tables?|Figures?)\s*~?\s*(\d+)")
#: A literal *including* its sign. Dropping a leading minus would compare `-0.499` and `0.499`
#: as the same string, and PD003 would PASS a sign error -- a false PASS, which §19 forbids.
_LITERAL = re.compile(r"(?<![\w.,])[-−]?\d+(?:\.\d+)?(?![\w.])")
_WORD = re.compile(r"[A-Za-z]+")
_ROUND = re.compile(r"(?:round|precision|digits?)\s*[:=]?\s*(\d+)", re.IGNORECASE)
_TOLERANCE = re.compile(r"(?:±|\+/-|tolerance\s*[:=]?)\s*([\d.]+)", re.IGNORECASE)


def _f(
    rule_id: str,
    target: str,
    status: RuleStatus,
    *,
    measurements: dict[str, Any] | None = None,
    evidence: tuple[SourceRef, ...] = (),
    reason: str = "",
) -> RuleFinding:
    """The only finding constructor the rules use: rule_name and question come from the frozen
    tables, never from a per-site string, so a PD finding and an RD finding serialize alike."""
    return RuleFinding(
        rule_id=rule_id,
        rule_name=NAME[rule_id],
        target=target,
        status=status,
        question=QUESTION[rule_id],
        measurements=dict(measurements or {}),
        evidence=evidence,
        reason=reason,
    )


# --- text-level helpers (all literal, none semantic) ---------------------------------------


def _norm(text: str) -> str:
    return " ".join(text.split())


def attribution_text(text: str) -> str:
    """The claim's own words with cross-references removed, so a referenced float's number is
    never mistaken for an attributed value."""
    return _NAMED_FLOAT.sub(" ", _CITE.sub(" ", text))


def literals(text: str) -> tuple[str, ...]:
    r"""Every value the claim itself states, cross-reference furniture removed.

    A digit group written with a thin-space macro (`$26\,048$`) is one value, matching the reading
    the cells get -- the two sides of a comparison are extracted by the same rule.

    A typographic minus (U+2212) is canonicalised to an ASCII minus: the two are the same number
    written by two engines, and keeping them distinct would make PD003 FAIL a claim whose cell
    agrees with it.
    """
    return tuple(
        match.group(0).replace("\u2212", "-")
        for match in _LITERAL.finditer(collapse_digit_groups(attribution_text(text)))
    )


def ref_labels(text: str) -> tuple[str, ...]:
    return tuple(_REF_MACROS.findall(text))


def named_float_numbers(text: str) -> tuple[int, ...]:
    return tuple(int(number) for number in _NAMED_FLOAT_NUMBER.findall(text))


def words(text: str) -> frozenset[str]:
    return frozenset(word.lower() for word in _WORD.findall(attribution_text(text)))


def _qualifier_statement(claim: Claim, kind: str) -> str:
    return next((q.statement for q in claim.qualifiers if q.kind == kind), "")


def _precision(declaration: str) -> tuple[str, float] | None:
    """`("round", digits)` or `("tolerance", amount)` -- or None, which means undeclared."""
    if not declaration:
        return None
    rounded = _ROUND.search(declaration)
    if rounded is not None:
        return ("round", float(rounded.group(1)))
    tolerance = _TOLERANCE.search(declaration)
    if tolerance is not None:
        return ("tolerance", float(tolerance.group(1)))
    return None


def _number(text: str) -> float | None:
    found = _LITERAL.search(plain_text(text))
    if found is None:
        return None
    try:
        return float(found.group(0).replace("\u2212", "-"))
    except ValueError:
        return None


def _unit_of(claim: Claim) -> ScopeUnit:
    return claim.scope.unit


def _declare_unit(unit: ScopeUnit) -> str:
    return f"unit={unit.value}"


# --- block addressing (Phase 2 §3, §13) ----------------------------------------------------

#: The spelling a declaration uses to say *which* structural block it means: the block key the
#: parser derived from the source's own group headers, rules and merges (`block=b2`). A bare key
#: is accepted too, because `statement` is the author's own prose. Nothing here reads what the
#: block means; the declaration only selects an address that the source already states.
_BLOCK_STATEMENT = re.compile(r"block\s*[:=]\s*([A-Za-z0-9_.-]+)")
_BARE_BLOCK = re.compile(r"^[A-Za-z0-9_.-]+$")


def _declared_block(claim: Claim) -> str:
    r"""The block name a claim declares, or `""` when it declares none.

    `block=b2` and a bare `b2` both name a block. Anything else -- an empty statement, prose, a
    half-written key -- names nothing, and is read as *undeclared* rather than as a block whose name
    is that text. The distinction matters: a declaration of nothing must fall into the ambiguous-row
    path and say which blocks exist, while a declaration of a block the table does not print must be
    honoured literally and find no row.
    """
    statement = _qualifier_statement(claim, "comparison_block").strip()
    found = _BLOCK_STATEMENT.search(statement)
    if found is not None:
        return found.group(1)
    return statement if _BARE_BLOCK.match(statement) else ""


def _row_address(grid: TableGrid, label: str, block: str) -> tuple[TableRow | None, str]:
    r"""Pick one printed row, and return the clause that says *how* it was picked.

    A label the source prints in two structural blocks is addressable only when the declaration
    names the block. Taking the first match, the numerically nearer one, or the one a caption
    seems to describe would be a silent choice of evidence (Phase 2 §1, §17).

    A label printed by several rows of the *same* block is refused too, and the reason says which
    of the two situations happened: a table that prints the label nowhere has no ambiguity to
    resolve, and a table that prints it twice under one vertical merge does. Collapsing both into
    "no row is addressed" tells the reader the paper is silent when the paper is ambiguous.
    """
    if block:
        row = grid.row(label, block) or grid.row_containing(label, block)
        if row is None:
            return None, f"block {block!r} prints no row addressed by {label!r}"
        return row, f"block={block} [{grid.block_basis(block)}]"
    blocks = grid.blocks_for(label)
    if len(blocks) > 1:
        separated = "; ".join(f"{key} <- {grid.block_basis(key)}" for key in blocks)
        return None, (
            f"{label!r} is printed in {len(blocks)} structural blocks ({separated}); the claim declares no block"
        )
    row = grid.row(label) or grid.row_containing(label)
    if row is not None:
        return row, f"block={row.block_key} [{grid.block_basis(row.block_key)}]"
    wanted = plain_text(label).lower()
    printed = [r for r in grid.rows if plain_text(r.label).lower() == wanted]
    if len(printed) > 1:
        inside = ", ".join(sorted({r.block_key for r in printed}))
        return None, (
            f"{label!r} is printed by {len(printed)} rows of {inside}; the source states no structure that "
            "separates them, so the declared address has more than one reading"
        )
    return None, f"no row is addressed by {label!r}"


# --- shared evidence / propagation ---------------------------------------------------------


def _claim_evidence(claim: Claim, extra: tuple[SourceRef, ...] = ()) -> tuple[SourceRef, ...]:
    refs: list[SourceRef] = []
    if claim.locator.path:
        refs.append(claim.locator)
    for link in claim.link_refs:
        if isinstance(link.target_ref, SourceRef) and link.target_ref.path:
            refs.append(link.target_ref)
    refs.extend(extra)
    seen: set[tuple[str, str, str]] = set()
    unique: list[SourceRef] = []
    for ref in refs:
        key = (ref.path, ref.key, str(ref.line))
        if key not in seen:
            seen.add(key)
            unique.append(ref)
    return tuple(unique)


def _upstream_evidence(findings: tuple[RDFinding, ...]) -> tuple[SourceRef, ...]:
    """Contract I-1 clause 5: upstream SourceRefs are propagated so provenance survives a hop."""
    return tuple(ref for finding in findings for ref in finding.evidence)


def _downstream(bundle: Bundle, claim: Claim) -> tuple[tuple[RDFinding, ...], RuleStatus | None, str]:
    """The linked upstream findings, the strongest gate they impose, and its propagated reason.

    `FAIL` or `INCONCLUSIVE` upstream caps the dependent judgment at `INCONCLUSIVE`;
    `NOT_RUN`/`NOT_APPLICABLE` upstream means "no downstream judgment exists", which does not
    stop PD from judging a relation RD cannot see (clause 5).
    """
    refs = bundle.rd_targets_for(claim)
    if bundle.rd is None or not refs:
        return (), None, ""
    resolved = {pair: bundle.rd.get(pair[0], pair[1]) for pair in refs}
    findings = tuple(finding for finding in resolved.values() if finding is not None)
    absent = sorted(f"{rule_id}:{target}" for (rule_id, target), finding in resolved.items() if finding is None)
    fail = next((f for f in findings if f.status is RuleStatus.FAIL), None)
    if fail is not None:
        return findings, RuleStatus.FAIL, f"downstream {fail.rule_id} on {fail.target} is FAIL: {fail.reason}"
    inconclusive = next((f for f in findings if f.status is RuleStatus.INCONCLUSIVE), None)
    if inconclusive is not None:
        return (
            findings,
            RuleStatus.INCONCLUSIVE,
            f"downstream {inconclusive.rule_id} on {inconclusive.target} is INCONCLUSIVE: {inconclusive.reason}",
        )
    note = ""
    if absent:
        note = f"no downstream finding exists for {', '.join(absent)}"
    elif not findings:
        note = "no downstream judgment exists on the linked targets"
    return findings, None, note


#: The limitation PD copies into a reason when an in-scope RD002 finding really is inconclusive:
#: RD002's inconclusiveness is about run-id binding, not about the enumeration PD005 tests, but
#: the author has to see both.
_RD002_LIMIT = "upstream RD002 on these targets is INCONCLUSIVE (member-to-run binding and criterion recomputability)"


def _limitation(findings: tuple[RDFinding, ...]) -> str:
    """The RD002 caveat, or the empty string when no in-scope finding is INCONCLUSIVE.

    Contract I-1 lets PD preserve or downgrade upstream uncertainty, never invent it: a reason
    that asserts an INCONCLUSIVE RD002 over a set of findings that actually PASSed misstates
    the upstream verdict.
    """
    reason = next((f.reason for f in findings if f.status is RuleStatus.INCONCLUSIVE), "")
    return f"; {_RD002_LIMIT}: {reason}" if reason else ""


# --- PD001 Claim Traceability --------------------------------------------------------------


def _is_out_of_universe(claim: Claim) -> bool:
    return bool(claim.not_audited_reason)


def pd001(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    for claim in bundle.claims:
        bases = tuple(sorted(link.link_basis.value for link in claim.link_refs))
        measurements: dict[str, Any] = {"n_links": len(claim.link_refs), "link_basis": bases, "target_resolved": False}
        if _is_out_of_universe(claim):
            out.append(
                _f(
                    "PD001",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim),
                    reason=f"out of the audited universe by declaration: {claim.not_audited_reason}",
                )
            )
            continue
        resolved = [link for link in claim.link_refs if bundle.link_resolves(link)]
        measurements["target_resolved"] = bool(resolved)
        measurements["n_links_resolved"] = len(resolved)
        if not claim.link_refs:
            out.append(
                _f(
                    "PD001",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim),
                    reason="the claim carries no declared support link; untraceable is not false",
                )
            )
            continue
        if not resolved:
            out.append(
                _f(
                    "PD001",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim),
                    reason="no declared link resolves to evidence on file: "
                    + "; ".join(bundle.link_resolution_failure(link) for link in claim.link_refs),
                )
            )
            continue
        out.append(
            _f(
                "PD001",
                claim.claim_id,
                RuleStatus.PASS,
                measurements=measurements,
                evidence=_claim_evidence(claim, _upstream_evidence(_downstream(bundle, claim)[0])),
                # Distinct bases in the prose; `measurements["link_basis"]` stays one entry per link.
                reason="declared link(s) with basis "
                + ", ".join(sorted(set(bases)))
                + f" resolve to evidence on file ({_targets_of(tuple(resolved))})",
            )
        )
    return out


def _targets_of(links: tuple[EvidenceLink, ...]) -> str:
    return ", ".join(sorted(bundle_target_text(link) for link in links))


def bundle_target_text(link: EvidenceLink) -> str:
    if isinstance(link.target_ref, tuple):
        return f"{link.target_ref[0]}:{link.target_ref[1]}"
    if isinstance(link.target_ref, SourceRef):
        return link.target_ref.label()
    return str(link.target_ref)


# --- PD002 Evidence Scope Consistency ------------------------------------------------------

#: The rule that certifies membership in each count unit. A count PD reads from a rule that is
#: itself undecided cannot support either a PASS or a FAIL about that count.
_CERTIFYING_RULE = {
    ScopeUnit.AGGREGATION: "RD002",
    ScopeUnit.REPORTED_CELL: "RD005",
    ScopeUnit.COMPARISON_MEMBER: "RD002",
}
_COUNT_KEY = {
    ScopeUnit.AGGREGATION: "n_members",
    ScopeUnit.REPORTED_CELL: "n",
    ScopeUnit.COMPARISON_MEMBER: "n_members",
}


def _in_scope_class(claim: Claim) -> bool:
    if claim.form is ClaimForm.SCOPE:
        return True
    return bool(claim.scope.declared_universe or claim.scope.members or claim.scope.stated_count is not None)


def _scope_source(bundle: Bundle, claim: Claim) -> tuple[tuple[RDFinding, ...], str]:
    """Which upstream findings carry the count the claim speaks about, and how they were picked.

    Selection is by explicit key equality only: the caption's own sentence matched against the
    upstream `spread_label`, or the claim's declared `(rule_id, target)` links. Never by
    proximity, adjacency or similarity.
    """
    if bundle.rd is None:
        return (), "no upstream artifact"
    unit = _unit_of(claim)
    rule_id = _CERTIFYING_RULE[unit]
    all_of_rule = bundle.rd.by_rule(rule_id)
    labelled = tuple(
        finding
        for finding in all_of_rule
        if isinstance(finding.measurements.get("spread_label"), str)
        and _norm(finding.measurements["spread_label"]) == _norm(claim.text)
    )
    if labelled:
        return labelled, "spread_label equal to the claim's sentence"
    refs = bundle.rd_targets_for(claim)
    if refs:
        picked = tuple(finding for finding in (bundle.rd.get(r, t) for r, t in refs) if finding is not None)
        if picked:
            return picked, "the claim's declared (rule_id, target) links"
    return (), "nothing declares which upstream targets this scope covers"


def pd002(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    for claim in bundle.claims:
        if _is_out_of_universe(claim) or not _in_scope_class(claim):
            continue
        unit = _unit_of(claim)
        stated = claim.scope.stated_count
        measurements: dict[str, Any] = {
            "unit": unit.value,
            "stated_count": stated,
            "n_members_listed": len(claim.scope.members),
            "universe_status": claim.scope.universe_status.value,
        }
        evidence = _claim_evidence(claim)
        if stated is None:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"the claim states no count ({_declare_unit(unit)}); nothing to compare"
                        + (
                            f" -- its enumeration of {len(claim.scope.members)} member(s) is PD005's relation"
                            if claim.scope.members
                            else ""
                        )
                    ),
                )
            )
            continue
        findings, basis = _scope_source(bundle, claim)
        measurements["n_targets_compared"] = len(findings)
        measurements["selection_basis"] = basis
        if not findings:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"the stated scope ({_declare_unit(unit)}) cannot be bound to upstream targets: {basis}",
                )
            )
            continue
        key = _COUNT_KEY[unit]
        counts = {finding.target: finding.known_measure(key) for finding in findings}
        unknown = sorted(target for target, value in counts.items() if value is None)
        divergent = sorted(
            f"{target} ({value!r})"
            for target, value in counts.items()
            if isinstance(value, int) and stated is not None and value != stated
        )
        exclusions = {finding.target: finding.n_exclusions for finding in findings if finding.n_exclusions > 0}
        measurements["n_counts_unknown"] = len(unknown)
        measurements["n_counts_divergent"] = len(divergent)
        measurements["n_targets_with_exclusions"] = len(exclusions)
        certified = all(finding.status is RuleStatus.PASS for finding in findings)
        statuses = {finding.status.value for finding in findings}
        measurements["upstream_statuses"] = sorted(statuses)

        if divergent and certified:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.FAIL,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                    reason=(
                        f"the claim states {stated} ({_declare_unit(unit)}) but {_COUNT_KEY[unit]} differs on "
                        f"{len(divergent)} of {len(findings)} compared targets: {', '.join(divergent)}"
                        + (f"; {len(unknown)} targets carry no {key}" if unknown else "")
                        + (
                            f"; {len(exclusions)} targets carry exclusions the stated count does not describe"
                            if exclusions
                            else ""
                        )
                    ),
                )
            )
            continue
        if divergent:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                    reason=(
                        f"{len(divergent)} of {len(findings)} compared targets differ from the stated {stated} "
                        f"({_declare_unit(unit)}) but upstream is {'/'.join(sorted(statuses))}, "
                        f"so the count is not certified{_limitation(findings)}"
                    ),
                )
            )
            continue
        if unit is ScopeUnit.AGGREGATION and exclusions and stated is not None:
            shrunk = sorted(f"{target} (-{n})" for target, n in exclusions.items())
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.FAIL,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                    reason=(
                        f"the claim states {stated} ({_declare_unit(unit)}) and every target reports {stated} members, "
                        f"but the effective counts after exclusions differ: {', '.join(shrunk)}"
                    ),
                )
            )
            continue
        if claim.scope.universe_status is not UniverseStatus.RECOVERED:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                    reason=(
                        f"the counts agree ({_declare_unit(unit)}, {len(findings)} targets) but the universe is "
                        f"{claim.scope.universe_status.value}: an unlisted universe cannot be PASSed"
                    ),
                )
            )
            continue
        if not certified:
            out.append(
                _f(
                    "PD002",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                    reason=(
                        f"counts agree ({_declare_unit(unit)}) but upstream is "
                        f"{'/'.join(sorted(statuses))}{_limitation(findings)}"
                        + (f"; {len(unknown)} targets carry no {key}" if unknown else "")
                    ),
                )
            )
            continue
        out.append(
            _f(
                "PD002",
                claim.claim_id,
                RuleStatus.PASS,
                measurements=measurements,
                evidence=_claim_evidence(claim, _upstream_evidence(findings)),
                reason=(
                    f"the stated scope agrees on all {len(findings)} compared targets "
                    f"({_declare_unit(unit)}, upstream PASS, universe RECOVERED)"
                ),
            )
        )
    return out


# --- PD003 Quantitative Claim Consistency --------------------------------------------------


def _cell_locator(claim: Claim) -> tuple[str, str] | None:
    """A `[path,column,row]` locus gives the printed cell by *name*. Without one the comparison
    is presence of the literal inside the float body."""
    for link in claim.link_refs:
        key = link.target_ref.key if isinstance(link.target_ref, SourceRef) else ""
        if key.startswith("column=") and ",row=" in key:
            column, _, row = key[len("column=") :].rpartition(",row=")
            return column, row
    return None


def _identity(bundle: Bundle, claim: Claim, anchor: FloatAnchor) -> tuple[bool, str]:
    """Quantity identity is declared on both sides and compared by string equality (DERIVED)."""
    declared = {link.quantity_identity for link in claim.link_refs if link.quantity_identity}
    if not anchor.quantity_declaration or not declared:
        return False, "undeclared"
    if anchor.quantity_declaration in declared:
        return True, "link quantity_identity equal to the float's quantity_declaration"
    return False, f"declared identities disagree ({sorted(declared)} vs {anchor.quantity_declaration!r})"


def pd003(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    for claim in bundle.claims:
        if _is_out_of_universe(claim) or claim.form is not ClaimForm.NUMERIC_ATTRIBUTION:
            continue
        values = literals(claim.text)
        anchors = bundle.anchors_for(claim)
        measurements: dict[str, Any] = {
            "claim_value": values[0] if len(values) == 1 else None,
            "n_literals": len(values),
            "cell_value": None,
            "delta": None,
            "identity_basis": "no float link",
            "n_float_links": len(anchors),
        }
        evidence = _claim_evidence(claim)
        if not values:
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="the claim states no numeric literal",
                )
            )
            continue
        if len(values) > 1:
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"the claim states {len(values)} numeric literals ({', '.join(values)}); "
                    "no single attributed value is declared",
                )
            )
            continue
        if not anchors:
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="no declared link resolves to a float, so the printed side of the comparison is unknown",
                )
            )
            continue
        anchor = anchors[0]
        body = bundle.body(anchor)
        if not body:
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=f"the body of {anchor.anchor_id} is not recoverable from the source",
                )
            )
            continue
        value = values[0]
        equal, identity_basis = _identity(bundle, claim, anchor)
        measurements["identity_basis"] = identity_basis
        located = _cell_locator(claim)
        cell: str | None = None
        addressed = ""
        cell_address = ""
        if located is not None:
            grid = bundle.grid(anchor)
            column, row = located
            if grid is None:
                out.append(
                    _pd003_inconclusive(bundle, claim, measurements, anchor, "the tabular structure is unrecoverable")
                )
                continue
            row_record, addressed = _row_address(grid, row, _declared_block(claim))
            if row_record is None:
                out.append(
                    _pd003_inconclusive(
                        bundle,
                        claim,
                        measurements,
                        anchor,
                        f"the declared cell address (column={column!r}, row={row!r}, "
                        f"{_declare_unit(ScopeUnit.REPORTED_CELL)}) is not addressable in "
                        f"{anchor.anchor_id}: {addressed}",
                    )
                )
                continue
            index = grid.column_index(column)
            if index is None:
                out.append(
                    _pd003_inconclusive(
                        bundle,
                        claim,
                        measurements,
                        anchor,
                        f"the declared cell address (column={column!r}, row={row!r}, {addressed}, "
                        f"{_declare_unit(ScopeUnit.REPORTED_CELL)}) names no column of {anchor.anchor_id}",
                    )
                )
                continue
            cell = row_record.cell(index)
            measurements["cell_value"] = cell
            cell_address = f"column={column}, row={row}, {addressed}, {_declare_unit(ScopeUnit.REPORTED_CELL)}"
        else:
            present = body_contains_literal(body, value)
            other = bundle.other_floats_with_literal(anchor, value)
            if not present and other:
                out.append(
                    _pd003_inconclusive(
                        bundle,
                        claim,
                        measurements,
                        anchor,
                        f"{value} is not printed in {anchor.anchor_id}; it prints in {', '.join(other)} "
                        "-- the attribution itself is PD006's finding, not a value mismatch here",
                    )
                )
                continue
            if not present:
                out.append(
                    _pd003_inconclusive(
                        bundle, claim, measurements, anchor, f"{value} is not printed in any parsed float"
                    )
                )
                continue
        _, gate, gate_reason = _downstream(bundle, claim)
        if gate is RuleStatus.FAIL:
            out.append(
                _pd003_inconclusive(
                    bundle, claim, measurements, anchor, f"{gate_reason} (PD does not upgrade upstream certainty)"
                )
            )
            continue
        if cell is None:
            if not equal:
                out.append(
                    _pd003_inconclusive(
                        bundle,
                        claim,
                        measurements,
                        anchor,
                        f"quantity identity {identity_basis}; DECLARED-only support cannot PASS",
                    )
                )
                continue
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.PASS,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=(
                        f"the stated value {value} is printed verbatim in {anchor.anchor_id} "
                        "under an identical declared quantity"
                    ),
                )
            )
            continue
        claimed_number = _number(value)
        cell_number = _number(cell)
        if claimed_number is None or cell_number is None:
            out.append(
                _pd003_inconclusive(
                    bundle, claim, measurements, anchor, "a side of the comparison is not a plain number"
                )
            )
            continue
        delta = round(abs(claimed_number - cell_number), 12)
        measurements["delta"] = delta
        precision = _precision(anchor.precision_declaration) or _precision(_qualifier_statement(claim, "precision"))
        string_equal = _norm(value) == _norm(cell)
        if string_equal:
            status = RuleStatus.PASS if equal else RuleStatus.INCONCLUSIVE
            reason = (
                f"the prose value and the printed cell at ({cell_address}) of {anchor.anchor_id} are the same string"
                if equal
                else f"the strings agree but quantity identity is {identity_basis}"
            )
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    status,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=reason,
                )
            )
            continue
        if precision is None:
            out.append(
                _pd003_inconclusive(
                    bundle,
                    claim,
                    measurements,
                    anchor,
                    f"{value} vs the printed {cell} at ({cell_address}) with no declared "
                    "precision semantics; "
                    "closeness is not a PASS",
                )
            )
            continue
        if not equal:
            out.append(
                _pd003_inconclusive(
                    bundle,
                    claim,
                    measurements,
                    anchor,
                    f"quantity identity is {identity_basis}, so the two sides are not declared comparable",
                )
            )
            continue
        kind, amount = precision
        agrees = (
            delta <= amount
            if kind == "tolerance"
            else round(claimed_number, int(amount)) == round(cell_number, int(amount))
        )
        if agrees:
            out.append(
                _f(
                    "PD003",
                    claim.claim_id,
                    RuleStatus.PASS,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=(
                        f"{value} equals the printed {cell} at declared precision ({kind}:{amount}) "
                        "under an identical declared quantity"
                    ),
                )
            )
            continue
        out.append(
            _f(
                "PD003",
                claim.claim_id,
                RuleStatus.FAIL,
                measurements=measurements,
                evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                reason=(
                    f"the claim states {value} but the printed cell at ({cell_address}) of "
                    f"{anchor.anchor_id} states {cell}; both declare {anchor.quantity_declaration!r} "
                    f"and the declared precision is {kind}:{amount}"
                ),
            )
        )
    return out


def _pd003_inconclusive(
    bundle: Bundle,
    claim: Claim,
    measurements: dict[str, Any],
    anchor: FloatAnchor,
    reason: str,
) -> RuleFinding:
    return _f(
        "PD003",
        claim.claim_id,
        RuleStatus.INCONCLUSIVE,
        measurements=measurements,
        evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
        reason=reason,
    )


# --- PD004 Comparative Claim Support -------------------------------------------------------


def _columns_in_scope(claim: Claim, grid: TableGrid) -> tuple[int, ...] | None:
    basis = _qualifier_statement(claim, "comparison_basis")
    if not basis:
        return None
    if basis in ("per_column", "all_columns"):
        return tuple(range(len(grid.columns)))
    named = re.match(r"named_column\s*[:=]\s*(.+)$", basis)
    if named is not None:
        index = grid.column_index(named.group(1))
        return (index,) if index is not None else ()
    listed = re.match(r"columns\s*[:=]\s*(.+)$", basis)
    if listed is not None:
        wanted = [name.strip() for name in listed.group(1).split(",") if name.strip()]
        indexes = [grid.column_index(name) for name in wanted]
        if any(index is None for index in indexes):
            return ()
        return tuple(index for index in indexes if index is not None)
    return None


def _beats(winner: float, loser: float, direction: str) -> bool | None:
    if direction == "down":
        return winner < loser
    if direction == "up":
        return winner > loser
    return None


def _universally_quantified(claim: Claim) -> bool:
    return claim.quantifier in (Quantifier.ALL, Quantifier.BARE)


def pd004(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    for claim in bundle.claims:
        if _is_out_of_universe(claim) or claim.form not in (ClaimForm.COMPARATIVE, ClaimForm.SUPERLATIVE):
            continue
        anchors = bundle.anchors_for(claim)
        measurements: dict[str, Any] = {
            "n_float_links": len(anchors),
            "n_subjects": len(claim.subjects),
            "quantifier": claim.quantifier.value,
            "n_columns_in_scope": 0,
            "n_supported": 0,
            "n_counterexamples": 0,
            "n_ties": 0,
        }
        evidence = _claim_evidence(claim)
        if not anchors and not bundle.rd_targets_for(claim):
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="no comparison target exists for this claim",
                )
            )
            continue
        intensifier = sorted(words(claim.text) & _INTENSIFIERS)
        threshold = _qualifier_statement(claim, "threshold")
        if intensifier and not threshold:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"'{', '.join(intensifier)}' has no declared test or threshold; "
                        "the strength of the claim cannot be checked"
                    ),
                )
            )
            continue
        if not anchors:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        "the comparison set is reachable only through an upstream target, "
                        "which carries no member values across this boundary"
                    ),
                )
            )
            continue
        anchor = anchors[0]
        grid = bundle.grid(anchor)
        if grid is None:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=f"no tabular with an identifiable header row could be recovered inside {anchor.anchor_id}",
                )
            )
            continue
        columns = _columns_in_scope(claim, grid)
        if columns is None:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason="no comparison basis is declared (per_column / columns=... / named_column=...)",
                )
            )
            continue
        if not columns:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason="the declared comparison basis names no column that exists in the float",
                )
            )
            continue
        _, gate, gate_reason = _downstream(bundle, claim)
        if gate is not None:
            measurements["downstream_status"] = gate.value
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(_downstream(bundle, claim)[0])),
                    reason=f"{gate_reason}; no downstream-free judgment of the same relation is possible",
                )
            )
            continue
        if len(claim.subjects) < 2:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason="a comparison needs at least two declared subjects as they appear in the float",
                )
            )
            continue
        first, second = claim.subjects[0], claim.subjects[1]
        block = _declared_block(claim)
        row_a, address_a = _row_address(grid, first, block)
        row_b, address_b = _row_address(grid, second, block)
        if row_a is None or row_b is None:
            missing, address = (first, address_a) if row_a is None else (second, address_b)
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, bundle.anchor_evidence(anchor)),
                    reason=(
                        f"the declared subject {missing!r} is not an addressable row in "
                        f"{anchor.anchor_id} ({_declare_unit(ScopeUnit.COMPARISON_MEMBER)}): {address}"
                    ),
                )
            )
            continue
        addressed = f"{first} -> {address_a}; {second} -> {address_b}"
        counterexamples: list[str] = []
        ties: list[str] = []
        supported = 0
        undetermined = 0
        for index in columns:
            column = grid.columns[index]
            direction = grid.directions[index] or _declared_direction(anchor)
            a = _number(row_a.cell(index))
            b = _number(row_b.cell(index))
            if a is None or b is None or not direction:
                undetermined += 1
                continue
            if a == b:
                ties.append(f"{column} ({a:g} = {b:g})")
                continue
            if _beats(a, b, direction) is True:
                supported += 1
            else:
                counterexamples.append(f"{column} ({row_a.label} {a:g} vs {row_b.label} {b:g}, {direction} is better)")
        measurements["n_columns_in_scope"] = len(columns)
        measurements["n_supported"] = supported
        measurements["n_counterexamples"] = len(counterexamples)
        measurements["n_ties"] = len(ties)
        measurements["n_undetermined"] = undetermined
        evidence = _claim_evidence(claim, bundle.anchor_evidence(anchor))
        if undetermined:
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"{undetermined} of {len(columns)} columns have no declared direction or no numeric cell "
                        f"({_declare_unit(ScopeUnit.COMPARISON_MEMBER)}, {addressed})"
                    ),
                )
            )
            continue
        if counterexamples and _universally_quantified(claim):
            out.append(
                _f(
                    "PD004",
                    claim.claim_id,
                    RuleStatus.FAIL,
                    measurements=measurements,
                    evidence=evidence,
                    # The predicate is quoted, not conjugated: it is the author's own declared word,
                    # and putting it after "does not" would print "does not outperforms".
                    reason=(
                        f"the declared relation '{claim.predicate or 'beats'}' fails: {first} vs {second} on "
                        f"{len(counterexamples)} of {len(columns)} "
                        f"columns in the referenced {anchor.anchor_id} "
                        f"({_declare_unit(ScopeUnit.COMPARISON_MEMBER)}, {addressed}): "
                        f"{', '.join(counterexamples)}" + (f"; declared ties: {', '.join(ties)}" if ties else "")
                    ),
                )
            )
            continue
        if not _universally_quantified(claim):
            status = RuleStatus.PASS if supported else RuleStatus.INCONCLUSIVE
            suffix = f" ({_declare_unit(ScopeUnit.COMPARISON_MEMBER)}, {addressed})" if supported else ""
            reason = (
                f"the claim is existential ({claim.quantifier.value}): {supported} of {len(columns)} columns support it"
                + suffix
                if supported
                else (
                    f"no column in the referenced {anchor.anchor_id} supports the claim, "
                    "and the comparison basis may be incomplete"
                )
            )
            out.append(_f("PD004", claim.claim_id, status, measurements=measurements, evidence=evidence, reason=reason))
            continue
        out.append(
            _f(
                "PD004",
                claim.claim_id,
                RuleStatus.PASS,
                measurements=measurements,
                evidence=evidence,
                reason=(
                    f"{first} beats {second} on all {len(columns)} declared columns of {anchor.anchor_id} "
                    f"({_declare_unit(ScopeUnit.COMPARISON_MEMBER)}, {addressed})"
                    + (f" ({len(ties)} declared ties are not counted as support)" if ties else "")
                ),
            )
        )
    return out


def _declared_direction(anchor: FloatAnchor) -> str:
    declaration = anchor.quantity_declaration
    if any(mark in declaration for mark in ("\\textdownarrow", "↓", "down")):
        return "down"
    if any(mark in declaration for mark in ("\\textuparrow", "↑", "up")):
        return "up"
    return ""


# --- PD005 Qualification Preservation ------------------------------------------------------


def _has_absolutive(claim: Claim) -> bool:
    return bool(words(claim.text) & _ABSOLUTIVES)


def _in_qualification_class(claim: Claim) -> bool:
    return claim.form is ClaimForm.QUALIFICATION or bool(claim.qualifiers) or _has_absolutive(claim)


def pd005(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    targets = bundle.rd.by_rule("RD002") if bundle.rd is not None else ()
    universe = bundle.exclusion_universe()
    for claim in bundle.claims:
        if _is_out_of_universe(claim) or not _in_qualification_class(claim):
            continue
        measurements: dict[str, Any] = {
            "n_qualifiers": len(claim.qualifiers),
            "n_members_listed": len(claim.scope.members),
            "n_rd002_findings": len(targets),
            "n_universe_targets": len(universe),
            "absolutive": sorted(words(claim.text) & _ABSOLUTIVES),
        }
        evidence = _claim_evidence(claim)
        if targets and not universe:
            out.append(
                _f(
                    "PD005",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"upstream reports {len(targets)} RD002 findings and no exclusions on any of them",
                )
            )
            continue
        if not claim.qualifiers and not _has_absolutive(claim):
            out.append(
                _f(
                    "PD005",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="no qualifier on either the claim or the evidence it names",
                )
            )
            continue
        in_scope = [finding for finding in universe if _scope_matches(claim, finding)]
        measurements["n_in_scope"] = len(in_scope)
        if not in_scope:
            out.append(
                _f(
                    "PD005",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="the claim's evidence cannot be bound to a target of the derived exclusion universe "
                    "(no declared (rule_id, target) link and no subject matching an upstream target id)",
                )
            )
            continue
        unevidenced = sorted(finding.target for finding in in_scope if not finding.listing_is_evidenced)
        measurements["n_listing_not_evidenced"] = len(unevidenced)
        unnamed = _unnamed_exclusions(claim, in_scope)
        measurements["n_unnamed_targets"] = len(unnamed)
        generic = _qualifier_statement(claim, "generic_coverage")
        if unnamed and not generic:
            tokens = sorted({token for target, _n, token in unnamed})
            out.append(
                _f(
                    "PD005",
                    claim.claim_id,
                    RuleStatus.FAIL,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(tuple(in_scope))),
                    reason=(
                        f"the claim enumerates {', '.join(claim.scope.members) or 'no member'} "
                        "but the evidence carries "
                        f"exclusions for {', '.join(tokens)} as well: "
                        + "; ".join(f"{target} ({n})" for target, n, _t in unnamed)
                        + _limitation(tuple(in_scope))
                    ),
                )
            )
            continue
        if unevidenced:
            out.append(
                _f(
                    "PD005",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=_claim_evidence(claim, _upstream_evidence(tuple(in_scope))),
                    reason=(
                        f"the exclusion listing on {', '.join(unevidenced)} is not evidenced "
                        "(n_exclusions_listed != n_exclusions, or the member rule is neither "
                        f"DIRECT nor DERIVED){_limitation(tuple(in_scope))}"
                    ),
                )
            )
            continue
        out.append(
            _f(
                "PD005",
                claim.claim_id,
                RuleStatus.PASS,
                measurements=measurements,
                evidence=_claim_evidence(claim, _upstream_evidence(tuple(in_scope))),
                reason=(
                    f"all {len(in_scope)} targets of the derived exclusion universe in this claim's "
                    "scope are named by the claim"
                    + (f" or covered by the declared statement {generic!r}" if generic else "")
                    + _limitation(tuple(in_scope))
                ),
            )
        )
    return out


def _tokens(finding: RDFinding) -> tuple[str, ...]:
    """The path-like parts of an upstream target id, lower-cased, for explicit key matching."""
    return tuple(part for part in re.split(r"[/:_\-]", finding.target.lower()) if part)


def _scope_matches(claim: Claim, finding: RDFinding) -> bool:
    refs = {target for _rule, target in bundle_ref_pairs(claim)}
    if finding.target in refs:
        return True
    haystack = finding.target.lower()
    return any(_norm(subject).lower() in haystack for subject in claim.subjects if _norm(subject))


def bundle_ref_pairs(claim: Claim) -> tuple[tuple[str, str], ...]:
    return tuple(
        link.target_ref
        for link in claim.link_refs
        if link.target_kind is TargetKind.RD_TARGET and isinstance(link.target_ref, tuple)
    )


def _unnamed_exclusions(claim: Claim, in_scope: list[RDFinding]) -> list[tuple[str, int, str]]:
    named = {_norm(member).lower() for member in claim.scope.members if _norm(member)}
    out: list[tuple[str, int, str]] = []
    for finding in in_scope:
        tokens = _tokens(finding)
        hits = [token for token in tokens if token in named]
        if hits:
            continue
        label = next((token for token in tokens if len(token) > 2), finding.target)
        out.append((finding.target, finding.n_exclusions, label))
    return out


# --- PD006 Result Reference Integrity ------------------------------------------------------


def _in_reference_class(claim: Claim) -> bool:
    return claim.form is ClaimForm.REFERENCE_ATTRIBUTION or bool(
        ref_labels(claim.text) or named_float_numbers(claim.text)
    )


def pd006(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    for claim in bundle.claims:
        if _is_out_of_universe(claim) or not _in_reference_class(claim):
            continue
        labels = ref_labels(claim.text)
        numbers = named_float_numbers(claim.text)
        values = literals(claim.text)
        measurements: dict[str, Any] = {
            "n_ref_macros": len(labels),
            "ref_labels": tuple(sorted(labels)),
            "named_float_numbers": numbers,
            "resolved": (),
            "n_literals": len(values),
        }
        evidence = _claim_evidence(claim)
        if not labels and not numbers:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="the claim contains no result reference",
                )
            )
            continue
        if bundle.index is None:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="no LaTeX float index was supplied, so no reference can be resolved",
                )
            )
            continue
        resolved: list[tuple[str, int, str]] = []
        unresolved: list[str] = []
        for label in labels:
            record = bundle.index.resolve_label(label)
            if record is None:
                unresolved.append(label)
            else:
                resolved.append((label, record.number, record.kind))
        measurements["resolved"] = tuple(f"{label} -> {kind} {number}" for label, number, kind in resolved)
        if unresolved:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"label(s) do not resolve to any float in the source: {', '.join(sorted(unresolved))}",
                )
            )
            continue
        mismatched_number = [
            number
            for number in numbers
            if not any(
                kind == _kind_of(number, bundle) and resolved_number == number for _l, resolved_number, kind in resolved
            )
        ]
        if numbers and mismatched_number and not resolved:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"the named number(s) {mismatched_number} cannot be matched to a parsed float",
                )
            )
            continue
        if not values:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.PASS,
                    measurements=measurements,
                    evidence=evidence,
                    reason="every reference in the claim resolves to a float in the source "
                    "(the resolution is DERIVED from the document's own numbering)",
                )
            )
            continue
        if len(values) > 1:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"the claim attributes {len(values)} literals ({', '.join(values)}); "
                        "which one belongs to the reference is undeclared"
                    ),
                )
            )
            continue
        value = values[0]
        bodies = bundle.referenced_bodies(claim)
        if not bodies:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"{value} cannot be checked: the referenced float(s) "
                        f"{', '.join(bundle.referenced_anchor_ids(claim))} have no recoverable body"
                    ),
                )
            )
            continue
        if any(body_contains_literal(body, value) for _anchor_id, body in bodies):
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.PASS,
                    measurements={
                        **measurements,
                        "claim_value": value,
                        "present_in": tuple(anchor_id for anchor_id, _b in bodies),
                    },
                    evidence=evidence,
                    reason=f"the reference resolves and {value} is printed inside the referenced float",
                )
            )
            continue
        carriers = bundle.floats_with_literal(value, exclude=tuple(anchor_id for anchor_id, _b in bodies))
        measurements["carriers"] = carriers
        if carriers:
            out.append(
                _f(
                    "PD006",
                    claim.claim_id,
                    RuleStatus.FAIL,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"the reference resolves to {', '.join(id for id, _b in bodies)}, "
                        f"which does not print {value}; "
                        f"it is printed in {', '.join(carriers)}"
                    ),
                )
            )
            continue
        out.append(
            _f(
                "PD006",
                claim.claim_id,
                RuleStatus.INCONCLUSIVE,
                measurements=measurements,
                evidence=evidence,
                reason=f"{value} is printed in no parsed float, so the attributed content itself is unverifiable",
            )
        )
    return out


def _kind_of(number: int, bundle: Bundle) -> str:
    return "table" if any(anchor.kind == "table" and anchor.number == number for anchor in bundle.floats) else "figure"


# --- PD007 Cross-Section Claim Consistency -------------------------------------------------


def _pair_key(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


def pd007(bundle: Bundle) -> list[RuleFinding]:
    out: list[RuleFinding] = []
    pairs: dict[str, list[tuple[Claim, Claim, str]]] = {}
    for claim in bundle.claims:
        for partner_id, basis in claim.same_as:
            partner = bundle.claim_by_id(partner_id)
            if partner is None:
                continue
            pairs.setdefault(_pair_key(claim.claim_id, partner_id), []).append((claim, partner, basis))
        if not claim.same_as:
            out.append(
                _f(
                    "PD007",
                    claim.claim_id,
                    RuleStatus.NOT_APPLICABLE,
                    measurements={"same_as": ()},
                    evidence=_claim_evidence(claim),
                    reason="the claim declares no same_as pairing, so there is no cross-section relation to check",
                )
            )
    for key, records in sorted(pairs.items()):
        bases = sorted({basis for _a, _b, basis in records})
        first, second = records[0][0], records[0][1]
        evidence = _claim_evidence(first, _claim_evidence(second))
        measurements = {"pair": key, "pairing_basis": tuple(bases), "n_declarations": len(records)}
        if PairingBasis.SUGGESTED.value in bases and PairingBasis.DECLARED.value not in bases:
            out.append(
                _f(
                    "PD007",
                    key,
                    RuleStatus.INCONCLUSIVE,
                    measurements=measurements,
                    evidence=evidence,
                    reason="the pairing is SUGGESTED only; a suggestion is not a link and cannot support a verdict",
                )
            )
            continue
        if _norm(first.predicate) != _norm(second.predicate) or tuple(first.subjects) != tuple(second.subjects):
            out.append(
                _f(
                    "PD007",
                    key,
                    RuleStatus.INCONCLUSIVE,
                    measurements={**measurements, "predicate_a": first.predicate, "predicate_b": second.predicate},
                    evidence=evidence,
                    reason=(
                        "the declared predicate and subjects are not identical, so the two claims "
                        f"are not the same proposition ({first.predicate!r} vs {second.predicate!r})"
                    ),
                )
            )
            continue
        scope_a = _scope_signature(first)
        scope_b = _scope_signature(second)
        if scope_a == scope_b:
            out.append(
                _f(
                    "PD007",
                    key,
                    RuleStatus.PASS,
                    measurements=measurements,
                    evidence=evidence,
                    reason=f"identical predicate, subjects and declared scope signature ({scope_a})",
                )
            )
            continue
        reconciliation = _qualifier_statement(first, "reconciliation") or _qualifier_statement(second, "reconciliation")
        if reconciliation:
            out.append(
                _f(
                    "PD007",
                    key,
                    RuleStatus.PASS,
                    measurements=measurements,
                    evidence=evidence,
                    reason=(
                        f"the scopes differ ({scope_a} vs {scope_b}) but a reconciliation "
                        f"is declared: {reconciliation!r}"
                    ),
                )
            )
            continue
        out.append(
            _f(
                "PD007",
                key,
                RuleStatus.FAIL,
                measurements={**measurements, "scope_a": scope_a, "scope_b": scope_b},
                evidence=evidence,
                reason=(
                    f"identical predicate and subjects, but the declared scopes differ with no reconciliation: "
                    f"{first.claim_id} says {scope_a} at {first.locator.label()}, "
                    f"{second.claim_id} says {scope_b} at {second.locator.label()}"
                ),
            )
        )
    return out


def _scope_signature(claim: Claim) -> str:
    scope = claim.scope
    return (
        f"universe={scope.declared_universe or '-'};unit={scope.unit.value};"
        f"members={','.join(scope.members) or '-'};status={scope.universe_status.value}"
    )


# --- dispatch ------------------------------------------------------------------------------


RULES = (pd001, pd002, pd003, pd004, pd005, pd006, pd007)


def evaluate(bundle: Bundle, rule_ids: Iterable[str] | None = None) -> list[RuleFinding]:
    ids = tuple(rule_ids) if rule_ids is not None else RULE_IDS
    findings: list[RuleFinding] = []
    for rule_id, function in zip(RULE_IDS, RULES):
        if rule_id in ids:
            findings.extend(function(bundle))
    return sorted([finding for finding in findings if finding.rule_id in ids], key=lambda f: (f.rule_id, f.target))
