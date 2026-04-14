# OOO Consolidator

A unified Out of Office automation tool that updates OOO status from a single form.

## Features

### Single Form Input
Enter your leave information once:
- Leave dates (start/end)
- Reason for leave (optional)
- Emergency contact information
- Custom OOO message

### Automated Updates
The tool automatically updates:
- ✅ **Slack Status** - Set custom status with OOO emoji and message
- ✅ **Google Calendar** - Create out-of-office event with visibility settings
- ✅ **Email Signature** - Append OOO notice to your signature
- ✅ **Email Auto-Reply** - Configure out-of-office auto-responder

## Architecture

```
┌─────────────────┐
│   Web Form UI   │
│  (Enter OOO)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │
│  (Orchestrator) │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌────────┐ ┌───────┐ ┌──────┐ ┌────────┐
│ Slack  │ │Google │ │Gmail │ │Gmail   │
│  API   │ │  Cal  │ │Signa-│ │Auto    │
│        │ │  API  │ │ture  │ │Reply   │
└────────┘ └───────┘ └──────┘ └────────┘
```

## Tech Stack

- **Frontend:** HTML/JavaScript (or React for richer UI)
- **Backend:** Python (Flask/FastAPI) or Node.js (Express)
- **APIs:**
  - Slack Web API
  - Google Calendar API
  - Gmail API
- **Authentication:** OAuth 2.0 for Google, Slack OAuth tokens

## Setup

### Prerequisites

1. **Slack App** with permissions:
   - `users.profile:write` - Update status
   - `dnd:write` - Set do-not-disturb (optional)

2. **Google Cloud Project** with APIs enabled:
   - Google Calendar API
   - Gmail API

3. **OAuth Credentials** for both services

### Installation

```bash
# Install dependencies
pip install -r requirements.txt  # Python
# or
npm install  # Node.js

# Configure environment variables
cp .env.example .env
# Edit .env with your API credentials
```

### Environment Variables

```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_USER_TOKEN=xoxp-your-token
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth/callback
EMAIL_ADDRESS=your.email@company.com
```

## Usage

### 1. Start the Application

```bash
python app.py  # Python
# or
npm start  # Node.js
```

### 2. Fill the Form

- **Leave Start Date:** 2026-04-20
- **Leave End Date:** 2026-04-30
- **OOO Message:** "On vacation in Hawaii 🌴"
- **Emergency Contact:** "Contact Jane Doe at jane@company.com"

### 3. Submit

Click "Set OOO" and the tool will:
1. Update Slack status: "🌴 On vacation until Apr 30"
2. Create Google Calendar event: "Out of Office" (all-day)
3. Update email signature with return date
4. Enable Gmail auto-reply with your message

## API Integrations

### Slack API
- **Endpoint:** `users.profile.set`
- **Updates:** Status text, emoji, expiration time
- **Docs:** https://api.slack.com/methods/users.profile.set

### Google Calendar API
- **Method:** `events.insert`
- **Event Type:** Out of office event
- **Docs:** https://developers.google.com/calendar/api/v3/reference/events

### Gmail API
- **Vacation Settings:** `users.settings.updateVacation`
- **Signature Update:** `users.settings.sendAs.update`
- **Docs:** https://developers.google.com/gmail/api/reference/rest

## Roadmap

- [ ] Basic web form UI
- [ ] Backend API setup
- [ ] Slack integration
- [ ] Google Calendar integration
- [ ] Gmail signature update
- [ ] Gmail auto-reply configuration
- [ ] User authentication
- [ ] Multi-user support
- [ ] Timezone handling
- [ ] Preview before submission
- [ ] Revert OOO settings (when you return)
- [ ] Microsoft Teams integration
- [ ] Outlook calendar integration

## Security

- All API tokens stored in environment variables
- OAuth 2.0 for secure authentication
- No sensitive data logged
- Session management for multi-user deployments

## License

MIT
