# Environment Promotion Guide

**Date:** 21 October 2025  
**Purpose:** Complete guide for TEST/PROD workspaces and promotion workflow  
**Status:** Production-Ready Implementation

---

## 📋 Table of Contents

1. [Creating TEST and PROD Workspaces](#1-creating-test-and-prod-workspaces)
2. [Promotion Workflow: Feature → DEV → TEST → PROD](#2-promotion-workflow)
3. [Using Fabric Deployment Pipelines](#3-using-fabric-deployment-pipelines)
4. [Git Branch Strategy](#4-git-branch-strategy)
5. [Automated CI/CD Pipeline](#5-automated-cicd-pipeline)

---

## 1. Creating TEST and PROD Workspaces

### Current State

Right now, you only have **DEV workspaces**:
- ✅ Customer Analytics [DEV]
- ✅ Sales Analytics [DEV]

### Step 1: Update YAML to Include TEST and PROD

Edit your product descriptor to add test and prod environments:

**File:** `data_products/onboarding/customer_analytics.yaml`

```yaml
product:
  name: "Customer Analytics"
  owner_email: "data-team@company.com"
  domain: "Customer Insights"

environments:
  dev:
    enabled: true
    capacity_type: "trial"
    description: "Development workspace for customer analytics"
  
  test:
    enabled: true
    capacity_type: "trial"  # or "capacity" with capacity_id
    description: "Test/QA workspace for customer analytics"
  
  prod:
    enabled: true
    capacity_type: "capacity"  # Production should use paid capacity
    capacity_id: "${FABRIC_CAPACITY_PROD_ID}"  # Required for prod
    description: "Production workspace for customer analytics"

git:
  organization: "${GITHUB_ORG}"
  repository: "${GITHUB_REPO}"
  feature_prefix: "feature"
  directory: "data_products/customer_analytics"

automation:
  audit_reference: "JIRA-12345"
```

### Step 2: Run Onboarding Again

```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd

# This will create ALL enabled environments (DEV, TEST, PROD)
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml
```

### Expected Output

```
ℹ️ Loaded 53 environment variables from .env
ℹ️ Starting onboarding for product 'Customer Analytics'
✅ Seeded scaffold for customer_analytics
ℹ️ Creating Fabric workspace: Customer Analytics [DEV]
⚠️ Workspace already exists: Customer Analytics [DEV]
ℹ️ Creating Fabric workspace: Customer Analytics [TEST]
✅ Created workspace 'Customer Analytics [TEST]'
   ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ℹ️ Creating Fabric workspace: Customer Analytics [PROD]
✅ Created workspace 'Customer Analytics [PROD]'
   ID: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
✅ Onboarding workflow complete
```

### Result: 3 Workspaces Created

After running this, you'll have:
- ✅ **Customer Analytics [DEV]** - Development
- ✅ **Customer Analytics [TEST]** - Test/QA
- ✅ **Customer Analytics [PROD]** - Production

---

## 2. Promotion Workflow

### The Standard Flow

```
Feature Branch → DEV → TEST → PROD
     ↓            ↓      ↓       ↓
  Isolated     Develop  QA    Release
   Workspace  Workspace Workspace Workspace
```

### Complete Workflow Explained

#### Phase 1: Feature Development (Isolated)

**Scenario:** Developer working on JIRA-12345

```bash
# Create feature workspace + branch
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml \
  --feature JIRA-12345
```

**Creates:**
- Feature workspace: `Customer Analytics [FEATURE-JIRA-12345]`
- Git branch: `feature/customer-analytics/JIRA-12345`
- Git sync: Workspace ↔ Branch

**Developer workflow:**
1. Create items in feature workspace (lakehouses, notebooks, pipelines)
2. Develop and test in isolation
3. Commit changes to Git (workspace → feature branch)
4. Create Pull Request: `feature/customer-analytics/JIRA-12345` → `main`

#### Phase 2: Merge to DEV

**After PR approval:**

```bash
# Merge feature branch to main
git checkout main
git pull origin main
git merge feature/customer-analytics/JIRA-12345
git push origin main
```

**What happens:**
- Feature branch merged into `main`
- Code now in repository `main` branch
- Ready to deploy to DEV workspace

**Deploy to DEV:**

```bash
# Option A: Using Fabric Git Integration
# In Fabric portal:
# 1. Open "Customer Analytics [DEV]" workspace
# 2. Click "Git sync" → "Update from Git"
# 3. Items from main branch appear in DEV workspace

# Option B: Using deployment script
python3 ops/scripts/deploy_fabric.py \
  --workspace "Customer Analytics [DEV]" \
  --mode standard
```

#### Phase 3: Promote DEV → TEST

**Using Fabric Deployment Pipeline (Recommended):**

```bash
# Promote items from DEV to TEST
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 0  # DEV stage
  --target-stage 1  # TEST stage
  --mode promote
```

**Manual alternative:**

```bash
# Export items from DEV
python3 ops/scripts/manage_fabric_items.py get-definition \
  --workspace "Customer Analytics [DEV]" \
  --item-name "CustomerDataLakehouse" \
  --type Lakehouse \
  --output exports/lakehouse_dev.json

# Import to TEST
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Customer Analytics [TEST]" \
  --name "CustomerDataLakehouse" \
  --type Lakehouse \
  --definition-file exports/lakehouse_dev.json
```

**Testing in TEST:**
1. Run integration tests
2. Validate data quality
3. Performance testing
4. UAT (User Acceptance Testing)

#### Phase 4: Promote TEST → PROD

**Using Fabric Deployment Pipeline:**

```bash
# Requires approval in production
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 1  # TEST stage
  --target-stage 2  # PROD stage
  --mode promote \
  --approval-required
```

**Production validation:**
1. Blue/green deployment (if configured)
2. Smoke tests
3. Rollback capability enabled
4. Monitoring alerts active

---

## 3. Using Fabric Deployment Pipelines

### What is a Deployment Pipeline?

A Fabric Deployment Pipeline is Microsoft's built-in tool for promoting items between workspaces (DEV → TEST → PROD).

### Setup (One-Time)

#### Step 1: Create Pipeline in Fabric Portal

1. **Open Fabric portal:** https://app.fabric.microsoft.com
2. **Navigate to:** Deployment pipelines
3. **Click:** "New pipeline"
4. **Name:** "Customer Analytics Pipeline"
5. **Create stages:**
   - Stage 0: Development
   - Stage 1: Test
   - Stage 2: Production

#### Step 2: Assign Workspaces to Stages

1. **Stage 0 (Development):** Assign "Customer Analytics [DEV]"
2. **Stage 1 (Test):** Assign "Customer Analytics [TEST]"
3. **Stage 2 (Production):** Assign "Customer Analytics [PROD]"

#### Step 3: Copy Pipeline ID

1. In pipeline settings, **copy the Pipeline ID**
2. Add to `.env` file:
   ```bash
   FABRIC_DEPLOYMENT_PIPELINE_ID=your-pipeline-id-here
   ```

### Using the Pipeline

#### Promote DEV → TEST

```bash
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 0 \
  --target-stage 1 \
  --mode promote
```

#### Promote TEST → PROD

```bash
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 1 \
  --target-stage 2 \
  --mode promote
```

#### Promote Specific Items Only

```bash
# Get item IDs from DEV workspace
LAKEHOUSE_ID=$(python3 ops/scripts/manage_fabric_items.py get \
  --workspace "Customer Analytics [DEV]" \
  --item-name "CustomerDataLakehouse" \
  --type Lakehouse \
  --json | jq -r '.id')

# Promote only that lakehouse
python3 ops/scripts/utilities/fabric_deployment_pipeline.py \
  promote \
  --pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 0 \
  --target-stage 1 \
  --items "${LAKEHOUSE_ID}"
```

---

## 4. Git Branch Strategy

### Branch Structure

```
main (production)
  └── develop (integration)
       └── feature/customer-analytics/JIRA-12345 (isolated development)
```

### Current Implementation

**Note:** Your current codebase uses a **simplified Git strategy**:

- **`main`** branch = production-ready code
- **`feature/*`** branches = isolated development

### Workflow

```bash
# 1. Create feature branch (done by onboarding script)
git checkout -b feature/customer-analytics/JIRA-12345

# 2. Develop in feature workspace
# (Items synced via Fabric Git Integration)

# 3. Commit changes
git add .
git commit -m "feat: Add customer segmentation pipeline"
git push origin feature/customer-analytics/JIRA-12345

# 4. Create PR
gh pr create \
  --base main \
  --head feature/customer-analytics/JIRA-12345 \
  --title "Customer Segmentation Pipeline" \
  --body "Implements customer segmentation using RFM analysis"

# 5. After approval, merge to main
gh pr merge --squash

# 6. Deploy from main to DEV
# (Automatic or manual trigger)

# 7. Promote DEV → TEST → PROD
# (Via Fabric Deployment Pipeline)
```

### Git-Workspace Mapping

| Git Branch | Fabric Workspace | Purpose |
|------------|------------------|---------|
| `feature/*` | Feature workspace | Isolated development |
| `main` | DEV workspace | Development testing |
| `main` (promoted) | TEST workspace | QA/UAT |
| `main` (promoted) | PROD workspace | Production |

---

## 5. Automated CI/CD Pipeline

### GitHub Actions Workflow

Your codebase includes a comprehensive GitHub Actions workflow:

**File:** `.github/workflows/fabric-cicd-pipeline.yml`

### How It Works

#### Trigger: Push to `main` branch

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

#### Stage 1: Build and Test

```yaml
- name: Run tests
  run: |
    pytest ops/scripts/tests/
```

#### Stage 2: Deploy to DEV (Automatic)

```yaml
- name: Deploy to Development
  run: |
    python ops/scripts/deploy_fabric.py \
      --workspace "Customer Analytics [DEV]" \
      --mode standard
```

#### Stage 3: Deploy to TEST (Manual Approval)

```yaml
environment:
  name: test
  url: https://app.fabric.microsoft.com

- name: Promote to Test
  run: |
    python ops/scripts/deploy_fabric.py \
      --deployment-pipeline-id "$DEPLOYMENT_PIPELINE_ID" \
      --source-stage 0 \
      --target-stage 1 \
      --mode promote
```

#### Stage 4: Deploy to PROD (Manual Approval)

```yaml
environment:
  name: production
  url: https://app.fabric.microsoft.com

- name: Promote to Production
  run: |
    python ops/scripts/deploy_fabric.py \
      --deployment-pipeline-id "$DEPLOYMENT_PIPELINE_ID" \
      --source-stage 1 \
      --target-stage 2 \
      --mode promote
```

### Setup GitHub Environments

1. **Go to repository:** Settings → Environments
2. **Create environments:**
   - `test` (with approvers)
   - `production` (with approvers)
3. **Add required reviewers** for each environment

---

## 📊 Complete Example Walkthrough

### Scenario: Deploy Customer Segmentation Feature

#### Step 1: Create Feature Workspace

```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml \
  --feature JIRA-456
```

**Result:**
- ✅ Feature workspace: `Customer Analytics [FEATURE-JIRA-456]`
- ✅ Git branch: `feature/customer-analytics/JIRA-456`

#### Step 2: Develop in Feature Workspace

```bash
# Create lakehouse
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Customer Analytics [FEATURE-JIRA-456]" \
  --name "CustomerSegmentationLH" \
  --type Lakehouse

# Create notebook
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Customer Analytics [FEATURE-JIRA-456]" \
  --name "RFM_Analysis_Notebook" \
  --type Notebook

# Sync to Git (in Fabric portal or via API)
# Items committed to feature branch
```

#### Step 3: Create PR and Merge

```bash
gh pr create \
  --base main \
  --head feature/customer-analytics/JIRA-456 \
  --title "Customer Segmentation via RFM"

# After approval
gh pr merge --squash
```

#### Step 4: Deploy to DEV

```bash
# Automatic via GitHub Actions
# Or manual:
python3 ops/scripts/deploy_fabric.py \
  --workspace "Customer Analytics [DEV]" \
  --mode standard
```

#### Step 5: Promote to TEST

```bash
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 0 \
  --target-stage 1 \
  --mode promote
```

**Test in TEST workspace:**
- ✅ Run integration tests
- ✅ Data quality validation
- ✅ UAT sign-off

#### Step 6: Promote to PROD

```bash
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 1 \
  --target-stage 2 \
  --mode promote \
  --approval-required
```

**Production validation:**
- ✅ Smoke tests pass
- ✅ Monitoring active
- ✅ Rollback plan ready

---

## 🔧 Quick Commands Reference

### Create All Environments

```bash
# Update YAML with dev, test, prod environments
# Then run:
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml
```

### Promote Items

```bash
# DEV → TEST
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 0 --target-stage 1 --mode promote

# TEST → PROD
python3 ops/scripts/deploy_fabric.py \
  --deployment-pipeline-id "${FABRIC_DEPLOYMENT_PIPELINE_ID}" \
  --source-stage 1 --target-stage 2 --mode promote
```

### List Workspaces by Environment

```bash
# All DEV workspaces
python3 ops/scripts/manage_workspaces.py list | grep "\[DEV\]"

# All TEST workspaces
python3 ops/scripts/manage_workspaces.py list | grep "\[TEST\]"

# All PROD workspaces
python3 ops/scripts/manage_workspaces.py list | grep "\[PROD\]"
```

---

## ✅ Summary

### Answer to Your Questions:

**1. What about TEST and PROD workspaces?**
- Update YAML to include `test` and `prod` environments
- Run onboarding script again
- It will create workspaces for all enabled environments
- Naming: `<Product> [DEV]`, `<Product> [TEST]`, `<Product> [PROD]`

**2. How does promotion work?**
- **Feature → DEV:** Git PR merge + Git sync or deployment
- **DEV → TEST:** Fabric Deployment Pipeline promotion (manual or CI/CD)
- **TEST → PROD:** Fabric Deployment Pipeline promotion (requires approval)
- **Git flow:** Feature branch → main branch → deployed to workspaces
- **Fabric flow:** Items promoted via Deployment Pipeline API

### Key Takeaways:

1. ✅ **Workspaces** = Environment-specific (DEV/TEST/PROD)
2. ✅ **Git branches** = Feature development (feature/*) → integration (main)
3. ✅ **Deployment Pipeline** = Microsoft Fabric's tool for promoting items
4. ✅ **CI/CD** = Automated via GitHub Actions
5. ✅ **Manual control** = Approvals required for TEST and PROD

---

*Generated: 21 October 2025*  
*Status: Production-Ready*  
*Next: Create TEST and PROD workspaces!* 🚀
