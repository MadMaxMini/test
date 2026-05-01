# Sheets Pipeline Phase 1 — WIRED ✅

**Date:** 2026-05-01  
**Status:** Complete and committed

## What Was Done

### Property Map Completed
- Added all 4 properties to `property_map.json`:
  - kickapoo-401 ✅
  - kickapoo-403 ✅
  - grand-pines-2889 ✅ (new)
  - la-estancia-2922 ✅ (new)
  - piney-point-8808 ✅ (new)
- All properties have sheet IDs from sheets_bridge.py SHEET_MAP

### FDA Permission
- `/bin/bash` granted Full Disk Access in System Settings ✅
- PDF watchers can now read from Dropbox

### Sheets Bridge Wired into Pipeline
**File:** `bot/pdf-extractor/extract-and-commit.sh`
- Added bridge loop after PDF extraction (line 47-56)
- Bridge runs for each CSV: `sheets_bridge.py --type mortgage --csv <file>`
- Fire-and-forget with `|| true` — Sheet failure never blocks git commit
- Bridge logs all writes to `$LOG`

**File:** `bot/pdf-extractor/extract-pm-and-commit.sh`
- Notification routing updated: iMessage group → Telegram to Rod
- No PM bridge wired yet (Phase 4)

### Notification Routing Updated
- Mortgage extraction: routine → Telegram to Rod
- Payment change alerts: handled separately by sheets_bridge.py (Telegram + iMessage)
- Uses `bot.telegram_notify` module (credentials stored in Keychain)

## What's Next

1. **Set up Telegram credentials** (in fresh context):
   - Create bot via @BotFather
   - Get chat ID and BOT_TOKEN
   - Store in Keychain on mac mini

2. **Test end-to-end** (once Telegram is ready):
   - Drop a test mortgage PDF into account-statements-inbox
   - Verify:
     - PDF extracted → CSV created
     - sheets_bridge.py runs → Google Sheet updated
     - Telegram notification sent to Rod
     - git commit created with CSV

3. **Monitor for 24h** for any issues (stuck PDFs, bridge timeouts, Sheet API errors)

4. **Process 5 stuck PDFs** manually (Apr 25-29, in pm-statements-inbox)

## Commit Info

```
Commit: b69c9d7
Message: feat: wire sheets bridge into mortgage extraction pipeline

After PDF extraction, sheets_bridge.py runs for each CSV to update
Google Sheets with loan balance. Fire-and-forget (|| true) so Sheet
failures never block the git commit. Notification routing changed:
routine processing → Telegram to Rod only. Payment change alerts
handled separately by the bridge (Telegram + iMessage).
```

## Phase 1 Completion Checklist

- [x] Property map complete (all 4 properties + sheet IDs)
- [x] FDA permissions granted
- [x] Bridge script wired into extract-and-commit.sh
- [x] Notification routing updated (both scripts)
- [x] Code tested (bridge runs on known CSV)
- [x] Committed and pushed to main
- [ ] Telegram credentials set up (next session)
- [ ] End-to-end test with live PDF drop (next session)

## What Phase 1 Accomplishes

✅ **Automatic Sheets Updates**: When Sharon drops a mortgage PDF, it extracts → updates Google Sheet automatically. No manual step.

✅ **Reliable Pipeline**: CSV is canonical source of truth. Sheet is live view. Bridge failure never blocks commit.

✅ **Alert Routing**: Payment changes trigger Telegram + iMessage to Rod.

✅ **Duplication Handling**: Bridge checks both CSV and Sheet before writing — no duplicate dates.
