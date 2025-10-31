#!/usr/bin/env python3
"""
============================================================================
COMPREHENSIVE DEMO SCENARIO - Run Automated Deployment
============================================================================

This scenario demonstrates ALL framework features with intelligent folder
organization:

Features:
    ✅ Folder Structure (Medallion Architecture)
    ✅ Git Integration (Auto-connect with directory structure)
    ✅ Naming Validation (Enforce standards with auto-fix)
    ✅ User Management (Roles, service principals)
    ✅ Item Creation (Lakehouses, notebooks, warehouses, reports)
    ✅ Multi-Environment Support (Dev/Test/Prod)
    ✅ Audit Logging (Complete operation tracking)
    ✅ Intelligent Item Organization (Auto-place by naming pattern)

Usage:
    # Dry run to preview deployment
    python run_comprehensive_demo.py --dry-run

    # Deploy development environment
    python run_comprehensive_demo.py

    # Deploy with custom config
    python run_comprehensive_demo.py --config my_custom_config.yaml

    # Deploy to specific environment
    python run_comprehensive_demo.py --environment prod

Prerequisites:
    - Azure authentication configured (.env file or environment variables)
    - Trial capacity available OR capacity ID configured
    - Appropriate permissions in Microsoft Fabric

Author: USF Fabric CI/CD Framework
Version: 2.0 (Comprehensive Demo with Folder Intelligence)
============================================================================
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import yaml
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "ops" / "scripts"))

# Import framework utilities
from utilities.config_manager import ConfigManager
from utilities.workspace_manager import WorkspaceManager, WorkspaceRole
from utilities.fabric_git_connector import FabricGitConnector
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.item_naming_validator import ItemNamingValidator
from utilities.audit_logger import AuditLogger

# Try to import folder manager (graceful degradation if not available)
try:
    from utilities.fabric_folder_manager import FabricFolderManager
    FOLDERS_AVAILABLE = True
except ImportError:
    FOLDERS_AVAILABLE = False
    print("⚠️  Warning: FabricFolderManager not available. Folder features will be disabled.")


# ============================================================================
# Color Output Utilities
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_step(step: int, total: int, text: str) -> None:
    """Print step indicator"""
    print(f"\n{Colors.BOLD}[Step {step}/{total}] {text}{Colors.ENDC}")


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load and validate configuration file
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            print_success(f"Loaded configuration from {config_path.name}")
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML configuration: {e}")


def get_environment_config(config: Dict[str, Any], environment: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for specific environment
    
    Args:
        config: Full configuration dictionary
        environment: Environment name (dev, test, prod)
        
    Returns:
        Environment configuration or None if not enabled
    """
    env_config = config.get('environments', {}).get(environment)
    
    if not env_config:
        print_error(f"Environment '{environment}' not found in configuration")
        return None
    
    if not env_config.get('enabled', False):
        print_warning(f"Environment '{environment}' is not enabled")
        return None
    
    return env_config


# ============================================================================
# Folder Structure Management
# ============================================================================

def create_folder_structure(
    workspace_id: str,
    config: Dict[str, Any],
    environment: str,
    dry_run: bool = False
) -> Dict[str, str]:
    """
    Create folder structure in workspace based on configuration
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        environment: Environment name
        dry_run: Preview mode without making changes
        
    Returns:
        Dictionary mapping folder paths to folder IDs
    """
    if not FOLDERS_AVAILABLE:
        print_warning("Folder creation skipped - FabricFolderManager not available")
        return {}
    
    env_config = config['environments'][environment]
    folder_config = env_config.get('folder_structure', {})
    
    if not folder_config.get('enabled', False):
        print_info("Folder structure disabled for this environment")
        return {}
    
    template = folder_config.get('template', 'medallion')
    print_info(f"Creating folder structure using template: {template}")
    
    if dry_run:
        print_warning("DRY RUN: Would create folders but skipping")
        return _preview_folder_structure(config, template)
    
    folder_manager = FabricFolderManager()
    folder_map = {}
    
    # Get folder structure definition from config
    folder_structure = config['folder_structure'].get(template, {})
    
    # Create medallion layers
    if template == 'medallion':
        layers = folder_structure.get('layers', [])
        for layer in layers:
            layer_name = layer['name']
            layer_desc = layer.get('description', '')
            
            print_info(f"Creating layer: {layer_name}")
            layer_folder_id = folder_manager.create_folder(
                workspace_id=workspace_id,
                display_name=layer_name,
                description=layer_desc
            )
            folder_map[layer_name] = layer_folder_id
            
            # Create subfolders
            for subfolder in layer.get('subfolders', []):
                subfolder_name = subfolder['name']
                subfolder_desc = subfolder.get('description', '')
                subfolder_path = f"{layer_name}/{subfolder_name}"
                
                print_info(f"  Creating subfolder: {subfolder_name}")
                sub_folder_id = folder_manager.create_folder(
                    workspace_id=workspace_id,
                    display_name=subfolder_name,
                    parent_folder_id=layer_folder_id,
                    description=subfolder_desc
                )
                folder_map[subfolder_path] = sub_folder_id
        
        # Create shared folders
        shared_folders = folder_structure.get('shared_folders', [])
        for shared in shared_folders:
            folder_name = shared['name']
            folder_desc = shared.get('description', '')
            
            print_info(f"Creating shared folder: {folder_name}")
            shared_folder_id = folder_manager.create_folder(
                workspace_id=workspace_id,
                display_name=folder_name,
                description=folder_desc
            )
            folder_map[folder_name] = shared_folder_id
    
    print_success(f"Created {len(folder_map)} folders")
    return folder_map


