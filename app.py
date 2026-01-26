"""
Training Tessa - Meraki Talent Training Bot
A Teams bot that answers staff questions using RAG-powered training documents.
Now with built-in Q&A using Gemini 2.5 Pro (no n8n dependency).
"""

import os
import asyncio
import httpx
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
import google.generativeai as genai

app = Flask(__name__)

# Bot Framework settings - initialized lazily to allow health checks before env vars are set
ADAPTER = None

def get_adapter():
    """Get or create Bot Framework adapter."""
    global ADAPTER
    if ADAPTER is None:
        settings = BotFrameworkAdapterSettings(
            app_id=os.environ.get("MICROSOFT_APP_ID"),
            app_password=os.environ.get("MICROSOFT_APP_PASSWORD"),
            channel_auth_tenant=os.environ.get("MICROSOFT_APP_TENANT_ID")
        )
        ADAPTER = BotFrameworkAdapter(settings)
    return ADAPTER

# =============================================================================
# Q&A CONFIGURATION - All secrets loaded from environment variables
# =============================================================================

# Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-pro-preview-05-06"

# Azure OpenAI (for embeddings - keep for compatibility with existing vectors)
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://meraki-training-bot.openai.azure.com")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
API_VERSION = "2025-03-01-preview"

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://uwxsflcpaigcygfhxzzl.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Request timeout (seconds)
REQUEST_TIMEOUT = 60

# =============================================================================
# TESSA'S PERSONALITY - Customize her communication style here!
# =============================================================================

TESSA_SYSTEM_PROMPT = """You are Training Tessa, the friendly and knowledgeable training assistant for Meraki Talent staff.

## Your Personality
- Warm, approachable, and encouraging
- Professional but not stiff - like a helpful colleague
- Patient when explaining complex topics
- Honest when you don't know something

## How You Communicate
- Use clear, simple language - avoid jargon unless it's in the source material
- Break down complex answers into easy-to-follow steps
- Use bullet points for lists and processes
- Keep answers concise but complete
- Add a brief encouraging note when appropriate

## How You Handle Questions
- Base your answers on the training documents provided in the context
- If the context contains relevant information, use it to give a helpful answer
- If you're not sure or the context doesn't cover the question, say so honestly
- Always mention which document(s) your answer comes from when relevant
- If someone asks something outside your training scope, kindly redirect them

## Response Format
- Start with a direct answer to the question
- Provide supporting details or steps if needed
- Keep responses focused - don't over-explain
- End with an offer to help further if the topic is complex

Remember: You're here to help Meraki Talent staff learn and succeed!"""

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def create_embedding(text):
    """Create embedding using Azure OpenAI."""
    try:
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{EMBEDDING_DEPLOYMENT}/embeddings?api-version={API_VERSION}"

        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(
                url,
                headers={
                    "api-key": AZURE_OPENAI_KEY,
                    "Content-Type": "application/json"
                },
                json={"input": text}
            )
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None


def search_documents(query_embedding, match_count=5, match_threshold=0.1):
    """Search Supabase for similar documents."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/rpc/match_documents"

        # Embedding must be passed as a string for Supabase RPC
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'

        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(
                url,
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query_embedding": embedding_str,
                    "match_threshold": match_threshold,
                    "match_count": match_count
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error searching documents: {e}")
        return []


def generate_answer(question, context_chunks):
    """Generate answer using Gemini 2.5 Pro."""
    try:
        # Build context from retrieved chunks
        if context_chunks:
            context_parts = []
            for i, chunk in enumerate(context_chunks, 1):
                source = chunk.get('source_document', 'Unknown')
                content = chunk.get('content', '')
                context_parts.append(f"[Document {i}: {source}]\n{content}")

            context = "\n\n---\n\n".join(context_parts)

            user_prompt = f"""Based on the following training documents, please answer the question.

## Training Documents:
{context}

## Question:
{question}

Please provide a helpful answer based on the documents above."""
        else:
            user_prompt = f"""The user has asked a question, but no relevant training documents were found.

## Question:
{question}

Please let them know you couldn't find specific information about this in the training materials, and offer to help if they rephrase or ask something else."""

        # Call Gemini
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=TESSA_SYSTEM_PROMPT
        )

        response = model.generate_content(user_prompt)
        return response.text

    except Exception as e:
        print(f"Error generating answer: {e}")
        return None


def ask_tessa(question):
    """Main Q&A function - creates embedding, searches, generates answer."""
    # Step 1: Create embedding for the question
    embedding = create_embedding(question)
    if not embedding:
        return {
            "answer": "Sorry, I had trouble processing your question. Please try again.",
            "sources": [],
            "chunk_count": 0
        }

    # Step 2: Search for relevant documents
    chunks = search_documents(embedding)

    # Step 3: Generate answer with Gemini
    answer = generate_answer(question, chunks)
    if not answer:
        return {
            "answer": "Sorry, I encountered an error generating a response. Please try again.",
            "sources": [],
            "chunk_count": len(chunks)
        }

    # Step 4: Extract unique sources
    sources = list(set(chunk.get('source_document', 'Unknown') for chunk in chunks if chunk.get('source_document')))

    return {
        "answer": answer,
        "sources": sources,
        "chunk_count": len(chunks)
    }


async def on_turn(turn_context: TurnContext):
    """Handle incoming messages."""
    if turn_context.activity.type == ActivityTypes.message:
        user_question = turn_context.activity.text

        if not user_question or not user_question.strip():
            await turn_context.send_activity("Hi! I'm Training Tessa. Ask me anything about Meraki Talent processes, policies, or training materials.")
            return

        # Show typing indicator
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

        try:
            # Use built-in Q&A with Gemini
            result = ask_tessa(user_question)

            # Extract answer and sources
            answer = result.get("answer", "Sorry, I couldn't find an answer to that question.")
            sources = result.get("sources", [])

            # Format response
            reply = answer

            # Add sources if available
            if sources and len(sources) > 0:
                unique_sources = list(set(sources))  # Remove duplicates
                reply += f"\n\n📚 **Sources:** {', '.join(unique_sources)}"

            await turn_context.send_activity(reply)

        except Exception as e:
            print(f"Error: {e}")
            await turn_context.send_activity(
                "Sorry, something went wrong. Please try again later."
            )

    elif turn_context.activity.type == ActivityTypes.conversation_update:
        # Welcome new users
        if turn_context.activity.members_added:
            for member in turn_context.activity.members_added:
                if member.id != turn_context.activity.recipient.id:
                    welcome_message = (
                        "👋 Hi! I'm **Training Tessa**, your Meraki Talent training assistant.\n\n"
                        "Ask me anything about:\n"
                        "• Company policies and procedures\n"
                        "• Training materials and guides\n"
                        "• Best practices and processes\n\n"
                        "Just type your question and I'll search our training documents for the answer!"
                    )
                    await turn_context.send_activity(welcome_message)


def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route("/api/messages", methods=["POST"])
def messages():
    """Main endpoint for Bot Framework messages."""
    if "application/json" in request.content_type:
        body = request.json
        activity = Activity().deserialize(body)
        auth_header = request.headers.get("Authorization", "")

        async def call_on_turn(turn_context: TurnContext):
            await on_turn(turn_context)

        task = get_adapter().process_activity(activity, auth_header, call_on_turn)
        run_async(task)

        return jsonify({"status": "ok"})

    return jsonify({"error": "Unsupported content type"}), 415


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "bot": "Training Tessa"})


@app.route("/", methods=["GET"])
def home():
    """Root endpoint."""
    return jsonify({
        "bot": "Training Tessa",
        "description": "Meraki Talent Training Assistant",
        "status": "running"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
