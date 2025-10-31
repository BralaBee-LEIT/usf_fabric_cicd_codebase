# GitHub Secrets Configuration Guide

This document explains how to configure GitHub repository secrets for CI/CD pipeline authentication with Microsoft Fabric and Azure services.

## Overview

The CI/CD pipeline requires Azure Service Principal credentials to run integration and E2E tests that interact with real Microsoft Fabric APIs. Unit tests do not require credentials as they use mocking.

## Required Secrets

### 1. Azure Service Principal Credentials

These secrets are required for authenticated API calls to Microsoft Fabric:

| Secret Name | Description | How to Obtain |
|------------|-------------|---------------|
| `AZURE_TENANT_ID` | Azure AD Tenant ID (GUID) | Azure Portal → Azure Active Directory → Overview → Tenant ID |
| `AZURE_CLIENT_ID` | Service Principal Application (Client) ID | Azure Portal → App registrations → Your App → Overview |
| `AZURE_CLIENT_SECRET` | Service Principal Client Secret | Azure Portal → App registrations → Your App → Certificates & secrets |
| `FABRIC_CAPACITY_ID` | Microsoft Fabric Capacity ID | Fabric Portal → Admin → Capacity settings |

### 2. Optional Secrets (for future use)

| Secret Name | Description | Required For |
|------------|-------------|-------------|
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | Resource deployment |
| `AZURE_RESOURCE_GROUP` | Default resource group name | Resource deployment |
| `CODECOV_TOKEN` | Code coverage reporting token | Codecov integration |

## How to Add Secrets to GitHub

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/BralaBee-LEIT/usf_fabric_cicd_codebase`
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add New Repository Secret

1. Click **New repository secret** button
2. Enter the secret **Name** (exactly as shown in the table above)
3. Enter the secret **Value** (the actual credential value)
4. Click **Add secret**

### Step 3: Verify Secrets

After adding all secrets, you should see them listed (values are hidden):

```
✓ AZURE_TENANT_ID
✓ AZURE_CLIENT_ID
✓ AZURE_CLIENT_SECRET
✓ FABRIC_CAPACITY_ID
```

## Creating Azure Service Principal

If you don't have a Service Principal yet, create one:

### Using Azure Portal:

1. **Register an Application:**
   - Azure Portal → Azure Active Directory → App registrations → New registration
   - Name: `fabric-cicd-pipeline`
   - Supported account types: "Accounts in this organizational directory only"
   - Click **Register**

2. **Note the Application (Client) ID:**
   - After registration, copy the **Application (client) ID** → This is your `AZURE_CLIENT_ID`
   - Copy the **Directory (tenant) ID** → This is your `AZURE_TENANT_ID`

3. **Create a Client Secret:**
   - Go to **Certificates & secrets** → **New client secret**
   - Description: "GitHub Actions CI/CD"
   - Expires: 24 months (or as per your policy)
   - Click **Add**
   - **IMPORTANT:** Copy the secret **Value** immediately → This is your `AZURE_CLIENT_SECRET`
   - (You won't be able to see it again!)

4. **Grant Permissions:**
   - Azure Portal → Azure Active Directory → Enterprise applications
   - Find your app → Permissions → Add required permissions
   - Required permissions:
     - `https://analysis.windows.net/powerbi/api/.default` (Fabric API)
     - Microsoft Graph API (User.Read, etc.)

5. **Assign Fabric Roles:**
   - Fabric Portal → Workspace settings → Manage access
   - Add the service principal with **Admin** or **Contributor** role

### Using Azure CLI:

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "fabric-cicd-pipeline" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth

# Output will contain:
# - clientId → AZURE_CLIENT_ID
# - clientSecret → AZURE_CLIENT_SECRET
# - tenantId → AZURE_TENANT_ID
```

## Getting Fabric Capacity ID

### Method 1: Fabric Portal

1. Go to https://app.fabric.microsoft.com
2. Click the **Settings** gear icon (top right)
3. Click **Admin portal**
4. Click **Capacity settings**
5. Select your capacity
6. The Capacity ID is shown in the URL or capacity details

### Method 2: PowerShell

```powershell
# Install Fabric PowerShell module
Install-Module -Name MicrosoftPowerBIMgmt

