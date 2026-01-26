# Training Tessa - Meraki Talent Training Bot

A Microsoft Teams bot that answers staff questions using RAG-powered training documents.

## Status: LIVE

| Component | Status |
|-----------|--------|
| Flask Bot App | Running on Railway |
| Supabase Vector DB | Document chunks with 768-dim embeddings |
| Google Gemini | gemini-2.5-pro (answers) + text-embedding-004 (embeddings) |
| Teams Integration | Installed |
| Image Processing | Gemini 2.5 Flash Vision |

## Features

- **RAG-powered answers** - Searches training documents and generates AI answers
- **Source citations** - Shows which documents the answer came from
- **Image understanding** - Extracts and describes images from Word/PowerPoint docs
- **Smart chunking** - Splits documents with overlap for better context
- **Customizable personality** - Edit TESSA_SYSTEM_PROMPT in app.py

## Architecture

```
Staff Question (Teams)
    ↓
Training Tessa (Flask on Railway)
    ↓
Gemini text-embedding-004 creates question embedding
    ↓
Supabase Vector Search (768 dimensions)
    ↓
Gemini 2.5 Pro generates answer with context
    ↓
Answer with sources back to Teams
```

```
Document Ingestion (Local Python Script)
    ↓
Extract text + images from files
    ↓
Gemini 2.5 Flash describes images
    ↓
Chunk text (1000 chars, 200 overlap)
    ↓
Gemini text-embedding-004 creates embeddings
    ↓
Store in Supabase with source_document
```

## Quick Links

| Service | URL |
|---------|-----|
| Bot Health | https://web-production-41f7a.up.railway.app/health |
| GitHub Repo | https://github.com/JimDogBass/training-tessa |

## Adding New Training Documents

See [docs/HOW_TO_ADD_DOCUMENTS.md](docs/HOW_TO_ADD_DOCUMENTS.md) for full instructions.

**Quick version:**
1. Add files to `C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training`
2. Set environment variables (GEMINI_API_KEY, SUPABASE_KEY)
3. Run `python ingest_local_files.py`
4. Answer `y` to clear existing docs (optional) and process images

## Project Structure

```
training-tessa/
├── app.py                  # Flask bot application (includes Q&A logic)
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
    ├── CREDENTIALS_REFERENCE.md      # API keys and endpoints (gitignored)
    ├── CREDENTIALS_TEMPLATE.md       # Template for credentials
    └── HOW_TO_ADD_DOCUMENTS.md       # Document ingestion guide
```

## Environment Variables (Railway)

| Variable | Description |
|----------|-------------|
| `MICROSOFT_APP_ID` | Azure Bot App ID |
| `MICROSOFT_APP_PASSWORD` | Azure Bot Client Secret |
| `MICROSOFT_APP_TENANT_ID` | Azure Bot Tenant ID |
| `GEMINI_API_KEY` | Google Gemini API key |
| `SUPABASE_KEY` | Supabase anon key |

## Local Development

```bash
pip install -r requirements.txt
set GEMINI_API_KEY=your-key
set SUPABASE_KEY=your-key
python app.py
```

Use Bot Framework Emulator to test locally.

## Customizing Tessa's Personality

Edit the `TESSA_SYSTEM_PROMPT` variable in `app.py` (around line 57) to change how Tessa communicates:
- Tone and personality
- Response format
- How she handles questions
- Communication style

## Troubleshooting

### Bot not responding in Teams
1. Check Railway logs for errors
2. Verify health endpoint: https://web-production-41f7a.up.railway.app/health
3. Check Azure Bot messaging endpoint is correct

### Wrong or no answers
1. Check Railway deployment logs
2. Verify documents are in Supabase (should have 768-dim embeddings)
3. Test health endpoint

### Adding new documents
1. Set environment variables
2. Run the ingestion script
3. Verify documents appear in Supabase

## Documentation

| File | Purpose |
|------|---------|
| `docs/CLAUDE_CODE_INSTRUCTIONS.md` | Full project documentation |
| `docs/CREDENTIALS_REFERENCE.md` | All API keys and endpoints |
| `docs/HOW_TO_ADD_DOCUMENTS.md` | How to add new training docs |
