# Diagnostics Tools

Diagnostic scripts for troubleshooting Microsoft Fabric and Azure AD permissions, workspace visibility, and API connectivity issues.

## 📁 Scripts

### Permission Diagnostics

**`check_graph_permissions.py`** - Microsoft Graph API permissions checker
- Validates service principal has Graph API permissions
- Checks for `User.Read.All`, `Directory.Read.All` roles
- Decodes JWT tokens to display granted permissions
- Diagnoses admin consent issues

**Usage:**
```bash
python diagnostics/check_graph_permissions.py
```

**`diagnose_fabric_permissions.py`** - Fabric API permissions diagnostic
- Tests GET (list workspaces) endpoint
- Tests POST (create workspace) endpoint
- Shows specific error codes (401 Unauthorized, 403 Forbidden)
- Provides actionable solutions for common issues

**Usage:**
```bash
python diagnostics/diagnose_fabric_permissions.py
```

---

### Token Management

**`clear_token_cache.py`** - MSAL token cache clearer
- Forces fresh token acquisition from Azure AD
- Clears cached tokens after permission changes
- Useful after updating app registrations in Azure Portal

**Usage:**
```bash
python diagnostics/clear_token_cache.py
```

---

### Workspace Diagnostics

**`diagnose_workspaces.py`** - Workspace visibility diagnostic
- Lists all workspaces accessible via API
- Checks for specific workspace IDs
- Performs direct API lookups by workspace ID
- Diagnoses permission and visibility issues

**Usage:**
```bash
python diagnostics/diagnose_workspaces.py
```

**`verify_workspace.py`** - Specific workspace verification
- Checks if specific workspaces exist in Fabric
- Provides portal URLs for manual verification
- Helps debug registry vs portal mismatches

**Usage:**
```bash
python diagnostics/verify_workspace.py
```

---

## 🔧 Common Use Cases

### "I can't see workspaces I created"
```bash
python diagnostics/diagnose_workspaces.py
```

### "Getting 401/403 errors from Fabric API"
```bash
python diagnostics/diagnose_fabric_permissions.py
```

### "Need to verify Graph API permissions"
```bash
python diagnostics/check_graph_permissions.py
```

### "Permission changes not taking effect"
```bash
python diagnostics/clear_token_cache.py
python diagnostics/diagnose_fabric_permissions.py
```

---

## 📋 Prerequisites

All scripts require:
- `.env` file with Azure credentials configured
- `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
- Virtual environment activated: `conda activate fabric-cicd`

---

## 🔍 Troubleshooting Flow

1. **Start here** → `check_graph_permissions.py` (verify Graph access)
2. **Then** → `diagnose_fabric_permissions.py` (verify Fabric access)
3. **If needed** → `clear_token_cache.py` (clear cache)
4. **Finally** → `diagnose_workspaces.py` (check workspace visibility)

---

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Setup Guide](../setup/README.md) - Environment setup
- [Tools](../tools/README.md) - Operational tools

---

**Location:** `/diagnostics/`  
**Purpose:** Troubleshooting and diagnostics  
**Type:** Support scripts
