"""Tests for data product onboarding workflow automation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pytest

from scripts import onboard_data_product as onboarding


def test_slugify_normalizes_names():
    """Ensure product names are converted into filesystem-safe slugs."""

    assert onboarding.slugify("Data Product 123") == "data_product_123"
    assert onboarding.slugify("  Mixed-Case---Name  ") == "mixed_case_name"
    assert onboarding.slugify("Name! With @Symbols") == "name_with_symbols"


def test_parse_capacity_type_variants():
    """Capacity type parser should accept friendly values and defaults."""

    assert onboarding.parse_capacity_type(None) == onboarding.CapacityType.TRIAL
    assert onboarding.parse_capacity_type("trial") == onboarding.CapacityType.TRIAL
    assert onboarding.parse_capacity_type("Premium-P1") == onboarding.CapacityType.PREMIUM_P1
    assert onboarding.parse_capacity_type("fabric_f8") == onboarding.CapacityType.FABRIC_F8


def test_parse_capacity_type_invalid_value():
    """Invalid capacity descriptors should raise a helpful error."""

    with pytest.raises(ValueError):
        onboarding.parse_capacity_type("unsupported_tier")


def test_load_env_file_sets_missing_variables(tmp_path, monkeypatch):
    """Environment loader should populate unset variables from dotenv files."""

    env_file = tmp_path / ".env.test"
    env_file.write_text("NEW_VAR=value\nEXISTING_VAR=should_not_override\n", encoding="utf-8")

    monkeypatch.delenv("NEW_VAR", raising=False)
    monkeypatch.setenv("EXISTING_VAR", "original")

    loaded = onboarding.load_env_file(env_file)

    assert loaded == 1
    assert os.getenv("NEW_VAR") == "value"
    assert os.getenv("EXISTING_VAR") == "original"


def test_onboarder_run_dry_run(monkeypatch, tmp_path):
    """Running the onboarding workflow in dry-run mode should avoid side effects."""

    fake_repo = tmp_path / "repo"
    templates_dir = fake_repo / "data_products" / "templates" / "base_product"
    templates_dir.mkdir(parents=True)

    descriptor_path = fake_repo / "descriptor.yaml"
    descriptor_path.write_text(
        """
product:
  name: Test Fabric Product
automation:
  audit_reference: AUD-123
environments:
  dev:
    capacity_type: premium_p1
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    class DummyConfigManager:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def get_github_config(self) -> dict:
            return {"organization": "dummy-org", "repository": "dummy-repo"}

    monkeypatch.setattr(onboarding, "repository_root", lambda: fake_repo)
    monkeypatch.setattr(onboarding, "ConfigManager", DummyConfigManager)

    args = onboarding.OnboardingArguments(
        descriptor_path=descriptor_path,
        feature_ticket=None,
        dry_run=True,
        skip_git=True,
        skip_workspaces=False,
        skip_scaffold=False,
        json_output=False,
    )

    onboarder = onboarding.DataProductOnboarder(args)
    result = onboarder.run()

    assert result.product.slug == "test_fabric_product"
    assert result.dev_workspace == {"displayName": "Test Fabric Product [DEV]", "id": None}
    assert result.dev_workspace_created is False
    assert result.feature_workspace is None
    assert result.registry_updated is False

    expected_scaffold_dir = fake_repo / "data_products" / "test_fabric_product"
    assert result.scaffold_path == expected_scaffold_dir
    assert not result.scaffold_path.exists()

    assert isinstance(result.audit_log_path, Path)
    assert result.audit_log_path.parent == fake_repo / ".onboarding_logs"
    assert not result.audit_log_path.exists()


