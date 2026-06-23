# Interview Prep Bot - Meraki Talent

A small Flask web app that turns recruiter notes into a candidate-facing info pack, with recent news on the firm pulled in via Google Search grounding.

## What it does

1. Consultant pastes raw recruiter notes (firm description, role, team, comp, internal colour) into a web form.
2. Gemini 2.5 Pro strips the internal stuff, structures the rest into the standard info pack template, and uses Google Search to add a Recent news block with real URLs.
3. Plain-text pack rendered on the page with a Copy-to-Clipboard button.

Compensation is never included. No closing line or signoff is added; the recruiter writes their own. No database, no Teams plumbing, no automated sending.

The output template, banned-phrase list and strip-internal rules all live in `SYSTEM_PROMPT` in `app.py` — edit there.

## Live

- App: https://web-production-41f7a.up.railway.app
- Health: https://web-production-41f7a.up.railway.app/health

## Environment Variables (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |

Old Tessa env vars (`MICROSOFT_APP_*`, `SUPABASE_*`) are no longer used and can be deleted from the Railway Variables tab.

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
