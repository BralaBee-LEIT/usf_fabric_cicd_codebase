# Fabric CLI - Quick Reference Guide# Fabric CLI - Quick Reference Card



**Version:** 2.0 (Enhanced CLI)  **CLI Location:** `./tools/fabric-cli.sh` (in the `tools/` directory)

**CLI Location:** `./tools/fabric-cli-enhanced.sh`  

**Last Updated:** October 28, 2025## 🚀 Super Short Commands



> 📘 **Note:** This guide covers the enhanced CLI that exposes **100% of framework functionality** (14 scripts, 10 categories, 37+ commands). For comprehensive details, see [`CLI_ENHANCEMENT_SUMMARY.md`](../../CLI_ENHANCEMENT_SUMMARY.md) and [`CLI_COMPREHENSIVE_TESTING.md`](../../CLI_COMPREHENSIVE_TESTING.md).### Workspace Operations

```bash

---./tools/fabric-cli.sh ls                    # List all workspaces

./tools/fabric-cli.sh lsd                   # List with details

## 🚀 Quick Start./tools/fabric-cli.sh create my-ws -e dev   # Create dev workspace

./tools/fabric-cli.sh get WORKSPACE_ID      # Get workspace info

### Get Help./tools/fabric-cli.sh delete WORKSPACE_ID   # Delete workspace

```bash```

./tools/fabric-cli-enhanced.sh help                 # Main help menu

./tools/fabric-cli-enhanced.sh help workspace       # Category-specific help### Environment Setup

./tools/fabric-cli-enhanced.sh help git             # Git commands help```bash

```./tools/fabric-cli.sh create-set analytics  # Create dev/test/prod at once

```

### Shortcuts

```bash### User Management

./tools/fabric-cli-enhanced.sh ls                   # Quick workspace list```bash

./tools/fabric-cli-enhanced.sh lsd                  # Detailed workspace list# Add user as Admin

```./tools/fabric-cli.sh add-user WORKSPACE_ID user@example.com --role Admin



---# Add user as Member

./tools/fabric-cli.sh add-user WORKSPACE_ID user@example.com --role Member

## 📁 1. Workspace Management

# List users

### List & Query./tools/fabric-cli.sh list-users WORKSPACE_ID

```bash

# List all workspaces# Remove user

./tools/fabric-cli-enhanced.sh workspace list./tools/fabric-cli.sh remove-user WORKSPACE_ID USER_ID

```

# List with details

./tools/fabric-cli-enhanced.sh workspace list --details### Bulk Operations

```bash

# Get specific workspace# Delete multiple workspaces from file

./tools/fabric-cli-enhanced.sh workspace get WORKSPACE_ID./tools/fabric-cli.sh delete-bulk --file workspaces.txt

```

# Delete all in dev environment

### Create./tools/fabric-cli.sh delete-all -e dev

```bash```

# Create workspace (dev/test/prod)

./tools/fabric-cli-enhanced.sh workspace create my-workspace -e dev---



# Create dev/test/prod set at once## 📋 Your Current Workspaces

./tools/fabric-cli-enhanced.sh workspace create-set analytics

```| Environment | Name | ID |

|-------------|------|-----|

### Delete| Dev | `usf-fabric-fabric-dev` | `205bdcad-cf08-4785-bcf2-1f656e4599a7` |

```bash| Test | `usf-fabric-fabric-test` | `67333397-e772-4269-baf0-34acdd1b2ac1` |

# Delete single workspace| Prod | `usf-fabric-fabric-prod` | `6a0a271c-8aac-4b19-a660-edb12c8e16c8` |

./tools/fabric-cli-enhanced.sh workspace delete WORKSPACE_ID

---

# Delete multiple from file

./tools/fabric-cli-enhanced.sh workspace delete-bulk --file workspaces.txt## 💡 Common Workflows



# Delete all in environment (use with caution!)### Add Team Member to All Environments

./tools/fabric-cli-enhanced.sh workspace delete-all -e dev```bash

```# Dev

./tools/fabric-cli.sh add-user 205bdcad-cf08-4785-bcf2-1f656e4599a7 dev@example.com --role Member

---

# Test

## 👥 2. User Management./tools/fabric-cli.sh add-user 67333397-e772-4269-baf0-34acdd1b2ac1 dev@example.com --role Member



```bash# Prod (Admin only)