def test_onboarder_run_writes_registry_and_audit(monkeypatch, tmp_path):
        """Executing a non-dry-run onboarding should persist registry and audit logs."""

        fake_repo = tmp_path / "repo"
        templates_dir = fake_repo / "data_products" / "templates" / "base_product"
        templates_dir.mkdir(parents=True)
        (templates_dir / "README.md").write_text("Template README", encoding="utf-8")

        descriptor_path = fake_repo / "descriptor.yaml"
        descriptor_path.write_text(
                """
product:
    name: Another Product
    owner_email: owner@example.com
automation:
    audit_reference: AUD-999
git:
    organization: test-org
    repository: test-repo
environments:
    dev:
        enabled: true
        capacity_type: trial
                """.strip()
                + "\n",
                encoding="utf-8",
        )

        class DummyConfigManager:
                def __init__(self, *_args, **_kwargs) -> None:
                        pass

                def get_github_config(self) -> dict:
                        return {"organization": "dummy-org", "repository": "dummy-repo"}

        class DummyWorkspaceManager:
                def __init__(self, *_args, **_kwargs) -> None:
                        raise AssertionError(
                                "WorkspaceManager should not be instantiated when skip_workspaces=True"
                        )

        monkeypatch.setattr(onboarding, "repository_root", lambda: fake_repo)
        monkeypatch.setattr(onboarding, "ConfigManager", DummyConfigManager)
        monkeypatch.setattr(onboarding, "WorkspaceManager", DummyWorkspaceManager)

        args = onboarding.OnboardingArguments(
                descriptor_path=descriptor_path,
                feature_ticket=None,
                dry_run=False,
                skip_git=True,
                skip_workspaces=True,
                skip_scaffold=False,
                json_output=False,
        )

        onboarder = onboarding.DataProductOnboarder(args)
        result = onboarder.run()

        product_dir = fake_repo / "data_products" / "another_product"
        assert result.scaffold_path == product_dir
        assert product_dir.exists()
        copied_readme = product_dir / "README.md"
        assert copied_readme.exists()
        assert copied_readme.read_text(encoding="utf-8") == "Template README"

        registry_path = fake_repo / "data_products" / "registry.json"
        assert registry_path.exists()
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert registry["products"][0]["slug"] == "another_product"
        assert registry["products"][0]["owner_email"] == "owner@example.com"

        assert result.audit_log_path and result.audit_log_path.exists()
        audit_payload = json.loads(result.audit_log_path.read_text(encoding="utf-8"))
        assert audit_payload["product"]["slug"] == "another_product"
        assert audit_payload["registry_updated"] is True

        assert result.registry_updated is True
        assert result.dev_workspace is None


def test_ensure_git_branch_existing_branch(monkeypatch, tmp_path):
    """If a feature branch already exists, it should be updated in place."""

    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()

    class DummyConfigManager:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def get_github_config(self) -> dict:
            return {"organization": "dummy-org", "repository": "dummy-repo"}

    monkeypatch.setattr(onboarding, "repository_root", lambda: fake_repo)
    monkeypatch.setattr(onboarding, "ConfigManager", DummyConfigManager)

    args = onboarding.OnboardingArguments(
        descriptor_path=fake_repo / "descriptor.yaml",
        feature_ticket="ABC-123",
        dry_run=False,
        skip_git=False,
        skip_workspaces=True,
        skip_scaffold=False,
        json_output=False,
    )

    args.descriptor_path.write_text("product:\n  name: Git Product\n", encoding="utf-8")

    onboarder = onboarding.DataProductOnboarder(args)
    product = onboarder.load_descriptor()
    result = onboarding.OnboardingResult(product=product)
    scaffold_dir = fake_repo / "data_products" / product.slug
    result.scaffold_path = scaffold_dir

    scaffold_dir.parent.mkdir(parents=True, exist_ok=True)
    scaffold_dir.mkdir()

    calls = []

    monkeypatch.setattr(onboarding, "git_current_branch", lambda repo: "main")
    monkeypatch.setattr(onboarding, "git_branch_exists", lambda repo, branch: True)

    def fake_git_checkout(repo, branch):
        calls.append(("checkout", branch))

    def fake_git_stage_and_commit(repo, paths, message):
        calls.append(("commit", [str(p.relative_to(repo)) for p in paths], message))

    monkeypatch.setattr(onboarding, "git_checkout", fake_git_checkout)
    monkeypatch.setattr(onboarding, "git_checkout_new", lambda repo, branch, base: calls.append(("checkout_new", branch, base)))
    monkeypatch.setattr(onboarding, "git_stage_and_commit", fake_git_stage_and_commit)

    branch_name, created = onboarder.ensure_git_branch(product, result)

    assert branch_name == f"{product.slug}/{product.git.feature_prefix}/ABC-123"
    assert created is False

    assert calls[0] == ("checkout", branch_name)
    assert calls[1][0] == "commit"
    assert "refresh scaffold" in calls[1][2]
    assert "ABC-123" in calls[1][2]
    assert calls[2] == ("checkout", "main")