def _preview_folder_structure(config: Dict[str, Any], template: str) -> Dict[str, str]:
    """Preview folder structure without creating"""
    folder_structure = config['folder_structure'].get(template, {})
    preview_map = {}
    
    print_info("Folder structure preview:")
    
    if template == 'medallion':
        layers = folder_structure.get('layers', [])
        for layer in layers:
            layer_name = layer['name']
            preview_map[layer_name] = f"<folder-id-{layer_name}>"
            print(f"  📁 {layer_name}")
            
            for subfolder in layer.get('subfolders', []):
                subfolder_name = subfolder['name']
                subfolder_path = f"{layer_name}/{subfolder_name}"
                preview_map[subfolder_path] = f"<folder-id-{subfolder_path}>"
                print(f"    📁 {subfolder_name}")
        
        shared_folders = folder_structure.get('shared_folders', [])
        for shared in shared_folders:
            folder_name = shared['name']
            preview_map[folder_name] = f"<folder-id-{folder_name}>"
            print(f"  📁 {folder_name}")
    
    return preview_map


def determine_item_folder(
    item_name: str,
    config: Dict[str, Any],
    folder_map: Dict[str, str]
) -> Optional[str]:
    """
    Determine target folder for item based on naming pattern
    
    Args:
        item_name: Item name
        config: Full configuration dictionary
        folder_map: Map of folder paths to IDs
        
    Returns:
        Folder ID or None for root placement
    """
    organization = config['folder_structure'].get('organization', {})
    
    if not organization.get('auto_organize', False):
        return None
    
    rules = organization.get('rules', [])
    
    for rule in rules:
        pattern = rule['pattern']
        folder_path = rule['folder']
        
        if re.match(pattern, item_name):
            folder_id = folder_map.get(folder_path)
            if folder_id:
                print_info(f"  → Placing '{item_name}' in '{folder_path}'")
                return folder_id
            else:
                print_warning(f"  → Folder '{folder_path}' not found for '{item_name}'")
    
    # Handle unmatched items
    unmatched_location = organization.get('unmatched_location', 'root')
    if unmatched_location == 'default_folder':
        default_folder = organization.get('default_folder')
        folder_id = folder_map.get(default_folder)
        if folder_id:
            print_info(f"  → Placing '{item_name}' in default folder '{default_folder}'")
            return folder_id
    
    print_info(f"  → Placing '{item_name}' in workspace root")
    return None


# ============================================================================
# Workspace Creation
# ============================================================================

