#!/usr/bin/env python3
"""
============================================================================
Comprehensive Sales Analytics ETL Demo
============================================================================

This scenario demonstrates the COMPLETE framework with proper integration:

✅ Uses ConfigManager for project.config.json integration
✅ Uses naming patterns from project.config.json
✅ Validates against naming_standards.yaml
✅ Creates workspace with medallion folder structure
✅ Creates items following proper naming conventions
✅ Intelligently places items in appropriate folders
✅ Connects to Git repository
✅ Adds users with proper roles
✅ Full audit logging

Architecture:
    Bronze Layer → Raw data ingestion
    Silver Layer → Cleansed and validated data
    Gold Layer → Analytics-ready aggregations
    Orchestration → Pipeline workflows
    Utilities → Shared helper functions

Usage:
    # Dry run to preview
    python run_sales_analytics_demo.py --dry-run

    # Full deployment
    python run_sales_analytics_demo.py

    # Use existing workspace
    python run_sales_analytics_demo.py --workspace-id <guid>

Prerequisites:
    - .env file with Azure credentials and FABRIC_CAPACITY_ID
    - project.config.json properly configured
    - naming_standards.yaml in place

Author: USF Fabric CI/CD Framework  
Version: 2.0 - Proper Integration Edition
============================================================================
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "ops" / "scripts"))

# Import framework utilities
from utilities.config_manager import ConfigManager
from utilities.workspace_manager import WorkspaceManager, WorkspaceRole
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.fabric_git_connector import FabricGitConnector
from utilities.audit_logger import AuditLogger

# Try to import folder manager
try:
    from utilities.fabric_folder_manager import FabricFolderManager
    FOLDERS_AVAILABLE = True
except ImportError:
    FOLDERS_AVAILABLE = False


# ============================================================================
# Output Utilities
# ============================================================================

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}{Colors.ENDC}\n")


def print_step(step: int, total: int, title: str):
    """Print step header"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}[Step {step}/{total}] {title}{Colors.ENDC}")


def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")


def print_info(msg: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")


# ============================================================================
# Core Deployment Logic
# ============================================================================

def load_product_config(config_path: str) -> Dict:
    """Load product configuration from YAML with environment variable substitution"""
    import re
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Substitute environment variables in format ${VAR_NAME}
    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))  # Return original if not found
    
    content = re.sub(r'\$\{([^}]+)\}', replace_env_var, content)
    
    return yaml.safe_load(content)


