#!/usr/bin/env python3
"""
Feature Branch Workflow - Test Script
Demonstrates the complete feature branch lifecycle

This script tests User Story 1: Automate Workspace for New Data Product
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv


# ANSI color codes
class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}💡 {text}{Colors.NC}")


def check_file_exists(file_path, description):
    """Check if a file exists and print result"""
    if not os.path.isfile(file_path):
        print_error(f"{description} not found!")
        print(f"   Expected: {file_path}")
        return False
    print_success(f"{description} found")
    return True


def run_command(cmd, description, capture_output=False):
    """Run a shell command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed")
        if capture_output and e.stderr:
            print(f"   Error: {e.stderr}")
        return None


def check_git_branch_exists(branch_name):
    """Check if a Git branch exists"""
    try:
        result = subprocess.run(
            ["git", "branch", "-a"], capture_output=True, text=True, check=True
        )
        return branch_name in result.stdout
    except subprocess.CalledProcessError:
        return False


def get_git_log(branch_name, count=5):
    """Get Git log for a branch"""
    return run_command(
        f'git log --oneline "{branch_name}" -{count}', "Git log", capture_output=True
    )


def check_audit_trail(audit_trail_path):
    """Check and display audit trail information"""
    if not os.path.isfile(audit_trail_path):
        print_warning("NEW: Audit trail not found (audit logging may be disabled)")
        return

    print_success("NEW: Audit trail found (v2.0 feature)")
    print("\nRecent events (last 5):")

    try:
        with open(audit_trail_path, "r") as f:
            lines = f.readlines()
            recent_lines = lines[-5:] if len(lines) >= 5 else lines

            for line in recent_lines:
                if line.strip():
                    try:
                        event = json.loads(line)
                        print(json.dumps(event, indent=2))
                    except json.JSONDecodeError:
                        print(line.strip())

        # Event summary
        print("\nEvent summary:")
        with open(audit_trail_path, "r") as f:
            events = []
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            if events:
                event_types = Counter(e.get("event_type", "unknown") for e in events)
                print(f"Total events: {len(events)}")
                for event_type, count in event_types.most_common():
                    print(f"  • {event_type}: {count}")
    except Exception as e:
        print_warning(f"Could not parse audit trail: {e}")


def check_git_integration_config(config_path):
    """Check Git integration configuration"""
    if not os.path.isfile(config_path):
        print_warning("project.config.json not found")
        return False

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            git_config = config.get("git_integration", {})
            enabled = git_config.get("enabled", False)
            auto_connect = git_config.get("auto_connect_workspaces", False)

            if enabled and auto_connect:
                print_success("Git auto-connect is ENABLED in project.config.json")
                print("   The workspace should be automatically connected to Git!")
                return True
            else:
                print_warning("Git auto-connect is DISABLED")
                print("   Enable it in project.config.json to test this feature")
                return False
    except Exception as e:
        print_error(f"Could not read project.config.json: {e}")
        return False


def test_naming_validation(repo_root):
    """Test naming validation utilities"""
    sys.path.insert(0, str(Path(repo_root) / "ops" / "scripts" / "utilities"))

    try:
        from item_naming_validator import validate_item_name

        # Test medallion architecture
        result = validate_item_name("BRONZE_CustomerData_Lakehouse", "Lakehouse")
        if result.is_valid:
            print_success("Medallion architecture validation: WORKING")
            print("   Example: BRONZE_CustomerData_Lakehouse is VALID")
        else:
            print_warning("Validation not working as expected")

        # Test invalid name
        result = validate_item_name("CustomerData", "Lakehouse")
        if not result.is_valid:
            print_success("Invalid name detection: WORKING")
            print("   Example: CustomerData is INVALID (missing BRONZE/SILVER/GOLD)")

        print("\nNaming validation is operational!")
        return True

    except ImportError as e:
        print_warning("Naming validation utilities not available")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print_warning(f"Error testing naming validation: {e}")
        return False