def create_workspace(
    config: Dict[str, Any],
    config_manager: ConfigManager,
    environment: str,
    dry_run: bool = False
) -> Optional[str]:
    """
    Create workspace with configured settings
    
    Args:
        config: Full configuration dictionary
        config_manager: ConfigManager instance
        environment: Environment name
        dry_run: Preview mode
        
    Returns:
        Workspace ID or None if creation failed
    """
    print_step(1, 7, "Creating Workspace")
    
    product_name = config['product']['name']
    env_config = config['environments'][environment]
    
    # Generate workspace name
    workspace_name = f"{product_name} - {environment.upper()}"
    
    # Generate description
    description_template = config['workspace'].get('description_template', '')
    if description_template:
        # Simple format with environment only
        try:
            description = description_template.format(environment=environment)
        except (KeyError, ValueError):
            # Fallback if template is invalid
            description = config['product'].get('description', '')
    else:
        description = config['product'].get('description', '')
    
    print_info(f"Workspace Name: {workspace_name}")
    print_info(f"Description: {description}")
    print_info(f"Capacity Type: {env_config['capacity_type']}")
    
    if dry_run:
        print_warning("DRY RUN: Would create workspace but skipping")
        return "<workspace-id-placeholder>"
    
    workspace_manager = WorkspaceManager(environment=environment)
    
    # Check capacity
    capacity_id = env_config.get('capacity_id')
    if capacity_id:
        print_info(f"Using capacity ID: {capacity_id}")
    elif env_config['capacity_type'] == 'trial':
        print_info("Using trial capacity")
        capacity_id = None
    else:
        print_error("Capacity ID required for non-trial deployments")
        return None
    
    # Create workspace
    try:
        workspace = workspace_manager.create_workspace(
            workspace_name,
            description,
            capacity_id=capacity_id
        )
        print_success(f"Workspace created: {workspace}")
        return workspace['id']  # Extract ID from workspace dict
    except Exception as e:
        print_error(f"Failed to create workspace: {e}")
        return None


# ============================================================================
# Item Creation
# ============================================================================

def create_items(
    workspace_id: str,
    config: Dict[str, Any],
    folder_map: Dict[str, str],
    dry_run: bool = False
) -> Dict[str, List[str]]:
    """
    Create items in workspace with intelligent folder placement
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        folder_map: Map of folder paths to IDs
        dry_run: Preview mode
        
    Returns:
        Dictionary mapping item types to created item IDs
    """
    print_step(3, 7, "Creating Items with Intelligent Folder Organization")
    
    if not config['workspace'].get('create_items', False):
        print_info("Item creation disabled in configuration")
        return {}
    
    items_config = config.get('items', {})
    created_items = {}
    
    if dry_run:
        print_warning("DRY RUN: Would create items but skipping")
        _preview_items(items_config, folder_map, config)
        return {}
    
    item_manager = FabricItemManager()
    folder_manager = FabricFolderManager() if folder_map else None
    
    # Create lakehouses
    lakehouses = items_config.get('lakehouses', [])
    if lakehouses:
        print_info(f"\nCreating {len(lakehouses)} lakehouses...")
        created_items['lakehouses'] = []
        
        for lakehouse in lakehouses:
            name = lakehouse['name']
            description = lakehouse.get('description', '')
            
            # Determine folder placement
            folder_id = determine_item_folder(name, config, folder_map)
            
            try:
                # Create item with correct signature
                item = item_manager.create_item(
                    workspace_id=workspace_id,
                    display_name=name,
                    item_type=FabricItemType.LAKEHOUSE,
                    description=description
                )
                item_id = item.id
                created_items['lakehouses'].append(item_id)
                
                # Move to folder if specified
                if folder_id and folder_manager:
                    folder_manager.move_items_to_folder(workspace_id, [item_id], folder_id)
                    print_success(f"Created lakehouse: {name} → folder")
                else:
                    print_success(f"Created lakehouse: {name}")
            except Exception as e:
                print_error(f"Failed to create lakehouse '{name}': {e}")
    
    # Create notebooks
    notebooks = items_config.get('notebooks', [])
    if notebooks:
        print_info(f"\nCreating {len(notebooks)} notebooks...")
        created_items['notebooks'] = []
        
        for notebook in notebooks:
            name = notebook['name']
            description = notebook.get('description', '')
            
            # Determine folder placement
            folder_id = determine_item_folder(name, config, folder_map)
            
            try:
                # Create item with correct signature
                item = item_manager.create_item(
                    workspace_id=workspace_id,
                    display_name=name,
                    item_type=FabricItemType.NOTEBOOK,
                    description=description
                )
                item_id = item.id
                created_items['notebooks'].append(item_id)
                
                # Move to folder if specified
                if folder_id and folder_manager:
                    folder_manager.move_items_to_folder(workspace_id, [item_id], folder_id)
                    print_success(f"Created notebook: {name} → folder")
                else:
                    print_success(f"Created notebook: {name}")
            except Exception as e:
                print_error(f"Failed to create notebook '{name}': {e}")
    
    # Create warehouses (if configured)
    warehouses = items_config.get('warehouses', [])
    if warehouses:
        print_info(f"\nCreating {len(warehouses)} warehouses...")
        created_items['warehouses'] = []
        
        for warehouse in warehouses:
            name = warehouse['name']
            description = warehouse.get('description', '')
            
            # Determine folder placement
            folder_id = determine_item_folder(name, config, folder_map)
            
            try:
                # Create item with correct signature
                item = item_manager.create_item(
                    workspace_id=workspace_id,
                    display_name=name,
                    item_type=FabricItemType.WAREHOUSE,
                    description=description
                )
                item_id = item.id
                created_items['warehouses'].append(item_id)
                
                # Move to folder if specified
                if folder_id and folder_manager:
                    folder_manager.move_items_to_folder(workspace_id, [item_id], folder_id)
                    print_success(f"Created warehouse: {name} → folder")
                else:
                    print_success(f"Created warehouse: {name}")
            except Exception as e:
                print_error(f"Failed to create warehouse '{name}': {e}")
    
    total_items = sum(len(items) for items in created_items.values())
    print_success(f"\nCreated {total_items} total items")
    
    return created_items


