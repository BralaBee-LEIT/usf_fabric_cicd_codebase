# Workspace Templating & Data Product Onboarding

This guide explains how to bootstrap new Microsoft Fabric workspaces, Git scaffolding, and registry entries using the automated onboarding CLI introduced in `ops/scripts/onboard_data_product.py`.

## Prerequisites

- Conda environment `fabric-cicd` activated (contains required Python dependencies).
- `.env` file at the repo root providing Fabric service principal credentials and Git metadata:
  - `AZURE_TENANT_ID`
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_SECRET`
  - Optional Git defaults: `GITHUB_ORG`, `GITHUB_REPO`
- Fabric service principal with permissions to create workspaces and assign Git integration.
- Git repository access for creating branches and committing scaffolds.
- (Optional) Feature ticket identifier (e.g., `JIRA-123`) when provisioning feature workspaces and branches.

## Descriptor Structure

Onboarding is driven by YAML descriptors stored under `data_products/onboarding/`. Use `sample_product.yaml` as a template.

```yaml
product:
  name: "Sample Data Product"
  owner_email: "owner@example.com"
  domain: "Customer Insights"

environments:
  dev:
    enabled: true
    capacity_type: "trial"
    description: "Development workspace"

git:
  organization: "${GITHUB_ORG}"
  repository: "${GITHUB_REPO}"
  feature_prefix: "feature"
  directory: "data_products/sample_data_product"

automation:
  audit_reference: "JIRA-000"
```

### Required Fields
- `product.name` — Display name for the data product (used in workspace names).
- `environments.dev.enabled` — Controls whether the DEV workspace is provisioned.

### Optional Fields
- `product.slug` — Overrides the auto-generated slug.
- `product.owner_email`, `product.domain` — Stored in the onboarding registry for metadata.
- `environments.dev.capacity_type`, `capacity` — Capacity assignments (defaults to Trial).
- `git.feature_prefix`, `git.directory`, `git.auto_commit` — Controls Git branch naming and scaffold commits.
- `automation.audit_reference` — Included in audit logs and registry entries (e.g., link to ticket).

## Running the Onboarding CLI

```bash
python ops/scripts/onboard_data_product.py data_products/onboarding/<descriptor>.yaml [options]
```

### Common Options
- `--dry-run` — Preview actions without changing Fabric or Git.
- `--skip-workspaces` — Bypass Fabric workspace provisioning (useful for Git-only runs).
- `--skip-git` — Skip branch creation and workspace Git linking.
- `--feature <ticket>` — Provision feature workspace and Git branch (e.g., `--feature JIRA-123`).
- `--json` — Emit JSON summary of the onboarding run.

### Examples

Preview actions:
```bash
python ops/scripts/onboard_data_product.py data_products/onboarding/sample_product.yaml --dry-run --skip-git
```

Create DEV workspace, scaffold, and registry entry:
```bash
python ops/scripts/onboard_data_product.py data_products/onboarding/sample_product.yaml
```

Provision feature workspace and Git branch:
```bash
python ops/scripts/onboard_data_product.py data_products/onboarding/sample_product.yaml --feature JIRA-123
```

## Generated Artifacts

- **Workspaces** — `"<product name> [DEV]"` plus optional feature workspaces `"<product name> [Feature <ticket>]"`.
- **Repository scaffold** — Copied from `data_products/templates/base_product/` into `data_products/<slug>/`.
- **Git branch** — `<slug>/<feature_prefix>/<ticket>` (commits scaffold if `auto_commit` is true).
- **Registry entry** — `data_products/registry.json` records workspace IDs, feature linkage, and metadata.
- **Audit log** — `.onboarding_logs/<timestamp>_<slug>.json` summarizing actions and IDs.

## Modifying the Scaffold Template

Adjust the base template folder at `data_products/templates/base_product/` to change the generated structure.

- Add README or documentation in `docs/`.
- Provide starter notebooks, pipelines, or dataset placeholders.
- Include custom files (e.g., `.fabricignore`) at the root.

Changes take effect on the next onboarding run.

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| `Missing required Azure credentials` | Ensure `.env` contains Fabric service principal variables. They load automatically at runtime. |
| Git branch creation fails | Confirm repository permissions and that `git` CLI is available. Use `--skip-git` to isolate workspace provisioning. |
| Scaffold not created | Check template path `data_products/templates/base_product/`. With `--dry-run`, scaffolding is skipped intentionally. |
| Fabric API errors | Validate service principal permissions and that the environment (e.g., tenant) matches `project.config.json` settings. |

## Next Steps

- Tag onboarding runs with feature identifiers to enable automated cleanup and promotion.
- Extend the registry to track lifecycle information (e.g., status, owners, approvals).
- Integrate onboarding with CI/CD pipelines for self-service product provisioning.
