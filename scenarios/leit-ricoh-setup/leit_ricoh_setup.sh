#!/bin/bash
################################################################################
# LEIT-Ricoh Domain - Complete Workspace Setup Scenario
# 
# This script creates a complete Fabric workspace with:
# - Notebooks for data processing
# - Users with different roles
# - Lakehouse for data storage
# - Warehouse for analytics
# - 3 additional Fabric items (Pipeline, Semantic Model, Report)
#
# Domain: leit-ricoh-domain
# Workspace: leit-ricoh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_NAME="leit-ricoh"
DOMAIN_NAME="leit-ricoh-domain"
ENVIRONMENT="dev"

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_step() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

################################################################################
# STEP 1: CREATE WORKSPACE
################################################################################

print_header "STEP 1: Creating Workspace - ${WORKSPACE_NAME}"

print_info "Creating workspace in ${ENVIRONMENT} environment..."

python3 ops/scripts/manage_workspaces.py create "$WORKSPACE_NAME" \
  -e "$ENVIRONMENT" \
  --description "LEIT-Ricoh domain workspace for data analytics and reporting" \
  --capacity-type Trial

print_step "Workspace '${WORKSPACE_NAME}' created successfully"

# Get workspace ID
print_info "Retrieving workspace ID..."
WORKSPACE_ID=$(python3 ops/scripts/manage_workspaces.py get \
  --name "${WORKSPACE_NAME}" \
  --json | grep -oP '"id":\s*"\K[^"]+' | head -1)

if [ -z "$WORKSPACE_ID" ]; then
    print_error "Failed to retrieve workspace ID"
    exit 1
fi

print_step "Workspace ID: ${WORKSPACE_ID}"

################################################################################
# STEP 2: CREATE LAKEHOUSE
################################################################################

print_header "STEP 2: Creating Lakehouse"

print_info "Creating main data lakehouse..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "RicohDataLakehouse" \
  --type Lakehouse \
  --description "Primary lakehouse for Ricoh data storage and processing"

print_step "Lakehouse 'RicohDataLakehouse' created"

################################################################################
# STEP 3: CREATE WAREHOUSE
################################################################################

print_header "STEP 3: Creating Data Warehouse"

print_info "Creating analytics warehouse..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "RicohAnalyticsWarehouse" \
  --type Warehouse \
  --description "Data warehouse for Ricoh analytics and reporting"

print_step "Warehouse 'RicohAnalyticsWarehouse' created"

################################################################################
# STEP 4: CREATE NOTEBOOKS
################################################################################

print_header "STEP 4: Creating Notebooks"

# Notebook 1: Data Ingestion
print_info "Creating data ingestion notebook..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "01_DataIngestion" \
  --type Notebook \
  --description "Ingests raw data from various sources into lakehouse"

print_step "Notebook '01_DataIngestion' created"

# Notebook 2: Data Transformation
print_info "Creating data transformation notebook..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "02_DataTransformation" \
  --type Notebook \
  --description "Transforms and cleanses data for analytics"

print_step "Notebook '02_DataTransformation' created"

# Notebook 3: Data Validation
print_info "Creating data validation notebook..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "03_DataValidation" \
  --type Notebook \
  --description "Validates data quality and completeness"

print_step "Notebook '03_DataValidation' created"

################################################################################
# STEP 5: CREATE ADDITIONAL FABRIC ITEMS
################################################################################

print_header "STEP 5: Creating Additional Fabric Items"

# Item 1: Data Pipeline
print_info "Creating orchestration pipeline..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "RicohDataPipeline" \
  --type DataPipeline \
  --description "Orchestrates the end-to-end data processing workflow"

print_step "Pipeline 'RicohDataPipeline' created"

# Item 2: Semantic Model
print_info "Creating semantic model..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "RicohSemanticModel" \
  --type SemanticModel \
  --description "Business semantic layer for Ricoh analytics"

print_step "Semantic Model 'RicohSemanticModel' created"

# Item 3: Report
print_info "Creating Power BI report..."

