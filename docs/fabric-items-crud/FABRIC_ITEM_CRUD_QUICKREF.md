# Fabric Item CRUD - Quick Reference Guide

## Quick Start

### Prerequisites
```bash
# Environment variables required
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

## CLI Commands

### List Items
```bash
# List all items
python ops/scripts/manage_fabric_items.py list --workspace WORKSPACE_NAME

# List specific type
python ops/scripts/manage_fabric_items.py list --workspace WORKSPACE_NAME --type Lakehouse

# JSON output
python ops/scripts/manage_fabric_items.py list --workspace WORKSPACE_NAME --json
```

### Get Item Details
```bash
# By name
python ops/scripts/manage_fabric_items.py get \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse"

# By ID
python ops/scripts/manage_fabric_items.py get \
    --workspace WORKSPACE_NAME \
    --item-id "item-guid"

# JSON output
python ops/scripts/manage_fabric_items.py get \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse" \
    --json
```

### Create Items
```bash
# Create lakehouse (no definition needed)
python ops/scripts/manage_fabric_items.py create \
    --workspace WORKSPACE_NAME \
    --name "MyLakehouse" \
    --type Lakehouse \
    --description "Development lakehouse"

# Create warehouse
python ops/scripts/manage_fabric_items.py create \
    --workspace WORKSPACE_NAME \
    --name "MyWarehouse" \
    --type Warehouse

# Create notebook with definition
python ops/scripts/manage_fabric_items.py create \
    --workspace WORKSPACE_NAME \
    --name "MyNotebook" \
    --type Notebook \
    --definition-file notebook.json

# Create data pipeline
python ops/scripts/manage_fabric_items.py create \
    --workspace WORKSPACE_NAME \
    --name "MyPipeline" \
    --type DataPipeline \
    --definition-file pipeline.json
```

### Update Items
```bash
# Update name
python ops/scripts/manage_fabric_items.py update \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse" \
    --new-name "MyLakehouse_v2"

# Update description
python ops/scripts/manage_fabric_items.py update \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse" \
    --description "Updated description"

# Update both
python ops/scripts/manage_fabric_items.py update \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse" \
    --new-name "MyLakehouse_v2" \
    --description "Updated description"
```

### Delete Items
```bash
# Delete with confirmation
python ops/scripts/manage_fabric_items.py delete \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse"

# Delete without confirmation
python ops/scripts/manage_fabric_items.py delete \
    --workspace WORKSPACE_NAME \
    --item-name "MyLakehouse" \
    --force

# Delete by ID
python ops/scripts/manage_fabric_items.py delete \
    --workspace WORKSPACE_NAME \
    --item-id "item-guid" \
    --force
```

### Get Item Definition
```bash
# Get and display
python ops/scripts/manage_fabric_items.py get-definition \
    --workspace WORKSPACE_NAME \
    --item-name "MyNotebook"

# Save to file
python ops/scripts/manage_fabric_items.py get-definition \
    --workspace WORKSPACE_NAME \
    --item-name "MyNotebook" \
    --output notebook_definition.json

# With format
python ops/scripts/manage_fabric_items.py get-definition \
    --workspace WORKSPACE_NAME \
    --item-name "MyReport" \
    --format "pbix" \
    --output report.json
```

### Bulk Delete
```bash
# Delete by type
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace WORKSPACE_NAME \
    --type Notebook \
    --force

# Delete specific IDs
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace WORKSPACE_NAME \
    --ids "id1" "id2" "id3" \
    --force

# Delete from file
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace WORKSPACE_NAME \
    --file item_ids.txt \
    --force

# File format (item_ids.txt):
# One ID per line, # for comments
# abc123-def456-ghi789
# xyz789-uvw456-rst123
# # This is a comment - ignored
```

## Python API

### Basic Usage
```python
from ops.scripts.utilities.fabric_item_manager import (
    FabricItemManager,
    FabricItemType
)

# Initialize
manager = FabricItemManager()

# Create item
lakehouse = manager.create_item(
    workspace_id="workspace-guid",
    display_name="MyLakehouse",
    item_type=FabricItemType.LAKEHOUSE,
    description="Development lakehouse"
)

# Get item
item = manager.get_item(
    workspace_id="workspace-guid",
    item_id="item-guid"
)

# Update item
updated = manager.update_item(
    workspace_id="workspace-guid",
    item_id="item-guid",
    display_name="NewName",
    description="New description"
)

# Delete item
success = manager.delete_item(
    workspace_id="workspace-guid",
    item_id="item-guid"
)

# List items
all_items = manager.list_items(workspace_id="workspace-guid")

# List filtered
notebooks = manager.list_items(
    workspace_id="workspace-guid",
    item_type=FabricItemType.NOTEBOOK
)
```

### Advanced Operations
```python
# Find by name
item = manager.find_item_by_name(
    workspace_id="workspace-guid",
    display_name="MyLakehouse",
    item_type=FabricItemType.LAKEHOUSE
)

