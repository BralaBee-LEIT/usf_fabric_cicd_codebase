#!/usr/bin/env python3
"""Data product onboarding workflow for Microsoft Fabric.

This script provisions the required Microsoft Fabric workspaces, bootstraps the
Git repository structure, and links feature branches/workspaces based on a
descriptor file. It follows the workspace templating blueprint defined in
`documentation/workspace_templating_design.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Allow importing shared utilities without installing as a package
UTILITIES_PATH = Path(__file__).parent / "utilities"
if str(UTILITIES_PATH) not in sys.path:
    sys.path.insert(0, str(UTILITIES_PATH))

from utilities.output import (
    console_error,
    console_info,
    console_json,
    console_success,
    console_warning,
)
from utilities.workspace_manager import CapacityType, WorkspaceManager
from utilities.config_manager import ConfigManager

# Optional: Import Git integration and audit logging utilities
try:
    from utilities.fabric_git_connector import get_git_connector
    GIT_CONNECTOR_AVAILABLE = True
except ImportError:
    GIT_CONNECTOR_AVAILABLE = False

try:
    from utilities.audit_logger import get_audit_logger
    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------

ENV_FILENAMES = (".env", ".env.local")


def load_env_file(path: Path) -> int:
    """Load environment variables from a dotenv-style file.

    Returns the number of variables added.
    """
    loaded = 0
    if not path.exists():
        return loaded

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("export "):
                line = line[len("export ") :]

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue

            value = value.strip()
            if (value.startswith("\"") and value.endswith("\"")) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            os.environ[key] = value
            loaded += 1

    if loaded:
        console_info(f"Loaded {loaded} environment variables from {path}")
    return loaded


def load_env_files(repo_root: Path) -> None:
    for filename in ENV_FILENAMES:
        load_env_file(repo_root / filename)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class GitConfig:
    provider: str = "GitHub"
    organization: Optional[str] = None
    repository: Optional[str] = None
    default_branch: str = "main"
    feature_prefix: str = "feature"
    directory: str = "/"
    auto_commit: bool = True


@dataclass
class EnvironmentDescriptor:
    name: str
    enabled: bool = True
    capacity_id: Optional[str] = None
    capacity_type: CapacityType = CapacityType.TRIAL
    description: Optional[str] = None


@dataclass
class ProductDescriptor:
    name: str
    slug: str
    owner_email: Optional[str] = None
    domain: Optional[str] = None
    audit_reference: Optional[str] = None
    git: GitConfig = field(default_factory=GitConfig)
    dev: EnvironmentDescriptor = field(
        default_factory=lambda: EnvironmentDescriptor(name="DEV")
    )


@dataclass
class OnboardingArguments:
    descriptor_path: Path
    feature_ticket: Optional[str] = None
    dry_run: bool = False
    skip_git: bool = False
    skip_workspaces: bool = False
    skip_scaffold: bool = False
    json_output: bool = False


@dataclass
class OnboardingResult:
    product: ProductDescriptor
    dev_workspace: Optional[Dict[str, Any]] = None
    dev_workspace_created: bool = False
    feature_workspace: Optional[Dict[str, Any]] = None
    feature_workspace_created: bool = False
    git_branch: Optional[str] = None
    git_branch_created: bool = False
    scaffold_path: Optional[Path] = None
    registry_updated: bool = False
    audit_log_path: Optional[Path] = None


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def slugify(value: str) -> str:
    """Convert a product name into a filesystem-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\-\s_]", "", value)
    value = re.sub(r"[\s\-]+", "_", value)
    return value


