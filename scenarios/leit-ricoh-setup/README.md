# LEIT-Ricoh Domain Setup

Complete workspace setup for the LEIT-Ricoh domain with full analytics infrastructure including lakehouses, warehouse, notebooks, pipelines, and reports.

## 📋 What This Creates

### Workspace
- **Name:** leit-ricoh
- **Domain:** leit-ricoh-domain
- **Environment:** dev/test/prod (configurable)

### Fabric Items (8 total)

| Category | Item | Type | Description |
|----------|------|------|-------------|
| **Storage** | RicohDataLakehouse | Lakehouse | Primary data storage |
| | RicohAnalyticsWarehouse | Warehouse | Analytics warehouse |
| **Processing** | 01_DataIngestion | Notebook | Data ingestion logic |
| | 02_DataTransformation | Notebook | Data transformation |
| | 03_DataValidation | Notebook | Data quality checks |
| **Analytics** | RicohDataPipeline | Pipeline | Orchestration pipeline |
| | RicohSemanticModel | Semantic Model | Business intelligence layer |
| | RicohExecutiveDashboard | Report | Executive dashboard |

### User Roles (6 configured)
- 1 Admin - Workspace administrator
- 2 Members - Data Engineers
- 1 Contributor - Data Analyst  
- 2 Viewers - Business Users

## 🚀 Usage

### Python Script (Recommended)

```bash
python3 leit_ricoh_setup.py
```

**Features:**
- ✅ Better error handling
- ✅ Detailed logging with progress tracking
- ✅ JSON log file generation
- ✅ Setup verification
- ✅ Comprehensive summary

### Bash Script

```bash
./leit_ricoh_setup.sh
```

**Features:**
- ✅ Simpler execution
- ✅ Colored console output
- ✅ Step-by-step progress
- ✅ Summary report

## 📁 Files

- `leit_ricoh_setup.py` - Python version (recommended)
- `leit_ricoh_setup.sh` - Bash version

## 🔧 Customization

### Change Workspace Configuration

Edit `leit_ricoh_setup.py`:

```python
class RicohWorkspaceSetup:
    def __init__(self):
        self.workspace_name = "leit-ricoh"          # Change name
        self.domain_name = "leit-ricoh-domain"      # Change domain
        self.environment = "dev"                    # dev/test/prod
```

### Add Custom Items

Modify the items list in the script:

```python
items = [
    {
        "name": "CustomLakehouse",
        "type": FabricItemType.LAKEHOUSE,
        "description": "Custom lakehouse description"
    },
    # ... more items
]
```

### Configure Users

Update user emails in `step_6_add_users()`:

```python
users = [
    {
        "email": "admin@company.com",
        "role": WorkspaceRole.ADMIN,
        "description": "Workspace administrator"
    },
    # ... more users
]
```

## 📊 Output

### Console Output

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
```

### Log File

JSON logs saved to `../../.onboarding_logs/`:

```json
{
  "timestamp": "2025-10-22T10:30:00Z",
  "domain": "leit-ricoh-domain",
  "workspace": "leit-ricoh",
  "workspace_id": "abc123-def456-ghi789",
  "items": [...],
  "users": [...],
  "errors": []
}
```

## 🔍 Verification

```bash
# Verify workspace created
python3 ../../ops/scripts/manage_workspaces.py get --name leit-ricoh

# List all items
python3 ../../ops/scripts/manage_fabric_items.py list --workspace leit-ricoh

# Check users
python3 ../../ops/scripts/manage_workspaces.py list-users --workspace leit-ricoh
```

## 📌 Notes

- Workspace will be created with Trial capacity if not specified
- User addition requires valid email addresses and proper permissions
- Items follow CamelCase naming convention for Fabric API compatibility
- Notebooks are numbered with prefix (01_, 02_, 03_) for execution order

## 📚 See Also

- [Main Scenarios README](../README.md)
- [Shared Documentation](../shared/)
- [Workspace Management Guide](../../docs/workspace-management/)
