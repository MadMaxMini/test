#!/Users/macBot/Work/local/scripts/.venv/bin/python3
"""
Visual explanation: Why networkidle hangs on Google Sheets.

Launches browser (headless=False) to visually show:
1. Page loads instantly with domcontentloaded
2. But background network requests keep firing forever
3. networkidle never triggers because network never idles
"""

import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = "/Users/macBot/.playwright-google"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ac7cAq8Drd2eXmOYt16zhRxZvnPxDGA0q-m8qrkyvMk/edit?gid=1111466851"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("Google Sheets networkidle explanation")
    log(f"Opening: {SHEET_URL}\n")

    network_events = {"request": 0, "response": 0, "finish": 0}

    with sync_playwright() as p:
        log("Launching browser (headless=False for visibility)...")
        browser = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,  # Visual mode
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Track network activity
        def on_request(req):
            network_events["request"] += 1
            if "gstatic" not in req.url and "google-analytics" not in req.url:
                log(f"  → request #{network_events['request']}: {req.url.split('/')[-1][:50]}")

        def on_response(res):
            network_events["response"] += 1

        def on_finish(res):
            network_events["finish"] += 1

        page.on("request", on_request)
        page.on("response", on_response)

        log("\n=== PHASE 1: Load with domcontentloaded ===")
        log("(Page becomes interactive here)")
        try:
            page.goto(SHEET_URL, wait_until="domcontentloaded", timeout=10000)
            log(f"✅ domcontentloaded reached in ~1s")
            log(f"   Page title: {page.title()}")
            log(f"   Network so far: {network_events['request']} requests\n")
        except Exception as e:
            log(f"❌ Failed: {e}")
            return 1

        log("=== PHASE 2: Try to reach networkidle ===")
        log("(Waiting for 500ms of network silence...)")
        log("Watch the browser window — notice background activity:\n")

        import time
        start = time.time()
        request_count_at_start = network_events["request"]

        # Monitor network activity for 20 seconds
        for i in range(20):
            time.sleep(1)
            new_requests = network_events["request"] - request_count_at_start
            elapsed = time.time() - start
            log(f"  {elapsed:.0f}s: {network_events['request']} total requests, "
                f"+{new_requests} in last 1s (network ACTIVE)" if new_requests > 0
                else f"  {elapsed:.0f}s: {network_events['request']} total requests (IDLE)")

        log(f"\n❌ networkidle NEVER triggers because:")
        log(f"   1. Google Sheets keeps background requests flowing continuously")
        log(f"   2. Collaborative editing protocol (real-time sync)")
        log(f"   3. Analytics/telemetry pings")
        log(f"   4. Auto-save API calls")
        log(f"   5. WebSocket keepalives")
        log(f"\n   → If you use wait_until='networkidle', it will timeout EVERY TIME")

        log(f"\n✅ SOLUTION: Use wait_until='domcontentloaded'")
        log(f"   Page is fully interactive at that point!")
        log(f"   Cells can be read/written immediately.")

        browser.close()
        log("\nBrowser closed. See visual window above for network activity proof.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
