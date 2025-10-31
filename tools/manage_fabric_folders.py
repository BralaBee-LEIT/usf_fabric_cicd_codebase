#!/usr/bin/env python3
"""
Microsoft Fabric Folder Management CLI

Interactive command-line tool for managing folders and organizing items
in Microsoft Fabric workspaces.

Usage:
    # Create folder
    python manage_fabric_folders.py create --workspace "Analytics" --name "Bronze Layer"
    
    # Create subfolder
    python manage_fabric_folders.py create --workspace "Analytics" --name "Archive" --parent "Bronze Layer"
    
    # List folders
    python manage_fabric_folders.py list --workspace "Analytics"
    
    # Show folder tree
    python manage_fabric_folders.py tree --workspace "Analytics" --show-items
    
    # Move folder
    python manage_fabric_folders.py move --workspace "Analytics" --folder "Archive" --parent "Bronze Layer"
    
    # Delete folder
    python manage_fabric_folders.py delete --workspace "Analytics" --folder "Archive" --force
    
    # Create structure from template
    python manage_fabric_folders.py create-structure --workspace "Analytics" --template medallion
    
    # Move items to folder
    python manage_fabric_folders.py move-items --workspace "Analytics" --folder "Bronze Layer" --items item1,item2,item3

Environment Variables:
    FABRIC_WORKSPACE_ID: Default workspace GUID (optional)
    AZURE_TENANT_ID: Azure AD tenant ID (required)
    AZURE_CLIENT_ID: Service principal client ID (required)
    AZURE_CLIENT_SECRET: Service principal client secret (required)

Examples:
    # Medallion architecture structure
    python manage_fabric_folders.py create-structure \\
        --workspace "Data Platform" \\
        --template medallion
    
    # Custom structure from YAML
    python manage_fabric_folders.py create-structure \\
        --workspace "Analytics" \\
        --config folder_structure.yaml
"""

import os
import sys
import argparse
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ops.scripts.utilities.fabric_folder_manager import (
    FabricFolderManager,
    FolderValidationError,
    FolderOperationError
)
from ops.scripts.utilities.fabric_api import FabricClient
from ops.scripts.utilities.output import (
    console_info as print_info,
    console_success as print_success,
    console_warning as print_warning,
    console_error as print_error,
)


# ============================================================================
# FOLDER STRUCTURE TEMPLATES
# ============================================================================

TEMPLATES = {
    "medallion": {
        "name": "Medallion Architecture",
        "description": "Bronze/Silver/Gold lakehouse layers",
        "structure": {
            "Bronze Layer": {
                "subfolders": ["Raw Data", "Archive"]
            },
            "Silver Layer": {
                "subfolders": ["Cleaned", "Transformed"]
            },
            "Gold Layer": {
                "subfolders": ["Analytics", "Reports"]
            }
        }
    },
    "data-science": {
        "name": "Data Science Project",
        "description": "ML/AI project structure",
        "structure": {
            "Data": {
                "subfolders": ["Raw", "Processed", "External"]
            },
            "Notebooks": {
                "subfolders": ["Exploration", "Feature Engineering", "Modeling"]
            },
            "Models": {
                "subfolders": ["Training", "Production", "Archive"]
            },
            "Reports": {}
        }
    },
    "departmental": {
        "name": "Departmental Organization",
        "description": "Organize by business department",
        "structure": {
            "Sales": {
                "subfolders": ["Reports", "Dashboards", "Data"]
            },
            "Marketing": {
                "subfolders": ["Reports", "Dashboards", "Data"]
            },
            "Finance": {
                "subfolders": ["Reports", "Dashboards", "Data"]
            },
            "Operations": {
                "subfolders": ["Reports", "Dashboards", "Data"]
            }
        }
    },
    "basic": {
        "name": "Basic Structure",
        "description": "Simple categorization",
        "structure": {
            "Data Sources": {},
            "Transformations": {},
            "Analytics": {},
            "Archive": {}
        }
    }
}


# ============================================================================
# CLI COMMANDS
# ============================================================================

