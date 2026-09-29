# Dataset Doctor Report - `F:\DatasetDoctorWork\realworld\adult\prepared`

`tool 0.1.2` · `schema 1.0` · `generated 2026-09-29T05:52:46+00:00` · `dataset ds_05c7465f` · `config cfg_091fd33c` · `16414 ms`

## Verdict

> ### FORMAL_EVAL_INVALID
> do not report a formal metric from this split until the blocking findings are resolved

**1** CRITICAL | **2** HIGH | **4** MEDIUM | **0** LOW | **2** INFO

Blocking findings: **2**. Why this verdict:

- DD009 Conflicting labels on identical content (26 group(s), across splits): 54 samples (status FAIL)
- DD009 Conflicting labels on identical content (1 group(s) inside one split): 2 samples (status FAIL)

## Dataset identity

| Field | Value |
| --- | --- |
| Samples | 48,842 |
| Type | tabular |
| Splits | `test`: 16281, `train`: 32561 |
| Classes | 4 - `<=50K` (24720), `<=50K.` (12435), `>50K` (7841), `>50K.` (3846) |
| Columns | 15 |
| Fingerprint | full |
| Manifest hash | `9bf9cea8ee536e96` |

Columns: `age`*(int)*, `capital_gain`*(int)*, `capital_loss`*(int)*, `education`*(string)*, `education_num`*(int)*, `fnlwgt`*(int)*, `hours_per_week`*(int)*, `income`*(string)*, `marital_status`*(string)*, `native_country`*(string)*, `occupation`*(string)*, `race`*(string)*, `relationship`*(string)*, `sex`*(string)*, `workclass`*(string)*

## Findings (9)


### DD009-0001 - Conflicting labels on identical content (26 group(s), across splits)

`CRITICAL` · FAIL · formal impact `BLOCKING` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD009** Label Conflict

**Where:** 50 file(s), starting `test.csv`, `train.csv`, `test.csv`  
26 content group(s) hold the same data under different labels; 54 samples are involved. In 23 of these group(s) the two labels are one class written two ways - they differ only by whitespace or a trailing '.' - so the copies are the same row appearing twice with a differently encoded answer, not a contradiction between annotators. Normalising the spelling is the first thing to check; the identical content across a split boundary is the part that contaminates the metric.

*Why it matters:* Identical input with two answers makes the label noise floor unremovable: the best a model can do is guess between them. Here one copy is trained and another is scored, so the metric measures recall of the label, not the model's generalisation.

**Affected:** 54 sample(s) (0.1%) · no automatic fix

**Do:** Decide a single label per content hash (majority, or expert review) and re-audit.

**Caveats:**
- For tabular data 'identical content' means identical feature values (label and id columns excluded). Two genuinely different cases can share a coarse feature vector; that is low-cardinality encoding, not mislabelling.
- Labels are compared as exact strings, so one class written two ways reads as a conflict. `encoding_only_groups` counts how many of these groups collapse to a single class once whitespace and a trailing '.' are removed; that count is a description of the evidence, and no grouping or severity uses it.

<details><summary>Evidence</summary>