def load_yaml_descriptor(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        content = handle.read()
        # Expand environment variables in ${VAR} format
        import re
        def expand_env_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # Return original if not found
        content = re.sub(r'\$\{([^}]+)\}', expand_env_var, content)
        return yaml.safe_load(content) or {}


def parse_capacity_type(raw: Optional[str]) -> CapacityType:
    if not raw:
        return CapacityType.TRIAL
    normalized = raw.upper().replace("-", "_")
    for choice in CapacityType:
        if choice.name == normalized or choice.value.upper() == normalized:
            return choice
    valid_options = ', '.join(c.value for c in CapacityType)
    raise ValueError(
        f"Unsupported capacity type '{raw}'. "
        f"Valid options (case-insensitive): {valid_options}. "
        f"Examples: 'trial', 'Premium-P1', 'fabric_f8'"
    )


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_command(command: List[str], *, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a shell command and capture output."""
    process = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def validate_git_repository(repo_path: Path) -> bool:
    """Verify the path is a valid git repository.
    
    Args:
        repo_path: Path to verify
        
    Returns:
        True if valid git repository
        
    Raises:
        RuntimeError: If path is not a git repository
    """
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        raise RuntimeError(f"{repo_path} is not a git repository. Run 'git init' first.")
    return True


def git_current_branch(repo_path: Path) -> str:
    validate_git_repository(repo_path)
    code, stdout, stderr = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)
    if code != 0:
        raise RuntimeError(f"Failed to determine current Git branch: {stderr}")
    return stdout


def git_branch_exists(repo_path: Path, branch_name: str) -> bool:
    validate_git_repository(repo_path)
    code, _, _ = run_command(["git", "rev-parse", "--verify", branch_name], cwd=repo_path)
    return code == 0


def git_checkout(repo_path: Path, branch_name: str) -> None:
    validate_git_repository(repo_path)
    code, _, stderr = run_command(["git", "checkout", branch_name], cwd=repo_path)
    if code != 0:
        raise RuntimeError(stderr or f"Failed to checkout branch {branch_name}")


def git_checkout_new(repo_path: Path, branch_name: str, base_branch: str) -> None:
    validate_git_repository(repo_path)
    code, _, stderr = run_command(
        ["git", "checkout", "-b", branch_name, base_branch], cwd=repo_path
    )
    if code != 0:
        raise RuntimeError(stderr or f"Failed to create branch {branch_name} from {base_branch}")


def git_stage_and_commit(repo_path: Path, paths: List[Path], message: str) -> None:
    if not paths:
        return
    validate_git_repository(repo_path)
    rel_paths = [str(path.relative_to(repo_path)) for path in paths]
    
    # Try to add files - it's OK if they don't exist or have no changes
    code, _, stderr = run_command(["git", "add", *rel_paths], cwd=repo_path)
    if code != 0:
        # Check if there are any changes to commit
        status_code, status_out, _ = run_command(["git", "status", "--porcelain", *rel_paths], cwd=repo_path)
        if status_code == 0 and not status_out.strip():
            # No changes, skip commit
            return
        raise RuntimeError(stderr or "Failed to stage onboarding assets")
    
    # Check if there are staged changes before committing
    status_code, status_out, _ = run_command(["git", "diff", "--cached", "--name-only"], cwd=repo_path)
    if status_code == 0 and not status_out.strip():
        # No staged changes, skip commit
        return
        
    code, _, stderr = run_command(["git", "commit", "-m", message], cwd=repo_path)
    if code != 0:
        raise RuntimeError(stderr or "Failed to commit onboarding assets")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


# ---------------------------------------------------------------------------
# Core onboarding workflow
# ---------------------------------------------------------------------------


class DataProductOnboarder:
    def __init__(self, arguments: OnboardingArguments):
        self.args = arguments
        self.repo_root = repository_root()
        load_env_files(self.repo_root)
        self.audit_dir = self.repo_root / ".onboarding_logs"
        self.registry_path = self.repo_root / "data_products" / "registry.json"
        self.templates_dir = self.repo_root / "data_products" / "templates" / "base_product"
        self.logger = console_info
        self.dry_run = arguments.dry_run
        self.console_json = console_json if arguments.json_output else None
        self.config_manager: Optional[ConfigManager] = None

        # Initialize Git connector and audit logger if available
        self.git_connector = get_git_connector() if GIT_CONNECTOR_AVAILABLE else None
        self.audit_logger = get_audit_logger() if AUDIT_LOGGER_AVAILABLE else None
        
        if self.audit_logger and not self.dry_run:
            self.audit_logger.log_onboarding_started(
                product_id=None,  # Will be set after loading descriptor
                descriptor_path=str(arguments.descriptor_path)
            )

        try:
            self.config_manager = ConfigManager()
        except Exception as exc:
            console_warning(
                "Unable to load project.config.json; continuing with descriptor defaults.\n"
                f"Reason: {exc}"
            )

        self.credentials_available = all(
            os.getenv(env_var)
            for env_var in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")
        )

        if not self.credentials_available and not (self.args.skip_workspaces or self.dry_run):
            console_warning(
                "Azure credentials not detected. Automatically enabling --skip-workspaces."
            )
            self.args.skip_workspaces = True

    def load_descriptor(self) -> ProductDescriptor:
        descriptor_data = load_yaml_descriptor(self.args.descriptor_path)

        product_block = descriptor_data.get("product", {})
        name = product_block.get("name")
        if not name:
            raise ValueError("Descriptor is missing required field: product.name")

        slug = product_block.get("slug") or slugify(name)
        git_block = descriptor_data.get("git", {})

        git_config = GitConfig(
            provider=git_block.get("provider", "GitHub"),
            organization=git_block.get("organization") or self._default_git_org(),
            repository=git_block.get("repository") or self._default_git_repo(),
            default_branch=git_block.get("default_branch", "main"),
            feature_prefix=git_block.get("feature_prefix", "feature"),
            directory=git_block.get("directory", f"data_products/{slug}"),
            auto_commit=git_block.get("auto_commit", True),
        )

        env_block = descriptor_data.get("environments", {}).get("dev", {})
        dev_descriptor = EnvironmentDescriptor(
            name="DEV",
            enabled=env_block.get("enabled", True),
            capacity_id=env_block.get("capacity"),
            capacity_type=parse_capacity_type(env_block.get("capacity_type")),
            description=env_block.get("description"),
        )

        product = ProductDescriptor(
            name=name,
            slug=slug,
            owner_email=product_block.get("owner_email"),
            domain=product_block.get("domain"),
            audit_reference=descriptor_data.get("automation", {}).get("audit_reference"),
            git=git_config,
            dev=dev_descriptor,
        )
        return product

    def _default_git_org(self) -> Optional[str]:
        if not self.config_manager:
            return None
        github = self.config_manager.get_github_config()
        return github.get("organization")

    def _default_git_repo(self) -> Optional[str]:
        if not self.config_manager:
            return None
        github = self.config_manager.get_github_config()
        return github.get("repository")

    def onboarding_paths(self, product: ProductDescriptor) -> Dict[str, Path]:
        base_dir = self.repo_root / "data_products" / product.slug
        descriptor_dir = self.repo_root / "data_products" / "onboarding"
        return {
            "base": base_dir,
            "descriptor": descriptor_dir,
            "readme": base_dir / "README.md",
        }

    def _workspace_manager(self) -> WorkspaceManager:
        try:
            return WorkspaceManager()
        except ValueError as exc:
            raise RuntimeError(
                "Microsoft Fabric credentials are required. Set AZURE_TENANT_ID, "
                "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or run with --skip-workspaces."
            ) from exc

    def ensure_dev_workspace(self, product: ProductDescriptor) -> Tuple[Optional[Dict[str, Any]], bool]:
        if self.dry_run:
            console_info(
                f"DRY-RUN: Would create workspace '{product.name} [DEV]' if it did not exist."
            )
            return {"displayName": f"{product.name} [DEV]", "id": None}, False

        if self.args.skip_workspaces or not product.dev.enabled:
            console_info("Skipping workspace provisioning (disabled/enabled flag)")
            return None, False

        workspace_name = f"{product.name} [DEV]"
        manager = self._workspace_manager()

        existing = manager.get_workspace_by_name(workspace_name)
        if existing:
            console_warning(f"Workspace already exists: {workspace_name}")
            return existing, False

        if self.dry_run:
            console_info(f"DRY-RUN: Would create workspace '{workspace_name}'")
            return {"displayName": workspace_name, "id": None}, False

        console_info(f"Creating Fabric workspace: {workspace_name}")
        workspace = manager.create_workspace(
            workspace_name,
            description=product.dev.description
            or f"DEV workspace for {product.name}",
            capacity_id=product.dev.capacity_id,
            capacity_type=product.dev.capacity_type,
        )
        console_success(f"Created workspace '{workspace_name}'")
        
        # Log workspace creation to audit trail
        if self.audit_logger:
            self.audit_logger.log_workspace_creation(
                workspace_id=workspace.get("id"),
                workspace_name=workspace_name,
                product_id=product.slug,
                environment="dev",
                capacity_id=product.dev.capacity_id,
                description=product.dev.description or f"DEV workspace for {product.name}"
            )
        
        # Auto-connect workspace to Git if enabled
        if self.git_connector and self.config_manager:
            git_config = self.config_manager.config.get("git_integration", {})
            if git_config.get("enabled") and git_config.get("auto_connect_workspaces"):
                try:
                    branch_name = git_config.get("default_branch", "main")
                    directory_path = f"/data_products/{product.slug}"
                    
                    console_info(f"Connecting workspace to Git: {product.git.organization}/{product.git.repository}#{branch_name}")
                    self.git_connector.initialize_git_connection(
                        workspace_id=workspace.get("id"),
                        git_provider_type=git_config.get("provider", "GitHub"),
                        organization_name=product.git.organization or git_config.get("organization"),
                        project_name=git_config.get("project"),
                        repository_name=product.git.repository or git_config.get("repository"),
                        branch_name=branch_name,
                        directory_path=directory_path
                    )
                    console_success(f"Connected DEV workspace to Git branch '{branch_name}'")
                    
                    # Log Git connection
                    if self.audit_logger:
                        self.audit_logger.log_git_connection(
                            workspace_id=workspace.get("id"),
                            git_provider=git_config.get("provider", "GitHub"),
                            organization=product.git.organization or git_config.get("organization"),
                            repository=product.git.repository or git_config.get("repository"),
                            branch=branch_name,
                            directory=directory_path
                        )
                except Exception as exc:
                    console_warning(f"Failed to connect workspace to Git: {exc}")
        
        return workspace, True

    def ensure_feature_workspace(
        self, product: ProductDescriptor, feature_ticket: str
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        if self.dry_run:
            workspace_name = f"{product.name} [Feature {feature_ticket}]"
            console_info(f"DRY-RUN: Would create feature workspace '{workspace_name}'")
            return {"displayName": workspace_name, "id": None}, False

        if self.args.skip_workspaces:
            console_info("Skipping feature workspace provisioning (flagged)")
            return None, False

        workspace_name = f"{product.name} [Feature {feature_ticket}]"
        manager = self._workspace_manager()

        existing = manager.get_workspace_by_name(workspace_name)
        if existing:
            console_warning(f"Feature workspace already exists: {workspace_name}")
            return existing, False

        if self.dry_run:
            console_info(f"DRY-RUN: Would create feature workspace '{workspace_name}'")
            return {"displayName": workspace_name, "id": None}, False

        console_info(f"Creating feature workspace: {workspace_name}")
        workspace = manager.create_workspace(
            workspace_name,
            description=f"Feature workspace ({feature_ticket}) for {product.name}",
            capacity_id=product.dev.capacity_id,
            capacity_type=product.dev.capacity_type,
        )
        console_success(f"Created feature workspace '{workspace_name}'")
        
        # Log workspace creation
        if self.audit_logger:
            self.audit_logger.log_workspace_creation(
                workspace_id=workspace.get("id"),
                workspace_name=workspace_name,
                product_id=product.slug,
                environment=f"feature_{feature_ticket}",
                capacity_id=product.dev.capacity_id,
                description=f"Feature workspace ({feature_ticket}) for {product.name}"
            )
        
        return workspace, True

    def generate_scaffold(self, product: ProductDescriptor) -> Path:
        paths = self.onboarding_paths(product)
        base_dir = paths["base"]

        if self.dry_run:
            console_info(
                f"DRY-RUN: Would seed scaffold for {product.slug} from template {self.templates_dir}"
            )
            return base_dir

        if self.args.skip_scaffold:
            console_info("Skipping repo scaffold generation (flagged)")
            return base_dir

        ensure_directory(base_dir)

        if self.templates_dir.exists():
            for item in self.templates_dir.iterdir():
                destination = base_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, destination, dirs_exist_ok=True)
                else:
                    if not destination.exists():
                        shutil.copy2(item, destination)
            console_success(
                f"Seeded scaffold for {product.slug} from template {self.templates_dir}"
            )
        else:
            subdirectories = [
                "workspace",
                "pipelines",
                "notebooks",
                "datasets",
                "docs",
            ]

            for folder in subdirectories:
                ensure_directory(base_dir / folder)

            readme_path = paths["readme"]
            if not readme_path.exists():
                readme_content = (
                    f"# {product.name}\n\n"
                    "This folder was generated by the onboarding automation.\n\n"
                    "## Structure\n"
                    "- `workspace/` – placeholders for Fabric workspace exports\n"
                    "- `pipelines/` – deployment-ready pipeline definitions\n"
                    "- `notebooks/` – notebooks synced with Fabric Git integration\n"
                    "- `datasets/` – semantic models and dataset assets\n"
                    "- `docs/` – product-specific documentation\n"
                )
                readme_path.write_text(readme_content, encoding="utf-8")
                console_success(f"Created scaffold README at {readme_path}")

        return base_dir

    def update_registry(self, product: ProductDescriptor, result: OnboardingResult) -> None:
        if self.dry_run:
            console_info("DRY-RUN: registry update skipped")
            return

        ensure_directory(self.registry_path.parent)
        registry = {"products": []}
        if self.registry_path.exists():
            with self.registry_path.open("r", encoding="utf-8") as handle:
                try:
                    registry = json.load(handle)
                except json.JSONDecodeError:
                    console_warning("Registry file is corrupted. Overwriting with new data.")

        products = registry.setdefault("products", [])
        products = [p for p in products if p.get("slug") != product.slug]

        entry = {
            "product": product.name,
            "slug": product.slug,
            "owner_email": product.owner_email,
            "domain": product.domain,
            "audit_reference": product.audit_reference,
            "dev_workspace_id": (result.dev_workspace or {}).get("id"),
            "feature_workspaces": {},
            "git": {
                "repository": product.git.repository,
                "organization": product.git.organization,
                "directory": product.git.directory,
                "default_branch": product.git.default_branch,
            },
        }

        if result.feature_workspace and self.args.feature_ticket:
            entry["feature_workspaces"][self.args.feature_ticket] = result.feature_workspace.get("id")

        products.append(entry)
        registry["products"] = products

        write_json(self.registry_path, registry)
        console_success(f"Updated onboarding registry at {self.registry_path}")

    def write_audit_log(self, result: OnboardingResult) -> Path:
        ensure_directory(self.audit_dir)
        from datetime import UTC

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{timestamp}_{result.product.slug}.json"
        path = self.audit_dir / filename

        payload = {
            "timestamp": timestamp,
            "product": {
                "name": result.product.name,
                "slug": result.product.slug,
            },
            "dev_workspace": result.dev_workspace,
            "feature_workspace": result.feature_workspace,
            "git_branch": result.git_branch,
            "git_branch_created": result.git_branch_created,
            "scaffold_path": str(result.scaffold_path) if result.scaffold_path else None,
            "registry_updated": result.registry_updated,
        }

        if self.dry_run:
            console_info(f"DRY-RUN: Would write audit log to {path}")
            return path

        write_json(path, payload)
        console_success(f"Audit log written to {path}")
        return path

    def ensure_git_branch(
        self,
        product: ProductDescriptor,
        result: OnboardingResult,
    ) -> Tuple[Optional[str], bool]:
        if self.args.skip_git:
            console_info("Skipping Git automation (flagged)")
            return None, False

        repo = self.repo_root
        branch_name = f"{product.slug}/{product.git.feature_prefix}/{self.args.feature_ticket}" if self.args.feature_ticket else None
        if not branch_name:
            return None, False

        current_branch = git_current_branch(repo)
        if git_branch_exists(repo, branch_name):
            console_warning(f"Git branch already exists: {branch_name}")
            if product.git.auto_commit and result.scaffold_path:
                console_info(f"Updating scaffold commit on existing branch {branch_name}")
                git_checkout(repo, branch_name)
                git_stage_and_commit(
                    repo,
                    [result.scaffold_path],
                    f"chore(onboarding): refresh scaffold for {product.name} ({self.args.feature_ticket})",
                )
                if current_branch != branch_name:
                    git_checkout(repo, current_branch)
            return branch_name, False

        if self.dry_run:
            console_info(f"DRY-RUN: Would create git branch {branch_name}")
            return branch_name, False

        base_branch = product.git.default_branch
        console_info(f"Creating git branch {branch_name} from {base_branch}")

        try:
            if current_branch != base_branch:
                git_checkout(repo, base_branch)
            git_checkout_new(repo, branch_name, base_branch)

            if product.git.auto_commit and result.scaffold_path:
                commit_message = (
                    f"chore(onboarding): bootstrap {product.name} ({self.args.feature_ticket})"
                )
                git_stage_and_commit(repo, [result.scaffold_path], commit_message)
                console_success(f"Committed scaffold on branch {branch_name}")
        finally:
            git_checkout(repo, current_branch)

        return branch_name, True

    def connect_feature_workspace_to_git(
        self, product: ProductDescriptor, workspace_id: str, workspace_name: str, branch_name: str
    ) -> None:
        """Connect feature workspace to Git using the new FabricGitConnector."""
        if self.args.skip_git or self.dry_run:
            console_info("Skipping workspace Git integration (dry-run/flagged)")
            return

        if not (product.git.organization and product.git.repository):
            console_warning("Git organization/repository not provided; cannot connect workspace to Git")
            return
        
        # Skip automated Git connection if manual integration is preferred
        skip_auto_connect = os.getenv("SKIP_AUTO_GIT_CONNECT", "false").lower() == "true"
        if skip_auto_connect:
            console_info("Skipping automated Git connection (SKIP_AUTO_GIT_CONNECT=true)")
            console_info(f"To connect manually:")
            console_info(f"  1. Open workspace '{workspace_name}' in Fabric portal")
            console_info(f"  2. Go to Workspace Settings → Git integration")
            console_info(f"  3. Connect to: {product.git.organization}/{product.git.repository}#{branch_name}")
            console_info(f"  4. Set directory: /data_products/{product.slug}")
            return

        # Use new git_connector if available
        if self.git_connector:
            try:
                directory_path = f"/data_products/{product.slug}/{self.args.feature_ticket}"
                
                console_info(f"Connecting feature workspace to Git: {product.git.organization}/{product.git.repository}#{branch_name}")
                self.git_connector.connect_to_git(
                    workspace_id=workspace_id,
                    branch_name=branch_name,
                    directory_path=directory_path
                )
                console_success(f"Connected feature workspace '{workspace_name}' to Git branch '{branch_name}'")
                
                # Log Git connection
                if self.audit_logger:
                    self.audit_logger.log_git_connection(
                        workspace_id=workspace_id,
                        git_provider=product.git.provider,
                        organization=product.git.organization,
                        repository=product.git.repository,
                        branch=branch_name,
                        directory=directory_path
                    )
                return
            except Exception as exc:
                console_warning(f"Git connector failed, falling back to legacy method: {exc}")

        # Fallback to legacy FabricGitIntegration
        try:
            from utilities.fabric_deployment_pipeline import FabricGitIntegration  # type: ignore
        except (ValueError, ImportError) as exc:
            console_error(
                "Unable to initialize Fabric Git integration. Module not found or "
                "credentials missing. Ensure Azure credentials "
                "(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET) are set or use --skip-git."
            )
            raise RuntimeError(str(exc)) from exc

        integration = FabricGitIntegration(workspace_name)
        directory_path = f"/data_products/{product.slug}/{self.args.feature_ticket}"
        integration.connect_to_git(
            git_provider=product.git.provider,
            organization=product.git.organization,
            repository=product.git.repository,
            branch=branch_name,
            directory_path=directory_path,
        )
        console_success(
            f"Linked workspace '{workspace_name}' to {product.git.organization}/{product.git.repository}#{branch_name}"
        )
        
        # Log Git connection
        if self.audit_logger:
            self.audit_logger.log_git_connection(
                workspace_id=workspace_id,
                git_provider=product.git.provider,
                organization=product.git.organization,
                repository=product.git.repository,
                branch=branch_name,
                directory=directory_path
            )

    def run(self) -> OnboardingResult:
        product = self.load_descriptor()
        console_info(f"Starting onboarding for product '{product.name}' (slug: {product.slug})")

        result = OnboardingResult(product=product)
        result.scaffold_path = self.generate_scaffold(product)

        workspace, created = self.ensure_dev_workspace(product)
        result.dev_workspace = workspace
        result.dev_workspace_created = created

        if self.args.feature_ticket:
            feature_workspace, feature_created = self.ensure_feature_workspace(product, self.args.feature_ticket)
            result.feature_workspace = feature_workspace
            result.feature_workspace_created = feature_created

            branch_name, branch_created = self.ensure_git_branch(product, result)
            result.git_branch = branch_name
            result.git_branch_created = branch_created

            if branch_name and feature_workspace and feature_workspace.get("id"):
                self.connect_feature_workspace_to_git(
                    product, 
                    feature_workspace.get("id"),
                    feature_workspace.get("displayName"),
                    branch_name
                )

        try:
            self.update_registry(product, result)
            result.registry_updated = not self.dry_run
        except Exception as exc:
            console_warning(f"Failed to update registry: {exc}")

        result.audit_log_path = self.write_audit_log(result)

        # Log onboarding completion
        if self.audit_logger and not self.dry_run:
            self.audit_logger.log_onboarding_completed(
                product_id=product.slug,
                workspace_id=result.dev_workspace.get("id") if result.dev_workspace else None,
                feature_workspace_id=result.feature_workspace.get("id") if result.feature_workspace else None,
                git_branch=result.git_branch
            )

        if self.args.json_output and self.console_json:
            self.console_json({
                "product": {
                    "name": product.name,
                    "slug": product.slug,
                },
                "dev_workspace": result.dev_workspace,
                "feature_workspace": result.feature_workspace,
                "git_branch": result.git_branch,
                "scaffold_path": str(result.scaffold_path) if result.scaffold_path else None,
                "registry_updated": result.registry_updated,
                "audit_log": str(result.audit_log_path) if result.audit_log_path else None,
            })

        console_success("Onboarding workflow complete")
        return result


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[List[str]] = None) -> OnboardingArguments:
    parser = argparse.ArgumentParser(
        description="Automate Microsoft Fabric workspace onboarding for a data product"
    )
    parser.add_argument(
        "descriptor",
        help="Path to onboarding descriptor YAML file (relative to repo root if not absolute)",
    )
    parser.add_argument(
        "--feature",
        dest="feature_ticket",
        help="Feature ticket or identifier to create an isolated workspace/branch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without modifying Fabric or Git",
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip Git operations (branch creation, commits, workspace linking)",
    )
    parser.add_argument(
        "--skip-workspaces",
        action="store_true",
        help="Skip Fabric workspace provisioning",
    )
    parser.add_argument(
        "--skip-scaffold",
        action="store_true",
        help="Skip repository scaffold generation",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit JSON summary on completion",
    )

    args = parser.parse_args(argv)
    descriptor_path = Path(args.descriptor)
    if not descriptor_path.is_absolute():
        descriptor_path = repository_root() / descriptor_path

    if not descriptor_path.exists():
        raise FileNotFoundError(f"Descriptor not found: {descriptor_path}")

    return OnboardingArguments(
        descriptor_path=descriptor_path,
        feature_ticket=args.feature_ticket,
        dry_run=args.dry_run,
        skip_git=args.skip_git,
        skip_workspaces=args.skip_workspaces,
        skip_scaffold=args.skip_scaffold,
        json_output=args.json_output,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    try:
        arguments = parse_args(argv)
        onboarder = DataProductOnboarder(arguments)
        onboarder.run()
        return 0
    except Exception as exc:
        console_error(f"Onboarding failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
