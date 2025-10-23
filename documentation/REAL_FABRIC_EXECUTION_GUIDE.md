# Real Microsoft Fabric Execution Guide

**Created**: 21 October 2025  
**Purpose**: Step-by-step guide to run workspace templating automation against a live Microsoft Fabric tenant  
**Status**: Production-ready with all quality improvements

---

## 🎯 Prerequisites Checklist

Before running against real Fabric, ensure you have:

### Required Access
- [ ] **Microsoft Fabric tenant** with Workspace creation permissions
- [ ] **Azure Service Principal** with Fabric API access
- [ ] **Fabric Capacity** (Trial, Premium, or Fabric F-series)
- [ ] **GitHub repository** access (if using Git integration)

### Required Information
- [ ] Azure Tenant ID
- [ ] Azure Client ID (Service Principal)
- [ ] Azure Client Secret (Service Principal Secret)
- [ ] Azure Subscription ID
- [ ] Fabric Capacity ID (optional for Trial, required for Premium/Fabric)

### Tools Installed
- [ ] Python 3.9+ with `fabric-cicd` Conda environment
- [ ] Git 2.30+
- [ ] Text editor (VSCode recommended)

---

## 📋 Step-by-Step Execution Journey

### **Phase 1: Environment Setup** (5-10 minutes)

#### Step 1.1: Verify Conda Environment

```bash
# Check current environment
conda env list

# Activate fabric-cicd environment
conda activate fabric-cicd

# Verify Python version (should be 3.11.14)
python --version

# Verify dependencies
python -c "import yaml, msal, requests; print('✅ Dependencies loaded')"
```

**Expected Output:**
```
✅ Dependencies loaded
```

**If errors occur:**
```bash
# Reinstall environment
conda env create -f environment.yml --force
conda activate fabric-cicd
```

---

#### Step 1.2: Configure Environment Variables

```bash
# Navigate to project root
cd /home/sanmi/Documents/J'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd

# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

**Minimum Required Configuration in `.env`:**

```bash
# ============================================================================
# Azure Authentication (Required)
# ============================================================================
AZURE_CLIENT_ID=<your-service-principal-client-id>
AZURE_CLIENT_SECRET=<your-service-principal-secret>
AZURE_TENANT_ID=<your-azure-tenant-id>
AZURE_SUBSCRIPTION_ID=<your-azure-subscription-id>

# ============================================================================
# GitHub Configuration (Required for Git integration)
# ============================================================================
GITHUB_TOKEN=ghp_<your-github-personal-access-token>
GITHUB_ORGANIZATION=<your-github-org>
GITHUB_REPOSITORY=<your-repo-name>

# ============================================================================
# Optional: API Configuration
# ============================================================================
FABRIC_API_MAX_RETRIES=3  # Configurable retry count (new!)
DEBUG_MODE=false
LOG_LEVEL=INFO
```

**Security Note:** 🔒 Never commit `.env` file to Git! It's in `.gitignore`.

---

#### Step 1.3: Validate Configuration

```bash
# Test configuration loading
python -c "
from ops.scripts.utilities.config_manager import ConfigManager
cm = ConfigManager()
print('✅ Configuration loaded successfully')
print(f'Project: {cm.get_project_name()}')
"
```

**Expected Output:**
```
✅ Configuration loaded successfully
Project: usf2-fabric-cicd
```

---

#### Step 1.4: Test Fabric Authentication

```bash
# Test authentication and API access
python -c "
import os
from ops.scripts.utilities.workspace_manager import WorkspaceManager

wm = WorkspaceManager()
print('✅ Authentication successful')
print(f'Token acquired for tenant: {os.getenv(\"AZURE_TENANT_ID\")}')
"
```

**Expected Output:**
```
✅ Authentication successful
Token acquired for tenant: <your-tenant-id>
```

**If authentication fails:**
- Verify service principal credentials
- Check service principal has **Workspace Admin** role in Fabric
- Ensure service principal is not blocked by Conditional Access policies

---

### **Phase 2: Prepare Data Product Descriptor** (5 minutes)

#### Step 2.1: Create Data Product Descriptor

```bash
# Create descriptor file
mkdir -p data_products/onboarding
nano data_products/onboarding/my_product.yaml
```

**Example Descriptor (`my_product.yaml`):**

```yaml
product:
  name: My Data Product
  slug: my-data-product  # auto-generated if omitted
  description: "Sample data product for testing workspace templating"
  owner: data-engineering@yourcompany.com
  team: Data Engineering

