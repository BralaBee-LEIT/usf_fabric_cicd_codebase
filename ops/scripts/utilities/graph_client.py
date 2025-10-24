"""
Microsoft Graph API Client for User/Group Lookups

This module provides functionality to look up Azure AD Object IDs
from user principal names (emails) or group display names.
"""

import os
import logging
from typing import Optional
import requests
from azure.identity import ClientSecretCredential

logger = logging.getLogger(__name__)


class GraphClient:
    """Microsoft Graph API client for user and group operations"""

    def __init__(self):
        """Initialize Graph client with service principal credentials"""
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required environment variables: "
                "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
            )

        # Initialize credential
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def _get_access_token(self) -> str:
        """Get access token for Microsoft Graph API"""
        token = self.credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Microsoft Graph API"""
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        url = f"{self.graph_endpoint}/{endpoint.lstrip('/')}"

        response = requests.request(method, url, headers=headers, **kwargs)

        if not response.ok:
            logger.error(f"Graph API error: {response.status_code} - {response.text}")
            response.raise_for_status()

        return response

    def get_user_by_upn(self, user_principal_name: str) -> Optional[dict]:
        """
        Get user by User Principal Name (email)

        Args:
            user_principal_name: User's email/UPN

        Returns:
            User object dict or None if not found
        """
        try:
            response = self._make_request("GET", f"users/{user_principal_name}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"User not found: {user_principal_name}")
                return None
            raise

    def get_group_by_display_name(self, display_name: str) -> Optional[dict]:
        """
        Get group by display name

        Args:
            display_name: Group display name

        Returns:
            Group object dict or None if not found
        """
        try:
            # Search for group by display name
            response = self._make_request(
                "GET",
                f"groups?$filter=displayName eq '{display_name}'&$select=id,displayName",
            )
            data = response.json()
            groups = data.get("value", [])

            if not groups:
                logger.warning(f"Group not found: {display_name}")
                return None

            if len(groups) > 1:
                logger.warning(
                    f"Multiple groups found with name '{display_name}', using first match"
                )

            return groups[0]

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error searching for group: {e}")
            return None

    def get_service_principal_by_display_name(
        self, display_name: str
    ) -> Optional[dict]:
        """
        Get service principal by display name

        Args:
            display_name: Service principal display name

        Returns:
            Service principal object dict or None if not found
        """
        try:
            response = self._make_request(
                "GET",
                f"servicePrincipals?$filter=displayName eq '{display_name}'&$select=id,displayName,appId",
            )
            data = response.json()
            sps = data.get("value", [])

            if not sps:
                logger.warning(f"Service principal not found: {display_name}")
                return None

            if len(sps) > 1:
                logger.warning(
                    f"Multiple service principals found with name '{display_name}', using first match"
                )

            return sps[0]

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error searching for service principal: {e}")
            return None


def get_user_object_id(user_principal_name: str) -> Optional[str]:
    """
    Helper function to get user Object ID from email/UPN

    Args:
        user_principal_name: User's email/UPN

    Returns:
        Object ID (GUID) or None if not found
    """
    try:
        client = GraphClient()
        user = client.get_user_by_upn(user_principal_name)
        return user.get("id") if user else None
    except Exception as e:
        logger.error(f"Error getting user Object ID: {e}")
        return None


def get_group_object_id(display_name: str) -> Optional[str]:
    """
    Helper function to get group Object ID from display name

    Args:
        display_name: Group display name

    Returns:
        Object ID (GUID) or None if not found
    """
    try:
        client = GraphClient()
        group = client.get_group_by_display_name(display_name)
        return group.get("id") if group else None
    except Exception as e:
        logger.error(f"Error getting group Object ID: {e}")
        return None


def get_service_principal_object_id(display_name: str) -> Optional[str]:
    """
    Helper function to get service principal Object ID from display name

    Args:
        display_name: Service principal display name

    Returns:
        Object ID (GUID) or None if not found
    """
    try:
        client = GraphClient()
        sp = client.get_service_principal_by_display_name(display_name)
        return sp.get("id") if sp else None
    except Exception as e:
        logger.error(f"Error getting service principal Object ID: {e}")
        return None
