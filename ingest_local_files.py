"""
Local File Ingestion Script for Training Tessa
Reads training documents from local OneDrive folder and sends to n8n ingestion webhook.
"""

import os
import sys
import httpx
import time
from pathlib import Path

# Configuration
TRAINING_FOLDER = r"C:\Users\JoelBentley\OneDrive - Meraki Talent\Agent Content\Training"
WEBHOOK_URL = "https://n8n-production-ac1d.up.railway.app/webhook/ingest-document"
REQUEST_TIMEOUT = 120

# File type handlers
def extract_docx(file_path):
    """Extract text from .docx files."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        return '\n\n'.join(text)
    except Exception as e:
        print(f"  Error extracting docx: {e}")
        return None

def extract_pptx(file_path):
    """Extract text from .pptx files."""
    try:
        from pptx import Presentation
        prs = Presentation(file_path)
        text = []
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text)
            if slide_text:
                text.append(f"Slide {slide_num}:\n" + '\n'.join(slide_text))
        return '\n\n'.join(text)
    except Exception as e:
        print(f"  Error extracting pptx: {e}")
        return None

def extract_pdf(file_path):
    """Extract text from .pdf files."""
    try:
        import pdfplumber
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text.append(f"Page {page_num}:\n{page_text}")
        return '\n\n'.join(text)
    except Exception as e:
        print(f"  Error extracting pdf: {e}")
        return None

def extract_odt(file_path):
    """Extract text from .odt files."""
    try:
        from odf import text as odf_text
        from odf.opendocument import load
        doc = load(file_path)
        all_text = []
        for elem in doc.getElementsByType(odf_text.P):
            text_content = ''.join(node.data for node in elem.childNodes if hasattr(node, 'data'))
            if text_content.strip():
                all_text.append(text_content)
        return '\n\n'.join(all_text)
    except Exception as e:
        print(f"  Error extracting odt: {e}")
        return None

def extract_text(file_path):
    """Extract text based on file extension."""
    ext = Path(file_path).suffix.lower()

    if ext in ['.docx', '.doc']:
        return extract_docx(file_path)
    elif ext in ['.pptx', '.ppt']:
        return extract_pptx(file_path)
    elif ext == '.pdf':
        return extract_pdf(file_path)
    elif ext in ['.odt', '.odp']:
        return extract_odt(file_path)
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        print(f"  Unsupported file type: {ext}")
        return None

def send_to_webhook(text, source_document):
    """Send extracted text to n8n ingestion webhook."""
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(
                WEBHOOK_URL,
                json={
                    "text": text,
                    "source_document": source_document
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"  Error sending to webhook: {e}")
        return False

def main():
    """Main ingestion function."""
    print("=" * 60)
    print("Training Tessa - Local File Ingestion")
    print("=" * 60)
    print(f"\nSource folder: {TRAINING_FOLDER}")
    print(f"Webhook URL: {WEBHOOK_URL}\n")

    # Check folder exists
    if not os.path.exists(TRAINING_FOLDER):
        print(f"ERROR: Folder not found: {TRAINING_FOLDER}")
        sys.exit(1)

    # Get all files
    files = [f for f in os.listdir(TRAINING_FOLDER) if os.path.isfile(os.path.join(TRAINING_FOLDER, f))]

    # Filter supported file types
    supported_extensions = ['.docx', '.doc', '.pptx', '.ppt', '.pdf', '.odt', '.odp', '.txt']
    files = [f for f in files if Path(f).suffix.lower() in supported_extensions]

    print(f"Found {len(files)} supported files to process\n")

    # Process each file
    success_count = 0
    error_count = 0

    for i, filename in enumerate(files, 1):
        file_path = os.path.join(TRAINING_FOLDER, filename)
        print(f"[{i}/{len(files)}] Processing: {filename}")

        # Extract text
        text = extract_text(file_path)

        if not text or len(text.strip()) < 50:
            print(f"  Skipped - no text extracted or too short")
            error_count += 1
            continue

        print(f"  Extracted {len(text)} characters")

        # Send to webhook
        if send_to_webhook(text, filename):
            print(f"  [OK] Sent to webhook successfully")
            success_count += 1
        else:
            print(f"  [FAIL] Failed to send to webhook")
            error_count += 1

        # Small delay to avoid overwhelming the webhook
        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"Successfully ingested: {success_count}")
    print(f"Failed/skipped: {error_count}")
    print(f"Total files: {len(files)}")

if __name__ == "__main__":
    main()
