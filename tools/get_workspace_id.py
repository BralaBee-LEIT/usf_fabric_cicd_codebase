"""
Quick helper to get Fabric workspace GUID by name

Usage: python get_workspace_id.py <workspace_name>
"""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from ops.scripts.utilities.fabric_api import FabricClient

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python get_workspace_id.py <workspace_name>")
    sys.exit(1)

workspace_name = sys.argv[1]

try:
    client = FabricClient()
    workspace_id = client.get_workspace_id(workspace_name)
    
    print(f"\nWorkspace: {workspace_name}")
    print(f"ID: {workspace_id}")
    print(f"\nAdd to .env:")
    print(f"FABRIC_WORKSPACE_ID={workspace_id}")
            
except Exception as e:
    print(f"Error: {e}")
    print("\nAvailable workspaces:")
    print("  Check your FABRIC_DEV_WORKSPACE value in .env")
    sys.exit(1)
