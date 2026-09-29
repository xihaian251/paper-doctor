# `release/onboarding/` — first-use measurement evidence

Two first-use runs of Paper Doctor against the TabM acceptance workspace, measured for Phase 3 §14.
Summary, defect ranking, fixes and declined items: `phase3/ONBOARDING_MEASUREMENT.md`.

| file | run | role | sha256 of the log as archived here |
| --- | --- | --- | --- |
| `RUN1_AGENT_LOG.md` | 1, 15:06 | reader of the **pre-fix** documentation: hit the traceback, the uninformative missing-root message and the README's contradictory worked example | `4c78daef820eb180b70f55a54d30b31fc13b2330f599c735fcc31dcf18ec1a02` at copy time, before the redaction below |
| `RUN2_AGENT_LOG.md` | 2, 15:39 | reader of the **post-fix** documentation: 65 s to the first audit, byte-identical JSON export, one substantive guess left | `1830ae9e60e8184cc8c2c68cc163dda1c275683a6087ed01d05b8ab198cbf975` at copy time, before the redaction below |

## Provenance and the one edit made to these files

Each log was written by the run itself, inside a stripped copy of the repository, and copied here
verbatim with a single mechanical change: every occurrence of the scratch clone root was replaced by
`<scratch>`. Seven such paths in each file. No number, quote, verdict, command or timing was altered,
reordered or removed; the commands still show their real arguments apart from that root.

The runs are agent runs, not the human observation §15 asks for, and they are labelled as agent runs
throughout. `ONBOARDING_MEASUREMENT.md` states why §15's human test is not satisfied by them.

## Reproducing a run

1. Copy the repository to a fresh directory, then delete everything that is not user-facing:
   `phase0/`, `phase1/`, `phase2/`, every phase report, brief, preflight, erratum and handoff document
   (including `phase3/TABM_PREFLIGHT.md`), `phase3/tools/`, `phase3/probe-invented-claim/`,
   `phase3/acceptance-inputs/`, and all cache and build directories. What must remain is `README.md`,
   `pyproject.toml`, `src/`, `tests/`, `scripts/`, `examples/` and `phase3/tabm/`.
2. Hand the directory to a reader with no prior context and this instruction, and nothing else: audit
   `phase3/tabm` and tell me what you had to do that the documentation did not tell you.
3. Do not answer questions. Record commands, times, error text verbatim, and every guess.
4. The reader's own exported JSON must hash to
   `08836ccfe17f3e2dc0750b30a2a3ae5e5022a53787cf93c2f085af932dff9aa0` to match the frozen acceptance.
