# 🎯 Framework Template - Quick Reference

**This is a reusable template for Microsoft Fabric CI/CD automation**

---

## ⚡ Quick Start

### For New Organizations

```bash
# 1. Clone this repository
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO

# 2. Run initialization wizard
python init_new_project.py
```

The wizard will configure the framework for your organization in minutes!

### What Gets Configured

| File | Purpose | Action |
|------|---------|--------|
| `project.config.json` | Organization settings, naming patterns | Generated from template |
| `.env` | Azure credentials, Git tokens | Created with your values |
| `naming_standards.yaml` | Naming conventions | Review and customize |

---

## 📋 Required Information

Have these ready before running the wizard:

### Organization Details
- Organization name (e.g., "Contoso Corporation")
- Project prefix (e.g., "contoso" - used in all resource names)
- Contact email addresses

### Azure Credentials
- Service Principal Client ID
- Service Principal Secret
- Azure Tenant ID
- Azure Subscription ID
- Fabric Capacity ID

### Git Configuration
- GitHub/Azure DevOps organization
- Repository name
- Personal Access Token (PAT)

---

## 📁 Template Files

### Do NOT Modify (Committed to Git)
- ✅ `project.config.template.json` - Configuration template
- ✅ `.env.example` - Environment variables template
- ✅ `naming_standards.yaml` - Naming conventions
- ✅ All Python scripts and documentation

### Generated for Your Organization (NOT Committed)
- ⚠️ `project.config.json` - Your actual configuration
- ⚠️ `.env` - Your actual credentials

The `.gitignore` file is already configured to protect generated files.

---

## 🎓 Full Documentation

See [docs/getting-started/NEW_PROJECT_SETUP.md](docs/getting-started/NEW_PROJECT_SETUP.md) for:
- Detailed setup instructions
- Manual configuration steps
- Azure Service Principal setup
- Troubleshooting guide
- Validation checklist

---

## 🚀 After Setup

Once configured, you can:

```bash
# Create workspaces
python ops/scripts/manage_workspaces.py create --project analytics --environment dev

# Run scenarios
cd scenarios/feature-branch-workflow/
python test_feature_workflow.py

# Validate naming
python ops/scripts/utilities/naming_validator.py validate --workspace-id {id}
```

---

## ❓ Need Help?

- **Setup Guide:** [docs/getting-started/NEW_PROJECT_SETUP.md](docs/getting-started/NEW_PROJECT_SETUP.md)
- **Quick Start:** [docs/getting-started/QUICKSTART.md](docs/getting-started/QUICKSTART.md)
- **Documentation Index:** [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)

---

**Ready to get started?** Run `python init_new_project.py` now! 🎉