environments:
  dev:
    enabled: true
    capacity_type: trial  # Options: trial, premium_p1, fabric_f2, fabric_f64, etc.
    capacity_id: null  # Optional: specify GUID for Premium/Fabric capacities
    description: "Development environment for testing"

git:
  provider: GitHub
  organization: your-github-org  # Will use GITHUB_ORGANIZATION from .env if omitted
  repository: your-repo-name     # Will use GITHUB_REPOSITORY from .env if omitted
  default_branch: main

scaffold:
  directories:
    - data/bronze
    - data/silver
    - data/gold
    - notebooks
    - pipelines
    - reports
  notebooks:
    - name: etl_bronze_to_silver
      language: PySpark
      description: "Transform raw data to silver layer"
    - name: etl_silver_to_gold
      language: PySpark
      description: "Transform silver data to gold layer"
```

**Configuration Tips:**

| Field | Description | Examples |
|-------|-------------|----------|
| `capacity_type` | Fabric capacity tier | `trial`, `premium_p1`, `fabric_f2`, `fabric_f8`, `fabric_f64` |
| `capacity_id` | GUID of existing capacity (optional for Trial) | `12345678-1234-1234-1234-123456789012` |
| `slug` | URL-safe identifier (auto-generated if omitted) | `my-data-product`, `sales-analytics` |

---

#### Step 2.2: Validate Descriptor Syntax

```bash
# Validate YAML syntax
python -c "
import yaml
with open('data_products/onboarding/my_product.yaml') as f:
    data = yaml.safe_load(f)
    print('✅ Descriptor syntax valid')
    print(f'Product: {data[\"product\"][\"name\"]}')
    print(f'DEV enabled: {data[\"environments\"][\"dev\"][\"enabled\"]}')
"
```

**Expected Output:**
```
✅ Descriptor syntax valid
Product: My Data Product
DEV enabled: True
```

---

### **Phase 3: Dry Run** (2 minutes)

**CRITICAL:** Always run with `--dry-run` first!

#### Step 3.1: Execute Dry Run

```bash
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml \
  --dry-run
```

**Expected Output:**
```
🔍 DRY RUN: No changes will be made

📦 Loaded data product descriptor: my_product.yaml
Product: My Data Product
Owner: data-engineering@yourcompany.com
Team: Data Engineering

🏗️  Would create workspace: My Data Product [DEV]
   Capacity: trial
   Description: Development environment for testing

📁 Would scaffold repository directories:
   ✓ data/bronze
   ✓ data/silver
   ✓ data/gold
   ✓ notebooks
   ✓ pipelines
   ✓ reports

📓 Would create notebooks:
   ✓ etl_bronze_to_silver.ipynb (PySpark)
   ✓ etl_silver_to_gold.ipynb (PySpark)

🌿 Would create Git branch: data-product/my-data-product/dev
🔗 Would link workspace to Git branch: data-product/my-data-product/dev

📋 Would write to registry: data_products/registry.json
📝 Would write audit log: .onboarding_logs/my-data-product_20251021_143022.json

✅ Dry run complete. Use --json for machine-readable output.
```

**Review the output carefully:**
- Workspace names are correct
- Directories and notebooks match your needs
- Git branch names follow your conventions

---

### **Phase 4: Live Execution** (3-5 minutes)

#### Step 4.1: Execute Against Real Fabric

```bash
# Full execution with live Fabric API calls
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml
```

**Real-Time Output:**
```
📦 Loaded data product descriptor: my_product.yaml
Product: My Data Product
Slug: my-data-product

🔐 Authenticating with Microsoft Fabric...
✅ Authentication successful

