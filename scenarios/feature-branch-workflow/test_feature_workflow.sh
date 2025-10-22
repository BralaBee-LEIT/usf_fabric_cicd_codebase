#!/bin/bash
# Test script for feature branch workflow scenario
# This demonstrates the complete feature branch lifecycle

set -e  # Exit on error

SCENARIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCENARIO_DIR/../.." && pwd)"
ONBOARD_SCRIPT="$REPO_ROOT/ops/scripts/onboard_data_product.py"
DESCRIPTOR="$SCENARIO_DIR/product_descriptor.yaml"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Feature Branch Workflow - Test Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test ticket ID
TICKET="TEST-$(date +%s)"

echo -e "${BLUE}🎯 Test Configuration${NC}"
echo "   Scenario: Feature Branch Workflow"
echo "   Descriptor: $DESCRIPTOR"
echo "   Test Ticket: $TICKET"
echo "   Repo Root: $REPO_ROOT"
echo ""

# Check prerequisites
echo -e "${BLUE}📋 Checking Prerequisites...${NC}"

if [ ! -f "$ONBOARD_SCRIPT" ]; then
    echo -e "${RED}❌ onboard_data_product.py not found!${NC}"
    echo "   Expected: $ONBOARD_SCRIPT"
    exit 1
fi
echo -e "${GREEN}✅ Onboarding script found${NC}"

if [ ! -f "$DESCRIPTOR" ]; then
    echo -e "${RED}❌ product_descriptor.yaml not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Product descriptor found${NC}"

# Check for .env file
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "   This test may fail if environment variables are not set"
    echo "   Copy .env.template to .env and fill in values"
    echo ""
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Step 1: Dry run
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1: Dry Run (Preview Actions)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Command: python3 $ONBOARD_SCRIPT $DESCRIPTOR --feature $TICKET --dry-run"
echo ""

cd "$REPO_ROOT"
python3 "$ONBOARD_SCRIPT" "$DESCRIPTOR" --feature "$TICKET" --dry-run

echo ""
echo -e "${GREEN}✅ Dry run completed${NC}"
echo ""
read -p "Press ENTER to continue with actual creation..."
echo ""

# Step 2: Create feature environment
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2: Create Feature Environment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "This will create:"
echo "  • Feature workspace: Customer Insights-feature-$TICKET"
echo "  • Git branch: feature/customer_insights/$TICKET"
echo "  • Scaffold: data_products/customer_insights/"
echo ""
echo "Command: python3 $ONBOARD_SCRIPT $DESCRIPTOR --feature $TICKET"
echo ""

python3 "$ONBOARD_SCRIPT" "$DESCRIPTOR" --feature "$TICKET"

echo ""
echo -e "${GREEN}✅ Feature environment created${NC}"
echo ""

# Step 3: Verify Git branch
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 3: Verify Git Branch${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if git branch -a | grep -q "feature/customer_insights/$TICKET"; then
    echo -e "${GREEN}✅ Feature branch exists: feature/customer_insights/$TICKET${NC}"
    echo ""
    echo "Branch details:"
    git log --oneline feature/customer_insights/$TICKET -5
else
    echo -e "${RED}❌ Feature branch not found${NC}"
fi

echo ""

# Step 4: Check scaffold
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 4: Verify Scaffold Creation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

SCAFFOLD_PATH="$REPO_ROOT/data_products/customer_insights"
if [ -d "$SCAFFOLD_PATH" ]; then
    echo -e "${GREEN}✅ Scaffold directory created${NC}"
    echo ""
    echo "Contents:"
    tree -L 2 "$SCAFFOLD_PATH" 2>/dev/null || ls -la "$SCAFFOLD_PATH"
else
    echo -e "${RED}❌ Scaffold directory not found${NC}"
fi

echo ""

# Step 5: Check audit log
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 5: Check Audit Log${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

AUDIT_LOG=$(ls -t "$REPO_ROOT/.onboarding_logs"/*customer_insights*.json 2>/dev/null | head -1)
if [ -n "$AUDIT_LOG" ]; then
    echo -e "${GREEN}✅ Audit log found: $(basename $AUDIT_LOG)${NC}"
    echo ""
    echo "Summary:"
    cat "$AUDIT_LOG" | python3 -m json.tool | head -20
else
    echo -e "${YELLOW}⚠️  Audit log not found${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ Feature branch workflow test completed!${NC}"
echo ""
echo "Created Resources:"
echo "  • Feature Branch: feature/customer_insights/$TICKET"
echo "  • Workspace: Customer Insights-feature-$TICKET"
echo "  • Scaffold: data_products/customer_insights/"
echo ""
echo "Next Steps:"
echo "  1. Check Fabric portal for workspace"
echo "  2. Verify Git integration in workspace settings"
echo "  3. Make changes and test workflow"
echo "  4. Create PR: gh pr create --base main --head feature/customer_insights/$TICKET"
echo ""
echo "Cleanup (when done):"
echo "  • Delete workspace in Fabric portal"
echo "  • Delete branch: git push origin --delete feature/customer_insights/$TICKET"
echo ""
echo -e "${YELLOW}💡 Tip: This demonstrates the missing feature branch functionality!${NC}"
echo ""
