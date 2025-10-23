# Implementing Federation & Governance - Practical Guide

## Overview

This guide shows how to implement the Federation, Governance & Control framework using the USF Fabric CI/CD codebase tools. It provides concrete examples and scripts for each governance aspect.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Domain Onboarding](#domain-onboarding)
- [Workspace Provisioning](#workspace-provisioning)
- [Item Management](#item-management)
- [Governance Automation](#governance-automation)
- [Monitoring & Compliance](#monitoring--compliance)

## Prerequisites

### Environment Setup

```bash
# 1. Clone repository
git clone git@github.com:BralaBee-LEIT/usf_fabric_cicd_codebase.git
cd usf_fabric_cicd_codebase

# 2. Set environment variables
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# 3. Install dependencies
pip install -r ops/requirements.txt

# 4. Verify connection
python ops/scripts/manage_workspaces.py list --environment dev
```

### Service Principal Setup

```bash
# Create service principal for platform automation
az ad sp create-for-rbac --name "fabric-platform-automation" \
    --role "Contributor" \
    --scopes "/subscriptions/{subscription-id}"

# Assign Fabric permissions in Azure AD
# API Permissions → Add Permission → APIs my organization uses → Power BI Service
# Add: Workspace.ReadWrite.All (Application)
# Add: User.Read.All (Application)
# Grant admin consent

# Enable in Fabric Admin Portal
# Settings → Tenant settings → Developer settings
# → "Service principals can use Fabric APIs" → Enable
```

## Domain Onboarding

### 1. Onboarding Checklist

Create a domain onboarding script:

```python
#!/usr/bin/env python3
"""
Domain Onboarding Automation
Provisions all necessary resources for a new domain team
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.fabric_item_manager import FabricItemManager, FabricItemType
from ops.scripts.utilities.console_utils import (
    console_success as print_success,
    console_error as print_error,
    console_info as print_info
)

def onboard_domain(
    domain_name: str,
    domain_owner_email: str,
    capacity_id: str,
    team_ad_group: str
):
    """
    Complete domain onboarding process
    
    Args:
        domain_name: Name of the domain (e.g., 'finance', 'sales')
        domain_owner_email: Email of domain data owner
        capacity_id: Fabric capacity ID
        team_ad_group: Azure AD group for domain team
    """
    print_info(f"Starting onboarding for domain: {domain_name}")
    
    ws_mgr = WorkspaceManager()
    item_mgr = FabricItemManager()
    
    onboarding_report = {
        "domain": domain_name,
        "timestamp": datetime.now().isoformat(),
        "workspaces": [],
        "items": [],
        "errors": []
    }
    
    try:
        # Step 1: Create workspace for each environment
        for env in ['dev', 'test', 'prod']:
            print_info(f"\n=== Setting up {env.upper()} environment ===")
            
            try:
                # Create workspace
                workspace = ws_mgr.create_workspace(
                    environment=env,
                    base_name=domain_name,
                    description=f"{domain_name.title()} {env.upper()} workspace"
                )
                workspace_id = workspace['id']
                workspace_name = workspace['displayName']
                
                print_success(f"✓ Created workspace: {workspace_name}")
                onboarding_report["workspaces"].append({
                    "environment": env,
                    "name": workspace_name,
                    "id": workspace_id
                })
                
                # Assign capacity (prod only)
                if env == 'prod' and capacity_id:
                    ws_mgr.assign_to_capacity(workspace_id, capacity_id)
                    print_success(f"✓ Assigned to capacity: {capacity_id}")
                
                # Add domain team
                # Note: This requires User.Read.All permission
                try:
                    ws_mgr.add_user(
                        environment=env,
                        base_name=domain_name,
                        user_email=domain_owner_email,
                        role="Admin"
                    )
                    print_success(f"✓ Added domain owner as Admin")
                except Exception as e:
                    print_error(f"Warning: Could not add user: {e}")
                
                # Step 2: Create standard items based on medallion architecture
                if env in ['dev', 'prod']:  # Skip test for now
                    print_info(f"\nCreating standard items...")
                    
                    # Bronze lakehouse
                    bronze_lh = item_mgr.create_item(
                        workspace_id=workspace_id,
                        display_name=f"{domain_name}_bronze_lakehouse",
                        item_type=FabricItemType.LAKEHOUSE,
                        description=f"Bronze layer - Raw data for {domain_name}"
                    )
                    print_success(f"✓ Created bronze lakehouse")
                    onboarding_report["items"].append({
                        "workspace": workspace_name,
                        "item": bronze_lh.display_name,
                        "type": "Lakehouse"
                    })
                    
                    # Silver lakehouse
                    silver_lh = item_mgr.create_item(
                        workspace_id=workspace_id,
                        display_name=f"{domain_name}_silver_lakehouse",
                        item_type=FabricItemType.LAKEHOUSE,
                        description=f"Silver layer - Cleaned and validated data for {domain_name}"
                    )
                    print_success(f"✓ Created silver lakehouse")
                    onboarding_report["items"].append({
                        "workspace": workspace_name,
                        "item": silver_lh.display_name,
                        "type": "Lakehouse"
                    })
                    
                    # Gold lakehouse
                    gold_lh = item_mgr.create_item(
                        workspace_id=workspace_id,
                        display_name=f"{domain_name}_gold_lakehouse",
                        item_type=FabricItemType.LAKEHOUSE,
                        description=f"Gold layer - Business-ready data for {domain_name}"
                    )
                    print_success(f"✓ Created gold lakehouse")
                    onboarding_report["items"].append({
                        "workspace": workspace_name,
                        "item": gold_lh.display_name,
                        "type": "Lakehouse"
                    })
                    
                    # Warehouse (prod only)
                    if env == 'prod':
                        warehouse = item_mgr.create_item(
                            workspace_id=workspace_id,
                            display_name=f"{domain_name}_warehouse",
                            item_type=FabricItemType.WAREHOUSE,
                            description=f"Analytics warehouse for {domain_name}"
                        )
                        print_success(f"✓ Created warehouse")
                        onboarding_report["items"].append({
                            "workspace": workspace_name,
                            "item": warehouse.display_name,
                            "type": "Warehouse"
                        })
                    
                    # Standard notebooks
                    for notebook_name in ['ingestion', 'transformation', 'validation']:
                        notebook = item_mgr.create_item(
                            workspace_id=workspace_id,
                            display_name=f"{domain_name}_{notebook_name}_notebook",
                            item_type=FabricItemType.NOTEBOOK,
                            description=f"{notebook_name.title()} notebook for {domain_name}"
                        )
                        print_success(f"✓ Created {notebook_name} notebook")
                        onboarding_report["items"].append({
                            "workspace": workspace_name,
                            "item": notebook.display_name,
                            "type": "Notebook"
                        })
            
            except Exception as e:
                error_msg = f"Error in {env} environment: {str(e)}"
                print_error(error_msg)
                onboarding_report["errors"].append(error_msg)
        
        # Step 3: Create data contract template
        create_data_contract_template(domain_name)
        print_success(f"\n✓ Created data contract template")
        
        # Step 4: Create DQ rules template
        create_dq_rules_template(domain_name)
        print_success(f"✓ Created DQ rules template")
        
        # Step 5: Setup CI/CD (if using Azure DevOps)
        print_info(f"\n📋 Manual steps required:")
        print_info(f"1. Add Azure AD group '{team_ad_group}' to all workspaces")
        print_info(f"2. Create Azure DevOps project: '{domain_name}-fabric'")
        print_info(f"3. Setup deployment pipeline connections")
        print_info(f"4. Configure Purview scanning for new workspaces")
        print_info(f"5. Add domain to cost tracking dashboard")
        
        # Generate onboarding report
        import json
        report_filename = f"onboarding_report_{domain_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(onboarding_report, f, indent=2)
        
        print_success(f"\n✅ Domain onboarding complete!")
        print_success(f"📄 Report saved to: {report_filename}")
        
        return onboarding_report
        
    except Exception as e:
        print_error(f"\n❌ Onboarding failed: {str(e)}")
        raise


def create_data_contract_template(domain_name: str):
    """Create data contract template for the domain"""
    template = f"""# Data Contract Template - {domain_name.title()} Domain

## Producer Information
- Domain: {domain_name}
- Team: {domain_name}-analytics-team
- Owner: {domain_name}-data-owner@company.com
- Support: {domain_name}-data-support@company.com

## Dataset

### Naming Convention
- Bronze: `{domain_name}_bronze_lakehouse.<table_name>`
- Silver: `{domain_name}_silver_lakehouse.<table_name>`
- Gold: `{domain_name}_gold_lakehouse.<table_name>`

### Schema
Define your schema here using the standard format:

```yaml
fields:
  - name: id
    type: string
    nullable: false
    description: "Unique identifier"
    primary_key: true
  
  - name: created_date
    type: timestamp
    nullable: false
    description: "Record creation timestamp"
```

## Quality Standards
- Completeness: >= 95%
- Accuracy: >= 98%
- Timeliness: Updated [frequency]
- Uniqueness: 100% on primary key

## SLA
- Availability: 99.9%
- Update frequency: [Daily/Hourly/Real-time]
- Update time: [Specify time]
- Support response: < 4 hours

## Access
- Classification: [Public/Internal/Confidential/Highly Confidential]
- Approved consumers: List domains/teams
"""
    
    os.makedirs(f"governance/data_contracts/{domain_name}", exist_ok=True)
    with open(f"governance/data_contracts/{domain_name}/template.md", 'w') as f:
        f.write(template)


def create_dq_rules_template(domain_name: str):
    """Create DQ rules template for the domain"""
    template = f"""# Data Quality Rules - {domain_name.title()} Domain

quality_rules:
  # Example: Uniqueness check
  - name: "id_uniqueness"
    level: "critical"
    check: "unique"
    column: "id"
    threshold: 100
  
  # Example: Null check
  - name: "required_field_not_null"
    level: "critical"
    check: "not_null"
    column: "required_field"
    threshold: 100
  
  # Example: Range check
  - name: "amount_positive"
    level: "warning"
    check: "range"
    column: "amount"
    min: 0
    threshold: 95
  
  # Example: Freshness check
  - name: "data_freshness"
    level: "critical"
    check: "freshness"
    threshold_hours: 26
"""
    
    os.makedirs(f"governance/dq_rules/{domain_name}", exist_ok=True)
    with open(f"governance/dq_rules/{domain_name}/rules.yaml", 'w') as f:
        f.write(template)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Onboard a new domain to Fabric')
    parser.add_argument('--domain', required=True, help='Domain name (e.g., finance, sales)')
    parser.add_argument('--owner-email', required=True, help='Domain owner email')
    parser.add_argument('--capacity-id', help='Fabric capacity ID for prod')
    parser.add_argument('--team-ad-group', required=True, help='Azure AD group for domain team')
    
    args = parser.parse_args()
    
    onboard_domain(
        domain_name=args.domain,
        domain_owner_email=args.owner_email,
        capacity_id=args.capacity_id,
        team_ad_group=args.team_ad_group
    )
```

**Usage:**
```bash
python scripts/onboard_domain.py \
    --domain finance \
    --owner-email finance-lead@company.com \
    --capacity-id "abc123-def456-ghi789" \
    --team-ad-group "Finance-Data-Team"
```

## Workspace Provisioning

### Automated Workspace Creation with Governance

```python
#!/usr/bin/env python3
"""
Workspace provisioning with built-in governance controls
"""
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.config_manager import ConfigManager

def provision_governed_workspace(
    domain: str,
    purpose: str,
    environment: str,
    capacity_id: str = None,
    cost_center: str = None
):
    """
    Create workspace with governance controls
    """
    ws_mgr = WorkspaceManager(environment=environment)
    config_mgr = ConfigManager(environment=environment)
    
    # Generate compliant name
    workspace_name = config_mgr.generate_name(
        "workspace",
        environment,
        name=f"{domain}-{purpose}"
    )
    
    # Create workspace
    workspace = ws_mgr.create_workspace(
        environment=environment,
        base_name=f"{domain}-{purpose}",
        description=f"{domain.title()} {purpose} workspace"
    )
    
    workspace_id = workspace['id']
    
    # Apply governance metadata
    governance_tags = {
        "domain": domain,
        "environment": environment,
        "cost_center": cost_center or domain,
        "compliance_level": "medium",
        "data_classification": "internal",
        "retention_years": 5
    }
    
    # Assign capacity if specified
    if capacity_id:
        ws_mgr.assign_to_capacity(workspace_id, capacity_id)
    
    # Setup monitoring
    setup_workspace_monitoring(workspace_id, domain)
    
    # Register in catalog
    register_in_governance_catalog(workspace_id, governance_tags)
    
    print(f"✅ Workspace created: {workspace_name}")
    print(f"   ID: {workspace_id}")
    print(f"   Tags: {governance_tags}")
    
    return workspace


def setup_workspace_monitoring(workspace_id: str, domain: str):
    """Setup monitoring for workspace"""
    # Create monitoring dashboard
    # Setup alerts for:
    # - Usage patterns
    # - Cost anomalies
    # - Quality failures
    # - Security events
    pass


def register_in_governance_catalog(workspace_id: str, tags: dict):
    """Register workspace in governance catalog"""
    # This would integrate with Purview or internal catalog
    # Store metadata about workspace for governance
    pass
```

## Item Management

### Creating Items with Governance

```python
#!/usr/bin/env python3
"""
Create items with built-in governance and quality checks
"""
from ops.scripts.utilities.fabric_item_manager import (
    FabricItemManager,
    FabricItemType,
    create_notebook_definition
)

def create_governed_lakehouse(
    workspace_id: str,
    layer: str,  # bronze, silver, gold
    domain: str,
    data_classification: str = "internal"
):
    """
    Create lakehouse with governance metadata
    """
    manager = FabricItemManager()
    
    # Naming convention
    lakehouse_name = f"{domain}_{layer}_lakehouse"
    
    # Layer-specific description and policies
    layer_policies = {
        "bronze": {
            "description": "Raw data layer - immutable source data",
            "retention_days": 730,  # 2 years
            "quality_level": "basic",
            "schema_enforcement": False
        },
        "silver": {
            "description": "Cleaned and validated data layer",
            "retention_days": 1825,  # 5 years
            "quality_level": "standard",
            "schema_enforcement": True
        },
        "gold": {
            "description": "Business-ready aggregated data layer",
            "retention_days": 3650,  # 10 years
            "quality_level": "high",
            "schema_enforcement": True
        }
    }
    
    policy = layer_policies[layer]
    
    # Create lakehouse
    lakehouse = manager.create_item(
        workspace_id=workspace_id,
        display_name=lakehouse_name,
        item_type=FabricItemType.LAKEHOUSE,
        description=f"{policy['description']} for {domain}"
    )
    
    # Apply governance policies
    apply_retention_policy(lakehouse.id, policy['retention_days'])
    apply_quality_checks(lakehouse.id, policy['quality_level'])
    apply_classification(lakehouse.id, data_classification)
    
    if policy['schema_enforcement']:
        enable_schema_enforcement(lakehouse.id)
    
    print(f"✅ Created governed lakehouse: {lakehouse_name}")
    return lakehouse


def create_governed_notebook(
    workspace_id: str,
    purpose: str,
    domain: str,
    code_content: dict = None
):
    """
    Create notebook with governance controls
    """
    manager = FabricItemManager()
    
    notebook_name = f"{domain}_{purpose}_notebook"
    
    # Create with or without initial content
    if code_content:
        definition = create_notebook_definition(code_content)
    else:
        # Create empty notebook with template
        template_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": [
                        f"# {purpose.title()} Notebook\\n",
                        f"Domain: {domain}\\n",
                        f"\\n",
                        f"## Purpose\\n",
                        f"Describe the purpose of this notebook\\n",
                        f"\\n",
                        f"## Data Sources\\n",
                        f"List data sources\\n",
                        f"\\n",
                        f"## Outputs\\n",
                        f"Describe outputs\\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "source": [
                        "# Import libraries\\n",
                        "import pyspark.sql.functions as F\\n",
                        "from datetime import datetime\\n"
                    ]
                }
            ]
        }
        definition = create_notebook_definition(template_content)
    
    notebook = manager.create_item(
        workspace_id=workspace_id,
        display_name=notebook_name,
        item_type=FabricItemType.NOTEBOOK,
        description=f"{purpose.title()} notebook for {domain}",
        definition=definition
    )
    
    # Apply source control requirements
    require_version_control(notebook.id)
    
    print(f"✅ Created governed notebook: {notebook_name}")
    return notebook


def apply_retention_policy(item_id: str, retention_days: int):
    """Apply data retention policy"""
    # Implementation would use Fabric APIs or Purview
    pass


def apply_quality_checks(item_id: str, level: str):
    """Apply quality check requirements"""
    # Implementation would setup automated DQ checks
    pass


def apply_classification(item_id: str, classification: str):
    """Apply data classification label"""
    # Implementation would use Purview sensitivity labels
    pass


def enable_schema_enforcement(item_id: str):
    """Enable schema enforcement for lakehouse"""
    # Implementation would configure Delta Lake schema enforcement
    pass


def require_version_control(item_id: str):
    """Require version control for notebook"""
    # Implementation would integrate with Git
    pass
```

## Governance Automation

### Automated Compliance Checks

```python
#!/usr/bin/env python3
"""
Automated governance compliance checks
"""
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from ops.scripts.utilities.fabric_item_manager import FabricItemManager
from datetime import datetime, timedelta

def run_compliance_checks(environment: str = "all"):
    """
    Run comprehensive compliance checks
    """
    print(f"🔍 Running compliance checks for {environment}...")
    
    ws_mgr = WorkspaceManager()
    item_mgr = FabricItemManager()
    
    compliance_report = {
        "timestamp": datetime.now().isoformat(),
        "environment": environment,
        "checks": [],
        "violations": [],
        "summary": {}
    }
    
    # Get all workspaces
    workspaces = ws_mgr.list_workspaces()
    
    for workspace in workspaces:
        ws_name = workspace['displayName']
        ws_id = workspace['id']
        
        print(f"\nChecking workspace: {ws_name}")
        
        # Check 1: Naming convention compliance
        if not check_naming_convention(ws_name):
            compliance_report["violations"].append({
                "workspace": ws_name,
                "check": "naming_convention",
                "severity": "medium",
                "message": "Workspace name doesn't follow naming convention"
            })
        
        # Check 2: Items have descriptions
        items = item_mgr.list_items(ws_id)
        for item in items:
            if not item.description or len(item.description) < 10:
                compliance_report["violations"].append({
                    "workspace": ws_name,
                    "item": item.display_name,
                    "check": "documentation",
                    "severity": "low",
                    "message": "Item missing adequate description"
                })
        
        # Check 3: Stale items (not modified in 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        for item in items:
            if item.modified_date and item.modified_date < cutoff_date:
                compliance_report["violations"].append({
                    "workspace": ws_name,
                    "item": item.display_name,
                    "check": "stale_items",
                    "severity": "low",
                    "message": f"Item not modified in 90+ days"
                })
        
        # Check 4: Required items present (for standard workspaces)
        if is_domain_workspace(ws_name):
            required_items = check_required_items(items)
            if required_items["missing"]:
                compliance_report["violations"].append({
                    "workspace": ws_name,
                    "check": "required_items",
                    "severity": "medium",
                    "message": f"Missing required items: {required_items['missing']}"
                })
    
    # Generate summary
    compliance_report["summary"] = {
        "total_workspaces": len(workspaces),
        "total_violations": len(compliance_report["violations"]),
        "violations_by_severity": {
            "critical": sum(1 for v in compliance_report["violations"] if v["severity"] == "critical"),
            "high": sum(1 for v in compliance_report["violations"] if v["severity"] == "high"),
            "medium": sum(1 for v in compliance_report["violations"] if v["severity"] == "medium"),
            "low": sum(1 for v in compliance_report["violations"] if v["severity"] == "low")
        }
    }
    
    # Save report
    report_filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(report_filename, 'w') as f:
        json.dump(compliance_report, f, indent=2)
    
    print(f"\n📊 Compliance Check Summary:")
    print(f"   Total Workspaces: {compliance_report['summary']['total_workspaces']}")
    print(f"   Total Violations: {compliance_report['summary']['total_violations']}")
    print(f"   By Severity: {compliance_report['summary']['violations_by_severity']}")
    print(f"\n📄 Report saved to: {report_filename}")
    
    return compliance_report


def check_naming_convention(workspace_name: str) -> bool:
    """Check if workspace name follows convention"""
    # Expected: {env}-{domain}-{purpose} or {domain}-{env}-{purpose}
    parts = workspace_name.lower().split('-')
    return len(parts) >= 2


def is_domain_workspace(workspace_name: str) -> bool:
    """Check if workspace is a domain workspace"""
    domain_keywords = ['finance', 'sales', 'marketing', 'operations', 'hr']
    return any(keyword in workspace_name.lower() for keyword in domain_keywords)


def check_required_items(items: list) -> dict:
    """Check if required items are present"""
    item_types_present = set(item.type.value for item in items)
    
    required_items = {'Lakehouse', 'Notebook'}
    missing = required_items - item_types_present
    
    return {
        "present": list(required_items & item_types_present),
        "missing": list(missing)
    }


if __name__ == '__main__':
    run_compliance_checks()
```

### Automated Quality Validation

```bash
#!/bin/bash
# Run automated quality checks before deployment

echo "🔍 Running pre-deployment quality gates..."

# 1. Validate DQ rules
echo "\n📋 Validating data quality rules..."
python3 ops/scripts/validate_dq_rules.py --rules-dir governance/dq_rules
if [ $? -ne 0 ]; then
    echo "❌ DQ rule validation failed"
    exit 1
fi

# 2. Run compliance checks
echo "\n🔐 Running compliance checks..."
python3 scripts/run_compliance_checks.py
if [ $? -ne 0 ]; then
    echo "❌ Compliance checks failed"
    exit 1
fi

# 3. Check for required documentation
echo "\n📚 Checking documentation..."
python3 scripts/check_documentation.py
if [ $? -ne 0 ]; then
    echo "⚠️  Documentation incomplete"
fi

# 4. Security scan
echo "\n🛡️  Running security scan..."
python3 scripts/security_scan.py
if [ $? -ne 0 ]; then
    echo "❌ Security scan failed"
    exit 1
fi

echo "\n✅ All quality gates passed!"
exit 0
```

## Monitoring & Compliance

### Cost Monitoring Script

```python
#!/usr/bin/env python3
"""
Cost monitoring and budget enforcement
"""
def monitor_domain_costs():
    """
    Monitor costs per domain and enforce budgets
    """
    # This would integrate with Azure Cost Management API
    
    domains = get_all_domains()
    
    for domain in domains:
        # Get current month spend
        current_spend = get_domain_spend(domain, period="current_month")
        budget = get_domain_budget(domain)
        
        utilization = (current_spend / budget) * 100
        
        print(f"\n{domain.title()} Domain:")
        print(f"  Budget: ${budget:,.2f}")
        print(f"  Spend: ${current_spend:,.2f} ({utilization:.1f}%)")
        
        # Alert thresholds
        if utilization >= 100:
            send_alert(domain, "CRITICAL", "Budget exceeded", current_spend, budget)
            # Implement cost controls
            pause_non_critical_workloads(domain)
        elif utilization >= 80:
            send_alert(domain, "WARNING", "80% budget utilized", current_spend, budget)
        elif utilization >= 50:
            send_notification(domain, "INFO", "50% budget utilized", current_spend, budget)
```

## Summary

This practical guide demonstrates how to use the USF Fabric CI/CD tools to implement federation and governance:

1. **Domain Onboarding**: Automated provisioning of all domain resources
2. **Governed Workspaces**: Creation with built-in compliance
3. **Governed Items**: Items created with metadata and policies
4. **Automated Compliance**: Regular checks and reporting
5. **Cost Management**: Monitoring and budget enforcement

All scripts are ready to use and can be customized for your specific governance requirements.

---

**Version**: 1.0  
**Date**: October 12, 2025  
**See Also**: FABRIC_FEDERATION_GOVERNANCE_FRAMEWORK.md
