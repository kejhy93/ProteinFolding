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
    if [[ -n "$fails" ]]; then
        echo "PR $pr FAILING: $(echo "$fails" | paste -sd, -)"
    elif [[ -n "$pending" ]]; then
        echo "PR $pr PENDING: $(echo "$pending" | paste -sd, -)"
    else
        echo "PR $pr: all green"
    fi
done

echo
echo "== Unresolved review threads =="
# Raw inline-comment counts are misleading: Sourcery (and other bots) often
# auto-resolve a thread once a follow-up commit matches their suggestion,
# leaving the comment itself in place but no longer actionable. Query
# isResolved via GraphQL instead of counting comments by non-owner authors.
OWNER=$(gh repo view "$REPO" --json owner --jq .owner.login)
REPO_OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"
for pr in $(gh pr list --repo "$REPO" --state open --limit 100 --json number --jq '.[].number'); do
    count=$(gh api graphql -f query='
    query { repository(owner:"'"$REPO_OWNER"'", name:"'"$REPO_NAME"'") { pullRequest(number: '"$pr"') {
      reviewThreads(first: 50) { nodes { isResolved } }
    }}}' --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length')
    echo "PR $pr: $count"
done

echo
echo "== New commits since last review =="
# Compares the last commit's committer date against the last *review*
# submission date (gh api .../reviews) — not issue/PR-level comments, which
# include CI status bots (sonarqubecloud, github-actions) that post after
# real reviews and would mask a genuinely unreviewed push.
for pr in $(gh pr list --repo "$REPO" --state open --limit 100 --json number --jq '.[].number'); do
    last_commit=$(gh api "repos/$REPO/pulls/$pr/commits" --jq '[.[].commit.committer.date] | sort | last // "1970-01-01T00:00:00Z"')
    last_review=$(gh api "repos/$REPO/pulls/$pr/reviews" --jq '[.[].submitted_at] | sort | last // "1970-01-01T00:00:00Z"')
    if [[ "$last_commit" > "$last_review" ]]; then
        echo "PR $pr: NEW PUSH since last review (commit $last_commit > review $last_review)"
    fi
done
