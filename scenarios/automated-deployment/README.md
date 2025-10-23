# Automated End-to-End Deployment Scenario

**Demonstrates: Fully automated Fabric deployment with zero interaction**

---

## 🎯 Overview

This scenario showcases the **complete automation capabilities** of the Fabric CI/CD framework by combining all key features into a single, non-interactive deployment:

✅ **Workspace Creation** - Config-driven naming from `project.config.json`  
✅ **Git Integration** - Automatic repository connection  
✅ **Item Creation** - Lakehouses and Notebooks  
✅ **Naming Validation** - Automatic standards enforcement  
✅ **User Management** - Role-based access control  
✅ **Audit Logging** - Complete operation trail  
✅ **Template-Driven** - All config from YAML files  

**Perfect for:**
- Validating the framework template system
- CI/CD pipeline integration
- Demonstrating framework capabilities
- Testing end-to-end automation

---

## Quick Start

### Prerequisites

1. **Configured Framework**
   ```bash
   # If you haven't set up the framework yet:
   python init_new_project.py
   ```

2. **Environment Variables** (in `.env` file)
   ```bash
   # Azure Authentication
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-secret
   
   # Git Integration (optional - will gracefully skip if not configured)
   GITHUB_ORG=your-github-org
   GITHUB_REPO=your-repo-name
   GITHUB_TOKEN=your-pat-token
   
   # Product Contacts
   DATA_OWNER_EMAIL=owner@company.com
   TECHNICAL_LEAD_EMAIL=lead@company.com
   ```

3. **Fabric Capacity**
   - **Note**: Item creation (Lakehouses, Notebooks) requires Fabric Premium capacity
   - Trial/F2 capacity will result in 403 errors for item creation
   - **The scenario handles this gracefully** - workspace and other steps still succeed
   - For full end-to-end testing, use Premium capacity workspace

### Run the Scenario

```bash
# Preview mode (dry run - no changes made)
python scenarios/automated-deployment/run_automated_deployment.py --dry-run

# Execute deployment
python scenarios/automated-deployment/run_automated_deployment.py

# Use custom config
python scenarios/automated-deployment/run_automated_deployment.py --config my_product.yaml
```

### What Actually Works

✅ **Always Works** (any capacity):
- Workspace creation with config-driven naming
- Prerequisites validation
- Audit logging (JSONL format)
- Error handling and graceful degradation

⚠️ **Requires Premium Capacity**:
- Lakehouse creation via API
- Notebook creation via API
- Git integration (workspace must support Git)

⚠️ **Requires Azure AD Configuration**:
- User addition (needs Object IDs, not emails)
- Currently documented as manual step

### Expected Output

```
================================================================================
           Automated End-to-End Fabric Deployment
================================================================================

ℹ Product: Sales Analytics
ℹ Owner: data-owner@company.com
ℹ Domain: Sales & Revenue

[Step 0/8] Validating Prerequisites
✓ project.config.json found
✓ .env file found
✓ All required environment variables set
✓ All prerequisites met!

[Step 1/8] Creating Workspace
ℹ Workspace name (from pattern): {your-prefix}-sales-analytics-dev
ℹ Description: Development environment for Sales Analytics
✓ Created workspace: {your-prefix}-sales-analytics-dev
ℹ Workspace ID: abc12345-6789-...

[Step 2/8] Connecting to Git Repository
ℹ Git Org: your-org
ℹ Repository: your-repo
ℹ Directory: data_products/sales_analytics
✓ Connected to Git: your-org/your-repo

[Step 3/8] Creating Fabric Items
ℹ Creating 3 lakehouses...
✓   Created: BRONZE_SalesData_Lakehouse
✓   Created: SILVER_SalesData_Lakehouse
✓   Created: GOLD_SalesAnalytics_Lakehouse

ℹ Creating 3 notebooks...
✓   Created: 01_IngestSalesData_Notebook
✓   Created: 02_TransformSales_Notebook
✓   Created: 03_ValidateData_Notebook

[Step 4/8] Validating Naming Standards
ℹ Validating 6 items...
✓   ✓ BRONZE_SalesData_Lakehouse
✓   ✓ SILVER_SalesData_Lakehouse
✓   ✓ GOLD_SalesAnalytics_Lakehouse
✓   ✓ 01_IngestSalesData_Notebook
✓   ✓ 02_TransformSales_Notebook
✓   ✓ 03_ValidateData_Notebook
✓ Naming validation complete

[Step 5/8] Adding Users to Workspace
ℹ Adding 2 users...
✓   Added: data-owner@company.com (Admin)
✓   Added: tech-lead@company.com (Member)

[Step 6/8] Committing to Git
✓ Committed to Git: Automated deployment: Sales Analytics [DEV]

[Step 7/8] Writing Audit Log
✓ Audit log written to: audit/audit_trail.jsonl

[Step 8/8] Deployment Summary

Deployment Results:

✓ Deployment completed successfully!

Product: Sales Analytics
Workspace ID: abc12345-6789-...

Items Created:
  Lakehouses: 3
    • BRONZE_SalesData_Lakehouse
    • SILVER_SalesData_Lakehouse
    • GOLD_SalesAnalytics_Lakehouse
  Notebooks: 3
    • 01_IngestSalesData_Notebook
    • 02_TransformSales_Notebook
    • 03_ValidateData_Notebook

Features Demonstrated:
  ✓ Config-driven workspace creation
  ✓ Git integration and automatic connection
  ✓ Naming standards validation
  ✓ Automated item creation
  ✓ User management
  ✓ Centralized audit logging

================================================================================
Automated deployment demonstration complete! 🚀
================================================================================
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `run_automated_deployment.py` | Main automation script |
| `product_config.yaml` | Product and deployment configuration |
| `README.md` | This documentation |

---

## ⚙️ Configuration

### Product Configuration (`product_config.yaml`)

All deployment settings are defined in the YAML configuration:

```yaml
product:
  name: "Sales Analytics"
  description: "Automated sales analytics data product"
  owner_email: "${DATA_OWNER_EMAIL}"
  domain: "Sales & Revenue"
  
