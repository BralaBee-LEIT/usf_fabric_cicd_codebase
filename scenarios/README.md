# Fabric Workspace Setup Scenarios

This directory contains ready-to-use scenario scripts for setting up complete Microsoft Fabric workspaces with various configurations.

> **⚠️ FRAMEWORK REQUIREMENTS (MANDATORY):**
> 
> **ALL scenarios require these files before execution:**
> 1. ✅ `project.config.json` - Organization naming standards (MANDATORY)
> 2. ✅ `.env` - Azure credentials (MANDATORY)
> 3. ✅ `naming_standards.yaml` - Naming validation rules (MANDATORY)
> 
> **Quick Setup:**
> ```bash
> cp project.config.template.json project.config.json
> cp .env.example .env
> nano project.config.json  # Edit with your org details
> nano .env                 # Edit with your Azure credentials
> python ops/scripts/utilities/framework_validator.py  # Verify setup
> ```
> 
> **Scenarios will fail with helpful error messages if prerequisites are missing.**

## 📁 Directory Structure

```
scenarios/
├── README.md                           # This file
├── automated-deployment/               # Automated end-to-end deployment
│   ├── run_automated_deployment.py
│   ├── product_config.yaml
│   └── README.md
├── comprehensive-demo/                 # 🆕 NEW: Full feature showcase with folders
│   ├── run_comprehensive_demo.py      # Complete demo with intelligent folders
│   ├── comprehensive_demo_config.yaml  # Full-featured configuration
│   ├── example_basic_medallion.yaml   # Simple medallion demo
│   ├── example_ml_lifecycle.yaml      # ML/Data science config
│   ├── example_multi_tenant.yaml      # Departmental multi-tenant
│   └── README.md                      # Comprehensive documentation
├── config-driven-workspace/            # Enterprise config-driven workspace
│   ├── config_driven_workspace.py
│   ├── README.md
│   └── *_setup_log.json               # Execution logs
├── domain-workspace/                   # Domain-based workspace with existing items
│   ├── domain_workspace_with_existing_items.py
│   ├── DOMAIN_WORKSPACE_GUIDE.md
│   ├── DOMAIN_WORKSPACE_QUICKREF.md
│   └── *_setup_log.json               # Execution logs
├── leit-ricoh-setup/                   # LEIT-Ricoh domain setup
│   ├── leit_ricoh_setup.py
│   └── leit_ricoh_setup.sh
├── leit-ricoh-fresh-setup/             # LEIT-Ricoh fresh setup variant
│   └── leit_ricoh_fresh_setup.py
├── feature-branch-workflow/            # Feature branch workspace workflow
│   ├── README.md
│   ├── FEATURE_WORKFLOW_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   ├── WHAT_WAS_MISSING.md
│   ├── product_descriptor.yaml
│   └── test_feature_workflow.py
└── shared/                             # Shared documentation
    ├── ARCHITECTURE.md
    ├── CAPACITY_ASSIGNMENT_GUIDE.md
    ├── CORE_BULK_ADDITION.md
    ├── GROUP_SUPPORT_QUICKREF.md
    ├── GROUP_SUPPORT_SUMMARY.md
    ├── ITEM_CREATION_FIXES.md
    ├── QUICKSTART.md
    ├── SCENARIO_SUMMARY.md
    └── USER_ADDITION_GUIDE.md
```

## 📋 Core Framework Principles (Enforced)

**As of v2.0, the framework enforces these principles across ALL scenarios:**

1. **Standardized Naming** - All workspaces/items follow `project.config.json` patterns
2. **Infrastructure-as-Code** - Declarative YAML configurations for repeatable deployments
3. **Governance & Compliance** - Naming validation via `naming_standards.yaml`
4. **Proper Authentication** - Azure credentials via `.env` file

**What This Means:**
- ❌ No ad-hoc workspace creation without configuration
- ❌ No bypassing organizational naming standards
- ✅ All resources follow governance policies
- ✅ Complete audit trail of all operations

## � Two Workflow Approaches

This repository supports **two distinct approaches** to workspace provisioning. Choose based on your use case:

### Approach 1: Config-Driven (Enterprise) - RECOMMENDED

