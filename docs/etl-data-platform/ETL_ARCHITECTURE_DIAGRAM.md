# Complete ETL Workspace Architecture

**Date:** 21 October 2025  
**Workspace:** ETL Platform [DEV]  
**Domain:** Customer Insights  

---

## 🏗️ Full Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          ETL PLATFORM [DEV] WORKSPACE                                    │
│                              Domain: Customer Insights                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    USERS & ROLES                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  👤 Admin            → Full control, workspace management                                │
│  👤 Data Engineer    → Create/edit items, run pipelines                                  │
│  👤 Data Analyst     → View + limited edit, create reports                               │
│  👤 Stakeholder      → Read-only access to reports                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA FLOW (LEFT TO RIGHT)                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

   SOURCES                 INGESTION              BRONZE LAYER          TRANSFORMATION
   ═══════                ════════════            ════════════          ══════════════

┌──────────────┐      ┌────────────────┐      ┌─────────────────┐    ┌──────────────────┐
│  CSV Files   │      │   Pipeline     │      │  BronzeLakehouse│    │   Notebook       │
│  customers   │──┐   │  "Ingestion"   │─────▶│                 │───▶│ "Transform"      │
│  orders      │  │   │                │      │  /raw/          │    │                  │
│  products    │  │   │  Orchestrates  │      │   customers/    │    │  Clean data      │
└──────────────┘  │   │  data loading  │      │   orders/       │    │  Deduplicate     │
                  │   └────────────────┘      │   products/     │    │  Validate        │
┌──────────────┐  │           ↓               └─────────────────┘    └──────────────────┘
│  JSON APIs   │  │   ┌────────────────┐              │                      │
│  REST        │──┼──▶│   Notebook     │              │                      │
│  endpoints   │  │   │  "Ingestion"   │              │                      ↓
└──────────────┘  │   │                │              │              
                  │   │  Load from:    │              │              SILVER LAYER
┌──────────────┐  │   │  - Storage     │              │              ════════════
│  Databases   │  │   │  - APIs        │              │
│  SQL Server  │──┘   │  - Files       │              │          ┌─────────────────┐
│  PostgreSQL  │      └────────────────┘              │          │ SilverLakehouse │
└──────────────┘                                      │          │                 │
                                                      │          │  /cleaned/      │
                                                      │          │   customers/    │
                                                      └─────────▶│   orders/       │
                                                                 │   products/     │
                                                                 └─────────────────┘
                                                                         │
                                                                         │
                                                                         ↓

   AGGREGATION                GOLD LAYER              ANALYTICS           CONSUMPTION
   ═══════════               ════════════            ══════════          ═══════════

┌──────────────────┐      ┌─────────────────┐    ┌──────────────────┐  ┌─────────────┐
│   Notebook       │      │  GoldLakehouse  │    │  Analytics       │  │  Power BI   │
│ "Aggregation"    │─────▶│                 │───▶│  Warehouse       │─▶│  Reports    │
│                  │      │  /aggregated/   │    │                  │  │             │
│  Create:         │      │   customer_seg/ │    │  Tables:         │  │  Dashboards │
│  - RFM segments  │      │   sales_sum/    │    │  CustomerSeg     │  │  KPIs       │
│  - Sales summary │      │   product_met/  │    │  SalesSummary    │  └─────────────┘
│  - Product KPIs  │      └─────────────────┘    │  ProductMetrics  │
└──────────────────┘                             └──────────────────┘  ┌─────────────┐
        ↑                                                │              │  Excel      │
        │                                                │              │  Exports    │
        │                                                └─────────────▶│  via API    │
        │                                                               └─────────────┘
┌──────────────────┐
│   Pipeline       │                                                   ┌─────────────┐
│ "Transformation" │                                                   │  Notebooks  │
│                  │                                                   │  Analysis   │
│  Orchestrates    │                                                   │  Ad-hoc     │
│  transformation  │                                                   └─────────────┘
└──────────────────┘

