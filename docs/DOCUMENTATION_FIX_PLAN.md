# Documentation Fix Plan

**Date:** 21 October 2025  
**Based on:** DOCUMENTATION_AUDIT_REPORT.md  
**Status:** 🟡 Awaiting Approval

---

## 🎯 Summary

**Issues Found:** 4 Critical, 5 Medium, 3 Low  
**Estimated Fix Time:** 8.75 hours (1-2 days)  
**Files to Update:** 15 documents  
**Priority:** HIGH (Critical fixes needed for usability)

---

## 🔴 CRITICAL FIXES (Must Do Today)

### Fix #1: CLI Syntax Errors - `--environment` Flag
**Time:** 30 minutes  
**Impact:** HIGH - Commands will fail without this fix  
**Files:** 4 documents

**Changes Required:**

#### File 1: `docs/getting-started/QUICKSTART.md`
**Lines 296, 301**

Replace:
```bash
python ops/scripts/deploy_fabric.py \
  --environment dev \
  --mode standard
```

With:
```bash
python ops/scripts/deploy_fabric.py \
  -e dev \
  --mode standard
```

#### File 2: `docs/workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md`
**Line 41**

Replace:
```bash
python3 ops/scripts/manage_workspaces.py create my-workspace \
  --environment dev \
  --description "My workspace"
```

With:
```bash
python3 ops/scripts/manage_workspaces.py -e dev create my-workspace \
  --description "My workspace"
```

Note: `-e` flag is global (before subcommand)

#### File 3: `docs/etl-data-platform/COMPLETE_ETL_SETUP_GUIDE.md`
**Line 169**

Replace:
```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml \
  --environment dev
```

With:
```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml
```

Note: Environment comes from YAML, not CLI

#### File 4: `docs/fabric-items-crud/FABRIC_ITEM_CRUD_SUMMARY.md`
**Lines 279, 293, 388**

Replace all instances of:
```bash
--environment test
```

With:
```bash
-e test
```

And ensure it's placed before the subcommand.

---

### Fix #2: Workspace Naming Convention
**Time:** 1 hour  
**Impact:** MEDIUM - Confusion but not breaking  
**Files:** 10+ documents

**Pattern to Replace:**

OLD (Hyphenated):
```
Customer-Analytics-dev
Customer-Analytics-feature-20251021
Sales-Analytics-dev
```

NEW (Bracket Notation):
```
Customer Analytics [DEV]
Customer Analytics [FEATURE-JIRA-12345]
Sales Analytics [DEV]
```

**Search Pattern:** `([A-Z][a-z]+)-([A-Z][a-z]+)-(dev|test|prod|feature)`  
**Replace With:** `$1 $2 [${3^^}]` (uppercase environment)

**Files Affected:**
- All in `docs/user-stories-validation/`
- All in `docs/workspace-management/`
- `docs/etl-data-platform/HOW_FLOWS_CONVERGE.md`

---

### Fix #3: YAML Template Updates
**Time:** 1 hour  
**Impact:** LOW - Examples work but don't follow best practice  
**Files:** 5 documents

**Changes Required:**

Replace hardcoded Git settings:
```yaml
git:
  organization: "YourGitHubOrg"      # Hardcoded
  repository: "usf-fabric-cicd"      # Hardcoded
```

With environment variable interpolation:
```yaml
git:
  organization: "${GITHUB_ORG}"      # Uses .env value
  repository: "${GITHUB_REPO}"       # Uses .env value
```

**Files:**
1. `docs/getting-started/REAL_FABRIC_QUICKSTART.md`
2. `docs/user-stories-validation/COMPLETE_USER_STORY_1_WORKFLOW.md`
3. `docs/user-stories-validation/USER_STORY_1_QUICK_REF.md`
4. `docs/etl-data-platform/COMPLETE_ETL_SETUP_GUIDE.md`
5. `docs/workspace-management/FABRIC_ITEMS_AND_USERS_GUIDE.md`

---

## ⚠️  MEDIUM PRIORITY (This Week)

### Fix #4: Cross-Reference Path Updates
**Time:** 2 hours  
**Impact:** LOW - Links broken but readers can navigate manually  
**Files:** All documents

**Changes Required:**

Update all cross-references to use relative paths from new folder structure.

**Pattern to Find:**
```markdown
See: WORKSPACE_MANAGEMENT_QUICKREF.md
Read: USER_STORY_VALIDATION.md
```

**Replace With:**
```markdown
See: [`workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md`](workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md)
Read: [`user-stories-validation/USER_STORY_VALIDATION.md`](user-stories-validation/USER_STORY_VALIDATION.md)
```

**Approach:**
1. Create mapping of all .md files to their new paths
2. Search/replace all document references
3. Test links in VS Code preview

---

### Fix #5: Add Workspace ID Disclaimers
**Time:** 15 minutes  
**Impact:** LOW - Might confuse users but not breaking  
**Files:** 2 documents

**Add this disclaimer after first workspace ID mention:**

```markdown
> **Note:** Workspace IDs shown are from example executions. Your actual workspace IDs will be different. Use these examples to understand the format and structure, not as literal values to copy.
```

**Files:**
1. `docs/user-stories-validation/LIVE_EXECUTION_SUCCESS.md` (after line 28)
2. `docs/user-stories-validation/USER_STORY_1_QUICK_REF.md` (after line 120)

---

### Fix #6: Console Output Format Updates
**Time:** 1 hour  
**Impact:** LOW - Examples don't match but still informative  
**Files:** 6 documents

**Update console output examples to match current script formatting:**

OLD:
```
✅ Created workspace 'Customer-Analytics-dev'
```

