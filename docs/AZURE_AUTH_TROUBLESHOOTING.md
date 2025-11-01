# Azure Authentication Troubleshooting Guide

## Common Authentication Errors

### 🔴 Error: "Client secret keys are expired" (AADSTS7000222)

**Full Error:**
```
Authentication failed: AADSTS7000222: The provided client secret keys for app 
'<app-id>' are expired. Visit the Azure portal to create new keys for your app
```

**Cause:** Azure Service Principal client secrets have expiration dates (90 days to 2 years max).

**Solution:**

#### Option 1: Azure Portal (Recommended)
1. Go to: https://portal.azure.com
2. Navigate: Azure Active Directory → App registrations
3. Find your app by searching the App ID from error message
4. Go to: Certificates & secrets
5. Click: "+ New client secret"
6. Set description: "Fabric CI/CD - [Current Month Year]"
7. Set expiration: 180 days or 1 year (recommended)
8. Click: "Add"
9. **COPY THE SECRET VALUE IMMEDIATELY** (shown only once)
10. Update `.env` file:
    ```bash
    AZURE_CLIENT_SECRET=<new-secret-value>
    ```

#### Option 2: Azure CLI
```bash
# Create new client secret (1 year expiration)
az ad app credential reset \
    --id <your-app-id> \
    --years 1

# Copy the outputted secret value to .env
```

#### Verify Fix
```bash
# Test credentials
python quick_preflight_check.py

# Test API connection
python ops/scripts/manage_workspaces.py list
```

---

### 🔴 Error: "Invalid client secret provided" (AADSTS7000215)

**Cause:** The `AZURE_CLIENT_SECRET` in `.env` is incorrect or contains extra spaces.

**Solution:**
1. Check for leading/trailing spaces in `.env`
2. Regenerate secret in Azure Portal (see above)
3. Copy-paste carefully (no line breaks or spaces)

---

### 🔴 Error: "Insufficient privileges" (AADSTS65001)

**Cause:** Service Principal doesn't have required permissions.

**Solution:**
1. Go to: Azure Portal → Azure Active Directory → App registrations
2. Find your app
3. Go to: API permissions
4. Ensure these permissions are granted:
   - **Power BI Service**: Workspace.ReadWrite.All
   - **Microsoft Graph**: User.Read
5. Click: "Grant admin consent"

---

### 🔴 Error: "Tenant not found" (AADSTS90002)

**Cause:** `AZURE_TENANT_ID` in `.env` is incorrect.

**Solution:**
1. Go to: Azure Portal → Azure Active Directory → Overview
2. Copy "Tenant ID" (GUID format)
3. Update `.env`:
    ```bash
    AZURE_TENANT_ID=<correct-tenant-id>
    ```

---

## Preventive Measures

### Set Expiration Reminders
```bash
# Check when your current secret expires
az ad app credential list \
    --id <your-app-id> \
    --query "[].{DisplayName:customKeyIdentifier, EndDate:endDateTime}"
```

### Best Practices
1. **Use longer expiration periods**: 1 year instead of 90 days
2. **Set calendar reminders**: 2 weeks before expiration
3. **Create overlapping secrets**: Add new secret before old one expires
4. **Document rotation**: Keep track of when secrets were last rotated
5. **Team communication**: Notify team when secrets are rotated

### Automated Expiration Check (Optional)

Create a script to check secret expiration:

```python
# check_secret_expiration.py
import os
from datetime import datetime, timedelta
import subprocess
import json

app_id = os.getenv("AZURE_CLIENT_ID")
result = subprocess.run(
    ["az", "ad", "app", "credential", "list", "--id", app_id],
    capture_output=True,
    text=True
)

credentials = json.loads(result.stdout)
for cred in credentials:
    end_date = datetime.fromisoformat(cred["endDateTime"].replace("Z", "+00:00"))
    days_remaining = (end_date - datetime.now()).days
    
    if days_remaining < 14:
        print(f"⚠️  WARNING: Secret expires in {days_remaining} days!")
        print(f"   End date: {end_date}")
        print(f"   Rotate soon: https://portal.azure.com")
    else:
        print(f"✓ Secret expires in {days_remaining} days")
```

---

## Quick Reference

### Required .env Variables
```bash
AZURE_TENANT_ID=<tenant-guid>
AZURE_CLIENT_ID=<app-guid>
AZURE_CLIENT_SECRET=<secret-value>  # Expires every 90 days - 2 years
FABRIC_CAPACITY_ID=<capacity-guid>
```

### Test Commands
```bash
# Verify all credentials
python quick_preflight_check.py

# Test Fabric API connection
python ops/scripts/manage_workspaces.py list

# Diagnose specific permission issues
python diagnostics/diagnose_fabric_permissions.py
```

---

## Getting Help

If issues persist after trying these solutions:

1. **Check logs**: Look in `audit/audit_trail.jsonl` for detailed error messages
2. **Run diagnostics**: `python diagnostics/diagnose_fabric_permissions.py`
3. **Verify permissions**: Ensure Service Principal has Fabric Admin role
4. **Contact admin**: Your Azure AD administrator may need to grant additional permissions

## Related Documentation

- [Azure Service Principal Setup](../docs/getting-started/AZURE_SERVICE_PRINCIPAL_SETUP.md)
- [GitHub Secrets Setup](./GITHUB_SECRETS_SETUP.md)
- [Troubleshooting Guide](../docs/troubleshooting/COMMON_ISSUES.md)
