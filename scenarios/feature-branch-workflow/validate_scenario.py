#!/usr/bin/env python3
"""
Quick validation script for feature-branch-workflow scenario
Tests prerequisites and configuration without running the full workflow
"""

import sys
from pathlib import Path


# ANSI color codes
class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def main():
    scenario_dir = Path(__file__).parent.absolute()
    repo_root = scenario_dir.parent.parent

    print(f"\n{Colors.BLUE}Feature Branch Workflow - Quick Validation{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.NC}\n")

    errors = []
    warnings = []

    # Check onboard script
    onboard_script = repo_root / "ops" / "scripts" / "onboard_data_product.py"
    if onboard_script.is_file():
        print_success(f"Onboarding script found: {onboard_script.name}")
    else:
        print_error(f"Onboarding script not found: {onboard_script}")
        errors.append("Missing onboard_data_product.py")

    # Check product descriptor
    descriptor = scenario_dir / "product_descriptor.yaml"
    if descriptor.is_file():
        print_success(f"Product descriptor found: {descriptor.name}")

        # Validate YAML syntax
        try:
            import yaml

            with open(descriptor, "r") as f:
                config = yaml.safe_load(f)
                if "product" in config and "environments" in config:
                    print_success("YAML structure valid (has product & environments)")
                else:
                    print_warning(
                        "YAML missing expected sections (product/environments)"
                    )
                    warnings.append("YAML structure incomplete")
        except ImportError:
            print_warning("PyYAML not installed - skipping YAML validation")
        except Exception as e:
            print_error(f"YAML parsing error: {e}")
            errors.append("Invalid YAML syntax")
    else:
        print_error(f"Product descriptor not found: {descriptor}")
        errors.append("Missing product_descriptor.yaml")

    # Check .env file
    env_file = repo_root / ".env"
    if env_file.is_file():
        print_success(".env file found")
    else:
        print_warning(".env file not found (copy from .env.template)")
        warnings.append("Missing .env file")

    # Check Python environment
    sys.path.insert(0, str(repo_root / "ops" / "scripts"))
    try:
        from utilities.workspace_manager import WorkspaceManager

        print_success("Python utilities accessible (import successful)")
    except ImportError as e:
        print_warning(f"Python utilities import failed: {e}")
        warnings.append("Python environment may need setup")

    # Check README files
    readme_files = list(scenario_dir.glob("*.md"))
    if readme_files:
        print_success(f"Documentation found: {len(readme_files)} markdown files")

    # Summary
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.NC}")
    if not errors:
        print_success(f"Validation passed! ({len(warnings)} warnings)")
        print(f"\n{Colors.BLUE}Ready to run:{Colors.NC}")
        print("  python3 test_feature_workflow.py")
        return 0
    else:
        print_error(
            f"Validation failed! ({len(errors)} errors, {len(warnings)} warnings)"
        )
        for error in errors:
            print(f"  • {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
