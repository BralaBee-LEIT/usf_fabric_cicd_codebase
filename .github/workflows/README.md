# CI/CD Pipeline Configuration

This directory contains GitHub Actions workflows for automated testing and deployment of the Microsoft Fabric CI/CD framework.

## 📋 Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main`, `develop`, or `feature/**` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

#### Lint and Code Quality
- Runs Black (code formatting check)
- Runs Flake8 (linting)
- Runs Pylint (static analysis)

#### Unit Tests
- Tests on Python 3.10, 3.11, 3.12
- Parallel test execution with pytest-xdist
- Code coverage reporting
- Upload to Codecov

#### Integration Tests
- Tests feature interactions
- Validates production hardening features
- Coverage reporting

#### E2E Tests
- Complete deployment scenarios
- Excludes real Fabric tests (manual only)

#### Security Scan
- Dependency vulnerability checking (Safety)
- Security linting (Bandit)
- Report generation

#### Documentation
- Validates documentation files exist
- Checks for broken links

#### Coverage Report
- Generates comprehensive coverage report
- Comments coverage on PRs
- Uploads HTML coverage report

### 2. Deployment Workflow (`deploy.yml`)

**Triggers:**
- Manual workflow dispatch only

**Inputs:**
- `environment`: Target environment (development/staging/production)
- `enable_features`: Enable production hardening features (boolean)

**Steps:**
1. Run pre-deployment tests
2. Configure Azure credentials
3. Set environment variables
4. Deploy application
5. Run smoke tests
6. Health check validation

## 🔧 Setup Instructions

### 1. Repository Secrets

Add these secrets to your GitHub repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets:**

```bash
# Azure Service Principal for Fabric API
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
AZURE_TENANT_ID=<your-tenant-id>
FABRIC_CAPACITY_ID=<your-capacity-id>

# Azure Credentials for deployment (JSON format)
AZURE_CREDENTIALS={
  "clientId": "<your-client-id>",
  "clientSecret": "<your-client-secret>",
  "subscriptionId": "<your-subscription-id>",
  "tenantId": "<your-tenant-id>"
}

# Optional: Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>

# Optional: Azure Key Vault
AZURE_KEY_VAULT_NAME=<your-keyvault-name>
```

### 2. GitHub Environments

Create environments for deployment workflow:

```
Settings → Environments → New environment
```

**Create these environments:**
- `development`
- `staging`
- `production`

**For each environment, configure:**
1. **Environment secrets** (environment-specific values)
2. **Protection rules** (for production):
   - Required reviewers: 2+
   - Deployment branches: `main` only
3. **Environment variables**

### 3. Codecov Integration (Optional)

1. Sign up at https://codecov.io
2. Add repository
3. Copy token
4. Add `CODECOV_TOKEN` to repository secrets

### 4. Branch Protection Rules

Configure branch protection for `main`:

```
Settings → Branches → Add rule
```

**Branch name pattern:** `main`

**Protections:**
- ✅ Require a pull request before merging
  - Required approvals: 2
  - Dismiss stale reviews
- ✅ Require status checks to pass
  - Required checks:
    - `Lint and Code Quality`
    - `Unit Tests (3.11)`
    - `Integration Tests`
    - `E2E Tests`
- ✅ Require conversation resolution
- ✅ Include administrators

## 🚀 Usage

### Running CI/CD Pipeline

The pipeline runs automatically on:
- Every push to tracked branches
- Every pull request

**Manual trigger:**
```
Actions → CI/CD Pipeline → Run workflow
```

### Deploying to Environments

**Via GitHub UI:**
```
Actions → Deploy to Environment → Run workflow
Select environment: staging
Enable features: ✅
Run workflow
```

**Via GitHub CLI:**
```bash
gh workflow run deploy.yml \
  -f environment=staging \
  -f enable_features=true
```

### Viewing Test Results

1. Go to **Actions** tab
2. Click on workflow run
3. View job details and logs
4. Download artifacts (coverage reports, security scans)

### Checking Coverage

1. View coverage comment on PR
2. Download coverage report artifact
3. Check Codecov dashboard (if configured)

## 📊 CI/CD Metrics

### Build Times (Approximate)

| Job | Duration |
|-----|----------|
| Lint | ~2 minutes |
| Unit Tests (per Python version) | ~3 minutes |
| Integration Tests | ~4 minutes |
| E2E Tests | ~5 minutes |
| Security Scan | ~2 minutes |
| **Total** | **~15-20 minutes** |

### Test Coverage Targets

- **Unit Tests**: >90%
- **Integration Tests**: >80%
- **Overall**: >85%

## 🔍 Troubleshooting

### Test Failures

**Unit Tests Fail:**
```bash
# Run locally to debug
pytest tests/unit/ -v --tb=short
```

**Integration Tests Fail:**
```bash
# Check feature flags
export FEATURE_USE_RETRY_LOGIC=true
pytest tests/integration/ -v
```

### Deployment Failures

**Pre-deployment tests fail:**
- Check if all dependencies installed
- Verify environment variables set
- Review test logs

**Azure authentication fails:**
- Verify `AZURE_CREDENTIALS` secret format
- Check service principal permissions
- Ensure subscription is active

### Coverage Drop

**Coverage decreased:**
1. Run coverage locally: `pytest --cov=ops/scripts/utilities --cov-report=html`
2. Open `htmlcov/index.html`
3. Identify uncovered lines
4. Add tests for missing coverage

## 🔒 Security Best Practices

### Secrets Management

✅ **DO:**
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly (every 90 days)
- Use environment-specific secrets
- Enable secret scanning

❌ **DON'T:**
- Commit secrets to code
- Log secret values
- Share secrets across environments
- Use production secrets in dev/staging

### Workflow Security

- Pin action versions (e.g., `@v4` not `@latest`)
- Review third-party actions
- Limit workflow permissions
- Use environment protection rules

## 📚 Additional Resources

### GitHub Actions Documentation
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

### Azure Integration
- [Azure Login Action](https://github.com/Azure/login)
- [Service Principal Setup](https://docs.microsoft.com/en-us/azure/developer/github/connect-from-azure)

### Testing
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Codecov](https://docs.codecov.io/)

## 🆘 Getting Help

**Issues with CI/CD:**
1. Check workflow logs in Actions tab
2. Review this README
3. Check [GitHub Actions status](https://www.githubstatus.com/)
4. Create issue with `[CI/CD]` tag

**Questions:**
- Check workflow file comments
- Review GitHub Actions docs
- Ask in team chat

---

**Maintained by:** DevOps Team  
**Last Updated:** October 24, 2025  
**Version:** 1.0.0
