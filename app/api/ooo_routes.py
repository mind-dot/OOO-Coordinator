"""Out of Office API routes"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.ooo_request import OOORequest, OOOResponse
from app.integrations.slack_client import SlackIntegration
from app.integrations.google_client import GoogleIntegration
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ooo", tags=["Out of Office"])


@router.post("/set", response_model=OOOResponse)
async def set_ooo(request: OOORequest, background_tasks: BackgroundTasks):
    """
    Set out-of-office status across all platforms

    This endpoint:
    1. Updates Slack status (if enabled)
    2. Creates Google Calendar event (if enabled)
    3. Updates email signature (if enabled)
    4. Enables Gmail auto-reply (if enabled)
    """
    results = {
        "slack": None,
        "calendar": None,
        "email_signature": None,
        "email_autoreply": None
    }
    errors = {}

    try:
        # Update Slack status
        if request.enable_slack and settings.slack_user_token:
            try:
                slack = SlackIntegration(
                    user_token=settings.slack_user_token,
                    user_id=settings.slack_user_id
                )
                slack_result = await slack.set_ooo_status(
                    message=request.message,
                    end_date=request.end_date
                )
                results["slack"] = slack_result
                if not slack_result.get("success"):
                    errors["slack"] = slack_result.get("error")
            except Exception as e:
                logger.error(f"Slack integration error: {str(e)}")
                errors["slack"] = str(e)

        # Create Google Calendar event
        if request.enable_calendar:
            try:
                google = GoogleIntegration()
                calendar_result = await google.create_calendar_event(
                    start_date=request.start_date,
                    end_date=request.end_date,
                    message=request.message
                )
                results["calendar"] = calendar_result
                if not calendar_result.get("success"):
                    errors["calendar"] = calendar_result.get("error")
            except Exception as e:
                logger.error(f"Calendar integration error: {str(e)}")
                errors["calendar"] = str(e)

        # Update email signature
        if request.enable_email_signature and settings.email_address:
            try:
                google = GoogleIntegration()
                signature_result = await google.update_email_signature(
                    ooo_message=request.message,
                    end_date=request.end_date,
                    email_address=settings.email_address
                )
                results["email_signature"] = signature_result
                if not signature_result.get("success"):
                    errors["email_signature"] = signature_result.get("error")
            except Exception as e:
                logger.error(f"Email signature update error: {str(e)}")
                errors["email_signature"] = str(e)

        # Enable Gmail auto-reply
        if request.enable_email_autoreply:
            try:
                google = GoogleIntegration()

                # Build auto-reply message
                auto_reply_message = f"{request.message}\n\n"
                if request.emergency_contact:
                    auto_reply_message += f"{request.emergency_contact}\n\n"
                auto_reply_message += f"I will return on {request.end_date.strftime('%B %d, %Y')} and will respond to your email then."

                autoreply_result = await google.set_gmail_vacation(
                    start_date=request.start_date,
                    end_date=request.end_date,
                    message=auto_reply_message
                )
                results["email_autoreply"] = autoreply_result
                if not autoreply_result.get("success"):
                    errors["email_autoreply"] = autoreply_result.get("error")
            except Exception as e:
                logger.error(f"Gmail auto-reply error: {str(e)}")
                errors["email_autoreply"] = str(e)

        # Determine overall success
        success = len(errors) == 0
        message = "Out of office settings updated successfully" if success else "Some updates failed"

        return OOOResponse(
            success=success,
            message=message,
            details=results,
            errors=errors
        )

    except Exception as e:
        logger.error(f"Unexpected error in set_ooo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear", response_model=OOOResponse)
async def clear_ooo():
    """
    Clear out-of-office status (for when you return)

    This endpoint:
    1. Clears Slack status
    2. Note: Calendar events and email settings must be manually reverted
    """
    results = {}
    errors = {}

    try:
        # Clear Slack status
        if settings.slack_user_token:
            try:
                slack = SlackIntegration(
                    user_token=settings.slack_user_token,
                    user_id=settings.slack_user_id
                )
                slack_result = await slack.clear_ooo_status()
                results["slack"] = slack_result
                if not slack_result.get("success"):
                    errors["slack"] = slack_result.get("error")
            except Exception as e:
                logger.error(f"Error clearing Slack status: {str(e)}")
                errors["slack"] = str(e)

        success = len(errors) == 0
        message = "Out of office cleared" if success else "Some operations failed"

        return OOOResponse(
            success=success,
            message=message,
            details=results,
            errors=errors
        )

    except Exception as e:
        logger.error(f"Unexpected error in clear_ooo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """
    Get current configuration status

    Returns which integrations are configured
    """
    return {
        "slack_configured": bool(settings.slack_user_token),
        "google_configured": bool(settings.google_client_id),
        "email_configured": bool(settings.email_address),
        "timezone": settings.timezone
    }
