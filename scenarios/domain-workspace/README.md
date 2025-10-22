# Domain Workspace Scenario

Create a domain-based workspace with new items and support for accessing existing items via OneLake shortcuts.

## 📋 What This Creates

- **1 Workspace** - Assigned to specified domain with capacity
- **1 Primary Lakehouse** - Main data storage for the workspace
- **1 Warehouse** - Analytics warehouse for SQL queries
- **1 Staging Lakehouse** - Temporary/staging data storage
- **User/Group Access** - Automatic configuration from principals file

## 🚀 Usage

### With Existing Principals File (Real-World Scenario)

```bash
python3 domain_workspace_with_existing_items.py \
  --workspace-name "finance-ops" \
  --domain-name "finance" \
  --principals-file "../../config/finance-ops_principals.txt"
```

### Interactive Mode (Creates Template)

```bash
python3 domain_workspace_with_existing_items.py \
  --workspace-name "marketing-ops" \
  --domain-name "marketing"
```

This will:
1. Create the workspace and items
2. Generate a principals template in `config/`
3. Prompt you to edit the file
4. Add users after you press ENTER

### Automation Mode (Skip User Prompt)

```bash
python3 domain_workspace_with_existing_items.py \
  --workspace-name "sales-ops" \
  --domain-name "sales" \
  --skip-user-prompt
```

## 📁 Files

- `domain_workspace_with_existing_items.py` - Main setup script
- `DOMAIN_WORKSPACE_GUIDE.md` - Comprehensive setup guide
- `DOMAIN_WORKSPACE_QUICKREF.md` - Quick reference card
- `*_setup_log.json` - Execution logs

## 📖 Documentation

See the comprehensive guides:
- [Domain Workspace Guide](DOMAIN_WORKSPACE_GUIDE.md) - Full documentation
- [Quick Reference](DOMAIN_WORKSPACE_QUICKREF.md) - Common commands

## 🔑 Key Features

- ✅ Domain-based workspace organization (logical grouping)
- ✅ Automatic capacity assignment
- ✅ CamelCase item naming (Fabric API requirement)
- ✅ Enhanced warehouse retry logic (5 attempts, 3s delay)
- ✅ Dual workflow: existing file or interactive template
- ✅ Integration with core CLI for user management
- ✅ OneLake shortcuts documentation for existing items

## 📌 Notes

### Item Naming

Fabric API requires CamelCase naming. The script automatically converts:
- `finance-ops` workspace → `FinanceOpsLakehouse`, `FinanceOpsWarehouse`
- `marketing-analytics` workspace → `MarketingAnalyticsLakehouse`

### Accessing Existing Items

To access existing lakehouses/warehouses from other workspaces:
- **Lakehouses**: Use OneLake Shortcuts (see guide)
- **Warehouses**: Use cross-workspace T-SQL queries (see guide)

Items cannot be "attached" to multiple workspaces - they belong to one workspace only.

## 🎯 Example Principals File

Create in `../../config/{workspace-name}_principals.txt`:

```csv
# Format: principal_id,role,description,type
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
a2b3c4d5-e6f7-8901-bcde-fg2345678901,Member,Data Engineer Team,Group
```

**Important:** Use Azure AD Object IDs (GUIDs), not emails!

Get Object IDs:
```bash
# User
az ad user show --id user@domain.com --query id -o tsv

# Group
az ad group show --group "Team Name" --query id -o tsv
```
