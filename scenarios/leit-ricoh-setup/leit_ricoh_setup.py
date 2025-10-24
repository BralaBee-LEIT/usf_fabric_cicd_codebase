#!/usr/bin/env python3
"""
LEIT-Ricoh Domain - Complete Workspace Setup Scenario

This script creates a complete Microsoft Fabric workspace with:
- Notebooks for data processing (3)
- Users with different roles (6)
- Lakehouse for data storage (1)
- Warehouse for analytics (1)
- 3 additional Fabric items (Pipeline, Semantic Model, Report)

Domain: leit-ricoh-domain
Workspace: leit-ricoh
Total Items: 9 Fabric items + 6 users
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add ops/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops" / "scripts"))

from utilities.workspace_manager import WorkspaceManager, WorkspaceRole
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
    console_table as print_table,
)


class RicohWorkspaceSetup:
    """Setup manager for LEIT-Ricoh workspace"""

    def __init__(self, capacity_id=None):
        self.workspace_name = "leit-ricoh"
        self.domain_name = "leit-ricoh-domain"
        self.environment = "dev"
        self.workspace_id = None
        self.capacity_id = capacity_id

        self.workspace_mgr = WorkspaceManager(environment=self.environment)
        self.item_mgr = FabricItemManager()

        self.created_items = []
        self.setup_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": self.domain_name,
            "workspace": self.workspace_name,
            "environment": self.environment,
            "capacity_id": capacity_id,
            "items": [],
            "users": [],
            "errors": [],
        }

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80 + "\n")

    def step_1_create_workspace(self):
        """Step 1: Create the workspace"""
        self.print_header("STEP 1: Creating Workspace - leit-ricoh")

        try:
            print_info(
                f"Creating workspace '{self.workspace_name}' in {self.environment} environment..."
            )
            if self.capacity_id:
                print_info(f"  Using capacity ID: {self.capacity_id}")
            else:
                print_warning(
                    "  No capacity ID - workspace will be Trial (item creation will fail)"
                )

            workspace = self.workspace_mgr.create_workspace(
                name=self.workspace_name,
                description="LEIT-Ricoh domain workspace for data analytics and reporting",
                capacity_id=self.capacity_id,
            )

            self.workspace_id = workspace.get("id")

            print_success(f"✓ Workspace '{self.workspace_name}' created successfully")
            print_info(f"  Workspace ID: {self.workspace_id}")

            self.setup_log["workspace_id"] = self.workspace_id

            return True

        except ValueError as e:
            # Workspace already exists - fetch it
            if "already exists" in str(e):
                print_warning(
                    "Workspace already exists, retrieving existing workspace..."
                )
                existing_workspace = self.workspace_mgr.get_workspace_by_name(
                    self.workspace_name
                )

                if existing_workspace:
                    self.workspace_id = existing_workspace.get("id")
                    print_success(f"✓ Using existing workspace '{self.workspace_name}'")
                    print_info(f"  Workspace ID: {self.workspace_id}")

                    self.setup_log["workspace_id"] = self.workspace_id
                    self.setup_log["errors"].append(
                        f"Workspace existed (reused): {self.workspace_id}"
                    )

                    return True
                else:
                    print_error("Failed to retrieve existing workspace")
                    self.setup_log["errors"].append(
                        f"Workspace retrieval failed: {str(e)}"
                    )
                    return False
            else:
                print_error(f"Failed to create workspace: {str(e)}")
                self.setup_log["errors"].append(f"Workspace creation: {str(e)}")
                return False
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
                description="Primary lakehouse for Ricoh data storage and processing",
            )

            print_success("✓ Lakehouse 'RicohDataLakehouse' created")
            print_info(f"  Item ID: {lakehouse.id}")

            self.created_items.append(lakehouse)
            self.setup_log["items"].append(
                {"name": "RicohDataLakehouse", "type": "Lakehouse", "id": lakehouse.id}
            )

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
                description="Data warehouse for Ricoh analytics and reporting",
            )

            print_success("✓ Warehouse 'RicohAnalyticsWarehouse' created")
            print_info(f"  Item ID: {warehouse.id}")

            self.created_items.append(warehouse)
            self.setup_log["items"].append(
                {
                    "name": "RicohAnalyticsWarehouse",
                    "type": "Warehouse",
                    "id": warehouse.id,
                }
            )

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
                "description": "Ingests raw data from various sources into lakehouse",
            },
            {
                "name": "02_DataTransformation",
                "description": "Transforms and cleanses data for analytics",
            },
            {
                "name": "03_DataValidation",
                "description": "Validates data quality and completeness",
            },
        ]

        success_count = 0

        for nb_config in notebooks:
            try:
                print_info(f"Creating notebook '{nb_config['name']}'...")

                notebook = self.item_mgr.create_item(
                    workspace_id=self.workspace_id,
                    display_name=nb_config["name"],
                    item_type=FabricItemType.NOTEBOOK,
                    description=nb_config["description"],
                )

                print_success(f"✓ Notebook '{nb_config['name']}' created")

                self.created_items.append(notebook)
                self.setup_log["items"].append(
                    {"name": nb_config["name"], "type": "Notebook", "id": notebook.id}
                )

                success_count += 1

            except Exception as e:
                print_error(
                    f"Failed to create notebook '{nb_config['name']}': {str(e)}"
                )
                self.setup_log["errors"].append(
                    f"Notebook {nb_config['name']}: {str(e)}"
                )

        print_info(f"\nCreated {success_count}/{len(notebooks)} notebooks")
        return success_count == len(notebooks)

    def step_5_create_additional_items(self):
        """Step 5: Create additional Fabric items"""
        self.print_header("STEP 5: Creating Additional Fabric Items")

        items = [
            {
                "name": "RicohDataPipeline",
                "type": FabricItemType.DATA_PIPELINE,
                "description": "Orchestrates the end-to-end data processing workflow",
            },
            {
                "name": "RicohSemanticModel",
                "type": FabricItemType.SEMANTIC_MODEL,
                "description": "Business semantic layer for Ricoh analytics",
            },
            {
                "name": "RicohExecutiveDashboard",
                "type": FabricItemType.REPORT,
                "description": "Executive dashboard for Ricoh business metrics",
            },
        ]

        success_count = 0

        for item_config in items:
            try:
                print_info(
                    f"Creating {item_config['type'].value} '{item_config['name']}'..."
                )

                item = self.item_mgr.create_item(
                    workspace_id=self.workspace_id,
                    display_name=item_config["name"],
                    item_type=item_config["type"],
                    description=item_config["description"],
                )

                print_success(
                    f"✓ {item_config['type'].value} '{item_config['name']}' created"
                )

                self.created_items.append(item)
                self.setup_log["items"].append(
                    {
                        "name": item_config["name"],
                        "type": item_config["type"].value,
                        "id": item.id,
                    }
                )

                success_count += 1

            except Exception as e:
                print_error(
                    f"Failed to create {item_config['type'].value} '{item_config['name']}': {str(e)}"
                )
                self.setup_log["errors"].append(
                    f"{item_config['type'].value} {item_config['name']}: {str(e)}"
                )

        print_info(f"\nCreated {success_count}/{len(items)} additional items")
        return success_count == len(items)

    def step_6_add_users(self):
        """Step 6: Add users to workspace (configuration only)"""
        self.print_header("STEP 6: User Configuration (Update with actual emails)")

        users = [
            {
                "email": "ricoh.admin@leit-teksystems.com",
                "role": WorkspaceRole.ADMIN,
                "description": "Workspace administrator",
            },
            {
                "email": "ricoh.engineer1@leit-teksystems.com",
                "role": WorkspaceRole.MEMBER,
                "description": "Data engineer - Senior",
            },
            {
                "email": "ricoh.engineer2@leit-teksystems.com",
                "role": WorkspaceRole.MEMBER,
                "description": "Data engineer - Junior",
            },
            {
                "email": "ricoh.analyst@leit-teksystems.com",
                "role": WorkspaceRole.CONTRIBUTOR,
                "description": "Data analyst",
            },
            {
                "email": "ricoh.business1@leit-teksystems.com",
                "role": WorkspaceRole.VIEWER,
                "description": "Business user - Finance",
            },
            {
                "email": "ricoh.business2@leit-teksystems.com",
                "role": WorkspaceRole.VIEWER,
                "description": "Business user - Operations",
            },
        ]

        print_warning(
            "User addition is commented out. Update emails and uncomment code to add users."
        )
        print_info("\nPlanned user configuration:")

        # Display user table
        headers = ["Email", "Role", "Description"]
        rows = [[u["email"], u["role"].value, u["description"]] for u in users]
        print_table(headers, rows)

        # Store in log
        self.setup_log["users"] = users

        print_info("\nTo add users, uncomment the add_user code and run:")
        print_info(
            "  python3 ops/scripts/manage_workspaces.py add-user --workspace leit-ricoh --email <email> --role <role>"
        )

        return True

    def step_7_verify_setup(self):
        """Step 7: Verify the setup"""
        self.print_header("STEP 7: Verifying Setup")

        try:
            print_info(f"Listing all items in workspace '{self.workspace_name}'...")

            items = self.item_mgr.list_items(workspace_id=self.workspace_id)

            # Display items table
            headers = ["Display Name", "Type", "ID"]
            rows = [
                [item.display_name, item.type.value, item.id[:8] + "..."]
                for item in items
            ]

            print_table(headers, rows)
            print_success(f"\n✓ Found {len(items)} item(s) in workspace")

            return True

        except Exception as e:
            print_error(f"Failed to verify setup: {str(e)}")
            return False

    def generate_summary(self):
        """Generate setup summary"""
        self.print_header("SETUP COMPLETE - Summary")

        print_success("✓ Workspace Setup Successful!\n")

        print(f"Domain:           {self.domain_name}")
        print(f"Workspace:        {self.workspace_name}")
        print(f"Environment:      {self.environment}")
        print(f"Workspace ID:     {self.workspace_id}")

        print("\n" + "=" * 80)
        print("\n📊 Fabric Items Created:\n")

        # Group items by category
        storage_items = [
            i
            for i in self.created_items
            if i.type in [FabricItemType.LAKEHOUSE, FabricItemType.WAREHOUSE]
        ]
        notebook_items = [
            i for i in self.created_items if i.type == FabricItemType.NOTEBOOK
        ]
        other_items = [
            i
            for i in self.created_items
            if i.type
            not in [
                FabricItemType.LAKEHOUSE,
                FabricItemType.WAREHOUSE,
                FabricItemType.NOTEBOOK,
            ]
        ]

        if storage_items:
            print("  Storage:")
            for item in storage_items:
                print(f"    • {item.display_name:<30} ({item.type.value})")

        if notebook_items:
            print("\n  Processing:")
            for item in notebook_items:
                print(f"    • {item.display_name:<30} ({item.type.value})")

        if other_items:
            print("\n  Orchestration & Analytics:")
            for item in other_items:
                print(f"    • {item.display_name:<30} ({item.type.value})")

        print("\n" + "=" * 80)
        print("\n📝 Next Steps:\n")
        print("  1. Update user email addresses with actual organizational emails")
        print("  2. Run user add commands to grant workspace access")
        print("  3. Configure workspace capacity if moving from Trial")
        print("  4. Set up data connections and sources")
        print("  5. Develop notebook code for data processing")
        print("  6. Configure pipeline orchestration")
        print("  7. Build semantic model relationships")
        print("  8. Design executive dashboard visuals")

        print("\n" + "=" * 80)

        if self.setup_log["errors"]:
            print_warning(f"\n⚠ {len(self.setup_log['errors'])} error(s) encountered:")
            for error in self.setup_log["errors"]:
                print_error(f"  - {error}")
        else:
            print_success("\n🚀 LEIT-Ricoh workspace is ready for use!")

        # Save setup log
        self.save_setup_log()

    def save_setup_log(self):
        """Save setup log to file"""
        try:
            log_dir = Path(__file__).parent.parent / ".onboarding_logs"
            log_dir.mkdir(exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            log_file = log_dir / f"{timestamp}_leit_ricoh_setup.json"

            with open(log_file, "w") as f:
                json.dump(self.setup_log, f, indent=2)

            print_info(f"\n📄 Setup log saved to: {log_file}")

        except Exception as e:
            print_warning(f"Failed to save setup log: {str(e)}")

    def run(self):
        """Execute the complete setup"""
        print("\n" + "=" * 80)
        print("  LEIT-Ricoh Domain - Complete Workspace Setup")
        print("=" * 80)
        print(f"\nDomain: {self.domain_name}")
        print(f"Workspace: {self.workspace_name}")
        print(f"Environment: {self.environment}")
        print("\nThis will create:")
        print("  - 1 Workspace")
        print("  - 1 Lakehouse")
        print("  - 1 Warehouse")
        print("  - 3 Notebooks")
        print("  - 3 Additional items (Pipeline, Semantic Model, Report)")
        print("  - 6 User role configurations")
        print("\n" + "=" * 80 + "\n")

        # Execute steps
        steps = [
            ("Create Workspace", self.step_1_create_workspace),
            ("Create Lakehouse", self.step_2_create_lakehouse),
            ("Create Warehouse", self.step_3_create_warehouse),
            ("Create Notebooks", self.step_4_create_notebooks),
            ("Create Additional Items", self.step_5_create_additional_items),
            ("Configure Users", self.step_6_add_users),
            ("Verify Setup", self.step_7_verify_setup),
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    print_warning(f"Step '{step_name}' completed with warnings")
            except Exception as e:
                print_error(f"Step '{step_name}' failed: {str(e)}")
                self.setup_log["errors"].append(f"{step_name}: {str(e)}")

        # Generate summary
        self.generate_summary()

        return len(self.setup_log["errors"]) == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="LEIT-Ricoh Domain - Complete Workspace Setup"
    )
    parser.add_argument(
        "--capacity-id",
        help="Fabric capacity ID (required for item creation)",
        default=os.getenv("FABRIC_CAPACITY_ID"),
    )

    args = parser.parse_args()

    try:
        setup = RicohWorkspaceSetup(capacity_id=args.capacity_id)
        success = setup.run()

        return 0 if success else 1

    except KeyboardInterrupt:
        print_warning("\n\nSetup interrupted by user")
        return 130
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