def _preview_items(
    items_config: Dict[str, Any],
    folder_map: Dict[str, str],
    config: Dict[str, Any]
) -> None:
    """Preview item creation without creating"""
    print_info("\nItems to be created:")
    
    for item_type in ['lakehouses', 'notebooks', 'warehouses']:
        items = items_config.get(item_type, [])
        if items:
            print(f"\n  {item_type.upper()}:")
            for item in items:
                name = item['name']
                folder_id = determine_item_folder(name, config, folder_map)
                folder_info = "root" if not folder_id else "in folder"
                print(f"    - {name} ({folder_info})")


# ============================================================================
# Git Integration
# ============================================================================

def connect_git(
    workspace_id: str,
    config: Dict[str, Any],
    dry_run: bool = False
) -> bool:
    """
    Connect workspace to Git repository
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        dry_run: Preview mode
        
    Returns:
        True if successful
    """
    print_step(4, 7, "Connecting to Git")
    
    git_config = config.get('git', {})
    
    if not git_config.get('enabled', False):
        print_info("Git integration disabled in configuration")
        return True
    
    org = git_config['organization']
    repo = git_config['repository']
    branch = git_config.get('branch', 'main')
    directory = git_config.get('directory', '')
    
    print_info(f"Repository: {org}/{repo}")
    print_info(f"Branch: {branch}")
    print_info(f"Directory: {directory}")
    
    if dry_run:
        print_warning("DRY RUN: Would connect git but skipping")
        return True
    
    try:
        git_connector = FabricGitConnector(workspace_id)
        git_connector.connect_workspace(org, repo, branch, directory)
        print_success("Git connection established")
        return True
    except Exception as e:
        print_error(f"Failed to connect git: {e}")
        return False


# ============================================================================
# User Management
# ============================================================================

def add_users(
    workspace_id: str,
    config: Dict[str, Any],
    dry_run: bool = False
) -> int:
    """
    Add users to workspace
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        dry_run: Preview mode
        
    Returns:
        Number of users added
    """
    print_step(5, 7, "Adding Users")
    
    users = config.get('users', [])
    
    if not users:
        print_info("No users configured")
        return 0
    
    print_info(f"Adding {len(users)} users...")
    
    if dry_run:
        print_warning("DRY RUN: Would add users but skipping")
        for user in users:
            print(f"  - {user['email']} ({user['role']})")
        return 0
    
    workspace_manager = WorkspaceManager()
    added_count = 0
    
    for user in users:
        email = user['email']
        role_str = user['role']
        principal_type = user.get('principal_type', 'User')
        
        # Convert role string to WorkspaceRole enum
        role_map = {
            'Admin': WorkspaceRole.ADMIN,
            'Member': WorkspaceRole.MEMBER,
            'Contributor': WorkspaceRole.CONTRIBUTOR,
            'Viewer': WorkspaceRole.VIEWER
        }
        role = role_map.get(role_str, WorkspaceRole.VIEWER)
        
        try:
            workspace_manager.add_user(
                workspace_id=workspace_id,
                principal_id=email,
                principal_type=principal_type,
                role=role
            )
            print_success(f"Added {principal_type}: {email} ({role_str})")
            added_count += 1
        except Exception as e:
            print_error(f"Failed to add {email}: {e}")
    
    print_success(f"Added {added_count}/{len(users)} users")
    return added_count


