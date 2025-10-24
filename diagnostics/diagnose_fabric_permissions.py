#!/usr/bin/env python3
"""
Diagnose Fabric API permissions and test different endpoints
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

print("=" * 70)
print("🔍 Microsoft Fabric API Permissions Diagnostic")
print("=" * 70)

# Get token
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

result = app.acquire_token_for_client(scopes=[scope])

if "access_token" not in result:
    print("❌ Failed to acquire token!")
    print(f"   Error: {result.get('error')}")
    print(f"   Description: {result.get('error_description')}")
    exit(1)

token = result["access_token"]
print("✅ Successfully acquired access token\n")

# Test different API endpoints
base_url = "https://api.fabric.microsoft.com/v1"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

tests = [
    ("GET", f"{base_url}/workspaces", "List Workspaces (READ)"),
    (
        "POST",
        f"{base_url}/workspaces",
        "Create Workspace (WRITE)",
        {
            "displayName": "test-workspace-diagnostic",
            "description": "Diagnostic test workspace",
        },
    ),
]

print("Testing API Endpoints:")
print("-" * 70)

for method, url, description, *payload in tests:
    print(f"\n📝 {description}")
    print(f"   Method: {method}")
    print(f"   URL: {url}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(
                url, headers=headers, json=payload[0] if payload else None, timeout=30
            )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ SUCCESS")
            data = response.json()
            if "value" in data:
                print(f"   Response: Found {len(data['value'])} items")
            elif "id" in data:
                print(f"   Response: Created resource with ID: {data['id']}")
        elif response.status_code == 401:
            print("   ❌ UNAUTHORIZED")
            try:
                error_data = response.json()
                print(f"   Error Code: {error_data.get('errorCode')}")
                print(f"   Message: {error_data.get('message')}")
            except:
                print(f"   Raw Response: {response.text[:200]}")
        elif response.status_code == 403:
            print("   ❌ FORBIDDEN (Insufficient Permissions)")
            try:
                error_data = response.json()
                print(f"   Message: {error_data.get('message')}")
            except:
                print(f"   Raw Response: {response.text[:200]}")
        else:
            print("   ⚠️  Unexpected Status")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("📊 Diagnostic Summary")
print("=" * 70)
print(
    """
If you see:
- ✅ GET succeeds, ❌ POST fails with 401: Permissions not granted correctly
- ❌ Both fail with 401: Token acquisition issue or API not enabled
- ❌ Both fail with 403: Need admin consent or Fabric Admin API not enabled

Common Solutions:
1. In Azure Portal → App Registrations → Your App:
   - Add Power BI Service API permissions (Application):
     • Workspace.ReadWrite.All
     • Tenant.Read.All (optional)
   - Grant admin consent

2. In Microsoft Fabric Admin Portal (https://app.fabric.microsoft.com):
   - Settings → Admin portal → Tenant settings
   - Enable "Service principals can use Fabric APIs"
   - Add your App ID to the list

3. Ensure you have an active Fabric capacity or trial
"""
)
