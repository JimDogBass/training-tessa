# How to Add New Training Documents

This guide explains how to add new training documents to Training Tessa's knowledge base.

## Quick Start

1. Add your files to the Training folder
2. Set environment variables
3. Run the ingestion script
4. Done!

---

## Step-by-Step Instructions

### Step 1: Add Files to the Training Folder

Copy your training documents to:
```
C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training
```

**Supported file types:**
- `.docx` - Word documents (text + images)
- `.pptx` - PowerPoint presentations (text + images)
- `.pdf` - PDF documents (text-based, not scanned images)
- `.doc` - Legacy Word documents
- `.ppt` - Legacy PowerPoint
- `.odt` / `.odp` - OpenDocument files
- `.txt` - Plain text files

### Step 2: Set Environment Variables

Open Command Prompt and run:

```cmd
set GEMINI_API_KEY=your-gemini-api-key
set SUPABASE_KEY=your-supabase-key
```

### Step 3: Run the Ingestion Script

```cmd
cd C:\Projects\training-tessa
py ingest_local_files.py
```

### Step 4: Answer the Prompts

The script will ask:
1. **Clear existing documents?** - Answer `y` to remove all old documents and start fresh, or `n` to add to existing
2. **Process images with Gemini Vision?** - Answer `y` to extract and describe images from documents (slower but more complete)

### Step 5: Wait for Processing

The script will:
1. Read each file and extract text content
2. Extract images from Word and PowerPoint files
3. Describe images using Gemini 2.5 Flash Vision (if enabled)
4. Split text into overlapping chunks (1000 chars with 200 overlap)
5. Create embeddings using Gemini text-embedding-004
6. Store directly in Supabase with source document name

You'll see output like:
```
[1/5] Processing: New Training Guide.docx
  Extracted 5432 characters, 3 images
  Processing 3 images with Gemini Vision...
    Image 1 described
    Image 2 described
    Image 3 described
  Split into 8 chunks
  [OK] Stored 8/8 chunks
```

**Note:** The script has retry logic (3 attempts with 5s delay) for network errors.

### Step 6: Verify

Ask Training Tessa a question about the new content. The answer should now include **source citations** showing which documents the information came from.

---

## Important Notes

### File Names
- Use descriptive file names (they appear in source citations)
- Avoid special characters in file names
- The filename becomes the `source_document` field in Supabase

### Image Processing
- Images are extracted from `.docx` and `.pptx` files
- Gemini 2.5 Flash describes each image's content
- Image descriptions are included in the document chunks
- Limited to 5 images per document to manage API costs

### File Content
- Text-based PDFs work best
- Scanned/image PDFs won't be extracted (no OCR yet)
- PowerPoint slides are extracted slide-by-slide

### Chunking
- Text is split into ~1000 character chunks
- 200 character overlap ensures context isn't lost at boundaries
- Chunks break at natural points (paragraphs, sentences)

### Embeddings
- Uses Gemini text-embedding-004 model
- Produces 768-dimensional vectors
- Stored in Supabase with pgvector

---

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"
- Make sure you ran the `set GEMINI_API_KEY=...` command in the same terminal
- Environment variables don't persist between terminal sessions

### "No text extracted" message
- The file might be an image-based/scanned PDF
- The file might be corrupted
- Try opening the file to verify it has text content

### Script fails with connection/timeout error
- Check your internet connection
- The script will automatically retry up to 3 times
- If it keeps failing, wait a few minutes and try again

### Documents not appearing in Tessa's answers
- Wait a few seconds after ingestion
- Try asking a question with specific keywords from the document
- Check Supabase to verify documents were stored

---

## Checking What's Been Ingested

### View recent documents in Supabase:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "Table Editor" → "documents"
4. Sort by `created_at` descending

---

## Current Ingestion Status

As of 27 January 2026:
- **35 of 39 files** processed successfully
- **~1,400+ chunks** stored in Supabase

### Skipped Files (need OCR)

These files were skipped because they are image-based/scanned:
- Exec Search Presentation.pdf
- Retainer Training Final.odp
- Strategic Leadership Course - Day 1.pdf
- Strategic Leadership Course - Day 2.pdf

---

## Future Improvements

Planned enhancements:
- [ ] Track processed files to avoid duplicates
- [ ] Add OCR for image-based PDFs
- [ ] Scheduled automatic ingestion of new files
