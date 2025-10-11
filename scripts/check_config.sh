#!/bin/bash
# Configuration validation
# Usage: ./scripts/check_config.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_utils.sh"

check_root_directory

print_header "Configuration Validation"

# Check project.config.json
print_step "1" "Project Configuration"
if [ -f "project.config.json" ]; then
    print_success "project.config.json found"
    
    # Validate JSON syntax
    if python3 -c "import json; json.load(open('project.config.json'))" 2>/dev/null; then
        print_success "Valid JSON syntax"
    else
        print_error "Invalid JSON syntax in project.config.json"
    fi
else
    print_warning "project.config.json not found"
    print_info "Run: python init_project_config.py"
fi

# Check .env file
print_step "2" "Environment Variables"
if [ -f ".env" ]; then
    print_success ".env file found"
    
    # Check for required variables
    REQUIRED_VARS=(
        "AZURE_CLIENT_ID"
        "AZURE_CLIENT_SECRET"
        "AZURE_TENANT_ID"
        "AZURE_SUBSCRIPTION_ID"
    )
    
    missing_vars=0
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" .env && ! grep -q "^$var=your-" .env; then
            print_success "$var is set"
        else
            print_warning "$var not configured"
            missing_vars=$((missing_vars + 1))
        fi
    done
    
    if [ $missing_vars -gt 0 ]; then
        print_warning "$missing_vars required variables not configured"
        print_info "Edit .env file with your actual values"
    fi
else
    print_warning ".env file not found"
    print_info "Run: cp .env.example .env"
    print_info "Then edit .env with your credentials"
fi

# Check constants module
print_step "3" "Constants Module"
if python3 -c "from ops.scripts.utilities.constants import *" 2>/dev/null; then
    print_success "Constants module loads successfully"
else
    print_error "Constants module has errors"
fi

echo ""
print_success "Configuration check complete!"
