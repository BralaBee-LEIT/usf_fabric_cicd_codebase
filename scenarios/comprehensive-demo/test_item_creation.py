#!/usr/bin/env python3
"""
Quick test to verify item creation works with proper capacity
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "ops" / "scripts"))

from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from dotenv import load_dotenv

load_dotenv()

# Test workspace with capacity
WORKSPACE_ID = "0a12f805-fba7-4ea2-8e43-a5fe1bb9042e"  # Sales ETL Prod workspace

print("Testing item creation with Fabric capacity...")
print(f"Workspace ID: {WORKSPACE_ID}")
print()

# Create item manager
item_manager = FabricItemManager()

# Try to create a test lakehouse
test_lakehouse_name = "BRONZE_CapacityTest_Lakehouse"

try:
    print(f"Attempting to create: {test_lakehouse_name}")
    item = item_manager.create_item(
        workspace_id=WORKSPACE_ID,
        display_name=test_lakehouse_name,
        item_type=FabricItemType.LAKEHOUSE,
        description="Test lakehouse to verify capacity permissions",
        validate_naming=False  # Skip validation for this test
    )
    print(f"✅ SUCCESS! Created lakehouse: {item.display_name}")
    print(f"   Item ID: {item.id}")
    print()
    print("✅ Capacity is working! Item creation is enabled.")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print()
    if "403" in str(e) or "Forbidden" in str(e):
        print("❌ Error 403: Capacity permissions issue")
        print("   Possible causes:")
        print("   1. Workspace not assigned to the capacity")
        print("   2. Service principal lacks permissions on capacity")
        print("   3. Capacity ID is invalid")
    else:
        print("❌ Unexpected error - see details above")
