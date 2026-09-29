# Paper Doctor

Paper Doctor checks whether an explicitly linked claim in a LaTeX paper is faithful to the reported
evidence behind it. It reads three things and nothing else: the paper source, one Result Doctor
findings artifact, and a `paper-doctor.yml` manifest that names them and says which sentences it
wants judged.

It never reads a PDF, never downloads anything, never searches the network, never runs an
experiment, and never verifies a bibliography. It produces no score and no verdict about the paper.

## What this is not

Read this before reading a finding.

Paper Doctor audits **paper claim -> reported evidence consistency**, one declared relation at a
time. It does not audit whether the paper is true, whether the experiments were well run, or
whether the evidence itself is right. The chain it can reach ends where the numbers are printed.

It does **not** judge: fraud or misconduct; novelty; whether a paper should be accepted or
rejected; theorem or proof correctness; whether a result reproduces; whether a claim is causal,
fair, or meaningful in the world; whether any citation or external fact is real.

**What a `FAIL` says**: one rule found one inconsistency between one declared claim and the evidence
that declaration points at. **What it does not say**: that the paper is false, unreliable,
fraudulent, or rejected. A `FAIL` is a question to ask an author, not a verdict on a paper.

**What a `FAIL` does not localize**: Paper Doctor compares a *sentence* against a *declaration*.
When they disagree, either side can be the wrong one - the paper's sentence may be stale, or the
manifest may have pointed the claim at the wrong table, column or row. Paper Doctor cannot tell
which. The reason line quotes both sides and names the address it used, so you can check.

The rules are literal-presence tests over declared structure. PD006 in particular asks whether the
referenced float actually *prints* the attributed content; it does not establish that the reference
was intended, nor that a different float would be wrong. `INCONCLUSIVE` is a first-class answer, not
a failure: untraceable is not false.

## Install

Requires Python 3.11 or newer. The only runtime dependency is PyYAML.

From PyPI:

```text
pip install paper-doctor==0.1.0
```

From a checkout, in a virtual environment:

```text
python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # macOS and Linux
pip install -e .
```

If your shell does not keep state between commands, activation will not carry over. Call the
executables by path instead - `.venv/Scripts/pip` and `.venv/Scripts/paper-doctor` on Windows,
`.venv/bin/pip` and `.venv/bin/paper-doctor` elsewhere.

Check it is on PATH:

```text
paper-doctor --version
paper-doctor --help
```

Both routes run the same code and print the same version, because the version has one source in the
package. Choose by what you are auditing: the PyPI install for any workspace you point at it, and the
checkout when you want the example or an acceptance workspace, since those directories only exist in
the repository. A checkout has one extra step the installed package does not need - see "When the audit
exits `2` because the paper source is not there" below.

## Quickstart

The repository ships a runnable example: `examples/quickstart/` holds a two-line table, three claims
and a manifest that declares them. From a checkout:

```text
paper-doctor audit examples/quickstart
```

This is what it prints, with the three claims being: C1 quotes 0.91 and the table prints 0.91; C2
quotes 0.92 while the table prints 0.88; C3 states a scope and declares no link:

