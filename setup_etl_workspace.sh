#!/bin/bash
# Complete ETL Workspace Setup Script
# Purpose: Create full end-to-end ETL environment with workspaces, users, and items
# Date: 21 October 2025

set -e  # Exit on error

WORKSPACE_NAME="ETL Platform [DEV]"
DOMAIN="Customer Insights"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Complete ETL Workspace Setup Script                   ║"
echo "║         Creating: ${WORKSPACE_NAME}                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# ============================================================================
# PHASE 1: CREATE WORKSPACES
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 1: Creating Workspaces"
echo "═══════════════════════════════════════════════════════════════"

python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml

echo ""
echo "✅ Workspaces created"
echo ""

# ============================================================================
# PHASE 2: ADD USERS
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 2: Adding Users"
echo "═══════════════════════════════════════════════════════════════"

# Note: Replace these with your actual user emails
# Uncomment and update when ready

# echo "Adding Admin user..."
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "${WORKSPACE_NAME}" \
#   --email "data-admin@company.com" \
#   --role Admin

# echo "Adding Data Engineer..."
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "${WORKSPACE_NAME}" \
#   --email "data-engineer@company.com" \
#   --role Member

# echo "Adding Data Analyst..."
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "${WORKSPACE_NAME}" \
#   --email "data-analyst@company.com" \
#   --role Contributor

# echo "Adding Stakeholder..."
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "${WORKSPACE_NAME}" \
#   --email "stakeholder@company.com" \
#   --role Viewer

echo "⚠️  User addition commented out - update emails and uncomment"
echo ""

# ============================================================================
# PHASE 3: CREATE LAKEHOUSES (MEDALLION ARCHITECTURE)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 3: Creating Lakehouses (Bronze, Silver, Gold)"
echo "═══════════════════════════════════════════════════════════════"

echo "Creating Bronze Lakehouse (Raw Data Layer)..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "BronzeLakehouse" \
  --type Lakehouse \
  --description "Raw data ingestion layer - unprocessed source data"

echo "Creating Silver Lakehouse (Cleaned Data Layer)..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "SilverLakehouse" \
  --type Lakehouse \
  --description "Cleaned and validated data layer"

echo "Creating Gold Lakehouse (Business Ready Layer)..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "GoldLakehouse" \
  --type Lakehouse \
  --description "Business-ready aggregated data for analytics"

echo ""
echo "✅ Lakehouses created"
echo ""

# ============================================================================
# PHASE 4: CREATE WAREHOUSE
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 4: Creating Analytics Warehouse"
echo "═══════════════════════════════════════════════════════════════"

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "AnalyticsWarehouse" \
  --type Warehouse \
  --description "SQL analytics warehouse for reporting and dashboards"

echo ""
echo "✅ Warehouse created"
echo ""

# ============================================================================
# PHASE 5: CREATE NOTEBOOKS
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 5: Creating Notebooks"
echo "═══════════════════════════════════════════════════════════════"

echo "Creating Data Ingestion Notebook..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "01_DataIngestion" \
  --type Notebook \
  --description "Ingest data from CSV, JSON, and API sources into Bronze layer"

echo "Creating Data Transformation Notebook..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "02_DataTransformation" \
  --type Notebook \
  --description "Transform and clean Bronze data into Silver layer"

echo "Creating Data Aggregation Notebook..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "03_DataAggregation" \
  --type Notebook \
  --description "Aggregate Silver data into Gold layer business metrics"

echo ""
echo "✅ Notebooks created"
echo ""

# ============================================================================
# PHASE 6: CREATE PIPELINES
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 6: Creating Data Pipelines"
echo "═══════════════════════════════════════════════════════════════"

echo "Creating Data Ingestion Pipeline..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "Pipeline_DataIngestion" \
  --type DataPipeline \
  --description "Orchestrate data ingestion from sources to Bronze layer"

echo "Creating Transformation Pipeline..."
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "${WORKSPACE_NAME}" \
  --name "Pipeline_Transformation" \
  --type DataPipeline \
  --description "Orchestrate data transformation from Bronze to Silver to Gold"

echo ""
echo "✅ Pipelines created"
echo ""

# ============================================================================
# PHASE 7: VERIFY SETUP
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 7: Verifying Setup"
echo "═══════════════════════════════════════════════════════════════"

echo "Listing all items in workspace..."
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "${WORKSPACE_NAME}"

echo ""

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    SETUP COMPLETE! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Created workspace: ${WORKSPACE_NAME}"
echo "✅ Created 3 Lakehouses (Bronze, Silver, Gold)"
echo "✅ Created 1 Warehouse (AnalyticsWarehouse)"
echo "✅ Created 3 Notebooks (Ingestion, Transformation, Aggregation)"
echo "✅ Created 2 Pipelines (Ingestion, Transformation)"
echo ""
echo "📊 Total: 9 Fabric items ready for ETL processing"
echo ""
echo "🔗 Next Steps:"
echo "   1. Open Fabric portal: https://app.fabric.microsoft.com"
echo "   2. Navigate to workspace: ${WORKSPACE_NAME}"
echo "   3. Open notebooks and add your ETL logic"
echo "   4. Run pipelines to test end-to-end flow"
echo "   5. Review COMPLETE_ETL_SETUP_GUIDE.md for detailed examples"
echo ""
echo "📚 Related Documentation:"
echo "   - COMPLETE_ETL_SETUP_GUIDE.md (Full setup guide)"
echo "   - ENVIRONMENT_PROMOTION_GUIDE.md (Deploy to TEST/PROD)"
echo "   - FABRIC_ITEMS_AND_USERS_GUIDE.md (Managing items and users)"
echo ""
