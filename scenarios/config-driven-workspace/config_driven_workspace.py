#!/usr/bin/env python3
"""
Config-Driven Workspace Provisioning Scenario

This scenario demonstrates the enterprise config-driven approach using project.config.json
for standardized, organization-wide naming patterns.

Key Differences from Direct-Name Scenarios:
- Uses project.config.json for naming patterns
- Generates workspace names automatically: {prefix}-{project}-{environment}
- Enforces organization-wide naming standards
- Suitable for large enterprises with governance requirements

Usage:
    python config_driven_workspace.py --project "analytics" --environment "dev"
    
    This creates workspace: usf2-fabric-analytics-dev (based on project.config.json)

Compare to Direct-Name Approach:
    python ../domain-workspace/domain_workspace_with_existing_items.py --workspace-name "analytics"
    
    This creates workspace: analytics (exact name provided)
"""

import sys
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add ops/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops" / "scripts"))

from utilities.workspace_manager import WorkspaceManager
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.config_manager import ConfigManager


class ConfigDrivenWorkspace:
    """
    Config-driven workspace provisioning using project.config.json patterns
    """
    
    def __init__(
        self,
        project_name: str,
        environment: str,
        capacity_id: Optional[str] = None,
        principals_file: Optional[str] = None,
        skip_user_prompt: bool = False
    ):
        """
        Initialize config-driven workspace setup
        
        Args:
            project_name: Project name (e.g., "analytics", "finance")
            environment: Environment (dev, test, prod)
            capacity_id: Optional Fabric capacity ID (required for lakehouse/warehouse creation)
            principals_file: Optional path to principals file
            skip_user_prompt: Skip user addition prompt for automation
        """
        self.project_name = project_name
        self.environment = environment
        self.capacity_id = capacity_id
        self.principals_file = principals_file
        self.skip_user_prompt = skip_user_prompt
        
        # Load configuration
        self.config_manager = ConfigManager()
        
        # Generate standardized workspace name from config
        self.workspace_name = self.config_manager.generate_name(
            "workspace",
            self.environment,
            name=self.project_name
        )
        
        # Initialize managers with environment
        self.workspace_mgr = WorkspaceManager(environment=self.environment)
        self.workspace_id = None
        self.created_items = []
        
        # Setup log directory - use config/setup-logs/
        config_base = Path(__file__).parent.parent.parent / "config"
        self.log_dir = config_base / "setup-logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{self.project_name}_{self.environment}_setup_log.json"
        
        print(f"\n{'='*70}")
        print("  Config-Driven Workspace Provisioning")
        print(f"{'='*70}")
        print("\n📋 Configuration:")
        print(f"   Project Name:    {self.project_name}")
        print(f"   Environment:     {self.environment}")
        print(f"   Workspace Name:  {self.workspace_name} (generated from config)")
        print(f"   Config Prefix:   {self.config_manager.config['project']['prefix']}")
        print(f"   Naming Pattern:  {self.config_manager.get_naming_pattern('workspace')}")
        print(f"\n{'='*70}\n")
    
    def step_1_create_workspace(self):
        """Create workspace using config-driven naming"""
        print(f"{'='*70}")
        print("  STEP 1: Creating Workspace (Config-Driven)")
        print(f"{'='*70}\n")
        
        env_config = self.config_manager.get_environment_config(self.environment)
        description = f"{self.project_name.title()} workspace - {env_config.get('description', '')}"
        
        print(f"ℹ Creating workspace '{self.workspace_name}'...")
        print(f"   Description: {description}")
        print(f"   Auto-deploy: {env_config.get('auto_deploy', False)}")
        print(f"   Requires approval: {env_config.get('requires_approval', False)}")
        if self.capacity_id:
            print(f"   Capacity ID: {self.capacity_id}")
        else:
            print("   ⚠️  No capacity ID - using Trial (lakehouse creation will fail)")
        print()
        
        try:
            result = self.workspace_mgr.create_workspace(
                name=self.project_name,  # Base name - will be expanded by config
                description=description,
                capacity_id=self.capacity_id
            )
            
            self.workspace_id = result['id']
            print("✓ Workspace created successfully")
            print(f"  Workspace ID: {self.workspace_id}")
            print(f"  Display Name: {result.get('displayName', 'N/A')}")
            print(f"  Type: {result.get('type', 'N/A')}\n")
            
        except ValueError as e:
            # Workspace already exists - fetch it
            if "already exists" in str(e):
                print("⚠️  Workspace already exists, retrieving existing workspace...")
                existing_workspace = self.workspace_mgr.get_workspace_by_name(self.workspace_name)
                
                if existing_workspace:
                    self.workspace_id = existing_workspace.get('id')
                    print(f"✓ Using existing workspace '{self.workspace_name}'")
                    print(f"  Workspace ID: {self.workspace_id}")
                    print(f"  Display Name: {existing_workspace.get('displayName', 'N/A')}")
                    print(f"  Type: {existing_workspace.get('type', 'N/A')}\n")
                else:
                    print("❌ Failed to retrieve existing workspace")
                    raise
            else:
                print(f"❌ Failed to create workspace: {str(e)}")
                raise
        except Exception as e:
            print(f"❌ Failed to create workspace: {str(e)}")
            raise
    
    def step_2_create_items(self):
        """Step 2: Create lakehouse and warehouse items"""
        print("\n" + "=" * 70)
        print("  STEP 2: Creating Fabric Items")
        print("=" * 70)
        print()
        
        # Initialize item manager
        item_mgr = FabricItemManager()
        
        try:
            # Create Lakehouse with proper naming (BRONZE tier for raw data)
            lakehouse_name = f"BRONZE_{self.project_name.capitalize()}_Lakehouse"
            print(f"ℹ Creating lakehouse: {lakehouse_name}")
            lakehouse = item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name=lakehouse_name,
                item_type=FabricItemType.LAKEHOUSE,
                description=f"{self.project_name.capitalize()} raw data lakehouse - {self.environment.upper()} environment"
            )
            print(f"✓ Created lakehouse: {lakehouse.display_name} (ID: {lakehouse.id})")
        except Exception as e:
            if "403" in str(e) or "FeatureNotAvailable" in str(e):
                print("❌ Lakehouse creation failed: 403 Forbidden")
                print("   This usually means:")
                print("   1. The capacity ID is invalid or inaccessible")
                print("   2. The service principal lacks permissions on the capacity")
                print("   3. The workspace isn't properly assigned to the capacity")
            else:
                print(f"❌ Failed to create lakehouse: {e}")
                raise
        
        # Create Warehouse (optional - uncomment if needed)
        # warehouse_name = f"{self.project_name.capitalize()}Warehouse{self.environment.capitalize()}"
        # print(f"\nℹ Creating warehouse: {warehouse_name}")
        # try:
        #     warehouse = item_mgr.create_item(
        #         workspace_id=self.workspace_id,
        #         display_name=warehouse_name,
        #         item_type=FabricItemType.WAREHOUSE,
        #         description=f"{self.project_name.capitalize()} warehouse - {self.environment.upper()} environment"
        #     )
        #     print(f"✓ Created warehouse: {warehouse.display_name} (ID: {warehouse.id})")
        # except Exception as e:
        #     if "403" in str(e):
        #         print("❌ Warehouse creation failed: 403 Forbidden (see lakehouse error above)")
        #     else:
        #         print(f"❌ Failed to create warehouse: {e}")
        #         raise
    
    def step_3_configure_principals(self):
        """Configure workspace principals (users/groups)"""
        print(f"{'='*70}")
        print("  STEP 3: Configuring Workspace Principals")
        print(f"{'='*70}\n")
        
        if not self.workspace_id:
            print("⚠️ No workspace ID available")
            return
        
        # Use config/principals/ subdirectory
        config_dir = Path(__file__).parent.parent.parent / "config"
        principals_dir = config_dir / "principals"
        principals_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if principals file provided
        if self.principals_file:
            principals_file = Path(self.principals_file)
            if not principals_file.exists():
                print(f"❌ Principals file not found: {self.principals_file}")
                return
            print(f"Using provided principals file: {principals_file.name}")
        else:
            # Create or use existing principals file in config/principals/
            principals_filename = f"{self.project_name}_{self.environment}_principals.txt"
            principals_file = principals_dir / principals_filename
            
            # Check if file already exists with users
            if principals_file.exists():
                print(f"Found existing principals file: {principals_file.name}")
            else:
                # Create template
                print(f"📝 Creating principals template: {principals_file}")
                template_source = principals_dir / "workspace_principals.template.txt"
                
                if template_source.exists():
                    import shutil
                    shutil.copy(template_source, principals_file)
                    print(f"  ✓ Template created from {template_source.name}\n")
                else:
                    # Create basic template
                    principals_file.write_text(
                        "# Principals file for workspace\n"
                        "# Format: principal_id,role,description,type\n"
                        "# Example: 9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Administrator,User\n\n"
                    )
                    print("  ✓ Basic template created\n")
                
                # Prompt user to edit (unless automation mode)
                if not self.skip_user_prompt:
                    print("✏️  Please edit the principals file:")
                    print(f"   {principals_file}\n")
                    print("   Add user/group Object IDs (not emails!)\n")
                    
                    print("   " + "─" * 60)
                    print("   ⏸️  PAUSED - Edit the file above to add users")
                    print("   " + "─" * 60)
                    response = input("   👉 Press ENTER after editing (or 's' to skip): ").strip().lower()
                    print("   " + "─" * 60 + "\n")
                    
                    if response == 's':
                        print("   ⏩ Skipping user addition\n")
                        return
                else:
                    print("   ⏩ Skipping user prompt (automation mode)")
                    print("   If file has valid users, they will be added automatically\n")
        
        # Check if file has valid users (not just comments)
        try:
            content = principals_file.read_text()
            lines = [line.strip() for line in content.split('\n') 
                     if line.strip() and not line.startswith('#')]
            
            if not lines:
                print("⚠️  No valid users found in principals file")
                print(f"   Template created at: {principals_file}")
                print("   Edit it and add users, then run:")
                print(f"   python ops/scripts/manage_workspaces.py add-users-from-file {self.workspace_id} {principals_file} --yes\n")
                return
            
            # Validate at least one line looks like a GUID
            has_valid_format = False
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 4 and '-' in parts[0] and len(parts[0]) > 30:
                    has_valid_format = True
                    break
            
            if not has_valid_format:
                print("⚠️  No valid user entries found (lines don't match expected format)")
                print("   Expected format: principal_id,role,description,type")
                print("   Example: abc123-def456-...,Admin,Administrator,User\n")
                return
                
        except Exception as e:
            print(f"⚠️  Could not read principals file: {e}\n")
            return
        
        # Add users via core CLI
        print(f"📤 Adding {len(lines)} principal(s) from: {principals_file.name}")
        cli_script = Path(__file__).parent.parent.parent / "ops" / "scripts" / "manage_workspaces.py"
        python = sys.executable
        
        try:
            result = subprocess.run(
                [python, str(cli_script), "add-users-from-file", 
                 self.workspace_id, str(principals_file), "--yes"],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Show output (filter out INFO logs)
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('INFO:'):
                        print(line)
            
            if result.returncode == 0:
                print("✓ Principals configured successfully\n")
            else:
                print("⚠️  Some principals may have failed to add")
                if result.stderr:
                    print(f"   Error details: {result.stderr}\n")
                    
        except Exception as e:
            print(f"❌ Failed to add principals: {e}\n")
    
    def step_4_save_log(self):
        """Save setup log"""
        print(f"{'='*70}")
        print("  STEP 4: Saving Setup Log")
        print(f"{'='*70}\n")
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "project_name": self.project_name,
            "environment": self.environment,
            "workspace_name": self.workspace_name,
            "workspace_id": self.workspace_id,
            "config_pattern": self.config_manager.get_naming_pattern('workspace'),
            "config_prefix": self.config_manager.config['project']['prefix'],
            "created_items": self.created_items,
            "principals_file": str(self.principals_file) if self.principals_file else None
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"✓ Log saved to: {self.log_file}\n")
    
    def run(self):
        """Execute the complete setup"""
        try:
            self.step_1_create_workspace()
            self.step_2_create_items()
            self.step_3_configure_principals()
            self.step_4_save_log()
            
            print(f"{'='*70}")
            print("  ✅ Setup Complete!")
            print(f"{'='*70}\n")
            print("📊 Summary:")
            print(f"   Workspace: {self.workspace_name}")
            print(f"   ID: {self.workspace_id}")
            print(f"   Items: {len(self.created_items)}")
            print(f"   URL: https://app.fabric.microsoft.com/groups/{self.workspace_id}\n")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Config-Driven Workspace Provisioning (uses project.config.json)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create dev environment for analytics project (Trial workspace)
  python config_driven_workspace.py --project analytics --environment dev
  
  # Create with capacity for lakehouse/warehouse creation
  python config_driven_workspace.py --project analytics --environment dev \\
    --capacity-id <your-capacity-guid>
  
  # Create prod environment with capacity and principals file
  python config_driven_workspace.py --project finance --environment prod \\
    --capacity-id <your-capacity-guid> \\
    --principals-file ../../config/finance_prod_principals.txt
  
  # Automation mode (skip prompts)
  python config_driven_workspace.py --project sales --environment test \\
    --capacity-id <your-capacity-guid> --skip-user-prompt

