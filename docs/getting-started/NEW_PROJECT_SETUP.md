# Setting Up Fabric CI/CD Framework for Your Organization

**Complete guide for customizing this framework for your organization**

---

## 📋 Overview

This Microsoft Fabric CI/CD framework is designed as a **reusable template** that can be customized for any organization. This guide walks you through the setup process, from cloning the repository to running your first workspace automation.

**Time to Complete:** 15-30 minutes  
**Prerequisites:** Python 3.8+, Git, Azure subscription with Fabric access

---

## 🎯 What You'll Configure

The framework requires configuration in **two main files**:

1. **`project.config.json`** - Organization-specific settings
   - Organization name and project prefix
   - Naming patterns for all resources
   - Environment definitions (dev/test/prod)
   - Git repository details

2. **`.env`** - Credentials and secrets
   - Azure Service Principal credentials
   - GitHub/Azure DevOps tokens
   - Fabric capacity IDs
   - Contact email addresses

---

## 🚀 Setup Methods

### Method 1: Interactive Wizard (Recommended)

The easiest way to get started is using the interactive setup wizard:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO

# 2. Create Python virtual environment
python -m venv fabric-env
source fabric-env/bin/activate  # On Windows: fabric-env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the initialization wizard
python init_new_project.py
```

The wizard will prompt you for:
- Organization name (e.g., "Contoso Corporation")
- Project prefix (e.g., "contoso" - used in all resource names)
- Contact email addresses
- Git repository details

**What it generates:**
- ✅ `project.config.json` (from template)
- ✅ `.env` (from .env.example with your values)
- ✅ Validates setup

**Next step:** Edit `.env` to add your Azure credentials (see step 3 below)

---

### Method 2: Manual Configuration

If you prefer manual control or need to understand the details:

#### Step 1: Copy Template Files

```bash
# Copy configuration template
cp project.config.template.json project.config.json

# Copy environment template
cp .env.example .env
```

#### Step 2: Edit project.config.json

Open `project.config.json` and update these sections:

```json
{
  "project": {
    "name": "your-company-fabric-cicd",
    "prefix": "yourco",              // Used in all resource names
    "description": "Fabric CI/CD for Your Company",
    "organization": "Your Company Inc"
  },
  // ... rest stays the same (uses environment variables)
}
```

**Key fields to update:**
- `project.name`: Your project name
- `project.prefix`: Short prefix (3-20 chars, lowercase, hyphens OK)
  - Examples: "contoso", "acme", "northwind"
  - Used as: `{prefix}-analytics-dev` → `contoso-analytics-dev`
- `project.organization`: Your organization name

**Don't modify:**
- `naming_patterns`: Already parameterized with `{prefix}`
- `azure`: Uses environment variables (`${AZURE_TENANT_ID}`)
- `github`: Uses environment variables
- `git_integration`: Uses environment variables

#### Step 3: Configure .env File

Open `.env` and update these sections:

**Required - Azure Authentication:**
```bash
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_CLIENT_SECRET=your-service-principal-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-azure-subscription-id
```

**Required - Fabric Configuration:**
```bash
FABRIC_CAPACITY_ID=your-fabric-capacity-id
```
Get this from: Fabric Portal → Settings → Admin Portal → Capacity Settings

**Required - Git Integration:**
```bash
GITHUB_TOKEN=ghp_your-personal-access-token
GITHUB_ORGANIZATION=your-github-org
GITHUB_REPOSITORY=your-repo-name
```

**Required - Contact Emails:**
```bash
DATA_OWNER_EMAIL=data-team@yourcompany.com
TECHNICAL_LEAD_EMAIL=tech-lead@yourcompany.com
DEVOPS_LEAD_EMAIL=devops@yourcompany.com
```

**Optional but Recommended:**
```bash
POWERBI_WORKSPACE_ID=your-powerbi-workspace-id
PURVIEW_ACCOUNT_NAME=your-purview-account
```

---

## 🔐 Setting Up Azure Service Principal

If you don't have a Service Principal yet:

### Create Service Principal

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac \
  --name "fabric-cicd-automation" \
  --role "Contributor" \
  --scopes /subscriptions/{subscription-id}
```

