#!/usr/bin/env python3
"""
Playwright diagnostic for Google Sheets timeout investigation.

Tests 5 scenarios:
1. domcontentloaded + 15s timeout (fail-fast)
2. domcontentloaded + 60s timeout (current)
3. networkidle + 15s timeout
4. networkidle + 60s timeout
5. headless=False to see visual load

Reports: timing, auth state, network errors.
"""

import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ac7cAq8Drd2eXmOYt16zhRxZvnPxDGA0q-m8qrkyvMk/edit?gid=1111466851"
PROFILE_DIR = "/Users/macBot/.playwright-google"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def check_profile():
    """Check browser profile state."""
    log("=== BROWSER PROFILE STATE ===")
    profile_path = Path(PROFILE_DIR)

    if not profile_path.exists():
        log("ERROR: Profile directory does not exist")
        return False

    # Check key files
    default_prefs = profile_path / "Default" / "Preferences"
    local_state = profile_path / "Local State"

    log(f"Profile dir: {profile_path}")
    log(f"  Size: {sum(f.stat().st_size for f in profile_path.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    log(f"  Default/Preferences exists: {default_prefs.exists()}")
    log(f"  Local State exists: {local_state.exists()}")

    # Check for stale locks
    locks = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
    for lock in locks:
        lock_path = profile_path / lock
        if lock_path.exists():
            age = time.time() - lock_path.stat().st_mtime
            log(f"  WARNING: {lock} exists (age: {age:.0f}s)")

    return True

def test_scenario(name, wait_until, timeout_ms, headless=True):
    """Run a single test scenario."""
    log(f"\n=== SCENARIO: {name} ===")
    log(f"wait_until={wait_until}, timeout={timeout_ms}ms, headless={headless}")

    # Clean stale locks before each test
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        Path(f"{PROFILE_DIR}/{lock}").unlink(missing_ok=True)

    script = f"""
import sys
import time
from playwright.sync_api import sync_playwright

start = time.time()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            "{PROFILE_DIR}",
            headless={headless},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            page.goto("{SHEET_URL}", wait_until="{wait_until}", timeout={timeout_ms})
            elapsed = time.time() - start
            print(f"OK — loaded in {{elapsed:.1f}}s")
            print(f"Title: {{page.title()}}")

            # Quick JS check for auth
            try:
                auth_check = page.evaluate("typeof document.body")
                print(f"DOM ready: True")
            except:
                print(f"DOM ready: False")

            browser.close()
            sys.exit(0)

        except Exception as e:
            elapsed = time.time() - start
            print(f"FAILED after {{elapsed:.1f}}s: {{type(e).__name__}}: {{str(e)[:100]}}")
            sys.exit(1)

except Exception as e:
    print(f"SETUP FAILED: {{e}}")
    sys.exit(2)
"""

    result = subprocess.run(
        ["/Users/macBot/Work/local/scripts/.venv/bin/python3", "-c", script],
        capture_output=True,
        text=True,
        timeout=max(timeout_ms // 1000 + 15, 60),
    )

    log("Output:")
    for line in result.stdout.split("\n"):
        if line:
            log(f"  {line}")

    if result.stderr:
        log("Stderr:")
        for line in result.stderr.split("\n"):
            if line:
                log(f"  {line}")

    log(f"Exit code: {result.returncode}")
    return result.returncode == 0

def main():
    log(f"Playwright Diagnostic — {datetime.now().isoformat()}")
    log(f"Target: {SHEET_URL}")

    # Check profile first
    if not check_profile():
        log("Profile check failed — stopping")
        return 1

    # Run scenarios
    scenarios = [
        ("domcontentloaded + 15s (fail-fast)", "domcontentloaded", 15000, True),
        ("domcontentloaded + 60s (current)", "domcontentloaded", 60000, True),
        ("networkidle + 15s", "networkidle", 15000, True),
        ("networkidle + 60s", "networkidle", 60000, True),
        ("headless=False (visual)", "domcontentloaded", 15000, False),
    ]

    results = {}
    for name, wait, timeout, headless in scenarios:
        try:
            results[name] = test_scenario(name, wait, timeout, headless)
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT: Test exceeded system timeout")
            results[name] = False
        except Exception as e:
            log(f"EXCEPTION: {e}")
            results[name] = False

        # Small delay between tests
        time.sleep(1)

    # Summary
    log(f"\n=== SUMMARY ===")
    for scenario, passed in results.items():
        status = "PASS" if passed else "FAIL"
        log(f"{scenario}: {status}")

    passed_count = sum(1 for v in results.values() if v)
    log(f"\nResult: {passed_count}/{len(results)} scenarios passed")

    # Diagnosis
    log(f"\n=== DIAGNOSIS ===")
    if all(results.values()):
        log("All tests passed — timeout is scenario-specific or intermittent")
    elif results["domcontentloaded + 15s (fail-fast)"] and not results["networkidle + 60s"]:
        log("DIAGNOSIS: networkidle hangs (network never stabilizes)")
        log("  → FIX: Use wait_until='domcontentloaded' instead of 'networkidle'")
    elif not results["domcontentloaded + 60s (current)"]:
        log("DIAGNOSIS: Even domcontentloaded times out — likely auth/network issue")
        log("  → CHECK: Browser profile auth, VPN/firewall, Google rate limits")
    elif not results["headless=False (visual)"]:
        log("DIAGNOSIS: Visual mode also fails — not headless-specific")
    else:
        log("DIAGNOSIS: Mixed results — check browser logs above for errors")

    return 0

if __name__ == "__main__":
    sys.exit(main())