# Connect
Connect-PowerBIServiceAccount

# List capacities
Get-PowerBICapacity | Select-Object Id, DisplayName

# Copy the Id (GUID) → This is your FABRIC_CAPACITY_ID
```

### Method 3: REST API

```bash
# Get access token
TOKEN=$(az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv)

# List capacities
curl -H "Authorization: Bearer $TOKEN" \
  https://api.powerbi.com/v1.0/myorg/capacities

# Find your capacity and copy the "id" field
```

## CI/CD Pipeline Usage

### Unit Tests (No Credentials Required)
- File: `.github/workflows/ci-cd.yml`
- Job: `unit-tests`
- Credentials: **Not required** (mocked dependencies)
- Runs on: All branches

### Integration Tests (Credentials Required)
- File: `.github/workflows/ci-cd.yml`
- Job: `integration-tests`
- Credentials: **Required** (real API calls, but tests skip external calls)
- Uses secrets:
  ```yaml
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    FABRIC_CAPACITY_ID: ${{ secrets.FABRIC_CAPACITY_ID }}
  ```

### E2E Tests (Full Credentials Required)
- File: `.github/workflows/ci-cd.yml`
- Job: `e2e-tests`
- Credentials: **Required** (real Fabric deployments)
- Marked with `@pytest.mark.real_fabric` (skipped in CI by default)

## Security Best Practices

### ✅ DO:
- Rotate service principal secrets regularly (every 6-12 months)
- Use least-privilege access (only required permissions)
- Monitor service principal activity in Azure AD logs
- Use separate service principals for dev/staging/prod
- Set secret expiration dates

### ❌ DON'T:
- Never commit secrets to git repositories
- Never expose secrets in logs or error messages
- Never share secrets via email or chat
- Never use personal accounts for CI/CD
- Never grant excessive permissions "just in case"

## Troubleshooting

### Problem: "Missing required Azure credentials" error in CI/CD

**Solution:**
1. Verify all 4 required secrets are added to GitHub
2. Check secret names match exactly (case-sensitive)
3. Verify service principal has not expired
4. Check service principal has Fabric workspace access

### Problem: "401 Unauthorized" errors in integration tests

**Solution:**
1. Verify service principal has the correct permissions:
   - Fabric Admin or Contributor role
   - `https://analysis.windows.net/powerbi/api` scope
2. Check client secret has not expired
3. Verify tenant ID is correct

### Problem: "403 Forbidden" errors when creating items

**Solution:**
1. Verify service principal is assigned to a Fabric capacity
2. Check capacity has available resources
3. Verify workspace permissions include Create/Edit rights

### Problem: Tests pass locally but fail in CI/CD

**Solution:**
1. Ensure you're using the same Python version locally and in CI
2. Check if tests are marked with `@pytest.mark.real_fabric`
3. Verify secrets are correctly configured in GitHub
4. Check if your local `.env` file has different values

## Verification

After adding secrets, trigger a CI/CD run to verify:

```bash
# Push to trigger CI/CD
git commit --allow-empty -m "test: Verify GitHub secrets configuration"
git push origin main

# Or trigger manually:
# GitHub → Actions → CI/CD Pipeline → Run workflow
```

Check the workflow run logs:
- ✅ Unit tests should pass (no credentials needed)
- ✅ Integration tests should pass (using secrets)
- ✅ E2E tests should be skipped (marked as real_fabric)

## Support

For issues with secrets configuration:
1. Check Azure Portal → Service Principal → Activity logs
2. Review GitHub Actions logs for error details
3. Verify with: `az ad sp show --id <client-id>`
4. Test locally with same credentials in `.env` file

---

**Last Updated:** October 31, 2025  
**Maintained By:** LEIT TekSystems DevOps Team