```text
# paper-doctor audit examples/quickstart/paper-doctor.yml
PD001   PASS            C1
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:4  links=[L1, L2]
        reason: declared link(s) with basis AUTHOR_REF_IN_SENTENCE resolve to evidence on file (paper.tex [column=Accuracy,row=A], tab-results)
PD001   PASS            C2
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:6  links=[L3, L4]
        reason: declared link(s) with basis AUTHOR_REF_IN_SENTENCE resolve to evidence on file (paper.tex [column=Accuracy,row=B], tab-results)
PD001   INCONCLUSIVE    C3
        claim:  form=SCOPE  locator=paper.tex:8  links=[]
        reason: the claim carries no declared support link; untraceable is not false
PD002   NOT_APPLICABLE  C3
        claim:  form=SCOPE  locator=paper.tex:8  links=[]
        reason: the claim states no count (unit=aggregation); nothing to compare
PD003   PASS            C1
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:4  links=[L1, L2]
        reason: the prose value and the printed cell at (column=Accuracy, row=A, block=b1 [hline at paper.tex:15], unit=reported_cell) of table:1 are the same string
PD003   FAIL            C2
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:6  links=[L3, L4]
        reason: the claim states 0.92 but the printed cell at (column=Accuracy, row=B, block=b1 [hline at paper.tex:15], unit=reported_cell) of table:1 states 0.88; both declare 'accuracy' and the declared precision is round:2.0
PD004   NOT_RUN         rule:PD004
        reason: no target was supplied for this rule: claims, links is populated, but nothing in it carries the key PD004 reads
PD005   NOT_RUN         rule:PD005
        reason: no target was supplied for this rule: claims, rd is populated, but nothing in it carries the key PD005 reads
PD006   PASS            C1
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:4  links=[L1, L2]
        reason: the reference resolves and 0.91 is printed inside the referenced float
PD006   INCONCLUSIVE    C2
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:6  links=[L3, L4]
        reason: 0.92 is printed in no parsed float, so the attributed content itself is unverifiable
PD007   NOT_APPLICABLE  C1
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:4  links=[L1, L2]
        reason: the claim declares no same_as pairing, so there is no cross-section relation to check
PD007   NOT_APPLICABLE  C2
        claim:  form=NUMERIC_ATTRIBUTION  locator=paper.tex:6  links=[L3, L4]
        reason: the claim declares no same_as pairing, so there is no cross-section relation to check
PD007   NOT_APPLICABLE  C3
        claim:  form=SCOPE  locator=paper.tex:8  links=[]
        reason: the claim declares no same_as pairing, so there is no cross-section relation to check

PASS: 4
FAIL: 1
INCONCLUSIVE: 2
NOT_APPLICABLE: 4
NOT_RUN: 2
```

The command exits `0` even though one finding is a `FAIL`, because the audit ran.

Write the same findings as machine-readable JSON (the destination is resolved against your current
directory, not the workspace; its directory must already exist, because Paper Doctor will not create
it, and the listing still goes to stdout):

```text
paper-doctor audit examples/quickstart --json report.json
```

## The seven rules

A rule only ever sees what the manifest declares. "What the manifest supplies" is therefore the
prerequisite for a rule to say anything at all; with nothing supplied the answer is `NOT_RUN`, whose
remedy is to declare the missing field, not to rerun the command.