**📐 Standardized Naming via `project.config.json` (ENFORCED)**

Uses ConfigManager to generate workspace names from organizational patterns. **Now required for ALL scenarios** to ensure governance.

**When to use:**
- ✅ Enterprise deployments with naming standards
- ✅ Multiple environments (dev/test/prod) with consistency
- ✅ Organization-wide governance and compliance
- ✅ Automated, repeatable infrastructure
- ✅ Deployment at scale across teams

**Example:**
```bash
# You provide: project + environment
python config_driven_workspace.py --project analytics --environment dev

# System generates: usf2-fabric-analytics-dev (from config pattern)
```

**Scenario:** `config-driven-workspace/`

---

### Approach 2: Domain-Based (Structured)

**📝 Domain + Environment Pattern (ENFORCED)**

You specify domain name and environment. Framework applies `project.config.json` patterns to ensure consistency.

**⚠️ BREAKING CHANGE (v2.0):** Domain workspace scenario now requires ConfigManager and enforces naming standards.

**When to use:**
- ✅ Domain-oriented architecture
- ✅ Logical grouping by business domain
- ✅ Still needs governance/compliance
- ✅ Multiple environments per domain

**Example:**
```bash
# You provide: domain name + environment
python domain_workspace_with_existing_items.py --domain-name finance --environment dev

# System generates: usf2-fabric-finance-dev (from project.config.json pattern)
```

**Scenarios:** `domain-workspace/`, `leit-ricoh-setup/`, `leit-ricoh-fresh-setup/`

---

### Quick Decision Matrix

| Requirement | Config-Driven | Domain-Based |
|-------------|---------------|--------------|
| Naming standards enforced | ✅ Always | ✅ Always |
| Simple one-off setup | ⚠️ Medium | ✅ Easy |
| Multi-environment consistency | ✅ | ✅ |
| Domain-oriented architecture | ⚠️ Optional | ✅ Core |
| Requires project.config.json | ✅ Required | ✅ Required |
| Requires YAML config | ⚠️ Optional | ⚠️ Optional |
| Setup complexity | Medium | Medium |
| Governance/Compliance | ✅ Always | ✅ Always |
| Best for | Enterprise standard workspaces | Domain-organized workspaces |

**Note:** As of v2.0, BOTH approaches enforce `project.config.json` for naming standards.

---

## �📋 Available Scenarios

### 1. Comprehensive Demo with Folder Management ⭐ 🆕 NEW

**Location:** `comprehensive-demo/`  
**Approach:** Full Feature Showcase 🎯

Complete demonstration of all framework capabilities including intelligent folder placement, medallion architecture, and automated organization.

**Features:**
- ✅ **Intelligent Folder Placement** - Items automatically organized by naming conventions
- ✅ **Medallion Architecture** - Bronze/Silver/Gold layer structure with subfolders
- ✅ **Naming Standards Integration** - Validates item names against naming_standards.yaml
- ✅ **Multiple Demos** - Sales analytics, ML lifecycle, multi-tenant scenarios
- ✅ **Configuration-Driven** - YAML-based scenario definitions
- ✅ **Known API Limitations** - Handles Fabric API folder placement bug gracefully
- ✅ **Complete Audit Trail** - Full logging of all operations

**What's Created:**
- **12 Folders**: 3 root layers (Bronze/Silver/Gold) + 9 subfolders
- **6 Lakehouses**: Organized by naming prefix (BRONZE_*, SILVER_*, GOLD_*)
- **8 Notebooks**: Numbered notebooks (01-09, 10-19, 20-29, 50+) for different stages
- **Intelligent Placement**: Items automatically mapped to appropriate folders

**Usage:**
```bash
# Sales Analytics Demo (recommended)
cd scenarios/comprehensive-demo
python run_sales_analytics_demo.py

# Or use full comprehensive demo
python run_comprehensive_demo.py --scenario sales_analytics_etl
```