**Output:**
```json
{
  "appId": "12345678-1234-1234-1234-123456789012",
  "displayName": "fabric-cicd-automation",
  "password": "your-secret-here",
  "tenant": "87654321-4321-4321-4321-210987654321"
}
```

**Add to .env:**
```bash
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your-secret-here
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
```

### Grant Fabric Permissions

The Service Principal needs these permissions:

1. **Fabric Capacity Admin** (for creating workspaces)
2. **Power BI Admin** or **Workspace Admin** (for managing items)

**Grant via Fabric Portal:**
1. Go to Fabric Admin Portal
2. Settings → Capacity settings
3. Add your Service Principal as Capacity Admin

---

## ✅ Validate Your Setup

### Run Validation Script

```bash
python setup/init_project_config.py --validate
```

**Expected output:**
```
✓ project.config.json exists and is valid
✓ Environment variables loaded successfully
✓ Azure authentication configured
✓ Git repository configured
✓ All required sections present
```

### Run Preflight Check

```bash
./setup/preflight_check.sh
```

This validates:
- ✅ Python environment
- ✅ Required packages installed
- ✅ Azure credentials valid
- ✅ Fabric capacity accessible
- ✅ Git repository accessible

---

## 🎯 Test Your Configuration

### Create Your First Workspace

```bash
# Activate virtual environment
source fabric-env/bin/activate

# Create a development workspace
python ops/scripts/manage_workspaces.py create \
  --project analytics \
  --environment dev

# Expected workspace name: {your-prefix}-analytics-dev
```

**Success indicators:**
- ✅ Workspace created in Fabric portal
- ✅ Named according to your prefix: `{prefix}-analytics-dev`
- ✅ Audit log created in `audit/audit_trail.jsonl`

### List Your Workspaces

```bash
python ops/scripts/manage_workspaces.py list
```

---

## 📁 Understanding the Configuration Files

### project.config.json Structure

```json
{
  "project": {
    // Your organization details
    "name": "yourco-fabric-cicd",
    "prefix": "yourco",
    "organization": "Your Company"
  },
  "naming_patterns": {
    // These use {prefix} automatically
    "workspace": "{prefix}-{name}-{environment}",
    "lakehouse": "{prefix_upper}_Lakehouse_{environment_title}"
  },
  "azure": {
    // Uses environment variables - no changes needed
    "tenant_id": "${AZURE_TENANT_ID}"
  },
  "environments": {
    // Define your environments
    "dev": { "auto_deploy": true },
    "test": { "requires_approval": true },
    "prod": { "requires_approval": true }
  }
}
```

### Environment Variables (.env)

**Pattern:** All credentials and instance-specific values go in `.env`
- ✅ **DO commit:** `project.config.template.json`, `.env.example`
- ❌ **DON'T commit:** `project.config.json`, `.env`

The `.gitignore` is already configured to protect these files.

---

## 🔄 Making This Your Own Repository

### Fork or Clone Approach

**Option A: Fork this repository** (if public)
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-ORG/fabric-cicd.git
cd fabric-cicd
```

**Option B: Clone and re-initialize** (for private use)
```bash
# Clone this repo
git clone https://github.com/ORIGINAL-ORG/fabric-cicd.git my-fabric-cicd
cd my-fabric-cicd

# Remove original git history
rm -rf .git

# Initialize as new repository
git init
git add .
git commit -m "Initial commit: Fabric CI/CD framework for [Your Org]"

# Add your remote
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

### Customize for Your Organization

After setup:

1. **Update README.md** with your organization name
2. **Customize naming_standards.yaml** for your naming conventions
3. **Add organization-specific scenarios** in `scenarios/`
4. **Configure data governance** rules in `governance/`

---

## 🎓 Next Steps

### 1. Explore Scenarios

```bash
cd scenarios/
cat README.md
```

