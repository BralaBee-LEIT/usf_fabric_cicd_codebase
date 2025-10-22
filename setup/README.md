# Setup & Initialization Scripts

Scripts for initial project setup, environment configuration, and workspace provisioning.

## 📁 Scripts

### Project Initialization

**`init_project_config.py`** - Interactive project configuration wizard

Creates `project.config.json` for **config-driven workspace provisioning** with enterprise naming standards.

**⚙️ When to use:**
- Setting up **config-driven-workspace** scenario (standardized enterprise naming)
- Managing multiple environments (dev/test/prod) with consistent patterns
- Enforcing organization-wide naming governance
- Automating workspace provisioning at scale

**❌ When NOT needed:**
- Using **domain-workspace** or **leit-ricoh** scenarios (direct-name approach)
- Simple workspace creation with explicit names
- Quick prototyping or one-off workspaces
- Small teams without formal naming standards

**What it does:**
- Creates `project.config.json` with your settings
- Collects project info (name, prefix, organization)
- Configures naming patterns: `{prefix}-{name}-{environment}`
- Sets up Azure settings (tenant, subscriptions)
- Configures GitHub integration
- Generates environment variables guide

**Usage:**
```bash
python setup/init_project_config.py
```

**What it creates:**
- `project.config.json` - Naming patterns and config (for config-driven scenarios ONLY)
- Updated `.env` template
- Environment variables documentation

**See:** [scenarios/README.md](../scenarios/README.md#two-workflow-approaches) for workflow comparison

---

### Environment Setup

**`preflight_check.sh`** - Pre-flight checklist (10 checks)
- ✅ Conda environment (fabric-cicd)
- ✅ Python version (3.9+)
- ✅ Python dependencies (yaml, msal, requests)
- ✅ .env file exists
- ✅ Azure credentials configured
- ✅ GitHub token (optional)
- ✅ Git repository status
- ✅ File structure integrity
- ✅ Fabric capacity
- ✅ Service principal permissions

**Usage:**
```bash
./setup/preflight_check.sh
```

**`quick_setup.sh`** - Fast environment setup (DEPRECATED)
- ⚠️ Legacy script - use modular setup instead
- Creates conda environment
- Installs dependencies
- Validates Python version

**Usage:**
```bash
./setup/quick_setup.sh
```

⚠️ **Note:** This script is deprecated. Use `./setup/preflight_check.sh` instead.

---

### Workspace Provisioning

**`setup_etl_workspace.sh`** - Complete ETL workspace setup
- Creates ETL Platform [DEV] workspace
- **Phase 1:** Workspace creation
- **Phase 2:** User addition (template provided)
- **Phase 3:** Medallion architecture lakehouses
  - Bronze (raw data)
  - Silver (cleaned data)
  - Gold (business-ready data)

**Usage:**
```bash
./setup/setup_etl_workspace.sh
```

**What it creates:**
- 1 Workspace: ETL Platform [DEV]
- 3 Lakehouses: Bronze, Silver, Gold
- User roles (template - needs customization)

---

## 🚀 Getting Started Workflow

### First-Time Setup

```bash
# 1. Pre-flight check
./setup/preflight_check.sh

# 2. Initialize project config
python setup/init_project_config.py

# 3. Verify setup
./setup/preflight_check.sh
```

### Create ETL Workspace

```bash
# Edit user emails in setup_etl_workspace.sh first!
./setup/setup_etl_workspace.sh
```

---

## 📋 Setup Checklist

- [ ] Conda environment created and activated
- [ ] `.env` file configured with credentials
- [ ] `project.config.json` initialized
- [ ] Preflight checks pass
- [ ] Azure service principal has permissions
- [ ] Fabric capacity available

---

## 🔧 Common Tasks

### "I need to set up the project for the first time"
```bash
./setup/preflight_check.sh
python setup/init_project_config.py
```

### "I want to create a complete ETL environment"
```bash
./setup/setup_etl_workspace.sh
```

### "I need to verify my environment is ready"
```bash
./setup/preflight_check.sh
```

---

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Documentation Index](../docs/DOCUMENTATION_INDEX.md) - Full documentation
- [Diagnostics](../diagnostics/README.md) - Troubleshooting tools
- [Scenarios](../scenarios/README.md) - Workspace scenarios

---

## 💡 Tips

1. **Always run preflight check first** - Catches 90% of setup issues
2. **Customize user emails** - Update setup_etl_workspace.sh before running
3. **Use project config** - Initialize project.config.json for reusability
4. **Environment separation** - Create separate workspaces for dev/test/prod

---

**Location:** `/setup/`  
**Purpose:** Project initialization and environment setup  
**Type:** Setup scripts
