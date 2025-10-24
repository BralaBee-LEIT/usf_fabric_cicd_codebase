#!/usr/bin/env python3
"""
Project Configuration Initialization Script
Sets up project-specific configuration for Microsoft Fabric CI/CD framework
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ProjectInitializer:
    """Initialize project configuration for Fabric CI/CD"""

    def __init__(self):
        self.config_file = Path("project.config.json")
        self.environments = ["dev", "test", "prod"]

    def run(self):
        """Run the interactive project initialization"""
        print("\n" + "=" * 60)
        print("🚀 Microsoft Fabric CI/CD Project Initialization")
        print("=" * 60)
        print("\nThis wizard will help you set up project-specific configuration")
        print("to replace hardcoded values throughout the codebase.\n")

        if self.config_file.exists():
            if not self._confirm(f"{self.config_file} already exists. Overwrite?"):
                print("✅ Initialization cancelled.")
                return

        try:
            # Collect project information
            project_info = self._collect_project_info()

            # Collect Azure configuration
            azure_config = self._collect_azure_config()

            # Collect GitHub configuration
            github_config = self._collect_github_config()

            # Collect contact information
            contacts = self._collect_contacts()

            # Create configuration
            config = self._create_configuration(
                project_info, azure_config, github_config, contacts
            )

            # Save configuration
            self._save_configuration(config)

            # Update environment files
            self._update_environment_files(config)

            # Generate environment variables guide
            self._generate_env_vars_guide(config)

            print("\n✅ Project initialization completed successfully!")
            print("\n📋 Next steps:")
            print("1. Review and customize project.config.json")
            print("2. Set up environment variables (see .env.example)")
            print("3. Update CODEOWNERS file with your GitHub organization")
            print("4. Run: python -m ops.scripts.utilities.config_manager")

        except KeyboardInterrupt:
            print("\n\n❌ Initialization cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during initialization: {e}")
            sys.exit(1)

    def _collect_project_info(self) -> Dict[str, Any]:
        """Collect project information from user"""
        print("📝 Project Information")
        print("-" * 20)

        name = self._prompt(
            "Project name", "fabric-cicd", "A descriptive name for your project"
        )

        prefix = self._prompt(
            "Project prefix",
            "your-project",
            "Short prefix for resource naming (lowercase, hyphens allowed)",
        )

        # Validate prefix
        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", prefix):
            raise ValueError(
                "Project prefix must start and end with alphanumeric, contain only lowercase letters, numbers, and hyphens"
            )

        description = self._prompt(
            "Project description",
            "Microsoft Fabric CI/CD Implementation",
            "Brief description of the project",
        )

        organization = self._prompt(
            "Organization name",
            "your-org",
            "Your organization name (used in GitHub teams)",
        )

        return {
            "name": name,
            "prefix": prefix,
            "description": description,
            "organization": organization,
        }

    def _collect_azure_config(self) -> Dict[str, Any]:
        """Collect Azure configuration"""
        print("\n☁️  Azure Configuration")
        print("-" * 20)

        tenant_id = self._prompt(
            "Azure Tenant ID", "${AZURE_TENANT_ID}", "Your Azure AD tenant ID"
        )

        subscription_id = self._prompt(
            "Azure Subscription ID",
            "${AZURE_SUBSCRIPTION_ID}",
            "Target Azure subscription ID",
        )

        client_id = self._prompt(
            "Azure Client ID",
            "${AZURE_CLIENT_ID}",
            "Service Principal client ID for authentication",
        )

        return {
            "tenant_id": tenant_id,
            "subscription_id": subscription_id,
            "client_id": client_id,
            "resource_group_pattern": "{prefix}-fabric-{environment}-rg",
        }

    def _collect_github_config(self) -> Dict[str, Any]:
        """Collect GitHub configuration"""
        print("\n🐙 GitHub Configuration")
        print("-" * 20)

        organization = self._prompt(
            "GitHub Organization", "${GITHUB_ORG}", "Your GitHub organization name"
        )

        repository = self._prompt(
            "Repository name", "${GITHUB_REPO}", "GitHub repository name"
        )

        return {
            "organization": organization,
            "repository": repository,
            "teams": {
                "data": "{organization}/data-team",
                "bi": "{organization}/bi-team",
                "governance": "{organization}/governance-team",
                "integration": "{organization}/integration-team",
                "platform": "{organization}/platform-team",
                "devops": "{organization}/devops-team",
            },
        }

    def _collect_contacts(self) -> Dict[str, Any]:
        """Collect contact information"""
        print("\n📧 Contact Information")
        print("-" * 20)

        data_owner = self._prompt(
            "Data Owner Email", "${DATA_OWNER_EMAIL}", "Primary data owner contact"
        )

        technical_lead = self._prompt(
            "Technical Lead Email", "${TECHNICAL_LEAD_EMAIL}", "Technical lead contact"
        )

        devops_lead = self._prompt(
            "DevOps Lead Email", "${DEVOPS_LEAD_EMAIL}", "DevOps lead contact"
        )

        return {
            "data_owner": data_owner,
            "technical_lead": technical_lead,
            "devops_lead": devops_lead,
        }

    def _create_configuration(
        self,
        project_info: Dict[str, Any],
        azure_config: Dict[str, Any],
        github_config: Dict[str, Any],
        contacts: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create the complete configuration"""
        return {
            "project": project_info,
            "naming_patterns": {
                "workspace": "{prefix}-fabric-{environment}",
                "lakehouse": "{prefix_upper}_Lakehouse_{environment_title}",
                "storage_account": "{prefix_clean}data{environment}",
                "key_vault": "{prefix}-kv-{environment}",
                "data_gateway": "{prefix}-gateway-{environment}",
                "sql_server": "{prefix}-sql-{environment}.database.windows.net",
                "cosmos_db": "https://{prefix}-cosmos-{environment}.documents.azure.com:443/",
                "event_hub": "sb://{prefix}-eventhub-{environment}.servicebus.windows.net/",
                "service_bus": "sb://{prefix}-servicebus-{environment}.servicebus.windows.net/",
                "disaster_recovery_storage": "{prefix_clean}datadr",
            },
            "azure": azure_config,
            "environments": {
                "dev": {
                    "description": "Development environment",
                    "requires_approval": False,
                    "auto_deploy": True,
                },
                "test": {
                    "description": "Test/QA environment",
                    "requires_approval": True,
                    "auto_deploy": False,
                },
                "prod": {
                    "description": "Production environment",
                    "requires_approval": True,
                    "auto_deploy": False,
                    "additional_validations": True,
                },
            },
            "github": github_config,
            "contacts": contacts,
            "purview": {
                "collections": {
                    "dev": "{prefix}-dev",
                    "test": "{prefix}-qa",
                    "prod": "{prefix}-prod",
                }
            },
            "metadata": {
                "created_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "version": "1.0.0",
                "fabric_cicd_version": "2.0.0",
            },
        }

    def _save_configuration(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved to {self.config_file}")

    def _update_environment_files(self, config: Dict[str, Any]):
        """Update environment configuration files if they exist"""
        config_dir = Path("ops/config")
        if not config_dir.exists():
            return

        # Import ConfigManager to generate names
        try:
            from config_manager import ConfigManager

            ConfigManager(str(self.config_file))

            for env in self.environments:
                env_file = config_dir / f"{env}.json"
                if env_file.exists():
                    print(
                        f"📄 Environment file {env_file} will be updated automatically"
                    )

        except ImportError:
            print(
                "⚠️  ConfigManager not available - environment files need manual update"
            )

    def _generate_env_vars_guide(self, config: Dict[str, Any]):
        """Generate environment variables guide"""
        env_example = """# Microsoft Fabric CI/CD Environment Variables
# Copy this file to .env and update with your values

# Azure Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here

# GitHub Configuration  
GITHUB_ORG=your-github-org
GITHUB_REPO=your-repo-name

# Contact Information
DATA_OWNER_EMAIL=data-owner@yourcompany.com
TECHNICAL_LEAD_EMAIL=tech-lead@yourcompany.com
DEVOPS_LEAD_EMAIL=devops@yourcompany.com

# Environment-specific Fabric Capacity IDs
FABRIC_CAPACITY_DEV_ID=your-dev-capacity-id
FABRIC_CAPACITY_TEST_ID=your-test-capacity-id
FABRIC_CAPACITY_PROD_ID=your-prod-capacity-id

# Notification Settings (Optional)
DEV_TEAM_EMAIL=dev-team@yourcompany.com
TEST_TEAM_EMAIL=test-team@yourcompany.com
PROD_TEAM_EMAIL=prod-team@yourcompany.com

DEV_ALERTS_WEBHOOK=your-dev-teams-webhook
TEST_ALERTS_WEBHOOK=your-test-teams-webhook
PROD_ALERTS_WEBHOOK=your-prod-teams-webhook

TEST_PAGERDUTY_KEY=your-test-pagerduty-integration-key
PROD_PAGERDUTY_KEY=your-prod-pagerduty-integration-key
PROD_SLACK_WEBHOOK=your-prod-slack-webhook
"""

        with open(".env.example", "w") as f:
            f.write(env_example)

        print("✅ Generated .env.example with required environment variables")

    def _prompt(self, question: str, default: str = "", help_text: str = "") -> str:
        """Prompt user for input with optional default and help"""
        if help_text:
            print(f"💡 {help_text}")

        prompt = f"{question}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "

        response = input(prompt).strip()
        return response if response else default

    def _confirm(self, question: str) -> bool:
        """Ask for yes/no confirmation"""
        while True:
            response = input(f"{question} (y/N): ").strip().lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no", ""]:
                return False
            else:
                print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    initializer = ProjectInitializer()
    initializer.run()
