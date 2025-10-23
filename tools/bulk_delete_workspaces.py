#!/usr/bin/env python3
"""
Bulk delete workspaces

Supports multiple deletion methods:
1. Direct workspace IDs as arguments
2. Reading from a file (--file/-f)
3. Deleting all workspaces (--all)
"""
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, 'ops/scripts')

from utilities.workspace_manager import WorkspaceManager

load_dotenv()

def read_workspace_ids_from_file(file_path):
    """Read workspace IDs from a file (one per line, supports comments)"""
    workspace_ids = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    workspace_ids.append(line)
        return workspace_ids
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        sys.exit(1)

def print_usage():
    """Print usage information"""
    print("Usage:")
    print("  1. Direct IDs:  python3 bulk_delete_workspaces.py <workspace_id_1> <workspace_id_2> ...")
    print("  2. From file:   python3 bulk_delete_workspaces.py --file <path/to/file.txt>")
    print("                  python3 bulk_delete_workspaces.py -f <path/to/file.txt>")
    print("  3. Delete all:  python3 bulk_delete_workspaces.py --all")
    print()
    print("File format (one workspace ID per line):")
    print("  8070ecd4-d1f2-4b08-addc-4a78adf2e1a4")
    print("  4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4")
    print("  # Comments are supported")
    print("  e5ca7fe9-e1f2-470b-97aa-5723ffef40de")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print_usage()
        sys.exit(0 if len(sys.argv) > 1 else 1)
    
    manager = WorkspaceManager()
    workspace_ids = []
    
    if sys.argv[1] == "--all":
        # Get all workspaces
        workspaces = manager.list_workspaces()
        workspace_ids = [ws['id'] for ws in workspaces]
        
        if not workspace_ids:
            print("✅ No workspaces to delete")
            return
        
        print(f"⚠️  WARNING: You are about to delete ALL {len(workspace_ids)} workspaces:")
        for ws in workspaces:
            print(f"   - {ws.get('displayName', 'Unknown')} ({ws['id']})")
        
        confirm = input("\nType 'DELETE ALL' to confirm: ")
        if confirm != "DELETE ALL":
            print("❌ Deletion cancelled")
            return
    
    elif sys.argv[1] in ["--file", "-f"]:
        # Read workspace IDs from file
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a file path")
            print("Usage: python3 bulk_delete_workspaces.py --file <path/to/file.txt>")
            sys.exit(1)
        
        file_path = sys.argv[2]
        workspace_ids = read_workspace_ids_from_file(file_path)
        
        if not workspace_ids:
            print("⚠️ No workspace IDs found in file")
            return
        
        print(f"\n⚠️  WARNING: You are about to delete {len(workspace_ids)} workspace(s) from file:")
        print(f"   File: {file_path}")
        for ws_id in workspace_ids:
            print(f"   - {ws_id}")
        
        confirm = input(f"\nType 'DELETE {len(workspace_ids)}' to confirm: ")
        if confirm != f"DELETE {len(workspace_ids)}":
            print("❌ Deletion cancelled")
            return
    
    else:
        # Use provided workspace IDs from command line arguments
        workspace_ids = sys.argv[1:]
    
    print(f"\n🗑️  Deleting {len(workspace_ids)} workspace(s)...")
    
    success_count = 0
    fail_count = 0
    
    for workspace_id in workspace_ids:
        try:
            result = manager.delete_workspace(workspace_id, force=True)
            print(f"✅ Deleted workspace: {workspace_id}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to delete {workspace_id}: {str(e)}")
            fail_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Deleted: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📋 Total: {len(workspace_ids)}")

if __name__ == "__main__":
    main()
