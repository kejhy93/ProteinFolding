---
name: github-pr-maintenance
description: "Use this skill whenever asked to check on, monitor, or fix open pull requests for this repo (kejhy93/ProteinFolding) — CI status, review comments, merge conflicts, or a batch of PRs at once. Triggers include 'check my PRs', 'are the PRs green', 'check for merge conflicts', 'reply to PR comments', 'why is this PR failing'. Wraps the scripts in scripts/github/ and documents recurring failure patterns specific to this repo's CI setup, discovered while managing ~90 sonar/* cleanup PRs in one session."
---

# GitHub PR Maintenance

## Scripts

Use these instead of hand-rolling `gh` one-liners — they already handle the
repo/owner defaults and edge cases:

- `scripts/github/pr-sweep.sh` — overview of every open PR: mergeability,
  conflicts, failing/pending checks, unresolved review-thread counts, and
  which PRs have new commits pushed since their last review. Run this first
  for any "check my PRs" style request, and also for "did anything get
  pushed since the last review" style requests — the last section does that
  comparison for every open PR in one pass.
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

**`BLOCKED` with all-green checks and no conflict usually means an
unresolved review thread, not a real problem.** This repo's branch protection
has `required_conversation_resolution` enabled (check with
`gh api repos/<owner>/<repo>/branches/master/protection`). A PR can show
`mergeable: MERGEABLE` / `mergeStateStatus: BLOCKED` purely because a
Sourcery/reviewer comment thread is unresolved — replying to the comment with
`gh pr comment` does **not** resolve the thread. Query and resolve it via
GraphQL:
```bash
gh api graphql -f query='
query { repository(owner:"OWNER", name:"REPO") { pullRequest(number: PR) {
  reviewThreads(first: 20) { nodes { id isResolved comments(first:1){nodes{body author{login}}} } }
}}}'

gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"THREAD_ID"}) { thread { isResolved } } }'
```
As the PR author you can resolve threads yourself once you've replied
explaining the scope boundary (or pushed the requested fix). Sourcery itself
auto-resolves a thread if a follow-up commit matches what it suggested — no
action needed in that case.

**A fix for one Sonar finding can expose a brand-new one on the same diff.**
SonarCloud's "new code" quality gate evaluates the whole diff, not just the
line the original issue was on. E.g. renaming a variable that was masking an
unused-parameter finding (because it was previously "used" as a reassignment
target) can turn a clean fix into a new `S1172` failure. Always check
`pr-detail.sh`'s SonarCloud section even on a PR you just opened and expect
to be clean — don't assume a freshly-created PR is safe from this. If a new
finding shows up and it's a direct, self-contained consequence of your own
diff (not a second, independent SonarCloud issue from the backlog), fixing it
in a follow-up commit is in scope — it isn't "bundling," it's finishing the
original fix properly.

**Raw inline-comment counts overstate what's outstanding — use thread
resolution, not comment authorship.** A PR can have review comments from
Sourcery while having zero *unresolved* threads, because Sourcery
auto-resolves a thread once a follow-up commit matches its suggestion (see
the `BLOCKED` pattern above). `pr-sweep.sh`'s "Unresolved review threads"
section already does the right thing (GraphQL `isResolved`) — don't fall
back to counting `pulls/<pr>/comments` by non-owner author, that count
includes comments whose threads are long since resolved and will make clean
PRs look like they need attention.

**Detecting and reviewing new pushes since the last review.** For "did
anything get pushed since I last reviewed" style requests: `pr-sweep.sh`'s
"New commits since last review" section compares each PR's last commit
(`commit.committer.date` from `pulls/<pr>/commits`) against its last actual
review (`submitted_at` from `pulls/<pr>/reviews`) — deliberately *not*
`pulls/<pr>/comments` or issue-timeline comments, which include CI status
bots (`sonarqubecloud`, `github-actions`) that post *after* a real review and
would mask a genuinely unreviewed push. For any PR it flags:
1. List commits (`gh api repos/<repo>/pulls/<pr>/commits`) and find the ones
   with a date after the last review's `submitted_at` — that's the new diff,
   not the whole PR.
2. Review only that slice: `git diff <last_reviewed_sha>..<head_sha> -- <path>`.
3. Post findings with `gh pr review <pr> --comment --body "..."` —
   **not** `--approve`. If the authenticated `gh` user is also the PR author
   (true for this repo's own maintenance PRs), `--approve` fails outright
   with `Can not approve your own pull request`. `--comment` works
   regardless of authorship and is the right choice for self-authored PRs.

**Sibling `sonar/*` PRs opened in the same batch will conflict once one
merges, if they touch the same or adjacent lines.** Each PR in a batch is
branched off master independently (not off each other), so two PRs fixing
different issues on the same line show no conflict while both are open —
`pr-sweep.sh` reports them clean. As soon as one merges, the other flips to
`mergeable: CONFLICTING` / `mergeStateStatus: DIRTY` against the new master.
This repo's owner tends to auto-merge PRs within minutes of them going green,
so re-run `pr-sweep.sh` periodically during a session rather than once at the
start — the picture changes fast. Resolve the conflict per the "keep HEAD as
superset" pattern above.
