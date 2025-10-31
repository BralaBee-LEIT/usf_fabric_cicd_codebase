#!/usr/bin/env python3
"""
Organize Existing Items into Folders
=====================================

This script demonstrates intelligent folder placement by moving
existing items in a workspace into their appropriate folders based
on naming conventions.

Usage:
    python organize_items_into_folders.py --workspace-id <guid>
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "ops" / "scripts"))

from utilities.fabric_folder_manager import FabricFolderManager
from utilities.fabric_item_manager import FabricItemManager

# Load environment
load_dotenv()


def organize_items(workspace_id: str):
    """Organize items into folders based on naming patterns"""
    
    print(f"\n{'='*80}")
    print(f"  Organizing Items with Intelligent Folder Placement")
    print(f"{'='*80}\n")
    
    # Initialize managers
    folder_manager = FabricFolderManager()
    item_manager = FabricItemManager()
    
    # Get folder structure
    print("📁 Retrieving folder structure...")
    structure = folder_manager.get_folder_structure(workspace_id)
    
    # Build folder map using the FolderStructure API
    folder_map = {}
    
    def add_folder_to_map(folder_info, parent_path=""):
        """Recursively add folders to map"""
        current_path = f"{parent_path}/{folder_info.display_name}" if parent_path else folder_info.display_name
        folder_map[current_path] = folder_info.id
        folder_map[folder_info.display_name] = folder_info.id
        
        # Get children from structure
        children = structure.get_children(folder_info.id)
        for child in children:
            add_folder_to_map(child, current_path)
    
    # Process all root folders
    for folder in structure.root_folders:
        add_folder_to_map(folder)
    
    print(f"✓ Found {len(set(folder_map.values()))} unique folders")
    print(f"  Sample folders:")
    for name in list(folder_map.keys())[:8]:
        print(f"    - {name}")
    print()
    
    # Get all items in workspace
    print("📦 Retrieving workspace items...")
    from utilities.fabric_api import FabricClient
    client = FabricClient()
    response = client._make_request('GET', f'/workspaces/{workspace_id}/items')
    
    # Handle response properly - it's a requests.Response object
    if hasattr(response, 'json'):
        items_data = response.json()
        items = items_data.get('value', [])
    else:
        items = []
    
    # Filter out SQL endpoints (created automatically with lakehouses)
    items = [item for item in items if item['type'] != 'SQLEndpoint']
    
    print(f"✓ Found {len(items)} items\n")
    
    # Define placement rules
    def determine_folder(item_name: str, item_type: str):
        """Determine folder based on naming pattern"""
        if item_type == 'Lakehouse':
            if item_name.startswith('BRONZE_'):
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
        
        elif item_type == 'Notebook':
            if '_' in item_name:
                prefix = item_name.split('_')[0]
                try:
                    num = int(prefix)
                    if 1 <= num <= 9:
                        for folder_name in ['Bronze Layer/Raw Data', 'Raw Data', 'Bronze Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                    elif 10 <= num <= 19:
                        for folder_name in ['Silver Layer/Transformed', 'Transformed', 'Silver Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                    elif 20 <= num <= 29:
                        for folder_name in ['Gold Layer/Analytics', 'Analytics', 'Gold Layer']:
                            if folder_name in folder_map:
                                return (folder_map[folder_name], folder_name)
                except ValueError:
                    pass
        
        return (None, 'Root')
    
    # Organize items
    print("🎯 Organizing items into folders...\n")
    organized_count = 0
    
    for item in items:
        item_name = item['displayName']
        item_type = item['type']
        item_id = item['id']
        
        # Skip test items
        if 'Test' in item_name or 'CapacityTest' in item_name:
            continue
        
        folder_id, folder_name = determine_folder(item_name, item_type)
        
        if folder_id:
            try:
                print(f"  Moving: {item_name}")
                print(f"    → Target: {folder_name}")
                
                folder_manager.move_items_to_folder(
                    workspace_id=workspace_id,
                    item_ids=[item_id],
                    target_folder_id=folder_id
                )
                
                print(f"    ✓ Moved successfully\n")
                organized_count += 1
                
            except Exception as e:
                print(f"    ✗ Failed: {e}\n")
        else:
            print(f"  Keeping at root: {item_name}\n")
    
    print(f"\n{'='*80}")
    print(f"  Summary")
    print(f"{'='*80}\n")
    print(f"✓ Organized {organized_count} items into folders")
    print(f"✓ Total items processed: {len(items)}")
    print(f"\n🎉 Organization complete!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize items into folders intelligently")
    parser.add_argument('--workspace-id', required=True, help='Workspace ID')
    args = parser.parse_args()
    
    organize_items(args.workspace_id)
