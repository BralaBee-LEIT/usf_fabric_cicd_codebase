#!/bin/bash
# File structure validation
# Usage: ./scripts/check_structure.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_utils.sh"

check_root_directory

print_header "File Structure Validation"

# Required directories
REQUIRED_DIRS=(
    "ops/scripts"
    "ops/scripts/utilities"
    "ops/config"
    "ops/tests"
    "governance/data_contracts"
    "governance/dq_rules"
    ".github/workflows"
)

# Required files
REQUIRED_FILES=(
    "ops/requirements.txt"
    "ops/scripts/utilities/constants.py"
    "ops/scripts/utilities/output.py"
    "ops/scripts/utilities/config_manager.py"
    "ops/scripts/utilities/fabric_api.py"
    "ops/scripts/validate_data_contracts.py"
    "ops/scripts/validate_dq_rules.py"
    ".github/workflows/fabric-cicd-pipeline.yml"
    "init_project_config.py"
    ".env.example"
    "README.md"
)

# Check directories
print_step "1" "Checking Required Directories"
missing_dirs=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "$dir"
    else
        print_error "$dir missing"
        missing_dirs=$((missing_dirs + 1))
    fi
done

# Check files
print_step "2" "Checking Required Files"
missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$(basename $file)"
    else
        print_error "$file missing"
        missing_files=$((missing_files + 1))
    fi
done

# Summary
echo ""
if [ $missing_dirs -eq 0 ] && [ $missing_files -eq 0 ]; then
    print_success "All required directories and files present!"
    exit 0
else
    print_error "Missing $missing_dirs directories and $missing_files files"
    exit 1
fi