| Rule | Question it asks | What the manifest must supply | Statuses it can answer |
| --- | --- | --- | --- |
| `PD001` Claim Traceability | does this claim have at least one explicitly based support link? | `_claims[].links` naming entries in `_links` | `PASS`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD002` Evidence Scope Consistency | does the scope the claim states match the scope of the evidence as declared or recovered? | `scope` (`stated_count`, `unit`, `universe_status`, ...) and a link to evidence that carries a count | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD003` Quantitative Claim Consistency | does the number the claim states equal the number printed at the locus the claim resolves to? | a `NUMERIC_ATTRIBUTION` claim and a link that resolves to one printed cell or anchor | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD004` Comparative Claim Support | over the comparison set the claim resolves to, does the stated relation hold for every member? | a `COMPARATIVE`/`SUPERLATIVE` claim, a float, and the comparison basis (and block, if the table repeats rows) | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD005` Qualification Preservation | does the claim carry every qualification that the evidence carries? | `qualifiers` on the claim and an evidence side that carries qualifiers | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD006` Result Reference Integrity | does the reference in the claim resolve to the float that actually carries the attributed content? | a claim that names a `\autoref`/`\ref` label and an anchor for that label | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |
| `PD007` Cross-Section Claim Consistency | do two claims with the same predicate and subjects state the same proposition? | `same_as` pairing two claim ids, with `predicate` and `subjects` on both | `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE` |

Two things are not in any rule's own answer set. `NOT_RUN` is emitted by the audit layer, not by a
rule: it means the run asked for that rule and nothing in the manifest carried the field it reads, so
the remedy is to declare it. And `PD001` has no `FAIL`: a claim with no declared link is untraceable,
which is `INCONCLUSIVE`, not false.

`PD006` deserves one more warning because its `FAIL` surprises readers. It compares **printed
strings**: it asks whether the anchor the reference resolves to prints the attributed content. A table
that lists eight dataset rows without printing the character `8` anywhere does not print it, so a claim
of "$8$ datasets" referred to that table `FAIL`s even though a human counting rows would agree with
the paper. Row-counting, column-summing and every other act of reading meaning into a float is outside
the audited universe by design; a `PD006` `FAIL` means "not printed where the reference points", and
says nothing about whether the sentence is right.

Every rule is evaluated for every target it can read; the listing groups by rule, then by claim, in
canonical order, and the trailing tally counts the five statuses. Nothing is summarised away.

## Statuses

| Status | Meaning |
| --- | --- |
| `PASS` | this narrow relation agrees with the evidence on file; nothing more |
| `FAIL` | one rule found this claim disagree with its linked evidence for this target |
| `INCONCLUSIVE` | the evidence on file is not sufficient to decide |
| `NOT_APPLICABLE` | this target has no such relation to check |
| `NOT_RUN` | no target of the class this rule reads was supplied |

## Exit codes

| Code | Meaning | What to do |
| --- | --- | --- |
| `0` | the audit ran, whatever the rules said. A `FAIL` exits `0`. | read the findings |
| `2` | the input is not a readable contract: bad YAML, a wrong field, an unknown key, a **declared input path that does not resolve**, a digest that does not match the bytes, or a `--json` destination whose directory does not exist | fix the manifest or the path; the message is `{code} at {field path}: {problem}` and names the absolute location it tried |
| `1` | Paper Doctor itself failed unexpectedly | treat it as a bug; the audit did not complete, so nothing printed should be trusted |

Exit codes track the *contract*, never the *findings*. Twelve `P_*` validation codes are frozen;
a thirteenth would be a contract change, and the test suite asserts the set.

## The manifest

Four sections, in this fixed order - the manifest is evidence about what the author declared, and a
declaration establishes provenance, not correctness:

```yaml
schema_version: 1
_registry:
  paper:
    path: paper.tex
    sha256: b81a75885e5d62b073d6bf3c9ea1b6b4a7ff336fdd0400bc79c72228c5fa07de
    size: 439
  rd_findings:
    path: findings.json
    sha256: 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
    size: 3
    rd_version: 0.1.0
_claims:
  - claim_id: C1
    text: Our model reaches $0.91$ accuracy, reported in \autoref{tab:results}.
    locator:
      path: paper.tex
      line: 4
      text: Our model reaches $0.91$ accuracy, reported in \autoref{tab:results}.
    form: NUMERIC_ATTRIBUTION
    links: [L1, L2]
  - claim_id: C2
    text: Baseline B reaches $0.92$ accuracy in \autoref{tab:results}.
    locator:
      path: paper.tex
      line: 6
      text: Baseline B reaches $0.92$ accuracy in \autoref{tab:results}.
    form: NUMERIC_ATTRIBUTION
    links: [L3, L4]
  - claim_id: C3
    text: We evaluate the two models across $4$ held-out splits.
    locator:
      path: paper.tex
      line: 8
      text: We evaluate the two models across $4$ held-out splits.
    form: SCOPE
    links: []
_floats:
  - float_id: tab-results
    label: 'tab:results'
    quantity_declaration: accuracy
    precision_declaration: 'round: 2'
_links:
  - link_id: L1
    claim: C1
    target_kind: FLOAT
    target_ref: tab-results
    link_basis: AUTHOR_REF_IN_SENTENCE
  - link_id: L2
    claim: C1
    target_kind: PROSE
    target_ref:
      path: paper.tex
      column: Accuracy
      row: A
    link_basis: AUTHOR_REF_IN_SENTENCE
    quantity_identity: accuracy
  - link_id: L3
    claim: C2
    target_kind: FLOAT
    target_ref: tab-results
    link_basis: AUTHOR_REF_IN_SENTENCE
  - link_id: L4
    claim: C2
    target_kind: PROSE
    target_ref:
      path: paper.tex
      column: Accuracy
      row: B
    link_basis: AUTHOR_REF_IN_SENTENCE
    quantity_identity: accuracy
