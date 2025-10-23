# Domain-Based Workspace Setup Guide

## Overview

This scenario demonstrates how to create a **domain-based workspace** with a mix of **new items** and **references to existing items** from other workspaces.

### Important Concepts

**Domains in Fabric:**
- Domains are **logical organizational units**, not API resources
- They provide governance structure and access control patterns
- Implemented through naming conventions and metadata
- Examples: `finance-domain`, `sales-domain`, `engineering-domain`

**Item Ownership:**
- Fabric items belong to **one workspace only**
- You cannot "attach" or "move" items between workspaces
- To access data across workspaces, use:
  - **OneLake Shortcuts** (for Lakehouses)
  - **Cross-workspace queries** (for Warehouses/SQL)
  - **Item copying** (when migration needed)

## Scenario Architecture

```
finance-analytics-domain (logical grouping)
└── finance-analytics-workspace
    ├── finance_lakehouse (NEW - created)
    │   └── Shortcuts → existing_source_lakehouse (REFERENCED)
    ├── finance_warehouse (NEW - created)
    ├── finance_staging_lakehouse (NEW - created)
    └── References → existing_warehouse (via cross-workspace SQL)
```

## What This Scenario Creates

✅ **1 Workspace** - Domain-based workspace with capacity assignment
✅ **1 Primary Lakehouse** - Main data lakehouse for the domain
✅ **1 Analytics Warehouse** - SQL analytics warehouse
✅ **1 Staging Lakehouse** - Additional lakehouse for intermediate data
✅ **Workspace Access** - Configured users/groups (if principals file provided)
📝 **References** - Documentation for accessing existing items

## Quick Start

### Basic Usage

```bash
# Create domain workspace with new items only
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance-analytics \
    --capacity-id <your-capacity-id>
```

### With Existing Item References

```bash
# Create workspace and document how to access existing items
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance-analytics \
    --capacity-id <your-capacity-id> \
    --existing-lakehouse-workspace <workspace-id> \
    --existing-lakehouse-name "SourceDataLakehouse" \
    --existing-warehouse-workspace <workspace-id> \
    --existing-warehouse-name "SourceWarehouse"
```

### With User/Group Access

```bash
# Create domain-specific principals file
cp config/workspace_principals.template.txt finance-analytics_principals.txt

# Edit and add your users/groups
# Format: principal_id,role,description,type

# Run scenario (will auto-detect principals file)
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance-analytics \
    --capacity-id <your-capacity-id> \
    --principals-file finance-analytics_principals.txt
```

## Step-by-Step Execution

### Step 1: Create Domain Workspace

Creates workspace with domain naming convention:
- Name: `{domain-name}-workspace`
- Description: Includes domain context
- Capacity: Assigned if provided

### Step 2: Create Primary Lakehouse

Creates main lakehouse for domain:
- Name: `{domain-name}_lakehouse`
- Type: Lakehouse
- Purpose: Primary data storage

### Step 3: Create Warehouse

Creates analytics warehouse:
- Name: `{domain-name}_warehouse`
- Type: Warehouse
- Purpose: SQL analytics and reporting

### Step 4: Create Additional Lakehouse

Creates staging/intermediate lakehouse:
- Name: `{domain-name}_staging_lakehouse`
- Type: Lakehouse
- Purpose: Temporary and intermediate data

### Step 5: Reference Existing Items

**For Existing Lakehouses:**
Documents how to create OneLake Shortcuts:
1. Open new lakehouse in Fabric portal
2. Right-click → New shortcut
3. Select "OneLake" source
4. Navigate to source workspace
5. Select source lakehouse
6. Choose tables/files to shortcut

**For Existing Warehouses:**
Documents cross-workspace T-SQL queries:
```sql
-- Query existing warehouse from new workspace
SELECT * 
FROM [source_workspace].[source_warehouse].[dbo].[TableName]
```

### Step 6: Configure Workspace Access

Adds users/groups using core CLI:
- Looks for `{domain-name}_principals.txt`
- Falls back to `--principals-file` argument
- Uses `manage_workspaces.py add-users-from-file` (no code duplication)

### Step 7: Generate Summary

Creates setup log:
- JSON file with complete setup details
- Location: `{domain-name}_setup_log.json`
- Includes items created, referenced, and errors

## Working with Existing Items

### Accessing Existing Lakehouse Data

**OneLake Shortcuts** (Recommended):

1. **Portal Method:**
   - Navigate to new lakehouse in Fabric portal
   - Lakehouse Explorer → right-click → "New shortcut"
   - Source: OneLake
   - Browse to source workspace → source lakehouse
   - Select tables/folders
   - Shortcuts appear as virtual folders

