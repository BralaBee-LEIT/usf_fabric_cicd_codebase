# Microsoft Fabric CI/CD Enterprise Solution

**A production-ready, reusable CI/CD framework for Microsoft Fabric** - Complete with data governance, quality validation, and multi-environment deployment capabilities.

> **🎯 Framework Template:** This is a reusable framework that can be customized for any organization. Run `python init_new_project.py` to configure it for your organization in minutes!

> **📝 Update (Oct 24, 2025):** Framework now supports Trial capacity (FTL64) for item creation! Configure `capacity_id` in scenario YAML files (e.g., `product_config.yaml`). Successfully validated with 3 Lakehouses + 3 Notebooks created via API. All scenarios tested and working. See [scenarios/SCENARIO_TEST_REPORT.md](scenarios/SCENARIO_TEST_REPORT.md) for details.

## 🚀 Quick Start for New Organizations

### Option 1: Interactive Setup (Recommended)
```bash
# Clone this repository
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO

# Run initialization wizard
python init_new_project.py
```

The wizard will:
- ✅ Collect your organization details
- ✅ Generate `project.config.json` from template
- ✅ Create customized `.env` file
- ✅ Validate setup

### Option 2: Manual Setup
```bash
# 1. Copy template files
cp project.config.template.json project.config.json
cp .env.example .env

# 2. Edit project.config.json with your organization details
# 3. Edit .env with your Azure credentials

# 4. Validate configuration
python setup/init_project_config.py --validate
```

See [docs/getting-started/NEW_PROJECT_SETUP.md](docs/getting-started/NEW_PROJECT_SETUP.md) for detailed instructions.

## ✨ New Features (v2.0)

### 🔄 Automated Git Integration
- **Auto-connect workspaces to Git** repositories during provisioning
- Support for GitHub and Azure DevOps
- Bidirectional sync (commit to Git, update from Git)
- Configurable branch patterns and directory structures

### ✅ Naming Standards Enforcement
- **Automatic validation** of Fabric item names
- Medallion architecture support (BRONZE/SILVER/GOLD)
- Ticket-based naming (e.g., JIRA-12345_ProjectName_Type)
- Sequential notebook numbering (01_Ingestion, 02_Transform, etc.)
- Auto-fix suggestions for non-compliant names

### 📊 Centralized Audit Logging
- **Complete audit trail** of all operations (JSONL format)
- Git context capture (commit hash, branch, user)
- Compliance reporting and analytics
- Event filtering by workspace, date range, event type

See [docs/guides/IMPLEMENTATION_GUIDE.md](docs/guides/IMPLEMENTATION_GUIDE.md) for detailed usage.

## 🚀 Quick Start

**See [docs/getting-started/QUICKSTART.md](docs/getting-started/QUICKSTART.md) for detailed setup instructions**

### 5-Minute Setup
```bash
# 1. Create virtual environment
python -m venv fabric-env && source fabric-env/bin/activate

# 2. Install dependencies
pip install -r ops/requirements.txt
pip install -r requirements-test.txt  # For testing (optional)

# 3. Configure environment
cp .env.example .env
# Edit .env with your Azure/GitHub credentials

# 4. Run preflight check
./setup/preflight_check.sh

# 5. Initialize project
python setup/init_project_config.py

# 6. Test validation
python tests/validate_solution.py

# 7. Run unit tests (optional)
pytest tests/ -v
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
├── tests/                # Validation and unit tests
│   ├── validate_solution.py
│   ├── test_workspace_management.sh
│   ├── test_audit_logger.py           # NEW: Audit logging tests
│   ├── test_fabric_git_connector.py   # NEW: Git integration tests
│   └── test_item_naming_validator.py  # NEW: Naming validation tests
├── tools/                # Operational utilities
│   ├── fabric-cli.sh
│   └── bulk_delete_workspaces.py
├── scenarios/            # Workspace provisioning scenarios
│   ├── domain-workspace/
│   ├── leit-ricoh-setup/
│   ├── feature-branch-workflow/       # NEW: Feature branch workflow
│   └── shared/
├── ops/                  # Core operations (scripts, utilities)
│   ├── scripts/
│   │   ├── onboard_data_product.py   # Enhanced with Git & audit logging
│   │   └── utilities/
│   │       ├── fabric_git_connector.py      # NEW: Git integration
│   │       ├── item_naming_validator.py     # NEW: Naming validation
│   │       ├── audit_logger.py              # NEW: Audit logging
│   │       ├── fabric_item_manager.py       # Enhanced with validation
│   │       └── workspace_manager.py         # Enhanced with audit logging
├── docs/                 # Comprehensive documentation
├── config/               # Configuration files
├── governance/           # Data governance rules
├── audit/                # NEW: Audit trail logs (JSONL)
└── naming_standards.yaml # NEW: Naming pattern configuration
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
- **NEW:** Enabling Git integration automation
- **NEW:** Configuring naming validation standards

**When NOT required:**
- Using `scenarios/domain-workspace/` or `scenarios/leit-ricoh-setup/`
- Simple workspace creation with explicit names
- Quick prototyping or testing

**Initialize when needed:**
```bash
python setup/init_project_config.py
```

This creates `project.config.json` with naming patterns and Git integration:
```json
{
  "naming_patterns": {
    "workspace": "{prefix}-{name}-{environment}"
  },
  "git_integration": {
    "enabled": true,
    "provider": "GitHub",
    "auto_connect_workspaces": true,
    "default_branch": "main"
  }
}
```

**See:** [docs/guides/IMPLEMENTATION_GUIDE.md](docs/guides/IMPLEMENTATION_GUIDE.md) for Git integration details

### `naming_standards.yaml` - **NEW**
Defines naming patterns for Fabric items (Lakehouse, Notebook, Pipeline, etc.).

**Features:**
- Medallion architecture patterns (BRONZE/SILVER/GOLD)
- Sequential notebook numbering (01-99)
- Ticket-based naming (JIRA-12345_ProjectName_Type)
- Reserved word validation
- Max length enforcement

**Usage:**
Validation happens automatically when creating items via `FabricItemManager` (if enabled).

**See:** [scenarios/README.md](scenarios/README.md) for workflow comparison

## 🔀 Two Workflow Approaches

This repository supports two distinct workspace provisioning approaches:

### 1. Config-Driven (Enterprise)
- **Uses:** `project.config.json` naming patterns
### Naming Pattern Examples

- **Pattern:** `{prefix}-{project}-{environment}`
- **Example:** `--project analytics --environment dev` → `{your-prefix}-analytics-dev`
- **Configured in:** `project.config.json` (naming_patterns section)
- **Best for:** Enterprise environments, standardized naming, governance
- **Scenario:** `scenarios/config-driven-workspace/`

### 2. Direct-Name (Simple)
- **Uses:** Explicit workspace names you provide
- **Example:** `--workspace-name "analytics-dev"` → `analytics-dev`
- **Best for:** Simple setups, full control, quick prototyping
- **Scenarios:** `scenarios/domain-workspace/`, `scenarios/leit-ricoh-setup/`

**See:** [scenarios/README.md](scenarios/README.md) for detailed comparison

## 🔧 New Utilities (v2.0)

### FabricGitConnector
Automates Git integration for Fabric workspaces.

```python
from utilities.fabric_git_connector import get_git_connector

