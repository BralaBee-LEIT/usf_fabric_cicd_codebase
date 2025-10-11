# Complete Implementation Guide: Microsoft Fabric CI/CD Setup

## Prerequisites & Initial Setup

### 1. Azure & Microsoft Fabric Requirements

**Azure Subscription Setup:**
```bash
# 1. Ensure you have an Azure subscription with Fabric capacity
# 2. Create or have access to Microsoft Fabric Premium capacity (P1 or higher)
# 3. Or use Fabric Trial capacity for testing
```

**Required Azure Resources:**
- Microsoft Fabric Premium Capacity (or Trial)
- Azure AD Service Principal
- Azure Key Vault (recommended for secrets)
- Three Fabric Workspaces: Dev, Test, Production

### 2. Create Azure Service Principal

```bash
# Login to Azure CLI
az login

# Create service principal for Fabric CI/CD
az ad sp create-for-rbac \
  --name "sp-fabric-cicd" \
  --role "Contributor" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" \
  --output json

# Save the output - you'll need:
# - appId (CLIENT_ID)
# - password (CLIENT_SECRET) 
# - tenant (TENANT_ID)
```

**Example Output:**
```json
{
  "appId": "12345678-1234-1234-1234-123456789012",
  "displayName": "sp-fabric-cicd",
  "password": "your-secret-password-here",
  "tenant": "87654321-4321-4321-4321-210987654321"
}
```

### 3. Set Up Fabric Workspaces

**Create Workspaces in Fabric Portal:**