2. **Benefits:**
   - No data duplication
   - Always up-to-date (points to source)
   - Works across workspaces
   - Supports tables and files

### Accessing Existing Warehouse Data

**Cross-Workspace T-SQL Queries:**

```sql
-- Format: [workspace_name].[warehouse_name].[schema].[table]
SELECT 
    s.ProductID,
    s.SalesAmount,
    p.ProductName
FROM 
    [source_workspace].[source_warehouse].[dbo].[Sales] s
    JOIN [current_workspace].[finance_warehouse].[dbo].[Products] p
        ON s.ProductID = p.ProductID
```

**Considerations:**
- Requires appropriate permissions on source workspace
- May impact performance (cross-workspace queries)
- Consider data governance policies

### When to Copy vs Reference

**Use References (Shortcuts) When:**
- ✅ Source data changes frequently
- ✅ Data should stay in original workspace (ownership)
- ✅ Multiple workspaces need same data
- ✅ Want to avoid duplication

**Copy Items When:**
- ✅ Need independent copy (different lifecycle)
- ✅ Source workspace will be deleted
- ✅ Performance critical (avoid cross-workspace queries)
- ✅ Different security requirements

## Command-Line Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--domain-name` | ✅ Yes | Logical domain name | `finance-analytics` |
| `--capacity-id` | ❌ No | Fabric capacity GUID | `abc-123-def-456` |
| `--principals-file` | ❌ No | Users/groups file path | `my_team.txt` |
| `--existing-lakehouse-workspace` | ❌ No | Source lakehouse workspace ID | `workspace-guid` |
| `--existing-lakehouse-name` | ❌ No | Source lakehouse name | `SourceData` |
| `--existing-warehouse-workspace` | ❌ No | Source warehouse workspace ID | `workspace-guid` |
| `--existing-warehouse-name` | ❌ No | Source warehouse name | `SourceWarehouse` |

## Example Scenarios

### Scenario 1: Finance Analytics Domain

```bash
# Create finance domain workspace
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name finance-analytics \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177 \
    --principals-file finance_team.txt
```

**Created:**
- `finance-analytics-workspace`
- `finance_lakehouse`
- `finance_warehouse`
- `finance_staging_lakehouse`

### Scenario 2: Sales Operations with Existing Data

```bash
# Create sales domain, reference existing ERP data
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name sales-ops \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177 \
    --existing-lakehouse-workspace abc-123 \
    --existing-lakehouse-name "ERP_DataLake" \
    --principals-file sales_team.txt
```

**Created:**
- `sales-ops-workspace`
- `sales_ops_lakehouse` (with shortcut instructions to ERP_DataLake)
- `sales_ops_warehouse`
- `sales_ops_staging_lakehouse`

### Scenario 3: Multi-Source Analytics

```bash
# Create analytics domain referencing multiple sources
python scenarios/domain_workspace_with_existing_items.py \
    --domain-name customer-360 \
    --capacity-id 0749b635-c51b-46c6-948a-02f05d7fe177 \
    --existing-lakehouse-workspace workspace-a \
    --existing-lakehouse-name "CRM_Lakehouse" \
    --existing-warehouse-workspace workspace-b \
    --existing-warehouse-name "Sales_Warehouse"
```

**Manual Steps After:**
1. Create shortcuts to CRM_Lakehouse tables
2. Set up cross-workspace queries to Sales_Warehouse
3. Integrate multiple data sources in new lakehouse

## Principals File Format

Create `{domain-name}_principals.txt`:

```text
# principal_id,role,description,type
# Types: User, Group, ServicePrincipal
# Roles: Admin, Member, Contributor, Viewer

# Users (Object IDs from Azure AD)
a1b2c3d4-...,Admin,Finance Team Lead,User
b2c3d4e5-...,Contributor,Data Engineer,User

# Groups (Object IDs from Azure AD)
c3d4e5f6-...,Member,Finance Analysts Team,Group
d4e5f6a7-...,Viewer,Executive Dashboard Viewers,Group

# Service Principals
e5f6a7b8-...,Contributor,ETL Pipeline Service,ServicePrincipal
```

**Get Object IDs:**

```bash
# Get user Object ID
az ad user show --id user@domain.com --query id -o tsv

# Get group Object ID
az ad group show --group "Finance Team" --query id -o tsv

# Get service principal Object ID
az ad sp show --id <app-id> --query id -o tsv
```

## Output and Logging

### Console Output

