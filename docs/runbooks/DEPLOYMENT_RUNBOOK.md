# Deployment Runbook

## 📋 Overview

This runbook provides step-by-step procedures for deploying the Microsoft Fabric CI/CD framework to different environments.

**Target Audience:** DevOps Engineers, Release Managers, System Administrators

**Prerequisites:**
- Azure subscription with Fabric capacity
- Azure service principal with appropriate permissions
- GitHub repository access
- Python 3.10+ installed locally (for validation)

---

## 🎯 Deployment Environments

### Environment Specifications

| Environment | Purpose | Fabric Capacity | Approval Required | Rollback Time |
|------------|---------|-----------------|-------------------|---------------|
| **Development** | Feature development & testing | F2 | No | Immediate |
| **Staging** | Pre-production validation | F4 | Yes (1 reviewer) | 5 minutes |
| **Production** | Live workloads | F64 | Yes (2 reviewers) | 15 minutes |

### Environment URLs

```bash
# Development
FABRIC_API_URL=https://api.fabric.microsoft.com/v1
CAPACITY_ID=<dev-capacity-id>

# Staging
FABRIC_API_URL=https://api.fabric.microsoft.com/v1
CAPACITY_ID=<staging-capacity-id>

# Production
FABRIC_API_URL=https://api.fabric.microsoft.com/v1
CAPACITY_ID=<prod-capacity-id>
```

---

## 🚀 Standard Deployment

### Phase 1: Pre-Deployment (15 minutes)

#### 1.1 Pre-Deployment Checklist

```bash
□ Code reviewed and approved
□ PR merged to target branch
□ All CI tests passing (105/105)
□ Security scan clean (no high/critical issues)
□ Release notes reviewed
□ Change ticket created
□ Deployment window scheduled
□ Stakeholders notified
□ Rollback plan reviewed
□ Backup verification complete
```

#### 1.2 Verify Prerequisites

**Check GitHub Actions Status:**
```bash
# Via GitHub CLI
gh run list --workflow=ci-cd.yml --limit 1 --json status,conclusion

# Expected output: status=completed, conclusion=success
```

**Verify Secrets Configuration:**
```bash
# List configured secrets (values hidden)
gh secret list

# Required secrets:
# - AZURE_CLIENT_ID
# - AZURE_CLIENT_SECRET
# - AZURE_TENANT_ID
# - FABRIC_CAPACITY_ID
# - AZURE_CREDENTIALS (for deployment)
```

**Test Azure Connectivity:**
```bash
# Local validation script
python ops/scripts/test_azure_connection.py \
  --client-id $AZURE_CLIENT_ID \
  --tenant-id $AZURE_TENANT_ID \
  --capacity-id $FABRIC_CAPACITY_ID

# Expected output: ✅ Connection successful
```

#### 1.3 Review Deployment Diff

```bash
# Compare staging vs production
git diff origin/staging origin/main

# Review changes
# - New features
# - Configuration changes
# - Database migrations (if any)
# - Breaking changes
```

#### 1.4 Communication

**Send Pre-Deployment Notification:**

```
Subject: [Deployment] Fabric CI/CD v1.0.0 - Scheduled Deployment

Environment: <Production/Staging>
Date: <YYYY-MM-DD>
Time: <HH:MM UTC>
Duration: ~30 minutes
Maintenance Window: <start> to <end>

Changes:
- Production hardening features
- Enhanced security controls
- Improved retry logic
- Comprehensive observability

Impact:
- No service interruption expected
- Performance improvement expected
- New features available after deployment

Rollback Plan:
- Automated rollback available
- RTO: 15 minutes
- RPO: None (no data loss)

Contact: devops-team@company.com
```

---

### Phase 2: Deployment Execution (20 minutes)

#### 2.1 Trigger Deployment

**Via GitHub UI:**
```
1. Navigate to: Actions → Deploy to Environment
2. Click: "Run workflow"
3. Select branch: main (for production) or develop (for staging)
4. Choose inputs:
   - environment: production
   - enable_features: true
5. Click: "Run workflow"
```

**Via GitHub CLI:**
```bash
# Production deployment
gh workflow run deploy.yml \
  --ref main \
  -f environment=production \
  -f enable_features=true

# Get workflow run ID
RUN_ID=$(gh run list --workflow=deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# Monitor progress
gh run watch $RUN_ID
```