1. Go to [Microsoft Fabric Portal](https://fabric.microsoft.com)
2. Create three workspaces:
   - `usf-fabric-dev` (Development)
   - `usf-fabric-test` (Testing) 
   - `usf-fabric-prod` (Production)

**Assign Service Principal Permissions:**
```bash
# For each workspace, add the service principal as Admin or Contributor
# This can be done via Fabric Portal → Workspace Settings → Users and Permissions
```

### 4. Create Fabric Deployment Pipeline

**In Fabric Portal:**
1. Go to Deployment Pipelines
2. Create new pipeline: "USF Fabric CI/CD Pipeline"
3. Assign workspaces to stages:
   - Stage 0 (Development): `usf-fabric-dev`
   - Stage 1 (Test): `usf-fabric-test` 
   - Stage 2 (Production): `usf-fabric-prod`
4. Copy the Pipeline ID (you'll need this for GitHub secrets)

## GitHub Repository Setup

### 1. Clone and Set Up Repository Structure

```bash
# Clone the repository
git clone <your-repo-url>
cd usf-fabric-cicd

# Verify directory structure
tree -L 3
```

**Expected Structure:**
```
usf-fabric-cicd/
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── notebooks/              # Jupyter notebooks
├── pipelines/             # Data pipeline definitions  
├── dataflows/             # Dataflow Gen2 definitions
├── sparkjobdefinitions/   # Spark job definitions
├── ops/
│   ├── scripts/           # Deployment scripts
│   ├── config/            # Environment configurations
│   └── requirements.txt   # Python dependencies
└── governance/            # Data governance files
```

### 2. Configure GitHub Secrets

**Go to GitHub Repository → Settings → Secrets and Variables → Actions**

**Add Repository Secrets:**
```bash
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
AZURE_SUBSCRIPTION_ID=your-subscription-id-here
AZURE_CLIENT_SECRET=your-service-principal-secret
FABRIC_DEPLOYMENT_PIPELINE_ID=your-fabric-pipeline-id
TEAMS_WEBHOOK_URI=https://your-org.webhook.office.com/...  # Optional
```

### 3. Set Up GitHub Environments (Optional but Recommended)

**Create Environments with Protection Rules:**

1. **Development Environment:**
   ```yaml
   # No protection rules - auto-deploy
   ```

2. **Test Environment:**
   ```yaml
   # Settings → Environments → test
   protection_rules:
     - required_reviewers: 1
     - prevent_self_review: false
   ```

3. **Production Environment:**
   ```yaml
   # Settings → Environments → production  
   protection_rules:
     - required_reviewers: 2
     - prevent_self_review: true
     - restrict_pushes: true
   ```

## Step-by-Step Implementation

### Step 1: Install Dependencies and Test Connection

```bash
# 1. Install Python dependencies
pip install -r ops/requirements.txt

# 2. Set environment variables for testing
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id" 
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# 3. Test Fabric API connection
python -c "
from ops.scripts.utilities.fabric_api import fabric_client
try:
    workspaces = fabric_client._make_request('GET', 'workspaces')
    print('✅ Fabric API connection successful')
    print(f'Found {len(workspaces.json().get(\"value\", []))} workspaces')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Step 2: Initialize Fabric Git Integration

**Connect Development Workspace to GitHub:**

```bash
# Initialize Git integration for development workspace
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action init-git \
  --git-provider "GitHub" \
  --organization "your-github-org" \
  --repository "usf-fabric-cicd" \
  --branch "main" \
  --directory "/"
```

**Expected Output:**
```
Action: init-git
Workspace: usf-fabric-dev
Status: success
Connected to: GitHub - usf-fabric-cicd
Branch: main
```

**Verify Connection:**
```bash
# Check Git integration status
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action status
```

### Step 3: Create Sample Fabric Artifacts

**Create Sample Notebook:**
```bash
mkdir -p notebooks
```

Create `notebooks/sample_data_processing.ipynb`:
```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# Sample Data Processing Notebook\n",
        "Environment: ${ENVIRONMENT}\n",
        "Lakehouse: ${LAKEHOUSE_NAME}"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Sample data processing code\n",
        "import pandas as pd\n",
        "print(f\"Processing data in {spark.conf.get('spark.app.name')}\")\n",
        "\n",
        "# Load data from lakehouse\n",
        "df = spark.read.table(\"${LAKEHOUSE_NAME}.bronze.customers\")\n",
        "print(f\"Loaded {df.count()} records\")"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 4
}
```

**Create Sample Pipeline:**
```bash
mkdir -p pipelines
```

Create `pipelines/customer_data_pipeline.pipeline.json`:
```json
{
  "name": "Customer Data Pipeline",
  "properties": {
    "description": "Process customer data from SQL to Lakehouse",
    "activities": [
      {
        "name": "Copy Customer Data",
        "type": "Copy",
        "dependsOn": [],
        "policy": {
          "timeout": "7.00:00:00",
          "retry": 3,
          "retryIntervalInSeconds": 30
        },
        "typeProperties": {
          "source": {
            "type": "SqlServerSource",
            "connectionString": "${SQL_SERVER};Database=CustomerDB"
          },
          "sink": {
            "type": "LakehouseSink", 
            "lakehouseName": "${LAKEHOUSE_NAME}",
            "tableName": "bronze.customers"
          }
        }
      },
      {
        "name": "Transform Customer Data",
        "type": "Notebook",
        "dependsOn": [
          {
            "activity": "Copy Customer Data",
            "dependencyConditions": ["Succeeded"]
          }
        ],
        "typeProperties": {
          "notebook": {
            "referenceName": "sample_data_processing"
          },
          "parameters": {
            "environment": "${ENVIRONMENT}",
            "lakehouse": "${LAKEHOUSE_NAME}"
          }
        }
      }
    ]
  }
}
```

### Step 4: Test Local Validation

```bash
# Test artifact validation
python ops/scripts/validate_fabric_artifacts.py \
  --path . \
  --output-format text

# Check notebook outputs are cleared
python ops/scripts/check_notebook_outputs.py \
  --path notebooks/ \
  --fail-on-outputs

# Test environment configuration
python -c "
from ops.scripts.utilities.environment_config import EnvironmentConfigManager
config = EnvironmentConfigManager('dev')
print('✅ Environment config loaded successfully')
print(f'Dev workspace: {config.env_config[\"workspace\"][\"name\"]}')
"
```

### Step 5: First Deployment Test

```bash
# Create deployment bundle
python ops/scripts/utilities/package_bundle.py \
  --input . \
  --output dist/test_bundle.zip \
  --include-notebooks \
  --include-pipelines

# Test deployment to dev workspace
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-dev" \
  --bundle dist/test_bundle.zip \
  --mode standard
```

**Expected Output:**
```
[INFO] Starting deployment to workspace: usf-fabric-dev
[INFO] Processing: notebooks/sample_data_processing.ipynb
[INFO] Successfully deployed notebook: sample_data_processing
[INFO] Processing: pipelines/customer_data_pipeline.pipeline.json  
[INFO] Successfully deployed pipeline: customer_data_pipeline.pipeline.json with environment config: dev
[INFO] Deployment Report: {
  "workspace": "usf-fabric-dev",
  "status": "SUCCESS", 
  "summary": {
    "total_deployed": 2,
    "total_failed": 0
  }
}
```

### Step 6: Test GitHub Actions Workflows

**Commit and Push to Trigger CI/CD:**

```bash
# Add files to Git
git add .
git commit -m "Initial Fabric artifacts - notebooks and pipelines"
git push origin main
```

**Monitor GitHub Actions:**
1. Go to GitHub → Actions tab
2. Watch the "Fabric CI/CD Pipeline" workflow execute
3. Check each stage:
   - ✅ Code Quality & Linting
   - ✅ Unit & Integration Tests
   - ✅ Package Artifacts
   - ✅ Deploy to Development

### Step 7: Test Manual Sync from Fabric to Git

**Make Changes in Fabric Portal:**
1. Open `usf-fabric-dev` workspace in Fabric
2. Modify the notebook or create a new pipeline
3. Use Source Control in Fabric to commit changes

**Or Trigger Manual Sync:**
```bash
# Sync workspace changes to Git
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action sync-to-git \
  --commit-message "Updated pipeline parameters"
```

**This will:**
- Create new branch: `fabric-sync-YYYYMMDD-HHMMSS`
- Commit workspace changes
- Create Pull Request automatically
- Trigger CI validation on PR

### Step 8: Test Deployment Pipeline Promotion

**Promote to Test Environment:**
```bash
# Manual promotion to test (requires approval in GitHub)
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-test" \
  --deployment-pipeline-id "your-pipeline-id" \
  --source-stage 0 \
  --target-stage 1 \
  --mode promote
```

**Monitor Fabric Portal:**
1. Go to Deployment Pipelines in Fabric
2. Watch the promotion from Dev → Test
3. Verify artifacts appear in Test workspace with correct parameters

## Troubleshooting Common Issues

### Issue 1: Authentication Failures

```bash
# Check service principal permissions
az ad sp show --id $AZURE_CLIENT_ID --query "appId"

# Test Azure login
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Verify Fabric API access
curl -H "Authorization: Bearer $(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)" \
  "https://api.fabric.microsoft.com/v1/workspaces"
```

### Issue 2: Workspace Not Found

```bash
# List available workspaces
python -c "
from ops.scripts.utilities.fabric_api import fabric_client
response = fabric_client._make_request('GET', 'workspaces')
workspaces = response.json().get('value', [])
for ws in workspaces:
    print(f\"Name: {ws['displayName']}, ID: {ws['id']}\")
"
```

### Issue 3: Git Integration Issues

```bash
# Check Git connection status
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action status \
  --output-format json
```

### Issue 4: Deployment Pipeline Not Found

```bash
# List deployment pipelines
python -c "
from ops.scripts.utilities.fabric_deployment_pipeline import FabricDeploymentManager
manager = FabricDeploymentManager()
pipelines = manager.list_deployment_pipelines()
for pipeline in pipelines:
    print(f\"Name: {pipeline['displayName']}, ID: {pipeline['id']}\")
"
```

## Monitoring and Maintenance

### Daily Health Checks

```bash
# Run health check for all environments
for env in dev test prod; do
  python ops/scripts/health_check_fabric.py \
    --workspace "usf-fabric-$env" \
    --environment $env \
    --output-format text
done
```

### Weekly Maintenance Tasks

```bash
# 1. Update Python dependencies
pip install --upgrade -r ops/requirements.txt

# 2. Run comprehensive artifact validation
python ops/scripts/validate_fabric_artifacts.py \
  --path . \
  --fail-on-high

# 3. Check Git sync status
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action status
```

### Monitoring Dashboard

The health check script generates metrics you can visualize:

```bash
# Generate health dashboard data
python ops/scripts/health_check_fabric.py \
  --workspace "usf-fabric-prod" \
  --environment prod \
  --output-format json \
  --output-file dashboard-data.json
```

## Next Steps

### 1. Add Your Real Fabric Artifacts
- Replace sample notebooks with your actual notebooks
- Add your data pipelines and dataflows
- Configure environment-specific parameters

### 2. Set Up Monitoring Integration
- Configure Teams/Slack notifications
- Set up PagerDuty for production alerts
- Create Grafana dashboards for metrics

### 3. Advanced Features
- Implement data quality checks with Great Expectations
- Add Power BI report deployment
- Set up disaster recovery procedures

### 4. Security Hardening
- Implement network restrictions
- Enable audit logging
- Set up vulnerability scanning

## Support and Documentation

**Key Files to Understand:**
- `ops/scripts/deploy_fabric.py` - Main deployment logic
- `ops/scripts/sync_fabric_git.py` - Git integration
- `ops/config/*.json` - Environment configurations
- `.github/workflows/` - CI/CD automation

**Getting Help:**
- Check GitHub Actions logs for workflow issues
- Use health check scripts for diagnostics
- Review Fabric Portal for workspace status
- Monitor deployment pipeline status

This guide provides everything needed to implement and maintain a production-ready Microsoft Fabric CI/CD solution!