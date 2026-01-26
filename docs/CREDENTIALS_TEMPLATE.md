# Training Tessa - Credentials Template

This file lists the credentials and environment variables needed for the project.
**Actual values are stored locally in CREDENTIALS_REFERENCE.md (not in git).**

## Google Gemini API

- **API Key**: `[GEMINI_API_KEY]`
- **Get one at**: https://aistudio.google.com/apikey

### Models Used

| Model | Purpose |
|-------|---------|
| gemini-2.5-pro | Answer generation |
| gemini-2.5-flash | Image descriptions (ingestion) |
| text-embedding-004 | Document/query embeddings (768 dimensions) |

## Supabase

- **Project URL**: `https://uwxsflcpaigcygfhxzzl.supabase.co`
- **Table**: documents (columns: id, content, embedding vector(768), source_document, metadata, created_at)
- **Anon Key**: `[SUPABASE_KEY]`

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
```

## Training Tessa Azure Bot

- **Bot Name**: training-tessa
- **Microsoft App ID**: `[MICROSOFT_APP_ID]`
- **Tenant ID**: `[MICROSOFT_APP_TENANT_ID]`
- **Client Secret**: `[MICROSOFT_APP_PASSWORD]`
- **Bot Type**: Single Tenant
- **Messaging Endpoint**: `https://web-production-41f7a.up.railway.app/api/messages`

## Railway Environment Variables

```
MICROSOFT_APP_ID=[your-app-id]
MICROSOFT_APP_PASSWORD=[your-client-secret]
MICROSOFT_APP_TENANT_ID=[your-tenant-id]
GEMINI_API_KEY=[your-gemini-key]
SUPABASE_KEY=[your-supabase-key]
```

## Local Environment Variables (for ingestion script)

```cmd
set GEMINI_API_KEY=[your-gemini-key]
set SUPABASE_KEY=[your-supabase-key]
```

## Quick Links

| Service | URL |
|---------|-----|
| Bot Health | https://web-production-41f7a.up.railway.app/health |
| Railway Dashboard | https://railway.app |
| Supabase Dashboard | https://supabase.com/dashboard |
| Google AI Studio | https://aistudio.google.com |
| GitHub Repo | https://github.com/JimDogBass/training-tessa |

---

## Setting Up Credentials

1. Copy `CREDENTIALS_TEMPLATE.md` to `CREDENTIALS_REFERENCE.md`
2. Fill in the actual values
3. `CREDENTIALS_REFERENCE.md` is gitignored and won't be pushed