NEW:
```
✅ Created workspace 'Customer Analytics [DEV]'
   ID: be8d1df8-9067-4557-a179-fd706a38dd20
   Capacity: trial
   URL: https://app.fabric.microsoft.com/groups/be8d1df8-9067-4557-a179-fd706a38dd20
```

**Files:**
- `docs/getting-started/REAL_FABRIC_QUICKSTART.md`
- `docs/user-stories-validation/COMPLETE_USER_STORY_1_WORKFLOW.md`
- `docs/user-stories-validation/LIVE_EXECUTION_SUCCESS.md`
- `docs/etl-data-platform/COMPLETE_ETL_SETUP_GUIDE.md`
- `docs/workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md`
- `docs/workspace-management/FABRIC_ITEMS_AND_USERS_GUIDE.md`

---

## 📋 LOW PRIORITY (Nice to Have)

### Fix #7: Command Path Consistency
**Time:** 30 minutes  
**Impact:** VERY LOW  
**Files:** 1 document

**File:** `docs/development-maintenance/DEVELOPMENT_TIMELINE.md` (Line 263)

Replace:
```bash
python manage_workspaces.py
```

With:
```bash
python3 ops/scripts/manage_workspaces.py
```

---

### Fix #8: Environment Variable Name Verification
**Time:** 30 minutes  
**Impact:** LOW  
**Files:** All documents

**Verify all documents use:**
- ✅ `GITHUB_ORG` (not `GITHUB_ORGANIZATION`)
- ✅ `GITHUB_REPO` (not `GITHUB_REPOSITORY`)
- ✅ `AZURE_CLIENT_ID` (consistent)
- ✅ `AZURE_TENANT_ID` (consistent)

**Create find/replace list:**
- `GITHUB_ORGANIZATION` → `GITHUB_ORG`
- `GITHUB_REPOSITORY` → `GITHUB_REPO`

---

## 🚀 Execution Plan

### Option A: Do All Critical Fixes Now (Recommended)
**Time:** 2.5 hours  
**Files:** 19 total  
**Result:** Documentation usable and accurate

Execute:
- Fix #1: CLI syntax (30 min)
- Fix #2: Workspace naming (1 hour)
- Fix #3: YAML templates (1 hour)

**Benefits:**
- Users can follow guides without errors
- Examples match current implementation
- Best practices enforced

### Option B: Critical + Medium Fixes
**Time:** 5.25 hours  
**Files:** All documents  
**Result:** Documentation fully polished

Execute:
- All critical fixes (2.5 hours)
- Cross-reference updates (2 hours)
- Workspace ID disclaimers (15 min)
- Console output updates (1 hour)

**Benefits:**
- All links work
- Examples are current
- Professional quality

### Option C: Phased Approach
**Phase 1 (Today):** Critical fixes (2.5 hours)  
**Phase 2 (This Week):** Medium priority (3.75 hours)  
**Phase 3 (Next Week):** Low priority (1 hour)

---

## ✅ Approval Required

Please approve one of the following:

### [ ] Option A: Critical Fixes Only (2.5 hours)
Fix the breaking errors so documentation is usable.

### [ ] Option B: Complete Overhaul (5.25 hours)
Make all critical and medium fixes for professional quality.

### [ ] Option C: Phased Approach (3 phases over 2 weeks)
Spread the work out over time.

### [ ] Custom: Let me know what to prioritize
Tell me which specific fixes you want done first.

---

## 📊 Impact Analysis

### If We Fix Critical Issues Only (Option A):

**Before Fix:**
- ❌ 4 documents have commands that will fail
- ❌ Users will get errors and confusion
- ❌ Documentation health: 65%

**After Fix:**
- ✅ All commands will work correctly
- ✅ Users can follow guides successfully
- ✅ Documentation health: 85%

### If We Do Complete Overhaul (Option B):

**Before Fix:**
- ❌ 15 documents have various issues
- ❌ Cross-references don't work
- ❌ Examples don't match reality

**After Fix:**
- ✅ All commands work correctly
- ✅ All links and references work
- ✅ All examples match current output
- ✅ Documentation health: 95%

---

## 🛡️ Quality Assurance

After fixes are applied, we will:

1. **Test all CLI commands** from documentation
2. **Verify all cross-references** work in VS Code
3. **Check YAML examples** can be executed
4. **Validate console output** matches current scripts
5. **Run spell check** on updated files
6. **Update DOCUMENTATION_INDEX.md** if needed

---

## 📝 Notes

### Files Not Requiring Changes:
- ✅ `docs/getting-started/EXECUTIVE_SUMMARY.md` - High-level only
- ✅ `docs/etl-data-platform/ETL_ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- ✅ `docs/user-stories-validation/USER_STORY_VALIDATION.md` - Criteria only
- ✅ `docs/development-maintenance/CODEBASE_REDUNDANCY_AUDIT.md` - Code review
- ✅ `docs/development-maintenance/IMPLEMENTATION_SUMMARY.md` - Status tracking

### Risky Changes (Need Extra Care):
- ⚠️  Cross-reference path updates (might break links)
- ⚠️  Workspace naming (need to update consistently)
- ⚠️  Console output examples (need to match exactly)

---

## 🎯 Success Metrics

After all fixes:
- ✅ 0 critical errors
- ✅ 0 medium errors  
- ✅ 95%+ documentation health
- ✅ All commands tested and working
- ✅ All links verified
- ✅ All examples current

---

**Ready to proceed? Please approve your preferred option above.**

---

*Generated: 21 October 2025*  
*Based on: DOCUMENTATION_AUDIT_REPORT.md*  
*Awaiting: User approval*

