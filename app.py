import os
import time
from datetime import datetime
import streamlit as st

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except Exception:
    sync_playwright = None

APP_TITLE = os.getenv("APP_TITLE", "Tony - KOP Desk QA Agent")
DEFAULT_HOLDING_RESPONSE = os.getenv(
    "HOLDING_RESPONSE",
    "Hello, thank you for contacting KOP Desk Support. We have received your incident and our support team is currently reviewing it. We will provide an update as soon as possible."
)

st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .main { background: #F2F4F7; }
    .tony-card {
        background: white;
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 10px 28px rgba(13, 27, 61, 0.12);
        border: 1px solid rgba(37, 99, 235, 0.12);
    }
    .tony-title { color: #0D1B3D; margin-bottom: 6px; }
    .tony-subtitle { color: #475569; font-size: 16px; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0D1B3D, #2563EB);
        color: white;
        border: 0;
        border-radius: 12px;
        padding: 0.75rem 1.2rem;
        font-weight: 700;
        width: 100%;
    }
    div.stButton > button:first-child:hover { color: white; filter: brightness(1.05); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class='tony-card'>
        <h1 class='tony-title'>{APP_TITLE}</h1>
        <p class='tony-subtitle'>Click the button below to log in, filter new incidents, add a holding response, and mark tickets as In Progress.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.sidebar:
    st.header("Configuration")
    st.caption("Use Streamlit secrets or environment variables in production.")
    headless = st.toggle("Run browser headless", value=True)
    dry_run = st.toggle("Dry run only", value=True, help="When enabled, Tony logs actions but does not save ticket updates.")
    max_tickets = st.number_input("Maximum tickets to process", min_value=1, max_value=100, value=10)


def cfg(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def run_tony(headless: bool, dry_run: bool, max_tickets: int):
    if sync_playwright is None:
        return {
            "status": "error",
            "message": "Playwright is not installed. Run: pip install -r requirements.txt && playwright install chromium",
            "tickets": [],
        }

    base_url = cfg("KOPDESK_BASE_URL", "https://kopdesk.koptechnology.com")
    incidents_url = cfg("KOPDESK_INCIDENTS_URL", f"{base_url}/incidents")
    username = cfg("KOPDESK_USERNAME")
    password = cfg("KOPDESK_PASSWORD")
    response = cfg("HOLDING_RESPONSE", DEFAULT_HOLDING_RESPONSE)

    if not username or not password:
        return {"status": "error", "message": "Missing KOPDESK_USERNAME or KOPDESK_PASSWORD.", "tickets": []}

    report = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            report.append("Opening KOP Desk login page")
            page.goto(base_url, wait_until="networkidle", timeout=60000)

            # Flexible selectors for common login forms.
            page.locator("input[type='email'], input[name='email'], input[name='username'], input[placeholder*='Email'], input[placeholder*='Username']").first.fill(username)
            page.locator("input[type='password'], input[name='password'], input[placeholder*='Password']").first.fill(password)
            page.locator("button[type='submit'], button:has-text('Login'), button:has-text('Sign in'), button:has-text('Log in')").first.click()
            page.wait_for_load_state("networkidle", timeout=60000)

            report.append("Navigating to incidents")
            page.goto(incidents_url, wait_until="networkidle", timeout=60000)

            # Try to filter status New using visible controls.
            try:
                page.locator("text=Status").first.click(timeout=5000)
            except Exception:
                pass

            filter_applied = False
            for selector in [
                "select[name*='status']",
                "select[aria-label*='Status']",
                "select",
            ]:
                try:
                    page.locator(selector).first.select_option(label="New", timeout=5000)
                    filter_applied = True
                    break
                except Exception:
                    continue

            if not filter_applied:
                for label in ["New", "Status: New", "Filter", "Apply"]:
                    try:
                        page.get_by_text(label, exact=False).first.click(timeout=3000)
                    except Exception:
                        pass

            page.wait_for_timeout(1500)

            rows = page.locator("tr, [role='row'], .incident-card, .ticket-card").all()
            processed = 0
            ticket_refs = []

            for i, row in enumerate(rows):
                if processed >= max_tickets:
                    break
                text = ""
                try:
                    text = row.inner_text(timeout=2000)
                except Exception:
                    continue

                if "new" not in text.lower():
                    continue

                ticket_ref = text.split("\n")[0][:80] or f"Ticket row {i + 1}"
                ticket_refs.append(ticket_ref)
                report.append(f"Found new incident: {ticket_ref}")

                if dry_run:
                    processed += 1
                    report.append(f"DRY RUN: Would add holding response and set In Progress for {ticket_ref}")
                    continue

                row.click(timeout=10000)
                page.wait_for_load_state("networkidle", timeout=30000)

                # Add note/comment.
                note_done = False
                for selector in [
                    "textarea[name*='comment']",
                    "textarea[name*='note']",
                    "textarea[placeholder*='comment']",
                    "textarea[placeholder*='response']",
                    "textarea",
                    "[contenteditable='true']",
                ]:
                    try:
                        page.locator(selector).first.fill(response, timeout=5000)
                        note_done = True
                        break
                    except Exception:
                        continue

                # Set status.
                status_done = False
                for selector in ["select[name*='status']", "select[aria-label*='Status']", "select"]:
                    try:
                        page.locator(selector).first.select_option(label="In Progress", timeout=5000)
                        status_done = True
                        break
                    except Exception:
                        continue

                if not status_done:
                    try:
                        page.get_by_text("In Progress", exact=False).first.click(timeout=5000)
                        status_done = True
                    except Exception:
                        pass

                # Save/update.
                saved = False
                for label in ["Save", "Update", "Submit", "Add response"]:
                    try:
                        page.get_by_role("button", name=label).first.click(timeout=5000)
                        saved = True
                        break
                    except Exception:
                        continue

                page.wait_for_timeout(1500)
                report.append(f"Updated {ticket_ref}: note={note_done}, status={status_done}, saved={saved}")
                processed += 1
                page.goto(incidents_url, wait_until="networkidle", timeout=60000)

            browser.close()
            return {
                "status": "success",
                "message": f"Tony completed. Tickets identified: {len(ticket_refs)}. Tickets processed: {processed}.",
                "tickets": ticket_refs,
                "log": report,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "dry_run": dry_run,
            }
        except PlaywrightTimeoutError as exc:
            browser.close()
            return {"status": "error", "message": f"Timeout: {exc}", "tickets": ticket_refs if 'ticket_refs' in locals() else [], "log": report}
        except Exception as exc:
            browser.close()
            return {"status": "error", "message": str(exc), "tickets": ticket_refs if 'ticket_refs' in locals() else [], "log": report}


if st.button("🚀 Execute Tony"):
    with st.spinner("Tony is running the incident workflow..."):
        result = run_tony(headless=headless, dry_run=dry_run, max_tickets=int(max_tickets))

    if result["status"] == "success":
        st.success(result["message"])
    else:
        st.error(result["message"])

    st.subheader("Execution Report")
    st.json(result)
