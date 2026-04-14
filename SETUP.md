## Setup Guide for OOO Consolidator

Follow these steps to get your OOO Consolidator up and running.

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up Slack Integration

#### Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "OOO Consolidator" and select your workspace
4. Navigate to "OAuth & Permissions"
5. Add these **User Token Scopes**:
   - `users.profile:write` - Update your profile
   - `users.profile:read` - Read profile info
6. Install the app to your workspace
7. Copy the **User OAuth Token** (starts with `xoxp-`)

#### Get Your Slack User ID

1. In Slack, click on your profile → "Profile"
2. Click "More" → "Copy member ID"
3. Save this ID

### 3. Set Up Google/Gmail Integration

#### Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g., "OOO Consolidator")
3. Enable these APIs:
   - Google Calendar API
   - Gmail API

#### Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name it "OOO Consolidator"
5. Download the JSON file
6. Rename it to `credentials.json` and place in project root

#### First-time OAuth Flow

The first time you run the app and use Google features, you'll need to:
1. A browser window will open
2. Log in with your Google account
3. Grant permissions for Calendar and Gmail
4. A `token.json` file will be created automatically

### 4. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Required values:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_TOKEN=xoxp-your-user-token
SLACK_USER_ID=U01234567

GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/google/callback

EMAIL_ADDRESS=your.email@company.com

SECRET_KEY=generate-a-random-secret-key
TIMEZONE=America/Los_Angeles
```

### 5. Run the Application

```bash
# Run with Python
python main.py

# Or with uvicorn directly
uvicorn app.main:app --reload
```

The app will be available at: http://localhost:8000

### 6. Test the Integration

1. Open http://localhost:8000 in your browser
2. Fill out the OOO form
3. Submit and check:
   - Your Slack status
   - Your Google Calendar
   - Your Gmail settings

### 7. API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Slack Token Issues
- Make sure you're using the **User Token** (xoxp-), not Bot Token
- Verify the token has `users.profile:write` scope
- Token must be from the user whose status you want to update

### Google OAuth Issues
- Ensure `credentials.json` is in the project root
- Check that Calendar and Gmail APIs are enabled
- Verify redirect URI matches in Google Console and .env

### Permission Errors
- Delete `token.json` and re-authenticate
- Check API scopes in Google Console
- Ensure your Google Workspace allows these API calls

## Security Notes

- Never commit `.env` or `token.json` to git
- Use environment-specific credentials for production
- Consider using a secrets manager (AWS Secrets Manager, etc.)
- Rotate tokens regularly
- Use HTTPS in production

## Production Deployment

For production use:

1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server (Gunicorn, etc.)
3. Set up SSL/TLS certificates
4. Use a reverse proxy (nginx, Caddy)
5. Implement proper logging and monitoring
6. Store secrets in a secure vault

Example with Gunicorn:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
