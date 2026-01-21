# How to Add New Training Documents

This guide explains how to add new training documents to Training Tessa's knowledge base.

## Quick Start

1. Add your files to the Training folder
2. Run the ingestion script
3. Done!

---

## Step-by-Step Instructions

### Step 1: Add Files to the Training Folder

Copy your training documents to:
```
C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training
```

**Supported file types:**
- `.docx` - Word documents
- `.pptx` - PowerPoint presentations
- `.pdf` - PDF documents (text-based, not scanned images)
- `.doc` - Legacy Word documents
- `.ppt` - Legacy PowerPoint
- `.odt` - OpenDocument text
- `.txt` - Plain text files

### Step 2: Run the Ingestion Script

Open a command prompt and run:

```bash
cd C:\Projects\training-tessa
python ingest_local_files.py
```

### Step 3: Wait for Processing

The script will:
1. Read each file
2. Extract text content
3. Send to n8n for chunking and embedding
4. Store in Supabase

You'll see output like:
```
[1/5] Processing: New Training Guide.docx
  Extracted 5432 characters
  [OK] Sent to webhook successfully
```

### Step 4: Verify

Ask Training Tessa a question about the new content to verify it's working.

---

## Important Notes

### File Names
- Use descriptive file names (they appear in source citations)
- Avoid special characters in file names

### File Content
- Text-based PDFs work best
- Scanned/image PDFs won't be extracted (no OCR)
- PowerPoint slides are extracted slide-by-slide
- Images in documents are NOT processed (text only)

### Duplicate Handling
- The script will re-process ALL files in the folder
- Duplicates may be created in Supabase
- For now, this is acceptable (search still works)

---

## Troubleshooting

### "No text extracted" message
- The file might be an image-based PDF
- The file might be corrupted
- Try opening the file to verify it has text content

### Script fails with connection error
- Check your internet connection
- Verify n8n is running: https://n8n-production-ac1d.up.railway.app/health

### Documents not appearing in Tessa's answers
- Wait a few seconds after ingestion
- Try asking a question with specific keywords from the document
- Check n8n execution logs for errors

---

## Alternative: Manual Ingestion

For a single document, you can use curl:

```bash
curl -X POST https://n8n-production-ac1d.up.railway.app/webhook/ingest-document \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document content here", "source_document": "Document Name.docx"}'
```

---

## Checking What's Been Ingested

### Count documents in Supabase:
```bash
curl -s "https://uwxsflcpaigcygfhxzzl.supabase.co/rest/v1/documents?select=count" \
  -H "apikey: YOUR_SUPABASE_KEY" \
  -H "Prefer: count=exact"
```

### View recent documents:
```bash
curl -s "https://uwxsflcpaigcygfhxzzl.supabase.co/rest/v1/documents?select=id,source_document,created_at&order=created_at.desc&limit=10" \
  -H "apikey: YOUR_SUPABASE_KEY"
```

---

## Future Improvements

Planned enhancements:
- [ ] Track processed files to avoid duplicates
- [ ] Add OCR for image-based PDFs
- [ ] Extract and describe images with GPT-4 Vision
- [ ] Scheduled automatic ingestion of new files
