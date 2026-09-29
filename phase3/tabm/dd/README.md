# Dataset Doctor evidence for the TabM acceptance chain

Two files live here and only two are committed.

| File | Committed? | Size | sha256 |
| --- | --- | --- | --- |
| `report/report.json` | yes | 56,359 B | `c1456a7bf602d4c3b4cda5f316a1fdb9e04ed15b7149ec2eb393046428c82f5f` |
| `report/report.md` | yes | 35,308 B | `927c5ea5b4f9231134e287f809080a8cd05a0d0d72440eefe11b5ee9298e756e` |
| `fingerprint.json` | **no** (git-ignored) | 13,013,232 B | `1f0dd1a5785fafde2627c9e47de94ebf436bbed551e11ac1200ad0804c63c9df` |

## Why `fingerprint.json` is not in git

It is the per-row identity of the Adult dataset: 48,842 entries, each with a full SHA-256 of the row and
a sample id. Nothing in it is authored by Paper Doctor and nothing in it is small. It is the same class of
artifact as the arXiv corpora in `phase3/acceptance-inputs/`, which this repository also refuses to vendor
and instead rebuilds from a pinned digest. The pin here is the sha256 above, recorded twice - in this table
and in `phase3/tabm/end_to_end_chain.json` under `dd_ref.fingerprint_sha256` - and the ledger's `dd_ref`
address is what the four-layer chain asserts.

## Reproducing it

From a checkout, with any released Dataset Doctor installed, against the official Adult copies:

```bash
dataset-doctor-audit fingerprint F:/DatasetDoctorWork/realworld/adult/prepared \
  --mode full -o fingerprint.json
```

The input directory is Dataset Doctor's own prepared Adult tree (`prepared/train.csv` 32,562 lines,
`prepared/test.csv` 16,282 lines); Paper Doctor never wrote to it.

**Measured on 2026-09-29**, in this repository's environment: that command emitted 13,013,232 bytes with
sha256 `1f0dd1a5785fafde2627c9e47de94ebf436bbed551e11ac1200ad0804c63c9df`, and reported
`dataset ds_05c7465f manifest 9bf9cea8ee536e96 (48,842 samples, full)`. Both digests match the ones the
ledger pins, so the excluded file is genuinely regenerable rather than merely asserted to be.

One thing that reproduction made visible, recorded rather than smoothed over: the CLI installed on this
machine is `dataset-doctor-audit 0.1.0`, while `report/report.json` - the original evidence, produced
earlier the same day - records `"tool_version": "0.1.2"`. The fingerprint bytes were identical across
those two versions, because the fingerprint payload carries no version field; the audit report is
version-stamped and is the artifact of record for the DD layer. Whether 0.1.0 and 0.1.2 agree on the
*report* was not tested here, and is not claimed.

## What Paper Doctor does with this layer

Nothing at runtime. The DD layer exists so the chain `paper claim -> PD -> reported result -> RD ->
aggregation/selection -> ED -> run provenance -> DD -> dataset identity` has a dataset fingerprint at its
end. The link that a reviewer can actually check is in the ledger: `ds_05c7465f` is the Adult identity the
TabM experiment's own declared dataset argument resolves to, and `eval_safety` there is
`FORMAL_EVAL_INVALID`, which is Dataset Doctor's finding about the dataset, not Paper Doctor's judgement
of the paper.