# Create or update (upsert)
item, is_new = manager.create_or_update_item(
    workspace_id="workspace-guid",
    display_name="MyLakehouse",
    item_type=FabricItemType.LAKEHOUSE,
    description="Development lakehouse"
)

if is_new:
    print("Created new item")
else:
    print("Updated existing item")

# Bulk delete
results = manager.bulk_delete_items(
    workspace_id="workspace-guid",
    item_ids=["id1", "id2", "id3"]
)

print(f"Deleted: {results['succeeded']}/{results['total']}")
print(f"Failed: {results['failed']}")
for error in results['errors']:
    print(f"  {error['item_id']}: {error['error']}")
```

### Working with Definitions
```python
from ops.scripts.utilities.fabric_item_manager import (
    create_notebook_definition,
    create_pipeline_definition,
    create_spark_job_definition
)

# Create notebook with definition
notebook_json = {
    "cells": [
        {
            "cell_type": "code",
            "source": "print('Hello World')"
        }
    ]
}
definition = create_notebook_definition(notebook_json)

notebook = manager.create_item(
    workspace_id="workspace-guid",
    display_name="MyNotebook",
    item_type=FabricItemType.NOTEBOOK,
    definition=definition
)

# Get item definition
definition = manager.get_item_definition(
    workspace_id="workspace-guid",
    item_id=notebook.id
)

# Update definition
from ops.scripts.utilities.fabric_item_manager import ItemDefinition
new_definition = ItemDefinition(...)

manager.update_item_definition(
    workspace_id="workspace-guid",
    item_id=notebook.id,
    definition=new_definition
)
```

## Supported Item Types

### Data Factory
- `DataPipeline`
- `MountedDataFactory`
- `CopyJob`

### Data Engineering
- `Environment`
- `GraphQLApi`
- `Lakehouse` ⭐
- `Notebook` ⭐
- `SparkJobDefinition`

### Data Science
- `MLModel`
- `MLExperiment`

### Data Warehouse
- `Datamart`
- `MirroredAzureDatabricksCatalog`
- `MirroredDatabase`
- `MirroredWarehouse`
- `SQLEndpoint`
- `Warehouse` ⭐

### Power BI
- `Dashboard`
- `Dataflow`
- `PaginatedReport`
- `Report`
- `SemanticModel`

### Real-Time Intelligence
- `DigitalTwinBuilder`
- `DigitalTwinBuilderFlow`
- `Eventhouse`
- `Eventstream`
- `GraphQuerySet`
- `KQLDatabase`
- `KQLQueryset`
- `KQLDashboard`
- `Reflex`

### Other
- `HLSCohort`

⭐ = Most commonly used

## Common Workflows

### Setup New Workspace with Items
```bash
# 1. Create workspace (-e flag before subcommand)
python ops/scripts/manage_workspaces.py -e dev create \
    --name analytics

# 2. Create lakehouse
python ops/scripts/manage_fabric_items.py create \
    --workspace analytics \
    --name bronze_lakehouse \
    --type Lakehouse

# 3. Create notebooks
for nb in ingestion transformation validation; do
    python ops/scripts/manage_fabric_items.py create \
        --workspace dev-analytics \
        --name "${nb}_notebook" \
        --type Notebook
done

# 4. Create warehouse
python ops/scripts/manage_fabric_items.py create \
    --workspace dev-analytics \
    --name analytics_warehouse \
    --type Warehouse
```

### Clone Items to Another Workspace
```bash
# 1. Get definitions from source
python ops/scripts/manage_fabric_items.py get-definition \
    --workspace source-workspace \
    --item-name "MyNotebook" \
    --output notebook_def.json

# 2. Create in target with definition
python ops/scripts/manage_fabric_items.py create \
    --workspace target-workspace \
    --name "MyNotebook" \
    --type Notebook \
    --definition-file notebook_def.json
```

### Cleanup Test Items
```bash
# Delete all test notebooks
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace test-workspace \
    --type Notebook \
    --force

# Delete all test lakehouses
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace test-workspace \
    --type Lakehouse \
    --force
```

### Audit Workspace Items
```bash
# Get all items as JSON
python ops/scripts/manage_fabric_items.py list \
    --workspace prod-workspace \
    --json > workspace_inventory.json

# Filter by type
python ops/scripts/manage_fabric_items.py list \
    --workspace prod-workspace \
    --type Lakehouse \
    --json > lakehouses.json
```

## Python Script Examples

### Create Standard Workspace Setup
```python
#!/usr/bin/env python3
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.fabric_item_manager import FabricItemManager, FabricItemType

