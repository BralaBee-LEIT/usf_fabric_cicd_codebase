#!/usr/bin/env python3
"""Diagnose workspace visibility issue."""
import sys
import os
from pathlib import Path

# Load environment
env_file = Path(__file__).parent / ".env"
loaded_count = 0
if env_file.exists():
    with env_file.open('r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, value = line.split('=', 1)
                key = key.strip()
                if key not in os.environ:
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
                    loaded_count += 1

print(f"✅ Loaded {loaded_count} environment variables")
print()

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent / "ops" / "scripts"))

from utilities.workspace_manager import WorkspaceManager
from utilities.config_manager import ConfigManager

print("🔍 Checking workspace visibility...")
print()

# Initialize manager
try:
    mgr = WorkspaceManager()
    print("✅ WorkspaceManager initialized")
    print()
    
    # List workspaces
    workspaces = mgr.list_workspaces()
    print(f"📊 Total workspaces found via API: {len(workspaces)}")
    print()
    
    if workspaces:
        print("Workspaces returned by API:")
        for ws in workspaces:
            print(f"  • {ws['displayName']}")
            print(f"    ID: {ws['id']}")
            print(f"    Type: {ws.get('type', 'N/A')}")
            print()
    
    # Check for our specific workspaces
    print("🎯 Looking for our created workspaces:")
    print()
    
    target_workspaces = {
        "Customer Analytics [DEV]": "be8d1df8-9067-4557-a179-fd706a38dd20",
        "Sales Analytics [DEV]": "f6f36e51-99e7-424e-aba6-1aa70b92d4e2"
    }
    
    for name, ws_id in target_workspaces.items():
        found = any(ws['id'] == ws_id for ws in workspaces)
        if found:
            print(f"  ✅ FOUND: {name}")
            print(f"     ID: {ws_id}")
        else:
            print(f"  ❌ NOT FOUND: {name}")
            print(f"     Expected ID: {ws_id}")
            print(f"     Status: Created by API but not returned in list")
        print()
    
    # Check tenant info
    print("🔐 Authentication Info:")
    tenant_id = os.environ.get('AZURE_TENANT_ID', 'NOT SET')
    client_id = os.environ.get('AZURE_CLIENT_ID', 'NOT SET')
    print(f"  Tenant ID: {tenant_id}")
    print(f"  Client ID: {client_id}")
    print()
    
    print("💡 Possible Issues:")
    print("  1. Service principal doesn't have 'read' permission on workspaces")
    print("  2. Workspaces created in different capacity/region than expected")
    print("  3. Trial capacity workspaces might not appear immediately")
    print("  4. Your user account is in different tenant than service principal")
    print()
    
    # Try to get specific workspace by ID
    print("🔬 Attempting direct workspace lookup by ID...")
    print()
    
    for name, ws_id in target_workspaces.items():
        try:
            # Try to get workspace details directly
            import requests
            token = mgr.auth_token
            headers = {"Authorization": f"Bearer {token}"}
            url = f"https://api.fabric.microsoft.com/v1/workspaces/{ws_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print(f"  ✅ {name}: EXISTS via direct API call")
                ws_data = response.json()
                print(f"     Name: {ws_data.get('displayName', 'N/A')}")
                print(f"     Type: {ws_data.get('type', 'N/A')}")
                print(f"     Capacity: {ws_data.get('capacityId', 'N/A')}")
            elif response.status_code == 404:
                print(f"  ❌ {name}: NOT FOUND (404)")
                print(f"     Workspace might have been deleted")
            elif response.status_code == 403:
                print(f"  🚫 {name}: ACCESS DENIED (403)")
                print(f"     Service principal lacks permission")
            else:
                print(f"  ⚠️ {name}: Unexpected response ({response.status_code})")
            print()
        except Exception as e:
            print(f"  ❌ Error checking {name}: {e}")
            print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
