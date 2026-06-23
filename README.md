# Interview Prep Bot - Meraki Talent

A small Flask app that turns recruiter notes into a candidate-facing info pack, with recent news on the firm pulled in via Google Search grounding.

## Two surfaces

1. **Teams chat** — message the bot ("Training Tessa" in Teams, behind `/api/messages`) with your raw notes, get the pack back in chat.
2. **Web form** — open the root URL in a browser, paste notes, click Generate, copy the result.

Both call the same `generate_info_pack()` and use the same system prompt.

## How it works

Recruiter pastes raw notes (firm description, role, team, comp, internal colour). Gemini 2.5 Pro strips the internal stuff, structures the rest into the standard info pack template, and uses Google Search to add a Recent news block. Redirect URLs from grounding are resolved server-side to the real publication URLs.

Compensation is never included. No closing line or signoff is added; the recruiter writes their own.

The output template, banned-phrase list and strip-internal rules all live in `SYSTEM_PROMPT` in `app.py` — edit there.

## Live

- App: https://web-production-41f7a.up.railway.app
- Health: https://web-production-41f7a.up.railway.app/health

## Environment Variables (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `MICROSOFT_APP_ID` | Yes (Teams) | Azure Bot App ID |
| `MICROSOFT_APP_PASSWORD` | Yes (Teams) | Azure Bot client secret |
| `MICROSOFT_APP_TENANT_ID` | Yes (Teams) | Azure Bot tenant ID |

`SUPABASE_*` vars are no longer used and can be deleted from the Railway Variables tab.

## Customising the email style

Edit `SYSTEM_PROMPT` in `app.py` — tone, structure, what sections to include, length, sign-off, etc.

## Local development

```bash
pip install -r requirements.txt
set GEMINI_API_KEY=your-key
python app.py
```

Then open http://localhost:3978.

## Stack

- Flask + Gunicorn (Railway)
- Google Gemini 2.5 Pro (`google-genai` package)
- Single-file app, inline HTML template