#### 2.2 Monitor Deployment

**Watch Deployment Logs:**
```bash
# Real-time log streaming
gh run watch $RUN_ID --interval 10

# View specific job logs
gh run view $RUN_ID --log
```

**Key Checkpoints:**

| Step | Duration | Success Criteria |
|------|----------|------------------|
| Checkout code | 30s | Code downloaded successfully |
| Setup Python | 1m | Python 3.11 configured |
| Install dependencies | 2m | All packages installed |
| Run pre-deployment tests | 5m | All tests passing |
| Configure Azure | 1m | Authenticated successfully |
| Deploy application | 5m | Deployment completed |
| Run smoke tests | 3m | Critical paths validated |
| Health check | 2m | All endpoints healthy |

#### 2.3 Validate Deployment

**Automated Validation (via workflow):**
- ✅ Pre-deployment tests pass
- ✅ Smoke tests pass (dev/staging)
- ✅ Health check pass
- ✅ No errors in logs

**Manual Validation:**

```bash
# 1. Test Fabric API connectivity
python -c "
from ops.scripts.utilities.fabric_api import FabricAPIClient
client = FabricAPIClient()
workspaces = client.list_workspaces()
print(f'✅ Connected - {len(workspaces)} workspaces found')
"

# 2. Verify workspace creation
pytest tests/integration/test_workspace_management.py::test_create_workspace -v

# 3. Test lakehouse operations
pytest tests/integration/test_lakehouse_management.py::test_create_lakehouse -v

# 4. Verify Git integration
pytest tests/integration/test_fabric_git_connector.py::test_update_from_git -v

# 5. Test retry logic
pytest tests/integration/test_retry_logic.py -v

# Expected: All tests PASSED
```

---

### Phase 3: Post-Deployment (10 minutes)

#### 3.1 Smoke Testing

**Critical Path Testing:**

```bash
# Run smoke test suite
pytest tests/smoke/ -v -m critical

# Test scenarios:
# - Create workspace
# - Create lakehouse
# - Upload file to lakehouse
# - Execute notebook
# - Delete resources
```

**Feature Validation:**

```python
# Test production hardening features
import os
os.environ['FEATURE_USE_RETRY_LOGIC'] = 'true'
os.environ['FEATURE_ENABLE_CIRCUIT_BREAKER'] = 'true'
os.environ['FEATURE_COLLECT_METRICS'] = 'true'

pytest tests/integration/ -v -k "retry or circuit or metric"
```

#### 3.2 Performance Validation

```bash
# Run performance benchmarks
pytest tests/performance/test_benchmarks.py -v

# Expected results:
# - API calls: <500ms average
# - Workspace creation: <30s
# - Lakehouse creation: <45s
# - Retry overhead: <10%
```

#### 3.3 Monitoring Setup

**Verify Application Insights:**

```bash
# Check telemetry collection
az monitor app-insights metrics show \
  --app $APPINSIGHTS_APP_NAME \
  --metric requests/count \
  --interval PT1M

# Verify custom metrics
az monitor app-insights metrics show \
  --app $APPINSIGHTS_APP_NAME \
  --metric "Fabric API Calls" \
  --interval PT1M
```

**Configure Alerts:**

```bash
# Create deployment alert
az monitor metrics alert create \
  --name "fabric-api-high-latency" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg requests/duration > 1000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action $ACTION_GROUP_ID
```

#### 3.4 Documentation Update

```bash
# Update deployment log
cat >> deployments.log <<EOF
$(date -u +"%Y-%m-%d %H:%M:%S UTC") | Production | v1.0.0 | SUCCESS | $USER
Features: retry_logic, circuit_breaker, metrics, structured_logging
Duration: 28m
Issues: None
EOF

# Commit to repository
git add deployments.log
git commit -m "docs: Log production deployment v1.0.0"
git push
```

#### 3.5 Communication

**Send Post-Deployment Notification:**

