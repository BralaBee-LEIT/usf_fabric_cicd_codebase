#!/usr/bin/env python3
"""
Microsoft Fabric CI/CD Framework - New Project Initialization Wizard

This interactive script helps set up the framework for a new organization by:
1. Collecting organization-specific information
2. Generating project.config.json from template
3. Creating a customized .env file
4. Validating the setup

Usage:
    python init_new_project.py

    # Non-interactive mode:
    python init_new_project.py --org "Contoso" --prefix "contoso" --non-interactive
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def validate_prefix(prefix: str) -> bool:
    """Validate project prefix format"""
    # Must be lowercase alphanumeric with hyphens, 3-20 characters
    pattern = r"^[a-z0-9][a-z0-9-]{1,18}[a-z0-9]$"
    return bool(re.match(pattern, prefix))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def prompt_with_default(prompt: str, default: str = "", validator=None) -> str:
    """Prompt user for input with optional default and validation"""
    while True:
        if default:
            user_input = input(
                f"{Colors.CYAN}{prompt} [{default}]: {Colors.ENDC}"
            ).strip()
            value = user_input if user_input else default
        else:
            user_input = input(f"{Colors.CYAN}{prompt}: {Colors.ENDC}").strip()
            value = user_input

        if not value:
            print_error("This field is required. Please provide a value.")
            continue

        if validator and not validator(value):
            print_error("Invalid format. Please try again.")
            continue

        return value


def collect_project_info(args) -> Dict[str, any]:
    """Collect project information from user"""
    print_header("Project Information")

    if args.non_interactive:
        # Use command-line arguments
        project_info = {
            "organization": args.org or "Your-Organization",
            "prefix": args.prefix or "your-org",
            "project_name": args.project_name or f"{args.prefix}-fabric-cicd",
            "description": args.description or "Microsoft Fabric CI/CD Implementation",
        }
    else:
        # Interactive prompts
        print_info("Enter your organization details. These will be used for:")
        print("  - Workspace naming conventions")
        print("  - Resource tagging and identification")
        print("  - Documentation and contact information\n")

        organization = prompt_with_default(
            "Organization name (e.g., 'Contoso Corp', 'Acme Inc')", ""
        )

        print_info(
            "\nThe prefix is used for all Fabric resources (lowercase, hyphens allowed)"
        )
        print("  Example: 'contoso' → 'contoso-analytics-dev' (workspace name)")
        prefix = prompt_with_default(
            "Project prefix (3-20 chars, lowercase, hyphens)",
            organization.lower().replace(" ", "-").replace("_", "-")[:20],
            validate_prefix,
        )

        project_name = prompt_with_default("Project name", f"{prefix}-fabric-cicd")

        description = prompt_with_default(
            "Project description", "Microsoft Fabric CI/CD Implementation"
        )

        project_info = {
            "organization": organization,
            "prefix": prefix,
            "project_name": project_name,
            "description": description,
        }

    return project_info


def collect_contact_info(args) -> Dict[str, str]:
    """Collect contact email addresses"""
    print_header("Contact Information")

    if args.non_interactive:
        domain = args.email_domain or "company.com"
        return {
            "data_owner": f"data-owner@{domain}",
            "technical_lead": f"tech-lead@{domain}",
            "devops_lead": f"devops@{domain}",
        }

    print_info("Enter email addresses for key contacts (used in data contracts)")
    print("  These can be distribution lists or individual emails\n")

    data_owner = prompt_with_default(
        "Data Owner email", "data-owner@company.com", validate_email
    )

    technical_lead = prompt_with_default(
        "Technical Lead email", "tech-lead@company.com", validate_email
    )

    devops_lead = prompt_with_default(
        "DevOps Lead email", "devops@company.com", validate_email
    )

    return {
        "data_owner": data_owner,
        "technical_lead": technical_lead,
        "devops_lead": devops_lead,
    }


def collect_git_info(args) -> Dict[str, str]:
    """Collect Git repository information"""
    print_header("Git Repository Configuration")

    if args.non_interactive:
        return {
            "organization": args.git_org or "your-github-org",
            "repository": args.git_repo or "fabric-cicd",
        }

    print_info("Configure Git integration for workspace synchronization")
    print("  This connects Fabric workspaces to your Git repository\n")

    git_org = prompt_with_default("GitHub/Azure DevOps organization", "")

    git_repo = prompt_with_default("Repository name", "fabric-cicd")

    return {"organization": git_org, "repository": git_repo}


def generate_project_config(project_info: Dict, contacts: Dict, git_info: Dict) -> Dict:
    """Generate project.config.json from template"""

    template_path = Path("project.config.template.json")

    if not template_path.exists():
        print_error(f"Template file not found: {template_path}")
        sys.exit(1)

    with open(template_path, "r") as f:
        config = json.load(f)

    # Update project section
    config["project"]["name"] = project_info["project_name"]
    config["project"]["prefix"] = project_info["prefix"]
    config["project"]["description"] = project_info["description"]
    config["project"]["organization"] = project_info["organization"]

    # Update metadata
    config["metadata"]["created_date"] = datetime.utcnow().isoformat() + "Z"
    config["metadata"][
        "_instructions"
    ] = "This file was generated from project.config.template.json - DO NOT commit to version control"

    return config


def generate_env_file(project_info: Dict, contacts: Dict, git_info: Dict):
    """Generate .env file from .env.example with customized values"""

    env_example_path = Path(".env.example")
    env_path = Path(".env")

    if not env_example_path.exists():
        print_warning(".env.example not found, skipping .env generation")
        return

    if env_path.exists():
        response = (
            input(
                f"{Colors.YELLOW}.env file already exists. Overwrite? (y/N): {Colors.ENDC}"
            )
            .strip()
            .lower()
        )
        if response != "y":
            print_info("Skipping .env file generation")
            return

    # Read template
    with open(env_example_path, "r") as f:
        env_content = f.read()

    # Replace placeholder values
    replacements = {
        "your-github-org": git_info["organization"],
        "your-repo-name": git_info["repository"],
        "data-owner@your-company.com": contacts["data_owner"],
        "tech-lead@your-company.com": contacts["technical_lead"],
        "devops@your-company.com": contacts["devops_lead"],
        "your-prefix-fabric-dev": f"{project_info['prefix']}-fabric-dev",
        "your-prefix-fabric-test": f"{project_info['prefix']}-fabric-test",
        "your-prefix-fabric-prod": f"{project_info['prefix']}-fabric-prod",
    }

    for placeholder, value in replacements.items():
        env_content = env_content.replace(placeholder, value)

    # Write .env file
    with open(env_path, "w") as f:
        f.write(env_content)

    print_success("Created .env file with customized values")
    print_warning(
        "IMPORTANT: Update Azure credentials in .env before running scenarios"
    )


def save_config(config: Dict):
    """Save project.config.json"""
    config_path = Path("project.config.json")

    if config_path.exists():
        response = (
            input(
                f"{Colors.YELLOW}project.config.json already exists. Overwrite? (y/N): {Colors.ENDC}"
            )
            .strip()
            .lower()
        )
        if response != "y":
            print_info("Keeping existing project.config.json")
            return False

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print_success("Created project.config.json")
    return True


def validate_setup():
    """Validate that setup is complete"""
    print_header("Validating Setup")

    issues = []

    # Check project.config.json
    if not Path("project.config.json").exists():
        issues.append("project.config.json not found")
    else:
        try:
            with open("project.config.json", "r") as f:
                config = json.load(f)
                if config["project"]["prefix"] == "your-org-prefix":
                    issues.append("project.config.json still has placeholder values")
                else:
                    print_success("project.config.json exists and is customized")
        except Exception as e:
            issues.append(f"project.config.json is invalid: {e}")

    # Check .env file
    if not Path(".env").exists():
        print_warning(".env file not found - create from .env.example")
    else:
        print_success(".env file exists")

    # Check template
    if Path("project.config.template.json").exists():
        print_success("project.config.template.json exists")
    else:
        issues.append("project.config.template.json not found")

    return issues


def print_next_steps(project_info: Dict):
    """Print next steps for user"""
    print_header("Next Steps")

    print(f"{Colors.BOLD}Your project is configured!{Colors.ENDC}\n")

    print(f"{Colors.CYAN}1. Update Azure Credentials{Colors.ENDC}")
    print("   Edit .env and add your Azure Service Principal credentials:")
    print("   - AZURE_CLIENT_ID")
    print("   - AZURE_CLIENT_SECRET")
    print("   - AZURE_TENANT_ID")
    print("   - AZURE_SUBSCRIPTION_ID")
    print("   - FABRIC_CAPACITY_ID\n")

    print(f"{Colors.CYAN}2. Validate Configuration{Colors.ENDC}")
    print("   python setup/init_project_config.py --validate\n")

    print(f"{Colors.CYAN}3. Run Preflight Check{Colors.ENDC}")
    print("   ./setup/preflight_check.sh\n")

    print(f"{Colors.CYAN}4. Create Your First Workspace{Colors.ENDC}")
    print("   python ops/scripts/manage_workspaces.py create \\")
    print("       --project analytics --environment dev\n")

    print(f"{Colors.CYAN}5. Explore Scenarios{Colors.ENDC}")
    print("   cd scenarios/")
    print("   cat README.md\n")

    print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
    print("   - Quick Start: docs/getting-started/QUICKSTART.md")
    print("   - Provisioning Guide: docs/guides/WORKSPACE_PROVISIONING_GUIDE.md")
    print("   - Implementation Guide: docs/guides/IMPLEMENTATION_GUIDE.md\n")

    print(f"{Colors.GREEN}{'=' * 80}{Colors.ENDC}")
    print(
        f"{Colors.GREEN}Setup Complete! Happy building with Microsoft Fabric! 🚀{Colors.ENDC}"
    )
    print(f"{Colors.GREEN}{'=' * 80}{Colors.ENDC}\n")


def main():
    """Main initialization workflow"""
    parser = argparse.ArgumentParser(
        description="Initialize Microsoft Fabric CI/CD Framework for a new organization"
    )
    parser.add_argument("--org", help="Organization name")
    parser.add_argument("--prefix", help="Project prefix (lowercase)")
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--git-org", help="GitHub/Azure DevOps organization")
    parser.add_argument("--git-repo", help="Repository name")
    parser.add_argument("--email-domain", help="Email domain for contacts")
    parser.add_argument(
        "--non-interactive", action="store_true", help="Non-interactive mode"
    )

    args = parser.parse_args()

    print_header("Microsoft Fabric CI/CD Framework - Project Initialization")

    print(f"{Colors.BOLD}Welcome!{Colors.ENDC}\n")
    print(
        "This wizard will help you configure the Fabric CI/CD framework for your organization."
    )
    print("You'll be prompted for:")
    print("  • Organization and project details")
    print("  • Contact information")
    print("  • Git repository configuration\n")

    if not args.non_interactive:
        response = (
            input(f"{Colors.CYAN}Ready to begin? (Y/n): {Colors.ENDC}").strip().lower()
        )
        if response == "n":
            print("Initialization cancelled.")
            return

    # Collect information
    project_info = collect_project_info(args)
    contacts = collect_contact_info(args)
    git_info = collect_git_info(args)

    # Generate configuration
    print_header("Generating Configuration Files")

    config = generate_project_config(project_info, contacts, git_info)

    # Save files
    if save_config(config):
        print_success("Configuration files generated successfully")

    generate_env_file(project_info, contacts, git_info)

    # Validate
    issues = validate_setup()

    if issues:
        print_warning("Setup completed with issues:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print_success("All validation checks passed!")

    # Next steps
    print_next_steps(project_info)


if __name__ == "__main__":
    main()
