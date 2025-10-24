# Production Hardening - Implementation Roadmap

**Date:** 24 October 2025  
**Branch:** `feature/production-hardening`  
**Status:** Ready to Begin

---

## 📊 **Plan Review & Adjustments**

After reviewing the current codebase and existing patterns, here are key adjustments to the original plan:

### **✅ Strengths of Current Implementation**

1. **Modular Architecture** - Clean separation of concerns already exists
2. **Environment Awareness** - `EnvironmentConfig` and `ConfigManager` already handle multi-env
3. **Audit Logging** - Comprehensive audit trail already implemented
4. **Error Handling** - Basic error handling with meaningful messages exists
5. **Naming Validation** - Item naming validator already enforces standards

### **🎯 Adjusted Priorities**

#### **Original Plan Issues:**
- Too aggressive timeline (4 weeks compressed to days)
- Missing dependencies on existing code patterns
- No consideration for current audit logging
- Didn't leverage existing ConfigManager patterns

#### **Adjusted Approach:**

| Priority | Feature | Reason | Timeline |
|----------|---------|--------|----------|
| **P0 - Critical** | Feature Flags | Enables safe rollout | Day 1 (2 hours) |
| **P0 - Critical** | Secret Manager | Security foundation | Day 1-2 (6 hours) |
| **P1 - High** | Retry Logic | Common failure scenario | Day 2-3 (4 hours) |
| **P1 - High** | Transaction Rollback | Prevents orphaned resources | Day 3-4 (8 hours) |
| **P2 - Medium** | Circuit Breaker | Fault isolation | Day 4-5 (4 hours) |
| **P2 - Medium** | Telemetry | Observability | Day 5-7 (8 hours) |
| **P3 - Nice-to-Have** | Graph API Enhancement | UX improvement | Day 8-9 (6 hours) |
| **P3 - Nice-to-Have** | Git OAuth Flow | UX improvement | Day 9-10 (6 hours) |

---

## 🏗️ **Implementation Order (Optimized)**

### **Phase 1: Foundation (Day 1-2) - 8 hours**

**Goal:** Add infrastructure with zero breaking changes

#### **Task 1.1: Create Feature Branch** ⏱️ 15 min

```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
git checkout main
git pull origin main
git checkout -b feature/production-hardening
git push -u origin feature/production-hardening
```

**Acceptance:**
- ✅ Branch exists on remote
- ✅ Branch protection configured (if applicable)

---

#### **Task 1.2: Update Dependencies** ⏱️ 30 min

**Files:**
- `requirements.txt`

**Changes:**
```diff
+# Production hardening dependencies
+azure-keyvault-secrets==4.7.0
+azure-identity==1.15.0
+tenacity==8.2.3
+applicationinsights==0.11.10
```

**Validation:**
```bash
pip install -r requirements.txt
python -c "import azure.keyvault.secrets; print('OK')"
python -c "import tenacity; print('OK')"
```

**Acceptance:**
- ✅ Dependencies install cleanly
- ✅ No version conflicts
- ✅ Import test passes

---

#### **Task 1.3: Create Feature Flags Module** ⏱️ 1 hour

**Files:**
- `ops/scripts/utilities/feature_flags.py` (NEW)
- `ops/scripts/utilities/__init__.py` (UPDATE)

**Implementation:**
```python
"""Feature flags for production hardening"""
import os

class FeatureFlags:
    USE_KEY_VAULT = os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"
    USE_RETRY_LOGIC = os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"
    USE_ROLLBACK = os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"
    USE_TELEMETRY = os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"
    USE_CIRCUIT_BREAKER = os.getenv("FEATURE_USE_CIRCUIT_BREAKER", "false").lower() == "true"
```

**Tests:**
- `tests/unit/test_feature_flags.py` (NEW)

**Acceptance:**
- ✅ All flags default to `false`
- ✅ Environment variables override defaults
- ✅ Unit tests pass

---

#### **Task 1.4: Create Secret Manager** ⏱️ 4 hours

**Files:**
- `ops/scripts/utilities/secret_manager.py` (NEW)
- `tests/unit/test_secret_manager.py` (NEW)
- `.env.example` (UPDATE)

**Key Features:**
1. Key Vault client with DefaultAzureCredential
2. In-memory cache with TTL (1 hour)
3. Graceful fallback to .env
4. Singleton pattern

**Integration Points:**
- Does NOT modify existing code yet
- Can be imported but not required

**Acceptance:**
- ✅ Works with Key Vault when feature enabled
- ✅ Falls back to .env when feature disabled
- ✅ Cache reduces Key Vault calls
- ✅ Unit tests >90% coverage
- ✅ All existing tests still pass

