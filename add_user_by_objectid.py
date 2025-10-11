#!/usr/bin/env python3
"""
Add user to Fabric workspaces using Object ID directly (no Graph API needed)
"""
import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import sys

load_dotenv()

if len(sys.argv) < 4:
    print("Usage: python3 add_user_by_objectid.py <workspace_id> <user_object_id> <role>")
    print("Example: python3 add_user_by_objectid.py 8070ecd4-... abc123-... Admin")
    sys.exit(1)

workspace_id = sys.argv[1]
user_object_id = sys.argv[2]
role = sys.argv[3] if len(sys.argv) > 3 else "Admin"

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")

print(f"👤 Adding user to workspace")
print(f"   Workspace ID: {workspace_id}")
print(f"   User Object ID: {user_object_id}")
print(f"   Role: {role}")

# Get Fabric token
authority = f"https://login.microsoftonline.com/{tenant_id}"
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

result = app.acquire_token_for_client(scopes=["https://api.fabric.microsoft.com/.default"])
if "access_token" not in result:
    print(f"❌ Failed to get Fabric token")
    sys.exit(1)

token = result["access_token"]

# Add user to workspace
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "principal": {
        "id": user_object_id,
        "type": "User"
    },
    "role": role
}

try:
    response = requests.post(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/roleAssignments",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ SUCCESS! User added to workspace")
        print(f"   Object ID: {user_object_id}")
        print(f"   Role: {role}")
    elif response.status_code == 409:
        print(f"⚠️  User already has access to this workspace")
    else:
        print(f"❌ Failed to add user")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error adding user: {str(e)}")
    sys.exit(1)

print("\n✅ Done!")
