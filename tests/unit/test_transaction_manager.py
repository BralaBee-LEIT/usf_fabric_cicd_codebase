"""
Unit tests for transaction rollback system
"""

import os
import pytest
from unittest.mock import Mock, MagicMock, call

from ops.scripts.utilities.transaction_manager import (
    DeploymentTransaction,
    TrackedResource,
    ResourceType,
    TransactionStatus,
    register_transaction,
    unregister_transaction,
    get_active_transactions,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment before each test"""
    env_vars = ["FEATURE_USE_ROLLBACK"]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


def test_transaction_rollback_disabled_by_default(clean_env):
    """Test that rollback is disabled by default (feature flag off)"""
    transaction = DeploymentTransaction(name="test")

    # Track some resources
    mock_cleanup = Mock()
    transaction.track_resource(
        ResourceType.WORKSPACE,
        "ws-123",
        "Test Workspace",
        cleanup_func=mock_cleanup,
    )

    # Rollback should be disabled
    assert transaction.enable_rollback is False

    # Rollback won't cleanup resources
    transaction.rollback()

    # Cleanup should NOT have been called
    mock_cleanup.assert_not_called()
    assert transaction.status == TransactionStatus.FAILED


def test_transaction_rollback_enabled_with_feature_flag(clean_env):
    """Test rollback works when feature flag is enabled"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")

    # Track resources with cleanup functions
    mock_cleanup1 = Mock()
    mock_cleanup2 = Mock()

    transaction.track_resource(
        ResourceType.WORKSPACE,
        "ws-123",
        "Workspace",
        cleanup_func=mock_cleanup1,
        cleanup_args=("ws-123",),
    )

    transaction.track_resource(
        ResourceType.LAKEHOUSE,
        "lh-456",
        "Lakehouse",
        workspace_id="ws-123",
        cleanup_func=mock_cleanup2,
        cleanup_args=("ws-123", "lh-456"),
    )

    assert transaction.enable_rollback is True

    # Rollback
    transaction.rollback()

    # Cleanup functions should have been called in reverse order
    mock_cleanup2.assert_called_once_with("ws-123", "lh-456")
    mock_cleanup1.assert_called_once_with("ws-123")
    assert transaction.status == TransactionStatus.ROLLED_BACK


def test_transaction_rollback_reverse_order(clean_env):
    """Test resources are cleaned up in reverse order (LIFO)"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")
    cleanup_order = []

    def cleanup_func(name):
        cleanup_order.append(name)

    # Track resources
    transaction.track_resource(
        ResourceType.WORKSPACE,
        "1",
        "First",
        cleanup_func=cleanup_func,
        cleanup_args=("first",),
    )
    transaction.track_resource(
        ResourceType.LAKEHOUSE,
        "2",
        "Second",
        cleanup_func=cleanup_func,
        cleanup_args=("second",),
    )
    transaction.track_resource(
        ResourceType.NOTEBOOK,
        "3",
        "Third",
        cleanup_func=cleanup_func,
        cleanup_args=("third",),
    )

    # Rollback
    transaction.rollback()

    # Should cleanup in reverse order: third, second, first
    assert cleanup_order == ["third", "second", "first"]


def test_transaction_commit_prevents_rollback(clean_env):
    """Test that committed transactions cannot be rolled back"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")

    mock_cleanup = Mock()
    transaction.track_resource(
        ResourceType.WORKSPACE, "ws-123", "Workspace", cleanup_func=mock_cleanup
    )

    # Commit
    transaction.commit()
    assert transaction.status == TransactionStatus.COMMITTED

    # Try to rollback
    transaction.rollback()

    # Should not rollback committed transaction
    mock_cleanup.assert_not_called()
    assert transaction.status == TransactionStatus.COMMITTED


def test_transaction_context_manager_success(clean_env):
    """Test context manager commits on success"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    mock_cleanup = Mock()

    with DeploymentTransaction(name="test") as transaction:
        transaction.track_resource(
            ResourceType.WORKSPACE, "ws-123", "Workspace", cleanup_func=mock_cleanup
        )
        # No exception - should commit

    # Should be committed
    assert transaction.status == TransactionStatus.COMMITTED
    mock_cleanup.assert_not_called()


def test_transaction_context_manager_rollback_on_exception(clean_env):
    """Test context manager rolls back on exception"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    mock_cleanup = Mock()

    with pytest.raises(ValueError):
        with DeploymentTransaction(name="test") as transaction:
            transaction.track_resource(
                ResourceType.WORKSPACE,
                "ws-123",
                "Workspace",
                cleanup_func=mock_cleanup,
            )
            raise ValueError("Something went wrong")

    # Should be rolled back
    assert transaction.status == TransactionStatus.ROLLED_BACK
    mock_cleanup.assert_called_once()


