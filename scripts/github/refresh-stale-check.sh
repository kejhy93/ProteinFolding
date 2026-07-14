#!/usr/bin/env bash
# Re-run the "SonarCloud analysis" workflow for a PR's latest commit.
#
# Occasionally the separate github-advanced-security "SonarCloud" check (not
# the "SonarCloud Code Analysis"/"SonarCloud analysis" checks) reports a
# failure for a finding that has already been fixed and confirmed resolved
# (0 open SonarCloud issues, 0 open code-scanning alerts for that commit) -
# it just hasn't refreshed. Re-running the workflow run that produced it
# regenerates the check with current results.
#
# This script only re-runs the workflow; it does NOT verify the finding is
# actually already fixed first - do that manually (see pr-detail.sh) before
# using this, otherwise you'll just get the same failure again.
#
# Usage:
#   scripts/github/refresh-stale-check.sh <PR> [repo] [workflow-name]

set -euo pipefail

PR="${1:?usage: refresh-stale-check.sh <PR> [repo] [workflow-name]}"
REPO="${2:-}"
WORKFLOW_NAME="${3:-SonarCloud analysis}"

if [[ -z "$REPO" ]]; then
    REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi

BRANCH=$(gh pr view "$PR" --repo "$REPO" --json headRefName --jq .headRefName)

RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 20 \
    --json databaseId,workflowName,createdAt \
    --jq "[.[] | select(.workflowName == \"$WORKFLOW_NAME\")] | sort_by(.createdAt) | last | .databaseId")

if [[ -z "$RUN_ID" ]] || [[ "$RUN_ID" = "null" ]]; then
    echo "No '$WORKFLOW_NAME' run found for $BRANCH" >&2
    exit 1
fi

echo "Re-running $WORKFLOW_NAME run $RUN_ID for PR #$PR ($BRANCH)"
gh run rerun "$RUN_ID" --repo "$REPO"