```json
{
  "encoding_only_groups": 23,
  "encoding_only_labels": [
    {
      "content_hash": "cd2a47a32e6f2309",
      "labels": [
        "<=50K",
        "<=50K."
      ]
    },
    {
      "content_hash": "1f65e6ac236d035f",
      "labels": [
        "<=50K",
        "<=50K."
      ]
    },
    {
      "content_hash": "aaf0adeafd9d2d9f",
      "labels": [
        "<=50K",
        "<=50K."
      ]
    },
    {
      "content_hash": "8bbd2edb62e91f41",
      "labels": [
        "<=50K",
        "<=50K."
      ]
    },
    {
      "content_hash": "6c1a38e16f425482",
      "labels": [
        "<=50K",
        "<=50K."
      ]
    }
  ],
  "groups": [
    {
      "content_hash": "cd2a47a32e6f2309",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "1dfdcdce88383779",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "e2bb8e50a283f706",
          "split": "train"
        },
        {
          "label": "<=50K",
          "sample_id": "4030708d300af5f5",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "1f65e6ac236d035f",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "93be50ef429b9ebc",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "5cbd4cfc2967ff61",
          "split": "train"
        },
        {
          "label": "<=50K",
          "sample_id": "9b046dda3b983655",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "aaf0adeafd9d2d9f",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "c773173406cb655e",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "448b234e5f4dcd29",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "8c8687535d0f4134",
      "labels": [
        "<=50K.",
        ">50K"
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "e445e2b785375cd7",
          "split": "test"
        },
        {
          "label": ">50K",
          "sample_id": "852938450a508259",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "8bbd2edb62e91f41",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "6e3e9f7ac9dd8de9",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "de0662a28d9a8335",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "6c1a38e16f425482",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "4f787a41a455ef90",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "206525cf332dd4b2",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "76fe0036e9f4d601",
      "labels": [
        "<=50K",
        ">50K."
      ],
      "members": [
        {
          "label": ">50K.",
          "sample_id": "9a3cebebfc6e3632",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "97d78eb2dbd7d8da",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "113b090a75c5d49f",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "be827ed3a0b50ac8",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "eeb99e0d5a5f1de3",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "b70169dcb345d19c",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "2a03786b34a4dfda",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "72b15bd2f9008d79",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "d4d64d9f47f79943",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "0e3484105ddd4b11",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "03668e5587ec4995",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "4d84f29c3a8d9631",
      "labels": [
        ">50K",
        ">50K."
      ],
      "members": [
        {
          "label": ">50K.",
          "sample_id": "02847304393e54b8",
          "split": "test"
        },
        {
          "label": ">50K",
          "sample_id": "a0dcefa0ab526619",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "f51b36e8294b634a",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "9008fe130f36d6cd",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "87d779298b5d77ee",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "b1c6057ca01c5eda",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "546589872966cffd",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "e9afd5bc8c9f1c40",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "6bf15ee711f91140",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "babd2c90f83e9410",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "1da2e3c30419b375",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "1b2094730837a8b5",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "86dd135d398028ba",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "b1156732fad11316",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "ddb78e431fdbf983",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "6d1810b2621db7ca",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "226eec58b62f2c31",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "0f7401f9b926107d",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "d7ef6794639cddf2",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "45b64a905fa76b1a",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "49d9c86ae6e103e2",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "f17dd9438ae947c3",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "069d91395ef2b3af",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "93c6b165c54ab5f9",
      "labels": [
        ">50K",
        ">50K."
      ],
      "members": [
        {
          "label": ">50K.",
          "sample_id": "03fb687a6b300dff",
          "split": "test"
        },
        {
          "label": ">50K",
          "sample_id": "8b2fdea0ab9cef3c",
          "split": "train"
        }
      ]
    },
    {
      "content_hash": "d59b5bd322abcfde",
      "labels": [
        "<=50K",
        "<=50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "4aed6ac77e647656",
          "split": "test"
        },
        {
          "label": "<=50K",
          "sample_id": "c42d9eadef4bdc9f",
          "split": "train"
        }
      ]
    }
  ],
  "scope": "cross_split"
}
```

</details>

Samples: `test.csv#row=1668`, `train.csv#row=3118`, `test.csv#row=1781`, `train.csv#row=16683`, `test.csv#row=1854`, `train.csv#row=20567`, `test.csv#row=1863`, `train.csv#row=30384`, `test.csv#row=2373`, `train.csv#row=29506` (+40 more)

_Known false-positive mode:_ Duplicate images with different labels are ambiguous only if content is truly identical; near-identical frames with different labels are a labelling-policy question.

Rule doc: `docs/rules/DD009-label-conflict.md`

### DD009-0002 - Conflicting labels on identical content (1 group(s) inside one split)

`HIGH` · FAIL · formal impact `BLOCKING` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD009** Label Conflict