```

That block is `examples/quickstart/paper-doctor.yml` verbatim, and a test pins it: what the README
shows is what the tool runs, not a paraphrase of it.

### Paths

Every path is resolved against the directory that holds `paper-doctor.yml`, so a workspace can be
moved as a unit:

- `_registry.paper.root` (optional) is where the paper's source files live. Relative to the manifest
  directory, or absolute. Paths *inside* it must stay inside it. If it is missing, `P_UNRESOLVED_REF`
  quotes both the declared string and the absolute path that was tried, and tells you to restore the
  source there or repoint the root.
- `_registry.rd_findings.path` is likewise resolved against the manifest directory. It must exist.
- `_claims[].locator.path` and PROSE `target_ref.path` are resolved against the paper root.

`_registry.paper.sha256` and `size` are verified before the file is read, and
`_registry.rd_findings.sha256` and `size` are verified as it is parsed. They are the author's own
commitment to the exact bytes audited. To fill them in:

```text
sha256sum paper.tex
wc -c < paper.tex
```

A digest mismatch is reported as `P_UNRESOLVED_REF` naming both hashes. Nothing is repaired
silently: if you intentionally audit different bytes, update the declaration and say so in `note`.

### When the audit exits `2` because the paper source is not there

The most common first failure is a workspace whose declared root is not on disk - a folder copied
without the paper, or a root typed one directory off. The whole message is one line, it exits `2`,
and it quotes both what you declared and what was tried:

```text
P_UNRESOLVED_REF at _registry/paper/root: declared root ../not-on-disk/paper/src resolves to
<the absolute path tried>, which is not a directory: restore the paper source there, or point
_registry/paper/root at the checkout that holds it
```

Paper Doctor will not search for a source, download one, or accept a different file because its name
looks right. There are exactly two ways out:

1. Put the source at the declared path yourself, or edit `root` to the directory that already holds
   it. `main.tex` and everything the manifest addresses must be under that one directory.
2. If you are running from this repository's own source checkout and you want the corpus a shipped
   acceptance workspace declares, use the fetch step documented under "Testing the tool" -
   `python scripts/fetch_acceptance_inputs.py tabm` materialises the pinned bytes into
   `phase3/acceptance-inputs/`, which is precisely where `phase3/tabm/paper-doctor.yml` points.
   From an installed package there is no such script; option 1 is the way.

### Field vocabulary

| Field | Values and meaning |
| --- | --- |
| `form` | one of `NUMERIC_ATTRIBUTION`, `COMPARATIVE`, `SUPERLATIVE`, `SCOPE`, `QUALIFICATION`, `REFERENCE_ATTRIBUTION` |
| `not_audited_reason` | alongside the required `form`: the sentence is declared and put outside the audited universe. Every rule then answers `NOT_APPLICABLE` with the reason `out of the audited universe by declaration: ...`, so the exclusion is visible in the findings instead of silent |
| `quantifier` | `all`, `most`, `some`, `bare` (the default) or `numeric` - whether the claim enumerates or merely asserts existence, as the author declares it |
| `scope` | `{declared_universe, stated_count, unit, members, universe_status, locator}` - what the claim says its evidence covers |
| `universe_status` | `UNKNOWN` (the default), `RECOVERED`, `PARTIAL`, `DECLARED_ONLY` or `UNRECOVERABLE`. PD002 can only `PASS` a count when the status is `RECOVERED`; at any other status an agreeing count is `INCONCLUSIVE`, and the reason says `an unlisted universe cannot be PASSed` |
| `qualifiers` | `{kind, statement, locator}` - conditions the claim or the evidence attaches (e.g. `comparison_basis: per_column`) |
| `same_as` | `{claim, basis}` - the pairing PD007 needs to compare two claims across sections |
| `target_kind` | `FLOAT`, `RD_TARGET` or `PROSE` - the three origins Paper Doctor can judge across, and no other |
| `target_ref` | a `float_id` for `FLOAT`; `[RD002, "aggregation:agg:adult-seed-mean"]` (rule id, finding target) for `RD_TARGET`; `{path, column, row}` for `PROSE` |
| `link_basis` | `AUTHOR_REF_IN_SENTENCE` (the sentence names the float), `AUTHOR_NAMED_FLOAT` (the author named the anchor), or `AUDITOR_DECLARED` (the auditor put the pair together). These are the only bases there are; Paper Doctor never infers a link from a name, a number, or a method |
| `quantity_identity` | the quantity both sides claim to speak about, in the author's words. PD003 compares only when both sides declare the same one |
| `precision_declaration` | on a float: `round: 2` means two decimal places, `round: 0` means integers. PD003 compares **at the declared precision**, so a coarse declaration can make 0.92 and 0.88 agree; the reason always quotes the precision it used |
| `quantity_declaration` | on a float: what the anchor prints, as a plain list, e.g. `accuracy` |

`locator.line` is the line the claim *starts* on. A sentence that wraps across three source lines is
declared at its first one, and `text` is the whole sentence with its internal line breaks turned into
spaces - Paper Doctor compares that text against the source and reports
`P_UNRESOLVED_REF at paper.tex:12: declared claim text starts at line 9, not 12` rather than guessing.

Numbers are addressed by their printed strings. `table:1` in a reason is the float's sequence in the
source, and `(column=Accuracy, row=A)` is the cell the declaration resolved to - it is quoted so you
can open the file at that address and look.

### Finding a row in a table that prints it twice

Some tables print the same model, dataset or metric more than once - under two settings, say, with a
group header over each. Paper Doctor addresses those blocks from the source structure alone: a
full-width `\multicolumn` group header, a rule between groups of rows, or a vertically merged leading
cell such as NiceTabular's `\Block{2-1}{...}`. Each block gets a stable local name, `b1`, `b2`, ... in
source order.

When a claim compares rows that a table prints more than once, declare which block it speaks about
and the audit will not guess:

```yaml
    qualifiers:
      - kind: comparison_basis
        statement: per_column
      - kind: comparison_block
        statement: block=b2
