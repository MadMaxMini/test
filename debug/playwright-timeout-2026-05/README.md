# Playwright Google Sheets Timeout Debug — May 2026

**Problem:** `wait_until="networkidle"` hangs forever on Google Sheets.
**Root cause:** Google Sheets never reaches network idle (collab sync, analytics, auto-save keep firing).
**Fix:** Use `wait_until="domcontentloaded"` — DOM is ready in ~1s, cells are readable/writable immediately.

## Files

| File | Purpose |
|------|---------|
| `playwright-timeout-diagnosis.md` | Full diagnosis report with test results and recommendations |
| `playwright-diagnostic.py` | 5-scenario diagnostic script (domcontentloaded vs networkidle, headless vs visual) |
| `explain-networkidle.py` | Visual demo showing why networkidle never triggers (launches visible browser) |

## Result

All production code (`sheets_bridge.py`, `gsheets_sync.py`) already uses `domcontentloaded`. No fix needed — this confirmed the correct approach.