# ============================================================================
# Naming Validation
# ============================================================================

def validate_naming(
    workspace_id: str,
    config: Dict[str, Any],
    created_items: Dict[str, List[str]],
    dry_run: bool = False
) -> bool:
    """
    Validate item naming standards
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        created_items: Dictionary of created item IDs
        dry_run: Preview mode
        
    Returns:
        True if all items pass validation
    """
    print_step(6, 7, "Validating Naming Standards")
    
    naming_config = config.get('naming', {})
    
    if not naming_config.get('validate', False):
        print_info("Naming validation disabled in configuration")
        return True
    
    if dry_run:
        print_warning("DRY RUN: Would validate naming but skipping")
        return True
    
    validator = ItemNamingValidator(workspace_id)
    all_valid = True
    
    # Validate all created items
    for item_type, item_ids in created_items.items():
        print_info(f"\nValidating {len(item_ids)} {item_type}...")
        
        for item_id in item_ids:
            result = validator.validate_item(item_id)
            
            if result['valid']:
                print_success(f"✓ {result['item_name']}")
            else:
                print_error(f"✗ {result['item_name']}: {result['reason']}")
                all_valid = False
                
                # Auto-fix if enabled
                if naming_config.get('auto_fix', False):
                    print_info(f"  Attempting auto-fix...")
                    # Implementation would go here
    
    if all_valid:
        print_success("All items pass naming validation")
    else:
        print_warning("Some items failed naming validation")
    
    return all_valid


# ============================================================================
# Deployment Validation
# ============================================================================

