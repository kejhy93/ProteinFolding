# GitHub interaction scripts

Small `gh`-CLI wrappers for the recurring tasks involved in managing a batch
of open PRs (checks, conflicts, stale CI status, review comments). All
scripts default `repo` to the current directory's git remote if omitted.

- **pr-sweep.sh** — one-shot overview of every open PR: mergeability,
  conflicts, failing/pending checks, and outstanding review-comment counts.
- **pr-detail.sh `<PR>`** — deep dive on one PR: full check list, SonarCloud
  quality gate + open issues for that PR's diff, open code-scanning alerts on
  its branch, and review comments.
- **cancel-stale-runs.sh** — cancels superseded queued/in_progress runs (same
  branch + workflow, older than the newest). Useful when a repo's workflows
  don't set `concurrency: cancel-in-progress` and pushes/merges pile up a
  large backlog. Pass `--dry-run` to preview.
- **refresh-stale-check.sh `<PR>`** — re-runs the SonarCloud analysis
  workflow for a PR when its GitHub code-scanning "SonarCloud" check shows a
  stale failure for an issue that's already confirmed fixed (verify with
  pr-detail.sh first).

## Requirements

- `gh` CLI, authenticated (`gh auth status`)
- `python3` (used for JSON processing)

## Example

```sh
scripts/github/pr-sweep.sh
scripts/github/pr-detail.sh 76
scripts/github/cancel-stale-runs.sh --dry-run
```
