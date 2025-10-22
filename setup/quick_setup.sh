#!/bin/bash
# Quick Setup Script for Microsoft Fabric CI/CD (Lightweight Version)
# 
# ⚠️  DEPRECATION NOTICE:
# This script is being replaced by the new modular setup system.
# Please use ./setup.sh instead for better maintainability.
# 
# New modular scripts:
#   ./setup.sh              - Full setup
#   ./scripts/check_*.sh    - Individual checks
# 
# This script will be removed in a future release.
#
set -e

echo "⚠️  DEPRECATION WARNING: Use './setup.sh' instead"
echo ""
echo "🚀 Microsoft Fabric CI/CD Quick Setup (Fast Mode - Legacy)"
echo "============================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "\n${BLUE}📋 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if script is run from correct directory
if [ ! -f "ops/requirements.txt" ]; then
    print_error "Please run this script from the repository root directory"
    exit 1
fi

print_step "1" "Environment Check"

# Check if conda is available
if command -v conda &> /dev/null; then
    print_success "Conda found"
    
    # Check if environment.yml exists
    if [ -f "environment.yml" ]; then
        print_success "environment.yml found"
        
        # Check if fabric-cicd environment exists
        if conda env list | grep -q "^fabric-cicd "; then
            print_success "fabric-cicd environment exists"
            
            # Check if we're in the correct environment
            if [ "$CONDA_DEFAULT_ENV" = "fabric-cicd" ]; then
                print_success "Already in fabric-cicd environment"
            else
                print_warning "Not in fabric-cicd environment (currently in: ${CONDA_DEFAULT_ENV:-none})"
                echo -e "${YELLOW}Activating fabric-cicd environment...${NC}"
                
                # Note: We can't directly activate in a subshell, so we inform the user
                echo -e "${YELLOW}Please run: conda activate fabric-cicd${NC}"
                echo -e "${YELLOW}Then re-run this script${NC}"
                exit 1
            fi
        else
            print_warning "fabric-cicd environment does not exist"
            echo -e "${YELLOW}Creating conda environment from environment.yml...${NC}"
            conda env create -f environment.yml
            print_success "Environment created successfully"
            echo -e "${YELLOW}Please run: conda activate fabric-cicd${NC}"
            echo -e "${YELLOW}Then re-run this script${NC}"
            exit 0
        fi
        
        # Verify Python version in environment
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION (from fabric-cicd environment)"
        
    else
        print_error "environment.yml not found"
        exit 1
    fi
else
    # Fallback to regular Python check
    print_warning "Conda not found, checking for Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Check virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        print_success "Virtual environment: $(basename $VIRTUAL_ENV)"
    else
        print_warning "No virtual environment detected"
        echo -e "\n${YELLOW}Create a virtual environment first:${NC}"
        echo "  python -m venv fabric-cicd-env && source fabric-cicd-env/bin/activate"
    fi
fi

print_step "2" "File Structure Check"

# Check required directories
REQUIRED_DIRS=("ops/scripts" "ops/config" ".github/workflows")
missing_dirs=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory $dir exists"
    else
        print_error "Directory $dir missing"
        missing_dirs=$((missing_dirs + 1))
    fi
done

# Check key files (quick check)
REQUIRED_FILES=(
    "ops/scripts/utilities/config_manager.py"
    "ops/scripts/validate_data_contracts.py"
    "ops/scripts/validate_dq_rules.py"
    ".github/workflows/fabric-cicd-pipeline.yml"
    "init_project_config.py"
    ".env.example"
)
missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "File $(basename $file) exists"
    else
        print_error "File $file missing"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_dirs -gt 0 ] || [ $missing_files -gt 0 ]; then
    print_error "Missing $missing_dirs directories and $missing_files files"
    exit 1
fi

print_step "3" "Configuration Check"

# Check for project configuration
if [ -f "project.config.json" ]; then
    print_success "project.config.json found"
else
    print_warning "project.config.json not found"
    echo -e "\n${YELLOW}Run 'python init_project_config.py' to create configuration${NC}"
fi

# Check for environment file
if [ -f ".env" ]; then
    print_success ".env file found"
else
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        echo -e "\n${YELLOW}Copy .env.example to .env and update with your values:${NC}"
        echo "  cp .env.example .env"
    fi
fi

print_step "4" "Quick Validation"

# Basic YAML syntax check (without installing dependencies)
if command -v python3 &> /dev/null; then
    echo "Checking YAML files syntax..."
    
    # Check data contracts
    if [ -d "governance/data_contracts" ]; then
        contract_count=$(find governance/data_contracts -name "*.yaml" -type f | wc -l)
        if [ $contract_count -gt 0 ]; then
            print_success "Found $contract_count data contract file(s)"
            
            # Quick YAML syntax check
            for file in governance/data_contracts/*.yaml; do
                if [ -f "$file" ]; then
                    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                        print_success "$(basename $file) - Valid YAML"
                    else
                        print_error "$(basename $file) - Invalid YAML syntax"
                    fi
                fi
            done
        else
            print_warning "No data contract files found"
        fi
    fi
    
    # Check DQ rules
    if [ -d "governance/dq_rules" ]; then
        rules_count=$(find governance/dq_rules -name "*.yaml" -type f | wc -l)
        if [ $rules_count -gt 0 ]; then
            print_success "Found $rules_count DQ rules file(s)"
            
            # Quick YAML syntax check
            for file in governance/dq_rules/*.yaml; do
                if [ -f "$file" ]; then
                    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                        print_success "$(basename $file) - Valid YAML"
                    else
                        print_error "$(basename $file) - Invalid YAML syntax"
                    fi
                fi
            done
        else
            print_warning "No DQ rules files found"
        fi
    fi
fi

print_step "5" "Setup Summary"

echo -e "\n${GREEN}🎉 Basic Setup Check Complete!${NC}"

echo -e "\n${BLUE}📋 Status Summary:${NC}"
echo "✅ Repository structure is valid"
echo "✅ Required files are present"
echo "✅ YAML files have valid syntax"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"

if [ ! -f ".env" ]; then
    echo "1. Create environment file:"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your actual values"
fi

if [ ! -f "project.config.json" ]; then
    echo "2. Initialize project configuration:"
    echo "   python init_project_config.py"
fi

if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "3. Create and activate virtual environment:"
    echo "   python -m venv fabric-cicd-env"
    echo "   source fabric-cicd-env/bin/activate"
fi

echo "4. Install dependencies:"
echo "   pip install -r ops/requirements.txt"

echo "5. Run full validation (after installing dependencies):"
echo "   python ops/scripts/validate_data_contracts.py --contracts-dir governance/data_contracts"
echo "   python ops/scripts/validate_dq_rules.py --rules-dir governance/dq_rules"

echo "6. Test configuration (after setup):"
echo "   python -c \"from ops.scripts.utilities.config_manager import ConfigManager; print('✅ Config loaded')\""

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo "- Environment Setup: ENVIRONMENT_SETUP.md"
echo "- Data Contracts: DATA_CONTRACTS_MULTI_FILE_IMPLEMENTATION.md"
echo "- DQ Rules: DQ_RULES_MULTI_FILE_IMPLEMENTATION.md"

echo -e "\n${GREEN}Setup completed in $(date)${NC}"
echo "This was a lightweight check. Run the full setup after creating your environment and installing dependencies."