**Folder Organization:**
```
Bronze Layer/
  ├── Raw Data/              # BRONZE_* lakehouses, 01-09_* notebooks
  ├── Archive/               # Historical data
  └── External Sources/      # Third-party data
Silver Layer/
  ├── Cleaned/               # SILVER_* lakehouses (cleaned)
  ├── Transformed/           # 10-19_* notebooks
  └── Validated/             # Quality-checked data
Gold Layer/
  ├── Analytics/             # GOLD_* lakehouses, 20-29_* notebooks
  ├── Reports/               # Business reports
  └── Business Metrics/      # KPIs and metrics
```

**⚠️ Known Limitation:**
The Microsoft Fabric API currently has a bug where the `folderId` parameter is accepted but ignored. Items are created at workspace root. See `FOLDER_PLACEMENT_FIX.md` for complete analysis and manual organization steps.

**Documentation:**
- [Comprehensive Demo README](comprehensive-demo/README.md) - Complete guide
- [Folder Placement Fix](../FOLDER_PLACEMENT_FIX.md) - API limitation details
- [Implementation Summary](comprehensive-demo/IMPLEMENTATION_SUMMARY.md) - Technical details
- [Quick Reference](comprehensive-demo/QUICK_REFERENCE.md) - Common commands

---

### 2. Automated Deployment

**Location:** `automated-deployment/`  
**Approach:** Config-Driven ⚙️

Production-ready automated deployment with folder structure support.

**Features:**
- ✅ Folder structure creation (medallion or custom)
- ✅ Automated workspace provisioning
- ✅ YAML-based configuration
- ✅ Dry-run mode for testing
- ✅ Integration with workspace manager

**Usage:**
```bash
cd scenarios/automated-deployment
python run_automated_deployment.py --config product_config.yaml
```

---

### 3. Config-Driven Workspace (Enterprise)

**Location:** `config-driven-workspace/`  
**Approach:** Config-Driven ⚙️

Enterprise workspace provisioning with standardized naming patterns from `project.config.json`.

**Features:**
- ✅ Automated name generation from config patterns
- ✅ Environment-aware settings (dev/test/prod)
- ✅ Organization-wide naming governance
- ✅ Multi-project consistency
- ✅ Lakehouse creation (capacity permitting)
- ✅ User/group configuration
- ✅ Setup logging and audit trail

**Prerequisites:**
```bash
# Initialize config (one-time)
python setup/init_project_config.py
```

**Usage:**
```bash
# Create dev workspace for analytics
python scenarios/config-driven-workspace/config_driven_workspace.py \
  --project analytics \
  --environment dev \
  --skip-user-prompt

# Create prod workspace for sales
python scenarios/config-driven-workspace/config_driven_workspace.py \
  --project sales \
  --environment prod \
  --principals-file config/sales_prod_principals.txt
```

**Generated Names:**
- `--project analytics --environment dev` → `usf2-fabric-analytics-dev`
- `--project sales --environment test` → `usf2-fabric-sales-test`
- `--project finance --environment prod` → `usf2-fabric-finance-prod`

**Documentation:**
- [Config-Driven Workspace Guide](config-driven-workspace/README.md) - Complete setup guide
- [Setup Guide](../setup/README.md) - Initialize `project.config.json`

---

### 2. Domain Workspace with Existing Items

**Location:** `domain-workspace/`  
**Approach:** Direct-Name 📝

Create a domain-based workspace and attach existing lakehouses/warehouses via OneLake shortcuts.

**Features:**
- ✅ Domain-based workspace organization
- ✅ Creates new lakehouse, warehouse, and staging lakehouse
- ✅ Automatic user/group configuration from principals file
- ✅ Interactive mode: prompts to edit template if no principals file
- ✅ Documents OneLake shortcuts for accessing existing items
- ✅ Support for automation via `--skip-user-prompt`

**Usage:**
```bash
# With existing principals file
python3 scenarios/domain-workspace/domain_workspace_with_existing_items.py \
  --workspace-name "finance-ops" \
  --domain-name "finance" \
  --principals-file "config/finance-ops_principals.txt"

# Interactive mode (creates template)
python3 scenarios/domain-workspace/domain_workspace_with_existing_items.py \
  --workspace-name "marketing-ops" \
  --domain-name "marketing"
```

**Documentation:**
- [Domain Workspace Guide](domain-workspace/DOMAIN_WORKSPACE_GUIDE.md) - Comprehensive setup guide
- [Quick Reference](domain-workspace/DOMAIN_WORKSPACE_QUICKREF.md) - Common commands and patterns