**Available scenarios:**
- `feature-branch-workflow/` - Automated workspace creation for feature branches
- `config-driven-workspace/` - Enterprise workspace provisioning
- `domain-workspace/` - Domain-driven workspace design

### 2. Read Key Documentation

- **Quick Start:** `docs/getting-started/QUICKSTART.md`
- **Provisioning Guide:** `docs/guides/WORKSPACE_PROVISIONING_GUIDE.md`
- **Implementation Guide:** `docs/guides/IMPLEMENTATION_GUIDE.md`

### 3. Configure Git Integration

If you want automatic Git sync for workspaces:

```bash
# Update .env with Git details
GIT_ORGANIZATION="your-org"
GIT_REPOSITORY="your-repo"
GIT_PROJECT="your-repo"  # For GitHub, same as repo

# Enable in project.config.json
"git_integration": {
  "enabled": true,
  "auto_connect_workspaces": true
}
```

### 4. Set Up Naming Standards

Review and customize `naming_standards.yaml`:

```bash
# Edit naming patterns
nano naming_standards.yaml

# Validate items against standards
python ops/scripts/utilities/naming_validator.py validate --workspace-id {id}
```

---

## 🆘 Troubleshooting

### Issue: "project.config.json not found"

**Solution:**
```bash
# Make sure you're in the repository root
pwd  # Should show: /path/to/fabric-cicd

# Copy template
cp project.config.template.json project.config.json
```

### Issue: "Missing required Azure credentials"

**Solution:**
1. Check `.env` file exists: `ls -la .env`
2. Verify values are set (not placeholders)
3. Load environment: `source .env` or `export $(cat .env | xargs)`

### Issue: "Failed to create workspace - 403 Forbidden"

**Causes:**
- Service Principal not added to Fabric capacity
- Insufficient permissions

**Solution:**
1. Add SP to capacity in Fabric Admin Portal
2. Grant "Workspace Admin" or "Capacity Admin" role
3. Wait 5-10 minutes for permissions to propagate

### Issue: Workspace names not using my prefix

**Solution:**
```bash
# Verify project.config.json has your prefix
cat project.config.json | grep prefix

# Should show:
# "prefix": "yourco",

# Regenerate config if needed
python init_new_project.py
```

---

## 📚 Additional Resources

### Documentation
- **Architecture:** `scenarios/shared/ARCHITECTURE.md`
- **User Management:** `docs/guides/BULK_USER_QUICKSTART.md`
- **Feature Summary:** `docs/development-maintenance/FEATURE_SUMMARY.md`

### Example Configurations
- **Sample Product Descriptor:** `scenarios/feature-branch-workflow/product_descriptor.yaml`
- **Naming Standards:** `naming_standards.yaml`
- **Project Config Template:** `project.config.template.json`

### Support
- **Issues:** Check existing issues or create new one
- **Discussions:** Use repository discussions for questions
- **Documentation:** Browse `docs/` directory

---

## ✅ Setup Checklist

Use this checklist to ensure complete setup:

- [ ] Repository cloned
- [ ] Python virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `project.config.json` created and customized
- [ ] `.env` file created with Azure credentials
- [ ] Service Principal created and configured
- [ ] Fabric capacity ID obtained and added to `.env`
- [ ] GitHub/Git credentials added to `.env`
- [ ] Configuration validated (`python setup/init_project_config.py --validate`)
- [ ] Preflight check passed (`./setup/preflight_check.sh`)
- [ ] Test workspace created successfully
- [ ] Git repository initialized (if using your own repo)
- [ ] Documentation reviewed

---

## 🎉 You're All Set!

Your Fabric CI/CD framework is now configured and ready to use!

**What you can do now:**
- ✅ Create workspaces automatically
- ✅ Enforce naming standards
- ✅ Sync workspaces with Git
- ✅ Manage users and permissions
- ✅ Deploy across environments
- ✅ Track all changes in audit logs

**Start building:** `python ops/scripts/manage_workspaces.py create --project {name} --environment dev`

Happy automating! 🚀
