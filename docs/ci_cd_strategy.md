# CI/CD Strategy (GitHub + Azure DevOps)

## Overview
- Build once in GitHub, promote the same artifact across Dev → QA → Prod in Azure DevOps.
- Short-lived feature branches; protected main; CODEOWNERS enforced reviews.

## Security
- GitHub OIDC to Azure for short-lived tokens.
- Secrets in Azure Key Vault; no creds in repo.
- Separate service principals: spn-fabric-dev|qa|prod.

## Quality Gates
- Lint (ruff/black/sqlfluff), unit tests (pytest), DQ gate (YAML rules) before QA/Prod.
- Schema + data diff checks as part of release.

## Rollback
- Re-deploy previous artifact from release history.
- Use Delta time-travel for data verification.
- Power BI rebind to previous dataset/model if needed.
