#!/usr/bin/env python3
"""
Add user to Fabric workspace by first resolving their Azure AD Object ID
"""
import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import sys

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")

if len(sys.argv) < 4:
    print("Usage: python3 add_user_to_workspace.py <workspace_id> <user_email> <role>")
    print("Example: python3 add_user_to_workspace.py 8070ecd4-... user@example.com Admin")
    sys.exit(1)

workspace_id = sys.argv[1]
user_email = sys.argv[2]
role = sys.argv[3] if len(sys.argv) > 3 else "Admin"

print(f"🔍 Looking up Azure AD Object ID for: {user_email}")

# Step 1: Get Microsoft Graph token
authority = f"https://login.microsoftonline.com/{tenant_id}"
graph_app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

graph_result = graph_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
if "access_token" not in graph_result:
    print(f"❌ Failed to get Graph token: {graph_result.get('error_description')}")
    sys.exit(1)

graph_token = graph_result["access_token"]

# Step 2: Look up user in Azure AD
graph_headers = {
    "Authorization": f"Bearer {graph_token}",
    "Content-Type": "application/json"
}

try:
    # Search for user by email
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user_email}",
        headers=graph_headers,
        timeout=30
    )
    
    if response.status_code == 200:
        user_data = response.json()
        user_object_id = user_data["id"]
        user_display_name = user_data.get("displayName", "Unknown")
        print(f"✅ Found user: {user_display_name}")
        print(f"   Object ID: {user_object_id}")
    else:
        print(f"❌ User not found in Azure AD")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error looking up user: {str(e)}")
    sys.exit(1)

# Step 3: Get Fabric token
fabric_result = graph_app.acquire_token_for_client(scopes=["https://api.fabric.microsoft.com/.default"])
if "access_token" not in fabric_result:
    print(f"❌ Failed to get Fabric token")
    sys.exit(1)

fabric_token = fabric_result["access_token"]

# Step 4: Add user to workspace
print(f"\n👤 Adding user to workspace: {workspace_id}")
print(f"   Role: {role}")

fabric_headers = {
    "Authorization": f"Bearer {fabric_token}",
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
        headers=fabric_headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ SUCCESS! User added to workspace")
        print(f"   User: {user_display_name} ({user_email})")
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
