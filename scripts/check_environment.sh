#!/bin/bash
# Environment validation check
# Usage: ./scripts/check_environment.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_utils.sh"

check_root_directory

print_header "Environment Validation"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
    
    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python version is compatible (3.8+)"
    else
        print_warning "Python 3.8+ recommended (you have $PYTHON_VERSION)"
    fi
else
    print_error "Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    print_success "Virtual environment active: $(basename $VIRTUAL_ENV)"
elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    print_success "Conda environment active: $CONDA_DEFAULT_ENV"
else
    print_warning "No virtual environment detected"
    echo ""
    print_info "Create a virtual environment:"
    echo "  python3 -m venv fabric-env && source fabric-env/bin/activate"
    echo "  # OR"
    echo "  conda create -n fabric-cicd python=3.12 && conda activate fabric-cicd"
fi

# Check pip
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_success "pip $PIP_VERSION found"
else
    print_warning "pip3 not found"
fi

# Check git
if command_exists git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_success "git $GIT_VERSION found"
else
    print_warning "git not found (optional but recommended)"
fi

# Check docker (optional)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_success "docker $DOCKER_VERSION found (optional)"
else
    print_info "docker not found (optional - only needed for containerized deployments)"
fi

echo ""
print_success "Environment check complete!"