**Where:** 2 file(s), starting `test.csv`, `test.csv`  
1 content group(s) hold the same data under different labels; 2 samples are involved.

*Why it matters:* Identical input with two answers makes the label noise floor unremovable: the best a model can do is guess between them. Here the contradiction sits inside the evaluation split, where the same input is counted both right and wrong, so no accuracy on this split is interpretable.

**Affected:** 2 sample(s) (0.0%) · no automatic fix

**Do:** Decide a single label per content hash (majority, or expert review) and re-audit.

**Caveats:**
- For tabular data 'identical content' means identical feature values (label and id columns excluded). Two genuinely different cases can share a coarse feature vector; that is low-cardinality encoding, not mislabelling.
- Labels are compared as exact strings, so one class written two ways reads as a conflict. `encoding_only_groups` counts how many of these groups collapse to a single class once whitespace and a trailing '.' are removed; that count is a description of the evidence, and no grouping or severity uses it.

<details><summary>Evidence</summary>

```json
{
  "encoding_only_groups": 0,
  "encoding_only_labels": [],
  "groups": [
    {
      "content_hash": "30ef735760f97163",
      "labels": [
        "<=50K.",
        ">50K."
      ],
      "members": [
        {
          "label": "<=50K.",
          "sample_id": "b419d0f6fc2c5f60",
          "split": "test"
        },
        {
          "label": ">50K.",
          "sample_id": "a970997acbbfaffe",
          "split": "test"
        }
      ]
    }
  ],
  "scope": "within_split"
}
```

</details>

Samples: `test.csv#row=11692`, `test.csv#row=16161`

_Known false-positive mode:_ Duplicate images with different labels are ambiguous only if content is truly identical; near-identical frames with different labels are a labelling-policy question.

Rule doc: `docs/rules/DD009-label-conflict.md`

### DD013-0001 - Label distribution shift: train vs test

`HIGH` · WARNING · formal impact `POTENTIAL` · evidence `STATISTICAL` · confidence `HIGH` · rule **DD013** Label Distribution Shift

**Where:** `train` <-> `test` (cross-split)  
P(income) differs between train and test: total variation 1.000, Jensen-Shannon distance 0.833. No label value appears in both splits, so this compares two vocabularies rather than two class proportions: a single class written differently in each file reaches total variation 1.000 exactly as genuinely disjoint classes do. Read it together with DD014, which names the categories that appear on one side only.

*Why it matters:* A weighted average over classes changes when prevalence changes, even with a fixed confusion matrix. Comparing this test set's accuracy with a differently balanced one is comparing different questions.

**Affected:** 16,281 sample(s) (33.3%) · no automatic fix

**Do:** Use metrics robust to prevalence shift, or document the intended difference.

**Caveats:**
- A test set deliberately enriched for rare cases is a design choice, not an error. Report it as the evaluation protocol instead of 'fixing' it.

<details><summary>Evidence</summary>

```json
{
  "common_support_classes": 0,
  "js_distance": 0.8326,
  "largest_movers": [
    {
      "class": " <=50K.",
      "test_share": 0.7638,
      "train_share": 0.0
    },
    {
      "class": " <=50K",
      "test_share": 0.0,
      "train_share": 0.7592
    },
    {
      "class": " >50K",
      "test_share": 0.0,
      "train_share": 0.2408
    },
    {
      "class": " >50K.",
      "test_share": 0.2362,
      "train_share": 0.0
    }
  ],
  "test_total": 16281,
  "threshold": 0.05,
  "train_total": 32561,
  "tv_distance": 1.0
}
```

</details>

_Known false-positive mode:_ If the test set is enriched for rare cases on purpose, the difference is intended - report it, do not fail it.

Rule doc: `docs/rules/DD013-label-shift.md`

### DD003-0001 - Within-split exact duplicates in 'train'

`MEDIUM` · WARNING · formal impact `POTENTIAL` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD003** Exact Duplicate

