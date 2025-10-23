# Test & Validation Scripts

Test suites and validation scripts for ensuring solution correctness, workspace management functionality, and deployment readiness.

## 📁 Scripts

### Solution Validation

**`validate_solution.py`** - Comprehensive solution validator
- ✅ File structure validation (all required files exist)
- ✅ YAML/JSON syntax validation
- ✅ Python import tests
- ✅ Configuration file validation
- ✅ Workflow file validation

**Usage:**
```bash
python tests/validate_solution.py
```

**`test_solution.py`** - Minimal validation (no heavy dependencies)
- ✅ Basic file structure check
- ✅ YAML syntax validation (if PyYAML installed)
- ✅ Python import tests
- Lighter weight than validate_solution.py

**Usage:**
```bash
python tests/test_solution.py
```

**`validate_improvements.py`** - Improvement validation
- Validates specific improvements and features
- Checks implementation correctness
- Useful for regression testing

**Usage:**
```bash
python tests/validate_improvements.py
```

---

### Workspace Management Tests

**`test_workspace_management.sh`** - Workspace management test suite
- **Phase 1:** Import & syntax tests
- **Phase 2:** CLI help & usage tests  
- **Phase 3:** Unit tests

**Usage:**
```bash
./tests/test_workspace_management.sh
```

**Features:**
- Color-coded output (green ✓, red ✗)
- Test counters (passed/failed)
- No actual API calls (safe testing)
- Tests all CLI commands

---

### API Testing

**`test_user_addition.py`** - User addition API format tester
- Tests 3 different API payload formats
- Helps identify correct Fabric API format
- Useful for debugging user addition failures

**Usage:**
```bash
python tests/test_user_addition.py
```

**Note:** This makes actual API calls. Use with caution or modify for dry-run.

---

## 🧪 Test Workflow

### Pre-Deployment Validation

```bash
# 1. Validate solution structure
python tests/validate_solution.py

# 2. Test workspace management
./tests/test_workspace_management.sh

# 3. Quick validation
python tests/test_solution.py
```

### Post-Implementation Validation

```bash
# Validate improvements
python tests/validate_improvements.py
```

---

## 📊 Test Categories

| Category | Script | Purpose |
|----------|--------|---------|
| **Structure** | validate_solution.py | File structure, YAML syntax |
| **Minimal** | test_solution.py | Lightweight validation |
| **Functional** | test_workspace_management.sh | Workspace operations |
| **API** | test_user_addition.py | API format testing |
| **Regression** | validate_improvements.py | Feature validation |

---

## 🔧 Common Use Cases

### "I want to validate the entire solution"
```bash
python tests/validate_solution.py
```

### "I need quick validation before commit"
```bash
python tests/test_solution.py
```

### "I want to test workspace management CLI"
```bash
./tests/test_workspace_management.sh
```

### "I'm debugging user addition issues"
```bash
python tests/test_user_addition.py
```

---

## ✅ What Gets Tested

### File Structure
- Core configuration files exist
- Script files exist
- Workflow files exist
- Governance files exist
- Documentation exists

### Syntax Validation
- YAML files parse correctly
- JSON files parse correctly
- Python files compile

### Functionality
- Module imports work
- CLI commands execute
- Help menus display

### API
- Different payload formats
- Authentication
- Error handling

---

## 📋 Prerequisites

- Virtual environment activated: `conda activate fabric-cicd`
- Dependencies installed: `pip install -r requirements.txt`
- For API tests: `.env` configured with credentials

---

## 💡 Best Practices

1. **Run tests before commits** - Catch issues early
2. **Use validate_solution.py regularly** - Comprehensive checks
3. **test_workspace_management.sh is safe** - No API calls
4. **test_user_addition.py is NOT safe** - Makes real API calls
5. **Add tests for new features** - Maintain test coverage

---

## 🚦 Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

Use in CI/CD pipelines:
```bash
python tests/validate_solution.py || exit 1
```

---

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Setup Scripts](../setup/README.md) - Environment setup
- [Diagnostics](../diagnostics/README.md) - Troubleshooting
- [CI/CD Workflows](../.github/workflows/) - Automated testing

---

**Location:** `/tests/`  
**Purpose:** Testing and validation  
**Type:** Test scripts
