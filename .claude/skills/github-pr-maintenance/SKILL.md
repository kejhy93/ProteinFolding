---
name: github-pr-maintenance
description: "Use this skill whenever asked to check on, monitor, or fix open pull requests for this repo (kejhy93/ProteinFolding) — CI status, review comments, merge conflicts, or a batch of PRs at once. Triggers include 'check my PRs', 'are the PRs green', 'check for merge conflicts', 'reply to PR comments', 'why is this PR failing'. Wraps the scripts in scripts/github/ and documents recurring failure patterns specific to this repo's CI setup, discovered while managing ~90 sonar/* cleanup PRs in one session."
---

# GitHub PR Maintenance

## Scripts

Use these instead of hand-rolling `gh` one-liners — they already handle the
repo/owner defaults and edge cases:

- `scripts/github/pr-sweep.sh` — overview of every open PR: mergeability,
  conflicts, failing/pending checks, outstanding review-comment counts. Run
  this first for any "check my PRs" style request.
- `scripts/github/pr-detail.sh <PR>` — deep dive on one PR: full check list,
  SonarCloud quality gate + open issues for that PR's diff, open
  code-scanning alerts on its branch, review comments. Run this when a PR is
  failing and you need to know why.
- `scripts/github/cancel-stale-runs.sh [--dry-run]` — cancels superseded
  queued/in_progress runs (same branch+workflow, older than the newest).
  This repo's workflows do **not** set `concurrency: cancel-in-progress`, so
  every push/merge queues a full new run without cancelling the one still
  queued from the previous push — run this whenever the Actions queue looks
  backed up (dozens of queued runs is normal after touching many PRs/merges
  in a short window, not a sign of anything broken).
- `scripts/github/refresh-stale-check.sh <PR>` — re-runs the "SonarCloud
  analysis" workflow to clear a stale check (see below). Verify the finding
  is actually fixed first with `pr-detail.sh` — this script just re-runs,
  it doesn't check anything.

All four take an optional `repo` argument; they default to the current
directory's `gh repo view` remote (`kejhy93/ProteinFolding`).

## Known recurring patterns (from managing ~90 sonar/* PRs)

**Stale "SonarCloud" check.** There's a separate `SonarCloud` check (created
by the `github-advanced-security` app from a SARIF upload) distinct from
`SonarCloud Code Analysis` / `SonarCloud analysis`. It occasionally reports
failure for a finding that's already fixed and confirmed resolved — verify
with `pr-detail.sh <PR>` (0 open SonarCloud issues *and* 0 open code-scanning
alerts for that PR's branch means it's stale), then run
`refresh-stale-check.sh <PR>`. Don't spend time debugging the underlying
finding again if both live sources already show clean.

**Merge-conflict resolution dropping NOSONAR/fix state.** When resolving a
conflict on one of the complexity-refactor branches by merging `origin/master`
in, the correct resolution is almost always "keep HEAD, it's a superset" —
master usually only has a smaller inline fix (e.g. a NOSONAR comment) for
code this branch already restructured into an extracted method. After
resolving, **grep the file for the specific suppression/fix master had**
(e.g. `# NOSONAR`) and confirm HEAD's version still has it on the equivalent
line in the extracted method — it's easy to accidentally drop it, which
reintroduces the exact SonarCloud finding the PR was created to fix. This has
happened repeatedly on file:branch pairs where multiple sonar/* PRs touch the
same function.

**Slow build matrix jobs.** `build (3.13)` and `build (3.14)` in the "Python
package" workflow routinely take 15–20 minutes (installing/building
numpy/scipy/torch for newer Python versions), while `build (3.10)`–`(3.12)`
finish in under 2 minutes. A PR sitting with only those two jobs pending for
10+ minutes is normal, not stuck — confirm with
`gh run view --job <id>` that it's progressed past "Install dependencies"
before assuming something's wrong.

**Reviewer feedback that's out of scope.** Sourcery frequently suggests
things that don't apply to a narrowly-scoped cleanup PR: renaming a
project-wide misspelling (e.g. `sequance`/`pheronome`) that appears in dozens
of files, adding backward-compat shims for internal (non-public-API)
parameter renames, or fixing an unrelated pre-existing bug spotted in a
complexity-refactor PR. The right response is usually a reply explaining the
scope boundary, not a code change — unless the fix is genuinely self-contained
to the one file already being touched (e.g. a misspelled identifier used
nowhere else), in which case just fix it.
