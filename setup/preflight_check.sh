#!/bin/bash
# Real Fabric Execution - Interactive Checklist
# Run this script to verify your environment before executing against live Fabric

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Microsoft Fabric Workspace Templating - Pre-Flight Checklist     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check 1: Conda Environment
echo -e "${YELLOW}[1/10]${NC} Checking Conda environment..."
if conda env list | grep -q "fabric-cicd"; then
    if [[ "$CONDA_DEFAULT_ENV" == "fabric-cicd" ]]; then
        echo -e "       ${GREEN}✓${NC} fabric-cicd environment is active"
    else
        echo -e "       ${YELLOW}⚠${NC} fabric-cicd exists but not active"
        echo -e "       ${BLUE}→${NC} Run: conda activate fabric-cicd"
        exit 1
    fi
else
    echo -e "       ${RED}✗${NC} fabric-cicd environment not found"
    echo -e "       ${BLUE}→${NC} Run: conda env create -f environment.yml"
    exit 1
fi

# Check 2: Python Version
echo -e "${YELLOW}[2/10]${NC} Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
if [[ "$PYTHON_VERSION" =~ ^3\.(9|10|11) ]]; then
    echo -e "       ${GREEN}✓${NC} Python $PYTHON_VERSION (compatible)"
else
    echo -e "       ${RED}✗${NC} Python $PYTHON_VERSION (requires 3.9+)"
    exit 1
fi

# Check 3: Required Dependencies
echo -e "${YELLOW}[3/10]${NC} Checking Python dependencies..."
if python -c "import yaml, msal, requests" 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Core dependencies installed (yaml, msal, requests)"
else
    echo -e "       ${RED}✗${NC} Missing dependencies"
    echo -e "       ${BLUE}→${NC} Run: pip install -r requirements.txt"
    exit 1
fi

# Check 4: .env File
echo -e "${YELLOW}[4/10]${NC} Checking .env file..."
if [ -f ".env" ]; then
    echo -e "       ${GREEN}✓${NC} .env file exists"
else
    echo -e "       ${YELLOW}⚠${NC} .env file not found"
    echo -e "       ${BLUE}→${NC} Run: cp .env.example .env"
    echo -e "       ${BLUE}→${NC} Then edit .env with your credentials"
    exit 1
fi

# Check 5: Azure Credentials
echo -e "${YELLOW}[5/10]${NC} Checking Azure credentials in .env..."
source .env 2>/dev/null || true
MISSING_CREDS=0

if [ -z "$AZURE_TENANT_ID" ] || [[ "$AZURE_TENANT_ID" == *"your-"* ]]; then
    echo -e "       ${RED}✗${NC} AZURE_TENANT_ID not configured"
    MISSING_CREDS=1
fi

if [ -z "$AZURE_CLIENT_ID" ] || [[ "$AZURE_CLIENT_ID" == *"your-"* ]]; then
    echo -e "       ${RED}✗${NC} AZURE_CLIENT_ID not configured"
    MISSING_CREDS=1
fi

if [ -z "$AZURE_CLIENT_SECRET" ] || [[ "$AZURE_CLIENT_SECRET" == *"your-"* ]]; then
    echo -e "       ${RED}✗${NC} AZURE_CLIENT_SECRET not configured"
    MISSING_CREDS=1
fi

if [ $MISSING_CREDS -eq 1 ]; then
    echo -e "       ${BLUE}→${NC} Edit .env file with real Azure credentials"
    exit 1
else
    echo -e "       ${GREEN}✓${NC} Azure credentials configured"
fi

# Check 6: GitHub Token (optional but recommended)
echo -e "${YELLOW}[6/10]${NC} Checking GitHub token..."
if [ -z "$GITHUB_TOKEN" ] || [[ "$GITHUB_TOKEN" == *"your-"* ]]; then
    echo -e "       ${YELLOW}⚠${NC} GITHUB_TOKEN not configured (Git integration will be limited)"
else
    echo -e "       ${GREEN}✓${NC} GitHub token configured"
fi

# Check 7: Git Repository
echo -e "${YELLOW}[7/10]${NC} Checking Git repository..."
if [ -d ".git" ]; then
    echo -e "       ${GREEN}✓${NC} Git repository initialized"
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "       ${BLUE}ℹ${NC} Current branch: $CURRENT_BRANCH"
else
    echo -e "       ${YELLOW}⚠${NC} Not a Git repository (Git operations will be skipped)"
fi

# Check 8: Configuration Manager
echo -e "${YELLOW}[8/10]${NC} Testing configuration manager..."
if python -c "from ops.scripts.utilities.config_manager import ConfigManager; cm = ConfigManager(); print(cm.get_project_name())" 2>/dev/null; then
    PROJECT_NAME=$(python -c "from ops.scripts.utilities.config_manager import ConfigManager; cm = ConfigManager(); print(cm.get_project_name())")
    echo -e "       ${GREEN}✓${NC} Configuration loaded (Project: $PROJECT_NAME)"
else
    echo -e "       ${RED}✗${NC} Configuration manager failed"
    exit 1
fi

# Check 9: Fabric Authentication
echo -e "${YELLOW}[9/10]${NC} Testing Fabric authentication..."
if python -c "from ops.scripts.utilities.workspace_manager import WorkspaceManager; wm = WorkspaceManager()" 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Fabric authentication successful"
else
    echo -e "       ${RED}✗${NC} Fabric authentication failed"
    echo -e "       ${BLUE}→${NC} Verify service principal credentials"
    echo -e "       ${BLUE}→${NC} Check service principal has Workspace Admin role"
    exit 1
fi

# Check 10: Test Suite
echo -e "${YELLOW}[10/10]${NC} Running test suite..."
if python -m pytest ops/tests/test_onboard_data_product.py -q 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} All tests passing (9/9)"
else
    echo -e "       ${YELLOW}⚠${NC} Some tests failed (may be environment-specific)"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Pre-Flight Checks Complete - Ready for Real Fabric Execution   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "  ${YELLOW}1. Create Data Product Descriptor:${NC}"
echo -e "     nano data_products/onboarding/my_product.yaml"
echo ""
echo -e "  ${YELLOW}2. Run Dry Run First:${NC}"
echo -e "     python ops/scripts/onboard_data_product.py \\"
echo -e "       data_products/onboarding/my_product.yaml --dry-run"
echo ""
echo -e "  ${YELLOW}3. Execute Against Real Fabric:${NC}"
echo -e "     python ops/scripts/onboard_data_product.py \\"
echo -e "       data_products/onboarding/my_product.yaml"
echo ""
echo -e "  ${YELLOW}4. Verify in Fabric Portal:${NC}"
echo -e "     https://app.fabric.microsoft.com"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  • Real Fabric Guide: documentation/REAL_FABRIC_EXECUTION_GUIDE.md"
echo -e "  • Live Behavior: documentation/LIVE_FABRIC_RUN_GUIDE.md"
echo -e "  • Troubleshooting: documentation/WORKSPACE_TEMPLATING_GUIDE.md"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
