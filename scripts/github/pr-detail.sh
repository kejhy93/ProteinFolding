#!/usr/bin/env bash
# Deep-dive on a single PR: all check statuses, SonarCloud quality gate +
# open issues for that PR's diff, open GitHub code-scanning alerts on its
# branch, and review comments not authored by the repo owner.
#
# Usage:
#   scripts/github/pr-detail.sh <PR> [repo] [sonar-project-key]

set -euo pipefail

PR="${1:?usage: pr-detail.sh <PR> [repo] [sonar-project-key]}"
REPO="${2:-}"
SONAR_PROJECT_KEY="${3:-}"

if [[ -z "$REPO" ]]; then
    REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi
if [ -z "$SONAR_PROJECT_KEY" ]; then
    # Best-effort guess from the SonarCloud workflow file, if present.
    SONAR_PROJECT_KEY=$(grep -h "sonar.projectKey" .github/workflows/*.yml 2>/dev/null \
        | head -1 | sed -E 's/.*projectKey=([^ ]+).*/\1/')
fi

BRANCH=$(gh pr view "$PR" --repo "$REPO" --json headRefName --jq .headRefName)
OWNER=$(gh repo view "$REPO" --json owner --jq .owner.login)

echo "== PR #$PR ($BRANCH) checks =="
gh pr checks "$PR" --repo "$REPO" 2>&1 || true

if [ -n "$SONAR_PROJECT_KEY" ]; then
    echo
    echo "== SonarCloud quality gate ($SONAR_PROJECT_KEY, PR $PR) =="
    curl -s "https://sonarcloud.io/api/qualitygates/project_status?projectKey=${SONAR_PROJECT_KEY}&pullRequest=${PR}" \
        | python3 -c "
import json, sys
d = json.load(sys.stdin)['projectStatus']
print('status:', d['status'])
for c in d['conditions']:
    if c['status'] == 'ERROR':
        print(' ERROR:', c['metricKey'], 'actual=', c['actualValue'])
"

    echo
    echo "== SonarCloud open issues on this PR's diff =="
    curl -s "https://sonarcloud.io/api/issues/search?componentKeys=${SONAR_PROJECT_KEY}&pullRequest=${PR}&resolved=false" \
        | python3 -c "
import json, sys
d = json.load(sys.stdin)
issues = d['issues']
if not issues:
    print('(none)')
for i in issues:
    print(i['type'], i['severity'], i['rule'], i['component'].split(':', 1)[-1], i.get('line'), '-', i['message'])
"
fi

echo
echo "== Open GitHub code-scanning alerts on $BRANCH =="
gh api "repos/$REPO/code-scanning/alerts?state=open&ref=refs/heads/$BRANCH" \
    --jq 'if length==0 then "(none)" else .[] | "\(.rule.id) \(.most_recent_instance.location.path):\(.most_recent_instance.location.start_line)" end'

echo
echo "== Review comments not from $OWNER =="
gh api "repos/$REPO/pulls/$PR/comments" \
    --jq "[.[] | select(.user.login != \"$OWNER\")] | if length==0 then \"(none)\" else .[] | \"[\(.id)] \(.path):\(.line) - \(.body[0:120])\" end"