---

#### **Task 1.5: Update .env.example** ⏱️ 15 min

**Files:**
- `.env.example`

**Changes:**
```diff
+# Production Hardening Feature Flags (all default to false)
+FEATURE_USE_KEY_VAULT=false
+FEATURE_USE_RETRY_LOGIC=false
+FEATURE_USE_ROLLBACK=false
+FEATURE_USE_TELEMETRY=false
+FEATURE_USE_CIRCUIT_BREAKER=false
+
+# Azure Key Vault (optional, required if FEATURE_USE_KEY_VAULT=true)
+KEY_VAULT_URL=https://your-keyvault.vault.azure.net
+
+# Application Insights (optional, required if FEATURE_USE_TELEMETRY=true)
+APPINSIGHTS_INSTRUMENTATION_KEY=your-instrumentation-key
```

**Acceptance:**
- ✅ Documentation clear
- ✅ All new variables documented

---

#### **Task 1.6: Commit Phase 1** ⏱️ 30 min

```bash
git add .
git commit -m "feat: Add production hardening foundation

- Add Feature Flags system (all disabled by default)
- Add SecretManager with Key Vault + .env fallback
- Add dependencies (azure-keyvault, tenacity, app insights)
- Update .env.example with new variables
- Add comprehensive unit tests

All features behind feature flags - zero breaking changes"
```

**Validation:**
```bash
# Run all tests
pytest tests/ -v

# Verify black/ruff pass
black --check .
ruff check .

# Push to remote
git push origin feature/production-hardening
```

**Acceptance:**
- ✅ All tests pass
- ✅ CI/CD passes
- ✅ No breaking changes

---

### **Phase 2: Reliability (Day 3-5) - 12 hours**

#### **Task 2.1: Create Retry Handler** ⏱️ 3 hours

**Files:**
- `ops/scripts/utilities/retry_handler.py` (NEW)
- `tests/unit/test_retry_handler.py` (NEW)

**Features:**
1. `@fabric_retry` decorator using tenacity
2. Exponential backoff (2s, 4s, 8s)
3. Rate limiting (429) handling
4. Feature flag integration

**Acceptance:**
- ✅ Retries on transient failures
- ✅ Respects Retry-After header
- ✅ No-op when feature disabled
- ✅ Unit tests >95% coverage

---

#### **Task 2.2: Integrate Retry into FabricClient** ⏱️ 1 hour

**Files:**
- `ops/scripts/utilities/fabric_api.py` (UPDATE)

**Changes:**
```python
from .retry_handler import fabric_retry

class FabricClient:
    @fabric_retry  # <-- Add this line only
    def _make_request(self, method: str, endpoint: str, **kwargs):
        # Existing code unchanged
```

**Acceptance:**
- ✅ Existing tests pass
- ✅ Retry works when feature enabled
- ✅ No retry when feature disabled

---

#### **Task 2.3: Create Circuit Breaker** ⏱️ 2 hours

**Files:**
- `ops/scripts/utilities/circuit_breaker.py` (NEW)
- `tests/unit/test_circuit_breaker.py` (NEW)

**Features:**
1. CLOSED/OPEN/HALF_OPEN states
2. Configurable thresholds
3. Recovery timeout
4. Feature flag integration

**Acceptance:**
- ✅ Opens after threshold failures
- ✅ Attempts recovery after timeout
- ✅ Unit tests >90% coverage

---

#### **Task 2.4: Create Deployment Transaction** ⏱️ 4 hours

**Files:**
- `ops/scripts/utilities/deployment_transaction.py` (NEW)
- `tests/unit/test_deployment_transaction.py` (NEW)

**Features:**
1. Resource registration
2. Reverse-order cleanup
3. Context manager support
4. Feature flag integration

**Acceptance:**
- ✅ Rolls back on failure
- ✅ No rollback when committed
- ✅ Handles cleanup failures gracefully
- ✅ Unit tests >90% coverage

---

#### **Task 2.5: Integrate Transactions** ⏱️ 2 hours

**Files:**
- `scenarios/automated-deployment/run_automated_deployment.py` (UPDATE)
- `ops/scripts/utilities/workspace_manager.py` (UPDATE)

**Changes:**
- Add optional `transaction` parameter to methods
- Register resources when transaction provided
- No changes to method signatures (backward compatible)

**Acceptance:**
- ✅ Existing scenarios work unchanged
- ✅ Rollback works when feature enabled
- ✅ All tests pass

---

