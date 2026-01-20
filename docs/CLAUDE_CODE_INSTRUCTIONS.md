# Training Tessa - Claude Code Instructions

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
│  DOCUMENT INGESTION (n8n workflow)                             │
│  SharePoint → Extract Text/Images → Chunk → Embed → Supabase   │
│                                                                 │
│  Q&A FLOW                                                       │
│  Teams → Training Tessa (Flask) → n8n Webhook → Supabase/OpenAI │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
C:\Projects\training-tessa\
├── app.py                  # Flask bot application
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
    ├── CREDENTIALS_REFERENCE.md      # API keys and endpoints (local only, gitignored)
    ├── CREDENTIALS_TEMPLATE.md       # Template for credentials (in git)
    └── synta-prompt-sharepoint-ingestion.md  # n8n workflow prompt (local only, gitignored)
```

---

## CURRENT STATUS (Updated 20 Jan 2026)

### Completed
| Component | Status | Details |
|-----------|--------|---------|
| n8n | ✅ Running | `https://n8n-production-ac1d.up.railway.app` |
| Supabase | ✅ Ready | Project: JimDogBass, pgvector enabled |
| Azure OpenAI | ✅ Configured | Resource: `meraki-training-bot` |
| Embedding Model | ✅ Working | `text-embedding-3-small` |
| Chat Model | ✅ Working | `gpt-4o` |
| Document Table | ✅ Created | `documents` table with metadata column |
| Vector Search Function | ✅ Created | `match_documents` RPC function |
| RAG Document Ingestion | ✅ Published & Working | Production webhook active |
| RAG Question Answering | ✅ Working | Test completed successfully |
| SharePoint App Registration | ✅ Complete | Admin consent granted |
| SharePoint n8n Credential | ✅ Connected | OAuth2 working |
| processed_documents table | ✅ Created | Supabase tracking table |
| SharePoint Ingestion Workflow | ✅ Built | n8n workflow ready, needs credentials + run |
| Training Tessa Flask App | ✅ Deployed | Railway: `web-production-41f7a.up.railway.app` |
| Training Tessa Azure Bot | ✅ Created | App ID: 070c41c0-02fd-44a8-becd-b8c4d33fb029 |
| GitHub Repo | ✅ Created | `https://github.com/JimDogBass/training-tessa` |
| Railway Deployment | ✅ Live | Auto-deploys from GitHub |
| Teams Channel | ✅ Enabled | Microsoft Teams Commercial |
| Teams App | ✅ Installed | Bot available in Teams |

### Test Results
- Successfully ingested test document about Meraki Talent
- Successfully queried: "What is Meraki Talent?"
- Got accurate response based on ingested document

---

## WHERE WE LEFT OFF

### Next Task: Add Credentials & Run Document Ingestion

The Training Tessa bot is deployed and installed in Teams. The SharePoint ingestion workflow has been built.

**Remaining steps:**
1. **Add credentials to workflow nodes** (if not already done)
2. **Run the workflow to ingest all ~50 training documents**
3. **Verify documents appear in Supabase**

**SharePoint Training Docs:**
- Site: merakitalent.sharepoint.com (root site)
- Folder: /Shared Documents/Agent Content/Training
- ~50 docs with images

### SharePoint Ingestion Workflow (n8n)

**Workflow nodes:**
```
Schedule Trigger → Get Processed Files → List SharePoint Files → Filter New Files
→ Download File → File Type Switch → Extract DOCX/PPTX/PDF → Merge Extracted Content
→ Extract Images → Loop Images → GPT-4o Vision → Format Enriched Content
→ Chunk Content → Send to Ingestion Webhook → Record Processed File
```

**What it does:**
1. Lists files in SharePoint training folder
2. Filters out already-processed files
3. Downloads and extracts text from .docx, .pptx, .pdf
4. Extracts images and describes them with GPT-4o Vision
5. Chunks content and sends to ingestion webhook
6. Records processed files to avoid re-processing

---

## Training Tessa Flask App

### Status: ✅ DEPLOYED & LIVE

### Deployment Checklist (All Complete)
- [x] **Create Azure Bot Registration** - `training-tessa` created
- [x] **Push to GitHub** - `https://github.com/JimDogBass/training-tessa`
- [x] **Deploy to Railway** - `https://web-production-41f7a.up.railway.app`
- [x] **Set Environment Variables** - MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD, MICROSOFT_APP_TENANT_ID
- [x] **Update Messaging Endpoint** - `https://web-production-41f7a.up.railway.app/api/messages`
- [x] **Add Teams Icons** - Tessa photo as bot avatar
- [x] **Enable Teams Channel** - Microsoft Teams Commercial
- [x] **Install in Teams** - Bot sideloaded and available

### n8n Integration
Calls existing webhook:
- URL: `https://n8n-production-ac1d.up.railway.app/webhook/ask-question`
- Method: POST
- Body: `{"question": "user's question"}`