def cmd_create(args):
    """Create a folder"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_info(f"\n📁 Creating folder '{args.name}' in workspace...")
    
    # Get parent folder ID if specified
    parent_id = None
    if args.parent:
        print_info(f"  Looking for parent folder '{args.parent}'...")
        folders = manager.list_folders(workspace_id)
        parent = next((f for f in folders if f.display_name == args.parent), None)
        if not parent:
            print_error(f"Parent folder '{args.parent}' not found")
            return 1
        parent_id = parent.id
        print_success(f"  Found parent: {parent_id[:8]}...")
    
    try:
        folder_id = manager.create_folder(
            workspace_id,
            args.name,
            parent_folder_id=parent_id,
            description=args.description
        )
        
        print_success(f"\n✅ Created folder: {args.name}")
        print_info(f"   ID: {folder_id}")
        
        if args.show_tree:
            print_info("\n📂 Updated folder structure:")
            manager.print_folder_tree(workspace_id)
        
        return 0
        
    except (FolderValidationError, FolderOperationError) as e:
        print_error(f"\n❌ Failed to create folder: {e}")
        return 1


def cmd_list(args):
    """List folders in workspace"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_info(f"\n📋 Listing folders in workspace...")
    
    try:
        folders = manager.list_folders(workspace_id, include_subfolders=not args.top_level)
        
        if not folders:
            print_warning("No folders found")
            return 0
        
        print_success(f"\nFound {len(folders)} folder(s):\n")
        
        # Group by parent
        root_folders = [f for f in folders if f.parent_folder_id is None]
        subfolders = [f for f in folders if f.parent_folder_id is not None]
        
        # Show root folders
        for folder in root_folders:
            print_info(f"📁 {folder.display_name}")
            print_info(f"   ID: {folder.id}")
            
            # Show immediate children if requested
            if args.show_children:
                children = [f for f in subfolders if f.parent_folder_id == folder.id]
                for child in children:
                    print_info(f"   └─ 📁 {child.display_name} ({child.id[:8]}...)")
            print()
        
        # Show orphaned subfolders (shouldn't happen but good to check)
        if subfolders and not args.show_children:
            print_info(f"\n{len(subfolders)} subfolder(s) not shown (use --show-children)")
        
        return 0
        
    except FolderOperationError as e:
        print_error(f"\n❌ Failed to list folders: {e}")
        return 1


def cmd_tree(args):
    """Show folder tree"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_info(f"\n🌳 Folder structure for workspace:\n")
    
    try:
        manager.print_folder_tree(workspace_id, show_items=args.show_items)
        return 0
        
    except FolderOperationError as e:
        print_error(f"\n❌ Failed to show tree: {e}")
        return 1


def cmd_move(args):
    """Move folder to different parent"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_info(f"\n📦 Moving folder '{args.folder}'...")
    
    try:
        # Find folder to move
        folders = manager.list_folders(workspace_id)
        folder = next((f for f in folders if f.display_name == args.folder), None)
        if not folder:
            print_error(f"Folder '{args.folder}' not found")
            return 1
        
        # Find new parent
        new_parent_id = None
        if args.parent:
            parent = next((f for f in folders if f.display_name == args.parent), None)
            if not parent:
                print_error(f"Parent folder '{args.parent}' not found")
                return 1
            new_parent_id = parent.id
            print_info(f"  Moving to parent: {args.parent}")
        else:
            print_info(f"  Moving to workspace root")
        
        manager.move_folder(workspace_id, folder.id, new_parent_id)
        
        print_success(f"\n✅ Moved folder: {args.folder}")
        
        if args.show_tree:
            print_info("\n📂 Updated folder structure:")
            manager.print_folder_tree(workspace_id)
        
        return 0
        
    except (FolderValidationError, FolderOperationError) as e:
        print_error(f"\n❌ Failed to move folder: {e}")
        return 1