#### **Task 2.6: Commit Phase 2** ⏱️ 30 min

```bash
git commit -m "feat: Add reliability features (retry, circuit breaker, rollback)

- Add RetryHandler with exponential backoff
- Add CircuitBreaker for fault isolation
- Add DeploymentTransaction for automatic rollback
- Integrate retry logic into FabricClient
- Add transaction support to automated deployment

All features behind feature flags - backward compatible"
```

---

### **Phase 3: Observability (Day 6-8) - 8 hours**

#### **Task 3.1: Create Telemetry Logger** ⏱️ 4 hours

**Files:**
- `ops/scripts/utilities/telemetry_logger.py` (NEW)
- `tests/unit/test_telemetry_logger.py` (NEW)

**Features:**
1. Application Insights integration
2. Custom events, metrics, exceptions
3. Operation tracking (context manager)
4. Feature flag integration

---

#### **Task 3.2: Add Health Check Script** ⏱️ 2 hours

**Files:**
- `ops/scripts/health_check.py` (NEW)
- `tests/unit/test_health_check.py` (NEW)

**Checks:**
1. Fabric API connectivity
2. Authentication status
3. Capacity availability
4. Key Vault access (if enabled)

---

#### **Task 3.3: Integrate Telemetry** ⏱️ 2 hours

**Files:**
- `ops/scripts/utilities/fabric_api.py` (UPDATE)
- `ops/scripts/utilities/workspace_manager.py` (UPDATE)
- `scenarios/automated-deployment/run_automated_deployment.py` (UPDATE)

**Changes:**
- Wrap operations in telemetry context
- Track key events
- No behavior changes

---

### **Phase 4: Testing & Documentation (Day 9-10) - 8 hours**

#### **Task 4.1: Integration Tests** ⏱️ 3 hours

**Files:**
- `tests/integration/test_secret_manager_integration.py` (NEW)
- `tests/integration/test_retry_integration.py` (NEW)
- `tests/integration/test_transaction_integration.py` (NEW)

---

#### **Task 4.2: E2E Tests** ⏱️ 3 hours

**Files:**
- `tests/e2e/test_complete_deployment.py` (NEW)
- `tests/e2e/test_deployment_rollback.py` (NEW)

---

#### **Task 4.3: Documentation** ⏱️ 2 hours

**Files:**
- `docs/security/KEY_VAULT_SETUP.md` (NEW)
- `docs/operations/RUNBOOK.md` (NEW)
- `docs/deployment/PRODUCTION_CHECKLIST.md` (NEW)
- `README.md` (UPDATE - add feature flags section)

---

## ✅ **Validation Gates**

### **After Phase 1:**
- [ ] All unit tests pass (>90% coverage)
- [ ] All existing integration tests pass
- [ ] Black formatting passes
- [ ] Ruff linting passes
- [ ] CI/CD pipeline passes
- [ ] No performance regression (within 5%)

### **After Phase 2:**
- [ ] Retry logic tested with real API
- [ ] Transaction rollback tested with real resources
- [ ] Circuit breaker tested under load
- [ ] All existing scenarios work unchanged

### **After Phase 3:**
- [ ] Telemetry appears in App Insights
- [ ] Health check returns status
- [ ] Dashboards show real data

### **After Phase 4:**
- [ ] Integration tests pass (>80% coverage)
- [ ] E2E tests pass for all scenarios
- [ ] Documentation complete and reviewed
- [ ] Migration guide tested with fresh environment

---

## 🚀 **Ready to Begin**

### **Starting Point:**
```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
git status  # Should show main branch, clean
```

### **First Command:**
```bash
git checkout -b feature/production-hardening
```

### **Expected Duration:**
- Phase 1 (Foundation): 8 hours → 1 day
- Phase 2 (Reliability): 12 hours → 1.5 days
- Phase 3 (Observability): 8 hours → 1 day
- Phase 4 (Testing/Docs): 8 hours → 1 day

**Total:** 36 hours → 4-5 days

---

## 📋 **Next Steps**

1. **Begin Phase 1, Task 1.1** - Create feature branch
2. **Complete Task 1.2** - Update dependencies
3. **Complete Task 1.3** - Create feature flags
4. **Complete Task 1.4** - Create secret manager
5. **Validate Phase 1** - All tests pass, CI/CD passes
6. **Commit & Push** - Get feedback before Phase 2

---

**Ready to proceed with implementation?**

Type "yes" to begin with Task 1.1 (create feature branch), or let me know if you'd like to adjust the plan further.

---

**Document Owner:** GitHub Copilot  
**Last Updated:** 24 October 2025