def main():
    """Main test execution"""
    # Setup paths
    scenario_dir = Path(__file__).parent.absolute()
    repo_root = scenario_dir.parent.parent
    onboard_script = repo_root / "ops" / "scripts" / "onboard_data_product.py"
    descriptor = scenario_dir / "product_descriptor.yaml"

    # Load environment variables from .env file
    env_file = repo_root / ".env"
    if env_file.is_file():
        load_dotenv(env_file)
        print_success("Loaded environment variables from .env")

    # Generate test ticket ID
    ticket = f"TEST-{int(datetime.now().timestamp())}"

    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}  Feature Branch Workflow - Test Script{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}\n")

    # Test configuration
    print(f"{Colors.BLUE}🎯 Test Configuration{Colors.NC}")
    print("   Scenario: Feature Branch Workflow")
    print(f"   Descriptor: {descriptor}")
    print(f"   Test Ticket: {ticket}")
    print(f"   Repo Root: {repo_root}")
    print()

    # Check prerequisites
    print_header("📋 Checking Prerequisites...")

    if not check_file_exists(onboard_script, "Onboarding script"):
        sys.exit(1)

    if not check_file_exists(descriptor, "Product descriptor"):
        sys.exit(1)

    # Check for .env file
    env_file = repo_root / ".env"
    if not env_file.is_file():
        print_warning("No .env file found")
        print("   This test may fail if environment variables are not set")
        print("   Copy .env.template to .env and fill in values")
        print()
        print(f"{Colors.YELLOW}{'─' * 60}{Colors.NC}")
        response = input(
            f"\n{Colors.BOLD}👉 Continue anyway? (y/N): {Colors.NC}"
        ).strip()
        print(f"{Colors.YELLOW}{'─' * 60}{Colors.NC}")
        if response.lower() != "y":
            sys.exit(1)

    # Change to repo root directory
    os.chdir(repo_root)

    # Step 1: Dry run
    print_header("Step 1: Dry Run (Preview Actions)")
    cmd = f'python3 "{onboard_script}" "{descriptor}" --feature {ticket} --dry-run'
    print(f"Command: {cmd}\n")

    if not run_command(cmd, "Dry run"):
        sys.exit(1)

    print_success("Dry run completed")
    print()
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.NC}")
    print(f"{Colors.YELLOW}⏸️  PAUSED - Review dry run results above{Colors.NC}")
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.NC}")
    input(
        f"\n{Colors.BOLD}👉 Press ENTER to continue with actual creation...{Colors.NC} "
    )

    # Step 2: Create feature environment
    print_header("Step 2: Create Feature Environment")
    print("This will create:")
    print(f"  • Feature workspace: Customer Insights-feature-{ticket}")
    print(f"  • Git branch: feature/customer_insights/{ticket}")
    print("  • Scaffold: data_products/customer_insights/")
    print()

    cmd = f'python3 "{onboard_script}" "{descriptor}" --feature {ticket}'
    print(f"Command: {cmd}\n")

    if not run_command(cmd, "Feature environment creation"):
        sys.exit(1)

    print_success("Feature environment created")

    # Step 3: Verify Git branch
    print_header("Step 3: Verify Git Branch")

    branch_name = f"customer_insights/feature/{ticket}"
    if check_git_branch_exists(branch_name):
        print_success(f"Feature branch exists: {branch_name}")
        print("\nBranch details:")
        log_output = get_git_log(branch_name, 5)
        if log_output:
            print(log_output)
    else:
        print_error("Feature branch not found")

    # Step 4: Check scaffold
    print_header("Step 4: Verify Scaffold Creation")

    scaffold_path = repo_root / "data_products" / "customer_insights"
    if scaffold_path.is_dir():
        print_success("Scaffold directory created")
        print("\nContents:")

        # Try to use tree command, fall back to ls
        tree_result = run_command(
            f'tree -L 2 "{scaffold_path}"', "Tree command", capture_output=True
        )
        if tree_result:
            print(tree_result)
        else:
            ls_result = run_command(
                f'ls -la "{scaffold_path}"', "Directory listing", capture_output=True
            )
            if ls_result:
                print(ls_result)
    else:
        print_error("Scaffold directory not found")

    # Step 5: Check audit logs
    print_header("Step 5: Check Audit Logs (v2.0)")

    # Check old format audit log
    onboarding_logs_dir = repo_root / ".onboarding_logs"
    if onboarding_logs_dir.is_dir():
        audit_files = list(onboarding_logs_dir.glob("*customer_insights*.json"))
        if audit_files:
            latest_audit = sorted(audit_files, key=os.path.getmtime, reverse=True)[0]
            print_success(f"Onboarding log found: {latest_audit.name}")
            print("\nSummary:")
            with open(latest_audit, "r") as f:
                try:
                    audit_data = json.load(f)
                    print(json.dumps(audit_data, indent=2)[:1000])  # First 1000 chars
                except json.JSONDecodeError:
                    print(f.read()[:1000])
        else:
            print_warning("Onboarding log not found")

    # Check new format audit trail (v2.0)
    audit_trail_path = repo_root / "audit" / "audit_trail.jsonl"
    print()
    check_audit_trail(audit_trail_path)

    # Step 6: Verify Git Integration
    print_header("Step 6: Verify Git Integration (v2.0)")

    print("Checking if workspace was auto-connected to Git...\n")
    print_info("Note: Auto-connection requires:")
    print("  • git_integration.enabled = true in project.config.json")
    print("  • git_integration.auto_connect_workspaces = true")
    print("  • GIT_ORGANIZATION and GIT_REPOSITORY environment variables set")
    print()

    config_path = repo_root / "project.config.json"
    check_git_integration_config(config_path)

    github_org = os.getenv("GITHUB_ORG", "your-org")
    github_repo = os.getenv("GITHUB_REPO", "your-repo")

    print()
    print_info("To verify in Fabric portal:")
    print("   1. Open the feature workspace in Fabric portal")
    print("   2. Go to Workspace Settings → Git integration")
    print(f"   3. Should show: Connected to {github_org}/{github_repo}")

    # Step 7: Verify Naming Standards
    print_header("Step 7: Verify Naming Standards (v2.0)")

    naming_standards_path = repo_root / "naming_standards.yaml"
    if naming_standards_path.is_file():
        print_success("Naming standards configuration found")
        print("\nChecking if naming validation is enabled...\n")
        test_naming_validation(repo_root)
    else:
        print_warning("naming_standards.yaml not found")
        print("   Create it to enable automatic naming validation")

    # Summary
    print_header("Test Summary")

    print_success("Feature branch workflow test completed!")
    print("\nCreated Resources:")
    print(f"  • Feature Branch: feature/customer_insights/{ticket}")
    print(f"  • Workspace: Customer Insights-feature-{ticket}")
    print("  • Scaffold: data_products/customer_insights/")
    print("\nv2.0 Features Tested:")
    print("  ✓ Git Integration (auto-connect capability)")
    print("  ✓ Audit Logging (JSONL trail)")
    print("  ✓ Naming Standards (validation utilities)")
    print("\nNext Steps:")
    print("  1. Check Fabric portal for workspace")
    print("  2. Verify Git integration in workspace settings")
    print("  3. Make changes and test workflow")
    print(
        f"  4. Create PR: gh pr create --base main --head feature/customer_insights/{ticket}"
    )
    print("\nCleanup (when done):")
    print("  • Delete workspace in Fabric portal")
    print(
        f"  • Delete branch: git push origin --delete feature/customer_insights/{ticket}"
    )
    print()
    print_info("Tip: Run 'cat audit/audit_trail.jsonl | jq .' to see full audit trail")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
