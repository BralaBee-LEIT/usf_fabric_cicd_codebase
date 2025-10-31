#!/usr/bin/env python3
"""
Quick Pre-Flight Check - Cross-Platform Python Version
Validates essential components before running framework
Works on Windows, macOS, and Linux
"""

import sys
import os
from pathlib import Path
import subprocess

# Colors for terminal output
if sys.platform == "win32":
    # Windows may not support ANSI colors in older terminals
    try:
        import colorama
        colorama.init()
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        RED = '\033[0;31m'
        BLUE = '\033[0;34m'
        NC = '\033[0m'
    except ImportError:
        GREEN = YELLOW = RED = BLUE = NC = ''
else:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header():
    """Print check header"""
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║  Microsoft Fabric CI/CD Framework - Quick Pre-Flight Check        ║{NC}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════╝{NC}")
    print()


def check_python_version():
    """Check Python version"""
    print(f"{YELLOW}[1/8]{NC} Checking Python version...")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 9:
        print(f"       {GREEN}✓{NC} Python {version_str} (compatible)")
        return True
    else:
        print(f"       {YELLOW}⚠{NC} Python {version_str} (recommended: 3.9+)")
        return None  # Warning, not failure


def check_dependencies():
    """Check required Python packages"""
    print(f"{YELLOW}[2/8]{NC} Checking Python dependencies...")
    missing = []
    
    for pkg in ['yaml', 'msal', 'requests', 'pandas']:
        try:
            if pkg == 'yaml':
                __import__('yaml')
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg if pkg != 'yaml' else 'pyyaml')
    
    if not missing:
        print(f"       {GREEN}✓{NC} All core dependencies installed")
        return True
    else:
        print(f"       {RED}✗{NC} Missing: {', '.join(missing)}")
        print(f"       {BLUE}→{NC} Run: pip install -r ops/requirements.txt")
        return False


def check_env_file():
    """Check .env file exists"""
    print(f"{YELLOW}[3/8]{NC} Checking .env file...")
    
    if Path(".env").exists():
        print(f"       {GREEN}✓{NC} .env file exists")
        return True
    else:
        print(f"       {RED}✗{NC} .env file not found")
        print(f"       {BLUE}→{NC} Windows: copy .env.example .env")
        print(f"       {BLUE}→{NC} Linux/macOS: cp .env.example .env")
        return False


def check_azure_credentials():
    """Check Azure credentials in .env"""
    print(f"{YELLOW}[4/8]{NC} Checking Azure credentials...")
    
    if not Path(".env").exists():
        print(f"       {RED}✗{NC} Cannot check (no .env file)")
        return False
    
    # Read .env file
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"       {RED}✗{NC} Error reading .env: {e}")
        return False
    
    required = ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET']
    missing = []
    
    for var in required:
        value = env_vars.get(var, '')
        if not value or 'your-' in value.lower():
            missing.append(var)
            print(f"       {RED}✗{NC} {var} not configured")
    
    if missing:
        print(f"       {BLUE}→{NC} Edit .env with your Azure credentials")
        return False
    else:
        print(f"       {GREEN}✓{NC} Azure credentials configured")
        return True


def check_fabric_capacity():
    """Check Fabric Capacity ID"""
    print(f"{YELLOW}[5/8]{NC} Checking Fabric Capacity ID...")
    
    if not Path(".env").exists():
        print(f"       {YELLOW}⚠{NC} FABRIC_CAPACITY_ID not configured (optional)")
        return None
    
    # Read .env file
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except:
        pass
    
    capacity_id = env_vars.get('FABRIC_CAPACITY_ID', '')
    
    if capacity_id and 'your-' not in capacity_id.lower():
        print(f"       {GREEN}✓{NC} FABRIC_CAPACITY_ID configured")
        return True
    else:
        print(f"       {YELLOW}⚠{NC} FABRIC_CAPACITY_ID not configured (optional)")
        return None


def check_project_config():
    """Check project configuration"""
    print(f"{YELLOW}[6/8]{NC} Checking project configuration...")
    
    if Path("project.config.json").exists():
        print(f"       {GREEN}✓{NC} project.config.json exists")
        return True
    else:
        print(f"       {YELLOW}⚠{NC} project.config.json not found (optional)")
        print(f"       {BLUE}→{NC} Run: python init_new_project.py (if needed)")
        return None


def check_git_repo():
    """Check Git repository"""
    print(f"{YELLOW}[7/8]{NC} Checking Git repository...")
    
    if Path(".git").is_dir():
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = result.stdout.strip() or "unknown"
            print(f"       {GREEN}✓{NC} Git repository initialized (branch: {branch})")
            return True
        except:
            print(f"       {GREEN}✓{NC} Git repository initialized")
            return True
    else:
        print(f"       {YELLOW}⚠{NC} Not a git repository")
        return None


def check_framework_scripts():
    """Check key framework scripts"""
    print(f"{YELLOW}[8/8]{NC} Checking framework scripts...")
    
    scripts = [
        "ops/scripts/manage_workspaces.py",
        "tools/manage_fabric_folders.py"
    ]
    
    missing = []
    for script in scripts:
        if not Path(script).exists():
            print(f"       {RED}✗{NC} Missing: {script}")
            missing.append(script)
    
    if not missing:
        print(f"       {GREEN}✓{NC} Framework scripts present")
        return True
    else:
        return False


def print_summary(passed, warned, failed):
    """Print summary"""
    print()
    print(f"{BLUE}════════════════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}                          SUMMARY                                   {NC}")
    print(f"{BLUE}════════════════════════════════════════════════════════════════════{NC}")
    print(f"{GREEN}✓ Passed:{NC}  {passed}")
    print(f"{YELLOW}⚠ Warnings:{NC} {warned}")
    print(f"{RED}✗ Failed:{NC}  {failed}")
    print()
    
    if failed > 0:
        print(f"{RED}❌ Pre-flight check FAILED{NC}")
        print("   Fix the issues above before proceeding")
        return 1
    elif warned > 0:
        print(f"{YELLOW}⚠️  Pre-flight check PASSED with warnings{NC}")
        print("   System is functional but some optional features unavailable")
        return 0
    else:
        print(f"{GREEN}✅ Pre-flight check PASSED{NC}")
        print("   System is ready for operations")
        return 0


def main():
    """Main entry point"""
    print_header()
    
    checks = [
        check_python_version,
        check_dependencies,
        check_env_file,
        check_azure_credentials,
        check_fabric_capacity,
        check_project_config,
        check_git_repo,
        check_framework_scripts
    ]
    
    passed = 0
    warned = 0
    failed = 0
    
    for check in checks:
        result = check()
        if result is True:
            passed += 1
        elif result is None:
            warned += 1
        else:
            failed += 1
    
    return print_summary(passed, warned, failed)


if __name__ == "__main__":
    sys.exit(main())
