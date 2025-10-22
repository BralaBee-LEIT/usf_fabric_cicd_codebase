# LEIT-Ricoh Domain - Workspace Architecture

## 🏗️ Complete Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LEIT-RICOH DOMAIN                                  │
│                         (leit-ricoh-domain)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LEIT-RICOH WORKSPACE                                 │
│                           (leit-ricoh)                                      │
│                         Environment: dev                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        ┌───────────────┐     ┌──────────────┐    ┌─────────────────┐
        │   STORAGE     │     │  PROCESSING  │    │   ANALYTICS     │
        └───────────────┘     └──────────────┘    └─────────────────┘
                │                     │                    │
                │                     │                    │
      ┌─────────┴─────────┐          │          ┌─────────┴─────────┐
      │                   │          │          │                   │
      ▼                   ▼          ▼          ▼                   ▼
┌──────────┐      ┌──────────┐  ┌──────┐  ┌──────────┐      ┌──────────┐
│Lakehouse │      │Warehouse │  │Note- │  │Pipeline  │      │Semantic  │
│          │      │          │  │books │  │          │      │Model     │
│ Ricoh    │      │ Ricoh    │  │(3x)  │  │ Ricoh    │      │          │
│ Data     │      │Analytics │  │      │  │ Data     │      │ Ricoh    │
│Lakehouse │      │Warehouse │  │      │  │Pipeline  │      │Semantic  │
│          │      │          │  │      │  │          │      │Model     │
└──────────┘      └──────────┘  └──────┘  └──────────┘      └──────────┘
                                    │                             │
                                    │                             ▼
                              ┌─────┴─────┐               ┌──────────┐
                              │           │               │Report    │
                              ▼           ▼               │          │
                         ┌─────────┐  ┌──────────┐       │ Ricoh    │
                         │01_Data  │  │02_Data   │       │Executive │
                         │Ingestion│  │Transform │       │Dashboard │
                         └─────────┘  └──────────┘       └──────────┘
                                           │
                                           ▼
                                    ┌──────────┐
                                    │03_Data   │
                                    │Validation│
                                    └──────────┘
```

## 📊 Item Details

### Storage Layer (2 items)

| Item | Type | Purpose |
|------|------|---------|
| RicohDataLakehouse | Lakehouse | Primary data storage for raw and processed data |
| RicohAnalyticsWarehouse | Warehouse | Structured analytics warehouse for reporting |

### Processing Layer (3 items)

| Item | Type | Purpose |
|------|------|---------|
| 01_DataIngestion | Notebook | Ingest data from source systems |
| 02_DataTransformation | Notebook | Transform and cleanse data |
| 03_DataValidation | Notebook | Validate data quality and completeness |

### Orchestration & Analytics Layer (3 items)

| Item | Type | Purpose |
|------|------|---------|
| RicohDataPipeline | Data Pipeline | Orchestrate notebooks and data flows |
| RicohSemanticModel | Semantic Model | Business logic and relationships |
| RicohExecutiveDashboard | Report | Executive-level visualizations |

## 👥 User Roles & Access

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER ACCESS MATRIX                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────┬──────────────────────────────────┐
│ User            │ Role     │ Capabilities                     │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.admin@    │ Admin    │ • Full workspace management      │
│ leit-teksystems │          │ • User management                │
│ .com            │          │ • All item operations            │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.engineer1 │ Member   │ • Create/edit/delete items       │
│ @leit-teksys... │          │ • Execute notebooks              │
│                 │          │ • Manage pipelines               │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.engineer2 │ Member   │ • Create/edit/delete items       │
│ @leit-teksys... │          │ • Execute notebooks              │
│                 │          │ • Manage pipelines               │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.analyst@  │Contributor│ • Edit existing items            │
│ leit-teksys...  │          │ • Execute notebooks              │
│                 │          │ • Create reports                 │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.business1 │ Viewer   │ • View items                     │
│ @leit-teksys... │          │ • View reports                   │
│                 │          │ • Read-only access               │
├─────────────────┼──────────┼──────────────────────────────────┤
│ ricoh.business2 │ Viewer   │ • View items                     │
│ @leit-teksys... │          │ • View reports                   │
│                 │          │ • Read-only access               │
└─────────────────┴──────────┴──────────────────────────────────┘
```

## 🔄 Data Flow Architecture

