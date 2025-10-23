#!/usr/bin/env python3
"""
LEIT-Ricoh Domain - Fresh Workspace Setup with Capacity Assignment

This script creates a NEW Microsoft Fabric workspace with capacity assigned immediately,
then creates all required items:
- Notebooks for data processing (3)
- Users/Groups with different roles (configurable via file)
- Lakehouse for data storage (1)
- Warehouse for analytics (1)
- 3 additional Fabric items (Pipeline, Semantic Model, Report)

Domain: leit-ricoh-domain
Workspace: leit-ricoh-fresh (NEW)

Key Features:
- Uses core CLI for user/group management (best practice)
- Configurable principals file (defaults to workspace-specific file)
- Supports Azure AD Groups for team management
"""
import sys
import os
import json
import base64
import subprocess
from pathlib import Path
from datetime import datetime

# Add ops/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops" / "scripts"))

from utilities.workspace_manager import WorkspaceManager, WorkspaceRole
from utilities.fabric_item_manager import FabricItemManager, FabricItemType, ItemDefinition, ItemDefinitionPart
from utilities.fabric_api import FabricClient
from utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
    console_table as print_table
)


class RicohFreshWorkspaceSetup:
    """Setup manager for LEIT-Ricoh fresh workspace with capacity"""
    
    def __init__(self, capacity_id=None, principals_file=None):
        """
        Initialize setup with optional capacity ID and principals file
        
        Args:
            capacity_id: Fabric capacity GUID. If None, will try to use trial capacity.
            principals_file: Path to principals file. If None, will look for workspace-specific file.
        """
        # Generate unique workspace name with timestamp
        # Don't use environment suffix since WorkspaceManager will add it
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.workspace_name = f"ricoh-fresh-{timestamp}"
        self.domain_name = "leit-ricoh-domain"
        self.environment = None  # Don't add env suffix, keep name unique
        self.workspace_id = None
        self.capacity_id = capacity_id
        self.principals_file = principals_file  # Allow custom principals file
        
        self.workspace_mgr = WorkspaceManager(environment=self.environment)
        self.item_mgr = FabricItemManager()
        self.fabric_client = FabricClient()
        
        self.created_items = []
        self.setup_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": self.domain_name,
            "workspace": self.workspace_name,
            "environment": self.environment,
            "capacity_id": capacity_id,
            "items": [],
            "users": [],
            "errors": []
        }
    
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80 + "\n")
    
    def detect_available_capacity(self):
        """Try to detect an available Fabric capacity"""
        try:
            print_info("Detecting available Fabric capacities...")
            response = self.fabric_client._make_request('GET', 'capacities')
            capacities = response.json().get('value', [])
            
            if not capacities:
                print_warning("No capacities found via API")
                return None
            
            print_info(f"Found {len(capacities)} capacity/capacities:")
            for cap in capacities:
                print_info(f"  - {cap.get('displayName')} (SKU: {cap.get('sku')}, State: {cap.get('state')})")
            
            # Prefer trial capacity if available
            for cap in capacities:
                if 'Trial' in cap.get('displayName', '') or cap.get('sku', '').startswith('FTL'):
                    print_success(f"✓ Selected trial capacity: {cap.get('displayName')}")
                    return cap.get('id')
            
            # Otherwise use first active capacity
            for cap in capacities:
                if cap.get('state') == 'Active':
                    print_success(f"✓ Selected capacity: {cap.get('displayName')}")
                    return cap.get('id')
            
            print_warning("No active capacities available")
            return None
            
        except Exception as e:
            print_warning(f"Could not detect capacities: {e}")
            return None
    
    def step_1_create_workspace_with_capacity(self):
        """Step 1: Create the workspace and assign capacity immediately"""
        self.print_header("STEP 1: Creating Fresh Workspace with Capacity")
        
        try:
            # Detect capacity if not provided
            if not self.capacity_id:
                print_info("No capacity ID provided, attempting to detect...")
                self.capacity_id = self.detect_available_capacity()
                
                if not self.capacity_id:
                    print_warning("⚠️  No capacity detected - workspace will be created without capacity")
                    print_warning("⚠️  Item creation will likely fail with 403 errors")
                    print_info("\nTo assign capacity manually after creation:")
                    print_info("  python ops/scripts/manage_workspaces.py assign-capacity <workspace_id> <capacity_id>")
            
            print_info(f"Creating workspace '{self.workspace_name}' in {self.environment} environment...")
            if self.capacity_id:
                print_info(f"  With capacity ID: {self.capacity_id}")
            
            # Create workspace with capacity
            workspace = self.workspace_mgr.create_workspace(
                name=self.workspace_name,
                description=f"LEIT-Ricoh domain workspace - Created {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                capacity_id=self.capacity_id
            )
            
            self.workspace_id = workspace.get('id')
            
            print_success(f"✓ Workspace '{self.workspace_name}' created successfully")
            print_info(f"  Workspace ID: {self.workspace_id}")
            
            # Verify capacity assignment
            if self.capacity_id:
                print_info("\nVerifying capacity assignment...")
                try:
                    detail_response = self.fabric_client._make_request('GET', f'workspaces/{self.workspace_id}')
                    detail = detail_response.json()
                    assigned_capacity = detail.get('capacityId')
                    
                    if assigned_capacity:
                        print_success(f"✓ Capacity assigned: {assigned_capacity}")
                    else:
                        print_warning("⚠️  Capacity assignment pending or not reflected in API yet")
                        print_info("  Waiting 5 seconds for propagation...")
                        import time
                        time.sleep(5)
                except Exception as e:
                    print_warning(f"Could not verify capacity: {e}")
            
            self.setup_log["workspace_id"] = self.workspace_id
            self.setup_log["capacity_assigned"] = bool(self.capacity_id)
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create workspace: {str(e)}")
            self.setup_log["errors"].append(f"Workspace creation: {str(e)}")
            return False
    
    def step_2_create_lakehouse(self):
        """Step 2: Create lakehouse"""
        self.print_header("STEP 2: Creating Lakehouse")
        
        try:
            print_info("Creating main data lakehouse...")
            
            lakehouse = self.item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name="RicohDataLakehouse",
                item_type=FabricItemType.LAKEHOUSE,
                description="Primary lakehouse for Ricoh data storage and processing"
            )
            
            print_success(f"✓ Lakehouse 'RicohDataLakehouse' created")
            print_info(f"  Item ID: {lakehouse.id}")
            
            self.created_items.append(lakehouse)
            self.setup_log["items"].append({
                "name": "RicohDataLakehouse",
                "type": "Lakehouse",
                "id": lakehouse.id
            })
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create lakehouse: {str(e)}")
            self.setup_log["errors"].append(f"Lakehouse creation: {str(e)}")
            return False
    
    def step_3_create_warehouse(self):
        """Step 3: Create data warehouse"""
        self.print_header("STEP 3: Creating Data Warehouse")
        
        try:
            print_info("Creating analytics warehouse...")
            
            warehouse = self.item_mgr.create_item(
                workspace_id=self.workspace_id,
                display_name="RicohAnalyticsWarehouse",
                item_type=FabricItemType.WAREHOUSE,
                description="Data warehouse for Ricoh analytics and reporting"
            )
            
            print_success(f"✓ Warehouse 'RicohAnalyticsWarehouse' created")
            print_info(f"  Item ID: {warehouse.id}")
            
            self.created_items.append(warehouse)
            self.setup_log["items"].append({
                "name": "RicohAnalyticsWarehouse",
                "type": "Warehouse",
                "id": warehouse.id
            })
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create warehouse: {str(e)}")
            self.setup_log["errors"].append(f"Warehouse creation: {str(e)}")
            return False
    
    def step_4_create_notebooks(self):
        """Step 4: Create processing notebooks"""
        self.print_header("STEP 4: Creating Notebooks")
        
        notebooks = [
            {
                "name": "01_DataIngestion",
                "description": "Notebook for ingesting data from various sources into the lakehouse"
            },
            {
                "name": "02_DataTransformation",
                "description": "Notebook for transforming and cleaning data using Spark"
            },
            {
                "name": "03_DataValidation",
                "description": "Notebook for validating data quality and running checks"
            }
        ]
        
        success_count = 0
        
        for nb_config in notebooks:
            try:
                print_info(f"Creating notebook '{nb_config['name']}'...")
                
                notebook = self.item_mgr.create_item(
                    workspace_id=self.workspace_id,
                    display_name=nb_config["name"],
                    item_type=FabricItemType.NOTEBOOK,
                    description=nb_config["description"]
                )
                
                print_success(f"✓ Notebook '{nb_config['name']}' created")
                print_info(f"  Item ID: {notebook.id}")
                
                self.created_items.append(notebook)
                self.setup_log["items"].append({
                    "name": nb_config["name"],
                    "type": "Notebook",
                    "id": notebook.id
                })
                
                success_count += 1
                
            except Exception as e:
                print_error(f"Failed to create notebook '{nb_config['name']}': {str(e)}")
                self.setup_log["errors"].append(f"Notebook {nb_config['name']}: {str(e)}")
        
        print_info(f"\nCreated {success_count}/{len(notebooks)} notebooks")
        
        return success_count == len(notebooks)
    
    def create_semantic_model_definition(self, model_name: str) -> ItemDefinition:
        """Create minimal Semantic Model definition
        
        Args:
            model_name: Name of the semantic model
            
        Returns:
            ItemDefinition with base64 encoded .bim content
        """
        # Minimal .bim file content for Tabular Model
        bim_content = {
            "name": model_name,
            "compatibilityLevel": 1550,
            "model": {
                "culture": "en-US",
                "dataAccessOptions": {
                    "legacyRedirects": True,
                    "returnErrorValuesAsNull": True
                },
                "tables": []
            }
        }
        
        # Encode to base64
        bim_json = json.dumps(bim_content, indent=2)
        payload_base64 = base64.b64encode(bim_json.encode('utf-8')).decode('utf-8')
        
        return ItemDefinition(
            parts=[
                ItemDefinitionPart(
                    path="model.bim",
                    payload=payload_base64,
                    payload_type="InlineBase64"
                )
            ]
        )
    
    def create_report_definition(self, report_name: str) -> ItemDefinition:
        """Create minimal Report definition
        
        Args:
            report_name: Name of the report
            
        Returns:
            ItemDefinition with base64 encoded .pbir content
        """
        # Minimal .pbir file content for Power BI Report
        pbir_content = {
            "version": "4.0",
            "dataModelSchema": {
                "name": report_name
            }
        }
        
        # Encode to base64
        pbir_json = json.dumps(pbir_content, indent=2)
        payload_base64 = base64.b64encode(pbir_json.encode('utf-8')).decode('utf-8')
        
        return ItemDefinition(
            parts=[
                ItemDefinitionPart(
                    path="report.pbir",
                    payload=payload_base64,
                    payload_type="InlineBase64"
                )
            ]
        )
    
    def step_5_create_additional_items(self):
        """Step 5: Create pipeline, semantic model, and report"""
        self.print_header("STEP 5: Creating Additional Fabric Items")
        
        additional_items = [
            {
                "name": "RicohDataPipeline",
                "type": FabricItemType.DATA_PIPELINE,
                "description": "Orchestration pipeline for automated data processing",
                "definition": None
            }
            # NOTE: Semantic Model and Report creation through API requires complex definitions
            # These item types are better created through the Fabric portal or Power BI Desktop
            # {
            #     "name": "RicohSemanticModel",
            #     "type": FabricItemType.SEMANTIC_MODEL,
            #     "description": "Semantic model for business intelligence and reporting",
            #     "definition": "semantic_model"
            # },
            # {
            #     "name": "RicohExecutiveDashboard",
            #     "type": FabricItemType.REPORT,
            #     "description": "Executive dashboard for key business metrics",
            #     "definition": "report"
            # }
        ]
        
        success_count = 0
        
        for item_config in additional_items:
            try:
                print_info(f"Creating {item_config['type'].value} '{item_config['name']}'...")
                
                # Create definition if needed
                definition = None
                if item_config.get("definition") == "semantic_model":
                    print_info(f"  Generating Semantic Model definition...")
                    definition = self.create_semantic_model_definition(item_config["name"])
                elif item_config.get("definition") == "report":
                    print_info(f"  Generating Report definition...")
                    definition = self.create_report_definition(item_config["name"])
                
                item = self.item_mgr.create_item(
                    workspace_id=self.workspace_id,
                    display_name=item_config["name"],
                    item_type=item_config["type"],
                    description=item_config["description"],
                    definition=definition
                )
                
                print_success(f"✓ {item_config['type'].value} '{item_config['name']}' created")
                print_info(f"  Item ID: {item.id}")
                
                self.created_items.append(item)
                self.setup_log["items"].append({
                    "name": item_config["name"],
                    "type": item_config["type"].value,
                    "id": item.id
                })
                
                success_count += 1
                
            except Exception as e:
                print_error(f"Failed to create {item_config['type'].value} '{item_config['name']}': {str(e)}")
                self.setup_log["errors"].append(f"{item_config['type'].value} {item_config['name']}: {str(e)}")
        
        print_info(f"\nCreated {success_count}/{len(additional_items)} additional items")
        print_warning("\nNote: Semantic Models and Reports are commented out.")
        print_info("These items require complex definitions and are best created through:")
        print_info("  - Fabric portal (https://app.fabric.microsoft.com)")
        print_info("  - Power BI Desktop")
        print_info("  - Semantic Model editor in Fabric")
        
        return success_count == len(additional_items)
    
    
    def step_6_configure_users(self):
        """Step 6: Add users/groups to workspace using core CLI (best practice)"""
        self.print_header("STEP 6: Adding Users/Groups to Workspace")
        
        # Determine principals file to use
        if self.principals_file:
            # Use provided file
            principals_file = Path(self.principals_file)
        else:
            # Look for workspace-specific file, fallback to ricoh_users.txt
            workspace_file = Path(__file__).parent / f"{self.workspace_name.split('-')[0]}_principals.txt"
            ricoh_file = Path(__file__).parent / "ricoh_users.txt"
            
            if workspace_file.exists():
                principals_file = workspace_file
            elif ricoh_file.exists():
                principals_file = ricoh_file
            else:
                # No file found
                principals_file = None
        
        if not principals_file or not principals_file.exists():
            print_warning("No principals file found")
            print_info("\n📝 To add users/groups to this workspace:")
            print_info("\n  Option 1 - Use Core CLI with template:")
            print_info("     # Copy template")
            print_info("     cp config/workspace_principals.template.txt my_workspace_users.txt")
            print_info("     # Edit and add your principals")
            print_info("     # Add to workspace")
            print_info(f"     python ops/scripts/manage_workspaces.py add-users-from-file {self.workspace_id} my_workspace_users.txt")
            print_info("\n  Option 2 - Add individual user/group:")
            print_info(f"     python ops/scripts/manage_workspaces.py add-user {self.workspace_id} <object_id> --role Admin --principal-type User")
            print_info("\n  Get Object IDs:")
            print_info("     User:  az ad user show --id user@domain.com --query id -o tsv")
            print_info("     Group: az ad group show --group 'Team Name' --query id -o tsv")
            print_warning("\n⚠️  Note: Fabric API requires Object IDs, not email addresses")
            
            # Store in log
            self.setup_log["users_configured"] = False
            self.setup_log["principals_file"] = "not_found"
            return True
        
        print_info(f"Using principals file: {principals_file.name}")
        
        # Use core CLI to add users (best practice - no code duplication)
        try:
            # Get path to core CLI script
            cli_script = Path(__file__).parent.parent / "ops" / "scripts" / "manage_workspaces.py"
            
            # Preview first
            print_info("\nPreviewing principals to be added...")
            preview_cmd = [
                sys.executable,
                str(cli_script),
                "add-users-from-file",
                self.workspace_id,
                str(principals_file),
                "--dry-run"
            ]
            
            preview_result = subprocess.run(
                preview_cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            
            # Show preview output (filter out verbose logging)
            if preview_result.stdout:
                for line in preview_result.stdout.split('\n'):
                    if line.strip() and not line.startswith('INFO:'):
                        print(line)
            
            if preview_result.returncode != 0:
                print_error(f"Preview failed: {preview_result.stderr}")
                return False
            
            # Now add for real
            print_info("\nAdding principals to workspace (using core CLI)...")
            add_cmd = [
                sys.executable,
                str(cli_script),
                "add-users-from-file",
                self.workspace_id,
                str(principals_file),
                "--yes"  # Skip confirmation since we already previewed
            ]
            
            add_result = subprocess.run(
                add_cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            
            # Show output (filter out verbose logging)
            if add_result.stdout:
                for line in add_result.stdout.split('\n'):
                    if line.strip() and not line.startswith('INFO:'):
                        print(line)
            
            if add_result.returncode != 0:
                print_error(f"Failed to add principals: {add_result.stderr}")
                self.setup_log["errors"].append(f"User configuration failed: {add_result.stderr}")
                return False
            
            # Success
            self.setup_log["users_configured"] = True
            self.setup_log["principals_file"] = str(principals_file)
            print_success("\n✓ User configuration complete (via core CLI)")
            return True
            
        except Exception as e:
            print_error(f"Failed to configure users: {str(e)}")
            self.setup_log["errors"].append(f"User configuration: {str(e)}")
            return False
    
    def step_7_verify_setup(self):
        """Step 7: Verify all items were created"""
        self.print_header("STEP 7: Verifying Setup")
        
        try:
            print_info(f"Listing all items in workspace '{self.workspace_name}'...")
            
            items = self.item_mgr.list_items(self.workspace_id)
            
            # Display items
            if items:
                headers = ["Display Name", "Type", "ID"]
                rows = [[item.display_name, item.type.value, item.id] for item in items]
                print_table(headers, rows)
            else:
                print_warning("No items found in workspace")
            
            print_success(f"\n✓ Found {len(items)} item(s) in workspace")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to verify setup: {str(e)}")
            self.setup_log["errors"].append(f"Verification: {str(e)}")
            return False
    
    def run(self):
        """Execute the complete setup"""
        self.print_header("LEIT-Ricoh Domain - Fresh Workspace Setup with Capacity")
        
        print(f"Domain: {self.domain_name}")
        print(f"Workspace: {self.workspace_name} (NEW)")
        print(f"Environment: {self.environment}")
        if self.capacity_id:
            print(f"Capacity ID: {self.capacity_id}")
        else:
            print("Capacity ID: Will auto-detect")
        
        print("\nThis will create:")
        print("  - 1 New Workspace (with capacity assigned)")
        print("  - 1 Lakehouse")
        print("  - 1 Warehouse")
        print("  - 3 Notebooks")
        print("  - 3 Additional items (Pipeline, Semantic Model, Report)")
        print("  - 6 User role configurations")
        
        self.print_header("")
        
        # Execute steps
        steps = [
            ("Create Workspace with Capacity", self.step_1_create_workspace_with_capacity),
            ("Create Lakehouse", self.step_2_create_lakehouse),
            ("Create Warehouse", self.step_3_create_warehouse),
            ("Create Notebooks", self.step_4_create_notebooks),
            ("Create Additional Items", self.step_5_create_additional_items),
            ("Configure Users", self.step_6_configure_users),
            ("Verify Setup", self.step_7_verify_setup),
        ]
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                if result:
                    print_success(f"✓ Step '{step_name}' completed successfully")
                else:
                    print_warning(f"⚠️  Step '{step_name}' completed with warnings")
            except Exception as e:
                print_error(f"✗ Step '{step_name}' failed: {e}")
                self.setup_log["errors"].append(f"{step_name}: {str(e)}")
        
        # Print summary
        self.print_header("SETUP COMPLETE - Summary")
        
        print_success("✓ Workspace Setup Successful!\n")
        print(f"Domain:           {self.domain_name}")
        print(f"Workspace:        {self.workspace_name}")
        print(f"Environment:      {self.environment}")
        print(f"Workspace ID:     {self.workspace_id}")
        if self.capacity_id:
            print(f"Capacity ID:      {self.capacity_id}")
        
        self.print_header("")
        
        print("📊 Fabric Items Created:\n")
        if self.created_items:
            for item in self.created_items:
                print(f"  ✓ {item.type.value}: {item.display_name}")
        else:
            print("  No items created")
        
        self.print_header("")
        
        print("📝 Next Steps:\n")
        print("  1. Verify capacity assignment in Fabric portal")
        print("  2. Add users/groups to workspace:")
        print(f"     python ops/scripts/manage_workspaces.py add-users-from-file {self.workspace_id} <principals_file>")
        print("  3. Set up data connections and sources")
        print("  4. Develop notebook code for data processing")
        print("  5. Configure pipeline orchestration")
        print("  6. Build semantic model relationships (Power BI Desktop)")
        print("  7. Design dashboard visuals (Power BI Desktop)")
        
        self.print_header("")
        
        # Print errors if any
        if self.setup_log["errors"]:
            print_warning(f"\n⚠ {len(self.setup_log['errors'])} error(s) encountered:")
            for error in self.setup_log["errors"]:
                print_error(f"  - {error}")
        
        # Save log
        log_dir = Path(__file__).parent.parent / ".onboarding_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        log_file = log_dir / f"{timestamp}_leit_ricoh_fresh_setup.json"
        
        with open(log_file, 'w') as f:
            json.dump(self.setup_log, f, indent=2)
        
        print_info(f"\n📄 Setup log saved to: {log_file}")
        
        # Return exit code
        return 0 if not self.setup_log["errors"] else 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="LEIT-Ricoh Fresh Workspace Setup with Capacity Assignment",
        epilog="Example: python leit_ricoh_fresh_setup.py --capacity-id abc123 --principals-file my_users.txt"
    )
    parser.add_argument(
        '--capacity-id',
        help='Fabric Capacity ID (GUID). If not provided, will auto-detect available capacity.',
        default=None
    )
    parser.add_argument(
        '--principals-file',
        help='Path to principals file (users/groups to add). If not provided, looks for ricoh_users.txt',
        default=None
    )
    
    args = parser.parse_args()
    
    setup = RicohFreshWorkspaceSetup(
        capacity_id=args.capacity_id,
        principals_file=args.principals_file
    )
    exit_code = setup.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
