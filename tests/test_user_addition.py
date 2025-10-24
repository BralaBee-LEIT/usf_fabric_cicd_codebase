#!/usr/bin/env python3
"""
Test adding users to Fabric workspace with different API formats
"""
import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = "https://api.fabric.microsoft.com/.default"

# Get token
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

result = app.acquire_token_for_client(scopes=[scope])
token = result["access_token"]

workspace_id = "8070ecd4-d1f2-4b08-addc-4a78adf2e1a4"
user_email = "sanmi.ibitoye@jtoyedigital.co.uk"

base_url = "https://api.fabric.microsoft.com/v1"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test different payload formats
test_payloads = [
    {
        "name": "Format 1: emailAddress field",
        "payload": {
            "emailAddress": user_email,
            "groupUserAccessRight": "Admin"
        }
    },
    {
        "name": "Format 2: identifier with email",
        "payload": {
            "identifier": user_email,
            "groupUserAccessRight": "Admin",
            "principalType": "User"
        }
    },
    {
        "name": "Format 3: PowerBI format",
        "payload": {
            "emailAddress": user_email,
            "workspaceRole": "Admin"
        }
    }
]

print(f"Testing user addition formats for workspace: {workspace_id}")
print("=" * 70)

for test in test_payloads:
    print(f"\n{test['name']}")
    print(f"Payload: {test['payload']}")
    
    try:
        response = requests.post(
            f"{base_url}/workspaces/{workspace_id}/roleAssignments",
            headers=headers,
            json=test['payload'],
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ SUCCESS!")
            print(f"Response: {response.json()}")
            break
        else:
            print("❌ Failed")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("If all fail, we may need to use Microsoft Graph API to get the user's Object ID first")
