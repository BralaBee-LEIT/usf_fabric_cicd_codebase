# Domain Workspace Setup - Quick Reference

## 🚀 Quick Start

```bash
# Basic: Create domain workspace with new items
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name <domain> \
    --capacity-id <capacity-guid>

# Advanced: Include existing item references + users
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name <domain> \
    --capacity-id <capacity-guid> \
    --existing-lakehouse-workspace <workspace-id> \
    --existing-lakehouse-name "SourceLakehouse" \
    --principals-file <domain>_principals.txt
```

## 📦 What Gets Created

| Item | Name Pattern | Type | Purpose |
|------|--------------|------|---------|
| Workspace | `{domain}-workspace` | Workspace | Container for all items |
| Primary Lakehouse | `{domain}_lakehouse` | Lakehouse | Main data storage |
| Warehouse | `{domain}_warehouse` | Warehouse | SQL analytics |
| Staging Lakehouse | `{domain}_staging_lakehouse` | Lakehouse | Intermediate data |

## 🎯 Key Concepts

### Domain = Logical Grouping (NOT an API Object)

```
finance-analytics-domain (logical concept)
├── Naming convention: finance-*
├── Governance: finance-specific policies
└── Access: finance team members

Implementation:
- Workspace naming: finance-analytics-workspace
- Item naming: finance_lakehouse, finance_warehouse
- Metadata: domain tags and descriptions
```

### Items Belong to ONE Workspace

```
❌ Cannot: "Move" or "Attach" existing items to new workspace
✅ Can:    Reference via shortcuts/queries
```

## 🔗 Accessing Existing Items

### Lakehouse → Use OneLake Shortcuts

```
Portal Steps:
1. Open new lakehouse
2. Right-click → "New shortcut"  
3. Source: OneLake
4. Navigate to source workspace → source lakehouse
5. Select tables/folders

Result: Virtual access (no duplication)
```

### Warehouse → Use Cross-Workspace SQL

```sql
-- Query warehouse in another workspace
SELECT *
FROM [source_workspace].[source_warehouse].[dbo].[Sales]
```

## 👥 Adding Users/Groups

### Option 1: During Setup

```bash
# Create principals file
cp config/workspace_principals.template.txt finance_principals.txt

# Edit: principal_id,role,description,type
# Example: a1b2c3d4-...,Admin,Finance Lead,User

# Run scenario (auto-detects <domain>_principals.txt)
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance \
    --principals-file finance_principals.txt
```

### Option 2: After Setup

```bash
# Add users later using core CLI
python ops/scripts/manage_workspaces.py add-users-from-file \
    <workspace-id> \
    finance_principals.txt
```

## 📋 Command Arguments

| Argument | Required | Example | Notes |
|----------|----------|---------|-------|
| `--domain-name` | ✅ | `finance-analytics` | Logical domain name |
| `--capacity-id` | ❌ | `abc-123...` | Uses trial if omitted |
| `--principals-file` | ❌ | `team.txt` | Auto-detects `{domain}_principals.txt` |
| `--existing-lakehouse-workspace` | ❌ | `workspace-guid` | For shortcuts documentation |
| `--existing-lakehouse-name` | ❌ | `SourceData` | Name of source lakehouse |
| `--existing-warehouse-workspace` | ❌ | `workspace-guid` | For cross-workspace SQL |
| `--existing-warehouse-name` | ❌ | `SourceWarehouse` | Name of source warehouse |

## 📊 Example Scenarios

### Scenario 1: Clean Start

```bash
# New domain, no existing items
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name sales-ops \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177
```

**Creates:**
- sales-ops-workspace
- sales_ops_lakehouse
- sales_ops_warehouse  
- sales_ops_staging_lakehouse

### Scenario 2: Reference Existing Data

```bash
# New domain, link to existing ERP lakehouse
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177 \
    --existing-lakehouse-workspace abc-123-def \
    --existing-lakehouse-name "ERP_DataLake"
```

**Creates:** Same items + shortcut documentation

**Manual Step:** Create OneLake shortcuts in portal

### Scenario 3: Full Setup with Team

```bash
# Create principals file
echo "9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Team Lead,User" > customer_principals.txt
echo "b2c3d4e5-...,Member,Analytics Team,Group" >> customer_principals.txt

# Run full setup
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name customer-360 \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177 \
    --existing-lakehouse-workspace ws1 \
    --existing-lakehouse-name "CRM_Data" \
    --existing-warehouse-workspace ws2 \
    --existing-warehouse-name "Sales_DW" \
    --principals-file customer_principals.txt
```

**Creates:** All items + users/groups configured

## 🔍 Finding Object IDs

### Users

```bash
az ad user show --id user@domain.com --query id -o tsv
```

### Groups

```bash
az ad group show --group "Team Name" --query id -o tsv
```

### Service Principals

```bash
az ad sp show --id <app-id> --query id -o tsv
```

### Workspaces

```bash
# List all workspaces
python ops/scripts/manage_workspaces.py list

# Find specific workspace
python ops/scripts/manage_workspaces.py list | grep "workspace-name"
```

## 📁 Output Files

| File | Location | Content |
|------|----------|---------|
| Setup Log | `{domain}_setup_log.json` | Complete setup details |
| Principals | `{domain}_principals.txt` | Users/groups (if used) |

## 🔧 Post-Setup Tasks

### 1. Create Shortcuts (if existing items referenced)

```
Portal:
finance_lakehouse → New shortcut → OneLake → [source workspace] → [source lakehouse]
```

### 2. Create Pipelines

```bash
python ops/scripts/manage_items.py create \
    --workspace-id <id> \
    --type DataPipeline \
    --name "etl_pipeline"
```

### 3. Create Notebooks

```bash
python ops/scripts/manage_items.py create \
    --workspace-id <id> \
    --type Notebook \
    --name "transform_notebook"
```

## ⚠️ Common Issues

### ❌ "Workspace creation failed: 403"

**Fix:** Service principal lacks capacity permission
```bash
# Verify capacity access or try without --capacity-id
```

### ❌ "Can't see existing lakehouse in new workspace"

**Expected!** Items stay in original workspace.
**Fix:** Create OneLake shortcut (see "Accessing Existing Items")

### ❌ "Principals file not found"

**Fix:** Create `{domain}_principals.txt` or use `--principals-file`

## 📚 Related Commands

```bash
# List workspaces
python ops/scripts/manage_workspaces.py list

# List items in workspace
python ops/scripts/manage_items.py list --workspace-id <id>

# Add more users later
python ops/scripts/manage_workspaces.py add-users-from-file <workspace-id> <file>

# Assign capacity later
python ops/scripts/manage_workspaces.py assign-capacity <workspace-id> <capacity-id>
```

## 🎯 Best Practices

✅ **DO:**
- Use domain-specific principals files
- Document shortcuts/references in setup log
- Apply consistent naming: `{domain}_*`
- Use Azure AD groups for teams

❌ **DON'T:**
- Try to "move" items between workspaces (use shortcuts)
- Mix multiple domains in one workspace
- Duplicate large datasets (use shortcuts)
- Grant Admin unnecessarily

## 📖 Full Documentation

See: `scenarios/DOMAIN_WORKSPACE_GUIDE.md`
