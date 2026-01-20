# Training Tessa - Meraki Talent Training Bot

A Microsoft Teams bot that answers staff questions using RAG-powered training documents.

## Architecture

```
Staff Question (Teams)
    ↓
Training Tessa (Flask on Railway)
    ↓
n8n Q&A Webhook
    ↓
Supabase Vector Search + Azure OpenAI
    ↓
Answer back to Teams
```

## Status

| Component | Status | Details |
|-----------|--------|---------|
| Flask App | ✅ Created | `C:\Projects\training-tessa` |
| Azure Bot Registration | ⏳ Pending | Need to create in Azure Portal |
| Railway Deployment | ⏳ Pending | Need to deploy |
| Teams App | ⏳ Pending | Need to install after deployment |

## Setup Steps

### 1. Create Azure Bot Registration

1. Go to **Azure Portal** → **Create a resource** → Search **"Azure Bot"**
2. Configure:
   - **Bot handle**: `training-tessa`
   - **Subscription**: Your subscription
   - **Resource group**: `meraki-bot` (or create new)
   - **Pricing tier**: F0 (free)
   - **Type of App**: Single Tenant
   - **Creation type**: Create new Microsoft App ID
3. Click **Create**
4. After creation, go to the bot → **Configuration**:
   - Copy **Microsoft App ID**
   - Click **Manage Password** → **New client secret** → Copy the **Value**
5. Go to **Channels** → Add **Microsoft Teams** channel

### 2. Deploy to Railway

```bash
cd C:\Projects\training-tessa

# Initialize git repo
git init
git add .
git commit -m "Initial Training Tessa bot"

# Create GitHub repo and push
# Then connect to Railway

# Or use Railway CLI:
railway login
railway init
railway up
```

### 3. Set Railway Environment Variables

In Railway dashboard, add these variables:

| Variable | Value |
|----------|-------|
| `MICROSOFT_APP_ID` | From Azure Bot |
| `MICROSOFT_APP_PASSWORD` | From Azure Bot (client secret) |
| `MICROSOFT_APP_TENANT_ID` | `0591f50e-b7a3-41d0-a0b1-b26a2df48dfc` |
| `PORT` | `3978` |

### 4. Update Azure Bot Messaging Endpoint

After Railway deployment:
1. Get Railway URL (e.g., `https://training-tessa-production.up.railway.app`)
2. Go to Azure Portal → Your Bot → **Configuration**
3. Set **Messaging endpoint**: `https://your-railway-url/api/messages`

### 5. Update Teams Manifest

1. Edit `teams-app/manifest.json`
2. Replace `REPLACE_WITH_BOT_APP_ID` with your Microsoft App ID (2 places)
3. Add icons:
   - `color.png` (192x192 pixels)
   - `outline.png` (32x32 pixels, transparent background)
4. Zip the contents: `manifest.json`, `color.png`, `outline.png`

### 6. Install in Teams

**Option A: Sideload (for testing)**
1. Teams → Apps → Manage your apps → Upload a custom app
2. Upload the zip file

**Option B: Admin deployment (for org-wide)**
1. Teams Admin Center → Manage apps → Upload new app
2. Upload zip, approve, assign to users

## Files

```
training-tessa/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway/Heroku start command
├── railway.toml       # Railway configuration
├── README.md          # This file
└── teams-app/
    ├── manifest.json  # Teams app manifest
    ├── color.png      # Bot icon (192x192) - ADD THIS
    └── outline.png    # Bot icon (32x32) - ADD THIS
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MICROSOFT_APP_ID` | Azure Bot App ID |
| `MICROSOFT_APP_PASSWORD` | Azure Bot Client Secret |
| `MICROSOFT_APP_TENANT_ID` | Azure AD Tenant ID |
| `PORT` | Server port (default: 3978) |

## n8n Integration

The bot calls the existing n8n Q&A webhook:
- **URL**: `https://n8n-production-ac1d.up.railway.app/webhook/ask-question`
- **Method**: POST
- **Body**: `{"question": "user's question"}`
- **Response**: `{"answer": "...", "sources": [...], "chunk_count": N}`

## Testing

### Local Testing (optional)
```bash
pip install -r requirements.txt
export MICROSOFT_APP_ID=your_app_id
export MICROSOFT_APP_PASSWORD=your_password
export MICROSOFT_APP_TENANT_ID=your_tenant_id
python app.py
```

Use Bot Framework Emulator to test locally.

### Production Testing
1. Deploy to Railway
2. Install in Teams
3. Send a message to Training Tessa
4. Verify answer comes from training documents

## Troubleshooting

### Bot not responding
- Check Railway logs for errors
- Verify environment variables are set
- Check Azure Bot messaging endpoint is correct

### "Unable to reach bot"
- Messaging endpoint must be HTTPS
- Railway URL must be correct in Azure Bot config
- Check bot is running (hit /health endpoint)

### Wrong answers
- Check n8n Q&A workflow is working
- Verify documents are ingested in Supabase
- Test webhook directly with curl

## Documentation

All project documentation is in the `docs/` folder:

| File | Purpose |
|------|---------|
| `CLAUDE_CODE_INSTRUCTIONS.md` | Full project status, architecture, where we left off |
| `CREDENTIALS_REFERENCE.md` | All API keys, endpoints, credentials |
| `synta-prompt-sharepoint-ingestion.md` | Synta prompt for SharePoint workflow |

## Related Projects

- **n8n Workflows**: `https://n8n-production-ac1d.up.railway.app`
- **Supabase**: Training documents stored in `documents` table
- **Jimmy Content Bot**: Similar architecture, different purpose