```

Without that declaration the finding is `INCONCLUSIVE`, and its reason names every block that prints
the row and what separates them. A declared `block=` that the table does not contain is reported the
same way; declarations are never repaired. Every reason that used a block quotes the structure that
opened it, for example
`block=b2 [midrule at paper.tex:41; multicolumn group header "Tuned hyperparameters" at paper.tex:44]`.

## Where `findings.json` comes from

From Result Doctor, not from Paper Doctor:

```text
result-doctor audit <run-dir> --json > findings.json
```

Paper Doctor reads that artifact and never re-audits it. It imports no Result Doctor code, and it
cannot raise the certainty of an upstream finding - a `NaN` upstream stays undetermined here. The
`RD002`-style ids in a `RD_TARGET` link are Result Doctor's rule ids, and they are addressed exactly
as Result Doctor emitted them.

## Testing the tool

```text
pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

The end-to-end acceptance tests audit real arXiv corpora that are not vendored. Fetch them first:

```text
python scripts/fetch_acceptance_inputs.py --list
python scripts/fetch_acceptance_inputs.py tabm
```

The script downloads the pinned arXiv e-print, verifies the tarball digest, extracts it refusing
absolute, `..` and symlink members, and verifies the main-file digest. It refuses to overwrite an
existing corpus whose bytes differ. If you already keep that corpus somewhere else, point the
acceptance test at it with `PAPER_DOCTOR_TABM_CORPUS` instead of fetching. Paper Doctor itself never
touches the network, and nothing in `src/` knows where a corpus lives: the tool is given paths by a
manifest.

Run the suite from a **git checkout**, not from an unpacked sdist. The acceptance tests read the
`phase0/`-`phase3/` working directories - frozen manifests, expected-anchor tables, the ledger - and
those are project records, not part of a Python artifact. From an unpacked sdist the package tests all
pass and the acceptance files report `FileNotFoundError` for the workspace they audit; measured on
0.1.0: 205 passed, 23 failed, 70 errors, every failure naming a missing `phase*/` path. The same count
in a git checkout before the corpora are fetched is 210 passed, 18 failed, 70 errors. The suite does
not skip them, because a silently missing acceptance input is exactly what a release gate must not
allow. What an artifact *does* prove is that the tool works: install it and run
`paper-doctor audit examples/quickstart`, and from a checkout
`paper-doctor audit phase3/tabm` after the fetch.

## What it will not do

No aggregate score, no "the paper is unreliable", no re-running experiments, no guessing that two
names refer to the same model, no reading of meaning into a table. When the evidence on file cannot
decide a relation, the answer is `INCONCLUSIVE`.
