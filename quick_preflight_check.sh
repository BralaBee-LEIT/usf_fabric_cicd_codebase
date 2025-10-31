#!/bin/bash
# Quick Pre-Flight Check - Works with any Python environment
# Validates essential components before running framework

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Microsoft Fabric CI/CD Framework - Quick Pre-Flight Check        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNED=0

# Check 1: Python Version
echo -e "${YELLOW}[1/8]${NC} Checking Python version..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    if [[ "$PYTHON_VERSION" =~ ^3\.(9|10|11|12) ]]; then
        echo -e "       ${GREEN}✓${NC} Python $PYTHON_VERSION (compatible)"
        ((CHECKS_PASSED++))
    else
        echo -e "       ${YELLOW}⚠${NC} Python $PYTHON_VERSION (recommended: 3.9+)"
        ((CHECKS_WARNED++))
    fi
else
    echo -e "       ${RED}✗${NC} Python not found"
    ((CHECKS_FAILED++))
fi

# Check 2: Required Python Packages
echo -e "${YELLOW}[2/8]${NC} Checking Python dependencies..."
MISSING_DEPS=()
for pkg in yaml msal requests pandas; do
    if ! python -c "import $pkg" 2>/dev/null; then
        MISSING_DEPS+=("$pkg")
    fi
done

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "       ${GREEN}✓${NC} All core dependencies installed"
    ((CHECKS_PASSED++))
else
    echo -e "       ${RED}✗${NC} Missing: ${MISSING_DEPS[*]}"
    echo -e "       ${BLUE}→${NC} Run: pip install -r ops/requirements.txt"
    ((CHECKS_FAILED++))
fi

# Check 3: .env File
echo -e "${YELLOW}[3/8]${NC} Checking .env file..."
if [ -f ".env" ]; then
    echo -e "       ${GREEN}✓${NC} .env file exists"
    ((CHECKS_PASSED++))
else
    echo -e "       ${RED}✗${NC} .env file not found"
    echo -e "       ${BLUE}→${NC} Run: cp .env.example .env"
    ((CHECKS_FAILED++))
fi

# Check 4: Azure Credentials
echo -e "${YELLOW}[4/8]${NC} Checking Azure credentials..."
if [ -f ".env" ]; then
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
    
    if [ $MISSING_CREDS -eq 0 ]; then
        echo -e "       ${GREEN}✓${NC} Azure credentials configured"
        ((CHECKS_PASSED++))
    else
        echo -e "       ${BLUE}→${NC} Edit .env with your Azure credentials"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "       ${RED}✗${NC} Cannot check (no .env file)"
    ((CHECKS_FAILED++))
fi

# Check 5: Fabric Capacity ID
echo -e "${YELLOW}[5/8]${NC} Checking Fabric Capacity ID..."
if [ -f ".env" ] && [ -n "$FABRIC_CAPACITY_ID" ] && [[ ! "$FABRIC_CAPACITY_ID" == *"your-"* ]]; then
    echo -e "       ${GREEN}✓${NC} FABRIC_CAPACITY_ID configured"
    ((CHECKS_PASSED++))
else
    echo -e "       ${YELLOW}⚠${NC} FABRIC_CAPACITY_ID not configured (optional)"
    ((CHECKS_WARNED++))
fi

# Check 6: Project Config
echo -e "${YELLOW}[6/8]${NC} Checking project configuration..."
if [ -f "project.config.json" ]; then
    echo -e "       ${GREEN}✓${NC} project.config.json exists"
    ((CHECKS_PASSED++))
else
    echo -e "       ${YELLOW}⚠${NC} project.config.json not found (optional)"
    echo -e "       ${BLUE}→${NC} Run: python init_new_project.py (if needed)"
    ((CHECKS_WARNED++))
fi

# Check 7: Git Repository
echo -e "${YELLOW}[7/8]${NC} Checking Git repository..."
if [ -d ".git" ]; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo -e "       ${GREEN}✓${NC} Git repository initialized (branch: $CURRENT_BRANCH)"
    ((CHECKS_PASSED++))
else
    echo -e "       ${YELLOW}⚠${NC} Not a git repository"
    ((CHECKS_WARNED++))
fi

# Check 8: Key Scripts
echo -e "${YELLOW}[8/8]${NC} Checking framework scripts..."
MISSING_SCRIPTS=0
for script in ops/scripts/manage_workspaces.py tools/manage_fabric_folders.py; do
    if [ ! -f "$script" ]; then
        echo -e "       ${RED}✗${NC} Missing: $script"
        MISSING_SCRIPTS=1
    fi
done

if [ $MISSING_SCRIPTS -eq 0 ]; then
    echo -e "       ${GREEN}✓${NC} Framework scripts present"
    ((CHECKS_PASSED++))
else
    ((CHECKS_FAILED++))
fi

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                          SUMMARY                                   ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Passed:${NC}  $CHECKS_PASSED"
echo -e "${YELLOW}⚠ Warnings:${NC} $CHECKS_WARNED"
echo -e "${RED}✗ Failed:${NC}  $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ Pre-flight check FAILED${NC}"
    echo -e "   Fix the issues above before proceeding"
    exit 1
elif [ $CHECKS_WARNED -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Pre-flight check PASSED with warnings${NC}"
    echo -e "   System is functional but some optional features unavailable"
    exit 0
else
    echo -e "${GREEN}✅ Pre-flight check PASSED${NC}"
    echo -e "   System is ready for operations"
    exit 0
fi
