#!/usr/bin/env python3
"""
Microsoft Fabric Workspace Management CLI
Command-line interface for managing workspaces and users across environments
"""
import argparse
import sys
import json
import logging
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.is_file():
    load_dotenv(env_file)

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent / "utilities"))

from utilities.workspace_manager import (
    WorkspaceManager,
    WorkspaceRole,
    CapacityType,
    setup_complete_environment,
)
from utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
    console_table as print_table,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cmd_list_workspaces(args):
    """List all workspaces"""
    try:
        manager = WorkspaceManager(environment=args.environment)
        workspaces = manager.list_workspaces(
            filter_by_environment=args.filter_env, include_details=args.details
        )

        if not workspaces:
            print_warning("No workspaces found")
            return 0

        # Prepare table data
        headers = ["Name", "ID", "Type"]
        if args.details:
            headers.extend(["Capacity", "State", "Region"])

        rows = []
        for ws in workspaces:
            row = [
                ws.get("displayName", "N/A"),
                ws.get("id", "N/A"),
                ws.get("type", "Workspace"),
            ]

            if args.details:
                row.extend(
                    [
                        ws.get("capacityId", "Trial"),
                        ws.get("state", "Active"),
                        ws.get("region", "N/A"),
                    ]
                )

            rows.append(row)

        print_table(headers, rows)
        print_success(f"\nFound {len(workspaces)} workspace(s)")

        return 0

    except Exception as e:
        print_error(f"Failed to list workspaces: {e}")
        logger.exception("List workspaces error")
        return 1


def cmd_create_workspace(args):
    """Create a new workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Parse capacity type
        capacity_type = (
            CapacityType(args.capacity_type)
            if args.capacity_type
            else CapacityType.TRIAL
        )

        workspace = manager.create_workspace(
            name=args.name,
            description=args.description,
            capacity_id=args.capacity_id,
            capacity_type=capacity_type,
        )

        print_success(f"✓ Created workspace: {workspace.get('displayName')}")
        print_info(f"  ID: {workspace.get('id')}")

        if args.json:
            print(json.dumps(workspace, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to create workspace: {e}")
        logger.exception("Create workspace error")
        return 1


def cmd_delete_workspace(args):
    """Delete a workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Confirm deletion if not forced
        if not args.yes:
            workspace = manager.get_workspace_details(args.workspace_id)
            workspace_name = workspace.get("displayName", args.workspace_id)

            print_warning(f"You are about to delete workspace: {workspace_name}")
            confirmation = input("Type 'DELETE' to confirm: ")

            if confirmation != "DELETE":
                print_info("Deletion cancelled")
                return 0

        success = manager.delete_workspace(args.workspace_id, force=args.force)

        if success:
            print_success(f"✓ Deleted workspace: {args.workspace_id}")
            return 0
        else:
            print_warning("Workspace not found or already deleted")
            return 1

    except Exception as e:
        print_error(f"Failed to delete workspace: {e}")
        logger.exception("Delete workspace error")
        return 1


