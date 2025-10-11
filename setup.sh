#!/bin/bash
# Main setup orchestrator - calls modular scripts
# Usage: ./setup.sh [--skip-deps]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/setup_utils.sh"

# Parse arguments
SKIP_DEPS=false
if [ "$1" == "--skip-deps" ]; then
    SKIP_DEPS=true
fi

check_root_directory

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

print_header "🚀 Microsoft Fabric CI/CD Setup"

# Step 1: Check environment
echo ""
print_step "1" "Environment Check"
if bash scripts/check_environment.sh; then
    print_success "Environment check passed"
else
    print_error "Environment check failed"
    exit 1
fi

# Step 2: Check file structure
echo ""
print_step "2" "File Structure Check"
if bash scripts/check_structure.sh; then
    print_success "Structure check passed"
else
    print_error "Structure check failed"
    exit 1
fi

# Step 3: Check configuration
echo ""
print_step "3" "Configuration Check"
bash scripts/check_config.sh || print_warning "Some configurations need attention"

# Step 4: Validate YAML files
echo ""
print_step "4" "YAML Validation"
bash scripts/validate_yaml.sh || print_warning "Some YAML files need attention"

# Step 5: Install dependencies (if not skipped)
if [ "$SKIP_DEPS" == "false" ]; then
    echo ""
    print_step "5" "Dependencies Installation"
    
    if [ -n "$VIRTUAL_ENV" ] || [ -n "$CONDA_DEFAULT_ENV" ]; then
        print_info "Installing Python dependencies..."
        pip install -r ops/requirements.txt --quiet
        print_success "Dependencies installed"
    else
        print_warning "Skipping dependency installation (no virtual environment)"
        print_info "Activate a virtual environment and run:"
        echo "  pip install -r ops/requirements.txt"
    fi
else
    print_info "Skipping dependency installation (--skip-deps flag)"
fi

# Summary
echo ""
print_header "✅ Setup Complete!"

echo ""
print_info "Next steps:"
echo ""
echo "  1. Configure environment (if not done):"
echo "     cp .env.example .env"
echo "     # Edit .env with your credentials"
echo ""
echo "  2. Initialize project configuration:"
echo "     python init_project_config.py"
echo ""
echo "  3. Run validators:"
echo "     python ops/scripts/validate_data_contracts.py --contracts-dir governance/data_contracts"
echo "     python ops/scripts/validate_dq_rules.py --rules-dir governance/dq_rules"
echo ""
echo "  4. Run tests:"
echo "     pytest ops/tests/ -v"
echo ""
echo "  5. Test new modules:"
echo "     python3 -c \"from ops.scripts.utilities.constants import *; print('✅ Constants loaded')\""
echo "     python3 -c \"from ops.scripts.utilities.output import console_success; console_success('Test')\""
echo ""

print_info "Documentation:"
echo "  - Quick Start: QUICKSTART.md"
echo "  - Project Overview: PROJECT_OVERVIEW.md"
echo "  - Latest Updates: MAINTENANCE_IMPROVEMENTS_COMPLETE.md"
echo ""

print_success "Setup completed successfully! 🎉"