def test_transaction_cleanup_with_kwargs(clean_env):
    """Test cleanup function receives kwargs correctly"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")

    mock_cleanup = Mock()
    transaction.track_resource(
        ResourceType.WORKSPACE,
        "ws-123",
        "Workspace",
        cleanup_func=mock_cleanup,
        cleanup_args=("arg1",),
        cleanup_kwargs={"key1": "value1", "key2": "value2"},
    )

    transaction.rollback()

    mock_cleanup.assert_called_once_with("arg1", key1="value1", key2="value2")


def test_transaction_rollback_continues_on_error(clean_env):
    """Test rollback continues even if cleanup fails"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")

    mock_cleanup1 = Mock()
    mock_cleanup2 = Mock(side_effect=Exception("Cleanup failed"))
    mock_cleanup3 = Mock()

    transaction.track_resource(
        ResourceType.WORKSPACE, "1", "First", cleanup_func=mock_cleanup1
    )
    transaction.track_resource(
        ResourceType.LAKEHOUSE, "2", "Second", cleanup_func=mock_cleanup2
    )
    transaction.track_resource(
        ResourceType.NOTEBOOK, "3", "Third", cleanup_func=mock_cleanup3
    )

    # Rollback should continue despite error
    transaction.rollback()

    # All cleanup functions should have been attempted
    mock_cleanup3.assert_called_once()
    mock_cleanup2.assert_called_once()
    mock_cleanup1.assert_called_once()

    # Should have recorded the error
    assert len(transaction.rollback_errors) == 1
    assert "Cleanup failed" in transaction.rollback_errors[0]
    assert transaction.status == TransactionStatus.ROLLED_BACK


def test_transaction_dry_run_mode(clean_env):
    """Test dry run mode logs but doesn't execute cleanup"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test", dry_run=True)

    mock_cleanup = Mock()
    transaction.track_resource(
        ResourceType.WORKSPACE, "ws-123", "Workspace", cleanup_func=mock_cleanup
    )

    transaction.rollback()

    # Cleanup should NOT have been called in dry run
    mock_cleanup.assert_not_called()
    assert transaction.status == TransactionStatus.ROLLED_BACK


def test_transaction_no_cleanup_function(clean_env):
    """Test resources without cleanup function are skipped"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test")

    # Track resource without cleanup function
    transaction.track_resource(
        ResourceType.WORKSPACE, "ws-123", "Workspace", cleanup_func=None
    )

    # Should not raise error
    transaction.rollback()
    assert transaction.status == TransactionStatus.ROLLED_BACK


def test_transaction_get_stats(clean_env):
    """Test transaction statistics"""
    os.environ["FEATURE_USE_ROLLBACK"] = "true"

    transaction = DeploymentTransaction(name="test_stats")

    transaction.track_resource(
        ResourceType.WORKSPACE,
        "ws-123",
        "Workspace",
        metadata={"created_by": "admin"},
    )

    transaction.commit()

    stats = transaction.get_stats()

    assert stats["name"] == "test_stats"
    assert stats["status"] == "committed"
    assert stats["enable_rollback"] is True
    assert stats["resource_count"] == 1
    assert len(stats["resources"]) == 1
    assert stats["resources"][0]["resource_type"] == "workspace"
    assert stats["resources"][0]["resource_id"] == "ws-123"
    assert stats["duration_seconds"] is not None


def test_transaction_track_resource_metadata(clean_env):
    """Test resource tracking with metadata"""
    transaction = DeploymentTransaction(name="test")

    metadata = {"deployment_id": "deploy-123", "environment": "dev"}

    transaction.track_resource(
        ResourceType.LAKEHOUSE,
        "lh-456",
        "Data Lakehouse",
        workspace_id="ws-123",
        metadata=metadata,
    )

    assert len(transaction.resources) == 1
    resource = transaction.resources[0]
    assert resource.resource_type == ResourceType.LAKEHOUSE
    assert resource.resource_id == "lh-456"
    assert resource.resource_name == "Data Lakehouse"
    assert resource.workspace_id == "ws-123"
    assert resource.metadata == metadata


def test_transaction_explicit_enable_rollback(clean_env):
    """Test explicitly enabling rollback regardless of feature flag"""
    # Feature flag off
    assert os.getenv("FEATURE_USE_ROLLBACK") != "true"

    # But explicitly enable
    transaction = DeploymentTransaction(name="test", enable_rollback=True)

    # Should still be disabled because feature flag is off
    assert transaction.enable_rollback is False


def test_transaction_registry(clean_env):
    """Test transaction registration and monitoring"""
    transaction1 = DeploymentTransaction(name="tx1")
    transaction2 = DeploymentTransaction(name="tx2")

    register_transaction(transaction1)
    register_transaction(transaction2)

    active = get_active_transactions()
    assert len(active) == 2
    names = [tx["name"] for tx in active]
    assert "tx1" in names
    assert "tx2" in names

    unregister_transaction("tx1")
    active = get_active_transactions()
    assert len(active) == 1
    assert active[0]["name"] == "tx2"
