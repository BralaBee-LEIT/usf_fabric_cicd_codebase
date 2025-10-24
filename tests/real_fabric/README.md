# Real Fabric Integration Testing Guide

## Overview

The `tests/real_fabric/` directory contains integration tests that interact with **actual Microsoft Fabric resources**. Unlike the mocked E2E tests, these tests create real workspaces, lakehouses, and other items in your Fabric environment.

## ⚠️ Important Warnings

- **CREATES REAL RESOURCES**: Tests create actual Fabric workspaces and items
- **INCURS COSTS**: Minimal but real Azure/Fabric costs
- **NOT FOR CI/CD**: Should only be run manually by developers
- **REQUIRES PERMISSIONS**: Service principal needs Fabric Admin or Contributor role
- **CLEANUP AUTOMATIC**: Resources are deleted after each test

## Test Status

| Test | Status | Description |
|------|--------|-------------|
| `test_create_workspace_with_production_features` | ✅ PASSING | Creates and validates workspace |
| `test_create_workspace_and_lakehouse` | ⚠️ INVESTIGATING | Lakehouse API 400 error |
| `test_circuit_breaker_with_real_api` | ✅ PASSING | Circuit breaker validation |

## Prerequisites

### 1. Azure Service Principal Setup

Your service principal needs:
- **Fabric Admin** or **Contributor** role in Fabric capacity
- Proper permissions in Azure AD
- Valid credentials in `.env` file

```bash
# Required environment variables
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
FABRIC_CAPACITY_ID=your-capacity-id
```

### 2. Capacity Requirements

- Active Fabric capacity (F2 or higher recommended)
- Available compute resources
- Sufficient quota for test workspaces

## Running Real Integration Tests

### Run All Real Fabric Tests

```bash
# Run all tests marked with @pytest.mark.real_fabric
pytest tests/real_fabric/ -v -s -m real_fabric
```

### Run Specific Test

```bash
# Run only workspace creation test
pytest tests/real_fabric/test_real_fabric_deployment.py::TestRealFabricDeployment::test_create_workspace_with_production_features -v -s -m real_fabric
```

### Normal Test Runs (Exclude Real Tests)

```bash
# This won't run real_fabric tests (configured in pyproject.toml)
pytest tests/unit/ tests/integration/ tests/e2e/
```

## What Gets Created

### Test: `test_create_workspace_with_production_features`

1. **Workspace**: `test-cicd-{timestamp}-{uuid}`
2. **Description**: "Automated test workspace - safe to delete"
3. **Duration**: ~6 seconds
4. **Cleanup**: Automatic deletion after validation

**Example Output:**
```
🔧 Creating real workspace: test-cicd-20251024-112025-b001b586
   Capacity ID: 0749B635-C51B-46C6-948A-02F05D7FE177
✅ Workspace created: 3667fd44-d488-4dfb-9eeb-1d7fb629346b
✅ Workspace validated: test-cicd-20251024-112025-b001b586
🧹 Cleaning up workspace: 3667fd44-d488-4dfb-9eeb-1d7fb629346b
✅ Workspace deleted successfully
PASSED (6.42s)
```

### Test: `test_create_workspace_and_lakehouse`

**Status**: ⚠️ Currently investigating lakehouse API 400 error

1. **Workspace**: Created successfully
2. **Lakehouse**: API returns 400 Bad Request
3. **Issue**: Investigating proper lakehouse creation parameters

## Safety Features

### 1. Automatic Cleanup

All tests use `try/finally` blocks to ensure cleanup:

```python
try:
    workspace_response = fabric_client.create_workspace(...)
    workspace_id = workspace_response["id"]
    # ... test logic ...
finally:
    if workspace_id:
        fabric_client.delete_workspace(workspace_id)
```

### 2. Unique Naming

Resources use timestamps + UUIDs to avoid conflicts:
```python
test-cicd-20251024-112025-b001b586
```

### 3. Timeout Protection

Tests have 5-minute timeout limits:
```python
@pytest.mark.timeout(300)
```

### 4. Production Hardening Integration

Tests use:
- **Retry logic** (`@fabric_retry`) for transient failures
- **Circuit breakers** for repeated failures
- **Transaction tracking** (optional)

## Cost Estimate

