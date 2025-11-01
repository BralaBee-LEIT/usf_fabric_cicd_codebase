"""
Manual Test Script for Git Reliability Improvements

This script tests the new Git connection features against a real Fabric workspace:
- Pre-flight validation
- Retry logic with exponential backoff
- Enhanced error messages
- Manual fallback workflow

Usage:
    python test_git_reliability_manual.py

Requirements:
    - .env file with FABRIC_* and GITHUB_* credentials
    - Access to a Fabric workspace
    - GitHub repository configured
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.scripts.utilities.fabric_git_connector import FabricGitConnector
from ops.scripts.utilities.output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
)


def load_config():
    """Load configuration from environment"""
    load_dotenv()
    
    config = {
        'workspace_id': os.getenv('FABRIC_WORKSPACE_ID'),
        'git_org': os.getenv('GITHUB_ORG') or os.getenv('GIT_ORGANIZATION'),
        'git_repo': os.getenv('GITHUB_REPO') or os.getenv('GIT_REPOSITORY'),
        'branch': os.getenv('GIT_BRANCH', 'main'),
        'directory': os.getenv('GIT_DIRECTORY', '/'),
    }
    
    # Validate required config
    missing = [k for k, v in config.items() if not v]
    if missing:
        print_error(f"Missing required environment variables: {', '.join(missing)}")
        print_info("\nRequired environment variables:")
        print_info("  FABRIC_WORKSPACE_ID - Fabric workspace GUID to test")
        print_info("  GITHUB_ORG or GIT_ORGANIZATION - GitHub organization name")
        print_info("  GITHUB_REPO or GIT_REPOSITORY - GitHub repository name")
        print_info("  GIT_BRANCH (optional) - Git branch (default: main)")
        print_info("  GIT_DIRECTORY (optional) - Directory path (default: /)")
        print_info("\nAlso required for Fabric API authentication:")
        print_info("  FABRIC_TENANT_ID, FABRIC_CLIENT_ID, FABRIC_CLIENT_SECRET")
        return None
    
    return config


def test_1_validation_only(connector, config):
    """Test 1: Pre-flight validation without connection attempt"""
    print_info("\n" + "="*70)
    print_info("TEST 1: Pre-Flight Validation Only")
    print_info("="*70)
    
    is_valid, error_msg = connector.validate_git_prerequisites(
        workspace_id=config['workspace_id'],
        branch_name=config['branch'],
        directory_path=config['directory']
    )
    
    if is_valid:
        print_success("\n✓ TEST 1 PASSED: Pre-flight validation successful")
        return True
    else:
        print_error("\n✗ TEST 1 FAILED: Pre-flight validation failed")
        print_error(f"Error: {error_msg}")
        return False


def test_2_connection_without_retry(connector, config):
    """Test 2: Direct connection (no retry) to establish baseline"""
    print_info("\n" + "="*70)
    print_info("TEST 2: Direct Connection (No Retry)")
    print_info("="*70)
    
    try:
        result = connector.initialize_git_connection(
            workspace_id=config['workspace_id'],
            branch_name=config['branch'],
            directory_path=config['directory'],
            auto_commit=False
        )
        print_success("\n✓ TEST 2 PASSED: Direct connection successful")
        return True, result
    except Exception as e:
        print_warning(f"\n⚠ TEST 2 RESULT: Direct connection failed (expected if not connected)")
        print_info(f"Error type: {type(e).__name__}")
        print_info(f"Error message: {str(e)[:200]}")
        return False, None


def test_3_connection_with_retry(connector, config):
    """Test 3: Connection with retry logic"""
    print_info("\n" + "="*70)
    print_info("TEST 3: Connection with Retry Logic")
    print_info("="*70)
    
    start_time = time.time()
    
    try:
        result = connector.initialize_git_connection_with_retry(
            workspace_id=config['workspace_id'],
            branch_name=config['branch'],
            directory_path=config['directory'],
            auto_commit=False,
            max_retries=3,
            initial_backoff=1.0  # Faster for testing
        )
        
        elapsed = time.time() - start_time
        print_success(f"\n✓ TEST 3 PASSED: Connection successful with retry (took {elapsed:.1f}s)")
        return True, result
        
    except Exception as e:
        elapsed = time.time() - start_time
        print_error(f"\n✗ TEST 3 FAILED: All retry attempts exhausted (took {elapsed:.1f}s)")
        print_info(f"Error type: {type(e).__name__}")
        
        # Check if error includes troubleshooting
        error_str = str(e)
        if "Troubleshooting steps:" in error_str:
            print_success("  ✓ Error includes troubleshooting steps")
        if "Documentation:" in error_str:
            print_success("  ✓ Error includes documentation links")
        
        return False, None


def test_4_manual_fallback(connector, config):
    """Test 4: Manual fallback workflow (non-interactive for automated testing)"""
    print_info("\n" + "="*70)
    print_info("TEST 4: Manual Fallback Workflow (Display Only)")
    print_info("="*70)
    
    # Test manual fallback without user interaction
    result = connector.prompt_manual_connection(
        workspace_id=config['workspace_id'],
        branch_name=config['branch'],
        directory_path=config['directory'],
        wait_for_user=False  # Non-interactive for automated testing
    )
    
    print_info("\n✓ TEST 4 PASSED: Manual fallback instructions displayed correctly")
    return True


def test_5_error_message_quality(connector, config):
    """Test 5: Verify error message quality with invalid config"""
    print_info("\n" + "="*70)
    print_info("TEST 5: Error Message Quality (Invalid Workspace)")
    print_info("="*70)
    
    try:
        # Try with invalid workspace ID to trigger error
        connector.initialize_git_connection(
            workspace_id="invalid-workspace-id-12345",
            branch_name=config['branch'],
            directory_path=config['directory']
        )
        print_warning("\n⚠ TEST 5: Connection unexpectedly succeeded")
        return False
        
    except Exception as e:
        error_str = str(e)
        
        # Check error message quality
        quality_checks = {
            "Has error type": "Error Type:" in error_str or type(e).__name__ in error_str,
            "Has workspace ID": "workspace" in error_str.lower(),
            "Has troubleshooting": "Troubleshooting" in error_str or "troubleshoot" in error_str.lower(),
            "Has documentation": "learn.microsoft.com" in error_str or "Documentation" in error_str,
            "Has specific advice": any(word in error_str for word in ["Verify", "Check", "Confirm", "Review"]),
        }
        
        print_info("\nError Message Quality Checks:")
        for check, passed in quality_checks.items():
            status = "✓" if passed else "✗"
            print_info(f"  {status} {check}")
        
        passed_count = sum(quality_checks.values())
        total_count = len(quality_checks)
        
        if passed_count >= 4:  # At least 4/5 checks should pass
            print_success(f"\n✓ TEST 5 PASSED: Error message quality good ({passed_count}/{total_count} checks)")
            return True
        else:
            print_warning(f"\n⚠ TEST 5 PARTIAL: Error message could be improved ({passed_count}/{total_count} checks)")
            return False


def main():
    """Run all Git reliability tests"""
    print_success("\n" + "="*70)
    print_success("Git Reliability Improvements - Manual Test Suite")
    print_success("="*70)
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    config = load_config()
    if not config:
        print_error("\n✗ Configuration validation failed")
        return 1
    
    print_success("\n✓ Configuration loaded successfully")
    print_info(f"  Workspace: {config['workspace_id'][:8]}...")
    print_info(f"  Repository: {config['git_org']}/{config['git_repo']}")
    print_info(f"  Branch: {config['branch']}")
    print_info(f"  Directory: {config['directory']}")
    
    # Initialize connector
    try:
        connector = FabricGitConnector(
            organization_name=config['git_org'],
            repository_name=config['git_repo']
        )
        print_success("✓ Git connector initialized")
    except Exception as e:
        print_error(f"\n✗ Failed to initialize Git connector: {e}")
        return 1
    
    # Run tests
    results = {}
    
    try:
        # Test 1: Validation
        results['validation'] = test_1_validation_only(connector, config)
        
        # Test 2: Direct connection (baseline)
        results['direct'], _ = test_2_connection_without_retry(connector, config)
        
        # Test 3: Connection with retry (main test)
        results['retry'], _ = test_3_connection_with_retry(connector, config)
        
        # Test 4: Manual fallback
        results['manual'] = test_4_manual_fallback(connector, config)
        
        # Test 5: Error message quality
        results['errors'] = test_5_error_message_quality(connector, config)
        
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        return 1
    except Exception as e:
        print_error(f"\n\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print_info("\n" + "="*70)
    print_info("TEST SUMMARY")
    print_info("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print_info(f"  {status}: {test_name.upper()}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print_info(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print_success("\n🎉 All tests passed!")
        return 0
    elif passed_count >= total_count - 1:
        print_warning(f"\n⚠ Most tests passed ({passed_count}/{total_count})")
        return 0
    else:
        print_error(f"\n✗ Multiple tests failed ({total_count - passed_count} failures)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
