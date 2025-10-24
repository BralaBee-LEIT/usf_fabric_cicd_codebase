# Production Hardening Migration Guide

**Version:** 1.0  
**Date:** 24 October 2025  
**Audience:** Developers, DevOps Engineers

---

## 📋 **Overview**

This guide walks through migrating from the current implementation to the production-hardened version with **zero breaking changes**.

**Key Principle:** All existing code continues to work unchanged. New features are opt-in via feature flags.

---

## 🎯 **Migration Path**

```
Current State              Intermediate State           Target State
─────────────             ──────────────────           ────────────
.env secrets    ──────>   Key Vault enabled  ──────>  Key Vault required
No retry        ──────>   Retry optional     ──────>  Retry default
No rollback     ──────>   Rollback optional  ──────>  Rollback required
No telemetry    ──────>   Telemetry optional ──────>  Telemetry required

Timeline:                 Week 1-2                     Week 3-4
```

---

## 📅 **Week-by-Week Migration Plan**

### **Week 1: Foundation (No Breaking Changes)**

#### **Day 1: Add Dependencies**

1. **Update `requirements.txt`:**

```diff
# Core dependencies for Microsoft Fabric CI/CD
PyYAML==6.0.1
msal==1.26.0
requests==2.31.0
urllib3==2.1.0

# Testing
pytest==8.3.3
pytest-cov==6.0.0
pytest-mock==3.14.0

# Code quality
flake8==7.0.0
black==24.3.0
isort==5.13.2
mypy==1.8.0

# Security scanning
bandit==1.7.7
safety==3.0.1

# Additional utilities
python-dotenv==1.0.1
jsonschema==4.21.1

+# Production hardening (NEW)
+azure-keyvault-secrets==4.7.0
+azure-identity==1.15.0
+tenacity==8.2.3
+applicationinsights==0.11.10
```

2. **Install dependencies:**

```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
pip install -r requirements.txt
```

3. **Verify installation:**

```bash
python -c "import azure.keyvault.secrets; print('Key Vault SDK OK')"
python -c "import tenacity; print('Tenacity OK')"
python -c "import applicationinsights; print('App Insights OK')"
```

**Expected Output:**
```
Key Vault SDK OK
Tenacity OK
App Insights OK
```

---

#### **Day 1-2: Add Feature Flags (Non-Breaking)**

1. **Create `ops/scripts/utilities/feature_flags.py`:**

```python
"""
Feature flags for production hardening
All features disabled by default for backward compatibility
"""

import os
import logging

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Control rollout of production hardening features"""

    # Secret Management
    USE_KEY_VAULT = os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"

    # Reliability
    USE_RETRY_LOGIC = os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"
    USE_CIRCUIT_BREAKER = os.getenv("FEATURE_USE_CIRCUIT_BREAKER", "false").lower() == "true"
    USE_ROLLBACK = os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"

    # Observability
    USE_TELEMETRY = os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"

    @classmethod
    def log_status(cls):
        """Log current feature flag status"""
        logger.info("Feature Flags Status:")
        logger.info(f"  USE_KEY_VAULT: {cls.USE_KEY_VAULT}")
        logger.info(f"  USE_RETRY_LOGIC: {cls.USE_RETRY_LOGIC}")
        logger.info(f"  USE_CIRCUIT_BREAKER: {cls.USE_CIRCUIT_BREAKER}")
        logger.info(f"  USE_ROLLBACK: {cls.USE_ROLLBACK}")
        logger.info(f"  USE_TELEMETRY: {cls.USE_TELEMETRY}")


# Log on import (helps with debugging)
if os.getenv("DEBUG", "false").lower() == "true":
    FeatureFlags.log_status()
```

2. **Verify existing code still works:**

```bash
# Run existing tests - should all pass
pytest tests/ -v

# Run existing scenario - should work unchanged
python scenarios/automated-deployment/run_automated_deployment.py --dry-run
```

**Expected:** All tests pass, no errors.

---

#### **Day 2-3: Add Secret Manager (With Fallback)**

1. **Create `ops/scripts/utilities/secret_manager.py`:**