**Where:** split `train`  
23 identical content group(s) repeat inside train (24 redundant copies).

*Why it matters:* Duplicates do not leak across the evaluation boundary here, but they overweight the duplicated material in the loss and shrink the effective sample size.

**Affected:** 47 sample(s) (0.1%) · no automatic fix

**Do:** Remove one member of each cross-split group (keep the earliest, or drop from train), then re-audit. Never let the tool delete data for you.

<details><summary>Evidence</summary>

```json
{
  "duplicate_groups": 23,
  "groups": [
    {
      "members": [
        "cf7978f3fced182f",
        "e523b52195853adc",
        "1149ed434f6d4f34"
      ],
      "row_sha256": "b76abe78d3641048"
    },
    {
      "members": [
        "648b8b48d459e7d8",
        "12d0aaa2045f54ff"
      ],
      "row_sha256": "e28fce607c47a9d3"
    },
    {
      "members": [
        "c73a2de65c7e96f5",
        "ca2cac50f95f4833"
      ],
      "row_sha256": "c7a8dbbfcecd0505"
    },
    {
      "members": [
        "5cbd4cfc2967ff61",
        "9b046dda3b983655"
      ],
      "row_sha256": "464329c462a94320"
    },
    {
      "members": [
        "eb934598aea532a8",
        "121a68dd76bb4f7b"
      ],
      "row_sha256": "fe80875eda4e2eb3"
    },
    {
      "members": [
        "4426bdf98bd31080",
        "bf8720e84924ba39"
      ],
      "row_sha256": "9075717631cf9d2e"
    },
    {
      "members": [
        "97afa24a0a9d7862",
        "ede3097051acaa4f"
      ],
      "row_sha256": "5725c702d9228d67"
    },
    {
      "members": [
        "204ce0f69ebcb273",
        "da062e740cb0e09d"
      ],
      "row_sha256": "4ffff910bc2d8201"
    },
    {
      "members": [
        "afaa4160c1f8a16a",
        "d7eae1895899fc62"
      ],
      "row_sha256": "b5883df23a344474"
    },
    {
      "members": [
        "bf0c23f14614b0a4",
        "8a20c7cff281dd84"
      ],
      "row_sha256": "4a73237381132d5e"
    },
    {
      "members": [
        "b67ab99ea0c3f7b6",
        "9bac9385289fa230"
      ],
      "row_sha256": "1a3c93c152a1a984"
    },
    {
      "members": [
        "e2bb8e50a283f706",
        "4030708d300af5f5"
      ],
      "row_sha256": "1b44a2579f3aae3f"
    },
    {
      "members": [
        "f5e07b067babac57",
        "c0a8e27750d2fbe2"
      ],
      "row_sha256": "985fa5859b8e2e26"
    },
    {
      "members": [
        "e0758f8bcd19a505",
        "b57d5c8d64b90361"
      ],
      "row_sha256": "8dc35ae5e9c20e4a"
    },
    {
      "members": [
        "6fc1c0189929194f",
        "f22fe8e93a1daadc"
      ],
      "row_sha256": "d1368c105bbf2323"
    },
    {
      "members": [
        "7e0236fe0af654c9",
        "3de91e250db4c4cd"
      ],
      "row_sha256": "1a53da17244686c9"
    },
    {
      "members": [
        "9b4b2e370b7ee963",
        "72dae4b5cac95c95"
      ],
      "row_sha256": "049a17e9f8a808e5"
    },
    {
      "members": [
        "f5c5c5ab9f7c7bcc",
        "71ad1135420dc5c7"
      ],
      "row_sha256": "8e0e038c846541c8"
    },
    {
      "members": [
        "0612ec903995431c",
        "fee468758674d24f"
      ],
      "row_sha256": "d5a08082897a9fd7"
    },
    {
      "members": [
        "22fac0f8db00ed55",
        "1f937845724e3834"
      ],
      "row_sha256": "707c56ff189391d1"
    }
  ],
  "key": "row_sha256",
  "redundant_copies": 24
}
```