---

### 3. LEIT-Ricoh Domain Setup

**Location:** `leit-ricoh-setup/`  
**Approach:** Direct-Name 📝

Complete workspace setup for the LEIT-Ricoh domain with full analytics infrastructure.

**Files:**
- `leit_ricoh_setup.sh` - Bash version
- `leit_ricoh_setup.py` - Python version (recommended)

**What's Created:**

| Category | Item | Type | Description |
|----------|------|------|-------------|
| **Storage** | RicohDataLakehouse | Lakehouse | Primary data storage |
| | RicohAnalyticsWarehouse | Warehouse | Analytics warehouse |
| **Processing** | 01_DataIngestion | Notebook | Data ingestion |
| | 02_DataTransformation | Notebook | Data transformation |
| | 03_DataValidation | Notebook | Data quality checks |
| **Analytics** | RicohDataPipeline | Pipeline | Orchestration |
| | RicohSemanticModel | Semantic Model | Business layer |
| | RicohExecutiveDashboard | Report | Executive dashboard |

**Users (to be configured):**
- 1 Admin
- 2 Members (Data Engineers)
- 1 Contributor (Data Analyst)
- 2 Viewers (Business Users)

**Total:** 8 Fabric items + 6 user roles

**Usage:**

```bash
# Python version (recommended)
python3 scenarios/leit-ricoh-setup/leit_ricoh_setup.py

# Bash version
./scenarios/leit-ricoh-setup/leit_ricoh_setup.sh
```

---

### 4. LEIT-Ricoh Fresh Setup

**Location:** `leit-ricoh-fresh-setup/`  
**Approach:** Direct-Name 📝

Fresh variant of the LEIT-Ricoh setup with additional configurations.

**Usage:**
```bash
python3 scenarios/leit-ricoh-fresh-setup/leit_ricoh_fresh_setup.py
```

---

### 5. Feature Branch Workflow ⭐ NEW

**Location:** `feature-branch-workflow/`  
**Approach:** Ticket-Based Development 🎫

**THE MISSING PIECE**: Create isolated feature workspaces linked to Git branches for ticket-based development.

**What's Different:**
This is the **only scenario** that creates feature branch workspaces - all previous scenarios only created permanent DEV/TEST/PROD workspaces. This demonstrates the complete developer workflow from ticket assignment → isolated development → code review → deployment.

**Features:**
- ✅ Creates isolated workspace per ticket (e.g., `Product-feature-JIRA-123`)
- ✅ Creates Git feature branch (e.g., `feature/product/JIRA-123`)
- ✅ Links workspace to Git branch (bidirectional sync)
- ✅ Enables parallel development (multiple tickets simultaneously)
- ✅ Safe experimentation without affecting shared environments
- ✅ Integrates with CI/CD pipeline (PR-based workflow)
- ✅ Complete cleanup documentation

**Usage:**
```bash
# Create isolated feature environment
python3 ops/scripts/onboard_data_product.py \
  scenarios/feature-branch-workflow/product_descriptor.yaml \
  --feature JIRA-12345

# Creates:
# • Workspace: Customer Insights-feature-JIRA-12345
# • Git Branch: feature/customer_insights/JIRA-12345
# • Git Connection: Workspace ↔ Branch
# • Scaffold: data_products/customer_insights/
```

**Why This Matters:**
```
Without Feature Branches:
├─ Everyone works in shared DEV workspace
├─ Changes collide and interfere
└─ Hard to track who changed what

With Feature Branches:
├─ Developer A: Product-feature-JIRA-101
├─ Developer B: Product-feature-JIRA-102
├─ Developer C: Product-feature-JIRA-103
└─ Complete isolation, safe experimentation
```

**Complete Workflow:**
```
1. Get Ticket       → JIRA-12345 assigned
2. Create Feature   → onboard_data_product.py --feature JIRA-12345
3. Develop          → Work in isolated workspace
4. Create PR        → feature/product/JIRA-12345 → main
5. CI/CD Validates  → Quality checks, tests, DQ gates
6. Merge            → Approved, merge to main
7. Auto-Deploy      → CI/CD deploys to DEV workspace
8. Promote          → DEV → TEST → PROD (via Fabric Pipeline)
9. Cleanup          → Delete feature workspace & branch
```