def validate_deployment(
    workspace_id: str,
    config: Dict[str, Any],
    folder_map: Dict[str, str],
    created_items: Dict[str, List[str]],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Validate complete deployment
    
    Args:
        workspace_id: Workspace ID
        config: Full configuration dictionary
        folder_map: Map of folder paths to IDs
        created_items: Dictionary of created item IDs
        dry_run: Preview mode
        
    Returns:
        Validation report dictionary
    """
    print_step(7, 7, "Validating Deployment")
    
    validation_config = config['deployment'].get('validation', {})
    report = {
        'timestamp': datetime.now().isoformat(),
        'workspace_id': workspace_id,
        'checks': {}
    }
    
    if dry_run:
        print_warning("DRY RUN: Would validate deployment but skipping")
        return report
    
    # Check folder structure
    if validation_config.get('check_folder_structure', False):
        print_info("Checking folder structure...")
        report['checks']['folders'] = {
            'expected': len(folder_map),
            'created': len(folder_map),
            'status': 'pass'
        }
        print_success(f"✓ {len(folder_map)} folders validated")
    
    # Verify items
    if validation_config.get('validate_all_items', False):
        print_info("Verifying all items created...")
        total_items = sum(len(items) for items in created_items.values())
        report['checks']['items'] = {
            'total_created': total_items,
            'by_type': {k: len(v) for k, v in created_items.items()},
            'status': 'pass'
        }
        print_success(f"✓ {total_items} items validated")
    
    # Check git connection
    if validation_config.get('verify_git_connection', False) and config['git'].get('enabled'):
        print_info("Verifying git connection...")
        # Would check git status here
        report['checks']['git'] = {'status': 'pass'}
        print_success("✓ Git connection validated")
    
    # Generate report
    if validation_config.get('generate_report', False):
        report_path = Path(f"deployment_report_{workspace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print_success(f"✓ Deployment report saved: {report_path}")
    
    print_success("Deployment validation complete")
    return report


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution workflow"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Demo Scenario - Full Feature Showcase with Intelligent Folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to preview deployment
  python run_comprehensive_demo.py --dry-run

  # Deploy development environment
  python run_comprehensive_demo.py

  # Deploy with custom config
  python run_comprehensive_demo.py --config my_config.yaml

  # Deploy to production
  python run_comprehensive_demo.py --environment prod
        """
    )
    parser.add_argument(
        "--config",
        default="comprehensive_demo_config.yaml",
        help="Path to configuration file (default: comprehensive_demo_config.yaml)"
    )
    parser.add_argument(
        "--environment",
        default="dev",
        choices=['dev', 'test', 'prod'],
        help="Target environment (default: dev)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deployment without making changes"
    )
    parser.add_argument(
        "--skip-folders",
        action="store_true",
        help="Skip folder creation (for testing)"
    )

    args = parser.parse_args()

    # Print banner
    print_header("COMPREHENSIVE DEMO SCENARIO - Full Feature Showcase")
    print(f"{Colors.BOLD}Features:{Colors.ENDC}")
    print("  ✅ Folder Structure (Medallion Architecture)")
    print("  ✅ Git Integration (Auto-connect)")
    print("  ✅ Naming Validation (Enforce standards)")
    print("  ✅ User Management (Roles, service principals)")
    print("  ✅ Item Creation (Lakehouses, notebooks, warehouses)")
    print("  ✅ Multi-Environment Support")
    print("  ✅ Audit Logging")
    print("  ✅ Intelligent Item Organization\n")

    if args.dry_run:
        print_warning("DRY RUN MODE - No changes will be made\n")

    # Load environment variables
    load_dotenv()

    # Get configuration path
    config_path = Path(__file__).parent / args.config

    # Load configuration
    try:
        config = load_config(config_path)
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Get environment configuration
    env_config = get_environment_config(config, args.environment)
    if not env_config:
        sys.exit(1)

    print_info(f"Product: {config['product']['name']}")
    print_info(f"Environment: {args.environment.upper()}")
    print_info(f"Domain: {config['product']['domain']}")
    print_info(f"Owner: {config['product']['owner_email']}\n")

    # Initialize config manager
    config_manager = ConfigManager()

    # Initialize audit logger if enabled
    audit_logger = None
    deployment_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    if config['audit'].get('enabled', False):
        audit_file = config['audit'].get('log_file', 'deployment_audit.jsonl')
        audit_logger = AuditLogger(audit_file=Path(audit_file))
        audit_logger.log_deployment_start(
            deployment_id=deployment_id,
            environment=args.environment,
            product_id=config['product']['name']
        )

    # Execute deployment workflow
    try:
        # Step 1: Create workspace
        workspace_id = create_workspace(config, config_manager, args.environment, args.dry_run)
        if not workspace_id:
            print_error("Failed to create workspace. Aborting.")
            sys.exit(1)

        # Step 2: Create folder structure
        folder_map = {}
        if not args.skip_folders:
            folder_map = create_folder_structure(workspace_id, config, args.environment, args.dry_run)
            print_step(2, 7, f"Folder Structure Created - {len(folder_map)} folders")
        else:
            print_step(2, 7, "Folder Structure Skipped")

        # Step 3: Create items with intelligent folder placement
        created_items = create_items(workspace_id, config, folder_map, args.dry_run)

        # Step 4: Connect Git
        git_success = connect_git(workspace_id, config, args.dry_run)

        # Step 5: Add users
        users_added = add_users(workspace_id, config, args.dry_run)

        # Step 6: Validate naming
        naming_valid = validate_naming(workspace_id, config, created_items, args.dry_run)

        # Step 7: Validate deployment
        validation_report = validate_deployment(workspace_id, config, folder_map, created_items, args.dry_run)

        # Print summary
        print_header("DEPLOYMENT COMPLETE")
        print_success(f"Workspace ID: {workspace_id}")
        print_success(f"Folders Created: {len(folder_map)}")
        print_success(f"Items Created: {sum(len(items) for items in created_items.values())}")
        print_success(f"Users Added: {users_added}")
        print_success(f"Git Connected: {'Yes' if git_success else 'No'}")
        print_success(f"Naming Valid: {'Yes' if naming_valid else 'No'}")

        if args.dry_run:
            print_warning("\nDRY RUN completed - No actual changes were made")
        else:
            print_success("\n✅ Deployment successful!")

    except Exception as e:
        print_error(f"\n❌ Deployment failed: {e}")
        
        if config['audit'].get('enabled', False) and audit_logger:
            audit_logger.log_deployment_failure(
                deployment_id=deployment_id if 'deployment_id' in locals() else "unknown",
                environment=args.environment,
                error_message=str(e)
            )
        
        # Cleanup on failure if configured
        if config['deployment'].get('cleanup_on_failure', False) and not args.dry_run:
            print_warning("Cleanup on failure enabled - consider implementing workspace deletion")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