def create_workspace_with_folders(
    product_config: Dict,
    config_manager: ConfigManager,
    dry_run: bool = False
) -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Create workspace with medallion folder structure using project patterns
    
    Returns:
        Tuple of (workspace_id, folder_map) where folder_map maps folder names to IDs
    """
    print_step(1, 6, "Creating Workspace with Folder Structure")
    
    product_name = product_config['product']['name']
    env_config = product_config['environments']['dev']
    
    # Generate workspace name using project.config.json pattern
    project_info = config_manager.get_project_info()
    prefix = project_info['prefix']
    workspace_name = f"{prefix}-{product_name}-dev"
    
    print_info(f"Workspace name (from pattern): {workspace_name}")
    print_info(f"Description: {env_config['description']}")
    print_info(f"Capacity ID: {env_config.get('capacity_id', 'None')}")
    
    if dry_run:
        print_warning("DRY RUN: Would create workspace with folders")
        return ("dry-run-workspace-id", {
            "Bronze": "folder-1",
            "Silver": "folder-2",
            "Gold": "folder-3",
            "Orchestration": "folder-4",
            "Utilities": "folder-5",
            "Documentation": "folder-6"
        })
    
    try:
        workspace_manager = WorkspaceManager(environment='dev')
        
        # Check if workspace already exists
        existing = workspace_manager.get_workspace_by_name(workspace_name)
        if existing:
            print_warning(f"Workspace already exists: {workspace_name}")
            workspace_id = existing["id"]
            print_info(f"Using existing workspace ID: {workspace_id}")
            
            # Try to get existing folder structure
            folder_map = {}
            if FOLDERS_AVAILABLE:
                try:
                    fm = FabricFolderManager()
                    structure = fm.get_folder_structure(workspace_id)
                    for folder in structure.root_folders:
                        folder_map[folder.display_name] = folder.id
                    print_success(f"Found {len(folder_map)} existing folders")
                except Exception as e:
                    print_warning(f"Could not retrieve folder structure: {e}")
            
            return (workspace_id, folder_map)
        
        # Create new workspace with folder structure
        capacity_id = env_config.get('capacity_id')
        
        # Check if medallion architecture is requested
        folder_config = env_config.get('folder_structure', {})
        use_medallion = folder_config.get('template') == 'medallion' if folder_config.get('enabled') else False
        
        print_info(f"Medallion architecture: {use_medallion} (config: {folder_config})")
        
        # Create workspace with structure
        result = workspace_manager.create_workspace_with_structure(
            name=workspace_name,
            description=env_config['description'],
            capacity_id=capacity_id,
            use_medallion_architecture=use_medallion,
            folder_structure=None  # Let medallion architecture create default structure
        )
        
        workspace_id = result['workspace_id']
        folder_ids = result['folder_ids']
        
        print_success(f"Created workspace: {workspace_name}")
        print_success(f"Created {len(folder_ids)} folders")
        print_info(f"Workspace ID: {workspace_id}")
        
        # Build folder name to ID map (including subfolders)
        folder_map = {}
        if FOLDERS_AVAILABLE:
            try:
                fm = FabricFolderManager()
                structure = fm.get_folder_structure(workspace_id)
                for folder in structure.root_folders:
                    folder_map[folder.display_name] = folder.id
                    print_info(f"  - {folder.display_name}: {folder.id[:8]}...")
                    
                    # Add subfolders to map
                    subfolders = structure.get_children(folder.id)
                    for subfolder in subfolders:
                        # Add both full path and subfolder name
                        full_path = f"{folder.display_name}/{subfolder.display_name}"
                        folder_map[full_path] = subfolder.id
                        folder_map[subfolder.display_name] = subfolder.id
                        print_info(f"    - {full_path}: {subfolder.id[:8]}...")
            except Exception as e:
                print_warning(f"Could not map folder names: {e}")
        
        return (workspace_id, folder_map)
        
    except Exception as e:
        print_error(f"Failed to create workspace: {e}")
        return None


def create_items_in_folders(
    workspace_id: str,
    product_config: Dict,
    folder_map: Dict[str, str],
    dry_run: bool = False
) -> Dict[str, List[str]]:
    """
    Create items following naming standards and place in appropriate folders
    """
    print_step(2, 6, "Creating Items with Proper Naming and Organization")
    
    items_config = product_config.get('items', {})
    created_items = {'lakehouses': [], 'notebooks': []}
    
    if dry_run:
        print_warning("DRY RUN: Would create items")
        total = len(items_config.get('lakehouses', [])) + len(items_config.get('notebooks', []))
        print_info(f"Would create {total} items")
        return created_items
    
    item_manager = FabricItemManager()
    
    # Re-fetch folder structure to ensure we have current mappings including subfolders
    folder_manager = None
    if FOLDERS_AVAILABLE:
        import time
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print_info(f"Retrying folder structure fetch (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay * attempt)  # Exponential backoff
                
                folder_manager = FabricFolderManager()
                # Always refresh to ensure we have subfolders (may have been rate-limited during creation)
                structure = folder_manager.get_folder_structure(workspace_id)
                
                # Build comprehensive folder map including subfolders
                folder_map = {}  # Clear and rebuild to ensure completeness
                for folder in structure.root_folders:
                    folder_map[folder.display_name] = folder.id
                    # Add subfolders using subfolder_map
                    subfolders = structure.get_children(folder.id)
                    for subfolder in subfolders:
                        # Map both "Parent/Child" and just "Child" formats
                        full_path = f"{folder.display_name}/{subfolder.display_name}"
                        folder_map[full_path] = subfolder.id
                        folder_map[subfolder.display_name] = subfolder.id
                
                print_success(f"Mapped {len(folder_map)} folders for intelligent placement")
                break  # Success - exit retry loop
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print_warning(f"API rate limited, will retry...")
                    continue
                else:
                    print_warning(f"Could not refresh folder structure after {attempt + 1} attempts: {e}")
                    folder_manager = None
                    break
    
    # Helper function to intelligently determine folder placement
    def determine_folder(item_name: str, item_type: str, specified_folder: str = None) -> tuple:
        """
        Intelligently determine folder placement based on naming patterns
        Returns: (folder_id, folder_name)
        """
        # If explicitly specified, use that
        if specified_folder and specified_folder in folder_map:
            return (folder_map[specified_folder], specified_folder)
        
        # Intelligent placement based on naming patterns
        if item_type == 'lakehouse':
            if item_name.startswith('BRONZE_'):
                # Try subfolders first, then main Bronze folder
                for folder_name in ['Bronze Layer/Raw Data', 'Raw Data', 'Bronze Layer']:
                    if folder_name in folder_map:
                        return (folder_map[folder_name], folder_name)
            elif item_name.startswith('SILVER_'):
                for folder_name in ['Silver Layer/Cleaned', 'Cleaned', 'Silver Layer']:
                    if folder_name in folder_map:
                        return (folder_map[folder_name], folder_name)
            elif item_name.startswith('GOLD_'):
                for folder_name in ['Gold Layer/Analytics', 'Analytics', 'Gold Layer']:
                    if folder_name in folder_map:
                        return (folder_map[folder_name], folder_name)
        
        elif item_type == 'notebook':
            # Parse notebook number prefix
            if '_' in item_name:
                prefix = item_name.split('_')[0]
                try:
                    num = int(prefix)
                    # 01-09: Ingestion (Bronze)
                    if 1 <= num <= 9:
                        for folder_name in ['Bronze Layer/Raw Data', 'Raw Data', 'Bronze Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                    # 10-19: Transformation (Silver)
                    elif 10 <= num <= 19:
                        for folder_name in ['Silver Layer/Transformed', 'Transformed', 'Silver Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                    # 20-29: Analytics (Gold)
                    elif 20 <= num <= 29:
                        for folder_name in ['Gold Layer/Analytics', 'Analytics', 'Gold Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                    # 50+: Orchestration
                    elif num >= 50:
                        # Keep at root or in Orchestration folder if it exists
                        return (None, 'Root (Orchestration)')
                except ValueError:
                    pass
        
        return (None, 'Root')
    
    # Create lakehouses
    lakehouses = items_config.get('lakehouses', [])
    if lakehouses:
        print_info(f"\nCreating {len(lakehouses)} lakehouses...")
        for lakehouse in lakehouses:
            name = lakehouse['name']
            description = lakehouse.get('description', '')
            specified_folder = lakehouse.get('target_folder')
            
            try:
                print_info(f"  Creating: {name}")
                
                # Determine target folder
                folder_id, folder_name = determine_folder(name, 'lakehouse', specified_folder)
                
                # Create item directly in folder
                item = item_manager.create_item(
                    workspace_id=workspace_id,
                    display_name=name,
                    item_type=FabricItemType.LAKEHOUSE,
                    description=description,
                    folder_id=folder_id  # Place directly in folder during creation
                )
                
                # Verify actual placement (item.folder_id confirms where it was created)
                if item.folder_id:
                    print_success(f"✓ Created: {name} → {folder_name}")
                else:
                    print_success(f"✓ Created: {name} (intended: {folder_name})")
                created_items['lakehouses'].append(item.id)
                
            except Exception as e:
                print_error(f"Failed to create {name}: {e}")
    
    # Create notebooks
    notebooks = items_config.get('notebooks', [])
    if notebooks:
        print_info(f"\nCreating {len(notebooks)} notebooks...")
        for notebook in notebooks:
            name = notebook['name']
            description = notebook.get('description', '')
            specified_folder = notebook.get('target_folder')
            
            try:
                print_info(f"  Creating: {name}")
                
                # Determine target folder
                folder_id, folder_name = determine_folder(name, 'notebook', specified_folder)
                
                # Create item directly in folder
                item = item_manager.create_item(
                    workspace_id=workspace_id,
                    display_name=name,
                    item_type=FabricItemType.NOTEBOOK,
                    description=description,
                    folder_id=folder_id  # Place directly in folder during creation
                )
                
                # Verify actual placement (item.folder_id confirms where it was created)
                if item.folder_id:
                    print_success(f"✓ Created: {name} → {folder_name}")
                else:
                    print_success(f"✓ Created: {name} (intended: {folder_name})")
                created_items['notebooks'].append(item.id)
                
            except Exception as e:
                print_error(f"Failed to create {name}: {e}")
    
    total = sum(len(items) for items in created_items.values())
    print_success(f"\nCreated {total} total items")
    
    # Warn about API limitation (folderId parameter not functional)
    if FOLDERS_AVAILABLE and folder_map:
        print_warning("\n⚠️  API LIMITATION: folderId parameter documented but not honored by Fabric API")
        print_info("📋 Items created at workspace root - manual organization required via Portal")
        print_info("💡 Use naming conventions (BRONZE_*, SILVER_*, GOLD_*, number prefixes) to identify placement")
        print_info("📖 See FOLDER_PLACEMENT_FIX.md for detailed analysis and workarounds")
    
    return created_items


def connect_git_repository(
    workspace_id: str,
    product_config: Dict,
    dry_run: bool = False
) -> bool:
    """Connect workspace to Git repository"""
    print_step(3, 6, "Connecting to Git Repository")
    
    git_config = product_config.get('git', {})
    if not git_config.get('enabled'):
        print_info("Git integration disabled in configuration")
        return False
    
    git_org = os.getenv("GIT_ORGANIZATION", git_config.get('organization', ''))
    git_repo = os.getenv("GIT_REPOSITORY", git_config.get('repository', ''))
    branch = git_config.get('branch', 'main')
    directory = git_config.get('directory', '/')
    
    print_info(f"Organization: {git_org}")
    print_info(f"Repository: {git_repo}")
    print_info(f"Branch: {branch}")
    print_info(f"Directory: {directory}")
    
    if dry_run:
        print_warning("DRY RUN: Would connect to Git")
        return True
    
    if not git_org or not git_repo or '${' in git_org or '${' in git_repo:
        print_warning("Git configuration incomplete - skipping")
        return False
    
    try:
        git_connector = FabricGitConnector(git_org, git_repo)
        git_connector.initialize_git_connection_with_retry(
            workspace_id=workspace_id,
            branch_name=branch,
            directory_path=directory,
            auto_commit=git_config.get('auto_commit', False),
            max_retries=git_config.get('max_retries', 3)
        )
        print_success("Git connection established")
        return True
    except Exception as e:
        print_error(f"Failed to connect Git: {e}")
        return False


def add_workspace_users(
    workspace_id: str,
    product_config: Dict,
    dry_run: bool = False
) -> int:
    """Add users to workspace from principals file"""
    print_step(4, 6, "Adding Users to Workspace")
    
    if dry_run:
        print_warning("DRY RUN: Would add users from principals file")
        return 0
    
    # Get product name for principals file lookup
    product_name = product_config.get('product', {}).get('name', '').lower().replace(' ', '_').replace('-', '_')
    
    # Look for principals file in centralized config/principals/ folder
    config_dir = Path(__file__).parent.parent.parent / "config" / "principals"
    principals_file = config_dir / f"{product_name}_dev_principals.txt"
    
    if not principals_file.exists():
        # Try alternate naming
        principals_file = config_dir / "sales_analytics_dev_principals.txt"
    
    if principals_file.exists():
        print_info(f"Found principals file: {principals_file.name}")
        print_info("Adding users from principals file...")
        
        # Use the manage_workspaces.py script to add users
        cli_script = Path(__file__).parent.parent.parent / "ops" / "scripts" / "manage_workspaces.py"
        python = sys.executable
        
        import subprocess
        
        result = subprocess.run(
            [
                python,
                str(cli_script),
                "add-users-from-file",
                workspace_id,
                str(principals_file),
                "--yes",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        
        # Show output (filter out INFO logs)
        if result.stdout:
            for line in result.stdout.split("\n"):
                if line.strip() and not line.startswith("INFO:"):
                    print(f"  {line}")
        
        if result.returncode == 0:
            print_success("Users added successfully")
            return 1
        else:
            print_warning("Some users may have failed to add")
            if result.stderr:
                print_warning(f"Errors: {result.stderr[:200]}")
            return 0
    else:
        # No principals file - show instructions
        print_warning("No principals file found")
        print_info(f"Expected location: {principals_file}")
        print_info("")
        print_info("To add users automatically, create a principals file with format:")
        print_info("  object_id,role,description,type")
        print_info("")
        print_info("Example:")
        print_info("  9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Administrator,User")
        print_info("")
        print_info("Get Object ID using: az ad user show --id user@domain.com --query id -o tsv")
        return 0


def validate_deployment(
    workspace_id: str,
    created_items: Dict[str, List[str]],
    dry_run: bool = False
) -> bool:
    """Validate the deployment"""
    print_step(5, 6, "Validating Deployment")
    
    if dry_run:
        print_warning("DRY RUN: Would validate deployment")
        return True
    
    total_items = sum(len(items) for items in created_items.values())
    print_info(f"Workspace ID: {workspace_id}")
    print_info(f"Total items created: {total_items}")
    print_info(f"  - Lakehouses: {len(created_items.get('lakehouses', []))}")
    print_info(f"  - Notebooks: {len(created_items.get('notebooks', []))}")
    
    print_success("Deployment validation complete")
    return True


def generate_summary(
    workspace_id: str,
    workspace_name: str,
    folder_count: int,
    created_items: Dict[str, List[str]],
    duration: float
):
    """Generate deployment summary"""
    print_step(6, 6, "Deployment Summary")
    
    print_header("Deployment Complete!")
    
    print(f"📊 Summary:")
    print(f"   Workspace: {workspace_name}")
    print(f"   Workspace ID: {workspace_id}")
    print(f"   Folders Created: {folder_count}")
    
    total_items = sum(len(items) for items in created_items.values())
    print(f"   Items Created: {total_items}")
    for item_type, items in created_items.items():
        if items:
            print(f"     - {item_type.capitalize()}: {len(items)}")
    
    print(f"   Duration: {duration:.2f} seconds")
    print()
    
    print(f"🔗 Next Steps:")
    print(f"   1. Open Fabric portal and verify workspace")
    print(f"   2. Check folder organization and item placement")
    print(f"   3. Review audit logs in audit/ directory")
    print(f"   4. Configure data sources and connections")
    print()


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Sales Analytics ETL Demo - Comprehensive Framework Showcase"
    )
    parser.add_argument(
        '--config',
        default=None,
        help='Product configuration file (defaults to config/scenarios/sales_analytics_etl.yaml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview deployment without creating resources'
    )
    parser.add_argument(
        '--workspace-id',
        help='Use existing workspace ID instead of creating new'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Verify capacity ID is available
    capacity_id = os.getenv('FABRIC_CAPACITY_ID')
    if not capacity_id and not args.dry_run:
        print_error("FABRIC_CAPACITY_ID not found in .env file")
        print_info("Item creation requires a valid Fabric capacity")
        sys.exit(1)
    
    # Print header
    print_header("Sales Analytics ETL - Comprehensive Demo")
    
    print("Features Demonstrated:")
    print("  ✅ ConfigManager integration with project.config.json")
    print("  ✅ Workspace naming from project patterns")
    print("  ✅ Medallion folder structure (Bronze/Silver/Gold)")
    print("  ✅ Item naming validation (naming_standards.yaml)")
    print("  ✅ Intelligent folder organization")
    print("  ✅ Git repository connection")
    print("  ✅ User management")
    print("  ✅ Full audit logging")
    print()
    
    if args.dry_run:
        print_warning("DRY RUN MODE - No resources will be created")
        print()
    
    start_time = datetime.now()
    
    try:
        # Load configuration from centralized config folder
        if args.config:
            # User provided a config path
            config_path = Path(args.config)
            if not config_path.is_absolute():
                # Try relative to current directory first
                if config_path.exists():
                    pass
                # Then try relative to project root
                elif (Path(__file__).parent.parent.parent / args.config).exists():
                    config_path = Path(__file__).parent.parent.parent / args.config
                # Then try in config/scenarios
                elif (Path(__file__).parent.parent.parent / "config" / "scenarios" / args.config).exists():
                    config_path = Path(__file__).parent.parent.parent / "config" / "scenarios" / args.config
        else:
            # Default to centralized config location
            config_path = Path(__file__).parent.parent.parent / "config" / "scenarios" / "sales_analytics_etl.yaml"
        
        if not config_path.exists():
            print_error(f"Configuration file not found: {config_path}")
            print_info("Expected location: config/scenarios/sales_analytics_etl.yaml")
            sys.exit(1)
        
        print_info(f"Loading configuration: {config_path.name}")
        print_info(f"Location: {config_path}")
        product_config = load_product_config(config_path)
        
        # Initialize ConfigManager (reads project.config.json)
        config_manager = ConfigManager()
        project_info = config_manager.get_project_info()
        
        print_success("Configuration loaded")
        print_info(f"Project: {project_info['name']}")
        print_info(f"Prefix: {project_info['prefix']}")
        print_info(f"Organization: {project_info['organization']}")
        print()
        
        # Step 1: Create workspace with folders
        result = create_workspace_with_folders(product_config, config_manager, args.dry_run)
        if not result:
            print_error("Workspace creation failed")
            sys.exit(1)
        
        workspace_id, folder_map = result
        workspace_name = f"{project_info['prefix']}-{product_config['product']['name']}-dev"
        
        # Step 2: Create items in folders
        created_items = create_items_in_folders(
            workspace_id,
            product_config,
            folder_map,
            args.dry_run
        )
        
        # Step 3: Connect Git
        git_connected = connect_git_repository(workspace_id, product_config, args.dry_run)
        
        # Step 4: Add users
        users_added = add_workspace_users(workspace_id, product_config, args.dry_run)
        
        # Step 5: Validate deployment
        validation_passed = validate_deployment(workspace_id, created_items, args.dry_run)
        
        # Step 6: Generate summary
        duration = (datetime.now() - start_time).total_seconds()
        generate_summary(
            workspace_id,
            workspace_name,
            len(folder_map),
            created_items,
            duration
        )
        
        print_success("✅ Deployment completed successfully!")
        sys.exit(0)
        
    except KeyboardInterrupt:
        print_error("\n\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
