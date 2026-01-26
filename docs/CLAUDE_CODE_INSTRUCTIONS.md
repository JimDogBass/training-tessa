# Training Tessa - Claude Code Instructions

**Last Updated:** 26 January 2026

## Project Overview

RAG-powered training bot for Meraki Talent staff. Users ask questions in Teams, the bot searches training documents in Supabase, and returns AI-generated answers with source citations.

**Project Location:** `C:\Projects\training-tessa`
**GitHub:** `https://github.com/JimDogBass/training-tessa`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING TESSA SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DOCUMENT INGESTION (Python script - direct to Supabase)       │
│  Local Files → Extract Text & Images → Gemini 2.5 Flash        │
│  describes images → Chunk (1000 chars/200 overlap) → Gemini    │
│  text-embedding-004 → Direct insert to Supabase (768-dim)      │
│                                                                 │
│  Q&A FLOW (Built into Flask app - no n8n)                      │
│  Teams → Training Tessa (Flask) → Gemini embedding →           │
│  Supabase Vector Search → Gemini 2.5 Pro → Answer with sources │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
C:\Projects\training-tessa\
├── app.py                  # Flask bot application with built-in Q&A
├── ingest_local_files.py   # Python script to ingest training docs
├── requirements.txt        # Python dependencies
├── Procfile               # Railway start command
├── railway.toml           # Railway configuration
├── README.md              # Setup instructions
├── .gitignore             # Excludes credentials from git
├── teams-app/
│   ├── manifest.json      # Teams app manifest
│   ├── color.png          # Bot icon (192x192) - Tessa photo
│   ├── outline.png        # Bot icon (32x32)
│   └── training-tessa.zip # Ready-to-install Teams app package
└── docs/
    ├── CLAUDE_CODE_INSTRUCTIONS.md   # This file
    ├── CREDENTIALS_REFERENCE.md      # API keys and endpoints (gitignored)
    ├── CREDENTIALS_TEMPLATE.md       # Template for credentials
    └── HOW_TO_ADD_DOCUMENTS.md       # Document ingestion guide
```

---

## CURRENT STATUS: LIVE

### All Components Working

| Component | Status | Details |
|-----------|--------|---------|
| Flask Bot App | Deployed | `https://web-production-41f7a.up.railway.app` |
| Supabase | Ready | Vector DB with pgvector (768 dimensions) |
| Google Gemini | Working | gemini-2.5-pro + text-embedding-004 |
| Azure Bot Registration | Created | App ID: 070c41c0-02fd-44a8-becd-b8c4d33fb029 |
| Teams App | Installed | Bot available in Teams |
| Document Ingestion | Working | Python script → direct to Supabase |
| Image Processing | Working | Gemini 2.5 Flash describes images |
| RAG Q&A | Working | Vector search + Gemini 2.5 Pro answers + source citations |

### AI Models Used

| Model | Purpose |
|-------|---------|
| gemini-2.5-pro | Answer generation (in app.py) |
| gemini-2.5-flash | Image descriptions (in ingestion script) |
| text-embedding-004 | Embeddings for documents and queries (768 dimensions) |

---

## Working Production URLs

| Service | URL |
|---------|-----|
| Training Tessa Bot | `https://web-production-41f7a.up.railway.app` |
| Bot Health Check | `https://web-production-41f7a.up.railway.app/health` |
| Bot Messages Endpoint | `https://web-production-41f7a.up.railway.app/api/messages` |

---

## How to Add New Documents

**See:** `docs/HOW_TO_ADD_DOCUMENTS.md`

Quick version:
1. Add files to `C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training`
2. Set environment variables: `GEMINI_API_KEY`, `SUPABASE_KEY`
3. Run `py ingest_local_files.py` from the project folder
4. Answer prompts (clear existing? process images?)
5. Documents will be chunked, embedded, and stored directly in Supabase

---

## Customizing Tessa's Personality

Edit `TESSA_SYSTEM_PROMPT` in `app.py` (around line 57) to change:
- Tone and personality
- How she communicates
- Response format
- How she handles questions

The prompt is fully customizable - just edit the text and redeploy.

---

## Environment Variables

### Railway (Production)

| Variable | Purpose |
|----------|---------|
| `MICROSOFT_APP_ID` | Azure Bot App ID |
| `MICROSOFT_APP_PASSWORD` | Azure Bot Client Secret |
| `MICROSOFT_APP_TENANT_ID` | Azure Bot Tenant ID |
| `GEMINI_API_KEY` | Google Gemini API key |
| `SUPABASE_KEY` | Supabase anon key |

### Local (for ingestion script)

```cmd
set GEMINI_API_KEY=your-key
set SUPABASE_KEY=your-key
```

---

## Supabase Configuration

### Documents Table
```sql
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  embedding VECTOR(768),
  source_document TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### match_documents Function
```sql
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  content text,
  source_document text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.content,
    d.source_document,
    1 - (d.embedding <=> query_embedding) AS similarity
  FROM documents d
  WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

---

## Troubleshooting

### Bot not responding in Teams
1. Check Railway logs: `https://railway.app` → training-tessa → Deployments → Logs
2. Verify health: `curl https://web-production-41f7a.up.railway.app/health`
3. Check Azure Bot messaging endpoint is `https://web-production-41f7a.up.railway.app/api/messages`

### Q&A returns no answer or errors
1. Check Railway logs for error messages
2. Verify GEMINI_API_KEY is set correctly in Railway
3. Verify SUPABASE_KEY is set correctly in Railway

### Vector search returns 0 chunks
1. Verify documents are in Supabase with 768-dimension embeddings
2. Lower match_threshold if needed (currently 0.1)
3. Re-run ingestion if embeddings were created with wrong model

### Document ingestion fails
1. Check GEMINI_API_KEY is set in terminal
2. Check SUPABASE_KEY is set in terminal
3. Verify internet connection

---

## Changing Endpoints

### If Railway URL changes:
1. Get new URL from Railway dashboard
2. Update Azure Bot: Azure Portal → Bot Services → your bot → Configuration → Messaging endpoint
3. Set to: `https://NEW-URL/api/messages`

### To use custom domain:
1. Railway → Settings → Networking → Custom Domain
2. Add DNS CNAME record
3. Update Azure Bot messaging endpoint

---

## Files NOT in Git (gitignored)

- `docs/CREDENTIALS_REFERENCE.md` - Contains actual API keys
- `.env` - Environment variables
- `__pycache__/` - Python cache