# Add user with role (Admin/Member/Contributor/Viewer)./tools/fabric-cli.sh add-user 6a0a271c-8aac-4b19-a660-edb12c8e16c8 admin@example.com --role Admin

./tools/fabric-cli-enhanced.sh user add WORKSPACE_ID user@example.com --role Admin```



# List users in workspace### Create New Project Workspaces

./tools/fabric-cli-enhanced.sh user list WORKSPACE_ID```bash

./tools/fabric-cli.sh create-set project-name

# Remove user from workspace```

./tools/fabric-cli-enhanced.sh user remove WORKSPACE_ID USER_ID

```### Check Who Has Access

```bash

**Available Roles:**./tools/fabric-cli.sh list-users 205bdcad-cf08-4785-bcf2-1f656e4599a7

- `Admin` - Full control```

- `Member` - Read/write access

- `Contributor` - Can contribute content---

- `Viewer` - Read-only access

## 🎯 Roles Explained

---

| Role | Permissions |

## 📦 3. Data Product Onboarding|------|-------------|

| **Admin** | Full control - manage workspace, users, and content |

```bash| **Member** | Create and edit content, cannot manage workspace |

# Onboard data product from YAML descriptor| **Contributor** | Edit existing content, cannot create new |

./tools/fabric-cli-enhanced.sh onboard data_products/onboarding/my_product.yaml| **Viewer** | Read-only access |



# Create feature workspace---

./tools/fabric-cli-enhanced.sh onboard descriptor.yaml --feature JIRA-1234

## ⚡ Pro Tips

# Preview without making changes (dry-run)

./tools/fabric-cli-enhanced.sh onboard descriptor.yaml --dry-run1. **Always use shortcuts**: `ls` instead of `list`

2. **Save IDs**: Keep workspace IDs handy for quick access

# Skip specific steps3. **Use variables**: 

./tools/fabric-cli-enhanced.sh onboard descriptor.yaml --skip-git   ```bash

./tools/fabric-cli-enhanced.sh onboard descriptor.yaml --skip-workspaces   DEV_WS="205bdcad-cf08-4785-bcf2-1f656e4599a7"

```   ./tools/fabric-cli.sh get $DEV_WS

   ```

**Descriptor Example:**4. **Check help anytime**: `./fabric-cli.sh help`

```yaml

# data_products/onboarding/sales-analytics.yaml---

name: sales-analytics

display_name: Sales Analytics## 🔧 Troubleshooting

description: Sales data product

team: analytics-team### Command not working?

environments:```bash

  - dev# Make sure it's executable

  - testchmod +x fabric-cli.sh

  - prod

```# Check .env file exists

ls -la .env

---```



## 📝 4. Fabric Items Management### Need to see more info?

```bash

### List Items# Add --details to most commands

```bash./tools/fabric-cli.sh lsd

# List all items in workspace```

./tools/fabric-cli-enhanced.sh items list --workspace dev-workspace

### Want JSON output?

# List specific type```bash

./tools/fabric-cli-enhanced.sh items list --workspace dev-workspace --type Notebook./tools/fabric-cli.sh list --json

./tools/fabric-cli-enhanced.sh items list --workspace dev-workspace --type Lakehouse```

```

---

### Create Items

```bash**Last Updated**: October 16, 2025  

# Create lakehouse**Your Project**: usf-fabric-cicd

./tools/fabric-cli-enhanced.sh items create \
  --workspace dev-workspace \
  --name MyLakehouse \
  --type Lakehouse

# Create notebook
./tools/fabric-cli-enhanced.sh items create \
  --workspace dev-workspace \
  --name MyNotebook \
  --type Notebook
```

### Delete Items
```bash
# Delete single item
./tools/fabric-cli-enhanced.sh items delete \
  --workspace dev-workspace \
  --name OldNotebook

# Bulk delete
./tools/fabric-cli-enhanced.sh items bulk-delete \
  --workspace dev-workspace \
  --type Notebook \
  --pattern "test-*"
```

**Supported Item Types:**
- `Lakehouse` - Data storage
- `Notebook` - Code notebooks
- `DataPipeline` - ETL pipelines
- `Report` - Power BI reports
- `SemanticModel` - Data models

