#!/usr/bin/env python3
"""
Test script to move existing items into their designated folders
This demonstrates the bulk move API functionality
"""

from ops.scripts.utilities.fabric_folder_manager import FabricFolderManager
from dotenv import load_dotenv
import sys

load_dotenv()

def print_colored(text, color='white'):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'white': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}\033[0m")

def main():
    workspace_id = '8ef68ccc-c5d6-4140-8b6f-a77f78eebebc'
    
    print_colored("\n" + "="*70, 'cyan')
    print_colored("  Testing Bulk Item Move to Folders", 'cyan')
    print_colored("="*70 + "\n", 'cyan')
    
    mgr = FabricFolderManager()
    
    # Get all folders
    print_colored("Step 1: Fetching folder structure...", 'blue')
    folders = mgr.list_folders(workspace_id)
    folder_map = {f.display_name: f.id for f in folders}
    
    print_colored(f"✓ Found {len(folders)} folders", 'green')
    for name, fid in folder_map.items():
        print(f"  - {name}: {fid[:8]}...")
    
    # Get items at root
    print_colored("\nStep 2: Fetching items at root...", 'blue')
    root_items = mgr.list_folder_items(workspace_id, None)
    
    # Filter to only Lakehouses and Notebooks (not SQLEndpoints)
    items_to_move = [
        item for item in root_items 
        if item['type'] in ['Lakehouse', 'Notebook']
    ]
    
    print_colored(f"✓ Found {len(items_to_move)} items to move", 'green')
    
    # Define placement rules
    placement_rules = {
        # Lakehouses
        'BRONZE_': 'Raw Data',
        'SILVER_': 'Transformed',
        'GOLD_': 'Analytics',
        # Notebooks by number
        '01_': 'Raw Data',
        '02_': 'Raw Data',
        '10_': 'Transformed',
        '11_': 'Transformed',
        '20_': 'Analytics',
        '21_': 'Analytics',
        '50_': None,  # Root (Orchestration)
        '70_': None,  # Root (Data Quality)
    }
    
    # Group items by target folder
    folder_groups = {}
    for item in items_to_move:
        name = item['displayName']
        item_id = item['id']
        
        # Determine target folder
        target_folder = None
        for prefix, folder_name in placement_rules.items():
            if name.startswith(prefix):
                target_folder = folder_name
                break
        
        # Skip if staying at root
        if target_folder is None:
            print_colored(f"  Keeping at root: {name}", 'yellow')
            continue
        
        # Get folder ID
        if target_folder not in folder_map:
            print_colored(f"  ⚠ Folder not found: {target_folder} for {name}", 'red')
            continue
        
        folder_id = folder_map[target_folder]
        
        if folder_id not in folder_groups:
            folder_groups[folder_id] = {
                'folder_name': target_folder,
                'items': []
            }
        
        folder_groups[folder_id]['items'].append({
            'id': item_id,
            'name': name,
            'type': item['type']
        })
    
    print_colored(f"\nStep 3: Moving items to {len(folder_groups)} folders...", 'blue')
    
    total_moved = 0
    total_failed = 0
    
    for folder_id, group in folder_groups.items():
        folder_name = group['folder_name']
        items = group['items']
        item_ids = [item['id'] for item in items]
        
        print_colored(f"\n  Moving {len(items)} items to '{folder_name}':", 'cyan')
        for item in items:
            print(f"    - {item['name']} ({item['type']})")
        
        try:
            results = mgr.move_items_to_folder(
                workspace_id=workspace_id,
                item_ids=item_ids,
                target_folder_id=folder_id
            )
            
            success_count = sum(results.values())
            fail_count = len(results) - success_count
            
            if success_count == len(items):
                print_colored(f"  ✓ All {success_count} items moved successfully", 'green')
                total_moved += success_count
            else:
                print_colored(f"  ⚠ {success_count}/{len(items)} items moved", 'yellow')
                total_moved += success_count
                total_failed += fail_count
                
                # Show failures
                for item in items:
                    if not results.get(item['id'], False):
                        print_colored(f"    ✗ Failed: {item['name']}", 'red')
        
        except Exception as e:
            print_colored(f"  ✗ Error moving to '{folder_name}': {e}", 'red')
            total_failed += len(items)
    
    # Final summary
    print_colored("\n" + "="*70, 'cyan')
    print_colored("  Summary", 'cyan')
    print_colored("="*70, 'cyan')
    print_colored(f"  ✓ Successfully moved: {total_moved} items", 'green')
    if total_failed > 0:
        print_colored(f"  ✗ Failed: {total_failed} items", 'red')
    print_colored("="*70 + "\n", 'cyan')
    
    # Verify final state
    print_colored("Step 4: Verifying final folder structure...", 'blue')
    for folder_name in ['Raw Data', 'Transformed', 'Analytics']:
        if folder_name in folder_map:
            folder_id = folder_map[folder_name]
            items = mgr.list_folder_items(workspace_id, folder_id)
            print_colored(f"\n  {folder_name}: {len(items)} items", 'green')
            for item in items:
                if item['type'] in ['Lakehouse', 'Notebook']:
                    print(f"    - {item['displayName']} ({item['type']})")
    
    print_colored("\n✓ Test complete!", 'green')
    return 0

if __name__ == "__main__":
    sys.exit(main())