See [API Documentation](../api/PRODUCTION_HARDENING_API.md#secretmanager-api) for complete implementation.

**Key Points:**
- Defaults to .env when `FEATURE_USE_KEY_VAULT=false`
- Gracefully falls back to .env on Key Vault errors
- No changes required to existing code

2. **Update `.env.example`:**

```diff
# Azure Service Principal Credentials
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

+# Optional: Azure Key Vault (for production)
+KEY_VAULT_URL=https://your-keyvault.vault.azure.net
+
+# Feature Flags (all default to false)
+FEATURE_USE_KEY_VAULT=false
+FEATURE_USE_RETRY_LOGIC=false
+FEATURE_USE_TELEMETRY=false
+FEATURE_USE_ROLLBACK=false
```

3. **Test without Key Vault (existing behavior):**

```bash
# Ensure feature flag is false (default)
export FEATURE_USE_KEY_VAULT=false

# Run existing code - should work exactly as before
python ops/scripts/manage_workspaces.py list-workspaces
```

4. **Test with Key Vault (opt-in):**

```bash
# Set up Key Vault (one-time)
# See setup guide: docs/security/KEY_VAULT_SETUP.md

# Enable feature flag
export FEATURE_USE_KEY_VAULT=true
export KEY_VAULT_URL=https://your-vault.vault.azure.net

# Run code - should use Key Vault
python ops/scripts/manage_workspaces.py list-workspaces
```

**Migration Status After Day 3:**
- ✅ Feature flags in place
- ✅ Secret manager implemented
- ✅ All existing code works unchanged
- ✅ Key Vault available for opt-in testing

---

### **Week 2: Reliability Features**

#### **Day 4-5: Add Retry Logic**

1. **Create `ops/scripts/utilities/retry_handler.py`:**

See [API Documentation](../api/PRODUCTION_HARDENING_API.md#retryhandler-api) for complete implementation.

2. **Update `fabric_api.py` (backward compatible):**

```python
# At top of file
from .retry_handler import fabric_retry
from .feature_flags import FeatureFlags

class FabricClient:
    # Existing code unchanged...
    
    # Add decorator to _make_request method
    @fabric_retry  # <-- Add this line (no-op if feature disabled)
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Fabric API"""
        # Existing implementation unchanged
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        if "timeout" not in kwargs:
            kwargs["timeout"] = HTTP_DEFAULT_TIMEOUT

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, **kwargs)

        if not response.ok:
            logger.error(f"Fabric API error: {response.status_code} - {response.text}")
            response.raise_for_status()

        return response
```

**Key Point:** When `FEATURE_USE_RETRY_LOGIC=false`, the decorator is a no-op. Existing behavior preserved.

3. **Test without retry (default):**

```bash
export FEATURE_USE_RETRY_LOGIC=false
python ops/scripts/manage_workspaces.py list-workspaces
# Should work exactly as before
```

4. **Test with retry (opt-in):**

```bash
export FEATURE_USE_RETRY_LOGIC=true
python ops/scripts/manage_workspaces.py list-workspaces
# Should retry on transient failures
```

---

#### **Day 6-7: Add Transaction Rollback**

1. **Create `ops/scripts/utilities/deployment_transaction.py`:**

See [API Documentation](../api/PRODUCTION_HARDENING_API.md#deploymenttransaction-api) for complete implementation.

2. **Update `run_automated_deployment.py` (backward compatible):**

```python
from ops.scripts.utilities.deployment_transaction import DeploymentTransaction
from ops.scripts.utilities.feature_flags import FeatureFlags
import uuid

def run_deployment(config, dry_run=False):
    """Run deployment with optional transaction support"""
    
    # Create transaction (no-op if feature disabled)
    transaction_id = str(uuid.uuid4())
    
    # Feature flag controls whether rollback happens
    with DeploymentTransaction(transaction_id) as transaction:
        try:
            # Existing code, but pass transaction to methods
            workspace = create_workspace_with_items(config, transaction)
            add_users(workspace["id"], config, transaction)
            connect_git(workspace["id"], config, transaction)
            
            # Success - commit (prevents rollback)
            transaction.commit()
            
            return workspace
        except Exception as e:
            # Automatic rollback if FEATURE_USE_ROLLBACK=true
            # Otherwise, just re-raise exception (existing behavior)
            logger.error(f"Deployment failed: {e}")
            raise

def create_workspace_with_items(config, transaction=None):
    """Create workspace, optionally register for rollback"""
    workspace = workspace_manager.create_workspace(config["workspace_name"])
    
    # Register for rollback (no-op if transaction disabled)
    if transaction and FeatureFlags.USE_ROLLBACK:
        transaction.register_resource(
            resource_type="workspace",
            resource_id=workspace["id"],
            resource_name=workspace["displayName"],
            cleanup_function=workspace_manager.delete_workspace,
            cleanup_args={"workspace_id": workspace["id"], "force": True}
        )
    
    return workspace
```

**Key Point:** Methods accept optional `transaction` parameter. When `None` or feature disabled, no rollback occurs.

3. **Test without rollback (default):**

```bash
export FEATURE_USE_ROLLBACK=false
# On failure, resources remain (existing behavior)
```

4. **Test with rollback (opt-in):**

```bash
export FEATURE_USE_ROLLBACK=true
# On failure, resources automatically cleaned up
```

---

### **Week 3: Observability**

#### **Day 8-10: Add Telemetry**

1. **Create `ops/scripts/utilities/telemetry_logger.py`:**

See [API Documentation](../api/PRODUCTION_HARDENING_API.md#telemetrylogger-api).

2. **Update existing code (minimal changes):**

```python
from ops.scripts.utilities.telemetry_logger import get_telemetry_logger
from ops.scripts.utilities.feature_flags import FeatureFlags

# Get telemetry instance (no-op if feature disabled)
telemetry = get_telemetry_logger()

def create_workspace(name: str):
    """Create workspace with optional telemetry"""
    
    # Track operation (no-op if FEATURE_USE_TELEMETRY=false)
    with telemetry.operation("CreateWorkspace", {"name": name}):
        workspace = fabric_client.create_workspace(name)
        return workspace
```

3. **Configure Application Insights:**

```bash
# Add to .env
export APPINSIGHTS_INSTRUMENTATION_KEY=your-key-here
export FEATURE_USE_TELEMETRY=true
```

---

### **Week 4: Final Migration**

#### **Day 11-13: Enable All Features (Development Environment)**

1. **Update development `.env`:**

```bash
# Enable all production hardening features
FEATURE_USE_KEY_VAULT=true
FEATURE_USE_RETRY_LOGIC=true
FEATURE_USE_ROLLBACK=true
FEATURE_USE_TELEMETRY=true
FEATURE_USE_CIRCUIT_BREAKER=true

# Provide required config
KEY_VAULT_URL=https://dev-keyvault.vault.azure.net
APPINSIGHTS_INSTRUMENTATION_KEY=dev-app-insights-key
```

2. **Run full integration tests:**

```bash
pytest tests/integration/ -v
```

3. **Run E2E scenario tests:**

```bash
pytest tests/e2e/ -v
```

---

#### **Day 14-15: Production Deployment**

1. **Update production `.env`:**

```bash
# All features mandatory in production
FEATURE_USE_KEY_VAULT=true
FEATURE_USE_RETRY_LOGIC=true
FEATURE_USE_ROLLBACK=true
FEATURE_USE_TELEMETRY=true
FEATURE_USE_CIRCUIT_BREAKER=true

KEY_VAULT_URL=https://prod-keyvault.vault.azure.net
APPINSIGHTS_INSTRUMENTATION_KEY=prod-app-insights-key
```

2. **Deployment checklist:**

- [ ] All secrets migrated to Key Vault
- [ ] Application Insights dashboard configured
- [ ] Alerts configured in Azure Monitor
- [ ] Health check endpoint tested
- [ ] Rollback procedures documented
- [ ] Team trained on new features

---

## 🔍 **Verification Checklist**

### **After Each Week**

#### **Week 1: Foundation**
- [ ] All existing tests pass
- [ ] Existing scenarios work unchanged
- [ ] Feature flags work (on/off)
- [ ] Secret manager works with .env
- [ ] Secret manager works with Key Vault (when enabled)

#### **Week 2: Reliability**
- [ ] Retry logic works for transient failures
- [ ] Circuit breaker opens after threshold
- [ ] Transaction rollback cleans up resources
- [ ] All existing scenarios still work without features

#### **Week 3: Observability**
- [ ] Telemetry events appear in App Insights
- [ ] Custom metrics tracked
- [ ] Exceptions logged correctly
- [ ] Dashboards show real-time data

#### **Week 4: Production**
- [ ] All features enabled in production
- [ ] Performance within 5% of baseline
- [ ] Error rate <1%
- [ ] Monitoring alerts configured
- [ ] Documentation complete

---

## 🚨 **Troubleshooting**

### **Issue: Key Vault Access Denied**

**Symptom:**
```
ERROR - Failed to get secret from Key Vault: (Forbidden) Access denied
```

**Solution:**
1. Grant service principal "Key Vault Secrets User" role:
```bash
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee YOUR_CLIENT_ID \
  --scope /subscriptions/SUB_ID/resourceGroups/RG/providers/Microsoft.KeyVault/vaults/VAULT_NAME
```

2. Or use Access Policies (legacy):
```bash
az keyvault set-policy \
  --name YOUR_VAULT \
  --spn YOUR_CLIENT_ID \
  --secret-permissions get list
```

---

### **Issue: Retry Logic Not Working**

**Symptom:**
```
Requests fail immediately, no retries
```

**Solution:**
1. Check feature flag:
```bash
echo $FEATURE_USE_RETRY_LOGIC  # Should be "true"
```

2. Check logs for retry attempts:
```
WARNING - Retrying request (attempt 2/3)
```

3. If not seeing retries, ensure decorator is applied:
```python
@fabric_retry  # <-- Must be present
def _make_request(...):
```

---

### **Issue: Rollback Not Cleaning Up**

**Symptom:**
```
Deployment failed but resources remain
```

**Solution:**
1. Check feature flag:
```bash
echo $FEATURE_USE_ROLLBACK  # Should be "true"
```

2. Ensure resources registered before failure:
```python
transaction.register_resource(...)  # Must happen before failure
```

3. Check rollback logs:
```
WARNING - Rolling back transaction abc-123
INFO - Cleaning up workspace...
```

---

### **Issue: Telemetry Not Appearing**

**Symptom:**
```
No data in Application Insights
```

**Solution:**
1. Check feature flag and instrumentation key:
```bash
echo $FEATURE_USE_TELEMETRY  # Should be "true"
echo $APPINSIGHTS_INSTRUMENTATION_KEY  # Should be set
```

2. Verify instrumentation key is correct:
```bash
# Test with App Insights CLI
az monitor app-insights component show \
  --app YOUR_APP_NAME \
  --resource-group YOUR_RG
```

3. Check for telemetry in code:
```python
telemetry.track_event("TestEvent")
telemetry.flush()  # Force send
```

4. Wait 2-5 minutes for data to appear in portal

---

## 📊 **Rollback Procedures**

### **If Issues Arise During Migration**

#### **Rollback to Week 1 (Foundation Only)**

```bash
# Disable all features except Key Vault
export FEATURE_USE_KEY_VAULT=true
export FEATURE_USE_RETRY_LOGIC=false
export FEATURE_USE_ROLLBACK=false
export FEATURE_USE_TELEMETRY=false

# Restart services
```

#### **Rollback to Pre-Migration (Original State)**

```bash
# Disable all features
export FEATURE_USE_KEY_VAULT=false
export FEATURE_USE_RETRY_LOGIC=false
export FEATURE_USE_ROLLBACK=false
export FEATURE_USE_TELEMETRY=false

# Code works exactly as before
```

**Recovery Time:** < 5 minutes (just change environment variables)

---

## 📝 **Summary**

### **What Changes**

| Component | Before | After | Breaking? |
|-----------|--------|-------|-----------|
| Secret Management | .env only | Key Vault + .env fallback | **No** |
| Error Handling | Fail fast | Retry + circuit breaker | **No** |
| Deployment Failures | Leave artifacts | Automatic rollback | **No** |
| Observability | Logs only | Logs + telemetry | **No** |
| Configuration | Static | Feature flags | **No** |

### **What Stays the Same**

- ✅ All existing CLI commands
- ✅ All existing scenarios
- ✅ All existing configurations
- ✅ All existing tests
- ✅ Local development workflow

### **What's New (Opt-In)**

- 🆕 Azure Key Vault integration
- 🆕 Automatic retry logic
- 🆕 Transaction rollback
- 🆕 Application Insights telemetry
- 🆕 Health check endpoints
- 🆕 Circuit breaker pattern

---

**Document Owner:** GitHub Copilot  
**Last Updated:** 24 October 2025  
**Next Review:** After Week 2 implementation
