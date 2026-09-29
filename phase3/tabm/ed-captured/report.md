# Experiment Doctor report - paper

- adapter: `captured`
- root: `F:\MLResearch\paper-doctor\phase3\.ed-workdir\tabm-ed\paper`
- runs discovered: 1
- families discovered: 1
- artifacts inventoried: 60175
- this tool is read-only and emits no verdict; every status below describes evidence, not validity

## Families

| family | kind | runs | declared reps | identity | seed status | membership |
| --- | --- | --- | --- | --- | --- | --- |
| `exp-cade5bdf7f3f4c4a9964dd0154598210` | unknown | 1 | None | UNKNOWN | CONSISTENT | 0+/0- |

- identity statuses: UNKNOWN=1
- seed statuses: CONSISTENT=1

## Runs

- total: 1
- by status: UNKNOWN=1
- run_id is a tool-assigned identifier; it is not the tracking-system id, not a seed and not a repetition index

## Aggregations

_No aggregation records were recovered._

## Rule Results

| rule | title | entity | PASS | FAIL | INCONCLUSIVE | N/A | NOT_RUN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ED001 | Run Identity Consistency | family | 0 | 0 | 0 | 1 | 0 |
| ED002 | Seed Provenance Integrity | family | 1 | 0 | 0 | 0 | 0 |
| ED003 | Historical Code Provenance | run | 1 | 0 | 0 | 0 | 0 |
| ED004 | Resolved Configuration Provenance | run | 0 | 0 | 1 | 0 | 0 |
| ED005 | Metric Selection Provenance | aggregation | 0 | 0 | 0 | 0 | 0 |
| ED006 | Aggregation Membership Provenance | aggregation | 0 | 0 | 0 | 0 | 0 |
| ED007 | Aggregation Numerical Consistency | aggregation | 0 | 0 | 0 | 0 | 0 |
| ED008 | Spread Semantics Consistency | aggregation | 0 | 0 | 0 | 0 | 0 |
| ED009 | Termination Provenance | run | 0 | 0 | 1 | 0 | 0 |
| ED010 | Runtime Environment Provenance | run | 0 | 0 | 1 | 0 | 0 |

_Each row is one rule counted over the entities it applies to.  There is no combined score across rules; read the statuses separately._

### Contradictions (FAIL)

_No rule found an artifact that contradicts a claim._

### Open questions (INCONCLUSIVE)

- **ED004** INCONCLUSIVE x1 - no effective configuration was recovered for this run (first: `exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json`)
    - a configuration file that exists in the repository says what could be run, not what was run
- **ED009** INCONCLUSIVE x1 - no artifact records why this run ended (first: `exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json`)
    - UNKNOWN here means no artifact states why the run ended; it does not mean the run failed, was stopped early or was abandoned
- **ED010** INCONCLUSIVE x1 - no artifact records the environment this run executed in (first: `exp-cade5bdf7f3f4c4a9964dd0154598210#experiment.run.json`)
    - a dependency file in the repository describes intended versions; it cannot show which versions a historical run actually loaded
    - UNKNOWN here means the run recorded nothing about its environment, not that the environment was wrong or unreproducible

### Supported and non-applicable results

- **ED001** NOT_APPLICABLE x1 - a family with fewer than two runs has no identity to compare
- **ED002** PASS x1 - every run's seed is recoverable from a run artifact and all 1 are distinct
- **ED003** PASS x1 - the run's own artifact records revision 28e47ae301c92ec37787dde1ce923a0793f405b4

## Findings

_Findings are the check-level observations the audit produced; the formal rule outcomes above are the authoritative statements about which claims the artifacts support._
- total: 20
- by category: METRIC_PROVENANCE=1, PROVENANCE_GAP=19
- by severity: HIGH=1, MEDIUM=19

- **HIGH / PROVENANCE_GAP** - 'termination_cause' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / METRIC_PROVENANCE** - no metric values recovered for this family (`exp-cade5bdf7f3f4c4a9964dd0154598210`)
    - runs: 1
    - metrics: none
- **MEDIUM / PROVENANCE_GAP** - 'command' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'compute_budget' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'dataset' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'dataset_version' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'end_time' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'entrypoint' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'exclusion_category' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'exclusion_evidence' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'exclusion_reason' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'history_rows' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'included_in_aggregation' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'method' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'repetition_index' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'resolved_config' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'runtime_seconds' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'start_time' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'task' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 
- **MEDIUM / PROVENANCE_GAP** - 'tracker_run_id' is UNKNOWN for every discovered run (`paper`)
    - 0 / 1 runs carry evidence for this field
    - 

## Provenance Coverage

Field-level evidence counts.  There is deliberately no composite trust score.

| field | runs | CONFIRMED | SUPPORTED | INFERRED | UNKNOWN | CONFLICTING |
| --- | --- | --- | --- | --- | --- | --- |
| code_commit | 1 | 1 | 0 | 0 | 0 | 0 |
| code_dirty | 1 | 1 | 0 | 0 | 0 | 0 |
| command | 1 | 0 | 0 | 0 | 1 | 0 |
| compute_budget | 1 | 0 | 0 | 0 | 1 | 0 |
| config_source | 1 | 1 | 0 | 0 | 0 | 0 |
| dataset | 1 | 0 | 0 | 0 | 1 | 0 |
| dataset_version | 1 | 0 | 0 | 0 | 1 | 0 |
| end_time | 1 | 0 | 0 | 0 | 1 | 0 |
| entrypoint | 1 | 0 | 0 | 0 | 1 | 0 |
| exclusion_category | 1 | 0 | 0 | 0 | 1 | 0 |
| exclusion_evidence | 1 | 0 | 0 | 0 | 1 | 0 |
| exclusion_reason | 1 | 0 | 0 | 0 | 1 | 0 |
| history_rows | 1 | 0 | 0 | 0 | 1 | 0 |
| included_in_aggregation | 1 | 0 | 0 | 0 | 1 | 0 |
| method | 1 | 0 | 0 | 0 | 1 | 0 |
| metric_direction | 0 | 0 | 0 | 0 | 0 | 0 |
| metric_value | 0 | 0 | 0 | 0 | 0 | 0 |
| repetition_index | 1 | 0 | 0 | 0 | 1 | 0 |
| resolved_config | 1 | 0 | 0 | 0 | 1 | 0 |
| runtime_seconds | 1 | 0 | 0 | 0 | 1 | 0 |
| seed | 1 | 1 | 0 | 0 | 0 | 0 |
| start_time | 1 | 0 | 0 | 0 | 1 | 0 |
| task | 1 | 0 | 0 | 0 | 1 | 0 |
| termination_cause | 1 | 0 | 0 | 0 | 1 | 0 |
| tracker_run_id | 1 | 0 | 0 | 0 | 1 | 0 |

## Discovery Notes

- scope: one bundle directory holds one lock and one run record, so this adapter discovers exactly one family of one run; it does not search the tree for further bundles
- the bundle carries no method, task or dataset name, so run identity (ED001) cannot be compared and stays UNKNOWN rather than being read off the directory
- metrics are absent by design: v1 Phase 2 captures stdout and stderr as logs and reads no value out of them