```
================================================================================
  STEP 1: Creating Domain-Based Workspace
================================================================================
✓ Workspace created: finance-analytics-workspace
  ID: abc-123-def-456

================================================================================
  STEP 2: Creating Primary Lakehouse
================================================================================
✓ Created lakehouse: finance_lakehouse
  ID: lakehouse-guid
  Type: Lakehouse

...

🎉 Domain workspace setup completed successfully!
```

### Setup Log File

Location: `{domain-name}_setup_log.json`

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "domain": "finance-analytics",
  "workspace_name": "finance-analytics-workspace",
  "workspace_id": "abc-123",
  "items_created": [
    {
      "type": "Lakehouse",
      "name": "finance_lakehouse",
      "id": "lakehouse-1"
    },
    {
      "type": "Warehouse",
      "name": "finance_warehouse",
      "id": "warehouse-1"
    }
  ],
  "items_referenced": [
    {
      "type": "Lakehouse",
      "name": "SourceDataLakehouse",
      "workspace": "source-workspace-id",
      "access_method": "OneLake Shortcut"
    }
  ],
  "errors": []
}
```

## Best Practices

### Domain Organization

✅ **DO:**
- Use consistent naming: `{domain}-{purpose}-workspace`
- Document domain ownership and purpose
- Apply domain-wide governance policies
- Use domain-specific capacity when possible

❌ **DON'T:**
- Mix unrelated domains in same workspace
- Create generic/vague domain names
- Ignore capacity planning for domains

### Item Management

✅ **DO:**
- Use shortcuts for cross-workspace lakehouse access
- Keep item ownership clear (one workspace)
- Document data lineage and dependencies
- Apply consistent naming conventions

❌ **DON'T:**
- Duplicate large datasets unnecessarily
- Create circular dependencies
- Mix production and development items

### Access Control

✅ **DO:**
- Use Azure AD groups for team access
- Apply least-privilege principle
- Document access patterns
- Audit access regularly

❌ **DON'T:**
- Add individual users for large teams
- Grant Admin role unnecessarily
- Share credentials

## Troubleshooting

### Issue: Workspace Creation Fails

**Error:** `403 Forbidden` or capacity assignment fails

**Solutions:**
1. Verify service principal has capacity access
2. Check capacity is not at item limit
3. Try without `--capacity-id` (uses trial)

### Issue: Can't See Existing Items

**Error:** Referenced items not visible in new workspace

**Explanation:**
- This is expected! Items belong to their original workspace
- You must create **shortcuts** or use **cross-workspace queries**

**Solution:**
Follow Step 5 instructions to create shortcuts/queries

### Issue: Principals File Not Found

**Error:** `No principals file found`

**Solutions:**
1. Create `{domain-name}_principals.txt` in scenarios folder
2. Use `--principals-file` argument with absolute path
3. Skip user addition, add manually later:
   ```bash
   python ops/scripts/manage_workspaces.py add-users-from-file <workspace-id> <file>
   ```

### Issue: Permission Denied on Existing Items

**Error:** Can't create shortcuts or query existing warehouse

**Solutions:**
1. Verify you have at least **Viewer** access on source workspace
2. Check service principal has permissions
3. Contact source workspace owner

## Next Steps After Setup

1. **Create OneLake Shortcuts:**
   - Navigate to primary lakehouse in portal
   - Create shortcuts to referenced lakehouses

2. **Set Up Data Pipelines:**
   ```bash
   # Create pipeline for ETL
   python ops/scripts/manage_items.py create \
       --workspace-id <workspace-id> \
       --type DataPipeline \
       --name "{domain}_etl_pipeline"
   ```

3. **Create Notebooks:**
   ```bash
   # Create transformation notebook
   python ops/scripts/manage_items.py create \
       --workspace-id <workspace-id> \
       --type Notebook \
       --name "{domain}_transform_notebook"
   ```

4. **Build Semantic Models:**
   - Create in Fabric portal (API limitations)
   - Connect to warehouse or lakehouse SQL endpoint

5. **Design Reports:**
   - Create Power BI reports
   - Connect to semantic models

## Related Documentation

- **Core CLI:** `ops/scripts/manage_workspaces.py --help`
- **User Management:** `../../docs/guides/BULK_USER_QUICKSTART.md`
- **Group Support:** `scenarios/GROUP_SUPPORT_QUICKREF.md`
- **Item Management:** `FABRIC_ITEM_CRUD_QUICKREF.md`
- **Workspace Templates:** `config/workspace_principals.template.txt`

## Support

For issues or questions:
1. Check setup log: `{domain-name}_setup_log.json`
2. Review error messages in console output
3. Verify prerequisites (capacity, permissions)
4. Consult Fabric API documentation