environments:
  dev:
    enabled: true
    capacity_type: "trial"
    auto_deploy: true
    
git:
  enabled: true
  organization: "${GITHUB_ORG}"
  repository: "${GITHUB_REPO}"
  directory: "data_products/sales_analytics"
  auto_connect: true
  auto_commit: true
  
items:
  lakehouses:
    - name: "BRONZE_SalesData_Lakehouse"
      description: "Raw sales data"
    - name: "SILVER_SalesData_Lakehouse"
      description: "Cleaned sales data"
    - name: "GOLD_SalesAnalytics_Lakehouse"
      description: "Analytics-ready data"
      
  notebooks:
    - name: "01_IngestSalesData_Notebook"
      description: "Ingest raw sales data"
    - name: "02_TransformSales_Notebook"
      description: "Transform sales data"
    - name: "03_ValidateData_Notebook"
      description: "Validate data quality"
      
users:
  - email: "${DATA_OWNER_EMAIL}"
    role: "Admin"
  - email: "${TECHNICAL_LEAD_EMAIL}"
    role: "Member"
    
naming:
  validate: true
  strict_mode: true
  
audit:
  enabled: true
  log_all_operations: true
```

### Environment Variables Used

All environment variables come from `.env`:

- `DATA_OWNER_EMAIL` - Product owner email
- `TECHNICAL_LEAD_EMAIL` - Technical lead email
- `GITHUB_ORG` - Git organization
- `GITHUB_REPO` - Git repository
- `AZURE_CLIENT_ID` - Azure authentication
- `AZURE_CLIENT_SECRET` - Azure authentication
- `AZURE_TENANT_ID` - Azure authentication
- `FABRIC_CAPACITY_ID` - Fabric capacity

### Workspace Naming

Workspace name is generated from `project.config.json`:

```
Pattern: {prefix}-{product}-{environment}
Example: contoso-sales-analytics-dev
```

Where `{prefix}` comes from your `project.config.json`.

---

## 🔍 What This Scenario Tests

### 1. Template System
- ✅ Reads from `project.config.json`
- ✅ Uses naming patterns correctly
- ✅ Substitutes environment variables
- ✅ Validates configuration

### 2. Workspace Management
- ✅ Creates workspace with config-driven name
- ✅ Applies description from config
- ✅ Uses correct capacity settings

### 3. Git Integration
- ✅ Connects workspace to repository
- ✅ Uses organization from `.env`
- ✅ Sets correct directory path
- ✅ Commits items automatically

### 4. Item Creation
- ✅ Creates multiple item types
- ✅ Handles Fabric API limitations (Trial capacity)
- ✅ Applies descriptions
- ✅ Reports success/failures

### 5. Naming Validation
- ✅ Validates against `naming_standards.yaml`
- ✅ Checks Lakehouse naming (BRONZE/SILVER/GOLD)
- ✅ Validates Notebook numbering (01_*, 02_*, etc.)
- ✅ Enforces strict mode if configured

### 6. User Management
- ✅ Adds multiple users
- ✅ Assigns correct roles
- ✅ Handles missing users gracefully

### 7. Audit Logging
- ✅ Logs deployment event
- ✅ Captures all details
- ✅ Writes to JSONL format
- ✅ Includes timestamps and context

---

## 🎓 Customization

### Change Product Details

Edit `product_config.yaml`:

```yaml
product:
  name: "Your Product Name"
  description: "Your description"
  domain: "Your Domain"
```

### Add More Items

Add to the `items` section:

```yaml
items:
  lakehouses:
    - name: "BRONZE_CustomData_Lakehouse"
      description: "Your lakehouse"
  
  notebooks:
    - name: "04_YourNotebook_Notebook"
      description: "Your notebook"
```

### Change User Roles

Modify the `users` section:

```yaml
users:
  - email: "user1@company.com"
    role: "Admin"
  - email: "user2@company.com"
    role: "Contributor"
  - email: "user3@company.com"
    role: "Viewer"
