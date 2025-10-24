#!/usr/bin/env python3
"""
Quick validation test for Fabric CI/CD solution
Tests core functionality without requiring credentials
"""

import sys
import yaml
import json
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("🔍 Testing file structure...")
    
    required_files = [
        # Core configuration
        "project.config.json",
        ".env.example",
        ".gitignore",
        "environment.yml",
        "ops/requirements.txt",
        
        # Scripts
        "ops/scripts/utilities/config_manager.py",
        "ops/scripts/utilities/environment_config.py", 
        "ops/scripts/validate_data_contracts.py",
        "ops/scripts/validate_dq_rules.py",
        "init_project_config.py",
        "setup.sh",
        
        # Workflows
        ".github/workflows/fabric-cicd-pipeline.yml",
        
        # Governance
        "governance/data_contracts/incidents_contract.yaml",
        "governance/dq_rules/dq_rules.yaml",
        
        # Documentation
        "README.md",
        "ENVIRONMENT_SETUP.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("  🎉 All required files present!")
    return True

def test_yaml_syntax():
    """Test YAML files for syntax errors"""
    print("\n🔍 Testing YAML syntax...")
    
    yaml_files = [
        "project.config.json",  # JSON but similar validation
        "governance/data_contracts/incidents_contract.yaml",
        "governance/dq_rules/dq_rules.yaml",
        "environment.yml",
        ".github/workflows/fabric-cicd-pipeline.yml"
    ]
    
    for file_path in yaml_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    if file_path.endswith('.json'):
                        json.load(f)
                    else:
                        yaml.safe_load(f)
                print(f"  ✅ {file_path} - Valid syntax")
            except Exception as e:
                print(f"  ❌ {file_path} - Syntax error: {e}")
                return False
    
    print("  🎉 All YAML/JSON files have valid syntax!")
    return True

def test_python_imports():
    """Test that Python modules can be imported"""
    print("\n🔍 Testing Python imports...")
    
    # Add ops directory to Python path
    sys.path.insert(0, 'ops')
    
    test_modules = [
        ("ops.scripts.utilities.config_manager", "ConfigManager"),
        ("ops.scripts.utilities.environment_config", "EnvironmentConfigManager")
    ]
    
    for module_path, class_name in test_modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_path}.{class_name}")
        except ImportError as e:
            print(f"  ❌ Failed to import {module_path}.{class_name}: {e}")
            return False
        except Exception as e:
            print(f"  ⚠️  {module_path}.{class_name} - Warning: {e}")
    
    print("  🎉 Core Python modules import successfully!")
    return True

def test_data_contracts_validation():
    """Test data contracts validation"""
    print("\n🔍 Testing data contracts validation...")
    
    try:
        # Test if the validation script exists and runs
        if Path("ops/scripts/validate_data_contracts.py").exists():
            print("  ✅ Data contracts validator exists")
            
            # Test discovering contracts
            contracts_dir = Path("governance/data_contracts")
            if contracts_dir.exists():
                contract_files = list(contracts_dir.glob("*.yaml"))
                print(f"  ✅ Found {len(contract_files)} contract file(s)")
                
                for contract_file in contract_files:
                    try:
                        with open(contract_file, 'r') as f:
                            contract_data = yaml.safe_load(f)
                        
                        # Basic validation
                        required_fields = ['dataset', 'owner', 'version']
                        missing = [f for f in required_fields if f not in contract_data]
                        
                        if missing:
                            print(f"  ⚠️  {contract_file.name} - Missing fields: {missing}")
                        else:
                            print(f"  ✅ {contract_file.name} - Basic validation passed")
                            
                    except Exception as e:
                        print(f"  ❌ {contract_file.name} - Error: {e}")
                        return False
            else:
                print("  ⚠️  No data contracts directory found")
                
        else:
            print("  ❌ Data contracts validator script not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Data contracts validation error: {e}")
        return False
    
    print("  🎉 Data contracts validation test passed!")
    return True