```

---

## 📦 Item Inventory

### **Storage Items (4 total)**

```
┌─────────────────────┐
│   BronzeLakehouse   │  → Raw data storage (Delta format)
├─────────────────────┤     Tables: bronze_customers, bronze_orders, bronze_products
│   Type: Lakehouse   │     Size: ~10GB (typical)
│   Layer: Bronze     │     Retention: 90 days
└─────────────────────┘

┌─────────────────────┐
│   SilverLakehouse   │  → Cleaned, validated data
├─────────────────────┤     Tables: silver_customers, silver_orders, silver_products
│   Type: Lakehouse   │     Size: ~8GB (after cleaning)
│   Layer: Silver     │     Retention: 365 days
└─────────────────────┘

┌─────────────────────┐
│   GoldLakehouse     │  → Business-ready aggregations
├─────────────────────┤     Tables: customer_segments, sales_summary, product_metrics
│   Type: Lakehouse   │     Size: ~2GB (aggregated)
│   Layer: Gold       │     Retention: Indefinite
└─────────────────────┘

┌─────────────────────┐
│ AnalyticsWarehouse  │  → SQL query engine for BI
├─────────────────────┤     Tables: CustomerSegments, SalesSummary, ProductMetrics
│   Type: Warehouse   │     Optimized for: Power BI, SQL queries
│   Query Engine: SQL │     Connections: DirectQuery + Import
└─────────────────────┘
```

### **Processing Items (3 Notebooks + 2 Pipelines = 5 total)**

```
┌──────────────────────────┐
│  01_DataIngestion.ipynb  │  → Load data from sources to Bronze
├──────────────────────────┤     Runtime: ~5 minutes
│  Type: Notebook          │     Frequency: Daily at 2:00 AM
│  Language: PySpark       │     Dependencies: None
└──────────────────────────┘

┌──────────────────────────┐
│ 02_DataTransformation    │  → Clean Bronze → Silver
├──────────────────────────┤     Runtime: ~10 minutes
│  Type: Notebook          │     Frequency: Daily at 2:10 AM
│  Language: PySpark       │     Dependencies: 01_DataIngestion
└──────────────────────────┘

┌──────────────────────────┐
│ 03_DataAggregation       │  → Aggregate Silver → Gold
├──────────────────────────┤     Runtime: ~8 minutes
│  Type: Notebook          │     Frequency: Daily at 2:25 AM
│  Language: PySpark       │     Dependencies: 02_DataTransformation
└──────────────────────────┘

┌──────────────────────────┐
│ Pipeline_DataIngestion   │  → Orchestrate ingestion
├──────────────────────────┤     Activities: Run notebook, validate, log
│  Type: Data Pipeline     │     Schedule: Daily 2:00 AM
│  Trigger: Scheduled      │     Notifications: On failure
└──────────────────────────┘

┌──────────────────────────┐
│ Pipeline_Transformation  │  → Orchestrate full ETL
├──────────────────────────┤     Activities: Transform → Aggregate → Load
│  Type: Data Pipeline     │     Schedule: Daily 2:10 AM
│  Trigger: After Pipeline │     Notifications: On success/failure
└──────────────────────────┘
```

---

## 🔄 Data Flow Timeline

```
TIME          ACTIVITY                                STATUS
═════════     ═══════════════════════════════════    ═══════

02:00 AM      Pipeline_DataIngestion starts          Running
              ├─ Execute 01_DataIngestion            Running
              ├─ Load customers.csv → Bronze         ✓ Complete
              ├─ Load orders.json → Bronze           ✓ Complete
              └─ Load products.parquet → Bronze      ✓ Complete
02:05 AM      Pipeline_DataIngestion complete        ✓ Success

02:10 AM      Pipeline_Transformation starts         Running
              ├─ Execute 02_DataTransformation       Running
              │  ├─ Read Bronze customers            ✓ Complete
              │  ├─ Clean & validate                 ✓ Complete
              │  └─ Write to Silver                  ✓ Complete
02:15 AM      Transformation phase complete          ✓ Success

02:15 AM      ├─ Execute 03_DataAggregation          Running
              │  ├─ Read Silver data                 ✓ Complete
              │  ├─ Calculate RFM segments           ✓ Complete
              │  ├─ Create sales summary             ✓ Complete
              │  └─ Write to Gold                    ✓ Complete
