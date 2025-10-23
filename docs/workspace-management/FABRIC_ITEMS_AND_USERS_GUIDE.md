# Fabric Items and User Management Guide

**Date:** 21 October 2025  
**Purpose:** Complete guide for creating Fabric items and managing workspace users  
**Tools:** `manage_fabric_items.py` and `manage_workspaces.py`

---

## Quick Answer: YES to Everything! ✅

This codebase provides comprehensive capabilities for:

✅ **Create Fabric items** in new or existing workspaces  
✅ **Assign items** to specific workspaces  
✅ **Add new users** to workspaces  
✅ **Assign roles** to new users  
✅ **Update roles** of existing users  
✅ **List all users** and their current roles  
✅ **Remove users** from workspaces

---

## 📦 Part 1: Creating Fabric Items

### Supported Item Types (26+ Types)

The `fabric_item_manager.py` module supports all major Fabric item types:

#### Data Engineering
- ✅ **Lakehouse** - Data lake storage
- ✅ **Notebook** - Spark notebooks
- ✅ **SparkJobDefinition** - Spark job definitions
- ✅ **Environment** - Spark environments
- ✅ **GraphQLApi** - GraphQL APIs

#### Data Factory
- ✅ **DataPipeline** - Data pipelines
- ✅ **CopyJob** - Copy activities
- ✅ **MountedDataFactory** - Mounted data factories

#### Data Warehouse
- ✅ **Warehouse** - SQL data warehouses
- ✅ **SQLEndpoint** - SQL endpoints
- ✅ **Datamart** - Datamarts
- ✅ **MirroredDatabase** - Mirrored databases
- ✅ **MirroredWarehouse** - Mirrored warehouses

#### Power BI
- ✅ **Report** - Power BI reports
- ✅ **Dashboard** - Dashboards
- ✅ **SemanticModel** - Semantic models (datasets)
- ✅ **Dataflow** - Dataflows
- ✅ **PaginatedReport** - Paginated reports

#### Real-Time Intelligence
- ✅ **Eventhouse** - Event houses
- ✅ **Eventstream** - Event streams
- ✅ **KQLDatabase** - KQL databases
- ✅ **KQLQueryset** - KQL querysets
- ✅ **KQLDashboard** - KQL dashboards
- ✅ **Reflex** - Reflex (Activator)

#### Data Science
- ✅ **MLModel** - ML models
- ✅ **MLExperiment** - ML experiments

---

## 🚀 Creating Fabric Items - Examples

### 1. List Existing Items in Workspace

```bash
# List all items
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "Test Data Product"

# Filter by type
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "Test Data Product" \
  --type Lakehouse

# Output as JSON
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "Test Data Product" \
  --json
```

### 2. Create a Lakehouse

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "MyLakehouse" \
  --type Lakehouse \
  --description "Main data lakehouse for test project"
```

### 3. Create a Notebook

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "DataProcessingNotebook" \
  --type Notebook \
  --description "ETL processing notebook"
```

### 4. Create a Data Pipeline

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "DailyETLPipeline" \
  --type DataPipeline \
  --description "Daily data ingestion pipeline"
```

### 5. Create a Warehouse

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "AnalyticsWarehouse" \
  --type Warehouse \
  --description "SQL warehouse for analytics"
```

### 6. Create Multiple Items in Sequence

```bash
# Create a complete data engineering workspace
WORKSPACE="Test Data Product"

# 1. Create lakehouse
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE" \
  --name "RawLakehouse" \
  --type Lakehouse \
  --description "Raw data layer"

# 2. Create processing notebook
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE" \
  --name "TransformNotebook" \
  --type Notebook \
  --description "Data transformation logic"

# 3. Create pipeline
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE" \
  --name "MainPipeline" \
  --type DataPipeline \
  --description "Orchestration pipeline"

# 4. Create warehouse
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE" \
  --name "ServeWarehouse" \
  --type Warehouse \
  --description "Serving layer"

echo "✅ Created complete data platform in $WORKSPACE"
```

---

## 📝 Creating Items with Definitions (Advanced)

Some items can be created with pre-defined content using JSON definition files.

### Create Notebook with Code

```bash
# 1. Create notebook definition file
cat > notebook_def.json << 'EOF'
{
  "cells": [
    {
      "cell_type": "markdown",
      "source": "# Data Processing Notebook\nThis notebook processes raw data"
    },
    {
      "cell_type": "code",
      "source": "# Load data\ndf = spark.read.parquet('/lakehouse/default/Files/raw/')\nprint(f'Loaded {df.count()} rows')"
    }
  ]
}
EOF

# 2. Create notebook with definition
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "PreloadedNotebook" \
  --type Notebook \
  --definition-file notebook_def.json
```

