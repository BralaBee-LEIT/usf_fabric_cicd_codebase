#!/usr/bin/env python3
"""
Check Microsoft Graph API permissions
"""
import os
import jwt
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"

print("=" * 70)
print("🔍 Microsoft Graph API Permissions Check")
print("=" * 70)

# Get Graph token
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

if "access_token" not in result:
    print(f"❌ Failed to acquire token")
    print(f"   Error: {result.get('error')}")
    print(f"   Description: {result.get('error_description')}")
    exit(1)

token = result["access_token"]
print("✅ Successfully acquired Microsoft Graph token\n")

# Decode token to see permissions
try:
    decoded = jwt.decode(token, options={"verify_signature": False})
    
    print("📋 Token Details:")
    print(f"   App ID: {decoded.get('appid')}")
    print(f"   Audience: {decoded.get('aud')}")
    print(f"   Issuer: {decoded.get('iss')}")
    print(f"   Expires: {decoded.get('exp')}")
    
    print("\n🔐 Application Permissions (Roles):")
    if 'roles' in decoded:
        for role in decoded['roles']:
            print(f"   ✅ {role}")
        
        # Check for required permissions
        required_permissions = ['User.Read.All', 'Directory.Read.All']
        has_required = any(perm in decoded['roles'] for perm in required_permissions)
        
        if has_required:
            print(f"\n✅ Has required permissions to read user information!")
        else:
            print(f"\n⚠️  Missing required permissions!")
            print(f"   Need one of: {', '.join(required_permissions)}")
    else:
        print("   ❌ No roles/permissions found in token")
        print("   This means admin consent was not granted or permissions not added")
    
    if 'scp' in decoded:
        print(f"\n📝 Delegated Permissions (Scopes): {decoded['scp']}")
        
except Exception as e:
    print(f"❌ Could not decode token: {str(e)}")

print("\n" + "=" * 70)
print("If you don't see User.Read.All or Directory.Read.All above,")
print("the admin consent may not have been granted properly.")
print("=" * 70)
