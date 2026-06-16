# Tony - KOP Desk QA Agent

A Streamlit app that exposes a button to trigger Tony, a Playwright-powered QA support agent.

## What Tony does

- Opens KOP Desk
- Logs in to the support portal
- Navigates to `/incidents`
- Filters or identifies `New` incidents
- Adds a holding response
- Marks tickets as `In Progress`
- Produces an execution report

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

## Required environment variables

Create `.streamlit/secrets.toml` or set environment variables.

```toml
KOPDESK_BASE_URL = "https://kopdesk.koptechnology.com"
KOPDESK_INCIDENTS_URL = "https://kopdesk.koptechnology.com/incidents"
KOPDESK_USERNAME = "support@koptechnology.co.uk"
KOPDESK_PASSWORD = "Tester@24680"
HOLDING_RESPONSE = "Hello, thank you for contacting KOP Desk Support. We have received your incident and our support team is currently reviewing it. We will provide an update as soon as possible."
```

## Streamlit Cloud deployment note

Add the same values under **App settings → Secrets**. If browser automation fails on Streamlit Cloud due to Chromium restrictions, deploy on a VPS, Render, Railway, or a private server where Playwright browsers can be installed.

## Safety switch

The app starts in **Dry run only** mode. Turn it off in the sidebar when you are ready for Tony to save live updates.
