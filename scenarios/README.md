# Fabric Workspace Setup Scenarios

This directory contains ready-to-use scenario scripts for setting up complete Microsoft Fabric workspaces with various configurations.

## 📁 Directory Structure

```
scenarios/
├── README.md                           # This file
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
├── feature-branch-workflow/           # NEW: Feature branch workspace workflow
│   ├── README.md
│   ├── FEATURE_WORKFLOW_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   ├── WHAT_WAS_MISSING.md
│   ├── product_descriptor.yaml
│   └── test_feature_workflow.sh
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

## � Two Workflow Approaches

This repository supports **two distinct approaches** to workspace provisioning. Choose based on your use case:

### Approach 1: Config-Driven (Enterprise)

**📐 Standardized Naming via `project.config.json`**

Uses ConfigManager to generate workspace names from organizational patterns. Best for enterprise environments with governance requirements.

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

### Approach 2: Direct-Name (Simple)

**📝 Explicit Naming You Control**

You specify exact workspace names. Best for simple setups where you need full control over naming.

**When to use:**
- ✅ Simple, one-off workspace creation
- ✅ Small teams without formal naming standards
- ✅ Need explicit control over names
- ✅ Quick prototyping or testing
- ✅ Non-standardized environments

**Example:**
```bash
# You provide: exact workspace name
python domain_workspace_with_existing_items.py --workspace-name "finance-ops"

# System uses: finance-ops (exactly as provided)
```

**Scenarios:** `domain-workspace/`, `leit-ricoh-setup/`, `leit-ricoh-fresh-setup/`

---

### Quick Decision Matrix

| Requirement | Config-Driven | Direct-Name |
|-------------|---------------|-------------|
| Naming standards enforced | ✅ | ❌ |
| Simple one-off setup | ❌ | ✅ |
| Multi-environment consistency | ✅ | ⚠️ Manual |
| Full naming control | ❌ | ✅ |
| Requires config file | ✅ Required | ❌ Optional |
| Setup complexity | Medium | Low |
| Governance/Compliance | ✅ | ⚠️ Manual |
| Quick prototyping | ❌ | ✅ |

---

## �📋 Available Scenarios

### 1. Config-Driven Workspace (Enterprise)

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
./test_feature_workflow.sh
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