02:20 AM      Aggregation phase complete             ✓ Success

02:20 AM      ├─ Load to AnalyticsWarehouse          Running
              │  └─ Sync Gold → Warehouse            ✓ Complete
02:23 AM      Pipeline_Transformation complete       ✓ Success

02:25 AM      All ETL processes complete             ✓ Success
              Data ready for business consumption
```

---

## 👥 User Access Matrix

```
┌─────────────────────┬──────────┬───────────┬─────────────┬─────────┐
│      User Role      │  Create  │   Edit    │    View     │ Delete  │
├─────────────────────┼──────────┼───────────┼─────────────┼─────────┤
│  Admin              │    ✓     │     ✓     │      ✓      │    ✓    │
│  (Full control)     │  All     │   All     │    All      │   All   │
├─────────────────────┼──────────┼───────────┼─────────────┼─────────┤
│  Member             │    ✓     │     ✓     │      ✓      │    ✓    │
│  (Data Engineer)    │  Items   │   Items   │    All      │  Items  │
├─────────────────────┼──────────┼───────────┼─────────────┼─────────┤
│  Contributor        │    ✓     │     ✓     │      ✓      │    ✗    │
│  (Data Analyst)     │  Reports │  Reports  │    All      │   No    │
├─────────────────────┼──────────┼───────────┼─────────────┼─────────┤
│  Viewer             │    ✗     │     ✗     │      ✓      │    ✗    │
│  (Stakeholder)      │   No     │    No     │   Read      │   No    │
└─────────────────────┴──────────┴───────────┴─────────────┴─────────┘
```

---

## 📊 Resource Utilization

```
ITEM TYPE          COUNT    STORAGE      COMPUTE       COST/DAY
═════════════     ══════   ═════════    ═══════════   ═════════

Lakehouses           3      ~20 GB      Low (Delta)   $2.50
Warehouse            1      ~2 GB       Med (SQL)     $5.00
Notebooks            3      ~100 MB     High (Spark)  $8.00
Pipelines            2      ~10 MB      Low (Orch)    $1.50

Total Resources      9      ~22 GB      Medium        $17.00/day
                                                      ≈ $510/month
```

---

## 🎯 Setup Checklist

```
PHASE                        STATUS        COMMAND
═════════════════════════   ═══════       ═══════════════════════════════

□ Create workspace           Pending       onboard_data_product.py
□ Add users                  Pending       manage_workspaces.py add-user
□ Create BronzeLakehouse     Pending       manage_fabric_items.py create
□ Create SilverLakehouse     Pending       manage_fabric_items.py create
□ Create GoldLakehouse       Pending       manage_fabric_items.py create
□ Create AnalyticsWarehouse  Pending       manage_fabric_items.py create
□ Create Notebooks (3)       Pending       manage_fabric_items.py create
□ Create Pipelines (2)       Pending       manage_fabric_items.py create
□ Test ingestion             Pending       Run 01_DataIngestion
□ Test transformation        Pending       Run 02_DataTransformation
□ Test aggregation           Pending       Run 03_DataAggregation
□ Verify warehouse data      Pending       Query AnalyticsWarehouse
□ Schedule pipelines         Pending       Configure triggers
□ Create Power BI report     Pending       Connect to warehouse

Quick Setup: Run ./setup_etl_workspace.sh to complete all phases
```

---

## 🚀 Quick Start Commands

```bash
# 1. ONE-COMMAND SETUP (Automated)
./setup_etl_workspace.sh

# 2. VERIFY SETUP
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "ETL Platform [DEV]"

# 3. ADD USERS
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "user@company.com" \
  --role Member

# 4. RUN ETL
python3 ops/scripts/manage_fabric_items.py run \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline

# 5. CHECK STATUS
python3 ops/scripts/manage_fabric_items.py get-status \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline
```

---

*Generated: 21 October 2025*  
*Architecture: Medallion (Bronze → Silver → Gold)*  
*Status: Ready for deployment* 🚀

