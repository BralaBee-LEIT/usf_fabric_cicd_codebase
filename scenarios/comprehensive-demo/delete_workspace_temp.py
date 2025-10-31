#!/usr/bin/env python3
"""Quick script to delete a specific workspace"""
import sys
sys.path.insert(0, '../../')

from dotenv import load_dotenv
from ops.scripts.utilities.workspace_manager import WorkspaceManager

if __name__ == "__main__":
    load_dotenv()
    wm = WorkspaceManager()
    
    # Find by name pattern
    workspaces = wm.list_workspaces()
    ws = [w for w in workspaces if 'usf2-fabric-sales-analytics-etl-dev' in w['displayName']]
    
    if ws:
        ws_id = ws[0]['id']
        ws_name = ws[0]['displayName']
        print(f"Deleting workspace: {ws_name}")
        print(f"ID: {ws_id}")
        
        wm.delete_workspace(ws_id, force=True)
        print(f"✅ Successfully deleted workspace")
    else:
        print(f"⚠️ No matching workspace found")