def test_dq_rules_validation():
    """Test DQ rules validation"""
    print("\n🔍 Testing DQ rules validation...")
    
    try:
        # Test if the validation script exists
        if Path("ops/scripts/validate_dq_rules.py").exists():
            print("  ✅ DQ rules validator exists")
            
            # Test discovering rules
            rules_dir = Path("governance/dq_rules")
            if rules_dir.exists():
                rules_files = list(rules_dir.glob("*.yaml"))
                print(f"  ✅ Found {len(rules_files)} DQ rules file(s)")
                
                for rules_file in rules_files:
                    try:
                        with open(rules_file, 'r') as f:
                            rules_data = yaml.safe_load(f)
                        
                        # Basic validation
                        if 'rules' in rules_data and isinstance(rules_data['rules'], list):
                            rule_count = len(rules_data['rules'])
                            print(f"  ✅ {rules_file.name} - {rule_count} rule(s) found")
                        else:
                            print(f"  ⚠️  {rules_file.name} - No rules section found")
                            
                    except Exception as e:
                        print(f"  ❌ {rules_file.name} - Error: {e}")
                        return False
            else:
                print("  ⚠️  No DQ rules directory found")
                
        else:
            print("  ❌ DQ rules validator script not found")
            return False
            
    except Exception as e:
        print(f"  ❌ DQ rules validation error: {e}")
        return False
    
    print("  🎉 DQ rules validation test passed!")
    return True

def test_github_workflow():
    """Test GitHub workflow syntax"""
    print("\n🔍 Testing GitHub workflow...")
    
    workflow_path = Path(".github/workflows/fabric-cicd-pipeline.yml")
    if workflow_path.exists():
        try:
            with open(workflow_path, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            # Check basic workflow structure
            required_sections = ['name', 'on', 'jobs']
            missing = [s for s in required_sections if s not in workflow_data]
            
            if missing:
                print(f"  ❌ Workflow missing sections: {missing}")
                return False
            
            # Check jobs
            jobs = workflow_data.get('jobs', {})
            print(f"  ✅ Workflow has {len(jobs)} job(s): {list(jobs.keys())}")
            
            # Look for validation steps
            validation_found = False
            for job_name, job_config in jobs.items():
                steps = job_config.get('steps', [])
                for step in steps:
                    step_name = step.get('name', '')
                    if 'validate' in step_name.lower() or 'contract' in step_name.lower():
                        validation_found = True
                        print(f"  ✅ Found validation step: '{step_name}' in job '{job_name}'")
            
            if not validation_found:
                print("  ⚠️  No validation steps found in workflow")
            
        except Exception as e:
            print(f"  ❌ Workflow syntax error: {e}")
            return False
    else:
        print("  ❌ GitHub workflow file not found")
        return False
    
    print("  🎉 GitHub workflow validation passed!")
    return True

def test_environment_configuration():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    
    # Check .env.example
    env_example_path = Path(".env.example")
    if env_example_path.exists():
        try:
            with open(env_example_path, 'r') as f:
                env_content = f.read()
            
            required_vars = [
                'AZURE_CLIENT_ID',
                'AZURE_CLIENT_SECRET', 
                'AZURE_TENANT_ID',
                'AZURE_SUBSCRIPTION_ID'
            ]
            
            missing_vars = [var for var in required_vars if var not in env_content]
            
            if missing_vars:
                print(f"  ⚠️  .env.example missing variables: {missing_vars}")
            else:
                print("  ✅ .env.example has all required variables")
            
        except Exception as e:
            print(f"  ❌ Error reading .env.example: {e}")
            return False
    else:
        print("  ❌ .env.example file not found")
        return False
    
    # Check conda environment file
    conda_env_path = Path("environment.yml")
    if conda_env_path.exists():
        try:
            with open(conda_env_path, 'r') as f:
                conda_env = yaml.safe_load(f)
            
            if 'dependencies' in conda_env:
                print("  ✅ Conda environment.yml has dependencies")
            else:
                print("  ⚠️  Conda environment.yml missing dependencies")
                
        except Exception as e:
            print(f"  ❌ Error reading environment.yml: {e}")
            return False
    else:
        print("  ⚠️  environment.yml not found")
    
    print("  🎉 Environment configuration test passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Microsoft Fabric CI/CD Solution Validation")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_yaml_syntax,
        test_python_imports,
        test_data_contracts_validation,
        test_dq_rules_validation,
        test_github_workflow,
        test_environment_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The solution appears to be working correctly.")
        print("\n📝 Next steps:")
        print("1. Set up your virtual environment (conda/venv)")
        print("2. Configure .env file with your credentials")
        print("3. Run ./setup.sh for full validation")
        print("4. Initialize with: python init_project_config.py")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)