Note: Without --capacity-id, workspace uses Trial capacity (lakehouse creation will fail)

Generated Workspace Names (from project.config.json):
  analytics + dev  → usf2-fabric-analytics-dev
  finance + prod   → usf2-fabric-finance-prod
  sales + test     → usf2-fabric-sales-test
        """
    )
    
    parser.add_argument(
        "--project",
        required=True,
        help="Project name (will be combined with config prefix and environment)"
    )
    
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "test", "prod"],
        help="Target environment"
    )
    
    parser.add_argument(
        "--capacity-id",
        help="Fabric capacity ID (required for creating lakehouses/warehouses)"
    )
    
    parser.add_argument(
        "--principals-file",
        help="Path to principals file (if not provided, template will be created)"
    )
    
    parser.add_argument(
        "--skip-user-prompt",
        action="store_true",
        help="Skip user addition prompt (for automation/CI-CD)"
    )
    
    args = parser.parse_args()
    
    # Check if project.config.json exists
    config_file = Path("project.config.json")
    if not config_file.exists():
        print("\n❌ project.config.json not found!")
        print("\nThis scenario requires project.config.json for naming patterns.")
        print("Please run: python setup/init_project_config.py")
        print("\nAlternatively, use the direct-name scenario:")
        print("  python scenarios/domain-workspace/domain_workspace_with_existing_items.py")
        sys.exit(1)
    
    scenario = ConfigDrivenWorkspace(
        project_name=args.project,
        environment=args.environment,
        capacity_id=args.capacity_id,
        principals_file=args.principals_file,
        skip_user_prompt=args.skip_user_prompt
    )
    
    scenario.run()


if __name__ == "__main__":
    main()