### Create Pipeline with Definition

```bash
# 1. Create pipeline definition
cat > pipeline_def.json << 'EOF'
{
  "activities": [
    {
      "name": "CopyActivity",
      "type": "Copy",
      "inputs": [],
      "outputs": []
    }
  ]
}
EOF

# 2. Create pipeline
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Test Data Product" \
  --name "PreloadedPipeline" \
  --type DataPipeline \
  --definition-file pipeline_def.json
```

---

## 👥 Part 2: User Management

### Available User Commands

```bash
# List users in workspace
python3 ops/scripts/manage_workspaces.py list-users <WORKSPACE_ID>

# Add user
python3 ops/scripts/manage_workspaces.py add-user <WORKSPACE_ID> <EMAIL> --role <ROLE>

# Remove user
python3 ops/scripts/manage_workspaces.py remove-user <WORKSPACE_ID> <EMAIL>

# Update user role
python3 ops/scripts/manage_workspaces.py update-role <WORKSPACE_ID> <EMAIL> <NEW_ROLE>
```

### Workspace Roles

| Role        | Permissions                                           |
|-------------|-------------------------------------------------------|
| **Admin**   | Full control: manage workspace, items, and users      |
| **Member**  | Create and manage items, cannot manage users          |
| **Contributor** | Edit existing items, cannot create new items      |
| **Viewer**  | Read-only access to all workspace items               |

### Principal Types

- **User** - Individual user account (email address)
- **Group** - Azure AD security group
- **ServicePrincipal** - Application/service principal

---

## 🎯 User Management Examples

### 1. Get Workspace ID First

```bash
# List workspaces and find ID
python3 ops/scripts/manage_workspaces.py list

# Or get specific workspace details
python3 ops/scripts/manage_workspaces.py get --name "Test Data Product"
```

Output will show workspace ID like: `8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 2. List Current Users

```bash
python3 ops/scripts/manage_workspaces.py list-users 8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 3. Add New User as Admin

```bash
python3 ops/scripts/manage_workspaces.py add-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  user@example.com \
  --role Admin
```

### 4. Add New User as Member

```bash
python3 ops/scripts/manage_workspaces.py add-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  developer@example.com \
  --role Member
```

### 5. Add User as Viewer

```bash
python3 ops/scripts/manage_workspaces.py add-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  analyst@example.com \
  --role Viewer
```

### 6. Update Existing User Role

```bash
# Promote viewer to member
python3 ops/scripts/manage_workspaces.py update-role \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  analyst@example.com \
  Member

# Promote member to admin
python3 ops/scripts/manage_workspaces.py update-role \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  developer@example.com \
  Admin
```

### 7. Remove User

```bash
python3 ops/scripts/manage_workspaces.py remove-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  olduser@example.com
```

### 8. Add Service Principal

```bash
python3 ops/scripts/manage_workspaces.py add-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  <service-principal-id> \
  --role Contributor \
  --principal-type ServicePrincipal
```

### 9. Add Azure AD Group

```bash
python3 ops/scripts/manage_workspaces.py add-user \
  8070ecd4-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  <group-object-id> \
  --role Member \
  --principal-type Group
```

---

## 🔄 Complete Workflow Example

### Scenario: Create New Workspace with Items and Users

```bash
#!/bin/bash
# Complete workspace setup script

WORKSPACE_NAME="Analytics Platform"
ENVIRONMENT="dev"

echo "🚀 Setting up complete analytics workspace..."

# Step 1: Create workspace
echo "1️⃣ Creating workspace..."
python3 ops/scripts/manage_workspaces.py create "$WORKSPACE_NAME" \
  -e "$ENVIRONMENT" \
  --description "Analytics platform with full team access"

# Step 2: Get workspace ID
WORKSPACE_ID=$(python3 ops/scripts/manage_workspaces.py get --name "${WORKSPACE_NAME}-${ENVIRONMENT}" --json | jq -r '.id')
echo "   Workspace ID: $WORKSPACE_ID"

# Step 3: Create Fabric items
echo "2️⃣ Creating Fabric items..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}-${ENVIRONMENT}" \
  --name "RawDataLakehouse" \
  --type Lakehouse \
  --description "Raw data storage"

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}-${ENVIRONMENT}" \
  --name "TransformationNotebook" \
  --type Notebook \
  --description "Data transformation logic"

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}-${ENVIRONMENT}" \
  --name "ETLPipeline" \
  --type DataPipeline \
  --description "Main ETL orchestration"

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}-${ENVIRONMENT}" \
  --name "AnalyticsWarehouse" \
  --type Warehouse \
  --description "SQL analytics layer"

# Step 4: Add team members
echo "3️⃣ Adding team members..."

# Add admin
python3 ops/scripts/manage_workspaces.py add-user "$WORKSPACE_ID" \
  admin@example.com --role Admin

# Add data engineers
python3 ops/scripts/manage_workspaces.py add-user "$WORKSPACE_ID" \
  engineer1@example.com --role Member

python3 ops/scripts/manage_workspaces.py add-user "$WORKSPACE_ID" \
  engineer2@example.com --role Member

# Add analysts
python3 ops/scripts/manage_workspaces.py add-user "$WORKSPACE_ID" \
  analyst1@example.com --role Viewer

python3 ops/scripts/manage_workspaces.py add-user "$WORKSPACE_ID" \
  analyst2@example.com --role Viewer

# Step 5: List everything
echo "4️⃣ Verification..."
echo ""
echo "Items created:"
python3 ops/scripts/manage_fabric_items.py list --workspace "${WORKSPACE_NAME}-${ENVIRONMENT}"

echo ""
echo "Users added:"
python3 ops/scripts/manage_workspaces.py list-users "$WORKSPACE_ID"

echo ""
echo "✅ Workspace setup complete!"
```

