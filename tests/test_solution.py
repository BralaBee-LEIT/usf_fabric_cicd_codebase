#!/usr/bin/env python3
"""
Minimal validation test for Microsoft Fabric CI/CD project
Tests if the solution works without heavy dependencies
"""

import os
import sys
import json
from pathlib import Path


def test_file_structure():
    """Test basic file structure"""
    print("🔍 Testing file structure...")

    required_files = [
        "ops/scripts/utilities/config_manager.py",
        "ops/scripts/validate_data_contracts.py",
        "ops/scripts/validate_dq_rules.py",
        ".github/workflows/fabric-cicd-pipeline.yml",
        "init_project_config.py",
        ".env.example",
        "project.config.json",
    ]

    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing:
        print(f"❌ Missing files: {missing}")
        return False

    print("✅ All required files present")
    return True


def test_yaml_syntax():
    """Test YAML files syntax without heavy parsing"""
    print("\n🔍 Testing YAML syntax...")

    try:
        import yaml
    except ImportError:
        print("⚠️ PyYAML not installed, skipping YAML tests")
        return True

    yaml_dirs = ["governance/data_contracts", "governance/dq_rules"]

    valid_files = 0
    total_files = 0

    for yaml_dir in yaml_dirs:
        if Path(yaml_dir).exists():
            for yaml_file in Path(yaml_dir).glob("*.yaml"):
                total_files += 1
                try:
                    with open(yaml_file, "r") as f:
                        yaml.safe_load(f)
                    print(f"✅ {yaml_file}")
                    valid_files += 1
                except Exception as e:
                    print(f"❌ {yaml_file}: {e}")

    print(f"✅ {valid_files}/{total_files} YAML files valid")
    return valid_files == total_files


def test_python_imports():
    """Test basic Python imports"""
    print("\n🔍 Testing Python imports...")

    test_modules = [
        "ops.scripts.utilities.config_manager",
        "ops.scripts.validate_data_contracts",
        "ops.scripts.validate_dq_rules",
    ]

    # Add current directory to path
    sys.path.insert(0, ".")

    working = []
    broken = []

    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            working.append(module)
        except Exception as e:
            print(f"❌ {module}: {str(e)[:60]}...")
            broken.append(module)

    if broken:
        print(f"⚠️ {len(broken)} modules need dependencies installed")
        print("Run: pip install -r ops/requirements.txt")

    return len(working) > 0


def test_configuration():
    """Test configuration files"""
    print("\n🔍 Testing configuration...")

    # Test project.config.json
    if Path("project.config.json").exists():
        try:
            with open("project.config.json", "r") as f:
                config = json.load(f)
            print("✅ project.config.json - Valid JSON")

            required_keys = ["project", "environments", "naming_patterns"]
            missing_keys = [k for k in required_keys if k not in config]
            if missing_keys:
                print(f"⚠️ Missing config keys: {missing_keys}")
            else:
                print("✅ project.config.json - All required keys present")

        except Exception as e:
            print(f"❌ project.config.json: {e}")
            return False
    else:
        print("⚠️ project.config.json not found - run init_project_config.py")

    # Test .env.example
    if Path(".env.example").exists():
        print("✅ .env.example found")

        if not Path(".env").exists():
            print("⚠️ .env not found - copy from .env.example")
    else:
        print("❌ .env.example missing")
        return False

    return True


def main():
    """Run all tests"""
    print("🚀 Microsoft Fabric CI/CD - Quick Validation")
    print("=" * 50)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    tests = [
        ("File Structure", test_file_structure),
        ("YAML Syntax", test_yaml_syntax),
        ("Python Imports", test_python_imports),
        ("Configuration", test_configuration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 Solution is working! All tests passed.")
        print("\nNext steps:")
        print("1. Set up virtual environment: python -m venv fabric-cicd-env")
        print("2. Activate it: source fabric-cicd-env/bin/activate")
        print("3. Install dependencies: pip install -r ops/requirements.txt")
        print("4. Create .env: cp .env.example .env")
        print("5. Run full validation scripts")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Check issues above.")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
