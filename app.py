"""
Training Tessa - Meraki Talent Training Bot
A Teams bot that answers staff questions using RAG-powered training documents.
"""

import os
import asyncio
import httpx
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes

app = Flask(__name__)

# Bot Framework settings - initialized lazily to allow health checks before env vars are set
ADAPTER = None

def get_adapter():
    """Get or create Bot Framework adapter."""
    global ADAPTER
    if ADAPTER is None:
        settings = BotFrameworkAdapterSettings(
            app_id=os.environ.get("MICROSOFT_APP_ID"),
            app_password=os.environ.get("MICROSOFT_APP_PASSWORD")
        )
        ADAPTER = BotFrameworkAdapter(settings)
    return ADAPTER

# n8n webhook URL for Q&A
N8N_QA_WEBHOOK = "https://n8n-production-ac1d.up.railway.app/webhook/ask-question"

# Timeout for n8n requests (seconds)
REQUEST_TIMEOUT = 60


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
            # Call n8n Q&A webhook
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    N8N_QA_WEBHOOK,
                    json={"question": user_question},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()

            # Extract answer and sources
            answer = result.get("answer", "Sorry, I couldn't find an answer to that question.")
            sources = result.get("sources", [])
            chunk_count = result.get("chunk_count", 0)

            # Format response
            reply = answer

            # Add sources if available
            if sources and len(sources) > 0:
                unique_sources = list(set(sources))  # Remove duplicates
                reply += f"\n\n📚 **Sources:** {', '.join(unique_sources)}"

            await turn_context.send_activity(reply)

        except httpx.TimeoutException:
            await turn_context.send_activity(
                "Sorry, the request timed out. Please try again or rephrase your question."
            )
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            await turn_context.send_activity(
                "Sorry, I encountered an error while searching for an answer. Please try again."
            )
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