</details>

Samples: `train.csv#row=2303`, `train.csv#row=5104`, `train.csv#row=3917`, `train.csv#row=31993`, `train.csv#row=4325`, `train.csv#row=4881`, `train.csv#row=4767`, `train.csv#row=9171`, `train.csv#row=4940`, `train.csv#row=29157` (+37 more)

_Known false-positive mode:_ Within-split duplication is a sample-weight problem, not a leakage problem; it is reported separately at lower severity. Synthetic or tile-based imagery can legitimately repeat.

Rule doc: `docs/rules/DD003-exact-duplicate.md`

### DD003-0002 - Within-split exact duplicates in 'test'

`MEDIUM` · WARNING · formal impact `POTENTIAL` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD003** Exact Duplicate

**Where:** split `test`  
5 identical content group(s) repeat inside test (5 redundant copies).

*Why it matters:* Duplicates do not leak across the evaluation boundary here, but they overweight the duplicated material in the loss and shrink the effective sample size.

**Affected:** 10 sample(s) (0.0%) · no automatic fix

**Do:** Remove one member of each cross-split group (keep the earliest, or drop from train), then re-audit. Never let the tool delete data for you.

<details><summary>Evidence</summary>

```json
{
  "duplicate_groups": 5,
  "groups": [
    {
      "members": [
        "abaeffc5dc9319a0",
        "856ec42566b8b003"
      ],
      "row_sha256": "cc2949b3c2e9912d"
    },
    {
      "members": [
        "03f57aebe4c10abf",
        "2e41af7706cf5e79"
      ],
      "row_sha256": "f80a067ef8b8ffe2"
    },
    {
      "members": [
        "f77465ba6b9603d2",
        "39f8a49ca68752f8"
      ],
      "row_sha256": "0ff7988733bac292"
    },
    {
      "members": [
        "f208b60ecd5958b4",
        "a3b5c63e822d9e22"
      ],
      "row_sha256": "892cb9288cee850c"
    },
    {
      "members": [
        "6abf3a937bebf965",
        "e6361db3aa84208e"
      ],
      "row_sha256": "5ff78862267fa534"
    }
  ],
  "key": "row_sha256",
  "redundant_copies": 5
}
```

</details>

Samples: `test.csv#row=488`, `test.csv#row=864`, `test.csv#row=1319`, `test.csv#row=11189`, `test.csv#row=3900`, `test.csv#row=15960`, `test.csv#row=7021`, `test.csv#row=13848`, `test.csv#row=9249`, `test.csv#row=11212`

_Known false-positive mode:_ Within-split duplication is a sample-weight problem, not a leakage problem; it is reported separately at lower severity. Synthetic or tile-based imagery can legitimately repeat.

Rule doc: `docs/rules/DD003-exact-duplicate.md`

### DD009-0003 - Conflicting labels on identical content (1 group(s) inside one split)

`MEDIUM` · WARNING · formal impact `POTENTIAL` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD009** Label Conflict

**Where:** 2 file(s), starting `train.csv`, `train.csv`  
1 content group(s) hold the same data under different labels; 2 samples are involved.

*Why it matters:* Identical input with two answers makes the label noise floor unremovable: the best a model can do is guess between them. Here the contradiction is confined to the training side. It puts a floor under achievable accuracy, but it does not make the test-set measurement invalid - reporting it as leakage would confuse label noise with contamination.

**Affected:** 2 sample(s) (0.0%) · no automatic fix

**Do:** Decide a single label per content hash (majority, or expert review) and re-audit.

**Caveats:**
- For tabular data 'identical content' means identical feature values (label and id columns excluded). Two genuinely different cases can share a coarse feature vector; that is low-cardinality encoding, not mislabelling.
- Labels are compared as exact strings, so one class written two ways reads as a conflict. `encoding_only_groups` counts how many of these groups collapse to a single class once whitespace and a trailing '.' are removed; that count is a description of the evidence, and no grouping or severity uses it.

