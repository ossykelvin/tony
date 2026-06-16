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

## Fix for `Missing KOPDESK_USERNAME or KOPDESK_PASSWORD`

Create this exact file:

```text
.streamlit/secrets.toml
```

Do not leave it as `secrets.toml.example`.

Add your values in this format:

```toml
KOPDESK_BASE_URL = "https://kopdesk.koptechnology.com"
KOPDESK_INCIDENTS_URL = "https://kopdesk.koptechnology.com/incidents"
KOPDESK_USERNAME = "support@koptechnology.co.uk"
KOPDESK_PASSWORD = "Tester@24680"
HOLDING_RESPONSE = "Hello, thank you for contacting KOP Desk Support. We have received your incident and our support team is currently reviewing it. We will provide an update as soon as possible."
```

You can also enter the username and password directly in the Streamlit sidebar.

## Streamlit Cloud deployment

In Streamlit Cloud, add the same TOML values under:

```text
App settings → Secrets
```

Then reboot/redeploy the app.

## Safety switch

The app starts in **Dry run only** mode. Turn it off in the sidebar when you are ready for Tony to save live updates.

## Streamlit Cloud Playwright fix

This version includes:

- `packages.txt` for Chromium Linux dependencies
- `setup.sh` to install the Playwright Chromium browser
- runtime fallback install if Chromium is missing
- Chromium launch flags for hosted Linux environments

After pushing these files, redeploy/reboot the Streamlit app. If the app was already deployed, use **Manage app → Reboot app** or redeploy from GitHub so `packages.txt` and `setup.sh` are picked up.
