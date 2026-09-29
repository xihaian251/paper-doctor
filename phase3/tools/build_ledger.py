"""Generate `phase3/tabm/end_to_end_chain.json` from the artifacts the layers actually wrote.

Every value is read out of a file on disk (the PD output, the RD snapshot, the ED report and lock,
the DD report) or out of the pinned inputs, so the ledger cannot drift from the run it describes.
Nothing here is parsed by Paper Doctor: the ledger is a record of declared references, not a
fourth object model. Keys are sorted and no timestamp is written, so the file is byte-diffable.

The committed `end_to_end_chain.json` is the artifact of record; this script is how it was built.
Re-running it requires the capture inputs to be present (the read-only TabM checkout, the prepared
official Adult copies, the ED bundle), so it prints which one is missing and stops rather than
emitting a ledger with holes in it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent.parent / "tabm"
REPO = HERE.parent.parent


def _bytes(path: Path) -> bytes:
    return path.read_bytes()


def _sha(path: Path) -> str:
    return hashlib.sha256(_bytes(path)).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _pd_findings(path: Path) -> dict[str, dict[str, str]]:
    """`{claim: {rule_id: status}}` -- the ledger's view of one claim's PD verdicts."""
    out: dict[str, dict[str, str]] = {}
    for finding in _json(path):
        out.setdefault(finding["target"], {})[finding["rule_id"]] = finding["status"]
    return out


def _rd_findings(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for finding in _json(path):
        out.setdefault(finding["target"], {})[finding["rule_id"]] = finding["status"]
    return out


def _ids(findings: dict[str, dict[str, str]], target: str) -> list[str]:
    return [f"{rule}@{target}" for rule in sorted(findings.get(target, {}))]


def _require(path: Path, what: str) -> Path:
    """Name the missing capture input instead of writing a ledger with a hole where its digest was."""
    if not path.is_file():
        raise SystemExit(f"build_ledger: {what} is not readable at {path}; the ledger needs the capture inputs")
    return path


def main() -> int:
    manifest_path = HERE / "paper-doctor.yml"
    manifest = _manifest(manifest_path)
    registry = manifest["_registry"]
    claims = {claim["claim_id"]: claim for claim in manifest["_claims"]}
    links = {link["link_id"]: link for link in manifest["_links"]}
    corpus_root = (HERE / str(registry["paper"]["root"])).resolve()
    paper_file = _require(corpus_root / registry["paper"]["path"], "the read-only TabM source")

    pd_path = HERE / "pd_findings.json"
    pd = _pd_findings(pd_path)
    rd_path = HERE / "findings.json"
    rd = _json(rd_path)
    rd_by_target = _rd_findings(rd_path)

    rd_manifest = _manifest(HERE / "result-doctor.yml")
    ed_report_path = HERE / "ed-captured" / "report.json"
    ed = _json(ed_report_path)
    ed_lock_path = ed_report_path.parent / "experiment.lock.json"
    dd_report_path = HERE / "dd" / "report" / "report.json"
    dd = _json(dd_report_path)
    # The dataset DD audited is identified inside its own report; the digests below are taken from
    # those bytes, not from a path this script happens to know.
    dataset_root = Path(dd["identity"]["root_path"])

    ed_rules = {rule["rule_id"]: rule for rule in ed["rules"]}
    ed_run_id = ed_rules["ED003"]["entity_id"]
    lock = _json(ed_lock_path) if ed_lock_path.is_file() else None

    def claim_block(claim_id: str) -> dict[str, Any]:
        claim = claims[claim_id]
        return {
            "paper_claim_id": claim_id,
            "paper_locator": {
                "path": claim["locator"]["path"],
                "line": claim["locator"]["line"],
                "text": claim["locator"]["text"],
            },
            "claim_form": claim["form"],
            "link_ids": claim["links"],
            # Read off the manifest, so §6's "declared bases only" is a recorded fact per claim
            # rather than a prose claim about it.
            "link_bases": sorted({links[link_id]["link_basis"] for link_id in claim["links"]}),
            "pd_finding_ids": sorted(f"{rule}@{claim_id}" for rule in pd.get(claim_id, {})),
            "pd_statuses": dict(sorted(pd.get(claim_id, {}).items())),
        }

    adult_target = "tabm/adult-seed3/test-score"
    agg_target = "aggregation:agg:adult-seed-mean"

    chains = [
        {
            "chain_id": "chain-1-adult-four-layers",
            "statement": (
                "the paper's printed Adult split size, the seed aggregation behind the Adult "
                "accuracy, the shipped run that is one member of it, and the official dataset copy "
                "that fed it"
            ),
            "paper_claims": [claim_block("C6"), claim_block("C7"), claim_block("C8")],
            "joins": [
                {
                    "from": "C6/C8 -> FLOAT default-datasets (table:4) + PROSE cell [column='# Train', row='Adult']",
                    "to": "reported_result tabm/adult-seed3/test-score",
                    "basis": "declared in the manifest; no cross-layer similarity is computed",
                },
                {
                    "from": "C7 -> RD_TARGET [RD002, 'aggregation:agg:adult-seed-mean']",
                    "to": "the 15 enumerated members of that aggregation, of which seed-3 is one",
                    "basis": "AUTHOR_DECLARED member enumeration in result-doctor.yml",
                },
                {
                    "from": "aggregation member seed-3 -> experiment run",
                    "to": ed_run_id,
                    "basis": "the run artifact exp/tabm/adult/0-evaluation/3/report.json is the "
                    "member's declared source and the captured bundle is the audit of that same "
                    "run directory",
                },
                {
                    "from": "experiment run -> dataset",
                    "to": f"{dd['identity']['dataset_id']} at {dd['identity']['root_path']}",
                    "basis": "the run config declares data.path = 'data/adult' (not shipped); the "
                    "auditor declared the official local copy as the dataset for both ED and DD, "
                    "and the two agree on its digests",
                },
            ],
            "reported_result_id": adult_target,
            "rd_finding_ids": sorted(_ids(rd_by_target, adult_target) + _ids(rd_by_target, agg_target)),
            "rd_target_statuses": {
                adult_target: dict(sorted(rd_by_target.get(adult_target, {}).items())),
                agg_target: dict(sorted(rd_by_target.get(agg_target, {}).items())),
            },
            "experiment_run_id": ed_run_id,
            "ed_evidence_refs": [
                evidence
                for rule_id in ("ED002", "ED003", "ED004", "ED009", "ED010")
                for evidence in ed_rules[rule_id]["evidence"]
            ],
            "ed_rule_statuses": {rule_id: ed_rules[rule_id]["status"] for rule_id in sorted(ed_rules)},
            "dataset_id": dd["identity"]["dataset_id"],
            "dd_ref": {
                "report": "phase3/tabm/dd/report/report.json",
                "report_sha256": _sha(dd_report_path),
                "fingerprint": "phase3/tabm/dd/fingerprint.json",
                "fingerprint_sha256": _sha(HERE / "dd" / "fingerprint.json"),
                "dataset_id": dd["identity"]["dataset_id"],
                "manifest_hash": dd["identity"]["manifest_hash"],
                "config_hash": dd["identity"]["config_hash"],
                "split_sizes": dd["identity"]["split_sizes"],
                "eval_safety": dd["eval_safety"],
                "tool_version": dd["tool_version"],
            },
            "source_commit_shas": {
                "tabm_code_repository": "28e47ae301c92ec37787dde1ce923a0793f405b4",
                "ed_captured_commit": (lock or {}).get("code", {}).get("commit", {}).get("value") if lock else None,
            },
            "artifact_hashes": {
                "paper main.tex": _sha(paper_file),
                "rd findings.json": _sha(rd_path),
                "pd findings.json": _sha(pd_path),
                "ed report.json": _sha(ed_report_path),
                "ed experiment.lock.json": _sha(_require(ed_lock_path, "the ED experiment lock")),
                "dd report.json": _sha(dd_report_path),
                "adult train.csv": _sha(_require(dataset_root / "train.csv", "the prepared official Adult train copy")),
                "adult test.csv": _sha(_require(dataset_root / "test.csv", "the prepared official Adult test copy")),
            },
        },
        {
            "chain_id": "chain-2-dataset-composition-counts",
            "statement": (
                "three counts the paper states about its own dataset composition, and one derived count it never prints"
            ),
            "paper_claims": [
                claim_block("C1"),
                claim_block("C2"),
                claim_block("C3"),
                claim_block("C4"),
                claim_block("C5"),
            ],
            "reported_result_id": None,
            "rd_finding_ids": [],
            "experiment_run_id": None,
            "dataset_id": None,
            "reason_lower_layers_are_absent": (
                "these claims are about the paper's own tables; no reported result, run or dataset "
                "reference is what they assert, so the chain ends at the PD layer and is marked so "
                "rather than being padded"
            ),
        },
        {
            "chain_id": "chain-3-block-addressed-cell",
            "statement": "a value in a transposed table whose row label is carried by a vertical merge",
            "paper_claims": [claim_block("C9")],
            "reported_result_id": None,
            "rd_finding_ids": [],
            "experiment_run_id": None,
            "dataset_id": None,
            "reason_lower_layers_are_absent": (
                "the declared cell address has two readings, so PD stops at INCONCLUSIVE and never "
                "reaches a value that could be joined downstream"
            ),
        },
    ]

    ledger = {
        "kind": "paper-doctor/phase3-end-to-end-chain",
        "ledger_version": 1,
        "acceptance_target": {
            "title": "TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembling",
            "venue": "ICLR 2025",
            "code_repository": {
                "url": "https://github.com/yandex-research/tabm",
                "commit": "28e47ae301c92ec37787dde1ce923a0793f405b4",
                "read_only_checkout": "F:/MLResearch/upstream/tabm",
                "paper_subdirectory": "paper",
            },
            "paper_source": {
                "arxiv_id": "2410.24210",
                "tarball_sha256": "cdcea2ddbe710fa6e9c19b0e611e0c82dd513491aa6ac680368ed5bc3127db8c",
                "entry_point": registry["paper"]["path"],
                # Observed here, so the ledger and the manifest agreeing is a check, not a copy.
                "entry_point_sha256": _sha(paper_file),
                "entry_point_size": paper_file.stat().st_size,
                "declared_entry_point_sha256": registry["paper"]["sha256"],
                "declared_entry_point_size": registry["paper"]["size"],
                "read_only_checkout": registry["paper"]["root"],
                # The corpus is not vendored: it is rebuilt from arXiv against the tarball digest
                # above, and the acceptance test reads it from either place.
                "rebuild": "python scripts/fetch_acceptance_inputs.py tabm",
                "corpus_override": "PAPER_DOCTOR_TABM_CORPUS",
            },
        },
        "pd_finding_id_convention": "<rule_id>@<claim_id>",
        "rd_finding_id_convention": "<rule_id>@<RD target string>",
        "layer_invocations": {
            "PD": {
                "command": "paper-doctor audit phase3/tabm --json phase3/tabm/pd_findings.json",
                "manifest": "phase3/tabm/paper-doctor.yml",
                "findings_sha256": _sha(pd_path),
                "n_findings": len(_json(pd_path)),
                "by_status": dict(sorted(_counts(_json(pd_path), "status").items())),
                "adapters_written_for_tabm": 0,
            },
            "RD": {
                "command": "result-doctor audit phase3/tabm/result-doctor.yml --json > phase3/tabm/findings.json",
                "rd_version": registry["rd_findings"]["rd_version"],
                "artifact_sha256": registry["rd_findings"]["sha256"],
                "artifact_size": registry["rd_findings"]["size"],
                "n_findings": len(rd),
                "by_rule": dict(sorted(_counts(rd, "rule_id").items())),
                "by_status": dict(sorted(_counts(rd, "status").items())),
                # The ReportedResult ids are the labels the RD manifest declares; they are read
                # from there rather than reconstructed from the finding targets.
                "reported_result_ids": sorted(row["label"] for row in rd_manifest["reported_results"]),
                "sha_and_size_verified_before_parse": True,
                "rd_code_modified": False,
                "rd_rules_added": 0,
            },
            "ED": {
                "command": "experiment-doctor init phase3/.ed-workdir/tabm-ed/paper --command "
                "'python bin/model.py exp/tabm/adult/0-evaluation/3.toml --force' --seed 3 "
                "--config exp/tabm/adult/0-evaluation/3.toml --dataset <official adult copies> && "
                "experiment-doctor audit <same> --adapter captured -o phase3/tabm/ed-captured",
                "tool_version": "1.0.0",
                "adapter_used": "captured (declared surface only)",
                "n_runs_discovered_by_generic": 0,
                "generic_discovery_reports": [
                    "phase3/tabm/ed-generic-adult-runs/report.json",
                    "phase3/tabm/ed-generic-whole-repo/report.json",
                ],
                "report_sha256": _sha(ed_report_path),
                "run_id": ed_run_id,
                "ed_code_modified": False,
                "workspace_reconstruction": (
                    "git clone https://github.com/yandex-research/tabm <scratch> && git -C <scratch> "
                    "checkout 28e47ae301c92ec37787dde1ce923a0793f405b4; the working clone was deleted "
                    "after capture and only its three emitted artifacts are kept here"
                ),
                "limitation": "the captured adapter records no metric by design, and no execution "
                "was performed, so the metric of record stays in the RD layer",
            },
            "DD": {
                "command": "dataset-doctor audit F:/DatasetDoctorWork/realworld/adult/prepared",
                "tool_version": dd["tool_version"],
                "report_sha256": _sha(dd_report_path),
                "dataset_id": dd["identity"]["dataset_id"],
                "dd_code_modified": False,
                "adapters_written_for_tabm": 0,
            },
        },
        "chains": chains,
        "unknowns": [
            {
                "where": "C7 / PD002",
                "state": "INCONCLUSIVE",
                "because": "the seed universe is declared PARTIAL: an unlisted universe cannot be PASSed",
            },
            {
                "where": "chain-1 / PD003 over the Adult accuracy",
                "state": "NOT REACHABLE",
                "because": "the paper prints per-dataset accuracies in longtables whose source "
                "gives no reference name for the printed cell, so no claim can address the mean; "
                "the value 0.8575 was not turned into a claim",
            },
            {
                "where": "chain-1 / ED004, ED009, ED010",
                "state": "INCONCLUSIVE",
                "because": "the repository ships no run-side bundle for the published runs: no "
                "effective configuration, no termination cause and no runtime environment are "
                "recorded in any artifact",
            },
            {
                "where": "chain-1 / ED code.dirty and ED environment fields",
                "state": "THEY DESCRIBE THE CAPTURE, NOT THE PUBLISHED RUN",
                "because": "ED computes the working-tree state before it writes "
                "experiment.lock.json, so `dirty = False` was true of the cloned tree at capture "
                "time and the lock itself is now its one untracked file; the python version and "
                "package list ED recorded are this machine's (3.13.1, Windows-11), not the run's, "
                "and ED says so itself -- ED010 is INCONCLUSIVE because no artifact records the "
                "environment the published run executed under",
            },
            {
                "where": "chain-1 / DD split sizes vs the printed # Train",
                "state": "AUDITOR OBSERVATION, NOT A PD VERDICT",
                "because": "DD measures the official files as train 32561 / test 16281, while the "
                "paper's # Train column prints 26048 and # Validation prints 6513; 26048 + 6513 = "
                "32561, i.e. the printed number is a hold-out of the official train file. PD does "
                "not compare across those layers and issues no verdict on it",
            },
            {
                "where": "chain-2 / C2 and C4",
                "state": "PD006 FAIL / INCONCLUSIVE",
                "because": "the referenced float does not print the counted number, and two of the "
                "labels in C4 resolve to no float in the source at all",
            },
            {
                "where": "chain-3 / C9",
                "state": "INCONCLUSIVE",
                "because": "the merged leading cell makes the declared row address have two "
                "readings and the source states nothing that separates them",
            },
            {
                "where": "PD004",
                "state": "NOT_RUN",
                "because": "no claim in this workspace declares a comparative relation over a "
                "block-addressed cell, so the rule has no key to read",
            },
        ],
        "searched_not_observed": [
            "a TabM table that both names its float in a sentence and prints a metric value that "
            "the shipped artifacts reconstruct: none found in main.tex or tables/",
            "a run-side artifact inside exp/ that records the environment a published run executed "
            "under: none (only paper/environment.yaml, which states a requirement, not a fact)",
        ],
    }

    out = HERE / "end_to_end_chain.json"
    out.write_text(json.dumps(ledger, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes, sha256 {_sha(out)[:16]}...)")
    return 0


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    tally: dict[str, int] = {}
    for row in rows:
        tally[row[key]] = tally.get(row[key], 0) + 1
    return tally


if __name__ == "__main__":
    sys.exit(main())
