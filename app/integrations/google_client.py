"""Google Calendar and Gmail API integration"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
]


class GoogleIntegration:
    """Google Calendar and Gmail API client"""

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        token_file: str = "token.json"
    ):
        """
        Initialize Google API client

        Args:
            credentials: Google OAuth credentials
            token_file: Path to store/load credentials
        """
        self.credentials = credentials or self._load_credentials(token_file)
        self.token_file = token_file

    def _load_credentials(self, token_file: str) -> Optional[Credentials]:
        """Load credentials from file"""
        if os.path.exists(token_file):
            return Credentials.from_authorized_user_file(token_file, SCOPES)
        return None

    def _save_credentials(self, credentials: Credentials):
        """Save credentials to file"""
        with open(self.token_file, 'w') as token:
            token.write(credentials.to_json())

    async def create_calendar_event(
        self,
        start_date: datetime,
        end_date: datetime,
        message: str
    ) -> dict:
        """
        Create out-of-office calendar event

        Args:
            start_date: Event start date
            end_date: Event end date
            message: Event description

        Returns:
            dict with success status and event details
        """
        try:
            service = build('calendar', 'v3', credentials=self.credentials)

            # Create out-of-office event
            event = {
                'summary': 'Out of Office',
                'description': message,
                'start': {
                    'date': start_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': end_date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC',
                },
                'transparency': 'transparent',  # Show as "Free"
                'visibility': 'public',
                'eventType': 'outOfOffice'
            }

            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            logger.info(f"Calendar event created: {created_event.get('id')}")
            return {
                "success": True,
                "message": "Calendar event created",
                "event_id": created_event.get('id'),
                "event_link": created_event.get('htmlLink')
            }

        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def set_gmail_vacation(
        self,
        start_date: datetime,
        end_date: datetime,
        message: str,
        subject: str = "Out of Office"
    ) -> dict:
        """
        Enable Gmail vacation auto-responder

        Args:
            start_date: Vacation start date
            end_date: Vacation end date
            message: Auto-reply message
            subject: Auto-reply subject

        Returns:
            dict with success status
        """
        try:
            service = build('gmail', 'v1', credentials=self.credentials)

            vacation_settings = {
                'enableAutoReply': True,
                'responseSubject': subject,
                'responseBodyPlainText': message,
                'startTime': int(start_date.timestamp() * 1000),  # milliseconds
                'endTime': int(end_date.timestamp() * 1000),
                'restrictToContacts': False,
                'restrictToDomain': False
            }

            result = service.users().settings().updateVacation(
                userId='me',
                body=vacation_settings
            ).execute()

            logger.info("Gmail vacation responder enabled")
            return {
                "success": True,
                "message": "Gmail auto-reply enabled",
                "details": result
            }

        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error setting Gmail vacation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_email_signature(
        self,
        ooo_message: str,
        end_date: datetime,
        email_address: str
    ) -> dict:
        """
        Update Gmail signature with OOO notice

        Args:
            ooo_message: OOO message to append
            end_date: Return date
            email_address: User's email address

        Returns:
            dict with success status
        """
        try:
            service = build('gmail', 'v1', credentials=self.credentials)

            # Get current signature
            send_as = service.users().settings().sendAs().get(
                userId='me',
                sendAsEmail=email_address
            ).execute()

            current_signature = send_as.get('signature', '')

            # Append OOO notice
            ooo_notice = f"\n\n---\n🏖️ OUT OF OFFICE\n{ooo_message}\nReturning: {end_date.strftime('%B %d, %Y')}"
            new_signature = current_signature + ooo_notice

            # Update signature
            send_as['signature'] = new_signature
            updated = service.users().settings().sendAs().update(
                userId='me',
                sendAsEmail=email_address,
                body=send_as
            ).execute()

            logger.info("Email signature updated")
            return {
                "success": True,
                "message": "Email signature updated",
                "signature": new_signature
            }

        except HttpError as e:
            logger.error(f"Gmail signature update error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error updating signature: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
