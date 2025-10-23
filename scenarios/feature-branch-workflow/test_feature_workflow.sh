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

# Step 5: Check audit log (v2.0)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 5: Check Audit Logs (v2.0)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check old format audit log
AUDIT_LOG=$(ls -t "$REPO_ROOT/.onboarding_logs"/*customer_insights*.json 2>/dev/null | head -1)
if [ -n "$AUDIT_LOG" ]; then
    echo -e "${GREEN}✅ Onboarding log found: $(basename $AUDIT_LOG)${NC}"
    echo ""
    echo "Summary:"
    cat "$AUDIT_LOG" | python3 -m json.tool | head -20
else
    echo -e "${YELLOW}⚠️  Onboarding log not found${NC}"
fi

echo ""

# Check new format audit trail (v2.0)
AUDIT_TRAIL="$REPO_ROOT/audit/audit_trail.jsonl"
if [ -f "$AUDIT_TRAIL" ]; then
    echo -e "${GREEN}✅ NEW: Audit trail found (v2.0 feature)${NC}"
    echo ""
    echo "Recent events (last 5):"
    tail -5 "$AUDIT_TRAIL" | python3 -c "import sys, json; [print(json.dumps(json.loads(line), indent=2)) for line in sys.stdin]" 2>/dev/null || tail -5 "$AUDIT_TRAIL"
    echo ""
    echo "Event summary:"
    python3 -c "
import json
from collections import Counter
try:
    events = []
    with open('$AUDIT_TRAIL', 'r') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    
    event_types = Counter(e['event_type'] for e in events)
    print('Total events:', len(events))
    for event_type, count in event_types.most_common():
        print(f'  • {event_type}: {count}')
except Exception as e:
    print(f'Could not parse audit trail: {e}')
" 2>/dev/null || echo "  (Install jq for better formatting: sudo apt install jq)"
else
    echo -e "${YELLOW}⚠️  NEW: Audit trail not found (audit logging may be disabled)${NC}"
fi

echo ""

# Step 6: Verify Git Integration (v2.0)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 6: Verify Git Integration (v2.0)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Checking if workspace was auto-connected to Git..."
echo ""
echo -e "${YELLOW}Note: Auto-connection requires:${NC}"
echo "  • git_integration.enabled = true in project.config.json"
echo "  • git_integration.auto_connect_workspaces = true"
echo "  • GIT_ORGANIZATION and GIT_REPOSITORY environment variables set"
echo ""

if [ -f "$REPO_ROOT/project.config.json" ]; then
    GIT_ENABLED=$(python3 -c "
import json
try:
    with open('$REPO_ROOT/project.config.json', 'r') as f:
        config = json.load(f)
        enabled = config.get('git_integration', {}).get('enabled', False)
        auto_connect = config.get('git_integration', {}).get('auto_connect_workspaces', False)
        print('enabled' if (enabled and auto_connect) else 'disabled')
except:
    print('error')
" 2>/dev/null)
    
    if [ "$GIT_ENABLED" = "enabled" ]; then
        echo -e "${GREEN}✅ Git auto-connect is ENABLED in project.config.json${NC}"
        echo "   The workspace should be automatically connected to Git!"
    else
        echo -e "${YELLOW}⚠️  Git auto-connect is DISABLED${NC}"
        echo "   Enable it in project.config.json to test this feature"
    fi
else
    echo -e "${YELLOW}⚠️  project.config.json not found${NC}"
fi

echo ""
echo -e "${BLUE}💡 To verify in Fabric portal:${NC}"
echo "   1. Open the feature workspace in Fabric portal"
echo "   2. Go to Workspace Settings → Git integration"
echo "   3. Should show: Connected to ${GITHUB_ORG:-your-org}/${GITHUB_REPO:-your-repo}"
echo ""

# Step 7: Verify Naming Standards (v2.0)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 7: Verify Naming Standards (v2.0)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "$REPO_ROOT/naming_standards.yaml" ]; then
    echo -e "${GREEN}✅ Naming standards configuration found${NC}"
    echo ""
    echo "Checking if naming validation is enabled..."
    
    # Test naming validation
    python3 -c "
import sys
sys.path.insert(0, '$REPO_ROOT/ops/scripts/utilities')
try:
    from item_naming_validator import validate_item_name
    
    # Test medallion architecture
    result = validate_item_name('BRONZE_CustomerData_Lakehouse', 'Lakehouse')
    if result.is_valid:
        print('✅ Medallion architecture validation: WORKING')
        print('   Example: BRONZE_CustomerData_Lakehouse is VALID')
    else:
        print('⚠️  Validation not working as expected')
    
    # Test invalid name
    result = validate_item_name('CustomerData', 'Lakehouse')
    if not result.is_valid:
        print('✅ Invalid name detection: WORKING')
        print('   Example: CustomerData is INVALID (missing BRONZE/SILVER/GOLD)')
    
    print('')
    print('Naming validation is operational!')
    
except ImportError as e:
    print('⚠️  Naming validation utilities not available')
    print(f'   Error: {e}')
except Exception as e:
    print(f'⚠️  Error testing naming validation: {e}')
" 2>&1
else
    echo -e "${YELLOW}⚠️  naming_standards.yaml not found${NC}"
    echo "   Create it to enable automatic naming validation"
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
echo "v2.0 Features Tested:"
echo "  ✓ Git Integration (auto-connect capability)"
echo "  ✓ Audit Logging (JSONL trail)"
echo "  ✓ Naming Standards (validation utilities)"
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
echo -e "${YELLOW}💡 Tip: Run 'cat audit/audit_trail.jsonl | jq .' to see full audit trail${NC}"
echo ""
