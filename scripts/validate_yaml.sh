#!/bin/bash
# YAML files validation
# Usage: ./scripts/validate_yaml.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_utils.sh"

check_root_directory

print_header "YAML Files Validation"

# Check data contracts
print_step "1" "Data Contracts"
if [ -d "governance/data_contracts" ]; then
    contract_count=$(find governance/data_contracts -name "*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$contract_count" -gt 0 ]; then
        print_info "Found $contract_count data contract file(s)"
        
        failed=0
        for file in governance/data_contracts/*.yaml; do
            if [ -f "$file" ]; then
                if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    print_success "$(basename $file)"
                else
                    print_error "$(basename $file) - Invalid YAML syntax"
                    failed=$((failed + 1))
                fi
            fi
        done
        
        if [ $failed -eq 0 ]; then
            print_success "All data contracts have valid YAML syntax"
        else
            print_error "$failed data contract(s) have invalid syntax"
        fi
    else
        print_warning "No data contract files found"
    fi
else
    print_warning "governance/data_contracts directory not found"
fi

# Check DQ rules
print_step "2" "Data Quality Rules"
if [ -d "governance/dq_rules" ]; then
    rules_count=$(find governance/dq_rules -name "*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$rules_count" -gt 0 ]; then
        print_info "Found $rules_count DQ rules file(s)"
        
        failed=0
        for file in governance/dq_rules/*.yaml; do
            if [ -f "$file" ]; then
                if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    print_success "$(basename $file)"
                else
                    print_error "$(basename $file) - Invalid YAML syntax"
                    failed=$((failed + 1))
                fi
            fi
        done
        
        if [ $failed -eq 0 ]; then
            print_success "All DQ rules have valid YAML syntax"
        else
            print_error "$failed DQ rule file(s) have invalid syntax"
        fi
    else
        print_warning "No DQ rules files found"
    fi
else
    print_warning "governance/dq_rules directory not found"
fi

echo ""
print_success "YAML validation complete!"