**Documentation:**
- [README](feature-branch-workflow/README.md) - Overview & use cases
- [Complete Guide](feature-branch-workflow/FEATURE_WORKFLOW_GUIDE.md) - Step-by-step workflow
- [Quick Reference](feature-branch-workflow/QUICK_REFERENCE.md) - Common commands
- [What Was Missing](feature-branch-workflow/WHAT_WAS_MISSING.md) - Comparison with previous scenarios

**Test Script:**
```bash
# Run automated test
cd scenarios/feature-branch-workflow
python3 test_feature_workflow.py
```

**Key Differences:**

| Scenario | Creates Feature Workspace? | Creates Git Branch? | Use Case |
|----------|---------------------------|-------------------|----------|
| config-driven-workspace | ❌ | ❌ | Environment setup |
| leit-ricoh-setup | ❌ | ❌ | Project initialization |
| domain-workspace | ❌ | ❌ | Domain organization |
| **feature-branch-workflow** | ✅ | ✅ | **Ticket-based development** |

---

## 🚀 Quick Start

### Running a Scenario

1. **Choose your scenario** from the list above
2. **Navigate to the scenario directory**
3. **Run the setup script**

Example:
```bash
# Domain workspace scenario
cd scenarios/domain-workspace
python3 domain_workspace_with_existing_items.py --workspace-name "my-workspace" --domain-name "my-domain"
```

---

## 📋 Prerequisites

### Required Environment Variables

```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export FABRIC_WORKSPACE_ID="your-workspace-id"  # Optional, will be created
```

### Authentication

Ensure you have:
1. Azure Service Principal with Fabric permissions
2. Or Azure CLI authentication configured
3. Or interactive browser authentication set up

Test authentication:
```bash
python3 ops/scripts/manage_workspaces.py list
```

### Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```

Or using conda:
```bash
conda env create -f environment.yml
conda activate fabric-cicd
```

## 🔧 Customization

### Modify Workspace Configuration

Edit the scenario script to change workspace settings:

```python
# Example: In domain_workspace_with_existing_items.py

def __init__(self, workspace_name, domain_name, ...):
    self.workspace_name = workspace_name        # Change workspace name
    self.domain_name = domain_name              # Change domain name
    self.environment = "dev"                    # Change environment (dev/test/prod)
```

### Configure Users

Create or update a principals file in the `config/` directory:

```bash
# config/my-workspace_principals.txt
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
a2b3c4d5-e6f7-8901-bcde-fg2345678901,Member,Data Engineer,User
```

Then reference it when running the scenario:
```bash
python3 scenarios/domain-workspace/domain_workspace_with_existing_items.py \
  --workspace-name "my-workspace" \
  --principals-file "config/my-workspace_principals.txt"
```

---

## 📊 Documentation

### Scenario-Specific Guides

