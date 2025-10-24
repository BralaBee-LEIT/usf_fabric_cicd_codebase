# Production Hardening Architecture

**Version:** 1.0  
**Date:** 24 October 2025  
**Status:** Planning Phase

---

## 📐 **Architecture Overview**

This document describes the architectural changes required to transform the Microsoft Fabric CI/CD framework from development-ready to production-ready.

---

## 🏗️ **Current Architecture (Baseline)**

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  CLI Scripts          │  Scenarios                               │
│  - manage_workspaces  │  - Automated Deployment                  │
│  - init_new_project   │  - Config-Driven Workspace               │
│                       │  - Feature Branch Workflow                │
└───────────┬───────────┴──────────────────────────────┬───────────┘
            │                                          │
            v                                          v
┌───────────────────────┐                 ┌────────────────────────┐
│   Utility Layer       │                 │   Configuration Layer   │
├───────────────────────┤                 ├────────────────────────┤
│ - FabricClient        │                 │ - ConfigManager        │
│ - WorkspaceManager    │                 │ - EnvironmentConfig    │
│ - ItemManager         │                 │ - YAML/JSON configs    │
│ - GitConnector        │                 │ - .env secrets         │
│ - GraphClient         │                 │                        │
└───────────┬───────────┘                 └────────────────────────┘
            │
            v
┌───────────────────────────────────────────────────────────────────┐
│                    External Services                              │
├───────────────────────────────────────────────────────────────────┤
│  Microsoft Fabric API  │  Azure AD  │  Git (GitHub/Azure DevOps) │
└───────────────────────────────────────────────────────────────────┘
```

### **Key Characteristics:**
- ✅ Modular design with clear separation of concerns
- ✅ Environment-aware configuration management
- ✅ Comprehensive audit logging
- ⚠️ Secrets stored in .env files
- ⚠️ No retry logic for transient failures
- ⚠️ No transaction rollback capability
- ⚠️ Limited observability
- ⚠️ Manual error handling

---

## 🎯 **Target Architecture (Production-Ready)**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Layer                                   │
├─────────────────────────────────────────────────────────────────────┤
│  CLI Scripts          │  Scenarios              │  Health Checks    │
│  - manage_workspaces  │  - Automated Deployment │  - /health        │
│  - init_new_project   │  - Config-Driven        │  - /readiness     │
│                       │  - Feature Branch       │                   │
└───────────┬───────────┴──────────────┬──────────┴──────────┬────────┘
            │                          │                      │
            v                          v                      v
┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────┐
│  Enhanced Utilities   │  │  Reliability Layer    │  │ Observability│
├───────────────────────┤  ├──────────────────────┤  ├──────────────┤
│ - FabricClient        │  │ - RetryHandler       │  │ - AppInsights│
│   + Retry logic       │  │ - CircuitBreaker     │  │ - Telemetry  │
│   + Circuit breaker   │  │ - TransactionMgr     │  │ - Metrics    │
│ - WorkspaceManager    │  │ - FeatureFlags       │  │ - Dashboards │
│   + Transactions      │  │                      │  │              │
│ - ItemManager         │  │                      │  │              │
│ - GitConnector        │  │                      │  │              │
│   + OAuth flow        │  │                      │  │              │
│ - GraphClient         │  │                      │  │              │
│   + Permission check  │  │                      │  │              │
└───────────┬───────────┘  └──────────────────────┘  └──────────────┘
            │
            v
┌───────────────────────────────────────────────────────────────────────┐
│                    Security & Configuration Layer                      │
├───────────────────────────────────────────────────────────────────────┤
│  SecretManager        │  ConfigValidator      │  Schema Validation    │
│  - Azure Key Vault    │  - JSON Schema        │  - Pre-deployment     │
│  - .env fallback      │  - Environment merge  │  - Runtime checks     │
│  - Cache with TTL     │  - Type validation    │                       │
└───────────┬───────────────────────────────────────────────────────────┘
            │
            v
┌───────────────────────────────────────────────────────────────────────┐
│                    External Services                                   │
├───────────────────────────────────────────────────────────────────────┤
│  Fabric API  │  Azure AD  │  Git  │  Key Vault  │  App Insights      │
└───────────────────────────────────────────────────────────────────────┘
```

