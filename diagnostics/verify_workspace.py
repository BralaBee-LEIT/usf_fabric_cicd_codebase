#!/usr/bin/env python3
"""Verify workspace exists in Microsoft Fabric."""
import sys
from pathlib import Path

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent / "ops" / "scripts" / "utilities"))

# Load environment
import os
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with env_file.open('r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, value = line.split('=', 1)
                key = key.strip()
                if key not in os.environ:
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

from workspace_manager import WorkspaceManager

print("🔍 Checking workspaces in Microsoft Fabric...")
print()

mgr = WorkspaceManager()
workspaces = mgr.list_workspaces()

print(f"Total workspaces found: {len(workspaces)}")
print()

# Check for Customer Analytics
customer_analytics = [ws for ws in workspaces if "Customer Analytics" in ws['displayName']]

if customer_analytics:
    print("✅ Found Customer Analytics workspace(s):")
    for ws in customer_analytics:
        print(f"   - Name: {ws['displayName']}")
        print(f"     ID: {ws['id']}")
        print(f"     URL: https://app.fabric.microsoft.com/groups/{ws['id']}")
        print()
else:
    print("❌ Customer Analytics workspace NOT found in Fabric")
    print()
    print("Registry says it should exist:")
    print("   - Name: Customer Analytics [DEV]")
    print("   - ID: be8d1df8-9067-4557-a179-fd706a38dd20")
    print()
    print("Possible reasons:")
    print("   1. Workspace was created but soft-deleted (check Fabric portal trash)")
    print("   2. Different tenant/environment than expected")
    print("   3. Permission issue (service principal can't see workspace)")
    print()

print("All workspaces:")
for ws in workspaces:
    print(f"   - {ws['displayName']} ({ws['id']})")
