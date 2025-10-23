# Complete ETL Workspace Setup Guide

**Date:** 21 October 2025  
**Purpose:** Create full end-to-end ETL environment in existing domain  
**Target:** Production-ready workspaces with users, items, and complete ETL pipeline  

---

## 📋 Table of Contents

1. [Overview: What We'll Build](#1-overview-what-well-build)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Create Workspace in Existing Domain](#3-step-1-create-workspace-in-existing-domain)
4. [Step 2: Add Users and Assign Roles](#4-step-2-add-users-and-assign-roles)
5. [Step 3: Create ETL Infrastructure](#5-step-3-create-etl-infrastructure)
6. [Step 4: Build Complete ETL Pipeline](#6-step-4-build-complete-etl-pipeline)
7. [Step 5: Test End-to-End Flow](#7-step-5-test-end-to-end-flow)
8. [Quick Commands Reference](#8-quick-commands-reference)

---

## 1. Overview: What We'll Build

### **ETL Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE ETL ENVIRONMENT                      │
└─────────────────────────────────────────────────────────────────┘

Data Sources              Ingestion              Transformation           Serving
═══════════              ═══════════            ═══════════════          ═══════════

CSV Files                                        Bronze Layer            
JSON Files        →    Pipeline (1)      →      Lakehouse       →      
REST APIs              "Data Ingestion"         "Raw Data"             
                                                      ↓                  
                                                      │                  
Database                                         Silver Layer           
Tables           →    Pipeline (2)      →       Lakehouse       →      Warehouse
                      "Data Transform"          "Cleaned Data"         "Analytics"
                                                      ↓                       ↓
                                                      │                       │
                                                 Gold Layer                Reports
                                          →      Lakehouse       →      Dashboards
                                                "Aggregated"            Notebooks
```

### **What We'll Create:**

1. ✅ **1 Workspace** in existing domain (e.g., "Customer Insights")
2. ✅ **3 Lakehouses** (Bronze, Silver, Gold layers)
3. ✅ **1 Warehouse** (Analytics database)
4. ✅ **2 Data Pipelines** (Ingestion + Transformation)
5. ✅ **2 Notebooks** (Data processing + Analysis)
6. ✅ **1 Semantic Model** (Power BI dataset)
7. ✅ **4 Users** with appropriate roles (Admin, Member, Contributor, Viewer)

---

## 2. Prerequisites

### **Check Your Environment:**

```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd

# Verify .env file exists and has credentials
cat .env | grep -E "AZURE_CLIENT_ID|AZURE_TENANT_ID|FABRIC_WORKSPACE_ID"

# Activate Conda environment
conda activate fabric-cicd

# Verify Python version
python3 --version  # Should be 3.11.14
```

### **Available Domains (From Your Codebase):**

Based on your existing YAML files:
- 📁 **Customer Insights** (used by Customer Analytics)
- 📁 **Sales Insights** (used by Sales Analytics)

We'll use **"Customer Insights"** for this example, but you can choose any existing domain.

---

## 3. Step 1: Create Workspace in Existing Domain

### **Option A: Using YAML Descriptor (Recommended)**

Create a new product descriptor for your ETL workspace:

**File:** `data_products/onboarding/etl_platform.yaml`

```yaml
product:
  name: "ETL Platform"
  owner_email: "data-engineering@company.com"
  domain: "Customer Insights"  # ← Existing domain
  description: "Complete end-to-end ETL infrastructure for customer data processing"

environments:
  dev:
    enabled: true
    capacity_type: "trial"
    description: "Development environment for ETL pipeline testing"
  
  test:
    enabled: true
    capacity_type: "trial"
    description: "QA environment for ETL validation"
  
  prod:
    enabled: true
    capacity_type: "capacity"
    capacity_id: "${FABRIC_CAPACITY_PROD_ID}"
    description: "Production ETL environment"

git:
  organization: "${GITHUB_ORG}"
  repository: "${GITHUB_REPO}"
  feature_prefix: "feature"
  directory: "data_products/etl_platform"

automation:
  audit_reference: "ETL-SETUP-001"
  create_default_items: true  # Auto-create basic lakehouse structure
```

**Run onboarding:**

```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml
```

**Expected Output:**

```
ℹ️ Loaded 53 environment variables from .env
ℹ️ Starting onboarding for product 'ETL Platform'
✅ Seeded scaffold for etl_platform
ℹ️ Creating Fabric workspace: ETL Platform [DEV]
✅ Created workspace 'ETL Platform [DEV]'
   ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Domain: Customer Insights
ℹ️ Creating Fabric workspace: ETL Platform [TEST]
✅ Created workspace 'ETL Platform [TEST]'
   ID: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
   Domain: Customer Insights
ℹ️ Creating Fabric workspace: ETL Platform [PROD]
✅ Created workspace 'ETL Platform [PROD]'
   ID: zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz
   Domain: Customer Insights
✅ Onboarding workflow complete
```

### **Option B: Direct Workspace Creation**

If you want more control:

```bash
# Create workspace directly
python3 ops/scripts/manage_workspaces.py -e dev create \
  --name "ETL Platform [DEV]" \
  --description "Development environment for ETL pipeline" \
  --capacity-type trial

# Note: -e/--environment flag goes before the subcommand (create/delete/etc)
# Domain is derived from workspace name pattern
```

---

## 4. Step 2: Add Users and Assign Roles

### **User Role Strategy:**

| User | Role | Permissions | Use Case |
|------|------|-------------|----------|
| **data-admin@company.com** | Admin | Full control, manage users | Team lead, workspace owner |
| **data-engineer@company.com** | Member | Create/edit items, run pipelines | ETL developers |
| **data-analyst@company.com** | Contributor | View + limited edit | Analysts, report builders |
| **stakeholder@company.com** | Viewer | Read-only access | Business stakeholders |

### **Add Users:**

```bash
# 1. Add Admin (Workspace Owner)
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "data-admin@company.com" \
  --role Admin

# 2. Add Data Engineer (Full Development Access)
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "data-engineer@company.com" \
  --role Member

# 3. Add Data Analyst (Contributor)
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "data-analyst@company.com" \
  --role Contributor

# 4. Add Stakeholder (Read-Only)
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "stakeholder@company.com" \
  --role Viewer
```

### **Verify Users:**

```bash
python3 ops/scripts/manage_workspaces.py list-users \
  --workspace "ETL Platform [DEV]"
```

**Expected Output:**

```
Users in workspace 'ETL Platform [DEV]':

Email                          Role          Status
─────────────────────────────────────────────────────
data-admin@company.com         Admin         Active
data-engineer@company.com      Member        Active
data-analyst@company.com       Contributor   Active
stakeholder@company.com        Viewer        Active
```

---

## 5. Step 3: Create ETL Infrastructure

### **Architecture: Medallion Design (Bronze → Silver → Gold)**

```
┌─────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────┘

Bronze Lakehouse                Silver Lakehouse              Gold Lakehouse
(Raw Ingestion)                 (Cleaned Data)                (Business Ready)
═══════════════                 ══════════════                ════════════════

/raw/                           /cleaned/                     /aggregated/
  customers.csv          →        customers_clean/      →       customer_segments/
  orders.json                     orders_clean/                 sales_summary/
  products.parquet                products_clean/               product_metrics/

Schema: Raw                     Schema: Validated             Schema: Optimized
Quality: None                   Quality: Basic rules          Quality: Production
Format: Mixed                   Format: Delta                 Format: Delta
```

### **3.1: Create Bronze Lakehouse (Raw Data)**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "BronzeLakehouse" \
  --type Lakehouse \
  --description "Raw data ingestion layer - unprocessed source data"
```

### **3.2: Create Silver Lakehouse (Cleaned Data)**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "SilverLakehouse" \
  --type Lakehouse \
  --description "Cleaned and validated data layer"
```

### **3.3: Create Gold Lakehouse (Business Ready)**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "GoldLakehouse" \
  --type Lakehouse \
  --description "Business-ready aggregated data for analytics"
```

### **3.4: Create Analytics Warehouse**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "AnalyticsWarehouse" \
  --type Warehouse \
  --description "SQL analytics warehouse for reporting and dashboards"
```

### **Verify Infrastructure:**

```bash
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "ETL Platform [DEV]"
```

**Expected Output:**

```
Items in workspace 'ETL Platform [DEV]':

Name                    Type         Description
────────────────────────────────────────────────────────────────
BronzeLakehouse         Lakehouse    Raw data ingestion layer
SilverLakehouse         Lakehouse    Cleaned and validated data layer
GoldLakehouse           Lakehouse    Business-ready aggregated data
AnalyticsWarehouse      Warehouse    SQL analytics warehouse

Total: 4 items
```

---

## 6. Step 4: Build Complete ETL Pipeline

### **6.1: Create Data Ingestion Notebook**

**Purpose:** Load raw data from sources into Bronze Lakehouse

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "01_DataIngestion" \
  --type Notebook \
  --description "Ingest data from CSV, JSON, and API sources into Bronze layer"
```

**Sample Notebook Code** (add this in Fabric portal or via API):

```python
# Fabric Notebook: 01_DataIngestion.ipynb

# Cell 1: Setup
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime

spark = SparkSession.builder.appName("DataIngestion").getOrCreate()

# Cell 2: Ingest Customer Data from CSV
customers_df = spark.read.csv(
    "abfss://source-data@storage.dfs.core.windows.net/customers.csv",
    header=True,
    inferSchema=True
)

# Write to Bronze Lakehouse
customers_df.write.mode("overwrite").format("delta").save(
    "Tables/bronze_customers"
)

print(f"✅ Ingested {customers_df.count()} customer records")

# Cell 3: Ingest Orders from JSON
orders_df = spark.read.json(
    "abfss://source-data@storage.dfs.core.windows.net/orders.json"
)

orders_df.write.mode("overwrite").format("delta").save(
    "Tables/bronze_orders"
)

print(f"✅ Ingested {orders_df.count()} order records")

# Cell 4: Ingest Products from Parquet
products_df = spark.read.parquet(
    "abfss://source-data@storage.dfs.core.windows.net/products.parquet"
)

products_df.write.mode("overwrite").format("delta").save(
    "Tables/bronze_products"
)

print(f"✅ Ingested {products_df.count()} product records")

# Cell 5: Log Ingestion Metadata
metadata_df = spark.createDataFrame([{
    "table": "bronze_customers",
    "record_count": customers_df.count(),
    "ingested_at": datetime.now().isoformat()
}])

metadata_df.write.mode("append").format("delta").save(
    "Tables/ingestion_metadata"
)

print("✅ Data ingestion complete")
```

### **6.2: Create Data Transformation Notebook**

**Purpose:** Clean and transform Bronze → Silver

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "02_DataTransformation" \
  --type Notebook \
  --description "Transform and clean Bronze data into Silver layer"
```

**Sample Notebook Code:**

```python
# Fabric Notebook: 02_DataTransformation.ipynb

# Cell 1: Setup
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName("DataTransformation").getOrCreate()

# Cell 2: Read Bronze Customers
bronze_customers = spark.read.format("delta").load(
    "Tables/bronze_customers"
)

# Cell 3: Clean and Transform Customers
silver_customers = bronze_customers \
    .dropDuplicates(["customer_id"]) \
    .filter(col("email").isNotNull()) \
    .withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name"))) \
    .withColumn("age_group", 
        when(col("age") < 25, "Young")
        .when(col("age") < 45, "Middle-Aged")
        .otherwise("Senior")
    ) \
    .withColumn("processed_at", current_timestamp())

# Cell 4: Write to Silver Lakehouse
silver_customers.write.mode("overwrite").format("delta").save(
    "Tables/silver_customers"
)

print(f"✅ Transformed {silver_customers.count()} customer records")

# Cell 5: Data Quality Checks
null_emails = bronze_customers.filter(col("email").isNull()).count()
duplicates = bronze_customers.count() - bronze_customers.dropDuplicates(["customer_id"]).count()

print(f"ℹ️ Quality Report:")
print(f"   - Null emails removed: {null_emails}")
print(f"   - Duplicates removed: {duplicates}")

# Cell 6: Read and Transform Orders
bronze_orders = spark.read.format("delta").load("Tables/bronze_orders")

silver_orders = bronze_orders \
    .filter(col("order_total") > 0) \
    .withColumn("order_date", to_date(col("order_timestamp"))) \
    .withColumn("processed_at", current_timestamp())

silver_orders.write.mode("overwrite").format("delta").save(
    "Tables/silver_orders"
)

print(f"✅ Transformed {silver_orders.count()} order records")
```

### **6.3: Create Aggregation Notebook**

**Purpose:** Create business metrics (Silver → Gold)

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "03_DataAggregation" \
  --type Notebook \
  --description "Aggregate Silver data into Gold layer business metrics"
```

**Sample Notebook Code:**

```python
# Fabric Notebook: 03_DataAggregation.ipynb

# Cell 1: Read Silver Data
silver_customers = spark.read.format("delta").load("Tables/silver_customers")
silver_orders = spark.read.format("delta").load("Tables/silver_orders")

# Cell 2: Customer Segmentation (RFM Analysis)
from pyspark.sql.window import Window

customer_metrics = silver_orders.groupBy("customer_id").agg(
    max("order_date").alias("last_order_date"),
    count("order_id").alias("order_frequency"),
    sum("order_total").alias("total_spent")
)

# Calculate RFM scores
customer_segments = customer_metrics \
    .withColumn("recency_days", datediff(current_date(), col("last_order_date"))) \
    .withColumn("rfm_segment",
        when((col("recency_days") < 30) & (col("order_frequency") > 10), "Champions")
        .when((col("recency_days") < 90) & (col("order_frequency") > 5), "Loyal")
        .when(col("recency_days") < 180, "Potential")
        .otherwise("At Risk")
    )

# Cell 3: Write to Gold Lakehouse
customer_segments.write.mode("overwrite").format("delta").save(
    "Tables/gold_customer_segments"
)

print(f"✅ Created {customer_segments.count()} customer segments")

# Cell 4: Sales Summary
sales_summary = silver_orders.groupBy("order_date").agg(
    count("order_id").alias("total_orders"),
    sum("order_total").alias("total_revenue"),
    avg("order_total").alias("avg_order_value")
)

sales_summary.write.mode("overwrite").format("delta").save(
    "Tables/gold_sales_summary"
)

print(f"✅ Created sales summary with {sales_summary.count()} days")

# Cell 5: Write to Analytics Warehouse
customer_segments.write \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://AnalyticsWarehouse") \
    .option("dbtable", "CustomerSegments") \
    .mode("overwrite") \
    .save()

print("✅ Data loaded to Analytics Warehouse")
```

### **6.4: Create Data Ingestion Pipeline**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "Pipeline_DataIngestion" \
  --type DataPipeline \
  --description "Orchestrate data ingestion from sources to Bronze layer"
```

**Pipeline Definition** (simplified JSON structure):

```json
{
  "name": "Pipeline_DataIngestion",
  "activities": [
    {
      "name": "RunIngestionNotebook",
      "type": "ExecuteNotebook",
      "notebook": "01_DataIngestion"
    },
    {
      "name": "ValidateIngestion",
      "type": "Script",
      "dependsOn": ["RunIngestionNotebook"]
    }
  ],
  "schedule": {
    "frequency": "Daily",
    "time": "02:00"
  }
}
```

### **6.5: Create Transformation Pipeline**

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "Pipeline_Transformation" \
  --type DataPipeline \
  --description "Orchestrate data transformation from Bronze to Silver to Gold"
```

---

## 7. Step 5: Test End-to-End Flow

### **7.1: Verify All Items Created**

```bash
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "ETL Platform [DEV]"
```

**Expected Output:**

```
Items in workspace 'ETL Platform [DEV]':

Name                        Type           Description
─────────────────────────────────────────────────────────────────────
BronzeLakehouse             Lakehouse      Raw data ingestion layer
SilverLakehouse             Lakehouse      Cleaned and validated data
GoldLakehouse               Lakehouse      Business-ready aggregated data
AnalyticsWarehouse          Warehouse      SQL analytics warehouse
01_DataIngestion            Notebook       Ingest from sources to Bronze
02_DataTransformation       Notebook       Transform Bronze to Silver
03_DataAggregation          Notebook       Aggregate Silver to Gold
Pipeline_DataIngestion      DataPipeline   Orchestrate ingestion
Pipeline_Transformation     DataPipeline   Orchestrate transformation

Total: 9 items
```

### **7.2: Manual Test (In Fabric Portal)**

1. **Open Fabric Portal:** https://app.fabric.microsoft.com
2. **Navigate to:** ETL Platform [DEV] workspace
3. **Run Ingestion Notebook:**
   - Open `01_DataIngestion`
   - Click "Run All"
   - Verify data appears in BronzeLakehouse
4. **Run Transformation Notebook:**
   - Open `02_DataTransformation`
   - Click "Run All"
   - Verify data appears in SilverLakehouse
5. **Run Aggregation Notebook:**
   - Open `03_DataAggregation`
   - Click "Run All"
   - Verify data appears in GoldLakehouse

### **7.3: Automated Test (Via API)**

```bash
# Run ingestion pipeline
python3 ops/scripts/manage_fabric_items.py run \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline

# Check pipeline status
python3 ops/scripts/manage_fabric_items.py get-status \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline
```

### **7.4: Query Gold Data**

```bash
# Query Analytics Warehouse
python3 ops/scripts/manage_fabric_items.py query \
  --workspace "ETL Platform [DEV]" \
  --item-name "AnalyticsWarehouse" \
  --type Warehouse \
  --sql "SELECT rfm_segment, COUNT(*) as customer_count FROM CustomerSegments GROUP BY rfm_segment"
```

**Expected Output:**

```
Query Results:

rfm_segment     customer_count
────────────────────────────────
Champions       1234
Loyal           5678
Potential       2345
At Risk         890

✅ Query executed successfully
```

---

## 8. Quick Commands Reference

### **Setup Workspace:**

```bash
# Create workspace with YAML
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml
```

### **Add Users:**

```bash
# Add Admin
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "user@company.com" \
  --role Admin

# List users
python3 ops/scripts/manage_workspaces.py list-users \
  --workspace "ETL Platform [DEV]"
```

### **Create Items:**

```bash
# Create Lakehouse
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "BronzeLakehouse" \
  --type Lakehouse

# Create Notebook
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "01_DataIngestion" \
  --type Notebook

# Create Pipeline
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "Pipeline_DataIngestion" \
  --type DataPipeline

# List all items
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "ETL Platform [DEV]"
```

### **Run ETL:**

```bash
# Run pipeline
python3 ops/scripts/manage_fabric_items.py run \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline

# Check status
python3 ops/scripts/manage_fabric_items.py get-status \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline
```

---

## 🎯 Summary

### **What You've Built:**

✅ **1 Workspace** in existing "Customer Insights" domain  
✅ **4 Users** with role-based access (Admin, Member, Contributor, Viewer)  
✅ **3 Lakehouses** (Bronze, Silver, Gold medallion architecture)  
✅ **1 Warehouse** (Analytics database for SQL queries)  
✅ **3 Notebooks** (Ingestion, Transformation, Aggregation)  
✅ **2 Pipelines** (Orchestration for automation)  

### **Complete ETL Flow:**

```
Source Data → [Pipeline] → Bronze Lakehouse → [Notebook] → 
Silver Lakehouse → [Notebook] → Gold Lakehouse → 
Analytics Warehouse → Reports/Dashboards
```

### **Next Steps:**

1. 📊 **Create Power BI Reports** connected to AnalyticsWarehouse
2. 🔄 **Schedule Pipelines** for daily/hourly runs
3. 📈 **Add Monitoring** with Great Expectations for data quality
4. 🔐 **Setup Row-Level Security** in Analytics Warehouse
5. 🚀 **Promote to TEST** using deployment pipeline
6. 🌍 **Deploy to PROD** after validation

---

*Generated: 21 October 2025*  
*Status: Production-Ready*  
*Related: ENVIRONMENT_PROMOTION_GUIDE.md, FABRIC_ITEMS_AND_USERS_GUIDE.md* 📚

