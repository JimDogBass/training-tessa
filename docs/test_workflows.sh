#!/bin/bash

# Meraki Training Bot - Test Script
# Run this to test the n8n workflows

echo "=== Testing Meraki Training Bot ==="
echo ""

# Test 1: Document Ingestion
echo "1. Testing Document Ingestion..."
echo "   Sending test document to n8n..."
echo ""

INGEST_RESPONSE=$(curl -s -X POST https://n8n-production-ac1d.up.railway.app/webhook-test/ingest-document \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Meraki Talent is a financial services recruitment agency founded in 2015. We have offices in Edinburgh, Glasgow, and London. We specialize in private equity, venture capital, and alternative asset recruitment. Our team of 40 consultants works with top-tier firms in the alternative assets space.",
    "source_document": "company-overview"
  }')

echo "   Response: $INGEST_RESPONSE"
echo ""

# Wait a moment for processing
echo "   Waiting 3 seconds for processing..."
sleep 3
echo ""

# Test 2: Question Answering
echo "2. Testing Question Answering..."
echo "   Asking: What is Meraki Talent?"
echo ""

QUESTION_RESPONSE=$(curl -s -X POST https://n8n-production-ac1d.up.railway.app/webhook-test/ask-question \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Meraki Talent?"}')

echo "   Response: $QUESTION_RESPONSE"
echo ""

echo "=== Tests Complete ==="
echo ""
echo "If you see errors, check:"
echo "  - n8n workflow execution logs"
echo "  - Credentials are configured in n8n"
echo "  - Workflows are active"
