#!/usr/bin/env python3
"""
Clear MSAL token cache and test new permissions
"""
import os
from msal import ConfidentialClientApplication

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = "https://api.fabric.microsoft.com/.default"

print("🔄 Creating MSAL app without cache...")

# Create app without persistent cache (force new token)
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
    # Don't use any token cache
)

print("🔄 Acquiring fresh token with new permissions...")
result = app.acquire_token_for_client(scopes=[scope])

if "access_token" in result:
    print("✅ Successfully acquired fresh access token!")
    print(f"   Token type: {result.get('token_type')}")
    print(f"   Expires in: {result.get('expires_in')} seconds")

    # Decode token to check claims (optional - requires pyjwt)
    try:
        import jwt

        decoded = jwt.decode(
            result["access_token"], options={"verify_signature": False}
        )
        print("\n📋 Token Claims:")
        print(f"   Audience: {decoded.get('aud')}")
        print(f"   Issuer: {decoded.get('iss')}")
        print(f"   App ID: {decoded.get('appid')}")
        if "roles" in decoded:
            print(f"   Roles: {', '.join(decoded['roles'])}")
        if "scp" in decoded:
            print(f"   Scopes: {decoded['scp']}")
    except ImportError:
        print("   (Install pyjwt to see token details: pip install pyjwt)")
    except Exception as e:
        print(f"   (Could not decode token: {e})")

    print("\n✅ Token cache cleared and fresh token acquired!")
    print("   You can now try creating workspaces again.")

else:
    print("❌ Failed to acquire token:")
    print(f"   Error: {result.get('error')}")
    print(f"   Description: {result.get('error_description')}")
    print(f"   Correlation ID: {result.get('correlation_id')}")
