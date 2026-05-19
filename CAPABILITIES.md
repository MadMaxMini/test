# Mad Max Capabilities — Live (2026-05-19)

This document tracks what's actually running and verified. Updated as features ship.

---

## Telegram Commands (Read-Only Stage B)

All commands available in direct 1-on-1 chat with `@madmax_mini_bot`. Group chat has same commands but different SOUL (honest about capabilities).

### Inbox Sweep

| Command | Output | Notes |
|---------|--------|-------|
| `/sweep` | 📬 bottleMsg items (13 items) + 📧 recent emails (last 10 of 74) | Saves browse state — `/read N` works after |
| `/inbox` | Quick count: `📬 13 items \| 📧 74 entries` | Real-time |
| `/email` | Last 10 emails with tier icons 🔴🟡🔵⚪ | Newest first (file is append-only) |
| `/email 25` | Last 25 emails (configurable up to 50) | For catching up on older batch |
| `/email pending` | Debounce batch contents sorted by urgency | Empty when batch hasn't fired |

### File Reading (Browse)

| Command | Output | Notes |
|---------|--------|-------|
| `/read 1` | Full content of bottleMsg item #1 from last `/sweep` | Works after `/sweep`, `/digest`, `/dig` |
| `/read filename` | Search and read by partial filename match | Searches digest/, inbox/, archive/ |
| `/digest [N\|today\|topic]` | List digest folder (learning material) | Uses browse state for `/read N` |
| `/dig keyword` | Search digest + inbox for keyword | Uses browse state for `/read N` |

### Other (Pre-Existing, Still Live)

| Command | What |
|---------|------|
| `/status` | Ollama + Docker + Vault health |
| `/models` | List Ollama models loaded |
| `/ping` | Alive check |
| `/queue` | Night planner task queue |
| `/go 1` / `/go all` | Approve and run tasks from queue |
| `/gtd` | Trigger GTD sweep |
| `/model X` | Switch active model (default/mistral/claude/gemma) |

---

## Behind-the-Scenes

### Daemon Status
- **email-poller** (LaunchAgent `com.dakotaops.emailpoller`): Gmail IMAP → classification → debounce → Telegram notify
  - Runs every 5 min, logs to `~/Work/local/scripts/email-poller.log`
  - Classifies emails into 4 tiers: 🔴 urgent, 🟡 important, 🔵 info, ⚪ noise
  - 15-min debounce window (urgent breaks it immediately)
  - Notifies via Telegram Max bot → Rod's direct chat

- **telegram-poller** (LaunchAgent `com.madmax.telegrampoller`): Long-polls Telegram, dispatches to dispatcher.py
  - Runs continuously, logs to `~/Work/local/scripts/telegram-poller.log`
  - Loads dispatcher.py on startup (reload requires restart)
  - Context="telegram" uses SOUL-telegram.md (honest about what it can do)
  - Chunks messages via `tg_send_chunked` (~4000 chars per chunk)

### Data Files
- `~/Work/local/scripts/email-inbox.md` — append-only log of all classified emails, one entry per line
  - Format: `- [TIMESTAMP] TIER_ICON uid=N [tier_name] | SENDER | SUBJECT`
  - Oldest at top, newest at bottom
  - `/email` shows last N (newest) entries
  - `/sweep` shows last 10

- `~/Work/local/scripts/email-batch.json` — pending debounce batch (temporary)
  - Format: `{"items": [...], "started": unix_timestamp}`
  - Each item: `{"classification": {...}, "sender": "...", "subject": "..."}`
  - Flushed every 15 min or on urgent email
  - `/email pending` reads this

- `~/Work/test/backlog.md` — task backlog (P0/P1/P2/P3)
  - Read-only in Telegram context
  - Updated via Claude Code sessions

- `~/Library/CloudStorage/Dropbox/bottleMsg/` — async inbox for Rod
  - Root items are actionable (inbox)
  - `digest/` = reading material
  - `archive/` = processed (with ARCHIVE.md manifest)
  - `/sweep` lists root items numbered 1-N
  - `/read N` retrieves item

---

## Testing Instructions

### Quick Smoke Test (5 min)