def cmd_delete(args):
    """Delete folder"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_warning(f"\n⚠️  Deleting folder '{args.folder}'...")
    
    try:
        # Find folder
        folders = manager.list_folders(workspace_id)
        folder = next((f for f in folders if f.display_name == args.folder), None)
        if not folder:
            print_error(f"Folder '{args.folder}' not found")
            return 1
        
        # Confirm if not forced
        if not args.force and not args.yes:
            items = manager.list_folder_items(workspace_id, folder.id)
            if items:
                print_warning(f"  Folder contains {len(items)} item(s)")
            
            response = input(f"  Delete folder '{args.folder}'? [y/N]: ")
            if response.lower() != 'y':
                print_info("Cancelled")
                return 0
        
        manager.delete_folder(workspace_id, folder.id, force=args.force)
        
        print_success(f"\n✅ Deleted folder: {args.folder}")
        
        if args.show_tree:
            print_info("\n📂 Updated folder structure:")
            manager.print_folder_tree(workspace_id)
        
        return 0
        
    except FolderOperationError as e:
        print_error(f"\n❌ Failed to delete folder: {e}")
        return 1


def cmd_create_structure(args):
    """Create folder structure from template or config"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    # Load structure
    if args.config:
        print_info(f"\n📋 Loading structure from {args.config}...")
        try:
            with open(args.config, 'r') as f:
                if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                    structure = yaml.safe_load(f)
                else:
                    structure = json.load(f)
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            return 1
    elif args.template:
        if args.template not in TEMPLATES:
            print_error(f"Unknown template: {args.template}")
            print_info(f"Available templates: {', '.join(TEMPLATES.keys())}")
            return 1
        
        template = TEMPLATES[args.template]
        print_info(f"\n📋 Using template: {template['name']}")
        print_info(f"   {template['description']}")
        structure = template["structure"]
    else:
        print_error("Must specify --template or --config")
        return 1
    
    # Show structure
    if args.dry_run:
        print_info("\n🔍 Dry run - would create:")
        _print_structure(structure)
        return 0
    
    # Create structure
    print_info(f"\n📁 Creating folder structure...")
    
    try:
        folder_ids = manager.create_folder_structure(workspace_id, structure)
        
        print_success(f"\n✅ Created {len(folder_ids)} folder(s)")
        
        if args.show_tree:
            print_info("\n📂 Folder structure:")
            manager.print_folder_tree(workspace_id)
        
        # Save folder IDs if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(folder_ids, f, indent=2)
            print_info(f"\n💾 Saved folder IDs to {args.output}")
        
        return 0
        
    except (FolderValidationError, FolderOperationError) as e:
        print_error(f"\n❌ Failed to create structure: {e}")
        return 1