### **Key Enhancements:**
- ✅ Centralized secret management (Azure Key Vault)
- ✅ Automatic retry with exponential backoff
- ✅ Circuit breaker pattern for fault tolerance
- ✅ Transaction rollback on failures
- ✅ Comprehensive telemetry and monitoring
- ✅ Health check endpoints
- ✅ Schema validation for configurations
- ✅ Feature flags for gradual rollout

---

## 🔐 **Security Architecture**

### **Secret Management Flow**

```
┌─────────────────┐
│  Application    │
│  Requests       │
│  Secret         │
└────────┬────────┘
         │
         v
┌────────────────────────────────────────────────────────┐
│              SecretManager                             │
│                                                        │
│  ┌──────────────────────────────────────────┐         │
│  │  Feature Flag Check                      │         │
│  │  USE_KEY_VAULT = true/false              │         │
│  └──────────────┬───────────────────────────┘         │
│                 │                                      │
│        ┌────────┴────────┐                            │
│        │                 │                            │
│    [Enabled]        [Disabled]                        │
│        │                 │                            │
│        v                 v                            │
│  ┌─────────────┐   ┌──────────┐                      │
│  │ Check Cache │   │ Load     │                      │
│  │ (TTL=1hr)   │   │ from .env│                      │
│  └──────┬──────┘   └────┬─────┘                      │
│         │               │                            │
│    [Cache Hit]     [Cache Miss]                      │
│         │               │                            │
│         v               v                            │
│  ┌──────────┐    ┌──────────────┐                   │
│  │ Return   │    │ Fetch from   │                   │
│  │ Cached   │    │ Key Vault    │                   │
│  │ Value    │    │ (with retry) │                   │
│  └──────────┘    └──────┬───────┘                   │
│                         │                            │
│                    [Success]                         │
│                         │                            │
│                         v                            │
│                  ┌──────────────┐                    │
│                  │ Cache Result │                    │
│                  │ Return Value │                    │
│                  └──────────────┘                    │
│                                                       │
│  Fallback on Failure:                                │
│    └─> Load from .env (graceful degradation)        │
└───────────────────────────────────────────────────────┘
```

### **Authentication Flow**

```
┌──────────────┐
│ Application  │
│ Startup      │
└──────┬───────┘
       │
       v
┌─────────────────────────────────────────┐
│  SecretManager Initialization           │
│  - Load AZURE_TENANT_ID                 │
│  - Load AZURE_CLIENT_ID                 │
│  - Load AZURE_CLIENT_SECRET             │
└──────┬──────────────────────────────────┘
       │
       v
┌─────────────────────────────────────────┐
│  MSAL Authentication                    │
│  ConfidentialClientApplication          │
│  - Authority: login.microsoft.com/{tid} │
│  - Scope: https://api.fabric.microsoft.com/.default
└──────┬──────────────────────────────────┘
       │
       v
┌─────────────────────────────────────────┐
│  Token Acquisition                      │
│  acquire_token_for_client()             │
│  - Returns JWT access token             │
│  - Cached for ~1 hour                   │
└──────┬──────────────────────────────────┘
       │
       v
┌─────────────────────────────────────────┐
│  Fabric API Requests                    │
│  Authorization: Bearer {token}          │
│  + Retry logic                          │
│  + Circuit breaker                      │
└─────────────────────────────────────────┘
```

---

## 🔄 **Reliability Architecture**

### **Retry Logic with Circuit Breaker**

```
┌────────────────────────────────────────────────────────┐
│              API Request Flow                          │
│                                                        │
│  ┌──────────────────────────────────────┐             │
│  │  Check Circuit Breaker State         │             │
│  └──────────────┬───────────────────────┘             │
│                 │                                      │
│       ┌─────────┼─────────┐                           │
│       │         │         │                           │
│   [CLOSED]  [HALF_OPEN] [OPEN]                        │
│       │         │         │                           │
│       │         │         v                           │
│       │         │   ┌──────────────────┐              │
│       │         │   │ Reject Request   │              │
│       │         │   │ Return Error     │              │
│       │         │   │ "Circuit OPEN"   │              │
│       │         │   └──────────────────┘              │
│       │         │                                      │
│       v         v                                      │
│  ┌──────────────────────────────────────┐             │
│  │  Execute Request with Retry          │             │
│  │  - Max attempts: 3                   │             │
│  │  - Wait: exponential backoff         │             │
│  │    * 1st retry: 2 seconds            │             │
│  │    * 2nd retry: 4 seconds            │             │
│  │    * 3rd retry: 8 seconds            │             │
│  │  - Retry on: 408, 429, 500-504       │             │
│  └──────────────┬───────────────────────┘             │
│                 │                                      │
│         ┌───────┴────────┐                            │
│         │                │                            │
│     [Success]        [Failure]                        │
│         │                │                            │
│         v                v                            │
│  ┌─────────────┐  ┌──────────────┐                   │
│  │ Reset       │  │ Increment    │                   │
│  │ Failure     │  │ Failure      │                   │
│  │ Count       │  │ Count        │                   │
│  │ Return      │  │              │                   │
│  │ Success     │  │ If count ≥ 5:│                   │
│  └─────────────┘  │ OPEN circuit │                   │
│                   │ Start timer  │                   │
│                   │ (60 seconds) │                   │
│                   └──────────────┘                   │
│                                                        │
│  After timeout: OPEN → HALF_OPEN (test recovery)     │
└────────────────────────────────────────────────────────┘
```

### **Transaction Rollback Flow**

```
┌────────────────────────────────────────────────────────┐
│           Deployment Transaction Flow                  │
│                                                        │
│  1. Create Transaction                                 │
│     transaction_id = uuid4()                           │
│     resources = []                                     │
│                                                        │
│  2. Execute Operations                                 │
│     ┌────────────────────────────┐                    │
│     │ Create Workspace           │                    │
│     │ ✓ Success                  │                    │
│     │ → Register for rollback    │                    │
│     └────────────┬───────────────┘                    │
│                  v                                     │
│     ┌────────────────────────────┐                    │
│     │ Add Users                  │                    │
│     │ ✓ Success                  │                    │
│     │ → Register for rollback    │                    │
│     └────────────┬───────────────┘                    │
│                  v                                     │
│     ┌────────────────────────────┐                    │
│     │ Connect Git                │                    │
│     │ ✗ FAILURE                  │                    │
│     │ → Trigger rollback         │                    │
│     └────────────┬───────────────┘                    │
│                  │                                     │
│                  v                                     │
│  3. Rollback (Reverse Order)                          │
│     ┌────────────────────────────┐                    │
│     │ Disconnect Git (skip)      │                    │
│     └────────────┬───────────────┘                    │
│                  v                                     │
│     ┌────────────────────────────┐                    │
│     │ Remove Users               │                    │
│     │ ✓ Cleaned up               │                    │
│     └────────────┬───────────────┘                    │
│                  v                                     │
│     ┌────────────────────────────┐                    │
│     │ Delete Workspace           │                    │
│     │ ✓ Cleaned up               │                    │
│     └────────────────────────────┘                    │
│                                                        │
│  Result: All changes reverted                         │
└────────────────────────────────────────────────────────┘
```

---

## 📊 **Observability Architecture**

### **Telemetry Data Flow**

```
┌────────────────────────────────────────────────────────────┐
│                Application Code                            │
│  ┌──────────────────────────────────────────┐             │
│  │  with telemetry_logger.operation():      │             │
│  │      fabric_client.create_workspace()    │             │
│  └──────────────┬───────────────────────────┘             │
└─────────────────┼────────────────────────────────────────┘
                  │
                  v
┌────────────────────────────────────────────────────────────┐
│              TelemetryLogger                               │
│  ┌──────────────────────────────────────────┐             │
│  │  Capture:                                │             │
│  │  - Operation name                        │             │
│  │  - Start time                            │             │
│  │  - Parameters                            │             │
│  │  - User context                          │             │
│  └──────────────┬───────────────────────────┘             │
└─────────────────┼────────────────────────────────────────┘
                  │
                  v
┌────────────────────────────────────────────────────────────┐
│              Execute Operation                             │
│  - Try/Catch wrapper                                       │
│  - Measure duration                                        │
│  - Capture result/error                                    │
└──────────────┬─────────────────────────────────────────────┘
               │
               v
┌────────────────────────────────────────────────────────────┐
│              Emit Telemetry                                │
│  ┌──────────────────────────────────────────┐             │
│  │  Application Insights                    │             │
│  │  - Custom Events                         │             │
│  │  - Custom Metrics                        │             │
│  │  - Dependencies                          │             │
│  │  - Exceptions                            │             │
│  └──────────────┬───────────────────────────┘             │
└─────────────────┼────────────────────────────────────────┘
                  │
                  v
┌────────────────────────────────────────────────────────────┐
│              Azure Monitor                                 │
│  ┌──────────────────────────────────────────┐             │
│  │  Log Analytics Workspace                 │             │
│  │  - Kusto queries                         │             │
│  │  - Dashboards                            │             │
│  │  - Alerts                                │             │
│  └──────────────────────────────────────────┘             │
└────────────────────────────────────────────────────────────┘
```

### **Monitored Metrics**

| Category | Metric | Alert Threshold |
|----------|--------|----------------|
| **API Performance** | Request duration | >5 seconds (P95) |
| **API Performance** | Request rate | >100 req/min |
| **Reliability** | Error rate | >5% |
| **Reliability** | Circuit breaker opens | >3 per hour |
| **Reliability** | Retry count | >10% of requests |
| **Deployment** | Rollback count | >1 per day |
| **Deployment** | Deployment duration | >10 minutes (P95) |
| **Authentication** | Token refresh failures | >0 |
| **Configuration** | Config validation failures | >0 |

---

## 🧪 **Testing Architecture**

### **Test Pyramid**

```
                    ┌──────────────┐
                    │     E2E      │  ← 5 tests
                    │   Tests      │  Full workflows
                    └──────────────┘
                  ┌──────────────────┐
                  │   Integration    │  ← 20 tests
                  │     Tests        │  Real API calls
                  └──────────────────┘
              ┌────────────────────────┐
              │      Unit Tests        │  ← 100+ tests
              │   (Mocked/Isolated)    │  Individual functions
              └────────────────────────┘
```

### **Test Coverage Goals**

| Layer | Target Coverage | Current Coverage | Gap |
|-------|----------------|------------------|-----|
| Unit Tests | >90% | ~60% | +30% |
| Integration Tests | >80% | ~20% | +60% |
| E2E Tests | Critical paths | 0% | New |
| Performance Tests | Baseline established | 0% | New |

---

## 🔄 **Migration Strategy**

### **Phase 1: Foundation (Week 1)**
- Add SecretManager with feature flag
- All existing code continues using .env
- No breaking changes

### **Phase 2: Gradual Adoption (Week 2)**
- Enable retry logic via feature flag
- Enable transaction rollback via feature flag
- Monitor for issues

### **Phase 3: Full Rollout (Week 3)**
- Enable Application Insights
- Enable all feature flags by default
- Deprecation warnings for .env-only usage

### **Phase 4: Enforcement (Week 4)**
- Require Key Vault for production deployments
- Document .env usage for local dev only
- Complete test coverage

---

## 📋 **Deployment Architecture**

### **Environment Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                        │
│  - .env for secrets (no Key Vault required)                │
│  - Feature flags default OFF                               │
│  - Retry logic enabled (helps with flaky connections)      │
│  - No transaction rollback (easier debugging)              │
│  - No telemetry (or local App Insights)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Development (Azure)                      │
│  - Key Vault enabled                                        │
│  - All feature flags ON                                     │
│  - Telemetry to dev App Insights                           │
│  - Transaction rollback enabled                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Production (Azure)                       │
│  - Key Vault REQUIRED                                       │
│  - All feature flags ON (cannot disable)                    │
│  - Telemetry to prod App Insights                          │
│  - Transaction rollback REQUIRED                            │
│  - Circuit breaker with strict thresholds                   │
│  - Health checks mandatory                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ All existing scenarios work without modification
- ✅ Secrets can be managed via Key Vault or .env
- ✅ Failed deployments automatically roll back
- ✅ Transient failures automatically retry
- ✅ All operations emit telemetry

### **Non-Functional Requirements**
- ✅ <5% performance degradation from baseline
- ✅ <1% error rate under normal load
- ✅ Recovery from circuit breaker within 60 seconds
- ✅ >90% unit test coverage
- ✅ >80% integration test coverage

### **Operational Requirements**
- ✅ Health check responds within 2 seconds
- ✅ Alerts fire within 5 minutes of incident
- ✅ Rollback completes within 2 minutes
- ✅ Documentation complete and accurate

---

**Document Owner:** GitHub Copilot  
**Last Updated:** 24 October 2025  
**Next Review:** Post-implementation (Week 4)