🏗️  Creating workspace: My Data Product [DEV]
⏳ Calling Fabric API: POST /v1/workspaces
✅ Workspace created successfully
   ID: abc-123-workspace-guid
   URL: https://app.fabric.microsoft.com/groups/abc-123-workspace-guid

📁 Scaffolding repository structure...
✅ Created directory: data/bronze
✅ Created directory: data/silver
✅ Created directory: data/gold
✅ Created directory: notebooks
✅ Created directory: pipelines
✅ Created directory: reports

📓 Creating notebooks...
✅ Created notebook: notebooks/etl_bronze_to_silver.ipynb
✅ Created notebook: notebooks/etl_silver_to_gold.ipynb

🌿 Creating Git branch: data-product/my-data-product/dev
✅ Branch created and checked out

🔗 Linking workspace to Git repository...
⏳ Configuring Fabric Git integration...
✅ Workspace linked to branch: data-product/my-data-product/dev

📋 Writing to registry...
✅ Registry updated: data_products/registry.json

📝 Writing audit log...
✅ Audit log created: .onboarding_logs/my-data-product_20251021_143530.json

🎉 Onboarding complete!
   Workspace: My Data Product [DEV]
   Workspace ID: abc-123-workspace-guid
   Git Branch: data-product/my-data-product/dev
   Execution time: 45.2s
```

---

#### Step 4.2: Verify in Fabric Portal

**Manual Verification Steps:**

1. **Open Fabric Portal:**
   ```
   https://app.fabric.microsoft.com
   ```

2. **Navigate to Workspaces:**
   - Click "Workspaces" in left sidebar
   - Find "My Data Product [DEV]"

3. **Verify Workspace Contents:**
   - Should be empty (scaffold is in Git, not yet synced)

4. **Check Git Integration:**
   - Click workspace settings (gear icon)
   - Navigate to "Git integration"
   - Should show: Connected to `your-org/your-repo` on branch `data-product/my-data-product/dev`

5. **Trigger Git Sync:**
   - Click "Source control" in workspace
   - Click "Sync" or "Update all"
   - Notebooks and directories should appear in workspace

---

### **Phase 5: Feature Branch Workflow** (Optional, 3-5 minutes)

Test the feature branch workflow for isolated development.

#### Step 5.1: Create Feature Workspace

```bash
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml \
  --feature ABC-123
```

**Expected Output:**
```
📦 Loaded data product descriptor: my_product.yaml
🎫 Feature ticket: ABC-123

🔐 Authenticating with Microsoft Fabric...
✅ Authentication successful

🏗️  Reusing existing DEV workspace: My Data Product [DEV]
   ID: abc-123-workspace-guid

🏗️  Creating feature workspace: My Data Product [Feature ABC-123]
⏳ Calling Fabric API: POST /v1/workspaces
✅ Feature workspace created successfully
   ID: def-456-workspace-guid
   URL: https://app.fabric.microsoft.com/groups/def-456-workspace-guid

🌿 Creating Git branch: feature/ABC-123
✅ Branch created from: data-product/my-data-product/dev

🔗 Linking feature workspace to Git repository...
✅ Workspace linked to branch: feature/ABC-123

📋 Writing to registry...
✅ Registry updated with feature workspace

📝 Writing audit log...
✅ Audit log created: .onboarding_logs/my-data-product_ABC-123_20251021_144015.json

🎉 Feature workspace onboarding complete!
   DEV Workspace: My Data Product [DEV]
   Feature Workspace: My Data Product [Feature ABC-123]
   Feature Branch: feature/ABC-123
   Execution time: 38.7s