def test_ensure_git_branch_creates_branch(monkeypatch, tmp_path):
    """When the feature branch does not exist, it should be created and committed."""

    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()

    class DummyConfigManager:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def get_github_config(self) -> dict:
            return {"organization": "dummy-org", "repository": "dummy-repo"}

    monkeypatch.setattr(onboarding, "repository_root", lambda: fake_repo)
    monkeypatch.setattr(onboarding, "ConfigManager", DummyConfigManager)

    args = onboarding.OnboardingArguments(
        descriptor_path=fake_repo / "descriptor.yaml",
        feature_ticket="FEAT-42",
        dry_run=False,
        skip_git=False,
        skip_workspaces=True,
        skip_scaffold=False,
        json_output=False,
    )

    args.descriptor_path.write_text("product:\n  name: Branch Product\n", encoding="utf-8")

    onboarder = onboarding.DataProductOnboarder(args)
    product = onboarder.load_descriptor()
    result = onboarding.OnboardingResult(product=product)
    scaffold_dir = fake_repo / "data_products" / product.slug
    result.scaffold_path = scaffold_dir

    scaffold_dir.parent.mkdir(parents=True, exist_ok=True)
    scaffold_dir.mkdir()

    calls = []

    monkeypatch.setattr(onboarding, "git_current_branch", lambda repo: "main")
    monkeypatch.setattr(onboarding, "git_branch_exists", lambda repo, branch: False)

    def fake_git_checkout(repo, branch):
        calls.append(("checkout", branch))

    def fake_git_checkout_new(repo, branch, base):
        calls.append(("checkout_new", branch, base))

    def fake_git_stage_and_commit(repo, paths, message):
        calls.append(("commit", [str(p.relative_to(repo)) for p in paths], message))

    monkeypatch.setattr(onboarding, "git_checkout", fake_git_checkout)
    monkeypatch.setattr(onboarding, "git_checkout_new", fake_git_checkout_new)
    monkeypatch.setattr(onboarding, "git_stage_and_commit", fake_git_stage_and_commit)

    branch_name, created = onboarder.ensure_git_branch(product, result)

    expected_branch = f"{product.slug}/{product.git.feature_prefix}/FEAT-42"
    assert branch_name == expected_branch
    assert created is True

    assert calls[0] == ("checkout_new", expected_branch, product.git.default_branch)
    assert calls[1][0] == "commit"
    assert "bootstrap" in calls[1][2]
    assert calls[2] == ("checkout", "main")


