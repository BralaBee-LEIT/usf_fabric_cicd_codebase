"""
Minimal placeholder client for Microsoft Purview
TODO: Implement full Purview API integration
"""

import logging

from .constants import PURVIEW_ENDPOINT
from .output import console_warning

logger = logging.getLogger(__name__)


def trigger_scan(collection: str, name: str) -> dict:
    """
    Trigger a Purview scan (placeholder implementation)

    Args:
        collection: Purview collection name
        name: Scan name to trigger

    Returns:
        Dictionary with scan status

    Note:
        This is a placeholder implementation. Real implementation should:
        - Authenticate with Purview API
        - Validate collection and scan exist
        - Trigger the scan via REST API
        - Return actual scan status and ID
    """
    console_warning(
        f"Purview scan trigger is a placeholder - '{name}' in collection '{collection}'"
    )
    logger.info(
        f"Placeholder: Triggering scan '{name}' in collection '{collection}' at {PURVIEW_ENDPOINT}"
    )

    return {
        "status": "queued",
        "message": "Placeholder implementation - no actual scan triggered",
        "collection": collection,
        "scan_name": name,
        "endpoint": PURVIEW_ENDPOINT,
    }