```
Subject: [Deployment] Fabric CI/CD v1.0.0 - Deployment Complete ✅

Environment: Production
Deployed: <YYYY-MM-DD HH:MM UTC>
Duration: 28 minutes
Status: SUCCESS

Validation Results:
✅ Pre-deployment tests: PASSED (105/105)
✅ Deployment: SUCCESSFUL
✅ Smoke tests: PASSED (15/15)
✅ Health checks: HEALTHY
✅ Performance: Within SLA

New Features Available:
- Automatic retry with exponential backoff
- Circuit breaker for API stability
- Comprehensive metrics collection
- Structured logging with correlation IDs

Known Issues: None

Next Steps:
- Monitor Application Insights dashboard
- Review metrics after 24 hours
- Collect user feedback

Contact: devops-team@company.com
```

---

## 🔄 Rollback Procedures

### When to Rollback

**Trigger rollback if:**
- Critical functionality broken
- Security vulnerability introduced
- Performance degradation >20%
- Data corruption detected
- Multiple user-reported issues

**Do NOT rollback if:**
- Minor UI issues
- Non-critical bugs
- Performance degradation <10%
- Single user-reported issue

### Rollback Process

#### Option 1: Automated Rollback (Preferred)

**Using GitHub Actions:**

```bash
# List recent deployments
gh run list --workflow=deploy.yml --limit 5

# Get previous successful deployment
PREVIOUS_RUN=$(gh run list --workflow=deploy.yml --status success --limit 2 --json databaseId --jq '.[1].databaseId')

# Re-run previous deployment
gh run rerun $PREVIOUS_RUN

# Monitor rollback
gh run watch $PREVIOUS_RUN
```

#### Option 2: Git-based Rollback

```bash
# Identify last good commit
git log --oneline --decorate -10

# Create rollback branch
git checkout -b rollback/to-v0.9.0 <commit-hash>

# Deploy rollback branch
gh workflow run deploy.yml \
  --ref rollback/to-v0.9.0 \
  -f environment=production \
  -f enable_features=false

# Monitor rollback
RUN_ID=$(gh run list --workflow=deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch $RUN_ID
```

#### Option 3: Manual Rollback

```bash
# 1. Disable production hardening features
export FEATURE_USE_RETRY_LOGIC=false
export FEATURE_ENABLE_CIRCUIT_BREAKER=false
export FEATURE_COLLECT_METRICS=false
export FEATURE_USE_STRUCTURED_LOGGING=false

# 2. Update configuration in Azure
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings \
    FEATURE_USE_RETRY_LOGIC=false \
    FEATURE_ENABLE_CIRCUIT_BREAKER=false \
    FEATURE_COLLECT_METRICS=false \
    FEATURE_USE_STRUCTURED_LOGGING=false

# 3. Restart application
az webapp restart --name $APP_NAME --resource-group $RG_NAME

# 4. Verify rollback
pytest tests/smoke/ -v -m critical
```

### Post-Rollback Actions

```bash
# 1. Update status page
echo "Rolled back to v0.9.0 due to <reason>" | tee -a status.txt

# 2. Notify stakeholders
# Send email with rollback details

# 3. Create incident report
cat > incident_$(date +%Y%m%d).md <<EOF
# Incident Report: Rollback v1.0.0

**Date:** $(date -u +"%Y-%m-%d %H:%M UTC")
**Severity:** High
**Impact:** Production deployment rolled back

## Timeline
- HH:MM: Deployment started
- HH:MM: Issue detected
- HH:MM: Rollback initiated
- HH:MM: Rollback completed

## Root Cause
<Describe issue>

## Resolution
- Rolled back to v0.9.0
- Features disabled
- Service restored

## Action Items
- [ ] Fix root cause
- [ ] Add test coverage
- [ ] Update runbook
- [ ] Schedule re-deployment
EOF

# 4. Schedule retrospective
# Create meeting to discuss what went wrong
```

---

## 🛠️ Troubleshooting

### Deployment Failures

#### Issue: Pre-deployment Tests Fail

**Symptoms:**
```
Error: Pre-deployment tests failed
Process completed with exit code 1
```

**Resolution:**
```bash
# 1. Check which tests failed
gh run view $RUN_ID --log | grep FAILED

# 2. Run tests locally
pytest tests/unit/ tests/integration/ -v

# 3. Fix issues and re-run
git commit -am "fix: Resolve test failures"
git push

# 4. Re-trigger deployment
gh workflow run deploy.yml -f environment=production
```

