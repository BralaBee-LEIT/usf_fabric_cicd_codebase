#!/usr/bin/env python3
"""Verify folder placement of items in workspace"""
import sys
sys.path.insert(0, '../../')

from dotenv import load_dotenv
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.fabric_folder_manager import FabricFolderManager

load_dotenv()

wm = WorkspaceManager()
fm = FabricFolderManager()

# Find latest workspace
workspaces = wm.list_workspaces()
ws = [w for w in workspaces if 'usf2-fabric-sales-analytics-etl-dev' in w['displayName']]

if ws:
    ws_id = ws[0]['id']
    ws_name = ws[0]['displayName']
    
    print(f'Workspace: {ws_name}')
    print(f'ID: {ws_id[:8]}...')
    print()
    
    # Check folders and items
    structure = fm.get_folder_structure(ws_id)
    root_items = fm.list_folder_items(ws_id, None)
    
    total_folders = len(structure.root_folders) + sum(len(structure.get_children(f.id)) for f in structure.root_folders)
    print(f'Total folders: {total_folders}')
    
    root_lh = len([i for i in root_items if i['type'] == 'Lakehouse'])
    root_nb = len([i for i in root_items if i['type'] == 'Notebook'])
    print(f'ROOT: {root_lh} LH, {root_nb} NB')
    print()
    
    # Check each main folder and its subfolders
    for folder in structure.root_folders:
        subfolders = structure.get_children(folder.id)
        for subfolder in subfolders:
            items = fm.list_folder_items(ws_id, subfolder.id)
            lh = len([i for i in items if i['type'] == 'Lakehouse'])
            nb = len([i for i in items if i['type'] == 'Notebook'])
            if lh + nb > 0:
                print(f'✅ {folder.display_name}/{subfolder.display_name}: {lh} LH, {nb} NB')
    
    # Summary
    print()
    if root_lh + root_nb == 0:
        print('✅ SUCCESS: All items placed in folders!')
    else:
        print(f'⚠️ ISSUE: {root_lh + root_nb} items still at ROOT')
else:
    print('⚠️ No workspace found')
