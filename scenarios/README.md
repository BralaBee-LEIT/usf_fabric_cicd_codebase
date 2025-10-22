# Fabric Workspace Setup Scenarios

This directory contains ready-to-use scenario scripts for setting up complete Microsoft Fabric workspaces with various configurations.

## 📁 Directory Structure

```
scenarios/
├── README.md                           # This file
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

## 📋 Available Scenarios

### 1. Domain Workspace with Existing Items

**Location:** `domain-workspace/`

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

### 2. LEIT-Ricoh Domain Setup

**Location:** `leit-ricoh-setup/`

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

### 3. LEIT-Ricoh Fresh Setup

**Location:** `leit-ricoh-fresh-setup/`

Fresh variant of the LEIT-Ricoh setup with additional configurations.

**Usage:**
```bash
python3 scenarios/leit-ricoh-fresh-setup/leit_ricoh_fresh_setup.py
```

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
