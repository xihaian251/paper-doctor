# Recording sheet

Write only what you observed. Where you did not measure something, write `UNKNOWN` rather than an
estimate - `UNKNOWN` is a real answer here and an estimate is not usable. Timestamps help: note the
clock whenever something succeeds or fails.

## 0. Your environment

| Field | Your answer |
| --- | --- |
| Operating system and version | |
| Shell you typed in | |
| Python version(s) on PATH | |
| Did you use a virtual environment? how did you decide | |
| Network access during the session | |
| Time you started | |
| Time you finished, or `still running` | |

## 1. The files you opened

List every file you opened, in order, and why. The kit contains `README.md`, `phase3/tabm/`,
`scripts/`, `dist/`, and this sheet.

| # | File | Why you opened it |
| --- | --- | --- |
| | | |

## 2. Every command you typed

In order, with the wall-clock time and the exit code where you noticed one.

| # | Time | Command | Exit | What it printed (short) |
| --- | --- | --- | --- | --- |
| | | | | |

- Commands until the first successful audit of `phase3/tabm`:
- Wall-clock time from starting the install to that first successful audit:
- Wall-clock time from session start to an exported JSON report:

## 3. Errors, quoted exactly

Paste every error message you got, character for character, including the command that produced it.

| # | Command | Exit code | Message, verbatim | Did it tell you what to do? |
| --- | --- | --- | --- | --- |
| | | | | |

## 4. Steps the documentation did not cover

For each: what you did, how you decided to do it (a guess, an inference from a filename, something the
README said elsewhere), and how confident you were at the time.

| # | Step you had to work out | How you found it | Confidence |
| --- | --- | --- | --- |
| | | | |

## 5. Manual declarations or preparations

Anything you changed, created, moved, downloaded or configured before the audit could run, including
environment variables and directories.

| # | Preparation | Was it documented? |
| --- | --- | --- |
| | | |

## 6. The result, in your own words

- The tally the tool printed, and the exit code of the audit:
- Which finding confused you most, and what you did about it:
- In your own words, what each of these means, as you now understand it:
  `PASS` / `FAIL` / `INCONCLUSIVE` / `NOT_APPLICABLE` / `NOT_RUN`
- Did you change your mind about any status while working? What changed your mind?

## 7. What you could not tell from the output

Specific questions you would have wanted to answer from the tool's own output and could not.

| # | Question you could not answer | Where you went instead |
| --- | --- | --- |
| | | |

## 8. Trust

- Do you trust the numbers the tool printed? Yes / No / Partly, and why:
- What would have raised your trust, concretely:
- What would have destroyed it:

## 9. Verdict

Circle one, and add the sentence that justifies it:

- **COMPLETED WITHOUT GUESSING** - every step was documented before I needed it
- **COMPLETED AFTER GUESSING** - I finished, but I had to work out something the docs did not say
- **DID NOT COMPLETE** - I stopped, and this is where:

The three costliest friction points, in seconds or minutes of your time:

1.
2.
3.

Anything you would tell the authors that is not covered above:
