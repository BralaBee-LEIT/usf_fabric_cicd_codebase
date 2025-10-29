# Production Hardening Architecture - Mermaid Diagrams

**Version:** 1.0  
**Date:** October 29, 2025  
**Source:** [PRODUCTION_HARDENING_ARCHITECTURE.md](PRODUCTION_HARDENING_ARCHITECTURE.md)

---

## 📐 1. Current vs Target Architecture Overview

```mermaid
graph TB
    subgraph "Current Architecture (Baseline)"
        U1[User Layer<br/>CLI Scripts & Scenarios]
        U2[Utility Layer<br/>FabricClient, WorkspaceManager<br/>ItemManager, GitConnector]
        U3[Configuration Layer<br/>ConfigManager, YAML/JSON, .env]
        U4[External Services<br/>Fabric API, Azure AD, Git]
        
        U1 --> U2
        U1 --> U3
        U2 --> U4
        
        style U1 fill:#e1f5ff
        style U2 fill:#fff3e0
        style U3 fill:#f3e5f5
        style U4 fill:#e8f5e9
    end
    
    subgraph "Target Architecture (Production-Ready)"
        T1[User Layer<br/>CLI + Scenarios + Health Checks]
        T2[Enhanced Utilities<br/>+ Retry Logic<br/>+ Circuit Breaker<br/>+ Transactions]
        T3[Reliability Layer<br/>RetryHandler<br/>CircuitBreaker<br/>TransactionMgr<br/>FeatureFlags]
        T4[Observability<br/>App Insights<br/>Telemetry<br/>Metrics<br/>Dashboards]
        T5[Security & Config<br/>SecretManager<br/>ConfigValidator<br/>Schema Validation]
        T6[External Services<br/>+ Key Vault<br/>+ App Insights]
        
        T1 --> T2
        T1 --> T3
        T1 --> T4
        T2 --> T3
        T2 --> T5
        T2 --> T6
        T3 --> T6
        T4 --> T6
        T5 --> T6
        
        style T1 fill:#4caf50
        style T2 fill:#ff9800
        style T3 fill:#2196f3
        style T4 fill:#9c27b0
        style T5 fill:#f44336
        style T6 fill:#00bcd4
    end
```

---

## 🔐 2. Secret Management Flow

```mermaid
flowchart TD
    A[Application Requests Secret] --> B{Feature Flag<br/>USE_KEY_VAULT?}
    
    B -->|Enabled| C{Check Cache<br/>TTL=1hr}
    B -->|Disabled| D[Load from .env]
    
    C -->|Cache Hit| E[Return Cached Value]
    C -->|Cache Miss| F[Fetch from Key Vault<br/>with Retry]
    
    F -->|Success| G[Cache Result<br/>Return Value]
    F -->|Failure| H[Fallback to .env<br/>Graceful Degradation]
    
    D --> I[Return Secret]
    E --> I
    G --> I
    H --> I
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style F fill:#ff9800
    style G fill:#4caf50
    style H fill:#f44336
    style I fill:#00bcd4
```

---

## 🔄 3. Authentication Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant SM as SecretManager
    participant MSAL as MSAL Library
    participant AAD as Azure AD
    participant Fabric as Fabric API
    
    App->>SM: Request Secrets
    SM->>SM: Load AZURE_TENANT_ID<br/>AZURE_CLIENT_ID<br/>AZURE_CLIENT_SECRET
    
    SM->>MSAL: Initialize<br/>ConfidentialClientApplication
    MSAL->>AAD: Authentication Request<br/>Client Credentials Flow
    AAD->>MSAL: JWT Access Token<br/>(Valid ~1hr)
    
    MSAL->>App: Return Token
    
    App->>Fabric: API Request<br/>Authorization: Bearer {token}
    Fabric->>Fabric: Validate Token
    Fabric->>App: API Response
    
    Note over MSAL,AAD: Token cached for reuse
    Note over App,Fabric: Retry logic + Circuit breaker applied
```

---

## 🔄 4. Retry Logic with Circuit Breaker

```mermaid
stateDiagram-v2
    [*] --> CLOSED: Initial State
    
    CLOSED --> ExecuteRequest: Request arrives
    ExecuteRequest --> CheckRetry: Failure (408, 429, 5xx)
    ExecuteRequest --> ResetFailures: Success
    
    CheckRetry --> Retry1: Attempt 1 failed<br/>Wait 2s
    Retry1 --> Retry2: Attempt 2 failed<br/>Wait 4s
    Retry2 --> Retry3: Attempt 3 failed<br/>Wait 8s
    Retry3 --> IncrementFailures: All retries exhausted
    
    IncrementFailures --> CheckThreshold: Increment failure count
    CheckThreshold --> OPEN: Failures ≥ 5
    CheckThreshold --> CLOSED: Failures < 5
    
    OPEN --> WaitTimeout: Start 60s timer
    WaitTimeout --> HALF_OPEN: Timeout expired
    
    HALF_OPEN --> ExecuteTest: Test request
    ExecuteTest --> CLOSED: Success (reset)
    ExecuteTest --> OPEN: Failure (back to open)
    
    OPEN --> RejectRequest: New request arrives
    RejectRequest --> ReturnError: Circuit OPEN error
    
    ResetFailures --> CLOSED: Continue
    
    style CLOSED fill:#4caf50
    style HALF_OPEN fill:#ff9800
    style OPEN fill:#f44336
    style ExecuteRequest fill:#2196f3
    style RejectRequest fill:#9c27b0
```

---

## 🔁 5. Transaction Rollback Flow

```mermaid
flowchart TD
    A[Start Deployment Transaction] --> B[Generate transaction_id]
    B --> C[Initialize resources list]
    
    C --> D[Operation 1:<br/>Create Workspace]
    D -->|Success| E[Register for Rollback:<br/>Delete Workspace]
    E --> F[Operation 2:<br/>Add Users]
    
    F -->|Success| G[Register for Rollback:<br/>Remove Users]
    G --> H[Operation 3:<br/>Connect Git]
    
    H -->|Failure| I[Trigger Rollback]
    H -->|Success| J[Commit Transaction]
    
    I --> K[Rollback Step 1:<br/>Disconnect Git]
    K --> L[Rollback Step 2:<br/>Remove Users]
    L --> M[Rollback Step 3:<br/>Delete Workspace]
    
    M --> N[All Changes Reverted]
    J --> O[Deployment Complete]
    
    style A fill:#e1f5ff
    style D fill:#4caf50
    style F fill:#4caf50
    style H fill:#f44336
    style I fill:#ff9800
    style K fill:#ff9800
    style L fill:#ff9800
    style M fill:#ff9800
    style N fill:#9c27b0
    style O fill:#00bcd4
```

---

## 📊 6. Telemetry Data Flow

```mermaid
flowchart LR
    A[Application Code<br/>with telemetry_logger.operation] --> B[TelemetryLogger<br/>Capture Context]
    
    B --> C{Execute<br/>Operation}
    
    C -->|Success| D[Measure Duration<br/>Capture Result]
    C -->|Error| E[Measure Duration<br/>Capture Exception]
    
    D --> F[Emit Telemetry]
    E --> F
    
    F --> G[Application Insights]
    
    G --> H1[Custom Events]
    G --> H2[Custom Metrics]
    G --> H3[Dependencies]
    G --> H4[Exceptions]
    
    H1 --> I[Azure Monitor<br/>Log Analytics]
    H2 --> I
    H3 --> I
    H4 --> I
    
    I --> J1[Kusto Queries]
    I --> J2[Dashboards]
    I --> J3[Alerts]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style F fill:#ff9800
    style G fill:#4caf50
    style I fill:#2196f3
    style J1 fill:#9c27b0
    style J2 fill:#9c27b0
    style J3 fill:#9c27b0
```

---

## 🧪 7. Test Pyramid

```mermaid
graph TD
    subgraph "Test Coverage Strategy"
        E2E["E2E Tests (5 tests)<br/>Full Workflows<br/>Real environments"]
        INT["Integration Tests (20 tests)<br/>Real API calls<br/>Component interactions"]
        UNIT["Unit Tests (100+ tests)<br/>Mocked/Isolated<br/>Individual functions"]
        
        E2E --> INT
        INT --> UNIT
        
        style E2E fill:#f44336,stroke:#c62828,stroke-width:3px
        style INT fill:#ff9800,stroke:#ef6c00,stroke-width:3px
        style UNIT fill:#4caf50,stroke:#388e3c,stroke-width:3px
    end
    
    subgraph "Coverage Targets"
        T1["Unit Tests: >90%<br/>Current: ~60%<br/>Gap: +30%"]
        T2["Integration: >80%<br/>Current: ~20%<br/>Gap: +60%"]
        T3["E2E: Critical Paths<br/>Current: 0%<br/>Status: New"]
        
        style T1 fill:#fff3e0
        style T2 fill:#fff3e0
        style T3 fill:#fff3e0
    end
```

---

## 🔄 8. Migration Strategy Timeline

```mermaid
gantt
    title Production Hardening Migration Strategy
    dateFormat YYYY-MM-DD
    section Phase 1: Foundation
    Add SecretManager with feature flag :done, p1, 2025-10-28, 7d
    Maintain .env compatibility :done, p1a, 2025-10-28, 7d
    No breaking changes :done, p1b, 2025-10-28, 7d
    
    section Phase 2: Gradual Adoption
    Enable retry logic :active, p2, 2025-11-04, 7d
    Enable transaction rollback :active, p2a, 2025-11-04, 7d
    Monitor for issues :active, p2b, 2025-11-04, 7d
    
    section Phase 3: Full Rollout
    Enable Application Insights :p3, 2025-11-11, 7d
    Enable all feature flags :p3a, 2025-11-11, 7d
    Deprecation warnings :p3b, 2025-11-11, 7d
    
    section Phase 4: Enforcement
    Require Key Vault (prod) :p4, 2025-11-18, 7d
    Document .env (dev only) :p4a, 2025-11-18, 7d
    Complete test coverage :p4b, 2025-11-18, 7d
```

---

## 🌍 9. Environment Strategy

```mermaid
graph TB
    subgraph "Local Development"
        L1[.env for secrets<br/>No Key Vault required]
        L2[Feature flags: OFF by default]
        L3[Retry logic: ENABLED]
        L4[Transaction rollback: DISABLED]
        L5[Telemetry: DISABLED or local]
        
        L1 --> L2
        L2 --> L3
        L3 --> L4
        L4 --> L5
        
        style L1 fill:#e1f5ff
        style L2 fill:#e1f5ff
        style L3 fill:#e1f5ff
        style L4 fill:#e1f5ff
        style L5 fill:#e1f5ff
    end
    
    subgraph "Development (Azure)"
        D1[Key Vault: ENABLED]
        D2[Feature flags: ALL ON]
        D3[Telemetry: dev App Insights]
        D4[Transaction rollback: ENABLED]
        
        D1 --> D2
        D2 --> D3
        D3 --> D4
        
        style D1 fill:#fff3e0
        style D2 fill:#fff3e0
        style D3 fill:#fff3e0
        style D4 fill:#fff3e0
    end
    
    subgraph "Production (Azure)"
        P1[Key Vault: REQUIRED]
        P2[Feature flags: ALL ON<br/>Cannot disable]
        P3[Telemetry: prod App Insights]
        P4[Transaction rollback: REQUIRED]
        P5[Circuit breaker: Strict thresholds]
        P6[Health checks: MANDATORY]
        
        P1 --> P2
        P2 --> P3
        P3 --> P4
        P4 --> P5
        P5 --> P6
        
        style P1 fill:#c8e6c9
        style P2 fill:#c8e6c9
        style P3 fill:#c8e6c9
        style P4 fill:#c8e6c9
        style P5 fill:#c8e6c9
        style P6 fill:#c8e6c9
    end
    
    Local --> Development
    Development --> Production
```

---

## 📊 10. Monitoring Metrics Dashboard

```mermaid
graph TB
    subgraph "API Performance"
        AP1[Request Duration<br/>Alert: >5s P95]
        AP2[Request Rate<br/>Alert: >100 req/min]
    end
    
    subgraph "Reliability"
        R1[Error Rate<br/>Alert: >5%]
        R2[Circuit Breaker Opens<br/>Alert: >3 per hour]
        R3[Retry Count<br/>Alert: >10% of requests]
    end
    
    subgraph "Deployment"
        D1[Rollback Count<br/>Alert: >1 per day]
        D2[Deployment Duration<br/>Alert: >10 min P95]
    end
    
    subgraph "Authentication"
        A1[Token Refresh Failures<br/>Alert: >0]
    end
    
    subgraph "Configuration"
        C1[Config Validation Failures<br/>Alert: >0]
    end
    
    AP1 --> Monitor[Azure Monitor<br/>Unified Dashboard]
    AP2 --> Monitor
    R1 --> Monitor
    R2 --> Monitor
    R3 --> Monitor
    D1 --> Monitor
    D2 --> Monitor
    A1 --> Monitor
    C1 --> Monitor
    
    Monitor --> Alerts[Alert Rules<br/>Automated Response]
    
    style AP1 fill:#2196f3
    style AP2 fill:#2196f3
    style R1 fill:#ff9800
    style R2 fill:#ff9800
    style R3 fill:#ff9800
    style D1 fill:#4caf50
    style D2 fill:#4caf50
    style A1 fill:#9c27b0
    style C1 fill:#f44336
    style Monitor fill:#00bcd4
    style Alerts fill:#e91e63
```

---

## 🎯 11. Success Criteria Matrix

```mermaid
mindmap
  root((Production<br/>Hardening<br/>Success))
    Functional
      Scenarios work without modification
      Key Vault or .env support
      Auto rollback on failure
      Auto retry transient errors
      All ops emit telemetry
    Non-Functional
      <5% performance degradation
      <1% error rate
      60s circuit breaker recovery
      >90% unit test coverage
      >80% integration coverage
    Operational
      Health check <2s response
      Alerts fire within 5 min
      Rollback complete <2 min
      Complete documentation
```

---

## 🔄 12. Complete System Architecture (Detailed)

```mermaid
graph TB
    subgraph "User Interaction Layer"
        CLI[CLI Scripts<br/>fabric-cli-enhanced.sh]
        Scenarios[Scenarios<br/>Automated Deployment<br/>Config-Driven<br/>Feature Branch]
        Health[Health Checks<br/>/health<br/>/readiness]
    end
    
    subgraph "Application Layer"
        WM[WorkspaceManager<br/>+ Transactions]
        IM[ItemManager<br/>+ Retry Logic]
        GC[GitConnector<br/>+ OAuth Flow]
        FC[FabricClient<br/>+ Circuit Breaker]
        GraphC[GraphClient<br/>+ Permission Check]
    end
    
    subgraph "Reliability Layer"
        RH[RetryHandler<br/>Exponential Backoff]
        CB[CircuitBreaker<br/>CLOSED/OPEN/HALF_OPEN]
        TM[TransactionManager<br/>Rollback Support]
        FF[FeatureFlags<br/>Gradual Rollout]
    end
    
    subgraph "Observability Layer"
        TL[TelemetryLogger<br/>Operation Tracking]
        AI[Application Insights<br/>Azure Monitor]
        Metrics[Custom Metrics<br/>Performance KPIs]
        Dash[Dashboards<br/>Real-time Monitoring]
    end
    
    subgraph "Security & Configuration"
        SM[SecretManager<br/>Key Vault + .env<br/>Cache TTL=1hr]
        CV[ConfigValidator<br/>JSON Schema<br/>Type Validation]
        SV[SchemaValidator<br/>Pre-deployment<br/>Runtime Checks]
    end
    
    subgraph "External Services"
        FabricAPI[Microsoft Fabric API]
        AAD[Azure AD<br/>Authentication]
        Git[GitHub/Azure DevOps]
        KV[Azure Key Vault]
        AppInsights[Application Insights]
    end
    
    CLI --> WM
    CLI --> IM
    Scenarios --> WM
    Scenarios --> GC
    Health --> WM
    
    WM --> RH
    IM --> RH
    GC --> RH
    FC --> CB
    GraphC --> CB
    
    RH --> TM
    CB --> TM
    TM --> FF
    
    WM --> TL
    IM --> TL
    GC --> TL
    TL --> AI
    AI --> Metrics
    Metrics --> Dash
    
    WM --> SM
    IM --> SM
    GC --> SM
    SM --> CV
    CV --> SV
    
    FC --> FabricAPI
    GraphC --> AAD
    GC --> Git
    SM --> KV
    TL --> AppInsights
    
    style CLI fill:#4caf50
    style Scenarios fill:#4caf50
    style Health fill:#4caf50
    style RH fill:#2196f3
    style CB fill:#2196f3
    style TM fill:#2196f3
    style FF fill:#2196f3
    style TL fill:#9c27b0
    style AI fill:#9c27b0
    style SM fill:#f44336
    style CV fill:#f44336
    style KV fill:#ff9800
    style AppInsights fill:#ff9800
```

---

## 📝 Usage Instructions

### Rendering These Diagrams

**1. In GitHub/GitLab:**
- These diagrams will render automatically in Markdown preview
- Click on diagrams to see them in full size

**2. In VS Code:**
- Install extension: "Markdown Preview Mermaid Support"
- Open this file and click "Open Preview" (Ctrl+Shift+V)

**3. In Documentation Sites:**
- Most modern documentation tools (MkDocs, Docusaurus, etc.) support Mermaid
- Copy diagram code blocks directly

**4. As Images:**
- Use [Mermaid Live Editor](https://mermaid.live/) to export as PNG/SVG
- Copy diagram code and paste into editor

### Customization

Each diagram uses consistent color coding:
- 🔵 **Blue** (#2196f3) - Reliability/Retry components
- 🟠 **Orange** (#ff9800) - Processing/Transition states
- 🟢 **Green** (#4caf50) - Success states/User layer
- 🔴 **Red** (#f44336) - Error states/Security
- 🟣 **Purple** (#9c27b0) - Monitoring/Observability
- 🔷 **Cyan** (#00bcd4) - External services

---

**Document Owner:** GitHub Copilot  
**Source:** PRODUCTION_HARDENING_ARCHITECTURE.md  
**Generated:** October 29, 2025  
**Format:** Mermaid.js v10.x
