# Fabric Workspace Setup Scenarios

This directory contains ready-to-use scenario scripts for setting up complete Microsoft Fabric workspaces with various configurations.

## 📁 Available Scenarios

### 1. LEIT-Ricoh Domain Setup

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

---

## 🚀 Usage

### Option 1: Python Script (Recommended)

```bash
# Run the Python setup script
python3 scenarios/leit_ricoh_setup.py
```

**Features:**
- ✅ Better error handling
- ✅ Detailed logging
- ✅ Progress tracking
- ✅ JSON log file generation
- ✅ Setup verification
- ✅ Comprehensive summary

### Option 2: Bash Script

```bash
# Run the bash setup script
./scenarios/leit_ricoh_setup.sh
```

**Features:**
- ✅ Simpler execution
- ✅ Colored output
- ✅ Step-by-step progress
- ✅ Summary report

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

---

## 🔧 Customization

### Modify Workspace Configuration

Edit the scenario script to change:

```python
# In leit_ricoh_setup.py

class RicohWorkspaceSetup:
    def __init__(self):
        self.workspace_name = "leit-ricoh"          # Change workspace name
        self.domain_name = "leit-ricoh-domain"      # Change domain name
        self.environment = "dev"                    # Change environment (dev/test/prod)
```

### Add Custom Fabric Items

Add items to the configuration arrays:

```python
# In step_5_create_additional_items()

items = [
    {
        "name": "CustomItem",
        "type": FabricItemType.LAKEHOUSE,  # Choose type
        "description": "Custom item description"
    },
    # ... more items
]
```

### Configure Users

Update user emails in `step_6_add_users()`:

```python
users = [
    {
        "email": "your.admin@company.com",      # Update with real email
        "role": WorkspaceRole.ADMIN,
        "description": "Workspace administrator"
    },
    # ... more users
]
```

Then uncomment the user addition code:

```python
# Uncomment this block to actually add users
# for user in users:
#     self.workspace_mgr.add_workspace_user(
#         workspace_id=self.workspace_id,
#         email=user["email"],
#         role=user["role"]
#     )
```

---

## 📊 Output

### Console Output

The script provides detailed progress updates:

```
================================================================================
  LEIT-Ricoh Domain - Complete Workspace Setup
================================================================================

Domain: leit-ricoh-domain
Workspace: leit-ricoh
Environment: dev

This will create:
  - 1 Workspace
  - 1 Lakehouse
  - 1 Warehouse
  - 3 Notebooks
  - 3 Additional items (Pipeline, Semantic Model, Report)
  - 6 User role configurations

================================================================================

================================================================================
  STEP 1: Creating Workspace - leit-ricoh
================================================================================

ℹ Creating workspace 'leit-ricoh' in dev environment...
✓ Workspace 'leit-ricoh' created successfully
  Workspace ID: abc123-def456-ghi789

...
```

### Log File

A detailed JSON log is saved to `.onboarding_logs/`:

```json
{
  "timestamp": "2025-10-22T10:30:00Z",
  "domain": "leit-ricoh-domain",
  "workspace": "leit-ricoh",
  "environment": "dev",
  "workspace_id": "abc123-def456-ghi789",
  "items": [
    {
      "name": "RicohDataLakehouse",
      "type": "Lakehouse",
      "id": "item-id-123"
    }
  ],
  "users": [...],
  "errors": []
}
```

---

## 🔍 Verification

### Verify Workspace

```bash
# List all workspaces
python3 ops/scripts/manage_workspaces.py list

# Get specific workspace details
python3 ops/scripts/manage_workspaces.py get --name leit-ricoh
```

### Verify Items

```bash
# List all items in workspace
python3 ops/scripts/manage_fabric_items.py list --workspace leit-ricoh

# List only specific type
python3 ops/scripts/manage_fabric_items.py list --workspace leit-ricoh --type Notebook
```

### Verify Users

```bash
# List workspace users
python3 ops/scripts/manage_workspaces.py list-users --workspace leit-ricoh
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
python3 ops/scripts/manage_workspaces.py delete --name leit-ricoh --force
```

**Issue: Insufficient Permissions**
```
Solution: Ensure service principal has Fabric Admin or Workspace Admin role
```

**Issue: Item Creation Failed**
```
Solution: Check workspace capacity and item type support
```

### Enable Debug Logging

```bash
# Set debug logging level
export LOG_LEVEL=DEBUG

# Run with verbose output
python3 scenarios/leit_ricoh_setup.py 2>&1 | tee setup.log
```

---

## 📝 Creating Your Own Scenario

### 1. Copy the Template

```bash
cp scenarios/leit_ricoh_setup.py scenarios/my_scenario_setup.py
```

### 2. Modify Configuration

Update workspace name, domain, and items to match your requirements.

### 3. Test the Script

```bash
# Dry run (modify script to skip actual creation)
python3 scenarios/my_scenario_setup.py --dry-run

# Full execution
python3 scenarios/my_scenario_setup.py
```

### 4. Document Your Scenario

Add a section to this README explaining your scenario.

---

## 🎯 Best Practices

### 1. **Environment Separation**
Always use different workspaces for dev/test/prod environments.

### 2. **Naming Conventions**
Follow consistent naming patterns:
- Workspace: `{domain}-{purpose}`
- Items: `{DomainName}{ItemType}`
- Notebooks: `{NN}_{Purpose}` (numbered)

### 3. **User Management**
- Use security groups instead of individual users when possible
- Follow least privilege principle for role assignments
- Document user responsibilities

### 4. **Version Control**
- Keep scenario scripts in version control
- Tag stable versions
- Document changes in commit messages

### 5. **Testing**
Test scenarios in dev environment before running in prod.

---

## 📚 Additional Resources

- [Workspace Management Guide](../docs/workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md)
- [Fabric Items CRUD Guide](../docs/fabric-items-crud/FABRIC_ITEM_CRUD_QUICKREF.md)
- [Complete ETL Setup Guide](../docs/etl-data-platform/COMPLETE_ETL_SETUP_GUIDE.md)
- [Developer Journey Guide](../docs/getting-started/DEVELOPER_JOURNEY_GUIDE.md)

---

## 🤝 Contributing

To add new scenarios:

1. Create scenario script in `scenarios/` directory
2. Follow the naming pattern: `{domain}_{purpose}_setup.py`
3. Include both bash and Python versions (optional)
4. Document the scenario in this README
5. Add example output and verification steps
6. Test thoroughly before committing

---

## 📞 Support

For issues or questions:
- Check the [main documentation](../docs/README.md)
- Review [troubleshooting guides](../docs/development-maintenance/)
- Contact the platform team

---

**Last Updated:** October 22, 2025  
**Version:** 1.0.0