def cmd_move_items(args):
    """Move items to folder"""
    manager = FabricFolderManager()
    client = FabricClient()
    
    # Get workspace ID
    workspace_id = args.workspace_id or os.getenv("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        workspace_id = client.get_workspace_id(args.workspace)
    
    print_info(f"\n📦 Moving items to folder '{args.folder}'...")
    
    try:
        # Find folder
        folders = manager.list_folders(workspace_id)
        folder = next((f for f in folders if f.display_name == args.folder), None)
        if not folder:
            print_error(f"Folder '{args.folder}' not found")
            return 1
        
        # Parse item IDs
        item_ids = [item.strip() for item in args.items.split(',')]
        
        print_info(f"  Moving {len(item_ids)} item(s)...")
        
        results = manager.move_items_to_folder(workspace_id, item_ids, folder.id)
        
        success_count = sum(results.values())
        print_success(f"\n✅ Moved {success_count}/{len(item_ids)} item(s)")
        
        # Show failures
        failures = [item_id for item_id, success in results.items() if not success]
        if failures:
            print_warning(f"\n⚠️  Failed to move {len(failures)} item(s):")
            for item_id in failures:
                print_warning(f"   - {item_id}")
        
        return 0 if success_count == len(item_ids) else 1
        
    except FolderOperationError as e:
        print_error(f"\n❌ Failed to move items: {e}")
        return 1


def cmd_list_templates(args):
    """List available folder structure templates"""
    print_info("\n📋 Available folder structure templates:\n")
    
    for template_name, template in TEMPLATES.items():
        print_success(f"  {template_name}")
        print_info(f"    {template['description']}")
        print_info(f"    Folders: {len(template['structure'])}")
        print()
    
    print_info("Usage:")
    print_info("  python manage_fabric_folders.py create-structure --workspace 'Analytics' --template medallion")
    
    return 0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _print_structure(structure: Dict[str, Any], indent: int = 0):
    """Print folder structure with indentation"""
    for name, config in structure.items():
        print_info("  " * indent + f"📁 {name}")
        
        if isinstance(config, dict) and "subfolders" in config:
            for subfolder in config["subfolders"]:
                print_info("  " * (indent + 1) + f"📁 {subfolder}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Microsoft Fabric Folder Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # CREATE command
    create_parser = subparsers.add_parser('create', help='Create a folder')
    create_parser.add_argument('--workspace', required=True, help='Workspace name')
    create_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    create_parser.add_argument('--name', required=True, help='Folder name')
    create_parser.add_argument('--parent', help='Parent folder name (for subfolders)')
    create_parser.add_argument('--description', help='Folder description')
    create_parser.add_argument('--show-tree', action='store_true', help='Show folder tree after creation')
    create_parser.set_defaults(func=cmd_create)
    
    # LIST command
    list_parser = subparsers.add_parser('list', help='List folders')
    list_parser.add_argument('--workspace', required=True, help='Workspace name')
    list_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    list_parser.add_argument('--top-level', action='store_true', help='Show only top-level folders')
    list_parser.add_argument('--show-children', action='store_true', help='Show immediate children')
    list_parser.set_defaults(func=cmd_list)
    
    # TREE command
    tree_parser = subparsers.add_parser('tree', help='Show folder tree')
    tree_parser.add_argument('--workspace', required=True, help='Workspace name')
    tree_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    tree_parser.add_argument('--show-items', action='store_true', help='Show items in folders')
    tree_parser.set_defaults(func=cmd_tree)
    
    # MOVE command
    move_parser = subparsers.add_parser('move', help='Move folder')
    move_parser.add_argument('--workspace', required=True, help='Workspace name')
    move_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    move_parser.add_argument('--folder', required=True, help='Folder name to move')
    move_parser.add_argument('--parent', help='New parent folder name (None for root)')
    move_parser.add_argument('--show-tree', action='store_true', help='Show folder tree after move')
    move_parser.set_defaults(func=cmd_move)
    
    # DELETE command
    delete_parser = subparsers.add_parser('delete', help='Delete folder')
    delete_parser.add_argument('--workspace', required=True, help='Workspace name')
    delete_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    delete_parser.add_argument('--folder', required=True, help='Folder name to delete')
    delete_parser.add_argument('--force', action='store_true', help='Delete even if contains items')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    delete_parser.add_argument('--show-tree', action='store_true', help='Show folder tree after deletion')
    delete_parser.set_defaults(func=cmd_delete)
    
    # CREATE-STRUCTURE command
    structure_parser = subparsers.add_parser('create-structure', help='Create folder structure from template')
    structure_parser.add_argument('--workspace', required=True, help='Workspace name')
    structure_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    structure_parser.add_argument('--template', help='Template name (medallion, data-science, departmental, basic)')
    structure_parser.add_argument('--config', help='YAML/JSON config file with structure')
    structure_parser.add_argument('--dry-run', action='store_true', help='Show structure without creating')
    structure_parser.add_argument('--show-tree', action='store_true', help='Show folder tree after creation')
    structure_parser.add_argument('--output', help='Save folder IDs to JSON file')
    structure_parser.set_defaults(func=cmd_create_structure)
    
    # MOVE-ITEMS command
    move_items_parser = subparsers.add_parser('move-items', help='Move items to folder')
    move_items_parser.add_argument('--workspace', required=True, help='Workspace name')
    move_items_parser.add_argument('--workspace-id', help='Workspace GUID (alternative to name)')
    move_items_parser.add_argument('--folder', required=True, help='Target folder name')
    move_items_parser.add_argument('--items', required=True, help='Comma-separated item IDs')
    move_items_parser.set_defaults(func=cmd_move_items)
    
    # LIST-TEMPLATES command
    templates_parser = subparsers.add_parser('list-templates', help='List available templates')
    templates_parser.set_defaults(func=cmd_list_templates)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Cancelled by user")
        return 130
    except Exception as e:
        print_error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