```

---

#### Step 5.2: Work in Feature Workspace

1. **Open Feature Workspace in Fabric Portal:**
   ```
   https://app.fabric.microsoft.com/groups/def-456-workspace-guid
   ```

2. **Make Changes:**
   - Edit notebooks
   - Add pipelines
   - Test transformations

3. **Commit Changes via Fabric:**
   - Click "Source control" in workspace
   - Enter commit message: "feat: ABC-123 - Added new transformation logic"
   - Click "Commit"

4. **Changes are isolated to `feature/ABC-123` branch**

5. **Merge via Pull Request (GitHub):**
   ```bash
   # Push feature branch to remote
   git push origin feature/ABC-123
   
   # Create PR on GitHub
   # Title: "[ABC-123] New transformation logic"
   # Base: data-product/my-data-product/dev
   # Compare: feature/ABC-123
   ```

---

### **Phase 6: Verification and Testing** (5 minutes)

#### Step 6.1: Check Registry File

```bash
# View registry contents
cat data_products/registry.json | python -m json.tool
```

**Expected Structure:**
```json
{
  "products": [
    {
      "name": "My Data Product",
      "slug": "my-data-product",
      "owner": "data-engineering@yourcompany.com",
      "workspaces": {
        "dev": {
          "id": "abc-123-workspace-guid",
          "url": "https://app.fabric.microsoft.com/groups/abc-123-workspace-guid",
          "capacity_type": "trial"
        },
        "feature_ABC-123": {
          "id": "def-456-workspace-guid",
          "url": "https://app.fabric.microsoft.com/groups/def-456-workspace-guid",
          "capacity_type": "trial",
          "feature_ticket": "ABC-123"
        }
      },
      "git_branches": {
        "dev": "data-product/my-data-product/dev",
        "feature_ABC-123": "feature/ABC-123"
      },
      "created_at": "2025-10-21T14:35:30Z",
      "updated_at": "2025-10-21T14:40:15Z"
    }
  ],
  "last_updated": "2025-10-21T14:40:15Z"
}
```

---

#### Step 6.2: Check Audit Logs

```bash
# List audit logs
ls -lh .onboarding_logs/

# View latest audit log
cat .onboarding_logs/my-data-product_*.json | python -m json.tool
```

**Audit Log Contains:**
- Timestamp of execution
- User who ran the script
- Data product descriptor used
- Workspaces created (with IDs)
- Git branches created
- Scaffold directories/files created
- API calls made (sanitized, no credentials)
- Execution time

---

#### Step 6.3: Test Workspace Access

```bash
# List workspaces via API
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager

wm = WorkspaceManager()
workspaces = wm.list_workspaces()

print('Your Fabric Workspaces:')
for ws in workspaces:
    if 'My Data Product' in ws['displayName']:
        print(f'  ✓ {ws[\"displayName\"]} - {ws[\"id\"]}')
"
```

**Expected Output:**
```
Your Fabric Workspaces:
  ✓ My Data Product [DEV] - abc-123-workspace-guid
  ✓ My Data Product [Feature ABC-123] - def-456-workspace-guid
