#!/usr/bin/env bash
# Cancel superseded GitHub Actions runs: when a branch gets pushed to multiple
# times (or master gets several merges back-to-back) without
# `concurrency: cancel-in-progress` configured, every push queues a full new
# run instead of cancelling the one still queued from the previous push. This
# keeps only the newest queued/in_progress run per (branch, workflow) pair and
# cancels the rest, freeing up concurrency slots.
#
# Usage:
#   scripts/github/cancel-stale-runs.sh [repo] [--dry-run]

set -euo pipefail

REPO="${1:-}"
DRY_RUN=false
for arg in "$@"; do
    [ "$arg" = "--dry-run" ] && DRY_RUN=true
done
if [ -z "$REPO" ] || [ "$REPO" = "--dry-run" ]; then
    REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi

gh run list --repo "$REPO" --limit 150 \
    --json databaseId,status,headBranch,workflowName,createdAt \
    | python3 -c "
import json, sys
from collections import defaultdict

data = json.load(sys.stdin)
not_done = [d for d in data if d['status'] in ('queued', 'in_progress')]

by_branch_wf = defaultdict(list)
for d in not_done:
    by_branch_wf[(d['headBranch'], d['workflowName'])].append(d)

to_cancel = []
for runs in by_branch_wf.values():
    if len(runs) > 1:
        runs_sorted = sorted(runs, key=lambda r: r['createdAt'], reverse=True)
        to_cancel.extend(r['databaseId'] for r in runs_sorted[1:])

print(f'{len(not_done)} active runs, {len(to_cancel)} superseded', file=sys.stderr)
for rid in to_cancel:
    print(rid)
" > /tmp/stale_runs_to_cancel.$$

count=$(wc -l < /tmp/stale_runs_to_cancel.$$)
if [ "$count" -eq 0 ]; then
    echo "No stale runs to cancel."
    rm -f /tmp/stale_runs_to_cancel.$$
    exit 0
fi

if [[ "$DRY_RUN" = true ]]; then
    echo "Would cancel $count run(s):"
    cat /tmp/stale_runs_to_cancel.$$
else
    while read -r rid; do
        gh run cancel "$rid" --repo "$REPO" 2>&1 || true
    done < /tmp/stale_runs_to_cancel.$$
fi

rm -f /tmp/stale_runs_to_cancel.$$