<details><summary>Evidence</summary>

```json
{
  "encoding_only_groups": 0,
  "encoding_only_labels": [],
  "groups": [
    {
      "content_hash": "d75f547ca7b1352e",
      "labels": [
        "<=50K",
        ">50K"
      ],
      "members": [
        {
          "label": "<=50K",
          "sample_id": "f6a1646cf728384d",
          "split": "train"
        },
        {
          "label": ">50K",
          "sample_id": "0dd80d33b4b768a4",
          "split": "train"
        }
      ]
    }
  ],
  "scope": "within_split"
}
```

</details>

Samples: `train.csv#row=848`, `train.csv#row=22761`

_Known false-positive mode:_ Duplicate images with different labels are ambiguous only if content is truly identical; near-identical frames with different labels are a labelling-policy question.

Rule doc: `docs/rules/DD009-label-conflict.md`

### DD014-0001 - Unseen categories in test

`MEDIUM` · WARNING · formal impact `POTENTIAL` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD014** Schema Drift

**Where:** `train` <-> `test` (cross-split)  
2 category value(s) appear in test but never in train across 1 column(s).

*Why it matters:* A categorical encoder fitted on train has no representation for these values. They land in an unknown bucket, so whatever they predict is decided by the encoder's fallback, not by training.

**Affected:** 0 sample(s) (0.0%) · no automatic fix

**Do:** Rebuild the split from one schema version, or map dtypes explicitly at load time.

<details><summary>Evidence</summary>

```json
{
  "columns": {
    "income": [
      " <=50K.",
      " >50K."
    ]
  },
  "identifier_columns_skipped": []
}
```

</details>

_Known false-positive mode:_ A column dropped from test because it is only available at training time (e.g. an annotation artefact) is correct, not drift.

Rule doc: `docs/rules/DD014-schema-drift.md`

### DD001-0001 - Dataset identified: ds_05c7465f

`INFO` · PASS · formal impact `NONE` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD001** Dataset Identity

**Where:** dataset-wide (dataset)  
48842 samples of type tabular; splits {'test': 16281, 'train': 32561}; 4 class(es); fingerprint mode full.

*Why it matters:* Every other finding cites sample ids from this manifest. Without a recorded identity and manifest hash, a published number cannot be tied back to the bytes that produced it.

**Affected:** 48,842 sample(s) (100.0%) · no automatic fix

**Do:** Nothing to fix: this is the baseline. Commit dataset-doctor.yaml and the manifest so a reviewer can reproduce it.

<details><summary>Evidence</summary>

```json
{
  "adapter_notes": [],
  "class_count": 4,
  "config_hash": "cfg_091fd33c9ce94a35",
  "dataset_id": "ds_05c7465f",
  "file_extensions": {
    ".csv": 48842
  },
  "inference_notes": [
    "Splits discovered from files and directories: test(file), train(file)"
  ],
  "manifest_hash": "9bf9cea8ee536e96483be1e5a0efef44",
  "schema": {
    "age": "int",
    "capital_gain": "int",
    "capital_loss": "int",
    "education": "string",
    "education_num": "int",
    "fnlwgt": "int",
    "hours_per_week": "int",
    "income": "string",
    "marital_status": "string",
    "native_country": "string",
    "occupation": "string",
    "race": "string",
    "relationship": "string",
    "sex": "string",
    "workclass": "string"
  },
  "split_sizes": {
    "test": 16281,
    "train": 32561
  }
}
```

</details>

Rule doc: `docs/rules/DD001-dataset-identity.md`

### DD020-0001 - Partial provenance

`INFO` · PASS · formal impact `NONE` · evidence `DETERMINISTIC` · confidence `HIGH` · rule **DD020** Dataset Provenance

**Where:** dataset-wide (config)  
Provenance declared but incomplete; missing: license.

*Why it matters:* Version and licence gaps are the ones that bite when a result is re-checked.

**Affected:** 0 sample(s) (0.0%) · no automatic fix

