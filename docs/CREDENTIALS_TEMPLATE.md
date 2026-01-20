# Training Tessa - Credentials Template

This file lists the credentials and environment variables needed for the project.
**Actual values are stored locally in CREDENTIALS_REFERENCE.md (not in git).**

## n8n Instance

- **URL**: https://n8n-production-ac1d.up.railway.app
- **Hosted on**: Railway

## Supabase

- **Project URL**: `https://[PROJECT_ID].supabase.co`
- **Table**: documents (with columns: id, content, embedding, source_document, metadata, created_at)
- **Anon Key**: `[SUPABASE_ANON_KEY]`

## Azure OpenAI

- **Resource Name**: meraki-training-bot
- **Endpoint**: `https://meraki-training-bot.openai.azure.com/`
- **Region**: uksouth
- **API Version**: 2025-03-01-preview
- **API Key**: `[AZURE_OPENAI_KEY]`

### Deployments

| Model | Deployment Name | Purpose |
|-------|-----------------|---------|
| gpt-4o | gpt-4o | Chat/answers |
| text-embedding-3-small | text-embedding-3-small | Document embeddings |

## Webhook URLs

### Production URLs (ACTIVE)
- **Ingest**: https://n8n-production-ac1d.up.railway.app/webhook/ingest-document
- **Question**: https://n8n-production-ac1d.up.railway.app/webhook/ask-question

## SharePoint Integration

### Azure App Registration
- **App Name**: n8n-sharepoint-integration
- **Client ID**: `[SHAREPOINT_CLIENT_ID]`
- **Tenant ID**: `[TENANT_ID]`
- **Client Secret**: `[SHAREPOINT_CLIENT_SECRET]`
- **Permissions**: Files.Read.All, Sites.Read.All, User.Read

### SharePoint Training Docs Location
- **Site**: merakitalent.sharepoint.com (root site)
- **Folder Path**: /Shared Documents/Agent Content/Training
- **Document Count**: ~50 files
- **File Types**: .docx, .pptx, .pdf, .doc, .ppt (with images)

## Training Tessa Azure Bot

- **Bot Name**: training-tessa
- **Microsoft App ID**: `[MICROSOFT_APP_ID]`
- **Tenant ID**: `[MICROSOFT_APP_TENANT_ID]`
- **Client Secret**: `[MICROSOFT_APP_PASSWORD]`
- **Bot Type**: Single Tenant
- **Messaging Endpoint**: `https://[RAILWAY_URL]/api/messages`

### Railway Environment Variables

```
MICROSOFT_APP_ID=[your-app-id]
MICROSOFT_APP_PASSWORD=[your-client-secret]
MICROSOFT_APP_TENANT_ID=[your-tenant-id]
```

---

## Setting Up Credentials

1. Copy `CREDENTIALS_TEMPLATE.md` to `CREDENTIALS_REFERENCE.md`
2. Fill in the actual values
3. `CREDENTIALS_REFERENCE.md` is gitignored and won't be pushed