```

**Available Roles:**
- `Admin` - Full control
- `Member` - Create and edit
- `Contributor` - Edit existing
- `Viewer` - Read-only

### Disable Features

Turn off optional features:

```yaml
git:
  enabled: false  # Disable Git integration
  
naming:
  validate: false  # Disable naming validation
  
audit:
  enabled: false  # Disable audit logging
```

---

## 🚀 CI/CD Integration

This scenario is designed for CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Deploy Fabric Data Product

on:
  push:
    branches: [main]
    paths:
      - 'data_products/sales_analytics/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m venv fabric-env
          source fabric-env/bin/activate
          pip install -r requirements.txt
      
      - name: Configure environment
        run: |
          echo "AZURE_CLIENT_ID=${{ secrets.AZURE_CLIENT_ID }}" >> .env
          echo "AZURE_CLIENT_SECRET=${{ secrets.AZURE_CLIENT_SECRET }}" >> .env
          echo "AZURE_TENANT_ID=${{ secrets.AZURE_TENANT_ID }}" >> .env
          echo "FABRIC_CAPACITY_ID=${{ secrets.FABRIC_CAPACITY_ID }}" >> .env
      
      - name: Run automated deployment
        run: |
          source fabric-env/bin/activate
          cd scenarios/automated-deployment/
          python run_automated_deployment.py
```

### Azure DevOps Example

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - data_products/sales_analytics/*

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.9'
  
  - script: |
      python -m venv fabric-env
      source fabric-env/bin/activate
      pip install -r requirements.txt
    displayName: 'Install dependencies'
  
  - script: |
      source fabric-env/bin/activate
      cd scenarios/automated-deployment/
      python run_automated_deployment.py
    env:
      AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
      AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)
      AZURE_TENANT_ID: $(AZURE_TENANT_ID)
      FABRIC_CAPACITY_ID: $(FABRIC_CAPACITY_ID)
    displayName: 'Deploy to Fabric'
```

---

## 📊 Verification

### Check Fabric Portal

1. Open Fabric Portal
2. Navigate to Workspaces
3. Find workspace: `{your-prefix}-sales-analytics-dev`
4. Verify items created:
   - 3 Lakehouses (BRONZE, SILVER, GOLD)
   - 3 Notebooks (01, 02, 03)

### Check Git Repository

```bash
# View committed items
cd {your-repo-path}/data_products/sales_analytics/
ls -la

# Check commit history
git log --oneline | head -5
```

### Check Audit Log

```bash
# View latest audit entries
tail -n 20 audit/audit_trail.jsonl | jq '.'

# Filter by scenario
grep "AUTOMATED-SCENARIO" audit/audit_trail.jsonl | jq '.'
```

---

## 🐛 Troubleshooting

### Issue: "project.config.json not found"

**Solution:**
```bash
# Run from repository root
cd /path/to/usf-fabric-cicd

# Run initialization if needed
python init_new_project.py

# Then retry
cd scenarios/automated-deployment/
python run_automated_deployment.py
```

### Issue: "Missing environment variables"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify required variables are set
grep -E "AZURE_CLIENT_ID|FABRIC_CAPACITY_ID" .env

# Load environment manually if needed
source .env
export $(cat .env | xargs)
```

### Issue: "Failed to create lakehouse"

**Cause:** Trial capacities often don't support lakehouse creation

**Solution:** This is expected - the scenario handles it gracefully:
- Notebooks will still be created
- Deployment continues
- Summary shows what succeeded

### Issue: "Git connection failed"

**Causes:**
- Invalid GitHub token
- Workspace already connected to different repo
- Insufficient permissions

**Solutions:**
```bash
# Verify GitHub token
echo $GITHUB_TOKEN

# Check token permissions (needs repo access)
# Regenerate token if needed

# Disable Git if not needed
# Edit product_config.yaml:
# git:
#   enabled: false
```

---

## 🎯 Success Criteria

A successful run shows:

- ✅ Workspace created with correct naming pattern
- ✅ Git connection established (if enabled)
- ✅ Items created (or gracefully skipped)
- ✅ Naming validation passed
- ✅ Users added to workspace
- ✅ Audit log written
- ✅ Summary shows "Deployment completed successfully!"

---

## 📚 Related Documentation

- **Main README:** `../../README.md`
- **Template Setup:** `../../docs/getting-started/NEW_PROJECT_SETUP.md`
- **Workspace Provisioning:** `../../docs/guides/WORKSPACE_PROVISIONING_GUIDE.md`
- **Naming Standards:** `../../naming_standards.yaml`
- **Other Scenarios:** `../README.md`

---

## ✨ Summary

This scenario proves that the Fabric CI/CD framework is:

- **Fully Template-Driven:** All org-specific values from config files
- **Zero-Touch Deployment:** Runs without any user interaction
- **Production-Ready:** Suitable for CI/CD pipelines
- **Comprehensive:** Exercises all major framework features
- **Validated:** Tests the entire template system end-to-end

**Perfect for demonstrating that any organization can clone this framework, run `python init_new_project.py`, and be deploying to Fabric in minutes!** 🚀