**Do:** Fill in the `provenance:` block of dataset-doctor.yaml.

<details><summary>Evidence</summary>

```json
{
  "declared": {
    "download_date": "2026-09-24",
    "license": "",
    "source": "UCI Machine Learning Repository - Adult / Census Income (Kohavi & Becker, 1996)",
    "version": "1996"
  },
  "missing": [
    "license"
  ]
}
```

</details>

_Known false-positive mode:_ Missing provenance is a reproducibility gap, not a corruption.

Rule doc: `docs/rules/DD020-provenance.md`

## Rule coverage

A rule that could not run is listed as such; PASS means the detector covered the data.

| Rule | Name | Status | Findings | Highest severity | Note |
| --- | --- | --- | --- | --- | --- |
| DD001 | Dataset Identity | PASS | 1 | INFO |  |
| DD002 | Split Integrity | PASS | 0 | - |  |
| DD003 | Exact Duplicate | WARNING | 2 | MEDIUM |  |
| DD004 | Near Duplicate | UNSUPPORTED | 0 | - | near-duplicate detection is defined for image datasets |
| DD005 | Group / Entity Leakage | NOT_RUN | 0 | - | no group columns declared (groups.columns / groups.entity_column) |
| DD006 | Temporal Leakage | NOT_RUN | 0 | - | temporal.column is not configured |
| DD007 | Target Leakage | PASS | 0 | - |  |
| DD008 | Identifier / Feature Leakage | PASS | 0 | - |  |
| DD009 | Label Conflict | FAIL | 3 | MEDIUM |  |
| DD010 | Missing Labels | PASS | 0 | - |  |
| DD011 | Class Imbalance | PASS | 0 | - |  |
| DD012 | Feature / Distribution Shift | PASS | 0 | - |  |
| DD013 | Label Distribution Shift | WARNING | 1 | HIGH |  |
| DD014 | Schema Drift | WARNING | 1 | MEDIUM |  |
| DD015 | Missingness Shift | PASS | 0 | - |  |
| DD016 | Corrupt Sample | PASS | 0 | - |  |
| DD017 | Image Property Shift | UNSUPPORTED | 0 | - | image property shift applies to image datasets |
| DD018 | Version Drift | NOT_RUN | 0 | - | no baseline snapshot was supplied (--baseline) |
| DD019 | Split Drift | NOT_RUN | 0 | - | no baseline snapshot was supplied (--baseline) |
| DD020 | Dataset Provenance | PASS | 1 | INFO |  |
| DD021 | PII Exposure | PASS | 0 | - |  |

| Coverage | Value |
| --- | --- |
| Fingerprint mode | full |
| Sample fraction | 1.0 |
| Rules attempted | 21/21 |
| INCONCLUSIVE | - |
| Not run | DD004, DD005, DD006, DD017, DD018, DD019 |
| Suppressed | - |

Notes from discovery:
- Splits discovered from files and directories: test(file), train(file)

## Repair plan

Run in this order; later steps depend on earlier ones.

1.    **Collapse exact duplicates before splitting** _(writes a new directory; original untouched)_

   0 cross-split duplicate group(s) and 2 within-split group(s). Keep one member per hash and record which was dropped; the finding evidence lists each hash with its sample ids.

   ```
   dataset-doctor-audit split F:\DatasetDoctorWork\realworld\adult\prepared --dedupe --output F:\DatasetDoctorWork\realworld\adult\prepared-deduped
   ```

   _Resolves:_ DD003-0001, DD003-0002
   _Why now:_ De-duplication changes row identity, so it must precede the split; otherwise the same content can land on both sides again.

   _Residual risk:_ De-duplicating a benchmark you did not build can change its published metrics.