---

## 🔄 5. Git Integration

### Initialize Git
```bash
# Connect workspace to Git
./tools/fabric-cli-enhanced.sh git init \
  --workspace dev-workspace \
  --git-provider GitHub \
  --organization myorg \
  --repository myrepo
```

### Sync Operations
```bash
# Pull from Git to workspace
./tools/fabric-cli-enhanced.sh git sync-to-workspace --workspace dev-workspace

# Push from workspace to Git
./tools/fabric-cli-enhanced.sh git sync-to-git \
  --workspace dev-workspace \
  --commit-message "Update notebooks"

# Check sync status
./tools/fabric-cli-enhanced.sh git status --workspace dev-workspace
```

**Supported Git Providers:**
- GitHub
- AzureDevOps

---

## 🚀 6. Deployment

### Deploy from Bundle
```bash
# Deploy ZIP bundle to workspace
./tools/fabric-cli-enhanced.sh deploy \
  --workspace prod-workspace \
  --bundle deploy-bundle.zip
```

### Deploy from Git
```bash
# Deploy from Git repository
./tools/fabric-cli-enhanced.sh deploy \
  --workspace prod-workspace \
  --git-repo https://github.com/org/repo
```

### Validation Mode
```bash
# Validate deployment without executing
./tools/fabric-cli-enhanced.sh deploy \
  --workspace staging-workspace \
  --bundle deploy.zip \
  --validate-only
```

**Deployment Modes:**
- `standard` - Normal deployment
- `promote` - Promote across environments
- `validation` - Validate only, no deployment

---

## 🏥 7. Health & Monitoring

```bash
# Run health check
./tools/fabric-cli-enhanced.sh health \
  --workspace dev-workspace \
  -e dev

# Save health report to file
./tools/fabric-cli-enhanced.sh health \
  --workspace prod-workspace \
  -e prod \
  --output-file health-report.json

# Health check with critical failure threshold
./tools/fabric-cli-enhanced.sh health \
  --workspace prod-workspace \
  -e prod \
  --fail-on-critical
```

**Output Formats:**
- `text` - Human-readable
- `json` - Machine-readable

---

## ✅ 8. Data Quality & Governance

### Validate DQ Rules
```bash
# Validate data quality rules
./tools/fabric-cli-enhanced.sh dq validate \
  --rules-dir dq_rules/ \
  --output-format console

# Quiet mode
./tools/fabric-cli-enhanced.sh dq validate --quiet
```

### Run Quality Gate
```bash
# Run quality gate for environment
./tools/fabric-cli-enhanced.sh dq gate --env dev

# With custom threshold profile
./tools/fabric-cli-enhanced.sh dq gate \
  --env prod \
  --threshold-profile strict
```

### Validate Data Contracts
```bash
# Validate contract file
./tools/fabric-cli-enhanced.sh contract validate \
  --file contracts/sales_contract.yaml

# Validate all contracts in directory
./tools/fabric-cli-enhanced.sh contract validate \
  --contracts-dir contracts/ \
  --fail-on-invalid
```

### Validate Artifacts
```bash
# Validate Fabric artifacts
./tools/fabric-cli-enhanced.sh artifacts validate \
  --path workspace_artifacts/ \
  --output-format json
```

---

## 📊 9. Power BI Deployment

```bash
# Deploy Power BI reports
./tools/fabric-cli-enhanced.sh powerbi deploy \
  --pipeline sales-pipeline \
  --stage production
```

---

## 🔍 10. Purview Integration

```bash
# Trigger Purview catalog scan
./tools/fabric-cli-enhanced.sh purview scan --env dev
./tools/fabric-cli-enhanced.sh purview scan --env prod
```

---

## 🎯 Common Workflows

### New Data Product Setup
```bash
# 1. Onboard data product
./tools/fabric-cli-enhanced.sh onboard data_products/onboarding/my_product.yaml

# 2. Initialize Git connection
./tools/fabric-cli-enhanced.sh git init \
  --workspace my-product-dev \
  --git-provider GitHub

# 3. Create lakehouse
./tools/fabric-cli-enhanced.sh items create \
  --workspace my-product-dev \
  --name MyLakehouse \
  --type Lakehouse
```