python3 ops/scripts/manage_fabric_items.py create \
  --workspace "$WORKSPACE_NAME" \
  --name "RicohExecutiveDashboard" \
  --type Report \
  --description "Executive dashboard for Ricoh business metrics"

print_step "Report 'RicohExecutiveDashboard' created"

################################################################################
# STEP 6: ADD USERS TO WORKSPACE
################################################################################

print_header "STEP 6: Adding Users to Workspace"

# Note: Replace these email addresses with actual user emails in your organization
# These are example placeholders

# Admin User
print_info "Adding Admin user..."
# Uncomment and replace with actual email:
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.admin@leit-teksystems.com" \
#   --role Admin
print_step "Admin user configuration ready (update with actual email)"

# Member Users
print_info "Adding Member users (Data Engineers)..."
# Uncomment and replace with actual emails:
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.engineer1@leit-teksystems.com" \
#   --role Member

# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.engineer2@leit-teksystems.com" \
#   --role Member
print_step "Member users configuration ready (update with actual emails)"

# Contributor User
print_info "Adding Contributor user (Data Analyst)..."
# Uncomment and replace with actual email:
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.analyst@leit-teksystems.com" \
#   --role Contributor
print_step "Contributor user configuration ready (update with actual email)"

# Viewer Users
print_info "Adding Viewer users (Business Users)..."
# Uncomment and replace with actual emails:
# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.business1@leit-teksystems.com" \
#   --role Viewer

# python3 ops/scripts/manage_workspaces.py add-user \
#   --workspace "$WORKSPACE_NAME" \
#   --email "ricoh.business2@leit-teksystems.com" \
#   --role Viewer
print_step "Viewer users configuration ready (update with actual emails)"

################################################################################
# STEP 7: VERIFY SETUP
################################################################################

print_header "STEP 7: Verifying Setup"

print_info "Listing all items in workspace..."

python3 ops/scripts/manage_fabric_items.py list \
  --workspace "$WORKSPACE_NAME"

print_step "Setup verification complete"

################################################################################
# SUMMARY
################################################################################

print_header "SETUP COMPLETE - Summary"

cat << EOF

${GREEN}✓ Workspace Setup Successful!${NC}

${BLUE}Domain:${NC}           ${DOMAIN_NAME}
${BLUE}Workspace:${NC}        ${WORKSPACE_NAME}
${BLUE}Environment:${NC}      ${ENVIRONMENT}
${BLUE}Workspace ID:${NC}     ${WORKSPACE_ID}

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}📊 Fabric Items Created:${NC}

  ${GREEN}Storage:${NC}
    • RicohDataLakehouse         (Lakehouse)
    • RicohAnalyticsWarehouse    (Warehouse)

  ${GREEN}Processing:${NC}
    • 01_DataIngestion           (Notebook)
    • 02_DataTransformation      (Notebook)
    • 03_DataValidation          (Notebook)

  ${GREEN}Orchestration & Analytics:${NC}
    • RicohDataPipeline          (Data Pipeline)
    • RicohSemanticModel         (Semantic Model)
    • RicohExecutiveDashboard    (Report)

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}👥 Users to be Added (Update with actual emails):${NC}

  ${GREEN}Admin:${NC}           ricoh.admin@leit-teksystems.com
  ${GREEN}Members:${NC}         ricoh.engineer1@leit-teksystems.com
                    ricoh.engineer2@leit-teksystems.com
  ${GREEN}Contributor:${NC}     ricoh.analyst@leit-teksystems.com
  ${GREEN}Viewers:${NC}         ricoh.business1@leit-teksystems.com
                    ricoh.business2@leit-teksystems.com

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}📝 Next Steps:${NC}

  1. Update user email addresses in this script (lines 150-194)
  2. Run user add commands after updating emails
  3. Configure workspace capacity if moving from Trial
  4. Set up data connections and sources
  5. Develop notebook code for data processing
  6. Configure pipeline orchestration
  7. Build semantic model relationships
  8. Design executive dashboard visuals

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${GREEN}🚀 LEIT-Ricoh workspace is ready for use!${NC}

EOF

print_info "To view workspace in Fabric portal, use Workspace ID: ${WORKSPACE_ID}"

exit 0
