"""Out of Office request data models"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class OOORequest(BaseModel):
    """Out of Office request model"""

    start_date: datetime = Field(
        ...,
        description="Start date and time of leave"
    )
    end_date: datetime = Field(
        ...,
        description="End date and time of leave"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Custom OOO message"
    )
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for leave"
    )
    emergency_contact: Optional[str] = Field(
        None,
        max_length=300,
        description="Emergency contact information"
    )
    enable_slack: bool = Field(
        True,
        description="Update Slack status"
    )
    enable_calendar: bool = Field(
        True,
        description="Create Google Calendar event"
    )
    enable_email_signature: bool = Field(
        True,
        description="Update email signature"
    )
    enable_email_autoreply: bool = Field(
        True,
        description="Enable email auto-reply"
    )

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Ensure end date is after start date"""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2026-04-20T00:00:00",
                "end_date": "2026-04-30T23:59:59",
                "message": "On vacation in Hawaii 🌴",
                "reason": "Annual vacation",
                "emergency_contact": "Contact Jane Doe at jane@company.com for urgent matters",
                "enable_slack": True,
                "enable_calendar": True,
                "enable_email_signature": True,
                "enable_email_autoreply": True
            }
        }


class OOOResponse(BaseModel):
    """Out of Office operation response"""

    success: bool
    message: str
    details: dict = {}
    errors: dict = {}