2.    **Rebuild the split so shared entities and labels stop crossing** _(writes a new directory; original untouched)_

   Entity/label leakage on the entity column: samples that must not be seen twice are in more than one split. Regenerate the split grouped by that key instead of shuffling rows.

   ```
   dataset-doctor-audit split F:\DatasetDoctorWork\realworld\adult\prepared --output F:\DatasetDoctorWork\realworld\adult\prepared-resplit
   ```

   _Resolves:_ DD009-0001, DD009-0002, DD009-0003
   _Why now:_ This is the only class of finding that can make a bad model look good; every later measurement is computed on the wrong partition until it is fixed.

   _Residual risk:_ A grouped split is coarser: effective sample count drops and class balance may shift.
3.    **Human review: semantics the data cannot answer**

   Unseen categories in test. Decide, per column, whether the value existed before the outcome happened. No statistic can distinguish a strong biomarker from a post-outcome measurement.

   _Resolves:_ DD014-0001
   _Why now:_ These are candidates, not verdicts; acting on them mechanically would delete real signal.

   _Residual risk:_ Dropping a column that turns out to be legitimate loses accuracy you cannot get back.
4.    **Decide whether the distribution difference is the dataset**

   Label distribution shift: train vs test. If the population genuinely differs, fix the evaluation (weighted metrics, per-segment reporting) rather than resampling the data into agreement.

   ```
   dataset-doctor-audit audit F:\DatasetDoctorWork\realworld\adult\prepared --policy research  # tighten or loosen thresholds deliberately
   ```

   _Resolves:_ DD013-0001
   _Why now:_ Shift is a fact about the world; 'fixing' it by resampling hides the very effect the model will be measured on.
5.    **Re-audit and snapshot the fixed dataset**

   Re-run the audit on the new output and diff it against this baseline, so the report shows which findings actually disappeared.

   ```
   dataset-doctor-audit audit F:\DatasetDoctorWork\realworld\adult\prepared --save-snapshot fixed && dataset-doctor-audit diff F:\DatasetDoctorWork\realworld\adult\prepared --baseline current
   ```

   _Resolves:_ verification only
   _Why now:_ A fix that was never re-measured is a claim, not a result.

- Every step that touches data writes to a new directory; the original dataset is never modified.
- Re-audit after each structural step: a fix that is not re-measured is a fix that is not verified.

## Methodology

1. Sample identity: images are hashed by streaming SHA256 over file bytes; tabular rows by SHA256 over a canonical per-row string (NaN has one spelling, floats are rounded to 12 decimals before repr).
2. Facts come from detectors, severities from policy. A finding's severity can only be changed by policies.<rule>.severity, and the report records that it was (metadata.severity_source).
3. Formal-evaluation verdict is rule-based: any BLOCKING finding => INVALID; MEDIUM-or-worse POTENTIAL finding => RISKY; too many INCONCLUSIVE rules => INCONCLUSIVE; else SAFE.
4. Statistics are reported as effect size first. Distribution shift uses standardised mean difference and PSI as the trigger, with KS/Wasserstein/JS as supporting evidence, Benjamini-Hochberg corrected across columns.
5. Near-duplicate search uses exact-match bit-band candidate generation over 64-bit pHash: for threshold t the candidate set is a superset of all pairs within Hamming distance t, so no O(N^2) sweep is needed and coverage loss is only from bucket truncation, which is itself reported.
6. Everything is read-only. No file in the dataset is modified, and reports are written to the output directory chosen by the user.

## Limitations

1. Data leakage has a semantic component that cannot be detected from data alone: a column that is only known after the outcome looks identical, in the table, to a column that is merely predictive. Those cases are reported as candidates, never verdicts.
2. Within-split findings are measured on hashes; a crop, rotation or recompression of an image is invisible to SHA256 and only partially covered by pHash.
3. Group/entity leakage can only be checked for entity columns the user declares. An undeclared patient id is undetectable, so the report lists the columns it did not check.
4. Sampling and metadata fingerprint modes reduce coverage; affected rules answer INCONCLUSIVE instead of PASS.
5. Preprocessing leakage (a scaler fitted on the full data before the split) requires static analysis of the training code and is not implemented in V0.1.