def cmd_delete_bulk(args):
    """Delete multiple workspaces from IDs or file"""
    try:
        manager = WorkspaceManager(environment=args.environment)
        workspace_ids = []

        # Read workspace IDs from file
        if args.file:
            try:
                with open(args.file, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith("#"):
                            workspace_ids.append(line)
            except FileNotFoundError:
                print_error(f"File not found: {args.file}")
                return 1
            except Exception as e:
                print_error(f"Error reading file: {e}")
                return 1

            if not workspace_ids:
                print_warning("No workspace IDs found in file")
                return 0

            # Show warning with file info
            print_warning(
                f"You are about to delete {len(workspace_ids)} workspace(s) from file:"
            )
            print_info(f"  File: {args.file}")
            for ws_id in workspace_ids:
                print(f"  - {ws_id}")

        # Use provided workspace IDs
        elif args.workspace_ids:
            workspace_ids = args.workspace_ids

            print_warning(f"You are about to delete {len(workspace_ids)} workspace(s):")
            for ws_id in workspace_ids:
                print(f"  - {ws_id}")

        else:
            print_error("Please provide workspace IDs or use --file option")
            return 1

        # Confirm deletion
        if not args.yes:
            confirmation = input(f"\nType 'DELETE {len(workspace_ids)}' to confirm: ")
            if confirmation != f"DELETE {len(workspace_ids)}":
                print_info("Deletion cancelled")
                return 0

        # Delete workspaces
        print_info(f"\n🗑️  Deleting {len(workspace_ids)} workspace(s)...")

        success_count = 0
        fail_count = 0

        for workspace_id in workspace_ids:
            try:
                success = manager.delete_workspace(workspace_id, force=args.force)
                if success:
                    print_success(f"✓ Deleted workspace: {workspace_id}")
                    success_count += 1
                else:
                    print_warning(
                        f"✗ Workspace not found or already deleted: {workspace_id}"
                    )
                    fail_count += 1
            except Exception as e:
                print_error(f"✗ Failed to delete {workspace_id}: {e}")
                fail_count += 1

        # Print summary
        print_info("\n📊 Summary:")
        print_success(f"  ✓ Deleted: {success_count}")
        if fail_count > 0:
            print_error(f"  ✗ Failed: {fail_count}")
        print_info(f"  📋 Total: {len(workspace_ids)}")

        return 0 if fail_count == 0 else 1

    except Exception as e:
        print_error(f"Bulk deletion failed: {e}")
        logger.exception("Bulk delete error")
        return 1


def cmd_delete_all(args):
    """Delete all workspaces in the environment"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Get all workspaces
        workspaces = manager.list_workspaces()

        if not workspaces:
            print_info("No workspaces found to delete")
            return 0

        # Show warning
        print_warning(
            f"⚠️  WARNING: You are about to delete ALL {len(workspaces)} workspaces:"
        )
        for ws in workspaces:
            print(f"  - {ws.get('displayName', 'Unknown')} ({ws['id']})")

        # Confirm deletion
        if not args.yes:
            confirmation = input("\nType 'DELETE ALL' to confirm: ")
            if confirmation != "DELETE ALL":
                print_info("Deletion cancelled")
                return 0

        # Delete all workspaces
        print_info(f"\n🗑️  Deleting {len(workspaces)} workspace(s)...")

        workspace_ids = [ws["id"] for ws in workspaces]
        success_count = 0
        fail_count = 0

        for workspace_id in workspace_ids:
            try:
                success = manager.delete_workspace(workspace_id, force=args.force)
                if success:
                    print_success(f"✓ Deleted workspace: {workspace_id}")
                    success_count += 1
                else:
                    print_warning(
                        f"✗ Workspace not found or already deleted: {workspace_id}"
                    )
                    fail_count += 1
            except Exception as e:
                print_error(f"✗ Failed to delete {workspace_id}: {e}")
                fail_count += 1

        # Print summary
        print_info("\n📊 Summary:")
        print_success(f"  ✓ Deleted: {success_count}")
        if fail_count > 0:
            print_error(f"  ✗ Failed: {fail_count}")
        print_info(f"  📋 Total: {len(workspace_ids)}")

        return 0 if fail_count == 0 else 1

    except Exception as e:
        print_error(f"Delete all failed: {e}")
        logger.exception("Delete all error")
        return 1


def cmd_update_workspace(args):
    """Update workspace properties"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        workspace = manager.update_workspace(
            workspace_id=args.workspace_id, name=args.name, description=args.description
        )

        print_success(f"✓ Updated workspace: {workspace.get('displayName')}")

        if args.json:
            print(json.dumps(workspace, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to update workspace: {e}")
        logger.exception("Update workspace error")
        return 1


def cmd_get_workspace(args):
    """Get workspace details"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        if args.name:
            workspace = manager.get_workspace_by_name(args.name)
            if not workspace:
                print_error(f"Workspace '{args.name}' not found")
                return 1
        else:
            workspace = manager.get_workspace_details(args.workspace_id)

        # Display details
        print_info(f"\n{'='*60}")
        print_info(f"Workspace: {workspace.get('displayName')}")
        print_info(f"{'='*60}")
        print_info(f"ID:          {workspace.get('id')}")
        print_info(f"Type:        {workspace.get('type', 'Workspace')}")
        print_info(f"Capacity:    {workspace.get('capacityId', 'Trial')}")
        print_info(f"State:       {workspace.get('state', 'Active')}")

        if workspace.get("description"):
            print_info(f"Description: {workspace.get('description')}")

        # List items in workspace
        items = manager.list_workspace_items(workspace["id"])
        print_info(f"\nItems:       {len(items)}")

        if items and args.show_items:
            print_info("\nWorkspace Items:")
            item_headers = ["Name", "Type", "State"]
            item_rows = [
                [item.get("displayName"), item.get("type"), item.get("state", "Active")]
                for item in items[:10]  # Show first 10
            ]
            print_table(item_headers, item_rows)

            if len(items) > 10:
                print_info(f"... and {len(items) - 10} more items")

        if args.json:
            print("\n" + json.dumps(workspace, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to get workspace details: {e}")
        logger.exception("Get workspace error")
        return 1


def cmd_list_users(args):
    """List users in a workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)
        users = manager.list_users(args.workspace_id)

        if not users:
            print_warning("No users found in workspace")
            return 0

        # Prepare table
        headers = ["Principal", "Type", "Role"]
        rows = [
            [
                user.get("identifier", "N/A"),
                user.get("principalType", "User"),
                user.get("workspaceRole", "N/A"),
            ]
            for user in users
        ]

        print_table(headers, rows)
        print_success(f"\nFound {len(users)} user(s)")

        if args.json:
            print("\n" + json.dumps(users, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to list users: {e}")
        logger.exception("List users error")
        return 1


def cmd_add_user(args):
    """Add user to workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Parse role
        role = WorkspaceRole(args.role)

        user = manager.add_user(
            workspace_id=args.workspace_id,
            principal_id=args.principal_id,
            principal_type=args.principal_type,
            role=role,
        )

        print_success(
            f"✓ Added {args.principal_type} '{args.principal_id}' with role '{role.value}'"
        )

        if args.json:
            print(json.dumps(user, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to add user: {e}")
        logger.exception("Add user error")
        return 1


def cmd_add_users_from_file(args):
    """Add multiple users/groups to workspace from file"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Read and parse file
        print_info(f"Reading principals from: {args.file}")
        principals = []

        with open(args.file, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse CSV format: principal_id,role,description[,type]
                parts = [p.strip() for p in line.split(",")]

                if len(parts) < 2:
                    print_warning(
                        f"Line {line_num}: Invalid format (need at least principal_id,role)"
                    )
                    continue

                principal_id = parts[0]
                role_str = parts[1]
                description = parts[2] if len(parts) > 2 else ""
                principal_type = parts[3] if len(parts) > 3 else "User"

                # Validate principal_type
                if principal_type not in ["User", "Group", "ServicePrincipal"]:
                    print_warning(
                        f"Line {line_num}: Invalid type '{principal_type}', defaulting to 'User'"
                    )
                    principal_type = "User"

                # Validate role
                try:
                    role = WorkspaceRole(role_str)
                except ValueError:
                    print_warning(
                        f"Line {line_num}: Invalid role '{role_str}', defaulting to 'Viewer'"
                    )
                    role = WorkspaceRole.VIEWER

                principals.append(
                    {
                        "principal_id": principal_id,
                        "role": role,
                        "type": principal_type,
                        "description": description,
                    }
                )

        if not principals:
            print_warning("No valid principals found in file")
            return 1

        print_info(f"Found {len(principals)} principal(s) to add\n")

        # Display table
        headers = ["Principal ID (Object ID)", "Role", "Type", "Description"]
        rows = [
            [p["principal_id"], p["role"].value, p["type"], p["description"]]
            for p in principals
        ]
        print_table(headers, rows)

        # Dry run check
        if args.dry_run:
            print_warning("\n🔍 DRY RUN MODE - No principals will be added")
            return 0

        # Confirm
        if not args.yes:
            print_warning(
                f"\n⚠️  About to add {len(principals)} principal(s) to workspace {args.workspace_id}"
            )
            response = input("Continue? (y/N): ")
            if response.lower() != "y":
                print_info("Cancelled")
                return 0

        # Add principals
        print_info("\nAdding principals...")
        success_count = 0
        failed_count = 0

        for principal in principals:
            try:
                manager.add_user(
                    workspace_id=args.workspace_id,
                    principal_id=principal["principal_id"],
                    role=principal["role"],
                    principal_type=principal["type"],
                )
                print_success(
                    f"✓ Added {principal['type']} {principal['principal_id']} as {principal['role'].value}"
                )
                success_count += 1

            except ValueError as e:
                if "already has access" in str(e):
                    print_warning(
                        f"⚠️  {principal['type']} {principal['principal_id']} already has access"
                    )
                else:
                    print_error(
                        f"✗ Failed to add {principal['type']} {principal['principal_id']}: {str(e)}"
                    )
                    failed_count += 1

            except Exception as e:
                print_error(
                    f"✗ Failed to add {principal['type']} {principal['principal_id']}: {str(e)}"
                )
                failed_count += 1

        # Summary
        print_info("\n📊 Summary:")
        print_success(f"  ✓ Successfully added: {success_count}")
        if failed_count > 0:
            print_error(f"  ✗ Failed: {failed_count}")

        return 0 if failed_count == 0 else 1

    except FileNotFoundError:
        print_error(f"File not found: {args.file}")
        return 1
    except Exception as e:
        print_error(f"Failed to add users from file: {e}")
        logger.exception("Add users from file error")
        return 1


def cmd_remove_user(args):
    """Remove user from workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        success = manager.remove_user(args.workspace_id, args.principal_id)

        if success:
            print_success(f"✓ Removed user '{args.principal_id}'")
            return 0
        else:
            print_warning("User not found in workspace")
            return 1

    except Exception as e:
        print_error(f"Failed to remove user: {e}")
        logger.exception("Remove user error")
        return 1


def cmd_update_user_role(args):
    """Update user role in workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Parse role
        role = WorkspaceRole(args.role)

        user = manager.update_user_role(
            workspace_id=args.workspace_id,
            principal_id=args.principal_id,
            new_role=role,
        )

        print_success(f"✓ Updated user '{args.principal_id}' to role '{role.value}'")

        if args.json:
            print(json.dumps(user, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to update user role: {e}")
        logger.exception("Update user role error")
        return 1


def cmd_create_workspace_set(args):
    """Create workspaces for multiple environments"""
    try:
        manager = WorkspaceManager()

        # Parse environments
        environments = (
            args.environments.split(",")
            if args.environments
            else ["dev", "test", "prod"]
        )

        print_info(f"Creating workspaces for environments: {', '.join(environments)}")

        workspaces = manager.create_workspace_set(
            base_name=args.name,
            environments=environments,
            description_template=args.description,
        )

        # Display results
        success_count = sum(1 for ws in workspaces.values() if "error" not in ws)
        fail_count = len(workspaces) - success_count

        print_info("\nResults:")
        for env, workspace in workspaces.items():
            if "error" in workspace:
                print_error(f"  ✗ {env}: {workspace['error']}")
            else:
                print_success(
                    f"  ✓ {env}: {workspace.get('displayName')} (ID: {workspace.get('id')})"
                )

        print_info(f"\n{success_count} succeeded, {fail_count} failed")

        if args.json:
            print("\n" + json.dumps(workspaces, indent=2))

        return 0 if fail_count == 0 else 1

    except Exception as e:
        print_error(f"Failed to create workspace set: {e}")
        logger.exception("Create workspace set error")
        return 1


def cmd_copy_users(args):
    """Copy users between workspaces"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        print_info(
            f"Copying users from {args.source_workspace_id} to {args.target_workspace_id}"
        )

        results = manager.copy_users_between_workspaces(
            source_workspace_id=args.source_workspace_id,
            target_workspace_id=args.target_workspace_id,
        )

        # Display results
        print_success(f"\n✓ Successfully copied {len(results['success'])} user(s)")

        if results["skipped"]:
            print_warning(
                f"⊘ Skipped {len(results['skipped'])} user(s) (already exists)"
            )

        if results["failed"]:
            print_error(f"✗ Failed to copy {len(results['failed'])} user(s)")
            for failure in results["failed"]:
                print_error(f"  - {failure['principal_id']}: {failure['error']}")

        if args.json:
            print("\n" + json.dumps(results, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to copy users: {e}")
        logger.exception("Copy users error")
        return 1


def cmd_assign_capacity(args):
    """Assign Fabric capacity to a workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Get workspace name for display
        workspace = manager.get_workspace_details(args.workspace_id)
        workspace_name = workspace.get("displayName", args.workspace_id)

        print_info(f"Assigning capacity to workspace: {workspace_name}")
        print_info(f"  Workspace ID: {args.workspace_id}")
        print_info(f"  Capacity ID:  {args.capacity_id}")

        # Assign capacity
        updated_workspace = manager.assign_capacity(
            workspace_id=args.workspace_id, capacity_id=args.capacity_id
        )

        print_success(
            f"✓ Successfully assigned capacity to workspace '{workspace_name}'"
        )
        print_info(f"  New Capacity ID: {updated_workspace.get('capacityId', 'N/A')}")

        if args.json:
            print("\n" + json.dumps(updated_workspace, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to assign capacity: {e}")
        logger.exception("Assign capacity error")
        return 1


def cmd_unassign_capacity(args):
    """Remove capacity assignment from a workspace"""
    try:
        manager = WorkspaceManager(environment=args.environment)

        # Get workspace name for display
        workspace = manager.get_workspace_details(args.workspace_id)
        workspace_name = workspace.get("displayName", args.workspace_id)
        current_capacity = workspace.get("capacityId", "None")

        print_info(f"Removing capacity assignment from workspace: {workspace_name}")
        print_info(f"  Workspace ID:     {args.workspace_id}")
        print_info(f"  Current Capacity: {current_capacity}")

        if not current_capacity or current_capacity == "None":
            print_warning("Workspace has no capacity assigned")
            return 0

        # Confirm if not forced
        if not args.yes:
            confirmation = input(
                "\nThis will revert the workspace to Trial/Shared capacity. Continue? (y/N): "
            )
            if confirmation.lower() != "y":
                print_info("Operation cancelled")
                return 0

        # Unassign capacity
        updated_workspace = manager.unassign_capacity(args.workspace_id)

        print_success(
            f"✓ Successfully removed capacity assignment from workspace '{workspace_name}'"
        )
        print_info("  Workspace reverted to Trial/Shared capacity")

        if args.json:
            print("\n" + json.dumps(updated_workspace, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to unassign capacity: {e}")
        logger.exception("Unassign capacity error")
        return 1


def cmd_setup_environment(args):
    """Set up complete environment with workspaces and users"""
    try:
        print_info(f"Setting up complete environment for project: {args.project_name}")

        # Parse user emails
        admin_emails = args.admins.split(",")
        member_emails = args.members.split(",") if args.members else None

        workspaces = setup_complete_environment(
            project_name=args.project_name,
            admin_emails=admin_emails,
            member_emails=member_emails,
        )

        # Display results
        print_info("\nCreated Workspaces:")
        for env, workspace in workspaces.items():
            if "error" in workspace:
                print_error(f"  ✗ {env}: {workspace['error']}")
            else:
                print_success(f"  ✓ {env}: {workspace.get('displayName')}")

        print_success(f"\nAdded {len(admin_emails)} admin(s)")
        if member_emails:
            print_success(f"Added {len(member_emails)} member(s)")

        if args.json:
            print("\n" + json.dumps(workspaces, indent=2))

        return 0

    except Exception as e:
        print_error(f"Failed to setup environment: {e}")
        logger.exception("Setup environment error")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Microsoft Fabric Workspace Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "-e",
        "--environment",
        choices=["dev", "test", "prod"],
        help="Target environment (filters workspaces by environment suffix)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List workspaces
    parser_list = subparsers.add_parser("list", help="List workspaces")
    parser_list.add_argument(
        "--filter-env", action="store_true", help="Filter by current environment"
    )
    parser_list.add_argument(
        "--details", action="store_true", help="Include detailed information"
    )
    parser_list.set_defaults(func=cmd_list_workspaces)

    # Create workspace
    parser_create = subparsers.add_parser("create", help="Create a new workspace")
    parser_create.add_argument(
        "name", help="Workspace name (without environment suffix)"
    )
    parser_create.add_argument("--description", help="Workspace description")
    parser_create.add_argument("--capacity-id", help="Capacity ID")
    parser_create.add_argument(
        "--capacity-type", help="Capacity type", choices=[c.value for c in CapacityType]
    )
    parser_create.set_defaults(func=cmd_create_workspace)

    # Delete workspace
    parser_delete = subparsers.add_parser("delete", help="Delete a workspace")
    parser_delete.add_argument("workspace_id", help="Workspace ID to delete")
    parser_delete.add_argument(
        "--force",
        action="store_true",
        help="Force deletion even if workspace has items",
    )
    parser_delete.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    parser_delete.set_defaults(func=cmd_delete_workspace)

    # Delete bulk workspaces
    parser_delete_bulk = subparsers.add_parser(
        "delete-bulk", help="Delete multiple workspaces from IDs or file"
    )
    parser_delete_bulk.add_argument(
        "workspace_ids", nargs="*", help="Workspace IDs to delete"
    )
    parser_delete_bulk.add_argument(
        "--file", "-f", help="File containing workspace IDs (one per line)"
    )
    parser_delete_bulk.add_argument(
        "--force",
        action="store_true",
        help="Force deletion even if workspace has items",
    )
    parser_delete_bulk.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    parser_delete_bulk.set_defaults(func=cmd_delete_bulk)

    # Delete all workspaces
    parser_delete_all = subparsers.add_parser(
        "delete-all", help="Delete all workspaces in environment"
    )
    parser_delete_all.add_argument(
        "--force",
        action="store_true",
        help="Force deletion even if workspace has items",
    )
    parser_delete_all.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    parser_delete_all.set_defaults(func=cmd_delete_all)

    # Update workspace
    parser_update = subparsers.add_parser("update", help="Update workspace properties")
    parser_update.add_argument("workspace_id", help="Workspace ID")
    parser_update.add_argument("--name", help="New workspace name")
    parser_update.add_argument("--description", help="New description")
    parser_update.set_defaults(func=cmd_update_workspace)

    # Assign capacity
    parser_assign_capacity = subparsers.add_parser(
        "assign-capacity", help="Assign Fabric capacity to workspace"
    )
    parser_assign_capacity.add_argument("workspace_id", help="Workspace ID")
    parser_assign_capacity.add_argument("capacity_id", help="Fabric Capacity ID (GUID)")
    parser_assign_capacity.set_defaults(func=cmd_assign_capacity)

    # Unassign capacity
    parser_unassign_capacity = subparsers.add_parser(
        "unassign-capacity", help="Remove capacity assignment from workspace"
    )
    parser_unassign_capacity.add_argument("workspace_id", help="Workspace ID")
    parser_unassign_capacity.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    parser_unassign_capacity.set_defaults(func=cmd_unassign_capacity)

    # Get workspace details
    parser_get = subparsers.add_parser("get", help="Get workspace details")
    group = parser_get.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", dest="workspace_id", help="Workspace ID")
    group.add_argument("--name", help="Workspace name")
    parser_get.add_argument(
        "--show-items", action="store_true", help="Show workspace items"
    )
    parser_get.set_defaults(func=cmd_get_workspace)

    # List users
    parser_list_users = subparsers.add_parser(
        "list-users", help="List users in workspace"
    )
    parser_list_users.add_argument("workspace_id", help="Workspace ID")
    parser_list_users.set_defaults(func=cmd_list_users)

    # Add user
    parser_add_user = subparsers.add_parser("add-user", help="Add user to workspace")
    parser_add_user.add_argument("workspace_id", help="Workspace ID")
    parser_add_user.add_argument(
        "principal_id", help="User email or service principal ID"
    )
    parser_add_user.add_argument(
        "--role",
        default="Viewer",
        choices=[r.value for r in WorkspaceRole],
        help="Workspace role (default: Viewer)",
    )
    parser_add_user.add_argument(
        "--principal-type",
        default="User",
        choices=["User", "Group", "ServicePrincipal"],
        help="Principal type (default: User)",
    )
    parser_add_user.set_defaults(func=cmd_add_user)

    # Add users from file (bulk)
    parser_add_users_file = subparsers.add_parser(
        "add-users-from-file", help="Add multiple users/groups from file"
    )
    parser_add_users_file.add_argument("workspace_id", help="Workspace ID")
    parser_add_users_file.add_argument(
        "file", help="Path to CSV file (principal_id,role,description,type)"
    )
    parser_add_users_file.add_argument(
        "--dry-run", action="store_true", help="Preview without making changes"
    )
    parser_add_users_file.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    parser_add_users_file.set_defaults(func=cmd_add_users_from_file)

    # Remove user
    parser_remove_user = subparsers.add_parser(
        "remove-user", help="Remove user from workspace"
    )
    parser_remove_user.add_argument("workspace_id", help="Workspace ID")
    parser_remove_user.add_argument(
        "principal_id", help="User email or service principal ID"
    )
    parser_remove_user.set_defaults(func=cmd_remove_user)

    # Update user role
    parser_update_role = subparsers.add_parser(
        "update-role", help="Update user role in workspace"
    )
    parser_update_role.add_argument("workspace_id", help="Workspace ID")
    parser_update_role.add_argument(
        "principal_id", help="User email or service principal ID"
    )
    parser_update_role.add_argument(
        "role", choices=[r.value for r in WorkspaceRole], help="New workspace role"
    )
    parser_update_role.set_defaults(func=cmd_update_user_role)

    # Create workspace set
    parser_create_set = subparsers.add_parser(
        "create-set", help="Create workspaces for multiple environments"
    )
    parser_create_set.add_argument("name", help="Base workspace name")
    parser_create_set.add_argument(
        "--environments",
        default="dev,test,prod",
        help="Comma-separated environments (default: dev,test,prod)",
    )
    parser_create_set.add_argument(
        "--description", help="Description template (use {env} for environment)"
    )
    parser_create_set.set_defaults(func=cmd_create_workspace_set)

    # Copy users
    parser_copy = subparsers.add_parser(
        "copy-users", help="Copy users between workspaces"
    )
    parser_copy.add_argument("source_workspace_id", help="Source workspace ID")
    parser_copy.add_argument("target_workspace_id", help="Target workspace ID")
    parser_copy.set_defaults(func=cmd_copy_users)

    # Setup environment
    parser_setup = subparsers.add_parser(
        "setup", help="Set up complete environment (dev/test/prod + users)"
    )
    parser_setup.add_argument("project_name", help="Project name")
    parser_setup.add_argument(
        "--admins", required=True, help="Comma-separated admin emails"
    )
    parser_setup.add_argument("--members", help="Comma-separated member emails")
    parser_setup.set_defaults(func=cmd_setup_environment)

    # Parse arguments
    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute command
    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
