# Microsoft Fabric CI/CD Process Demonstration

## Step-by-Step Workflow Example

This notebook demonstrates the complete CI/CD process for Microsoft Fabric using our implementation.

### Prerequisites Setup

```bash
# 1. Set up environment variables
export AZURE_CLIENT_ID="your-service-principal-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_CLIENT_SECRET="your-service-principal-secret"
```

### Step 1: Initialize Fabric Git Integration

```bash
# Connect development workspace to GitHub
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action init-git \
  --git-provider "GitHub" \
  --organization "your-org" \
  --repository "usf-fabric-cicd" \
  --branch "dev"
```

**Expected Output:**
```
Action: init-git
Workspace: usf-fabric-dev
Status: success
Connected to: GitHub - usf-fabric-cicd
Branch: dev
```

### Step 2: Developer Workflow - Make Changes in Fabric

1. **Developer works in Fabric workspace:**
   - Creates/modifies notebooks in `usf-fabric-dev`
   - Updates data pipelines
   - Tests changes in development environment

2. **Sync changes to Git automatically (daily at 2 AM) or manually:**

```bash
# Manual sync from workspace to Git
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action sync-to-git \
  --commit-message "Added new customer analytics pipeline"
```

**This creates:**
- New feature branch: `fabric-sync-20251008-143022`
- Automatic Pull Request to `main` branch
- PR includes all workspace changes

### Step 3: Continuous Integration (CI) Triggers

**When PR is created, GitHub Actions automatically runs:**

1. **Code Quality Checks:**
```bash
# These run automatically in GitHub Actions
black --check --diff notebooks/ ops/
flake8 notebooks/ ops/ --max-line-length=88
python ops/scripts/validate_fabric_artifacts.py --path .
python ops/scripts/check_notebook_outputs.py --path notebooks/
```

2. **Unit Tests:**
```bash
pytest ops/tests/ -v --cov=ops
```

3. **Data Quality Validation:**
```bash
python ops/scripts/run_gx.py --profile ci --workspace usf-fabric-dev
```

**CI Results Example:**
```
✅ Code Quality: PASSED
✅ Unit Tests: PASSED (95% coverage)
✅ Artifact Validation: PASSED
✅ Security Scan: PASSED
⚠️  Data Quality: WARNING (1 minor issue)
```

### Step 4: Continuous Deployment (CD) Process

**After PR approval and merge to `main`:**

#### 4a. Automatic Deployment to Development

```bash
# This runs automatically in GitHub Actions
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-dev" \
  --bundle "./artifacts/fabric_bundle.zip" \
  --mode standard
```

**Environment Configuration Applied:**
```json
{
  "lakehouse_name": "USF_Lakehouse_Dev",
  "sql_server": "usf-sql-dev.database.windows.net",
  "storage_account": "usfdatadev"
}
```

#### 4b. Manual Approval for Test Environment

**GitHub Actions workflow pauses for approval, then:**

```bash
# Deployment via Fabric Deployment Pipeline
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-test" \
  --deployment-pipeline-id "abc123-def456" \
  --source-stage 0 \
  --target-stage 1 \
  --mode promote
```

**Test Environment Configuration:**
```json
{
  "lakehouse_name": "USF_Lakehouse_Test",
  "sql_server": "usf-sql-test.database.windows.net", 
  "storage_account": "usfdatatest",
  "validation_level": "standard",
  "approval_required": true
}
```

#### 4c. Production Deployment (Manual Approval Required)

```bash
# Final promotion to production
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-prod" \
  --deployment-pipeline-id "abc123-def456" \
  --source-stage 1 \
  --target-stage 2 \
  --mode promote
```

**Production Configuration:**
```json
{
  "lakehouse_name": "USF_Lakehouse_Prod",
  "sql_server": "usf-sql-prod.database.windows.net",
  "storage_account": "usfdataprod",
  "validation_level": "strict",
  "blue_green_deployment": true,
  "rollback_enabled": true
}
```

### Step 5: Post-Deployment Validation

**Automated health checks run after each deployment:**

```bash
python ops/scripts/health_check_fabric.py \
  --workspace "usf-fabric-prod" \
  --environment prod \
  --fail-on-critical
```

**Health Check Results:**
```json
{
  "workspace": "usf-fabric-prod",
  "overall_status": "healthy",
  "metrics": {
    "total_items": 47,
    "workspace_response_time": 0.85,
    "failed_items": 0
  },
  "recommendations": [
    "Workspace is operating normally - continue regular monitoring"
  ]
}
```

### Example Pipeline Parameter Substitution

**Original Pipeline Definition:**
```json
{
  "name": "Customer Analytics Pipeline",
  "properties": {
    "activities": [
      {
        "name": "Copy Customer Data",
        "type": "Copy",
        "inputs": [
          {
            "referenceName": "${SQL_SERVER}/CustomerData"
          }
        ],
        "outputs": [
          {
            "referenceName": "${LAKEHOUSE_NAME}/bronze/customers"
          }
        ]
      }
    ]
  }
}
```

**After Environment Substitution (Test):**
```json
{
  "name": "Customer Analytics Pipeline",
  "properties": {
    "activities": [
      {
        "name": "Copy Customer Data", 
        "type": "Copy",
        "inputs": [
          {
            "referenceName": "usf-sql-test.database.windows.net/CustomerData"
          }
        ],
        "outputs": [
          {
            "referenceName": "USF_Lakehouse_Test/bronze/customers"
          }
        ]
      }
    ]
  }
}
```

### Monitoring and Alerting

**Continuous monitoring runs every 4 hours in production:**

```bash
# Scheduled health checks
python ops/scripts/health_check_fabric.py \
  --workspace "usf-fabric-prod" \
  --environment prod \
  --output-format json
```

**Alert Integration:**
- Microsoft Teams notifications for critical issues
- PagerDuty for production incidents
- Email for warnings and updates

### Git Integration Status

**Check current Git sync status:**

```bash
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-prod" \
  --action status
```

**Sample Output:**
```
Git sync status: Committed
Connected to: GitHub - usf-fabric-cicd
Branch: main
Last sync: 2025-10-08T14:30:22Z
```

## Advanced Features

### 1. Rollback Capabilities
```bash
# Rollback to previous version using deployment pipeline
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-prod" \
  --deployment-pipeline-id "abc123-def456" \
  --source-stage 2 \
  --target-stage 2 \
  --mode rollback \
  --rollback-version "v2024.10.07-001"
```

### 2. Canary Deployments (Production)
```bash
# Deploy to 10% of production capacity first
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-prod" \
  --mode canary \
  --canary-percentage 10 \
  --success-threshold 0.99
```

### 3. Blue-Green Deployments
```bash
# Deploy to green environment, then switch traffic
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-prod" \
  --mode blue-green \
  --target-slot green
```

## Summary

This CI/CD implementation provides:

✅ **Automated Git Integration** - Bi-directional sync between Fabric and GitHub
✅ **Environment-Specific Configurations** - Dev/Test/Prod parameter substitution  
✅ **Comprehensive Validation** - Code quality, security, data quality gates
✅ **Multi-Stage Deployment** - Automated Dev → Manual Test → Manual Prod
✅ **Health Monitoring** - Continuous workspace and pipeline monitoring
✅ **Enterprise Features** - Rollbacks, canary deployments, audit trails
✅ **Security Best Practices** - Workload Identity Federation, no secrets in code

The process ensures reliable, secure, and auditable deployments while maintaining development velocity and quality standards.