1. **Open Telegram** on your phone, go to `@madmax_mini_bot` direct chat
2. **Send** `/inbox` → should see count of bottleMsg items + emails
3. **Send** `/sweep` → should see formatted list with emojis
4. **Check response** — verify:
   - bottleMsg items numbered 1-13
   - emoji types (📝 for md files, 📸 screenshots, etc.)
   - ages in human format (e.g., "4d" for 4 days)
   - ⏰ markers on items >48h old
   - recent email list at bottom (last 10)

### Browse State Test (5 min)

1. **After** `/sweep` completes, **send** `/read 1` → should return the first bottleMsg item (2026-05-11-30-day-no-build-pact.md)
2. **Try** `/read 5` → should return item #5
3. **Try** `/read 99` → should error: "Item 99 not in browse list (have 13)"
4. **Verify:** browse state works and persists across messages

### Email Commands (5 min)

1. **Send** `/email` → last 10 emails with tier icons
2. **Send** `/email 20` → last 20 emails
3. **Verify:** most recent emails appear first (May 19 at top)
4. **Check icons:** 🔴 urgent, 🟡 important, 🔵 info should be visible
5. **Send** `/email pending` → should say "empty" (or show batch if one is queued)

### PDF Reading (5 min, if you have a PDF in bottleMsg)

1. **Upload** a PDF to `~/Library/CloudStorage/Dropbox/bottleMsg/` (e.g., a mortgage statement)
2. **Run** `/sweep` → PDF should appear as `📄 filename.pdf`
3. **Send** `/read N` where N is the PDF's number → should show first 5 pages
4. **Verify:** text extraction works (may vary by PDF quality)

### Monitoring

**Check for errors:**
```bash
# Email poller
tail -20 ~/Work/local/scripts/email-poller.log | grep -i error

# Telegram poller
tail -20 ~/Work/local/scripts/telegram-poller.log | grep -i error
```

**Verify daemons are running:**
```bash
launchctl list | grep -E "dakotaops.email|madmax.telegram"
# Should show two entries with PID numbers (not -)
```

**Simulate an email** (test the poller):
- This is scripted in the poller but requires IMAP access
- For now, just monitor logs after real emails arrive in your inbox

---

## Known Limitations (Stage B)

- **No file actions via Telegram** — can only read, not archive/move/delete
  - Use Claude Code sessions or GTD sweep for file ops
- **PDF reading is first 5 pages only** — limit to prevent huge messages
  - Full PDF requires Claude Code session with pdfplumber
- **No screenshots inline** — bot says "screenshot, can't read inline, open in Dropbox"
  - Vision model support deferred to Stage C
- **Audio transcription not wired** — .m4a/.mp3 files show but can't read
  - Needs mlx-whisper integration (deferred)
- **Browse state is per-session** — resets if telegram-poller restarts
  - File listings shown before `/read` still work (fallback by filename)

---

## What's Not Implemented Yet (Stage C+)

- `/archive 1` — move item to archive/ (requires file ops + safety)
- `/backlog P2 item description` — add to backlog (state-changing)
- `/route 1 health-coach` — copy to coach inbox (multi-user context)
- GTD sweep state machine (multi-message conversation tracking)
- Proactive nudges (scheduled morning brief, aged-item reminders)
- Audio transcription, screenshot OCR, email reply generation

---

## Configuration

All settings are in `dispatcher.py`:
- Email tiers and contact list: `email_classifier.py` (portable, copies to dakota-software later)
- Telegram chunking limit: `tg_send_chunked(...)` in telegram-poller.py (~4000 chars)
- PDF page limit: `pdf.pages[:5]` in `_read_pdf()` (easy to adjust)
- Email count defaults: `/email` → last 10, `/sweep` → last 10 emails (configurable via args)
- Debounce window: 15 minutes, urgent breaks immediately (email-poller.py line 44)

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Commands not responding | `launchctl list \| grep telegram` — is PID live? |
| Emoji render as `?` | Terminal font issue (Telegram app itself should show them) |
| `/email` shows "no emails logged yet" | Check `email-inbox.md` exists and has entries |
| `/read` says "no active browse list" | Run `/sweep` or `/digest` first to create browse state |
| PDF reading fails silently | Check pdfplumber venv exists: `ls ~/Work/dakota-software/bot/pdf-extractor/venv/bin/python3` |
| Poller crashed | Check logs for timeout/exception, restart: `launchctl kickstart -k gui/$(id -u)/com.madmax.telegrampoller` |

---

Last updated: 2026-05-19 (Stage B shipped)
