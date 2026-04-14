"""Slack API integration"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Slack API client for updating user status"""

    def __init__(self, user_token: str, user_id: Optional[str] = None):
        """
        Initialize Slack client

        Args:
            user_token: Slack user OAuth token (xoxp-...)
            user_id: Optional Slack user ID
        """
        self.client = WebClient(token=user_token)
        self.user_id = user_id

    async def set_ooo_status(
        self,
        message: str,
        end_date: datetime,
        emoji: str = ":palm_tree:"
    ) -> dict:
        """
        Set out-of-office Slack status

        Args:
            message: Status message
            end_date: When OOO ends (for status expiration)
            emoji: Status emoji

        Returns:
            dict with success status and details
        """
        try:
            # Calculate expiration timestamp (Unix timestamp)
            expiration = int(end_date.timestamp())

            # Update user profile
            response = self.client.users_profile_set(
                profile={
                    "status_text": message,
                    "status_emoji": emoji,
                    "status_expiration": expiration
                }
            )

            if response["ok"]:
                logger.info(f"Slack status updated successfully")
                return {
                    "success": True,
                    "message": "Slack status updated",
                    "status_text": message,
                    "status_emoji": emoji,
                    "expires_at": end_date.isoformat()
                }
            else:
                logger.error(f"Slack API error: {response}")
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error")
                }

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {
                "success": False,
                "error": e.response["error"]
            }
        except Exception as e:
            logger.error(f"Unexpected error updating Slack status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def clear_ooo_status(self) -> dict:
        """
        Clear OOO status (when returning from leave)

        Returns:
            dict with success status
        """
        try:
            response = self.client.users_profile_set(
                profile={
                    "status_text": "",
                    "status_emoji": "",
                    "status_expiration": 0
                }
            )

            if response["ok"]:
                logger.info("Slack status cleared")
                return {
                    "success": True,
                    "message": "Slack status cleared"
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error")
                }

        except SlackApiError as e:
            logger.error(f"Error clearing Slack status: {e.response['error']}")
            return {
                "success": False,
                "error": e.response["error"]
            }