def setup_workspace(workspace_name, environment="dev"):
    """Create workspace with standard items"""
    ws_mgr = WorkspaceManager(environment=environment)
    item_mgr = FabricItemManager()
    
    # Create workspace
    workspace = ws_mgr.create_workspace(environment, workspace_name)
    workspace_id = workspace['id']
    
    # Create medallion lakehouses
    for layer in ['bronze', 'silver', 'gold']:
        item_mgr.create_item(
            workspace_id=workspace_id,
            display_name=f"{layer}_lakehouse",
            item_type=FabricItemType.LAKEHOUSE,
            description=f"{layer.title()} layer lakehouse"
        )
    
    # Create warehouse
    item_mgr.create_item(
        workspace_id=workspace_id,
        display_name="analytics_warehouse",
        item_type=FabricItemType.WAREHOUSE,
        description="Analytics warehouse"
    )
    
    # Create notebooks
    for notebook in ['ingestion', 'transformation', 'validation']:
        item_mgr.create_item(
            workspace_id=workspace_id,
            display_name=f"{notebook}_notebook",
            item_type=FabricItemType.NOTEBOOK,
            description=f"{notebook.title()} notebook"
        )
    
    print(f"✓ Workspace '{workspace_name}' setup complete")

if __name__ == '__main__':
    setup_workspace("analytics-workspace", "dev")
```

### Inventory Report
```python
#!/usr/bin/env python3
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.fabric_item_manager import FabricItemManager
from collections import Counter

def generate_inventory_report(environment="dev"):
    """Generate inventory report for all workspaces"""
    ws_mgr = WorkspaceManager(environment=environment)
    item_mgr = FabricItemManager()
    
    workspaces = ws_mgr.list_workspaces()
    
    print(f"\n{'='*60}")
    print(f"Fabric Inventory Report - {environment.upper()}")
    print(f"{'='*60}\n")
    
    total_items = 0
    type_counts = Counter()
    
    for workspace in workspaces:
        ws_name = workspace['displayName']
        ws_id = workspace['id']
        
        items = item_mgr.list_items(ws_id)
        
        print(f"Workspace: {ws_name}")
        print(f"  Items: {len(items)}")
        
        if items:
            item_types = Counter(item.type.value for item in items)
            for item_type, count in item_types.items():
                print(f"    - {item_type}: {count}")
                type_counts[item_type] += count
        
        print()
        total_items += len(items)
    
    print(f"{'='*60}")
    print(f"Summary:")
    print(f"  Total Workspaces: {len(workspaces)}")
    print(f"  Total Items: {total_items}")
    print(f"\nItems by Type:")
    for item_type, count in type_counts.most_common():
        print(f"  {item_type}: {count}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    generate_inventory_report("dev")
```

### Cleanup Old Items
```python
#!/usr/bin/env python3
from ops.scripts.utilities.fabric_item_manager import FabricItemManager
from datetime import datetime, timedelta

def cleanup_old_items(workspace_id, days_old=30):
    """Delete items older than specified days"""
    manager = FabricItemManager()
    items = manager.list_items(workspace_id)
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    old_items = [
        item for item in items
        if item.created_date and item.created_date < cutoff_date
    ]
    
    if not old_items:
        print(f"No items older than {days_old} days found")
        return
    
    print(f"Found {len(old_items)} items older than {days_old} days:")
    for item in old_items:
        print(f"  - {item.display_name} ({item.type.value})")
    
    response = input(f"\nDelete {len(old_items)} items? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    item_ids = [item.id for item in old_items]
    results = manager.bulk_delete_items(workspace_id, item_ids)
    
    print(f"\n✓ Deleted {results['succeeded']}/{results['total']} items")

if __name__ == '__main__':
    cleanup_old_items("workspace-guid", days_old=30)
```

## Troubleshooting

### Common Errors

**Error: "Workspace not found"**
```bash
# List workspaces to check name (-e flag before subcommand)
python ops/scripts/manage_workspaces.py -e dev list
```

**Error: "Item not found"**
```bash
# List items to check name
python ops/scripts/manage_fabric_items.py list --workspace WORKSPACE_NAME
```

**Error: "Authentication failed"**
```bash
# Check environment variables
echo $AZURE_TENANT_ID
echo $AZURE_CLIENT_ID
echo $AZURE_CLIENT_SECRET  # Should show value (not empty)
```

**Error: "Permission denied"**
- Verify service principal has workspace admin role
- Check Fabric tenant setting: "Service principals can use Fabric APIs"
- Verify Application permission: Workspace.ReadWrite.All

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from ops.scripts.utilities.fabric_item_manager import FabricItemManager
manager = FabricItemManager()
# Now all API calls will be logged
```

## Tips & Best Practices

1. **Always use type filters** when listing large workspaces
2. **Test in dev** before running in production
3. **Use `--json`** for automation and parsing
4. **Cache workspace IDs** in long-running scripts
5. **Use bulk operations** for multiple items
6. **Always confirm** before bulk deletes (unless automated)
7. **Log all operations** in production scripts
8. **Version control** item definitions
9. **Document naming conventions** for your team
10. **Use descriptive descriptions** for all items

## Getting Help

```bash
# CLI help
python ops/scripts/manage_fabric_items.py --help

# Command-specific help
python ops/scripts/manage_fabric_items.py create --help
python ops/scripts/manage_fabric_items.py list --help

# Python API help
python -c "from ops.scripts.utilities.fabric_item_manager import FabricItemManager; help(FabricItemManager)"
```

---

**Quick Reference Version**: 1.0  
**Last Updated**: October 11, 2025  
**For Full Documentation**: See `FABRIC_ITEM_CRUD_DESIGN.md`
