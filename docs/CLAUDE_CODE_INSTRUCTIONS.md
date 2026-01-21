# Training Tessa - Claude Code Instructions

**Last Updated:** 21 January 2026

## Project Overview

RAG-powered training bot for Meraki Talent staff. Users ask questions in Teams, the bot searches training documents in Supabase, and returns AI-generated answers.

**Project Location:** `C:\Projects\training-tessa`
**GitHub:** `https://github.com/JimDogBass/training-tessa`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING TESSA SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DOCUMENT INGESTION (Python script)                            │
│  Local Files → Extract Text → n8n Webhook → Chunk → Embed →   │
│  Supabase                                                       │
│                                                                 │
│  Q&A FLOW                                                       │
│  Teams → Training Tessa (Flask) → n8n Webhook →                │
│  Supabase/OpenAI → Answer                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
C:\Projects\training-tessa\
├── app.py                  # Flask bot application
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
    ├── CREDENTIALS_REFERENCE.md      # API keys and endpoints
    ├── CREDENTIALS_TEMPLATE.md       # Template for credentials
    ├── HOW_TO_ADD_DOCUMENTS.md       # Document ingestion guide
    └── synta-prompt-sharepoint-ingestion.md  # (archived)
```

---

## CURRENT STATUS: LIVE

### All Components Working

| Component | Status | Details |
|-----------|--------|---------|
| n8n | Running | `https://n8n-production-ac1d.up.railway.app` |
| Supabase | Ready | 631 document chunks ingested |
| Azure OpenAI | Working | gpt-4o + text-embedding-3-small |
| Training Tessa Flask App | Deployed | `https://web-production-41f7a.up.railway.app` |
| Azure Bot Registration | Created | App ID: 070c41c0-02fd-44a8-becd-b8c4d33fb029 |
| Teams App | Installed | Bot available in Teams |
| Document Ingestion | Working | Via Python script |
| RAG Q&A | Working | Vector search + GPT-4o answers |

### Documents Ingested
- 35 training documents successfully ingested
- 631 text chunks with embeddings in Supabase
- 4 files skipped (image-based PDFs with no extractable text)

---

## Working Production URLs

| Service | URL |
|---------|-----|
| Training Tessa Bot | `https://web-production-41f7a.up.railway.app` |
| Bot Health Check | `https://web-production-41f7a.up.railway.app/health` |
| Document Ingestion | `https://n8n-production-ac1d.up.railway.app/webhook/ingest-document` |
| Question Answering | `https://n8n-production-ac1d.up.railway.app/webhook/ask-question` |
| n8n Dashboard | `https://n8n-production-ac1d.up.railway.app` |

---

## How to Add New Documents

**See:** `docs/HOW_TO_ADD_DOCUMENTS.md`

Quick version:
1. Add files to `C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training`
2. Run `python ingest_local_files.py` from the project folder
3. Documents will be processed and added to Supabase

---

## n8n Workflow Details

### RAG Document Ingestion Workflow
Receives documents via webhook, chunks them, creates embeddings, stores in Supabase.

**Webhook:** POST to `/webhook/ingest-document`
```json
{
  "text": "Document content here",
  "source_document": "filename.docx"
}
```

### RAG Question Answering Workflow
Receives questions, searches similar documents, generates AI answer.

**Webhook:** POST to `/webhook/ask-question`
```json
{
  "question": "User's question here"
}
```

**Response:**
```json
{
  "question": "...",
  "answer": "AI-generated answer",
  "sources": ["document1.docx", "document2.pdf"],
  "chunk_count": 5
}
```

### Key n8n Node Configurations

#### Vector Similarity Search Node
```javascript
const item = $input.first();
const questionEmbedding = item.json.question_embedding;
const SUPABASE_URL = 'https://uwxsflcpaigcygfhxzzl.supabase.co';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';

const embeddingStr = '[' + questionEmbedding.join(',') + ']';

const response = await this.helpers.httpRequest({
  method: 'POST',
  url: SUPABASE_URL + '/rest/v1/rpc/match_documents',
  headers: {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json'
  },
  body: {
    query_embedding: embeddingStr,
    match_threshold: 0.1,
    match_count: 5
  }
});

return [{
  json: {
    question: item.json.question,
    retrieved_chunks: response,
    chunk_count: response.length,
    timestamp: item.json.timestamp
  }
}];
```

**Important:** The embedding must be passed as a string `'[0.1,0.2,...]'` not an array.

---

## Supabase Configuration

### Documents Table
```sql
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  embedding VECTOR(1536),
  source_document TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### match_documents Function
```sql
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
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

### Q&A returns "I don't have that information"
1. Check if `chunk_count > 0` in webhook response
2. If 0, vector search isn't finding matches - lower `match_threshold`
3. If > 0, adjust the system prompt in Build RAG Prompt node

### Vector search returns 0 chunks
1. Verify documents are in Supabase
2. Check embedding format is string `'[...]'` not array
3. Lower match_threshold to 0.1 or lower

### Document ingestion fails
1. Check n8n execution logs
2. Verify Azure OpenAI API key is valid
3. Check Supabase connection

---

## Key Fixes Applied

1. **BotFrameworkAdapterSettings** - Removed invalid `app_tenantid` parameter
2. **Vector search embedding format** - Must be string `'[...]'` for Supabase RPC
3. **match_threshold** - Lowered to 0.1 for better matching
4. **System prompt** - Made less strict to give helpful answers

---

## Files NOT in Git (gitignored)

- `docs/CREDENTIALS_REFERENCE.md` - Contains API keys
- `docs/synta-prompt-sharepoint-ingestion.md` - Archived
- `.env` - Environment variables
- `__pycache__/` - Python cache