---

## 🔧 Item Management Operations

### Get Item Details

```bash
python3 ops/scripts/manage_fabric_items.py get \
  --workspace "Test Data Product" \
  --item-name "MyLakehouse" \
  --type Lakehouse
```

### Update Item

```bash
# Rename item
python3 ops/scripts/manage_fabric_items.py update \
  --workspace "Test Data Product" \
  --item-name "OldName" \
  --new-name "NewName" \
  --type Lakehouse

# Update description
python3 ops/scripts/manage_fabric_items.py update \
  --workspace "Test Data Product" \
  --item-name "MyLakehouse" \
  --description "Updated description" \
  --type Lakehouse
```

### Delete Item

```bash
python3 ops/scripts/manage_fabric_items.py delete \
  --workspace "Test Data Product" \
  --item-name "OldLakehouse" \
  --type Lakehouse \
  --force
```

### Get Item Definition (Export)

```bash
python3 ops/scripts/manage_fabric_items.py get-definition \
  --workspace "Test Data Product" \
  --item-name "MyNotebook" \
  --type Notebook \
  --output notebook_export.json
```

### Bulk Delete Items

```bash
# Delete all notebooks in workspace
python3 ops/scripts/manage_fabric_items.py bulk-delete \
  --workspace "Test Data Product" \
  --type Notebook \
  --force

# Delete specific items by ID
python3 ops/scripts/manage_fabric_items.py bulk-delete \
  --workspace "Test Data Product" \
  --ids item-id-1 item-id-2 item-id-3 \
  --force

# Delete from file
cat > items_to_delete.txt << EOF
item-id-1
item-id-2
item-id-3
EOF

python3 ops/scripts/manage_fabric_items.py bulk-delete \
  --workspace "Test Data Product" \
  --file items_to_delete.txt \
  --force
```

---

## 🔍 Query and Filter Examples

### Find All Lakehouses Across Workspaces

```bash
# List all workspaces
for ws in $(python3 ops/scripts/manage_workspaces.py list --json | jq -r '.[].displayName'); do
  echo "Workspace: $ws"
  python3 ops/scripts/manage_fabric_items.py list --workspace "$ws" --type Lakehouse
  echo ""
done
```

### Count Items by Type

```bash
WORKSPACE="Test Data Product"

echo "Item count summary for $WORKSPACE:"
for type in Lakehouse Notebook DataPipeline Warehouse; do
  count=$(python3 ops/scripts/manage_fabric_items.py list --workspace "$WORKSPACE" --type "$type" --json | jq length)
  echo "  $type: $count"
done
```

---

## 📊 Python API Usage (Programmatic)

For those who prefer Python code over CLI commands:

### Create Items Programmatically

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'ops/scripts')

from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.workspace_manager import WorkspaceManager

# Initialize managers
item_mgr = FabricItemManager()
ws_mgr = WorkspaceManager()

# Get workspace ID
workspaces = ws_mgr.list_workspaces()
workspace_id = next(ws['id'] for ws in workspaces if ws['displayName'] == 'Test Data Product')

# Create lakehouse
lakehouse = item_mgr.create_item(
    workspace_id=workspace_id,
    display_name='MyLakehouse',
    item_type=FabricItemType.LAKEHOUSE,
    description='Main data lakehouse'
)
print(f"Created lakehouse: {lakehouse.id}")