```

---

### **Phase 7: Monitoring and Logs** (Ongoing)

#### Step 7.1: Check Logs for Errors

```bash
# View recent logs (credential-sanitized!)
tail -f .onboarding_logs/*.json | python -m json.tool
```

**Log Entries Show:**
- ✅ Workspace creation API calls (200 OK)
- ✅ Git branch creation (success/already exists)
- ✅ Git workspace linking (success)
- ⚠️ Warnings (e.g., workspace already exists, reusing)
- ❌ Errors (e.g., authentication failed, API rate limit)

**Security Note:** All logs are sanitized! Bearer tokens, passwords, and secrets are automatically redacted.

---

#### Step 7.2: Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| **"Authentication failed"** | Verify service principal credentials in `.env` |
| **"Workspace already exists"** | Script will reuse existing workspace (safe) |
| **"Git repository not initialized"** | Run `git init` in project root |
| **"Capacity not found"** | Verify `capacity_id` in descriptor or use `trial` |
| **"Permission denied"** | Ensure service principal has **Workspace Admin** role |
| **"API rate limit exceeded"** | Wait 60 seconds and retry (configurable via `FABRIC_API_MAX_RETRIES`) |

---

### **Phase 8: Cleanup (Optional)**

If you want to remove test workspaces:

#### Step 8.1: Delete Workspaces via API

```bash
# Delete feature workspace
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager

wm = WorkspaceManager()
wm.delete_workspace('def-456-workspace-guid')
print('✅ Feature workspace deleted')
"

# Delete DEV workspace
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager

wm = WorkspaceManager()
wm.delete_workspace('abc-123-workspace-guid')
print('✅ DEV workspace deleted')
"
```

#### Step 8.2: Clean Up Git Branches

```bash
# Delete feature branch
git branch -D feature/ABC-123
git push origin --delete feature/ABC-123

# Delete product branch
git branch -D data-product/my-data-product/dev
git push origin --delete data-product/my-data-product/dev
```

#### Step 8.3: Remove Registry Entry

```bash
# Edit registry manually
nano data_products/registry.json

# Or reset registry
echo '{"products": [], "last_updated": null}' > data_products/registry.json
```

---

## 🎯 Production Deployment Checklist

When ready to deploy for real teams:

- [ ] **Service Principal configured** with minimal required permissions
- [ ] **Capacity provisioned** (Premium or Fabric F-series for production)
- [ ] **Git repository initialized** and pushed to remote
- [ ] **CI/CD pipeline configured** (`.github/workflows/test.yml` is ready!)
- [ ] **Data product descriptors reviewed** by data owners
- [ ] **Security scan passed** (Bandit, Safety - automated in CI/CD)
- [ ] **Documentation shared** with data engineering teams
- [ ] **Audit logs configured** for monitoring (`.onboarding_logs/`)
- [ ] **Notification webhooks set up** (optional, Teams/Slack)

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Rotate credentials regularly** - Service principal secrets should expire
3. **Use Azure Key Vault** - Store secrets in Key Vault for production
4. **Monitor service principal usage** - Check Azure AD audit logs
5. **Enable Conditional Access** - Restrict service principal to trusted IPs
6. **Review audit logs** - Check `.onboarding_logs/` for suspicious activity
7. **Sanitization enabled** - All logs automatically redact sensitive data (new!)

---

## 📊 What Gets Created in Fabric

After successful execution, your Fabric tenant will have:

### Workspaces
- `My Data Product [DEV]` - Development workspace
- `My Data Product [Feature ABC-123]` - Feature workspace (if --feature used)

### Git Integration
- Workspace linked to Git repository
- Branch: `data-product/my-data-product/dev`
- Feature branch: `feature/ABC-123` (if applicable)

### Scaffold (In Git, synced to Fabric)
- Directories: `data/bronze`, `data/silver`, `data/gold`, `notebooks`, `pipelines`, `reports`
- Notebooks: `etl_bronze_to_silver.ipynb`, `etl_silver_to_gold.ipynb`

### Local Artifacts
- `data_products/registry.json` - Workspace registry
- `.onboarding_logs/*.json` - Audit logs (credential-sanitized)

---

## 🚀 Next Steps

After successful onboarding:

1. **Share workspace URLs** with data product team
2. **Configure workspace settings** (data retention, permissions)
3. **Add team members** to workspaces via Fabric portal
4. **Develop data pipelines** using notebooks and dataflows
5. **Set up deployment pipelines** for TEST/PROD promotion
6. **Configure monitoring** (Application Insights, Log Analytics)
7. **Document data contracts** in descriptor YAML files

---

## 📚 Additional Resources

- **Main Documentation**: `documentation/WORKSPACE_TEMPLATING_GUIDE.md`
- **Live Behavior Details**: `documentation/LIVE_FABRIC_RUN_GUIDE.md`
- **Quality Improvements**: `documentation/IMPROVEMENTS_IMPLEMENTATION_SUMMARY.md`
- **CLI Reference**: `FABRIC_CLI_QUICKREF.md`
- **API Documentation**: https://learn.microsoft.com/fabric/rest-api/

---

## ✅ Success Criteria

You'll know the execution was successful when:

- ✅ Script completes without errors
- ✅ Workspace visible in Fabric portal
- ✅ Git integration configured in workspace settings
- ✅ Notebooks/directories appear after Git sync
- ✅ Registry file updated with workspace IDs
- ✅ Audit log created in `.onboarding_logs/`
- ✅ CI/CD tests pass (9/9 tests) ✨

---

**Questions or Issues?**  
Check `documentation/LIVE_FABRIC_RUN_GUIDE.md` for detailed API behavior and troubleshooting.

**Ready for Production?** ✅  
All quality improvements implemented. Security hardened. Tests passing. Go for it! 🚀
