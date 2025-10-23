#!/usr/bin/env python3
"""
CLI for managing Microsoft Fabric items (CRUD operations)
Supports all Fabric item types: Lakehouses, Notebooks, Pipelines, Warehouses, etc.
"""
import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ops.scripts.utilities.fabric_item_manager import (
    FabricItemManager,
    FabricItemType,
    FabricItem,
    ItemDefinition,
    create_notebook_definition,
    create_pipeline_definition,
    create_spark_job_definition,
)
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_info as print_info,
    console_warning as print_warning,
    console_table as print_table,
    console_json as print_json,
)


def get_workspace_id(workspace_name: str, workspace_manager: WorkspaceManager) -> str:
    """Get workspace ID from name"""
    workspaces = workspace_manager.list_workspaces()
    for ws in workspaces:
        if ws["displayName"] == workspace_name:
            return ws["id"]
    raise ValueError(f"Workspace '{workspace_name}' not found")


def cmd_list_items(args):
    """List items in a workspace"""
    print_info(f"Listing items in workspace: {args.workspace}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        item_type = None
        if args.type:
            try:
                item_type = FabricItemType(args.type)
            except ValueError:
                print_error(f"Invalid item type: {args.type}")
                print_info(
                    f"Valid types: {', '.join([t.value for t in FabricItemType])}"
                )
                return 1

        items = manager.list_items(workspace_id, item_type)

        if args.json:
            print_json(
                [
                    {
                        "id": item.id,
                        "displayName": item.display_name,
                        "type": item.type.value if item.type else None,
                        "description": item.description,
                        "createdDate": (
                            item.created_date.isoformat() if item.created_date else None
                        ),
                        "modifiedDate": (
                            item.modified_date.isoformat()
                            if item.modified_date
                            else None
                        ),
                    }
                    for item in items
                ]
            )
        else:
            if not items:
                print_warning("No items found")
                return 0

            headers = ["Display Name", "Type", "ID", "Created"]
            rows = []
            for item in items:
                rows.append(
                    [
                        item.display_name,
                        item.type.value if item.type else "Unknown",
                        item.id[:8] + "..." if item.id else "N/A",
                        (
                            item.created_date.strftime("%Y-%m-%d")
                            if item.created_date
                            else "N/A"
                        ),
                    ]
                )

            print_table(headers, rows)
            print_success(f"\nFound {len(items)} item(s)")

        return 0

    except Exception as e:
        print_error(f"Failed to list items: {str(e)}")
        return 1


def cmd_get_item(args):
    """Get details of a specific item"""
    print_info(f"Getting item: {args.item_name or args.item_id}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        # Find item by name or ID
        if args.item_name:
            item_type = FabricItemType(args.type) if args.type else None
            item = manager.find_item_by_name(workspace_id, args.item_name, item_type)
            if not item:
                print_error(f"Item '{args.item_name}' not found")
                return 1
        else:
            item = manager.get_item(workspace_id, args.item_id)

        if args.json:
            print_json(
                {
                    "id": item.id,
                    "displayName": item.display_name,
                    "type": item.type.value if item.type else None,
                    "description": item.description,
                    "workspaceId": item.workspace_id,
                    "createdDate": (
                        item.created_date.isoformat() if item.created_date else None
                    ),
                    "modifiedDate": (
                        item.modified_date.isoformat() if item.modified_date else None
                    ),
                }
            )
        else:
            print_success(f"Item: {item.display_name}")
            print_info(f"  ID: {item.id}")
            print_info(f"  Type: {item.type.value if item.type else 'Unknown'}")
            if item.description:
                print_info(f"  Description: {item.description}")
            print_info(f"  Workspace ID: {item.workspace_id or workspace_id}")
            if item.created_date:
                print_info(
                    f"  Created: {item.created_date.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            if item.modified_date:
                print_info(
                    f"  Modified: {item.modified_date.strftime('%Y-%m-%d %H:%M:%S')}"
                )

        return 0

    except Exception as e:
        print_error(f"Failed to get item: {str(e)}")
        return 1


def cmd_create_item(args):
    """Create a new Fabric item"""
    print_info(f"Creating {args.type} '{args.name}' in workspace: {args.workspace}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        try:
            item_type = FabricItemType(args.type)
        except ValueError:
            print_error(f"Invalid item type: {args.type}")
            print_info(f"Valid types: {', '.join([t.value for t in FabricItemType])}")
            return 1

        # Prepare definition if content file provided
        definition = None
        if args.definition_file:
            definition_path = Path(args.definition_file)
            if not definition_path.exists():
                print_error(f"Definition file not found: {args.definition_file}")
                return 1

            with open(definition_path, "r") as f:
                content = json.load(f)

            # Create appropriate definition based on type
            if item_type == FabricItemType.NOTEBOOK:
                definition = create_notebook_definition(content)
            elif item_type == FabricItemType.DATA_PIPELINE:
                definition = create_pipeline_definition(content)
            elif item_type == FabricItemType.SPARK_JOB_DEFINITION:
                main_content = content.get("main", "")
                additional = content.get("additional", {})
                definition = create_spark_job_definition(main_content, additional)

        item = manager.create_item(
            workspace_id=workspace_id,
            display_name=args.name,
            item_type=item_type,
            description=args.description,
            definition=definition,
        )

        print_success(f"Successfully created {item_type.value} '{item.display_name}'")
        print_info(f"Item ID: {item.id}")

        return 0

    except Exception as e:
        print_error(f"Failed to create item: {str(e)}")
        return 1


def cmd_update_item(args):
    """Update an existing Fabric item"""
    print_info(f"Updating item: {args.item_name or args.item_id}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        # Find item
        if args.item_name:
            item_type = FabricItemType(args.type) if args.type else None
            item = manager.find_item_by_name(workspace_id, args.item_name, item_type)
            if not item:
                print_error(f"Item '{args.item_name}' not found")
                return 1
            item_id = item.id
        else:
            item_id = args.item_id

        # Update properties
        updated_item = manager.update_item(
            workspace_id=workspace_id,
            item_id=item_id,
            display_name=args.new_name,
            description=args.description,
        )

        print_success(f"Successfully updated item '{updated_item.display_name}'")

        return 0

    except Exception as e:
        print_error(f"Failed to update item: {str(e)}")
        return 1


def cmd_delete_item(args):
    """Delete a Fabric item"""
    print_info(f"Deleting item: {args.item_name or args.item_id}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        # Find item
        if args.item_name:
            item_type = FabricItemType(args.type) if args.type else None
            item = manager.find_item_by_name(workspace_id, args.item_name, item_type)
            if not item:
                print_error(f"Item '{args.item_name}' not found")
                return 1
            item_id = item.id
            item_name = item.display_name
        else:
            item_id = args.item_id
            item_name = item_id

        # Confirm deletion
        if not args.force:
            response = input(
                f"Are you sure you want to delete '{item_name}'? Type 'DELETE' to confirm: "
            )
            if response != "DELETE":
                print_warning("Deletion cancelled")
                return 0

        manager.delete_item(workspace_id, item_id)
        print_success(f"Successfully deleted item '{item_name}'")

        return 0

    except Exception as e:
        print_error(f"Failed to delete item: {str(e)}")
        return 1


def cmd_get_definition(args):
    """Get item definition"""
    print_info(f"Getting definition for: {args.item_name or args.item_id}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        # Find item
        if args.item_name:
            item_type = FabricItemType(args.type) if args.type else None
            item = manager.find_item_by_name(workspace_id, args.item_name, item_type)
            if not item:
                print_error(f"Item '{args.item_name}' not found")
                return 1
            item_id = item.id
        else:
            item_id = args.item_id

        definition = manager.get_item_definition(workspace_id, item_id, args.format)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(definition, f, indent=2)
            print_success(f"Definition saved to: {args.output}")
        else:
            print_json(definition)

        return 0

    except Exception as e:
        print_error(f"Failed to get definition: {str(e)}")
        return 1


def cmd_bulk_delete(args):
    """Bulk delete items"""
    print_warning(f"Bulk deleting items from workspace: {args.workspace}")

    try:
        manager = FabricItemManager()
        workspace_mgr = WorkspaceManager()

        workspace_id = get_workspace_id(args.workspace, workspace_mgr)

        # Get item IDs
        item_ids = []
        if args.file:
            with open(args.file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        item_ids.append(line)
        elif args.ids:
            item_ids = args.ids
        elif args.type:
            # Delete all items of a specific type
            item_type = FabricItemType(args.type)
            items = manager.list_items(workspace_id, item_type)
            item_ids = [item.id for item in items]
        else:
            print_error("Must provide --ids, --file, or --type")
            return 1

        if not item_ids:
            print_warning("No items to delete")
            return 0

        print_info(f"Items to delete: {len(item_ids)}")

        # Confirm deletion
        if not args.force:
            response = input(
                f"Delete {len(item_ids)} item(s)? Type 'DELETE {len(item_ids)}' to confirm: "
            )
            if response != f"DELETE {len(item_ids)}":
                print_warning("Deletion cancelled")
                return 0

        results = manager.bulk_delete_items(workspace_id, item_ids)

        print_success(f"Deleted {results['succeeded']}/{results['total']} items")
        if results["failed"] > 0:
            print_error(f"Failed to delete {results['failed']} items")
            for error in results["errors"]:
                print_error(f"  {error['item_id']}: {error['error']}")

        return 0 if results["failed"] == 0 else 1

    except Exception as e:
        print_error(f"Failed to bulk delete: {str(e)}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Manage Microsoft Fabric items (CRUD operations)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all items in a workspace
  %(prog)s list --workspace dev-workspace
  
  # List only notebooks
  %(prog)s list --workspace dev-workspace --type Notebook
  
  # Create a lakehouse
  %(prog)s create --workspace dev-workspace --name MyLakehouse --type Lakehouse
  
  # Create a notebook with definition
  %(prog)s create --workspace dev-workspace --name MyNotebook --type Notebook --definition notebook.json
  
  # Get item details
  %(prog)s get --workspace dev-workspace --item-name MyLakehouse
  
  # Update item
  %(prog)s update --workspace dev-workspace --item-name MyLakehouse --new-name MyLakehouse_v2
  
  # Delete item
  %(prog)s delete --workspace dev-workspace --item-name MyLakehouse --force
  
  # Get item definition
  %(prog)s get-definition --workspace dev-workspace --item-name MyNotebook --output notebook_def.json
  
  # Bulk delete by type
  %(prog)s bulk-delete --workspace dev-workspace --type Notebook --force
  
  # Bulk delete from file
  %(prog)s bulk-delete --workspace dev-workspace --file item_ids.txt
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # List command
    list_parser = subparsers.add_parser("list", help="List items in workspace")
    list_parser.add_argument("--workspace", required=True, help="Workspace name")
    list_parser.add_argument("--type", help="Filter by item type")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_parser.set_defaults(func=cmd_list_items)

    # Get command
    get_parser = subparsers.add_parser("get", help="Get item details")
    get_parser.add_argument("--workspace", required=True, help="Workspace name")
    get_parser.add_argument("--item-name", help="Item display name")
    get_parser.add_argument("--item-id", help="Item ID")
    get_parser.add_argument("--type", help="Item type (for name lookup)")
    get_parser.add_argument("--json", action="store_true", help="Output as JSON")
    get_parser.set_defaults(func=cmd_get_item)

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new item")
    create_parser.add_argument("--workspace", required=True, help="Workspace name")
    create_parser.add_argument("--name", required=True, help="Item display name")
    create_parser.add_argument("--type", required=True, help="Item type")
    create_parser.add_argument("--description", help="Item description")
    create_parser.add_argument(
        "--definition-file", help="JSON file with item definition"
    )
    create_parser.set_defaults(func=cmd_create_item)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an item")
    update_parser.add_argument("--workspace", required=True, help="Workspace name")
    update_parser.add_argument("--item-name", help="Item display name")
    update_parser.add_argument("--item-id", help="Item ID")
    update_parser.add_argument("--type", help="Item type (for name lookup)")
    update_parser.add_argument("--new-name", help="New display name")
    update_parser.add_argument("--description", help="New description")
    update_parser.set_defaults(func=cmd_update_item)

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("--workspace", required=True, help="Workspace name")
    delete_parser.add_argument("--item-name", help="Item display name")
    delete_parser.add_argument("--item-id", help="Item ID")
    delete_parser.add_argument("--type", help="Item type (for name lookup)")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete_item)

    # Get definition command
    getdef_parser = subparsers.add_parser("get-definition", help="Get item definition")
    getdef_parser.add_argument("--workspace", required=True, help="Workspace name")
    getdef_parser.add_argument("--item-name", help="Item display name")
    getdef_parser.add_argument("--item-id", help="Item ID")
    getdef_parser.add_argument("--type", help="Item type (for name lookup)")
    getdef_parser.add_argument("--format", help="Definition format")
    getdef_parser.add_argument("--output", help="Output file path")
    getdef_parser.set_defaults(func=cmd_get_definition)

    # Bulk delete command
    bulkdel_parser = subparsers.add_parser("bulk-delete", help="Delete multiple items")
    bulkdel_parser.add_argument("--workspace", required=True, help="Workspace name")
    bulkdel_parser.add_argument("--ids", nargs="+", help="Item IDs to delete")
    bulkdel_parser.add_argument("--file", help="File with item IDs (one per line)")
    bulkdel_parser.add_argument("--type", help="Delete all items of this type")
    bulkdel_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation"
    )
    bulkdel_parser.set_defaults(func=cmd_bulk_delete)

    args = parser.parse_args()

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
