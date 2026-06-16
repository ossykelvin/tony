# Tony - KOP Desk QA Agent

Streamlit app that runs a Playwright-based QA support agent for KOP Desk incidents.

## Streamlit Cloud deployment

This version pins Python to 3.12 using `runtime.txt` and removes the risky `setup.sh` install step.

Files required in your GitHub repo:

- `app.py`
- `requirements.txt`
- `packages.txt`
- `runtime.txt`
- `.streamlit/secrets.toml` or Streamlit Cloud Secrets

## Secrets

In Streamlit Cloud, open **Manage app → Settings → Secrets** and add:

```toml
KOPDESK_BASE_URL = "https://kopdesk.koptechnology.com"
KOPDESK_INCIDENTS_URL = "https://kopdesk.koptechnology.com/incidents"
KOPDESK_USERNAME = "support@koptechnology.co.uk"
KOPDESK_PASSWORD = "Tester@24680"
HOLDING_RESPONSE = "Hello, thank you for contacting KOP Desk Support. We have received your incident and our support team is currently reviewing it. We will provide an update as soon as possible."
```

## Local run

```bash
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## Important

Dry run is ON by default. Turn it OFF only when you are ready for Tony to save updates.
