---
name: sonarcloud-dashboard
description: "Use this skill whenever the user asks about SonarCloud, code quality, the quality gate, bugs, vulnerabilities, code smells, security hotspots, test coverage, or duplication for this project. Triggers include 'sonarcloud', 'sonar dashboard', 'code quality', 'quality gate', 'check sonar'. Pulls live data from the SonarCloud public API instead of guessing — this project's analysis is public, so no auth token is required."
---

# SonarCloud Dashboard

## Project identity

Found in `.github/workflows/sonarcloud.yml`:
- Project key: `kejhy93_ProteinFolding`
- Organization: `kejhy93`

If the workflow file's `-Dsonar.projectKey` / `-Dsonar.organization` values ever change, re-read that file — don't assume these are still current.

## Access

The project analysis is public, so the SonarCloud REST API (`https://sonarcloud.io/api/...`) can be queried directly with `curl`, no `SONAR_TOKEN` needed. If a query ever returns 401/403, the project may have gone private — ask the user for a token in that case rather than guessing.

## Common queries

**Overall metrics** (bugs, vulnerabilities, code smells, coverage, duplication, ratings):
```bash
curl -s "https://sonarcloud.io/api/measures/component?component=kejhy93_ProteinFolding&metricKeys=alert_status,bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc,security_hotspots,sqale_rating,reliability_rating,security_rating"
```

**Quality gate status**:
```bash
curl -s "https://sonarcloud.io/api/qualitygates/project_status?projectKey=kejhy93_ProteinFolding"
```
Note: `"status":"NONE"` means no quality gate is attached/evaluated for this project, not that it's passing.

**Recent analyses** (dates, commit revisions — cross-check `revision` against `git log` to tie a scan to a commit):
```bash
curl -s "https://sonarcloud.io/api/project_analyses/search?project=kejhy93_ProteinFolding&ps=10"
```

**Issue list** (bugs/vulnerabilities/code smells with file + line), filter by `types` (`BUG`, `VULNERABILITY`, `CODE_SMELL`) and/or `severities` (`BLOCKER`, `CRITICAL`, `MAJOR`, `MINOR`, `INFO`):
```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=kejhy93_ProteinFolding&types=VULNERABILITY&resolved=false&ps=50"
```

**Security hotspots** (separate endpoint from `issues/search`):
```bash
curl -s "https://sonarcloud.io/api/hotspots/search?projectKey=kejhy93_ProteinFolding"
```

## Notes

- Ratings are `1.0`–`5.0` mapping to `A`–`E` (1=A, 2=B, 3=C, 4=D, 5=E) for `sqale_rating` (maintainability), `reliability_rating`, `security_rating`.
- Responses are JSON; pipe through `python3 -m json.tool` or `jq` if pretty-printing helps, but raw JSON is usually fine to parse directly.
- When summarizing for the user, prefer a compact table of the key metrics over dumping raw JSON, and call out anything that looks off (e.g. vulnerability count high relative to LOC, hotspots at 0 despite vulnerabilities present) rather than just listing numbers.
