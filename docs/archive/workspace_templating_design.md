# Workspace Templating - Technical Blueprint

## Goal
Automate the end-to-end onboarding experience for a new data product by creating the required Microsoft Fabric workspaces, Git repository scaffolding, and standards-compliant folder structures from a single descriptor. The workflow must satisfy the acceptance criteria defined for automatic DEV/FEATURE workspace provisioning, Git branch linkage, and reproducible deployment.

## Inputs
- **Onboarding descriptor (YAML)** under `data_products/onboarding/<product>.yaml` containing:
  ```yaml
  product:
    name: "DataProduct 1"
    slug: "data_product_1"        # optional override; derived from name if absent
    owner_email: "owner@contoso.com"
    domain: "Customer Analytics"   # used for metadata tagging
  environments:
    dev:
      enabled: true
      capacity: "trial"            # optional override
    feature:
      template: "feature"          # provision feature workspaces on demand
  git:
    repo: "main"                   # target Git repo (assumed current repo)
    default_branch: "main"
    feature_prefix: "feature"      # branch prefix naming convention
  automation:
    trigger: "workflow"            # workflow or manual CLI
    audit_reference: "JIRA-123"
  ```
- **Feature onboarding payload** (`--feature JIRA-123`) optionally supplied to generate a feature branch/workspace `DataProduct 1 [Feature JIRA-123]`.

## Outputs
1. **DEV workspace** `DataProduct 1 [DEV]` created (or idempotently retrieved) via Fabric REST API with:
   - Standard tags/metadata (domain, owner, audit reference)
   - Optional capacity assignment/policies from constants
2. **Repo scaffolding** under `data_products/data_product_1/` seeded from template skeletons:
   - `workspace/` (Fabric artifacts placeholders)
   - `pipelines/`, `notebooks/`, `datasets/`, etc.
   - Optional README describing structure
3. **Feature branch** `data_product_1/feature/JIRA-123` created from `main` with initial commit referencing onboarding descriptor.
4. **Feature workspace** `DataProduct 1 [Feature JIRA-123]` provisioned and linked to corresponding Git branch using Fabric Git integration API.
5. **Registration record** appended to `project.config.json` (or new registry file) capturing:
   ```json
   {
     "product": "DataProduct 1",
     "slug": "data_product_1",
     "dev_workspace_id": "...",
     "feature_workspaces": {
       "JIRA-123": "..."
     },
     "git": {
       "folder": "data_products/data_product_1",
       "feature_branch": "data_product_1/feature/JIRA-123"
     }
   }
   ```

## Workflow Steps
1. **Parse onboarding descriptor** and validate required fields.
2. **Slugify name** (`DataProduct 1` -> `data_product_1`).
3. **Provision DEV workspace** using `WorkspaceManager.create_workspace` with standardized naming `f"{name} [DEV]"`.
4. **Seed Git folder** by copying from `workspace_templates/base_product/` into `data_products/<slug>/`.
5. **Commit + optional PR** using CLI git commands (configurable `--no-commit`).
6. **If feature flag provided**:
   - Create git branch `data_product_1/feature/<ticket>`
   - Create workspace `DataProduct 1 [Feature <ticket>]`
   - Call Fabric Git binding endpoint `POST /v1/workspaces/{id}/git/connect` with branch info.
7. **Apply permissions** (owner/admin) from descriptor.
8. **Persist registration metadata** for audit (JSON file under `data_products/registry.json`).

## Fabric API Touchpoints
- `POST /v1/workspaces` — create workspace
- `GET /v1/workspaces?$filter=displayName eq '...'` — idempotency
- `POST /v1/workspaces/{workspaceId}/git/connect` — link to Git branch
- `POST /v1/workspaces/{workspaceId}/users` — assign owners/admins

## Git Automation
- Utilize `subprocess.run(["git", ...])` for safety (no new dependencies).
- Wrap operations in helper functions for easier mocking.
- Support `--dry-run` to preview actions.

## Error Handling & Audit
- Log all actions to console via `output.console_*` utilities.
- Write audit trail JSON to `.onboarding_logs/{timestamp}_{slug}.json` summarizing operations and IDs.
- Gracefully roll back git changes on failure (reset staged files, delete incomplete branches).

## Configuration Hooks
- Extend `project.config.json` with `"products"` array storing onboarding metadata.
- Add constants for naming patterns and default capacities in `ops/scripts/utilities/constants.py`.

## Testing Strategy
- Unit tests for slug generation, descriptor parsing, command building.
- Integration test (mocked Fabric API via responses) to simulate provisioning.
- CLI smoke test using `--dry-run` mode to assert log output.

## Delivery Scope (Initial Sprint)
- Implement onboarding CLI with DEV + feature provisioning.
- Provide starter descriptors and templates.
- Document usage in new `documentation/WORKSPACE_TEMPLATING_GUIDE.md`.
- Add GitHub Actions workflow example (`.github/workflows/onboard_data_product.yml`).

Dependencies: rely on existing Fabric workspace utilities, Git CLI availability, and repository template assets.