# Create notebook
notebook = item_mgr.create_item(
    workspace_id=workspace_id,
    display_name='ProcessingNotebook',
    item_type=FabricItemType.NOTEBOOK,
    description='ETL notebook'
)
print(f"Created notebook: {notebook.id}")

# Create pipeline
pipeline = item_mgr.create_item(
    workspace_id=workspace_id,
    display_name='ETLPipeline',
    item_type=FabricItemType.DATA_PIPELINE,
    description='Main pipeline'
)
print(f"Created pipeline: {pipeline.id}")
```

### Manage Users Programmatically

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'ops/scripts')

from utilities.workspace_manager import WorkspaceManager, WorkspaceRole

# Initialize manager
mgr = WorkspaceManager()

# Get workspace ID
workspaces = mgr.list_workspaces()
workspace_id = next(ws['id'] for ws in workspaces if ws['displayName'] == 'Test Data Product')

# Add admin
mgr.add_user(
    workspace_id=workspace_id,
    principal_id='admin@example.com',
    principal_type='User',
    role=WorkspaceRole.ADMIN
)
print("Added admin user")

# Add member
mgr.add_user(
    workspace_id=workspace_id,
    principal_id='developer@example.com',
    principal_type='User',
    role=WorkspaceRole.MEMBER
)
print("Added member user")

# Add viewer
mgr.add_user(
    workspace_id=workspace_id,
    principal_id='analyst@example.com',
    principal_type='User',
    role=WorkspaceRole.VIEWER
)
print("Added viewer user")

# List all users
users = mgr.list_users(workspace_id)
print(f"\nTotal users: {len(users)}")
for user in users:
    print(f"  - {user['identifier']}: {user['workspaceRole']}")

# Update role
mgr.update_user_role(
    workspace_id=workspace_id,
    principal_id='analyst@example.com',
    new_role=WorkspaceRole.CONTRIBUTOR
)
print("Updated analyst to Contributor role")
```

---

## 🎓 Best Practices

### 1. Item Naming Conventions

```bash
# Use descriptive, consistent names
✅ RawDataLakehouse
✅ TransformedDataLakehouse
✅ AnalyticsWarehouse
✅ DailyETLPipeline

❌ lakehouse1
❌ test
❌ notebook
```

### 2. User Role Assignment

```
Development:
- Admins: Lead developers, workspace owners
- Members: Developers, data engineers
- Contributors: QA, testers (can edit, not create)
- Viewers: Stakeholders, analysts

Production:
- Admins: DevOps, platform team
- Members: Limited (specific automation accounts)
- Contributors: None
- Viewers: Business users, analysts
```

### 3. Item Organization

```
Standard workspace structure:
├── Lakehouses (Raw, Processed, Curated)
├── Notebooks (ETL, Analysis)
├── Pipelines (Orchestration)
├── Warehouses (Serving layer)
└── Reports (Visualization)
```

### 4. Error Handling

Always check outputs:

```bash
# Check if workspace exists before adding items
if python3 ops/scripts/manage_workspaces.py get --name "MyWorkspace" &>/dev/null; then
  echo "Workspace exists, proceeding..."
else
  echo "ERROR: Workspace not found!"
  exit 1
fi
```

---

## 🔗 Related Documentation

- **[`WORKSPACE_MANAGEMENT_QUICKREF.md`](WORKSPACE_MANAGEMENT_QUICKREF.md)** - Quick workspace commands
- **[`../getting-started/REAL_FABRIC_QUICKSTART.md`](../getting-started/REAL_FABRIC_QUICKSTART.md)** - Step-by-step execution guide
- **[`../development-maintenance/CODEBASE_REDUNDANCY_AUDIT.md`](../development-maintenance/CODEBASE_REDUNDANCY_AUDIT.md)** - Redundancy review
- **[`../fabric-items-crud/FABRIC_ITEM_CRUD_QUICKREF.md`](../fabric-items-crud/FABRIC_ITEM_CRUD_QUICKREF.md)** - Fabric items CRUD operations

---

## ✅ Summary

**Available Capabilities:**

1. ✅ Create 26+ types of Fabric items in any workspace
2. ✅ List, get, update, delete items
3. ✅ Add users (User, Group, ServicePrincipal) with any role
4. ✅ Update user roles
5. ✅ Remove users
6. ✅ List all users and their roles
7. ✅ Bulk operations for items and users

**Primary Tools:**
- `ops/scripts/manage_fabric_items.py` - Item CRUD operations
- `ops/scripts/manage_workspaces.py` - Workspace and user management

**Best Practice:** Always use these existing tools to avoid creating redundant scripts! 🎯

---

*Generated: 21 October 2025*  
*Last Updated: After redundancy audit*  
*Tools Version: Current production*
