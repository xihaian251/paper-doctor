"""The twelve frozen `P_*` validation codes, each exercised by one broken manifest.

Validation is a separate channel from science (Phase 0 §17): everything asserted here
raises `ManifestError` before any rule runs, so no malformed input can reach a finding.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from paper_doctor.latex_index import build_index
from paper_doctor.manifest import MANIFEST_NAME, VALIDATION_CODES, ManifestError, load_manifest

REPO = Path(__file__).resolve().parents[1]
GMMVI_ROOT = REPO / "phase0" / "sources" / "2209.11533v2.tex"

PAPER = "Model section\n\nThe score is 0.42 on the held-out split.\n"

#: Contract I-1 makes the upstream findings artifact a required declaration, so every manifest in
#: this file points at one. It is never parsed here -- the reader is `rd_findings.load`.
FINDINGS = "findings.json"


def _write_findings(directory: Path) -> None:
    (directory / FINDINGS).write_text("[]\n", encoding="utf-8")


def _registry(**paper: Any) -> dict[str, Any]:
    return {
        "paper": paper or {"path": "paper.tex"},
        "rd_findings": {
            "path": FINDINGS,
            "sha256": hashlib.sha256(b"[]\n").hexdigest(),
            "size": 3,
            "rd_version": "0.1.0",
        },
    }


def _manifest_dir(tmp_path: Path) -> Path:
    (tmp_path / "paper.tex").write_text(PAPER, encoding="utf-8")
    _write_findings(tmp_path)
    return tmp_path


def _write(tmp_path: Path, document: dict[str, Any]) -> Path:
    path = tmp_path / MANIFEST_NAME
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _base(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema_version": 1,
        "_registry": _registry(),
        "_claims": [
            {
                "claim_id": "K1",
                "text": "The score is 0.42",
                "locator": {"path": "paper.tex", "line": 3, "text": "The score is 0.42"},
                "form": "NUMERIC_ATTRIBUTION",
            }
        ],
        "_floats": [],
        "_links": [],
    }
    document.update(overrides)
    for key, value in overrides.items():
        if value is None:
            document.pop(key, None)
    return document


def _code(tmp_path: Path, document: dict[str, Any]) -> str:
    path = _write(tmp_path, document)
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    return caught.value.code


def _error_text(tmp_path: Path, document: dict[str, Any]) -> str:
    path = _write(tmp_path, document)
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    return str(caught.value)


def test_a_valid_minimal_manifest_loads(tmp_path: Path) -> None:
    path = _write(tmp_path, _base())
    manifest = load_manifest(_manifest_dir(tmp_path) / MANIFEST_NAME)
    assert manifest.paper.path == "paper.tex"
    assert manifest.claims[0].claim_id == "K1"
    assert manifest.claims[0].locator.line == 3
    assert path.name == MANIFEST_NAME


def test_error_text_keeps_upstreams_rendering(tmp_path: Path) -> None:
    text = _error_text(tmp_path, _base(schema_version=2))
    assert text.startswith("P_SCHEMA_VERSION at ")
    assert ": schema_version must be 1" in text


def test_p_yaml(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    path = tmp_path / MANIFEST_NAME
    path.write_text("schema_version: 1\n  bad indent: [unclosed\n", encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    assert caught.value.code == "P_YAML"


def test_p_top_level_not_a_mapping(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    path = _write(tmp_path, {})  # empty mapping is falsy but still a mapping
    path.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    assert caught.value.code == "P_TOP_LEVEL"


def test_p_top_level_section_order_is_frozen(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    document = {
        "schema_version": 1,
        "_claims": _base()["_claims"],
        "_registry": {"paper": {"path": "paper.tex"}},
    }
    path = _write(tmp_path, document)
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    assert caught.value.code == "P_TOP_LEVEL"
    assert "frozen order" in caught.value.problem


def test_p_schema_version(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    assert _code(tmp_path, _base(schema_version=2)) == "P_SCHEMA_VERSION"
    assert _code(tmp_path, _base(schema_version=None)) == "P_SCHEMA_VERSION"


def test_p_unknown_key(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    assert _code(tmp_path, _base(project_name="synthetic")) == "P_UNKNOWN_KEY"
    claim = _base()["_claims"][0] | {"confidence": 0.9}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_UNKNOWN_KEY"
    assert _code(tmp_path, _base(_registry={"paper": {"path": "paper.tex"}, "llm": "gpt"})) == "P_UNKNOWN_KEY"


def test_p_type_enum_domains(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"form": "RHETORICAL"}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_TYPE"
    link = {
        "link_id": "L1",
        "claim": "K1",
        "target_kind": "TABLE_CELL",
        "target_ref": "table:1",
        "link_basis": "AUDITOR_DECLARED",
    }
    assert _code(tmp_path, _base(_links=[link])) == "P_TYPE"


def test_p_not_a_number(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"locator": {"path": "paper.tex", "line": "three"}}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_NOT_A_NUMBER"
    scoped = _base()["_claims"][0] | {"scope": {"stated_count": "ten"}}
    assert _code(tmp_path, _base(_claims=[scoped])) == "P_NOT_A_NUMBER"


def test_p_missing_field(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0]
    del claim["text"]
    assert _code(tmp_path, _base(_claims=[claim])) == "P_MISSING_FIELD"
    link = {"link_id": "L1", "claim": "K1", "target_kind": "PROSE", "target_ref": {"path": "paper.tex", "line": 3}}
    assert _code(tmp_path, _base(_links=[link])) == "P_MISSING_FIELD"


def test_p_duplicate_id(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    first = _base()["_claims"][0]
    assert _code(tmp_path, _base(_claims=[first, dict(first)])) == "P_DUPLICATE_ID"


def test_p_locator_keys_illegal_family(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"locator": {"path": "paper.tex", "line": 3, "key": "text"}}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_LOCATOR_KEYS"


def test_p_path_outside_root(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"locator": {"path": "../escape.tex", "text": "x"}}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_PATH_OUTSIDE_ROOT"


def test_p_unresolved_ref_text_not_in_source(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {
        "text": "The score is 0.99",
        "locator": {"path": "paper.tex", "line": 3, "text": "The score is 0.99"},
    }
    assert _code(tmp_path, _base(_claims=[claim])) == "P_UNRESOLVED_REF"


def test_p_unresolved_ref_declared_line_is_wrong(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"locator": {"path": "paper.tex", "line": 1, "text": "The score is 0.42"}}
    code = _code(tmp_path, _base(_claims=[claim]))
    assert code == "P_UNRESOLVED_REF"


def test_p_unresolved_ref_unknown_link_id(tmp_path: Path) -> None:
    _manifest_dir(tmp_path)
    claim = _base()["_claims"][0] | {"links": ["L404"]}
    assert _code(tmp_path, _base(_claims=[claim])) == "P_UNRESOLVED_REF"


@pytest.fixture(scope="module")
def gmmvi_index():  # type: ignore[no-untyped-def]
    if not GMMVI_ROOT.is_dir():
        raise FileNotFoundError(f"read-only corpus fixture missing: {GMMVI_ROOT}")
    return build_index(GMMVI_ROOT, GMMVI_ROOT / "arxiv.tex")


def _corpus_manifest(tmp_path: Path) -> Path:
    """A manifest whose audit root is the real GMMVI checkout, read-only."""
    _write_findings(tmp_path)
    document = {
        "schema_version": 1,
        "_registry": _registry(path="arxiv.tex", root=str(GMMVI_ROOT)),
        "_claims": [],
        "_floats": [],
        "_links": [],
    }
    path = tmp_path / MANIFEST_NAME
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_float_label_resolves_through_the_document_order(tmp_path: Path, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    path = _corpus_manifest(tmp_path)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["_floats"] = [{"label": "tab:exp1", "quantity_declaration": "negated ELBO"}]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    manifest = load_manifest(path, index=gmmvi_index, verify_claim_locators=False)
    assert [(f.kind, f.number, f.source_file, f.begin_line) for f in manifest.floats] == [
        ("table", 2, "arxiv.tex", 400)
    ]


def test_p_unresolved_ref_float_label_absent(tmp_path: Path, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    path = _corpus_manifest(tmp_path)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["_floats"] = [{"label": "tab:not_in_this_paper"}]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path, index=gmmvi_index, verify_claim_locators=False)
    assert caught.value.code == "P_UNRESOLVED_REF"


def test_p_conflicting_ref_declared_number_disagrees(tmp_path: Path, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    path = _corpus_manifest(tmp_path)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["_floats"] = [{"label": "tab:exp1", "kind": "table", "number": 3}]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path, index=gmmvi_index, verify_claim_locators=False)
    assert caught.value.code == "P_CONFLICTING_REF"
    assert "document order" in caught.value.problem


def test_p_conflicting_ref_two_float_targets_for_one_claim(tmp_path: Path, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    """GMMVI C1 vs C2: one claim linked to both Table 2 and Table 3 is a contract fault,
    not a scientific judgment -- PD never picks a float by value proximity."""
    path = _corpus_manifest(tmp_path)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    fragment = r"the optimistic value provided in Table~\ref{tab:exp1_eval} for \emph{BreastCancer}"
    document["_claims"] = [
        {
            "claim_id": "C1",
            "text": fragment,
            "locator": {"path": "arxiv.tex", "line": 426, "text": fragment},
            "form": "REFERENCE_ATTRIBUTION",
            "links": ["LA", "LB"],
        }
    ]
    document["_floats"] = [{"label": "tab:exp1"}, {"label": "tab:exp1_eval"}]
    document["_links"] = [
        {
            "link_id": "LA",
            "claim": "C1",
            "target_kind": "FLOAT",
            "target_ref": "table:2",
            "link_basis": "AUTHOR_REF_IN_SENTENCE",
        },
        {
            "link_id": "LB",
            "claim": "C1",
            "target_kind": "FLOAT",
            "target_ref": "table:3",
            "link_basis": "AUTHOR_NAMED_FLOAT",
        },
    ]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path, index=gmmvi_index)
    assert caught.value.code == "P_CONFLICTING_REF"


def test_fm_p11_macro_definition_locator_is_rejected_as_input(tmp_path: Path, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    """A `text:` locator that lands inside a `\\def` body is a validation fault, not a PD006
    finding (Phase 0 §16/§17): PD does not audit macro definitions as claims."""
    path = _corpus_manifest(tmp_path)
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["_claims"] = [
        {
            "claim_id": "M1",
            "text": "\\def\\figref#1{figure~\\ref{#1}}",
            "locator": {"path": "math_commands.tex", "line": 21, "text": "\\def\\figref#1{figure~\\ref{#1}}"},
            "form": "REFERENCE_ATTRIBUTION",
        }
    ]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(ManifestError) as caught:
        load_manifest(path, index=gmmvi_index)
    assert caught.value.code == "P_UNRESOLVED_REF"
    assert "outside the document body" in caught.value.problem


def test_inferred_link_grade_is_refused(tmp_path: Path) -> None:
    """A suggestion is not a link, so it cannot enter the model at all (§15)."""
    _manifest_dir(tmp_path)
    link = {
        "link_id": "L1",
        "claim": "K1",
        "target_kind": "PROSE",
        "target_ref": {"path": "paper.tex", "line": 3},
        "link_basis": "AUDITOR_DECLARED",
        "grade": "INFERRED",
    }
    assert _code(tmp_path, _base(_links=[link])) == "P_TYPE"


# --- The frozen code set is both closed and reachable ------------------------------------
#
# Phase 0 §7 freezes twelve codes and forbids a thirteenth. A test that only checks the
# constant would pass while a code stays unreachable, so each code is also *raised* here.


def _yaml_doc(tmp_path: Path) -> Path:
    _manifest_dir(tmp_path)
    path = tmp_path / MANIFEST_NAME
    path.write_text("schema_version: 1\n  bad indent: [unclosed\n", encoding="utf-8")
    return path


def _top_level_doc(tmp_path: Path) -> Path:
    _manifest_dir(tmp_path)
    path = tmp_path / MANIFEST_NAME
    path.write_text("- a\n- b\n", encoding="utf-8")
    return path


def _doc_factory(document: dict[str, Any]):
    def build(tmp_path: Path) -> Path:
        _manifest_dir(tmp_path)
        return _write(tmp_path, document)

    return build


TRIGGERS: dict[str, tuple[Any, bool]] = {
    "P_YAML": (_yaml_doc, False),
    "P_TOP_LEVEL": (_top_level_doc, False),
    "P_SCHEMA_VERSION": (_doc_factory(_base(schema_version=2)), False),
    "P_UNKNOWN_KEY": (_doc_factory(_base(project_name="synthetic")), False),
    "P_TYPE": (_doc_factory(_base(_claims=[_base()["_claims"][0] | {"form": "RHETORICAL"}])), False),
    "P_NOT_A_NUMBER": (
        _doc_factory(_base(_claims=[_base()["_claims"][0] | {"locator": {"path": "paper.tex", "line": "three"}}])),
        False,
    ),
    "P_MISSING_FIELD": (
        _doc_factory(_base(_claims=[{k: v for k, v in _base()["_claims"][0].items() if k != "text"}])),
        False,
    ),
    "P_DUPLICATE_ID": (_doc_factory(_base(_claims=[_base()["_claims"][0], _base()["_claims"][0]])), False),
    "P_LOCATOR_KEYS": (
        _doc_factory(
            _base(_claims=[_base()["_claims"][0] | {"locator": {"path": "paper.tex", "line": 3, "key": "t"}}])
        ),
        False,
    ),
    "P_PATH_OUTSIDE_ROOT": (
        _doc_factory(_base(_claims=[_base()["_claims"][0] | {"locator": {"path": "../e.tex", "text": "x"}}])),
        False,
    ),
    "P_UNRESOLVED_REF": (
        _doc_factory(
            _base(
                _claims=[
                    {
                        "claim_id": "X",
                        "text": "no such sentence",
                        "locator": {"path": "paper.tex", "line": 3, "text": "no such sentence"},
                        "form": "SCOPE",
                    }
                ]
            )
        ),
        False,
    ),
    "P_CONFLICTING_REF": (None, True),  # built below: it needs the real corpus and an index
}


def test_the_code_set_is_closed_at_twelve() -> None:
    assert len(VALIDATION_CODES) == 12
    assert set(VALIDATION_CODES) == set(TRIGGERS)


@pytest.mark.parametrize("code", sorted(VALIDATION_CODES))
def test_every_frozen_code_is_reachable(tmp_path: Path, code: str, gmmvi_index) -> None:  # type: ignore[no-untyped-def]
    if code == "P_CONFLICTING_REF":
        path = _corpus_manifest(tmp_path)
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        document["_floats"] = [{"label": "tab:exp1", "number": 3}]
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        index = gmmvi_index
    else:
        build, needs_index = TRIGGERS[code]
        path = build(tmp_path)
        index = gmmvi_index if needs_index else None
    with pytest.raises(ManifestError) as caught:
        load_manifest(path, index=index)
    assert caught.value.code == code


def test_p_unresolved_ref_quotes_the_resolved_root_not_only_the_declaration(tmp_path: Path) -> None:
    """Phase 3 §14: a fresh user's first run failed here, and the message only repeated the declared
    relative string -- which points at nothing for anyone reading from elsewhere.

    The code stays `P_UNRESOLVED_REF` (the set is frozen at twelve); what changed is that the text
    must show the absolute location that was actually tried, so the fix is obvious: restore the
    corpus there, or repoint `_registry/paper/root`.
    """
    _manifest_dir(tmp_path)
    declared = "no-such-checkout"
    path = _write(tmp_path, _base(_registry=_registry(path="paper.tex", root=declared)))
    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    assert caught.value.code == "P_UNRESOLVED_REF"
    text = str(caught.value)
    assert "no-such-checkout" in text, "the declared string identifies which field was wrong"
    resolved = (tmp_path / declared).resolve().as_posix()
    assert resolved in text, f"the message must name the absolute path that was tried: {text}"
    assert "not a directory" in text and "_registry/paper/root" in text
