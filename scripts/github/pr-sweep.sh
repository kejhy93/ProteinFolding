#!/usr/bin/env bash
# Summarize every open PR's CI status, mergeability, and outstanding review
# comments in one pass. Requires the `gh` CLI to be authenticated.
#
# Usage:
#   scripts/github/pr-sweep.sh [repo]
#
# repo defaults to the current directory's git remote if omitted.

set -euo pipefail

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
    REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi

echo "== Open PRs on $REPO =="
gh pr list --repo "$REPO" --state open --limit 100 \
    --json number,headRefName,mergeable,mergeStateStatus \
    --jq '.[] | "\(.number)\t\(.headRefName)\t\(.mergeable)\t\(.mergeStateStatus)"' \
    | column -t -s $'\t'

echo
echo "== Conflicting PRs =="
gh pr list --repo "$REPO" --state open --limit 100 \
    --json number,headRefName,mergeable \
    --jq '[.[] | select(.mergeable=="CONFLICTING")] | if length==0 then "(none)" else .[] | "\(.number)\t\(.headRefName)" end'

echo
echo "== Failing / pending checks per PR =="
for pr in $(gh pr list --repo "$REPO" --state open --limit 100 --json number --jq '.[].number'); do
    checks=$(gh pr checks "$pr" --repo "$REPO" 2>&1 || true)
    fails=$(echo "$checks" | awk -F'\t' '$2=="fail"{print $1}')
    pending=$(echo "$checks" | awk -F'\t' '$2=="pending"{print $1}')
    if [ -n "$fails" ]; then
        echo "PR $pr FAILING: $(echo "$fails" | paste -sd, -)"
    elif [ -n "$pending" ]; then
        echo "PR $pr PENDING: $(echo "$pending" | paste -sd, -)"
    else
        echo "PR $pr: all green"
    fi
done

echo
echo "== Review comments not authored by the repo owner =="
OWNER=$(gh repo view "$REPO" --json owner --jq .owner.login)
for pr in $(gh pr list --repo "$REPO" --state open --limit 100 --json number --jq '.[].number'); do
    count=$(gh api "repos/$REPO/pulls/$pr/comments" --jq "[.[] | select(.user.login != \"$OWNER\")] | length")
    echo "PR $pr: $count"
done
