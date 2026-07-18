---
name: github-pr-review
description: "Use this skill whenever asked to code-review open pull requests for this repo (kejhy93/ProteinFolding) — as opposed to fixing/cleaning them (see github-pr-maintenance for that). Triggers include 'review my PRs', 'code review each PR', 'take a look at the open PRs and review them', 'post review comments', or a recurring goal like 'review PRs and repeat every N minutes unless no new pushes'. Produces independent, verified review comments (not a paraphrase of bot comments) posted via `gh pr review`, and gives the correct pattern for a recurring review loop with a real stopping condition — discovered while reviewing a batch of test-coverage PRs and turning that into a genuinely recurring goal."
---

# GitHub PR Review

Distinct from `github-pr-maintenance`: that skill drives PRs to green/clean
(fixing CI, resolving threads, resolving conflicts). This skill produces the
*review itself* — reading the diff and posting substantive comments, whether
as a one-off or as a recurring loop.

## Getting the right diff to review

**Never trust the local working tree's branch.** In a long-running or
goal-loop session, the local checkout can silently be on a different PR's
branch than the one you're reviewing (e.g. a prior loop iteration checked out
another branch and left it there). Reading `data/foo.py` from disk without
checking `git branch --show-current` first can review the wrong version of
the file entirely.

Get the true PR content two ways and don't rely on just one:
```bash
gh pr diff <PR>                                    # the diff itself
git fetch origin <branch> && git show origin/<branch>:<path>   # full file at PR HEAD
```
If `git branch --show-current` doesn't match the PR's `headRefName`, treat
anything read from the working tree as suspect until fetched/shown instead.

## Doing an actual review, not a paraphrase

A bot (Sourcery, etc.) will already have left generic "consider adding a test
for X" comments on most PRs. Repeating those isn't a code review — it adds no
signal the PR author doesn't already have. The valuable review is one where
you **verify claims by hand**, not just read them:

- For test PRs: pick the least-obvious assertions (complex arithmetic, sort
  order, accumulation over loops, off-by-one bounds) and hand-trace the real
  implementation against the exact test inputs to confirm the expected value
  is actually correct — don't assume a test is right because it exists and
  passes CI. This is how you catch a test that's accidentally validating
  wrong behavior.
- Check whether a bot's *suggested* test/fix is itself correct against the
  real code before treating it as valid feedback — bots confidently propose
  wrong things (e.g. asserting a specific return value where the real code
  actually raises an exception on that input). State plainly when a bot
  suggestion doesn't hold up, and why.
- Actively look for latent bugs in the code under test, not just coverage
  gaps — a test-coverage PR is often the first time anyone has traced these
  code paths carefully, and a wrong-argument or dead-condition bug hiding
  behind untested code is a much higher-value finding than "add one more
  case." Report these as informational/follow-up, explicitly scoped as
  pre-existing and not something this PR needs to fix (don't drop it as a
  demand into someone else's coverage-only PR).

## Posting the review

```bash
gh pr review <PR> --comment --body "$(cat <<'EOF'
## Code review

... findings, each with what you verified and why it holds ...
EOF
)"
```
Use `--comment` (not `--approve`/`--request-changes`) unless explicitly asked
to gate the PR — the goal here is substantive feedback, not merge control.
Structure the body so the reader can tell what you actually checked (specific
test names, hand-traced values) from what you're flagging as a heads-up.

See `github-pr-maintenance`'s scripts (`pr-sweep.sh`, `pr-detail.sh`) for
overview/detail on CI status and existing comment counts — useful context
before reviewing, but not a substitute for reading the diff yourself.

## Recurring review loops ("review PRs, repeat every N minutes")

This is the part that's easy to get structurally wrong. Two failure modes to
avoid:

**Don't use a one-shot wakeup and call it "recurring."** `ScheduleWakeup` is
for `/loop`'s self-paced dynamic mode; a bare Stop-hook goal asking for
"repeat this every N minutes" needs an actual repeating schedule, not a
single deferred call — `CronCreate` with `recurring: true` and a cron
expression (e.g. `"7,27,47 * * * *"` for ~20 min, offset off the round
minute marks). Check `CronList` first so you don't stack a second job on top
of one already running.

**Don't just schedule the loop and stop — demonstrate it executes.** A
condition like "repeat every 20 minutes unless no new pushes are created" has
two parts: the repetition mechanism, *and* the stopping logic actually
running at least once. Prove the stopping logic works immediately rather than
waiting for the first real cron fire:
1. `pr-sweep.sh` for the current PR list.
2. For each PR, compare its latest commit timestamp against your own last
   review timestamp on that PR:
   ```bash
   gh pr view <PR> --json reviews --jq '[.reviews[] | select(.author.login=="<you>")] | last | .submittedAt'
   gh pr view <PR> --json commits --jq '.commits | last | .authoredDate'
   ```
3. If the latest commit predates your last review → no new pushes → correctly
   take no action this cycle (this *is* satisfying the stop condition, not
   skipping the task).
4. If a commit postdates your last review → review the new diff and post a
   fresh comment.

Doing this once, synchronously, before relying on the cron job to repeat it
is what shows the loop's decision logic is real rather than aspirational.

**Cron job lifetime:** session-only, auto-expires after 7 days. If the goal
is expected to outlive that, say so — don't imply indefinite automation.