### Per Test Run

- **Workspace creation**: Free
- **Lakehouse creation**: Free (storage costs if used)
- **Test duration**: 5-10 seconds per test
- **Resources exist for**: <30 seconds (deleted immediately)
- **Total cost**: Negligible (<$0.01 per run)

### Monthly Estimate

- **10 test runs/day** × 30 days = 300 runs/month
- **Estimated cost**: <$3.00/month

## Troubleshooting

### Issue: Missing Azure Credentials

```
ValueError: Missing Azure credentials
```

**Solution**: Ensure `.env` file has all required variables:
```bash
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
FABRIC_CAPACITY_ID=...
```

### Issue: 401 Unauthorized

```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Solution**: 
1. Verify service principal credentials are correct
2. Check service principal has Fabric Admin role
3. Ensure token hasn't expired
4. Verify capacity ID is correct

### Issue: 403 Forbidden

```
requests.exceptions.HTTPError: 403 Client Error: Forbidden
```

**Solution**: Service principal needs additional permissions:
- Add to Fabric Admin role in capacity settings
- Verify Azure AD permissions
- Check conditional access policies

### Issue: 400 Bad Request (Lakehouse)

```
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: .../lakehouses
```

**Status**: Under investigation. Possible causes:
- Lakehouse name validation rules
- Workspace not fully provisioned yet
- API version mismatch
- Missing required parameters

### Issue: Resources Not Cleaned Up

If tests fail and resources aren't deleted:

```python
# Run cleanup utility
python tests/real_fabric/test_real_fabric_deployment.py
```

Or manually delete via Azure Portal:
1. Go to Fabric Portal
2. Find workspaces starting with `test-cicd-`
3. Delete manually

## Configuration

### Pytest Markers

Configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "real_fabric: Tests that create actual resources (run manually only)",
]
# Don't run real_fabric tests by default
addopts = "-m 'not real_fabric'"
```

### Feature Flags

Real Fabric tests use production hardening features:
- ✅ Retry logic (enabled)
- ✅ Circuit breakers (enabled)
- ⚠️ Transaction rollback (optional)
- ⚠️ Telemetry (removed for simplicity)
- ⚠️ Health checks (optional)

## Best Practices

### 1. Run During Development Only

- **DO**: Run locally when testing Fabric API integration
- **DON'T**: Add to CI/CD pipelines
- **DON'T**: Run on every commit

### 2. Monitor Costs

- Check Azure billing regularly
- Set up cost alerts in Azure Portal
- Review Fabric capacity usage

### 3. Clean Up Failed Tests

- Always verify resources are deleted
- Check Fabric Portal after test runs
- Use cleanup utility if needed

### 4. Test Responsibly

- Limit test frequency
- Use minimal resources
- Don't create large datasets
- Delete immediately after validation

## Future Enhancements

### Planned Improvements

1. **Fix lakehouse creation** - Investigate 400 error
2. **Add more item types** - Notebooks, reports, semantic models
3. **Transaction rollback integration** - Automatic cleanup on failure
4. **Telemetry integration** - Track test metrics
5. **Health check validation** - Test with real Fabric API
6. **Cleanup utility** - Better handling of orphaned resources

### Potential New Tests

- ✅ Workspace with multiple lakehouses
- ✅ Notebook creation and execution
- ✅ Data pipeline deployment
- ✅ Semantic model creation
- ✅ Git integration testing
- ✅ Deployment pipeline testing

## Support

### Documentation

- [Microsoft Fabric API Docs](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Azure Service Principal Setup](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [Fabric Capacity Management](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-capacity-settings)

### Internal Resources

- `tests/e2e/` - Mocked E2E tests (safe to run anytime)
- `tests/integration/` - Integration tests (no real resources)
- `tests/unit/` - Unit tests (fast, isolated)
- `PRODUCTION_HARDENING_COMPLETE.md` - Complete hardening docs

## Summary

Real Fabric integration tests provide:
- ✅ **Validation** against actual Fabric API
- ✅ **Confidence** in production deployment
- ✅ **Safety** with automatic cleanup
- ✅ **Cost-effective** testing (~seconds per run)
- ⚠️ **Manual only** - not for automation

**Current Status**: 2/3 tests passing, lakehouse creation under investigation.