Each scenario directory contains its own documentation:
- **domain-workspace/** - Domain workspace setup guides
- **leit-ricoh-setup/** - LEIT-Ricoh specific documentation
- **leit-ricoh-fresh-setup/** - Fresh setup documentation

### Shared Documentation

The `shared/` directory contains documentation applicable to all scenarios:
- [ARCHITECTURE.md](shared/ARCHITECTURE.md) - Overall architecture patterns
- [CAPACITY_ASSIGNMENT_GUIDE.md](shared/CAPACITY_ASSIGNMENT_GUIDE.md) - Capacity management
- [USER_ADDITION_GUIDE.md](shared/USER_ADDITION_GUIDE.md) - User management best practices
- [QUICKSTART.md](shared/QUICKSTART.md) - Quick start guide
- [SCENARIO_SUMMARY.md](shared/SCENARIO_SUMMARY.md) - Summary of all scenarios

## 🔍 Verification

### Verify Workspace

```bash
# List all workspaces
python3 ops/scripts/manage_workspaces.py list

# Get specific workspace details
python3 ops/scripts/manage_workspaces.py get --name my-workspace
```

### Verify Items

```bash
# List all items in workspace
python3 ops/scripts/manage_fabric_items.py list --workspace my-workspace

# List only specific type
python3 ops/scripts/manage_fabric_items.py list --workspace my-workspace --type Notebook
```

### Verify Users

```bash
# List workspace users
python3 ops/scripts/manage_workspaces.py list-users --workspace my-workspace
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue: Authentication Failed**
```
Solution: Verify environment variables and service principal permissions
```

**Issue: Workspace Already Exists**
```
Solution: Use a different workspace name or delete the existing workspace
python3 ops/scripts/manage_workspaces.py delete --name my-workspace --force
```

**Issue: Insufficient Permissions**
```
Solution: Ensure service principal has Fabric Admin or Workspace Admin role
```

**Issue: Item Creation Failed**
```
Solution: Check workspace capacity and item type support
```

See the [shared troubleshooting documentation](shared/) for more details.

---

## 📝 Creating Your Own Scenario

### 1. Choose a Template

Copy an existing scenario as a starting point:

```bash
# Copy domain workspace scenario
cp -r scenarios/domain-workspace scenarios/my-new-scenario

# Or copy LEIT-Ricoh setup
cp -r scenarios/leit-ricoh-setup scenarios/my-new-scenario
```

### 2. Modify Configuration

Update the script with your requirements:
- Workspace name and domain
- Fabric items to create
- User/group assignments
- Environment settings

### 3. Add Documentation

Create a README in your scenario directory explaining:
- What the scenario creates
- How to use it
- Any special requirements

### 4. Test the Script

```bash
# Test in dev environment first
python3 scenarios/my-new-scenario/my_setup.py
```

### 5. Document in Main README

Add your scenario to this README's "Available Scenarios" section.

---

## 🎯 Best Practices

### 1. **Environment Separation**
Always use different workspaces for dev/test/prod environments.

### 2. **Naming Conventions**
Follow consistent naming patterns:
- Workspace: `{domain}-{purpose}`
- Items: `{DomainName}{ItemType}` (CamelCase for Fabric API)
- Notebooks: `{NN}_{Purpose}` (numbered)

### 3. **User Management**
- Store principals in `config/` directory
- Use Azure AD Object IDs (GUIDs), NOT emails
- Format: `principal_id,role,description,type`
- Use security groups instead of individual users when possible
- Follow least privilege principle

### 4. **Version Control**
- Keep scenario scripts in version control
- Document changes in commit messages
- Tag stable versions

### 5. **Testing**
Test scenarios in dev environment before running in prod.

---

## 📚 Additional Resources

### Core Documentation
- [Workspace Management Guide](../docs/workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md)
- [Fabric Items CRUD Guide](../docs/fabric-items-crud/FABRIC_ITEM_CRUD_QUICKREF.md)
- [Developer Journey Guide](../docs/getting-started/DEVELOPER_JOURNEY_GUIDE.md)

### Shared Scenario Documentation
- [Architecture Patterns](shared/ARCHITECTURE.md)
- [Capacity Assignment Guide](shared/CAPACITY_ASSIGNMENT_GUIDE.md)
- [User Addition Guide](shared/USER_ADDITION_GUIDE.md)
- [Quick Start Guide](shared/QUICKSTART.md)

---

## 🤝 Contributing

To add new scenarios:

1. Create a new subdirectory in `scenarios/` following the naming pattern: `{scenario-name}/`
2. Add your scenario script(s) to the subdirectory
3. Include scenario-specific documentation (README, guides, etc.)
4. Add shared documentation to `shared/` if applicable to all scenarios
5. Update this README's "Available Scenarios" section
6. Test thoroughly before committing

**Example structure:**
```
scenarios/
└── my-new-scenario/
    ├── my_setup.py              # Main setup script
    ├── README.md                # Scenario-specific guide
    ├── QUICKREF.md              # Quick reference (optional)
    └── *_setup_log.json         # Execution logs
```

---

## 📞 Support

For issues or questions:
- Check scenario-specific documentation in each subdirectory
- Review [shared documentation](shared/) for common patterns
- Check the [main documentation](../docs/README.md)
- Contact the platform team

---

**Last Updated:** October 22, 2025  
**Version:** 2.0.0 (Reorganized into subdirectories)