def test_onboarder_full_workflow_with_feature(monkeypatch, tmp_path):
    """Test complete end-to-end workflow including feature workspace and git integration."""

    fake_repo = tmp_path / "repo"
    templates_dir = fake_repo / "data_products" / "templates" / "base_product"
    templates_dir.mkdir(parents=True)
    (templates_dir / "README.md").write_text("Template README", encoding="utf-8")

    descriptor_path = fake_repo / "descriptor.yaml"
    descriptor_path.write_text(
        """
product:
  name: Full Workflow Product
  owner_email: owner@example.com
  domain: Analytics
automation:
  audit_reference: TEST-100
git:
  organization: test-org
  repository: test-repo
environments:
  dev:
    enabled: true
    capacity_type: trial
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    class DummyConfigManager:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def get_github_config(self) -> dict:
            return {"organization": "dummy-org", "repository": "dummy-repo"}

    class DummyWorkspaceManager:
        def get_workspace_by_name(self, name):
            return None

        def create_workspace(self, name, description=None, capacity_id=None, capacity_type=None):
            return {
                "id": f"ws-{name.replace(' ', '-').lower()}",
                "displayName": name,
                "description": description,
            }

    monkeypatch.setattr(onboarding, "repository_root", lambda: fake_repo)
    monkeypatch.setattr(onboarding, "ConfigManager", DummyConfigManager)
    monkeypatch.setattr(onboarding, "WorkspaceManager", DummyWorkspaceManager)

    # Set fake credentials to prevent auto-skip
    monkeypatch.setenv("AZURE_TENANT_ID", "fake-tenant-id")
    monkeypatch.setenv("AZURE_CLIENT_ID", "fake-client-id")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "fake-client-secret")

    git_operations = []

    def track_git_current_branch(repo):
        return "main"

    def track_git_branch_exists(repo, branch):
        return False

    def track_git_checkout(repo, branch):
        git_operations.append(("checkout", branch))

    def track_git_checkout_new(repo, branch, base):
        git_operations.append(("checkout_new", branch, base))

    def track_git_stage_and_commit(repo, paths, message):
        git_operations.append(("commit", len(paths), message))

    monkeypatch.setattr(onboarding, "git_current_branch", track_git_current_branch)
    monkeypatch.setattr(onboarding, "git_branch_exists", track_git_branch_exists)
    monkeypatch.setattr(onboarding, "git_checkout", track_git_checkout)
    monkeypatch.setattr(onboarding, "git_checkout_new", track_git_checkout_new)
    monkeypatch.setattr(onboarding, "git_stage_and_commit", track_git_stage_and_commit)

    args = onboarding.OnboardingArguments(
        descriptor_path=descriptor_path,
        feature_ticket="TEST-100",
        dry_run=False,
        skip_git=False,
        skip_workspaces=False,
        skip_scaffold=False,
        json_output=False,
    )

    # Mock the entire git workflow to avoid Git integration complexity
    def mock_ensure_git_branch(self, product, result):
        branch_name = f"{product.slug}/{product.git.feature_prefix}/{args.feature_ticket}"
        git_operations.append(("branch_created", branch_name))
        return branch_name, True

    monkeypatch.setattr(
        onboarding.DataProductOnboarder,
        "ensure_git_branch",
        mock_ensure_git_branch,
    )

    # Mock connect_feature_workspace_to_git to avoid MSAL auth
    def mock_connect(self, product, workspace_id, workspace_name, branch_name):
        git_operations.append(("connected_to_git", workspace_id, workspace_name, branch_name))

    monkeypatch.setattr(
        onboarding.DataProductOnboarder,
        "connect_feature_workspace_to_git",
        mock_connect,
    )

    onboarder = onboarding.DataProductOnboarder(args)
    result = onboarder.run()

    # Verify complete workflow
    assert result.product.slug == "full_workflow_product"
    assert result.product.owner_email == "owner@example.com"

    # Verify DEV workspace created
    assert result.dev_workspace is not None
    assert result.dev_workspace["displayName"] == "Full Workflow Product [DEV]"
    assert result.dev_workspace_created is True

    # Verify feature workspace created
    assert result.feature_workspace is not None
    assert result.feature_workspace["displayName"] == "Full Workflow Product [Feature TEST-100]"
    assert result.feature_workspace_created is True

    # Verify git branch created (via mock)
    assert result.git_branch is not None
    assert "full_workflow_product" in result.git_branch
    assert "TEST-100" in result.git_branch
    assert result.git_branch_created is True

    # Verify scaffold created
    assert result.scaffold_path is not None
    assert result.scaffold_path.exists()
    readme = result.scaffold_path / "README.md"
    assert readme.exists()
    assert readme.read_text(encoding="utf-8") == "Template README"

    # Verify registry updated
    assert result.registry_updated is True
    registry_path = fake_repo / "data_products" / "registry.json"
    assert registry_path.exists()
    import json

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry["products"]) == 1
    product_entry = registry["products"][0]
    assert product_entry["slug"] == "full_workflow_product"
    assert product_entry["owner_email"] == "owner@example.com"
    assert product_entry["dev_workspace_id"] == result.dev_workspace["id"]
    assert "TEST-100" in product_entry["feature_workspaces"]

    # Verify audit log created
    assert result.audit_log_path is not None
    assert result.audit_log_path.exists()
    audit = json.loads(result.audit_log_path.read_text(encoding="utf-8"))
    assert audit["product"]["slug"] == "full_workflow_product"
    assert audit["git_branch_created"] is True
    assert audit["registry_updated"] is True

    # Verify git operations occurred
    assert len(git_operations) >= 1
    assert any("branch_created" in op for op in git_operations)
    assert any("connected_to_git" in op for op in git_operations)
