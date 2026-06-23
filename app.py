"""
Info Pack Bot - Meraki Talent
Web form: paste recruiter notes, get a candidate-facing info pack with recent news.
(Page title still reads "Interview Prep Bot" per Joel.)
"""

import os
import re
import httpx
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-pro"

_gemini_client = None


def get_gemini_client():
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


SYSTEM_PROMPT = """You generate a candidate-facing info pack for a recruitment opportunity at Meraki Talent. The pack pitches the role to a prospective candidate. It is not internal, it is not interview prep, and it is not a covering email.

You are given:
- notes: the recruiter's raw notes about the firm and the role (firm description, fund history, role, team, comp and internal commentary all mixed together).
- Google Search access: use it to find recent news about the firm for the Recent news section only.

OUTPUT FORMAT
Plain text, ready to paste into Outlook. No markdown, no bold, no headings prefixed with #, no bullet symbols other than the hyphen lists shown below. Produce exactly this section structure and order. Drop any section whole when there is nothing real to fill it. Do NOT include a Compensation section under any circumstances. Do NOT add a closing line or signoff; the recruiter writes their own.

Structure:

{Firm}
{Role title}
Prepared by Meraki Talent

About {firm}
{two to four plain lines: what they do, focus, footprint}

Track record
- {fund or milestone, with year and amount}
- {fund or milestone, with year and amount}
{optional headline stat line}

Your contact at the firm
{name}, {title}
{one or two lines on background}

The opportunity
{what the role is and what they actually want}

What they're looking for
- {background sought}
- {location}
- {any flexibility, e.g. player/coach}

Recent news
- {one short summary line}
  {url}
- {one short summary line}
  {url}

WHAT TO INCLUDE, WHAT TO STRIP
Everything candidate-facing goes in: firm, track record, contact, role, background sought, location. Strip all internal colour, no exceptions:
- pipeline state ("open since February", "not getting traction")
- urgency to the recruiter ("ready to move on this")
- candid team assessments ("not producing", "likely to move into marketing")
Neutralise team detail to a plain structure ("a capital raising team of three") or drop it. If you cannot tell whether a line is sell-side or internal, leave it out. Never include compensation figures, even when present in the notes.

WHERE FACTS COME FROM
Everything above Recent news comes from the notes. Google Search only feeds the Recent news block. If a news item contradicts the notes, the notes win for the pack body. Never invent figures, names, fund sizes or URLs.

NEWS BLOCK RULES
- Find two to four recent, relevant items about the firm via Google Search.
- Use the real publication URL (e.g. https://commercialobserver.com/...). Never use a Google redirect URL or any vertexaisearch.cloud.google.com link. If the only URL you have is a redirect, drop that item.
- Each item: one short summary line, then the URL on its own line directly underneath, indented by two spaces.
- If you cannot find genuine news with real URLs, drop the Recent news section entirely rather than inventing.

STYLE
- British English.
- No em dashes anywhere. Use a comma or full stop instead.
- No AI filler. Never use these phrases or words: "I hope this finds you well", "I wanted to reach out", "delve", "leverage", "furthermore", "moreover", "it's worth noting", "in today's landscape".
- Short, plain sentences, the way an experienced recruiter writes.
- No praise or marketing fluff in the firm description. State facts.
- Links on their own line under each news item. Never inline.

Output the plain-text info pack with no preamble, no closing remark, no markdown code fences."""


PAGE = """<!doctype html>
<html><head><title>Interview Prep Bot</title>
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { margin-bottom: 0.25rem; }
  .sub { color: #666; margin-top: 0; }
  label { display: block; margin-top: 1rem; font-weight: 600; }
  textarea { width: 100%; padding: 0.55rem; font-size: 1rem; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; min-height: 320px; }
  button { margin-top: 1rem; padding: 0.65rem 1.4rem; font-size: 1rem; cursor: pointer; background: #2563eb; color: white; border: none; border-radius: 4px; }
  button:hover { background: #1d4ed8; }
  .pack { background: #f5f5f5; padding: 1rem 1.2rem; border-radius: 6px; white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin-top: 0.5rem; font-size: 0.92rem; line-height: 1.5; }
  .error { color: #b00020; background: #ffe8ec; padding: 0.75rem 1rem; border-radius: 4px; }
  .copy-btn { background: #555; font-size: 0.85rem; padding: 0.4rem 0.8rem; color: white; }
</style></head>
<body>
<h1>Interview Prep Bot</h1>
<p class="sub">Paste your recruiter notes about the firm and the role. The bot drafts a candidate-facing info pack and finds recent news about the firm.</p>
<form method="post">
  <label>Notes</label>
  <textarea name="notes" required placeholder="Firm description, fund history, role, team, comp, internal colour - paste it all. The bot will strip the internal stuff and structure the rest. Compensation is never included.">{{ notes or '' }}</textarea>
  <button type="submit">Generate info pack</button>
</form>
{% if pack %}
  <h2>Info pack</h2>
  <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('pack-text').innerText)">Copy to clipboard</button>
  <div class="pack" id="pack-text">{{ pack }}</div>
{% endif %}
{% if error %}
  <p class="error">{{ error }}</p>
{% endif %}
</body></html>"""


def strip_code_fence(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


# Gemini grounding hands back Google redirect URLs; resolve them to the real
# publication URLs the info-pack spec requires.
REDIRECT_PATTERN = re.compile(
    r"https?://vertexaisearch\.cloud\.google\.com/grounding-api-redirect/[^\s)]+"
)


def _resolve_one(redirect_url):
    try:
        with httpx.Client(follow_redirects=True, timeout=8.0) as client:
            resp = client.head(redirect_url)
            final = str(resp.url)
            if final == redirect_url or "vertexaisearch.cloud.google.com" in final:
                resp = client.get(redirect_url)
                final = str(resp.url)
            return redirect_url, final
    except Exception:
        return redirect_url, redirect_url


def resolve_redirect_urls(text):
    urls = list(set(REDIRECT_PATTERN.findall(text)))
    if not urls:
        return text
    with ThreadPoolExecutor(max_workers=min(8, len(urls))) as pool:
        for original, final in pool.map(_resolve_one, urls):
            if final and final != original:
                text = text.replace(original, final)
    return text


def generate_info_pack(notes):
    client = get_gemini_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"notes:\n{notes}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return resolve_redirect_urls(strip_code_fence(response.text))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        notes = request.form.get("notes", "").strip()
        try:
            pack = generate_info_pack(notes)
            return render_template_string(PAGE, pack=pack, notes=notes, error=None)
        except Exception as e:
            return render_template_string(
                PAGE, pack=None, notes=notes, error=f"Error generating info pack: {e}"
            )
    return render_template_string(PAGE, pack=None, notes="", error=None)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy", "bot": "Info Pack Bot"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