```
┌─────────────┐
│   SOURCE    │
│   SYSTEMS   │
└──────┬──────┘
       │
       │ [01_DataIngestion.ipynb]
       ▼
┌─────────────────┐
│ RicohData       │ ◄─── RAW DATA
│ Lakehouse       │
│                 │
│ Tables/         │
│ ├── bronze/     │ ◄─── Landing zone
│ ├── silver/     │ ◄─── Cleaned data
│ └── gold/       │ ◄─── Aggregated data
└────────┬────────┘
         │
         │ [02_DataTransformation.ipynb]
         ▼
┌─────────────────┐
│ RicohAnalytics  │ ◄─── STRUCTURED DATA
│ Warehouse       │
│                 │
│ Schemas/        │
│ ├── dim_*       │ ◄─── Dimensions
│ ├── fact_*      │ ◄─── Facts
│ └── vw_*        │ ◄─── Views
└────────┬────────┘
         │
         │ [03_DataValidation.ipynb]
         ▼
    ┌────────┐
    │ VALID? │
    └───┬────┘
        │
    ┌───┴───┐
    │       │
    ▼       ▼
  YES      NO
    │       │
    │       └─► [Alert & Log]
    │
    │ [RicohSemanticModel]
    ▼
┌─────────────────┐
│ Business Layer  │ ◄─── SEMANTIC MODEL
│                 │
│ • Measures      │
│ • Relationships │
│ • Hierarchies   │
└────────┬────────┘
         │
         │ [RicohExecutiveDashboard]
         ▼
┌─────────────────┐
│   REPORTS &     │
│   DASHBOARDS    │
└─────────────────┘
         │
         └─► END USERS
```

## 🔄 Pipeline Orchestration

```
┌─────────────────────────────────────────────────────────────────┐
│              RicohDataPipeline - Orchestration                  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
  ┌──────────┐          ┌──────────┐         ┌──────────┐
  │ Activity │          │ Activity │         │ Activity │
  │   #1     │──────►   │   #2     │──────►  │   #3     │
  │ Ingest   │          │Transform │         │ Validate │
  └──────────┘          └──────────┘         └──────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
  Execute:             Execute:              Execute:
  01_DataIngestion     02_DataTransform      03_DataValidation
        │                     │                     │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │ Success? │
                        └────┬─────┘
                             │
                        ┌────┴────┐
                        ▼         ▼
                       YES        NO
                        │         │
                        │         └─► Notify & Retry
                        │
                        ▼
                   ┌─────────┐
                   │Completed│
                   └─────────┘
```

## 📈 Scale & Performance

### Current Setup (Development)

| Metric | Value |
|--------|-------|
| Workspaces | 1 |
| Fabric Items | 8 |
| Notebooks | 3 |
| Storage Items | 2 |
| Users | 6 (configured) |
| Environment | Dev (Trial capacity) |

### Production Recommendations

| Component | Recommendation |
|-----------|----------------|
| Capacity | Premium Capacity (P1 minimum) |
| Redundancy | Multi-region replication |
| Backup | Automated daily backups |
| Monitoring | Application Insights integration |
| Security | Row-level security (RLS) on semantic model |

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Authentication
  ├── Azure Active Directory
  ├── Service Principal (CI/CD)
  └── Multi-Factor Authentication (MFA)

Layer 2: Authorization
  ├── Workspace Roles (Admin, Member, Contributor, Viewer)
  ├── Item-level permissions
  └── Row-level security (RLS) on semantic model

Layer 3: Data Protection
  ├── Encryption at rest (Azure Storage)
  ├── Encryption in transit (TLS 1.2+)
  └── Data masking for sensitive fields

Layer 4: Audit & Compliance
  ├── Activity logs (.onboarding_logs/)
  ├── Access audit trails
  └── Change tracking
```

## 🚀 Deployment Timeline

```
T+0 min:  Start setup script
          └─► Create workspace

T+1 min:  Create storage layer
          ├─► Lakehouse
          └─► Warehouse

T+2 min:  Create processing layer
          ├─► 01_DataIngestion
          ├─► 02_DataTransformation
          └─► 03_DataValidation

T+3 min:  Create analytics layer
          ├─► RicohDataPipeline
          ├─► RicohSemanticModel
          └─► RicohExecutiveDashboard

T+4 min:  Configure users (manual)
          └─► Add 6 users with roles

T+5 min:  Verification complete
          └─► Setup log generated
```

## 📊 Resource Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESOURCE ALLOCATION                          │
└─────────────────────────────────────────────────────────────────┘

Domain:              leit-ricoh-domain
Workspace:           leit-ricoh
Environment:         dev
Capacity Type:       Trial (upgradeable to Premium)

Items by Type:
  • Lakehouse:       1
  • Warehouse:       1
  • Notebook:        3
  • Pipeline:        1
  • Semantic Model:  1
  • Report:          1
  ─────────────────────
  Total:             8

Users by Role:
  • Admin:           1
  • Member:          2
  • Contributor:     1
  • Viewer:          2
  ─────────────────────
  Total:             6

Storage Estimated:
  • Lakehouse:       ~10 GB (initial)
  • Warehouse:       ~5 GB (initial)
  ─────────────────────
  Total:             ~15 GB
```

---

**Architecture Version:** 1.0  
**Last Updated:** October 22, 2025  
**Status:** Ready for Deployment ✅