connector = get_git_connector()
connector.initialize_git_connection(
    workspace_id="ws-123",
    git_provider_type="GitHub",
    organization_name="my-org",
    repository_name="my-repo",
    branch_name="main",
    directory_path="/data_products/my_product"
)
```

**Features:**
- Initialize Git connection (GitHub/Azure DevOps)
- Commit workspace items to Git
- Update workspace from Git (pull)
- Bidirectional sync with conflict resolution
- Disconnect Git integration

### ItemNamingValidator
Enforces naming standards for all Fabric items.

```python
from utilities.item_naming_validator import validate_item_name

result = validate_item_name(
    item_name="BRONZE_CustomerData_Lakehouse",
    item_type="Lakehouse"
)

if not result.is_valid:
    print(f"Errors: {result.errors}")
    print(f"Suggestions: {result.suggestions}")
```

**Supported Patterns:**
- Medallion architecture: `BRONZE_*`, `SILVER_*`, `GOLD_*`
- Sequential notebooks: `01_DataIngestion_Notebook`
- Ticket-based: `JIRA12345_ProjectName_Type`
- Environment suffixes: `_dev`, `_test`, `_prod`

### AuditLogger
Centralized audit trail for compliance and troubleshooting.

```python
from utilities.audit_logger import get_audit_logger

logger = get_audit_logger()
logger.log_workspace_creation(
    workspace_id="ws-123",
    workspace_name="My Product [DEV]",
    product_id="my_product",
    environment="dev"
)

# Generate compliance report
report = logger.generate_compliance_report(
    start_date="2025-01-01",
    end_date="2025-12-31"
)
```

**Event Types:**
- Workspace operations (created, updated, deleted)
- Item operations (created, updated, deleted)
- Git operations (connected, committed, updated, disconnected)
- User operations (added, removed, role_changed)
- Deployment operations (started, completed, failed)
- Validation operations (passed, failed)

**Audit Log Format:** JSONL (`audit/audit_trail.jsonl`)

See [docs/guides/IMPLEMENTATION_GUIDE.md](docs/guides/IMPLEMENTATION_GUIDE.md) for complete API reference.

## 📚 Documentation

- **[docs/guides/IMPLEMENTATION_GUIDE.md](docs/guides/IMPLEMENTATION_GUIDE.md)** - Complete implementation guide for new features
- **[docs/development-maintenance/FEATURE_SUMMARY.md](docs/development-maintenance/FEATURE_SUMMARY.md)** - Feature overview and compliance impact
- **[docs/guides/WORKSPACE_PROVISIONING_GUIDE.md](docs/guides/WORKSPACE_PROVISIONING_GUIDE.md)** - Workspace provisioning reference
- **[scenarios/README.md](scenarios/README.md)** - Workflow comparison and examples
- **[docs/getting-started/QUICKSTART.md](docs/getting-started/QUICKSTART.md)** - Quick start guide

## 🧪 Testing

### Run Unit Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_audit_logger.py -v

# Run with coverage
pytest tests/ --cov=ops/scripts/utilities --cov-report=html
```

### Test Coverage
- **42 unit tests** across 3 test files
- All tests use mocks (no real Fabric API calls)
- Tests for Git integration, naming validation, audit logging

## Notes
- Scripts under `ops/scripts/utilities/*` are placeholders: integrate with real Fabric, Purview, and Power BI REST APIs.
- Add your notebooks, SQL, and dataflows under `data/` and BI assets under `bi/`.
