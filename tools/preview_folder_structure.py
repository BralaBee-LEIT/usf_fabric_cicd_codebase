#!/usr/bin/env python3
"""
Preview Folder Structure - No Credentials Required
Shows what folder structure would be created without connecting to Fabric
"""

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def print_success(msg): print(f"{GREEN}{msg}{END}")
def print_info(msg): print(f"{BLUE}{msg}{END}")
def print_warning(msg): print(f"{YELLOW}{msg}{END}")

# Medallion Architecture Template
MEDALLION_STRUCTURE = {
    "name": "Medallion Architecture",
    "description": "Bronze/Silver/Gold data lake structure",
    "folders": [
        {
            "name": "Bronze Layer",
            "description": "Raw data ingestion layer",
            "subfolders": [
                {"name": "Raw Data", "description": "Ingested raw data"},
                {"name": "Archive", "description": "Historical data archive"},
                {"name": "External Sources", "description": "Third-party data sources"}
            ]
        },
        {
            "name": "Silver Layer",
            "description": "Cleansed and validated data",
            "subfolders": [
                {"name": "Cleaned", "description": "Cleansed datasets"},
                {"name": "Transformed", "description": "Transformed data"},
                {"name": "Validated", "description": "Quality validated data"}
            ]
        },
        {
            "name": "Gold Layer",
            "description": "Analytics-ready data",
            "subfolders": [
                {"name": "Analytics", "description": "Analytics datasets"},
                {"name": "Reports", "description": "Report-ready data"},
                {"name": "Business Metrics", "description": "Business KPIs and metrics"}
            ]
        }
    ]
}

TEMPLATES = {
    "medallion": MEDALLION_STRUCTURE,
}


def preview_structure(template_name="medallion"):
    """Preview folder structure without credentials"""
    
    if template_name not in TEMPLATES:
        print_warning(f"Unknown template: {template_name}")
        print_info(f"Available templates: {', '.join(TEMPLATES.keys())}")
        return
    
    template = TEMPLATES[template_name]
    
    print_success(f"\n🔍 DRY RUN - Preview of '{template['name']}' Structure")
    print_info(f"Description: {template['description']}\n")
    
    print_info("📁 Folder Structure:")
    print_info("=" * 80)
    
    total_folders = 0
    
    for folder in template["folders"]:
        print_success(f"\n├── {folder['name']}")
        print_info(f"│   └── {folder['description']}")
        total_folders += 1
        
        if "subfolders" in folder:
            for i, subfolder in enumerate(folder["subfolders"]):
                is_last = i == len(folder["subfolders"]) - 1
                prefix = "└──" if is_last else "├──"
                print_success(f"│   {prefix} {subfolder['name']}")
                print_info(f"│       └── {subfolder['description']}")
                total_folders += 1
    
    print_info("\n" + "=" * 80)
    print_success(f"\n✅ Total Folders: {total_folders}")
    print_warning("\n⚠️  This is a preview only - no folders created!")
    print_info("\nTo create this structure, run:")
    print_info(f"  python tools/manage_fabric_folders.py create-structure \\")
    print_info(f"      --workspace \"Your Workspace Name\" \\")
    print_info(f"      --template {template_name}")


def preview_intelligent_placement():
    """Preview intelligent item placement rules"""
    
    print_success("\n🎯 Intelligent Item Placement Rules")
    print_info("=" * 80)
    
    rules = [
        ("BRONZE_*", "Bronze Layer/Raw Data", "Items prefixed with BRONZE_"),
        ("SILVER_*", "Silver Layer/Cleaned", "Items prefixed with SILVER_"),
        ("GOLD_*", "Gold Layer/Analytics", "Items prefixed with GOLD_"),
        ("01-09_*", "Bronze Layer/Raw Data", "Notebooks numbered 01-09"),
        ("10-19_*", "Silver Layer/Transformed", "Notebooks numbered 10-19"),
        ("20-29_*", "Gold Layer/Analytics", "Notebooks numbered 20-29"),
        ("50+_*", "Workspace Root", "Notebooks numbered 50+"),
    ]
    
    print_info("\nItem Naming Pattern → Target Folder")
    print_info("-" * 80)
    
    for pattern, folder, description in rules:
        print_success(f"  {pattern:15} → {folder}")
        print_info(f"                    ({description})")
    
    print_info("\n" + "=" * 80)
    print_info("\n💡 Examples:")
    print_success("  BRONZE_SalesData_Lakehouse  → Bronze Layer/Raw Data")
    print_success("  01_IngestData_Notebook      → Bronze Layer/Raw Data")
    print_success("  SILVER_Cleaned_Lakehouse    → Silver Layer/Cleaned")
    print_success("  10_Transform_Notebook       → Silver Layer/Transformed")
    print_success("  GOLD_Analytics_Lakehouse    → Gold Layer/Analytics")
    print_success("  20_BuildKPIs_Notebook       → Gold Layer/Analytics")
    print_success("  50_Orchestration_Notebook   → Workspace Root")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Preview folder structures without credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--template",
        default="medallion",
        choices=["medallion"],
        help="Template to preview (default: medallion)"
    )
    
    parser.add_argument(
        "--show-placement",
        action="store_true",
        help="Show intelligent item placement rules"
    )
    
    args = parser.parse_args()
    
    # Preview structure
    preview_structure(args.template)
    
    # Show placement rules if requested
    if args.show_placement:
        preview_intelligent_placement()
    
    print()


if __name__ == "__main__":
    main()
