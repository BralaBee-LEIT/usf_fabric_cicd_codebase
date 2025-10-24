#!/usr/bin/env python3
"""
Domain-Based Workspace Setup with Existing Items

This scenario demonstrates:
1. Creating a logical domain structure (organizational pattern)
2. Creating a workspace within that domain context
3. Creating a NEW lakehouse and warehouse in the workspace
4. Referencing/linking to EXISTING lakehouses from other workspaces (via shortcuts)
5. Adding an additional new lakehouse

Domain Concept:
- In Fabric, "domains" are logical organizational units, not API resources
- We simulate domain structure through naming conventions and metadata
- Workspaces are organized by domain for governance and access control

Architecture:
- Domain: finance-analytics-domain (logical grouping)
- Workspace: finance-analytics-workspace
- Items:
  - finance_lakehouse (NEW)
  - finance_warehouse (NEW)  
  - additional_lakehouse (NEW)
  - Shortcuts to existing items from other workspaces (optional)

Usage:
    python scenarios/domain_workspace_with_existing_items.py \\
        --domain-name finance-analytics \\
        --capacity-id <capacity-guid> \\
        --principals-file my_team.txt \\
        --existing-lakehouse-workspace <workspace-id> \\
        --existing-lakehouse-name "SourceDataLakehouse"
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Add ops/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops" / "scripts"))

from utilities.workspace_manager import WorkspaceManager, WorkspaceRole
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.fabric_api import FabricClient
from utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
    console_table as print_table
)


class DomainWorkspaceSetup:
    """
    Setup manager for domain-based workspace with existing and new items
    
    This class demonstrates Fabric best practices for:
    - Domain-based organization (logical grouping)
    - Workspace creation within domain context
    - Creating new Fabric items
    - Referencing existing items from other workspaces
    """
    
    def __init__(
        self,
        domain_name: str,
        capacity_id: Optional[str] = None,
        principals_file: Optional[str] = None,
        existing_lakehouse_workspace: Optional[str] = None,
        existing_lakehouse_name: Optional[str] = None,
        existing_warehouse_workspace: Optional[str] = None,
        existing_warehouse_name: Optional[str] = None,
        skip_user_prompt: bool = False
    ):
        """
        Initialize domain workspace setup
        
        Args:
            domain_name: Logical domain name (e.g., 'finance-analytics', 'sales-ops')
            capacity_id: Fabric capacity GUID
            principals_file: Path to principals file for workspace access
            existing_lakehouse_workspace: Workspace ID containing existing lakehouse
            existing_lakehouse_name: Name of existing lakehouse to reference
            existing_warehouse_workspace: Workspace ID containing existing warehouse  
            existing_warehouse_name: Name of existing warehouse to reference
            skip_user_prompt: Skip interactive prompt for editing principals file (for automation)
        """
        self.domain_name = domain_name
        self.workspace_name = f"{domain_name}-workspace"
        self.workspace_id = None
        self.capacity_id = capacity_id
        self.principals_file = principals_file
        self.skip_user_prompt = skip_user_prompt
        
        # Existing items to reference
        self.existing_lakehouse_workspace = existing_lakehouse_workspace
        self.existing_lakehouse_name = existing_lakehouse_name
        self.existing_warehouse_workspace = existing_warehouse_workspace
        self.existing_warehouse_name = existing_warehouse_name
        
        # Managers
        self.workspace_mgr = WorkspaceManager()
        self.item_mgr = FabricItemManager()
        self.fabric_client = FabricClient()
        
        # Tracking
        self.created_items = []
        self.setup_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": self.domain_name,
            "workspace_name": self.workspace_name,
            "items_created": [],
            "items_referenced": [],
            "errors": []
        }
    
    def print_header(self, text: str):
        """Print section header"""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80)
    
    def step_1_create_domain_workspace(self):
        """Step 1: Create workspace within domain context"""
        self.print_header("STEP 1: Creating Domain-Based Workspace")
        
        print_info(f"Domain: {self.domain_name}-domain (logical grouping)")
        print_info(f"Workspace: {self.workspace_name}")
        
        if self.capacity_id:
            print_info(f"Capacity: {self.capacity_id}")
        
        try:
            # Create workspace
            workspace = self.workspace_mgr.create_workspace(
                name=self.workspace_name,
                description=f"Workspace for {self.domain_name} domain - Created {datetime.utcnow().strftime('%Y-%m-%d')}",
                capacity_id=self.capacity_id
            )
            
            self.workspace_id = workspace.get('id')
            
            print_success(f"✓ Workspace created: {self.workspace_name}")
            print_info(f"  ID: {self.workspace_id}")
            
            # Verify capacity
            if self.capacity_id:
                print_info("\nVerifying capacity assignment...")
                detail_response = self.fabric_client._make_request('GET', f'workspaces/{self.workspace_id}')
                detail = detail_response.json()
                assigned_capacity = detail.get('capacityId')
                
                if assigned_capacity == self.capacity_id:
                    print_success(f"✓ Capacity verified: {assigned_capacity}")
                else:
                    print_warning(f"⚠️  Capacity mismatch. Expected: {self.capacity_id}, Got: {assigned_capacity}")
            
            self.setup_log["workspace_id"] = self.workspace_id
            return True
            
        except Exception as e:
            print_error(f"Failed to create workspace: {str(e)}")
            self.setup_log["errors"].append(f"Workspace creation: {str(e)}")
            return False
    
    def step_2_create_primary_lakehouse(self):
        """Step 2: Create primary lakehouse for the domain"""
        self.print_header("STEP 2: Creating Primary Lakehouse")
        
        # Convert domain-name to CamelCase and follow BRONZE naming standard
        domain_camel = ''.join(word.capitalize() for word in self.domain_name.split('-'))
        lakehouse_name = f"BRONZE_{domain_camel}_Lakehouse"
        
        try:
            print_info(f"Creating lakehouse: {lakehouse_name}")
            
            lakehouse = self.item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name=lakehouse_name,
                item_type=FabricItemType.LAKEHOUSE,
                description=f"Primary data lakehouse for {self.domain_name} domain (Bronze tier - raw data)"
            )
            
            self.created_items.append(lakehouse)
            self.setup_log["items_created"].append({
                "type": "Lakehouse",
                "name": lakehouse.display_name,
                "id": lakehouse.id
            })
            
            print_success(f"✓ Created lakehouse: {lakehouse.display_name}")
            print_info(f"  ID: {lakehouse.id}")
            print_info(f"  Type: {lakehouse.type.value}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create lakehouse: {str(e)}")
            self.setup_log["errors"].append(f"Lakehouse creation: {str(e)}")
            return False
    
    def step_3_create_warehouse(self):
        """Step 3: Create warehouse for analytics"""
        self.print_header("STEP 3: Creating Analytics Warehouse")
        
        # Convert domain-name to CamelCase
        domain_camel = ''.join(word.capitalize() for word in self.domain_name.split('-'))
        warehouse_name = f"{domain_camel}Warehouse"
        
        try:
            print_info(f"Creating warehouse: {warehouse_name}")
            
            warehouse = self.item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name=warehouse_name,
                item_type=FabricItemType.WAREHOUSE,
                description=f"Analytics warehouse for {self.domain_name} domain"
            )
            
            self.created_items.append(warehouse)
            self.setup_log["items_created"].append({
                "type": "Warehouse",
                "name": warehouse.display_name,
                "id": warehouse.id
            })
            
            print_success(f"✓ Created warehouse: {warehouse.display_name}")
            print_info(f"  ID: {warehouse.id}")
            print_info(f"  Type: {warehouse.type.value}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create warehouse: {str(e)}")
            self.setup_log["errors"].append(f"Warehouse creation: {str(e)}")
            return False
    
    def step_4_create_additional_lakehouse(self):
        """Step 4: Create additional lakehouse"""
        self.print_header("STEP 4: Creating Additional Lakehouse")
        
        # Convert domain-name to CamelCase and follow SILVER naming standard for staging
        domain_camel = ''.join(word.capitalize() for word in self.domain_name.split('-'))
        additional_lakehouse_name = f"SILVER_{domain_camel}_Staging_Lakehouse"
        
        try:
            print_info(f"Creating additional lakehouse: {additional_lakehouse_name}")
            
            lakehouse = self.item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name=additional_lakehouse_name,
                item_type=FabricItemType.LAKEHOUSE,
                description=f"Staging lakehouse for {self.domain_name} domain (Silver tier - curated/staging data)"
            )
            
            self.created_items.append(lakehouse)
            self.setup_log["items_created"].append({
                "type": "Lakehouse",
                "name": lakehouse.display_name,
                "id": lakehouse.id
            })
            
            print_success(f"✓ Created additional lakehouse: {lakehouse.display_name}")
            print_info(f"  ID: {lakehouse.id}")
            print_info(f"  Type: {lakehouse.type.value}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create additional lakehouse: {str(e)}")
            self.setup_log["errors"].append(f"Additional lakehouse creation: {str(e)}")
            return False
    
    def step_5_reference_existing_items(self):
        """Step 5: Document references to existing items from other workspaces"""
        self.print_header("STEP 5: Referencing Existing Items")
        
        print_info("Note: Fabric doesn't 'attach' existing items to multiple workspaces.")
        print_info("Items belong to one workspace. To access data from other workspaces:")
        print_info("  1. Use Shortcuts in Lakehouses (recommended)")
        print_info("  2. Use cross-workspace queries in Warehouses/SQL Endpoints")
        print_info("  3. Copy/migrate items if needed")
        
        if self.existing_lakehouse_workspace and self.existing_lakehouse_name:
            print_info(f"\n📌 Existing Lakehouse Reference:")
            print_info(f"   Workspace: {self.existing_lakehouse_workspace}")
            print_info(f"   Lakehouse: {self.existing_lakehouse_name}")
            print_info(f"\n   To access this data:")
            print_info(f"   1. Open your new lakehouse in Fabric portal")
            print_info(f"   2. Right-click in Lakehouse Explorer → New shortcut")
            print_info(f"   3. Select 'OneLake' as source")
            print_info(f"   4. Navigate to workspace '{self.existing_lakehouse_workspace}'")
            print_info(f"   5. Select lakehouse '{self.existing_lakehouse_name}'")
            print_info(f"   6. Choose tables/files to create shortcuts for")
            
            self.setup_log["items_referenced"].append({
                "type": "Lakehouse",
                "name": self.existing_lakehouse_name,
                "workspace": self.existing_lakehouse_workspace,
                "access_method": "OneLake Shortcut"
            })
        
        if self.existing_warehouse_workspace and self.existing_warehouse_name:
            print_info(f"\n📌 Existing Warehouse Reference:")
            print_info(f"   Workspace: {self.existing_warehouse_workspace}")
            print_info(f"   Warehouse: {self.existing_warehouse_name}")
            print_info(f"\n   To query this warehouse:")
            print_info(f"   1. Use cross-workspace T-SQL queries")
            print_info(f"   2. Format: [workspace_name].[warehouse_name].[schema].[table]")
            print_info(f"   3. Example: SELECT * FROM [{self.existing_warehouse_workspace}].[{self.existing_warehouse_name}].[dbo].[Sales]")
            
            self.setup_log["items_referenced"].append({
                "type": "Warehouse",
                "name": self.existing_warehouse_name,
                "workspace": self.existing_warehouse_workspace,
                "access_method": "Cross-workspace T-SQL"
            })
        
        if not self.existing_lakehouse_workspace and not self.existing_warehouse_workspace:
            print_info("\nℹ️  No existing items specified to reference.")
            print_info("   Use --existing-lakehouse-workspace and --existing-lakehouse-name")
            print_info("   to reference existing items from other workspaces.")
        
        return True
    
    def step_6_configure_principals(self):
        """Step 6: Configure workspace access using core CLI"""
        self.print_header("STEP 6: Configuring Workspace Access")
        
        # Determine principals file
        config_dir = Path(__file__).parent.parent / "config"
        
        if self.principals_file:
            principals_file = Path(self.principals_file)
            print_info(f"Using provided principals file: {principals_file}")
        else:
            # Look for domain-specific file in config directory
            domain_file = config_dir / f"{self.domain_name}_principals.txt"
            if domain_file.exists():
                principals_file = domain_file
                print_info(f"Found existing principals file: config/{domain_file.name}")
            else:
                principals_file = None
        
        # If no file exists, create template and prompt user
        if not principals_file or not principals_file.exists():
            print_warning("No principals file found - creating template")
            
            # Create a template principals file for this domain in config directory
            template_path = config_dir / "workspace_principals.template.txt"
            domain_principals_path = config_dir / f"{self.domain_name}_principals.txt"
            
            if template_path.exists():
                import shutil
                shutil.copy(template_path, domain_principals_path)
                print_info(f"\n✓ Created template: config/{domain_principals_path.name}")
            else:
                # Create basic template if source doesn't exist
                with open(domain_principals_path, 'w') as f:
                    f.write("# Workspace Principals Configuration\n")
                    f.write("# Format: principal_id,role,description,type\n")
                    f.write("# Types: User, Group, ServicePrincipal\n")
                    f.write("# Roles: Admin, Member, Contributor, Viewer\n\n")
                    f.write("# Get Object IDs:\n")
                    f.write("# User:   az ad user show --id user@domain.com --query id -o tsv\n")
                    f.write("# Group:  az ad group show --group \"Team Name\" --query id -o tsv\n\n")
                    f.write("# Add your principals below:\n")
                print_info(f"\n✓ Created template: config/{domain_principals_path.name}")
            
            print_warning("\n⚠️  ACTION REQUIRED: Edit the principals file")
            print_info(f"\nPlease edit: config/{domain_principals_path.name}")
            print_info("Add your users/groups (Object IDs from Azure AD)\n")
            print_info("Example:")
            print_info("  # Get user Object ID:")
            print_info("  az ad user show --id user@domain.com --query id -o tsv")
            print_info("  # Add to file:")
            print_info("  a1b2c3d4-e5f6-...,Admin,Workspace Administrator,User\n")
            
            # Prompt user to edit file (unless skipped for automation)
            if self.skip_user_prompt:
                print_warning("\n⚠️  Skipped user configuration (--skip-user-prompt) - workspace has NO users!")
                print_info(f"To add users later, run:")
                print_info(f"  python ops/scripts/manage_workspaces.py add-users-from-file {self.workspace_id} config/{domain_principals_path.name}")
                self.setup_log["principals_configured"] = False
                self.setup_log["principals_file_created"] = str(domain_principals_path)
                return True
            
            print()
            print_warning("═" * 70)
            print_warning("⏸️  PAUSED - Edit the file above to add users")
            print_warning("═" * 70)
            response = input("\n✏️  Press ENTER after you've edited the file (or 's' to skip): ").strip().lower()
            print_warning("═" * 70)
            print()
            
            if response == 's':
                print_warning("\n⚠️  Skipped user configuration - workspace has NO users!")
                print_info(f"To add users later, run:")
                print_info(f"  python ops/scripts/manage_workspaces.py add-users-from-file {self.workspace_id} config/{domain_principals_path.name}")
                self.setup_log["principals_configured"] = False
                self.setup_log["principals_file_created"] = str(domain_principals_path)
                return True
            
            # User edited the file, use it
            principals_file = domain_principals_path
        
        print_info(f"Using principals file: {principals_file.name}")
        
        # Check if principals file has actual users (not just comments/examples)
        has_valid_users = False
        try:
            with open(principals_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Check if it looks like a valid GUID (basic check)
                        parts = line.split(',')
                        if len(parts) >= 4 and '-' in parts[0]:
                            has_valid_users = True
                            break
        except Exception as e:
            print_warning(f"Could not read principals file: {str(e)}")
        
        if not has_valid_users:
            print_warning("\n⚠️  Principals file has no valid users yet")
            print_info("The template was created but you need to add actual user/group Object IDs")
            self.setup_log["principals_configured"] = False
            return True
        
        try:
            cli_script = Path(__file__).parent.parent / "ops" / "scripts" / "manage_workspaces.py"
            
            # Add principals using core CLI
            print_info("\nAdding principals to workspace (using core CLI)...")
            add_cmd = [
                sys.executable,
                str(cli_script),
                "add-users-from-file",
                self.workspace_id,
                str(principals_file),
                "--yes"
            ]
            
            add_result = subprocess.run(
                add_cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            
            # Show output (filter logging)
            if add_result.stdout:
                for line in add_result.stdout.split('\n'):
                    if line.strip() and not line.startswith('INFO:'):
                        print(line)
            
            if add_result.returncode != 0:
                print_error(f"Failed to add principals: {add_result.stderr}")
                self.setup_log["principals_configured"] = False
                return False
            
            self.setup_log["principals_configured"] = True
            print_success("\n✓ Workspace access configured")
            return True
            
        except Exception as e:
            print_error(f"Failed to configure principals: {str(e)}")
            self.setup_log["errors"].append(f"Principal configuration: {str(e)}")
            self.setup_log["principals_configured"] = False
            return False
    
    def step_7_generate_summary(self):
        """Step 7: Generate setup summary"""
        self.print_header("SETUP COMPLETE - Summary")
        
        print_success("✓ Domain Workspace Setup Successful!\n")
        print(f"Domain:           {self.domain_name}-domain (logical)")
        print(f"Workspace:        {self.workspace_name}")
        print(f"Workspace ID:     {self.workspace_id}")
        if self.capacity_id:
            print(f"Capacity ID:      {self.capacity_id}")
        
        self.print_header("")
        
        print("📊 Items Created:\n")
        if self.created_items:
            for item in self.created_items:
                print(f"  ✓ {item.type.value}: {item.display_name}")
        else:
            print("  No items created")
        
        if self.setup_log["items_referenced"]:
            print("\n📌 Items Referenced (from other workspaces):\n")
            for ref in self.setup_log["items_referenced"]:
                print(f"  → {ref['type']}: {ref['name']}")
                print(f"    Workspace: {ref['workspace']}")
                print(f"    Access: {ref['access_method']}")
        
        self.print_header("")
        
        # Check if users were configured
        if self.setup_log.get("principals_configured"):
            print("✅ Workspace Access: Configured\n")
        else:
            print_warning("⚠️  IMPORTANT: Workspace Access Not Configured!\n")
            print("The workspace has been created but has NO users assigned.")
            print("You MUST add users before the workspace can be used.\n")
            if self.setup_log.get("principals_file_created"):
                principals_path = Path(self.setup_log['principals_file_created'])
                print(f"📝 Template created: config/{principals_path.name}\n")
                print("   Next step: Add your users/groups to this file")
        
        print("📝 Next Steps:\n")
        
        # Prioritize user addition if not configured
        if not self.setup_log.get("principals_configured"):
            principals_path = Path(self.setup_log.get('principals_file_created', ''))
            print("  🔴 PRIORITY: Add users to workspace")
            print(f"     1. Edit: config/{principals_path.name if principals_path.name else f'{self.domain_name}_principals.txt'}")
            print("     2. Add principals (Object IDs from Azure AD)")
            print("     3. Run: python ops/scripts/manage_workspaces.py add-users-from-file \\")
            print(f"             {self.workspace_id} \\")
            print(f"             config/{principals_path.name if principals_path.name else f'{self.domain_name}_principals.txt'}")
            print("")
        
        print("  2. Create OneLake shortcuts to access existing lakehouse data:")
        print(f"     - Open '{self.domain_name}-lakehouse' in Fabric portal")
        print("     - Create shortcuts to source data")
        print("  3. Set up data pipelines for ETL processes")
        print("  4. Create notebooks for data transformation")
        print("  5. Build semantic models for reporting")
        print("  6. Design Power BI dashboards")
        
        # Save log
        log_file = Path(__file__).parent / f"{self.domain_name}_setup_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.setup_log, f, indent=2)
        
        print(f"\n📄 Setup log saved: {log_file}")
        
        return True
    
    def run(self):
        """Execute the complete setup"""
        self.print_header(f"Domain Workspace Setup: {self.domain_name}")
        
        print(f"\nDomain: {self.domain_name}-domain")
        print(f"Workspace: {self.workspace_name}")
        if self.capacity_id:
            print(f"Capacity: {self.capacity_id}")
        
        print("\nThis will create:")
        print("  - 1 Workspace (within domain context)")
        print("  - 1 Primary Lakehouse")
        print("  - 1 Analytics Warehouse")
        print("  - 1 Additional Lakehouse (staging)")
        if self.existing_lakehouse_workspace:
            print(f"  - Reference to existing lakehouse (via shortcuts)")
        
        self.print_header("")
        
        # Execute steps
        steps = [
            ("Create Domain Workspace", self.step_1_create_domain_workspace),
            ("Create Primary Lakehouse", self.step_2_create_primary_lakehouse),
            ("Create Warehouse", self.step_3_create_warehouse),
            ("Create Additional Lakehouse", self.step_4_create_additional_lakehouse),
            ("Reference Existing Items", self.step_5_reference_existing_items),
            ("Configure Workspace Access", self.step_6_configure_principals),
            ("Generate Summary", self.step_7_generate_summary)
        ]
        
        for step_name, step_func in steps:
            print_info(f"\nExecuting: {step_name}...")
            if not step_func():
                print_error(f"Setup failed at step: {step_name}")
                return 1
        
        print_success("\n🎉 Domain workspace setup completed successfully!")
        return 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Domain-Based Workspace Setup with Existing and New Items",
        epilog="Example: python domain_workspace_with_existing_items.py --domain-name finance-analytics --capacity-id abc123"
    )
    parser.add_argument(
        '--domain-name',
        required=True,
        help='Domain name (e.g., finance-analytics, sales-ops)'
    )
    parser.add_argument(
        '--capacity-id',
        help='Fabric Capacity ID (GUID). If not provided, will use trial capacity.'
    )
    parser.add_argument(
        '--principals-file',
        help='Path to principals file (users/groups). If not provided, looks for <domain>_principals.txt'
    )
    parser.add_argument(
        '--existing-lakehouse-workspace',
        help='Workspace ID containing existing lakehouse to reference'
    )
    parser.add_argument(
        '--existing-lakehouse-name',
        help='Name of existing lakehouse to reference'
    )
    parser.add_argument(
        '--existing-warehouse-workspace',
        help='Workspace ID containing existing warehouse to reference'
    )
    parser.add_argument(
        '--existing-warehouse-name',
        help='Name of existing warehouse to reference'
    )
    parser.add_argument(
        '--skip-user-prompt',
        action='store_true',
        help='Skip interactive prompt for editing principals file (for automation)'
    )
    
    args = parser.parse_args()
    
    setup = DomainWorkspaceSetup(
        domain_name=args.domain_name,
        capacity_id=args.capacity_id,
        principals_file=args.principals_file,
        existing_lakehouse_workspace=args.existing_lakehouse_workspace,
        existing_lakehouse_name=args.existing_lakehouse_name,
        existing_warehouse_workspace=args.existing_warehouse_workspace,
        existing_warehouse_name=args.existing_warehouse_name,
        skip_user_prompt=args.skip_user_prompt
    )
    
    exit_code = setup.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
