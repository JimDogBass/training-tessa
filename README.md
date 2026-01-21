# Training Tessa - Meraki Talent Training Bot

A Microsoft Teams bot that answers staff questions using RAG-powered training documents.

## Status: LIVE

| Component | Status |
|-----------|--------|
| Flask Bot App | Running on Railway |
| n8n Workflows | Active |
| Supabase Vector DB | 631 document chunks |
| Azure OpenAI | gpt-4o + embeddings |
| Teams Integration | Installed |

## Architecture

```
Staff Question (Teams)
    |
Training Tessa (Flask on Railway)
    |
n8n Q&A Webhook
    |
Supabase Vector Search + Azure OpenAI
    |
Answer back to Teams
```

## Quick Links

| Service | URL |
|---------|-----|
| Bot Health | https://web-production-41f7a.up.railway.app/health |
| n8n Dashboard | https://n8n-production-ac1d.up.railway.app |
| GitHub Repo | https://github.com/JimDogBass/training-tessa |

## Adding New Training Documents

See [docs/HOW_TO_ADD_DOCUMENTS.md](docs/HOW_TO_ADD_DOCUMENTS.md) for instructions.

**Quick version:**
1. Add files to `C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training`
2. Run `python ingest_local_files.py`

## Project Structure

```
training-tessa/
├── app.py                  # Flask bot application
├── ingest_local_files.py   # Script to ingest training documents
├── requirements.txt        # Python dependencies
├── Procfile               # Railway start command
├── railway.toml           # Railway configuration
├── README.md              # This file
├── teams-app/
│   ├── manifest.json      # Teams app manifest
│   ├── color.png          # Bot icon (192x192)
│   ├── outline.png        # Bot icon (32x32)
│   └── training-tessa.zip # Ready-to-install Teams app
└── docs/
    ├── CLAUDE_CODE_INSTRUCTIONS.md   # Project documentation
    ├── CREDENTIALS_REFERENCE.md      # API keys and endpoints
    ├── CREDENTIALS_TEMPLATE.md       # Template for credentials
    └── HOW_TO_ADD_DOCUMENTS.md       # Document ingestion guide
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MICROSOFT_APP_ID` | Azure Bot App ID |
| `MICROSOFT_APP_PASSWORD` | Azure Bot Client Secret |
| `PORT` | Server port (default: 3978) |

## n8n Workflows

### RAG Document Ingestion
- **Webhook**: POST to `/webhook/ingest-document`
- **Body**: `{"text": "content", "source_document": "filename"}`
- **Process**: Chunks text, creates embeddings, stores in Supabase

### RAG Question Answering
- **Webhook**: POST to `/webhook/ask-question`
- **Body**: `{"question": "user's question"}`
- **Process**: Creates embedding, vector search, GPT-4o generates answer

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Use Bot Framework Emulator to test locally.

## Troubleshooting

### Bot not responding in Teams
1. Check Railway logs for errors
2. Verify health endpoint: https://web-production-41f7a.up.railway.app/health
3. Check Azure Bot messaging endpoint is correct

### Wrong or no answers
1. Check n8n Q&A workflow execution logs
2. Verify documents are in Supabase
3. Test webhook directly with curl

### Adding new documents
1. Run the ingestion script
2. Check n8n logs for any errors
3. Verify documents appear in Supabase

## Documentation

| File | Purpose |
|------|---------|
| `docs/CLAUDE_CODE_INSTRUCTIONS.md` | Full project documentation |
| `docs/CREDENTIALS_REFERENCE.md` | All API keys and endpoints |
| `docs/HOW_TO_ADD_DOCUMENTS.md` | How to add new training docs |
