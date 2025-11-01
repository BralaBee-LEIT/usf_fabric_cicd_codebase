"""
List all available Fabric workspaces to find a workspace ID for testing

Usage: python list_workspaces.py
"""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from ops.scripts.utilities.fabric_api import FabricClient

load_dotenv()

try:
    print("\n🔍 Fetching available Fabric workspaces...\n")
    
    client = FabricClient()
    
    # Use the API client to make a direct request
    response = client._make_request("GET", "workspaces")
    data = response.json()
    
    if 'value' in data:
        workspaces = data['value']
        
        if not workspaces:
            print("⚠️  No workspaces found")
        else:
            print(f"✅ Found {len(workspaces)} workspace(s):\n")
            
            for i, ws in enumerate(workspaces, 1):
                print(f"{i}. {ws.get('displayName', 'Unknown')}")
                print(f"   ID: {ws['id']}")
                print(f"   Type: {ws.get('type', 'N/A')}")
                print(f"   Capacity ID: {ws.get('capacityId', 'N/A')}")
                print()
            
            # Suggest first workspace for testing
            first_ws = workspaces[0]
            print("\n" + "="*70)
            print("📋 To use the first workspace for testing, add to .env:")
            print("="*70)
            print(f"FABRIC_WORKSPACE_ID={first_ws['id']}")
            print()
    else:
        print("❌ Unexpected API response format")
        print(f"Response: {data}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