---

## Working Production URLs

| Service | URL |
|---------|-----|
| Training Tessa Bot | `https://web-production-41f7a.up.railway.app` |
| Document Ingestion | `https://n8n-production-ac1d.up.railway.app/webhook/ingest-document` |
| Question Answering | `https://n8n-production-ac1d.up.railway.app/webhook/ask-question` |
| n8n Dashboard | `https://n8n-production-ac1d.up.railway.app` |

### Ingestion Request Format
```bash
curl -X POST https://n8n-production-ac1d.up.railway.app/webhook/ingest-document \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document content here", "source_document": "document-name"}'
```

### Question Request Format
```bash
curl -X POST https://n8n-production-ac1d.up.railway.app/webhook/ask-question \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

---

## Code Fixes Applied to n8n Workflows

### 1. RAG Document Ingestion
- Fixed Merge node: Changed to "Append" mode with 2 inputs
- Uses `text` field (not `content`) for document content

### 2. RAG Question Answering - Create Question Embedding Node
```javascript
const question = $input.first().json.question;
const url = 'https://meraki-training-bot.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2025-03-01-preview';
const apiKey = 'YOUR_AZURE_OPENAI_KEY';

const response = await this.helpers.httpRequest({
  method: 'POST',
  url: url,
  headers: {
    'api-key': apiKey,
    'Content-Type': 'application/json'
  },
  body: { input: question }
});

return [{
  json: {
    question: question,
    question_embedding: response.data[0].embedding,
    timestamp: $input.first().json.timestamp
  }
}];
```

### 3. RAG Question Answering - Vector Similarity Search Node
```javascript
const item = $input.first();
const questionEmbedding = item.json.question_embedding;
const SUPABASE_URL = 'https://uwxsflcpaigcygfhxzzl.supabase.co';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
const TOP_K = 5;

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
    match_threshold: 0.7,
    match_count: TOP_K
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

### 4. RAG Question Answering - Generate Answer Node
```javascript
const item = $input.first();
const systemPrompt = item.json.system_prompt;
const userPrompt = item.json.user_prompt;

const AZURE_OPENAI_ENDPOINT = 'https://meraki-training-bot.openai.azure.com';
const AZURE_OPENAI_KEY = 'YOUR_AZURE_OPENAI_KEY';
const DEPLOYMENT_NAME = 'gpt-4o';
const API_VERSION = '2025-03-01-preview';

const response = await this.helpers.httpRequest({
  method: 'POST',
  url: AZURE_OPENAI_ENDPOINT + '/openai/deployments/' + DEPLOYMENT_NAME + '/chat/completions?api-version=' + API_VERSION,
  headers: {
    'api-key': AZURE_OPENAI_KEY,
    'Content-Type': 'application/json'
  },
  body: {
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: 0.7,
    max_tokens: 800,
    top_p: 0.95
  }
});

const answer = response.choices[0].message.content;

return [{
  json: {
    question: item.json.question,
    answer: answer,
    sources: item.json.sources,
    chunk_count: item.json.chunk_count,
    timestamp: new Date().toISOString()
  }
}];
```

### 5. Return Answer Node
- Changed to "Respond With" → "First Incoming Item" (instead of custom JSON)

---

## Supabase SQL Functions Created

### match_documents function
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

## Remaining Tasks

### 1. Add Credentials to Workflow Nodes
The SharePoint ingestion workflow is built. Add credentials to these nodes:
- **List SharePoint Files** - Microsoft SharePoint OAuth2 credential
- **Download File** - Microsoft SharePoint OAuth2 credential
- **GPT-4o Vision** - Azure OpenAI API key
- **Send to Ingestion Webhook** - Already configured (n8n internal)
- **Get Processed Files / Record Processed File** - Supabase credential

### 2. Run Document Ingestion
- Execute the workflow manually or wait for schedule trigger
- ~50 documents to process
- Monitor for errors in n8n execution logs
- Verify documents appear in Supabase `documents` table

### 3. Customizing Bot Responses
To change the bot's tone/style, edit the **"Build RAG Prompt"** node in the Q&A workflow. The system prompt controls personality, length, and response style.

---

## Troubleshooting

### Key fixes discovered during setup:
1. n8n Code nodes use `this.helpers.httpRequest()` not `fetch` or `$request`
2. Azure OpenAI uses `api-key` header (not `Authorization: Bearer`)
3. Azure OpenAI URL format: `https://{resource}.openai.azure.com/openai/deployments/{deployment}/...`
4. Supabase needed `metadata` column added to documents table
5. n8n Merge node should use "Append" mode for optional paths
6. Bot Framework adapter should initialize lazily to allow health checks before env vars are set

### Bot not responding in Teams?
- Check Railway logs for errors
- Verify environment variables are set in Railway
- Confirm messaging endpoint is correct in Azure Bot config
- Test the /health endpoint: `https://web-production-41f7a.up.railway.app/health`