### Feature Development Workflow
```bash
# 1. Create feature workspace
./tools/fabric-cli-enhanced.sh onboard descriptor.yaml --feature JIRA-1234

# 2. Sync from main workspace
./tools/fabric-cli-enhanced.sh git sync-to-workspace \
  --workspace my-product-feature-JIRA-1234

# 3. After development, push changes
./tools/fabric-cli-enhanced.sh git sync-to-git \
  --workspace my-product-feature-JIRA-1234 \
  --commit-message "JIRA-1234: Add new transformations"
```

### Deployment Pipeline
```bash
# 1. Validate in staging
./tools/fabric-cli-enhanced.sh deploy \
  --workspace staging-ws \
  --bundle deploy.zip \
  --validate-only

# 2. Run health check
./tools/fabric-cli-enhanced.sh health --workspace staging-ws -e test

# 3. Run quality gate
./tools/fabric-cli-enhanced.sh dq gate --env test

# 4. Deploy to production
./tools/fabric-cli-enhanced.sh deploy \
  --workspace prod-ws \
  --bundle deploy.zip \
  --mode promote
```

---

## 📚 Additional Resources

### Comprehensive Documentation
- **[CLI_ENHANCEMENT_SUMMARY.md](../../CLI_ENHANCEMENT_SUMMARY.md)** - Full CLI enhancement details, migration guide, benefits
- **[CLI_COMPREHENSIVE_TESTING.md](../../CLI_COMPREHENSIVE_TESTING.md)** - Complete test results, all 37 commands verified

### Related Documentation
- **[WORKSPACE_MANAGEMENT_QUICKREF.md](../workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md)** - Workspace operations deep dive
- **[USER_STORY_1_IMPLEMENTATION.md](../user-stories/USER_STORY_1_IMPLEMENTATION.md)** - Data product onboarding workflows
- **[DEPLOYMENT_PACKAGE_GUIDE.md](../deployment-cicd/DEPLOYMENT_PACKAGE_GUIDE.md)** - Deployment packaging and strategies

### Legacy Documentation (Archived)
- **Old CLI Reference** → [`docs/archive/cli-legacy-docs/FABRIC_CLI_QUICKREF_OLD.md`](../archive/cli-legacy-docs/FABRIC_CLI_QUICKREF_OLD.md)
- **CLI Path Updates** → [`docs/archive/cli-legacy-docs/CLI_PATH_UPDATE_SUMMARY.md`](../archive/cli-legacy-docs/CLI_PATH_UPDATE_SUMMARY.md)

---

## 🔧 Environment Setup

### Required Environment Variables
```bash
# Azure Authentication
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret

# Git Integration
GIT_ORGANIZATION=your-org
GIT_REPOSITORY=your-repo
GIT_PAT=your-personal-access-token
```

### Verify Setup
```bash
# Run preflight check
./setup/preflight_check.sh

# Should show:
# ✓ Check 1: Python version OK
# ✓ Check 2: Azure CLI installed
# ✓ Check 3: Conda environment activated
# ... (10 checks total)
```

---

## ❓ Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'nbformat'`
```bash
# Solution: Install missing dependency
pip install nbformat==5.10.4
```

**Issue:** `Command not found: ./tools/fabric-cli-enhanced.sh`
```bash
# Solution: Make executable
chmod +x ./tools/fabric-cli-enhanced.sh
```

**Issue:** `Invalid workspace ID`
```bash
# Solution: List workspaces to get correct ID
./tools/fabric-cli-enhanced.sh ls
```

**Issue:** Authentication errors
```bash
# Solution: Verify environment variables are set
echo $AZURE_TENANT_ID
echo $AZURE_CLIENT_ID

# Re-source .env file
set -a && source .env && set +a
```

---

## 💡 Tips & Best Practices

1. **Use `--dry-run` first** - Preview changes before executing
2. **Check help often** - `./tools/fabric-cli-enhanced.sh help <category>`
3. **Use shortcuts** - `ls` and `lsd` for quick workspace checks
4. **JSON output** - Add `--json` flag for programmatic use
5. **Save reports** - Use `--output-file` for health checks and validations

---

**CLI Version:** 2.0 (Enhanced)  
**Coverage:** 100% of framework functionality (14 scripts, 37+ commands)  
**Status:** ✅ Production-ready (all commands tested and verified)