#### Issue: Azure Authentication Fails

**Symptoms:**
```
Error: Azure authentication failed
DefaultAzureCredential failed to retrieve a token
```

**Resolution:**
```bash
# 1. Verify service principal
az ad sp show --id $AZURE_CLIENT_ID

# 2. Check secret expiration
az ad sp credential list --id $AZURE_CLIENT_ID

# 3. Test authentication
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# 4. Update GitHub secret if needed
gh secret set AZURE_CLIENT_SECRET
```

#### Issue: Smoke Tests Fail

**Symptoms:**
```
Error: Smoke tests failed
Critical paths validation error
```

**Resolution:**
```bash
# 1. Check Fabric API status
curl -H "Authorization: Bearer $TOKEN" \
  https://api.fabric.microsoft.com/v1/workspaces

# 2. Verify capacity
az fabric capacity show --name $CAPACITY_NAME

# 3. Check quota limits
az fabric capacity show --name $CAPACITY_NAME --query "properties.sku"

# 4. Re-run smoke tests
pytest tests/smoke/ -v -s
```

### Performance Issues

#### Issue: High Latency After Deployment

**Diagnosis:**
```bash
# Check Application Insights
az monitor app-insights metrics show \
  --app $APPINSIGHTS_APP_NAME \
  --metric requests/duration \
  --interval PT5M

# Review slow requests
az monitor app-insights query \
  --app $APPINSIGHTS_APP_NAME \
  --analytics-query "requests | where duration > 1000 | summarize count() by operation_Name"
```

**Resolution:**
```bash
# 1. Check feature flags
echo $FEATURE_USE_RETRY_LOGIC
echo $FEATURE_ENABLE_CIRCUIT_BREAKER

# 2. Review retry configuration
cat config/retry_config.json

# 3. Adjust retry settings if needed
# Edit retry_config.json to reduce max_attempts

# 4. Redeploy with adjusted settings
git commit -am "fix: Adjust retry configuration"
git push
```

---

## 📊 Deployment Metrics

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment Duration | <30 minutes | GitHub Actions duration |
| Test Pass Rate | 100% | pytest results |
| Deployment Success Rate | >95% | Success vs. total deployments |
| Rollback Time | <15 minutes | Time to restore service |
| Mean Time to Recover | <30 minutes | Average recovery time |

### Tracking Deployments

```bash
# View deployment history
gh run list --workflow=deploy.yml --limit 20 --json conclusion,createdAt,displayTitle

# Calculate success rate
SUCCESS=$(gh run list --workflow=deploy.yml --status success --limit 100 --json conclusion | jq length)
TOTAL=$(gh run list --workflow=deploy.yml --limit 100 --json conclusion | jq length)
echo "Success Rate: $(($SUCCESS * 100 / $TOTAL))%"
```

---

## 📞 Escalation

### Contact Information

| Role | Contact | When to Escalate |
|------|---------|------------------|
| **DevOps Lead** | devops-lead@company.com | Deployment failures |
| **Platform Team** | platform-team@company.com | Azure/Fabric issues |
| **Security Team** | security@company.com | Security vulnerabilities |
| **On-Call Engineer** | +1-555-ON-CALL | Critical production issues |

### Escalation Criteria

**Severity 1 (Critical):**
- Production completely down
- Data loss occurring
- Security breach detected

**Severity 2 (High):**
- Major functionality broken
- Significant performance degradation
- Affecting multiple users

**Severity 3 (Medium):**
- Minor functionality issues
- Single user affected
- Workaround available

---

## 📚 Additional Resources

- [Release Notes](../../RELEASE_NOTES_v1.0.0.md)
- [CI/CD Pipeline Guide](../../.github/workflows/README.md)
- [Feature Flags Configuration](./FEATURE_FLAGS_RUNBOOK.md)
- [Monitoring Guide](./MONITORING_RUNBOOK.md)
- [Incident Response](./INCIDENT_RESPONSE_RUNBOOK.md)

---

**Document Owner:** DevOps Team  
**Last Updated:** 2025-10-24  
**Version:** 1.0.0  
**Review Cycle:** Monthly
