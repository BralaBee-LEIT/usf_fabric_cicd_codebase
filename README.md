# Microsoft Fabric CI/CD Enterprise Solution

**The most robust CI/CD setup for Microsoft Fabric with GitHub** - A production-ready, configurable, and reusable CI/CD framework for Microsoft Fabric with comprehensive data governance, quality validation, and multi-environment deployment capabilities.

## 🚀 Quick Start

**See [docs/getting-started/QUICKSTART.md](docs/getting-started/QUICKSTART.md) for detailed setup instructions**

### 5-Minute Setup
```bash
# 1. Create virtual environment
python -m venv fabric-env && source fabric-env/bin/activate

# 2. Install dependencies
pip install -r ops/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Azure/GitHub credentials

# 4. Run preflight check
./setup/preflight_check.sh

# 5. Initialize project
python setup/init_project_config.py

# 6. Test validation
python tests/validate_solution.py
```

### Alternative Setup (Python venv)
```bash
# Create virtual environment
python3 -m venv fabric-cicd-env
source fabric-cicd-env/bin/activate

# Continue with steps 3-6 above
cp .env.example .env
./setup/preflight_check.sh
python setup/init_project_config.py
python tests/validate_solution.py
```

## 📁 Project Structure

```
usf-fabric-cicd/
├── diagnostics/          # Troubleshooting tools
│   ├── check_graph_permissions.py
│   ├── diagnose_fabric_permissions.py
│   └── diagnose_workspaces.py
├── setup/                # Setup and initialization
│   ├── init_project_config.py
│   ├── preflight_check.sh
│   └── setup_etl_workspace.sh
├── tests/                # Validation and testing
│   ├── validate_solution.py
│   └── test_workspace_management.sh
├── tools/                # Operational utilities
│   ├── fabric-cli.sh
│   └── bulk_delete_workspaces.py
├── scenarios/            # Workspace provisioning scenarios
│   ├── domain-workspace/
│   ├── leit-ricoh-setup/
│   └── shared/
├── ops/                  # Core operations (scripts, utilities)
├── docs/                 # Comprehensive documentation
├── config/               # Configuration files
└── governance/           # Data governance rules
```

## 🛠️ Available Tools

### Operational Tools
- **[fabric-cli.sh](tools/README.md)** - User-friendly CLI wrapper
- **[bulk_delete_workspaces.py](tools/README.md)** - Bulk workspace deletion

### Diagnostics
- **[diagnose_fabric_permissions.py](diagnostics/README.md)** - API permissions checker
- **[diagnose_workspaces.py](diagnostics/README.md)** - Workspace visibility diagnostic

### Setup & Initialization  
- **[preflight_check.sh](setup/README.md)** - Pre-flight checklist (10 checks)
- **[init_project_config.py](setup/README.md)** - Project configuration wizard

### Testing & Validation
- **[validate_solution.py](tests/README.md)** - Comprehensive validation
- **[test_workspace_management.sh](tests/README.md)** - Workspace tests

See folder READMEs for detailed usage instructions.

## ⚙️ Configuration Files

### `.env` - **REQUIRED**
Azure and GitHub credentials. Required for all scenarios.

```bash
# Azure Service Principal
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id

# GitHub (optional)
GITHUB_TOKEN=your-github-token
GITHUB_ORG=your-org
GITHUB_REPO=your-repo
```

### `project.config.json` - **OPTIONAL**
Enterprise naming patterns for config-driven workflows. 

**When required:**
- Using `scenarios/config-driven-workspace/` for enterprise naming standards
- Managing multiple environments (dev/test/prod) with consistency
- Need organization-wide naming governance

**When NOT required:**
- Using `scenarios/domain-workspace/` or `scenarios/leit-ricoh-setup/`
- Simple workspace creation with explicit names
- Quick prototyping or testing

**Initialize when needed:**
```bash
python setup/init_project_config.py
```

This creates `project.config.json` with naming patterns like:
```json
{
  "naming_patterns": {
    "workspace": "{prefix}-{name}-{environment}"
  }
}
```

**See:** [scenarios/README.md](scenarios/README.md) for workflow comparison

## 🔀 Two Workflow Approaches

This repository supports two distinct workspace provisioning approaches:

### 1. Config-Driven (Enterprise)
- **Uses:** `project.config.json` naming patterns
- **Example:** `--project analytics --environment dev` → `usf2-fabric-analytics-dev`
- **Best for:** Enterprise environments, standardized naming, governance
- **Scenario:** `scenarios/config-driven-workspace/`

### 2. Direct-Name (Simple)
- **Uses:** Explicit workspace names you provide
- **Example:** `--workspace-name "analytics-dev"` → `analytics-dev`
- **Best for:** Simple setups, full control, quick prototyping
- **Scenarios:** `scenarios/domain-workspace/`, `scenarios/leit-ricoh-setup/`

**See:** [scenarios/README.md](scenarios/README.md) for detailed comparison

## Notes
- Scripts under `ops/scripts/utilities/*` are placeholders: integrate with real Fabric, Purview, and Power BI REST APIs.
- Add your notebooks, SQL, and dataflows under `data/` and BI assets under `bi/`.
