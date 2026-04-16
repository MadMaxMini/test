# Telegram Bots — Setup Guide
*Written 2026-04-16. All code is done. Just need credentials + LaunchAgent load.*

---

## What was built

| Bot | Keychain keys | Interactive | Daily push |
|-----|--------------|-------------|------------|
| Health Coach | `telegram-health-bot-token`, `telegram-health-chat-id` | Yes — ask questions, log weight | 6am nudge + 6:30pm check-in |
| AutoDakota | `telegram-bot-token`, `telegram-chat-id` | Yes — query tasks, digest | 7am standup (already wired) |
| Mad Max | `telegram-max-bot-token`, `telegram-max-chat-id` | Already live | Night planner |

---

## Step 1 — Register with BotFather (phone, ~10 min total)

Open Telegram → search **@BotFather** → `/newbot`

### Health Coach bot
- Name: `Health Coach`
- Username: `healthcoach_rod_bot` (or whatever BotFather accepts ending in `bot`)
- Copy the token

### AutoDakota bot
- Name: `AutoDakota`
- Username: `autodakota_mini_bot` (or `autodakotabot` if available)
- Copy the token

---

## Step 2 — Get your chat_id for each bot

For each new bot, message it **anything** from your phone, then run on the mini:

```bash
# Health Coach
curl -s "https://api.telegram.org/bot<HEALTH_TOKEN>/getUpdates" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for u in d.get('result',[]): print(u['message']['chat']['id'], u['message']['text'][:20])
"

# AutoDakota
curl -s "https://api.telegram.org/bot<DAKOTA_TOKEN>/getUpdates" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for u in d.get('result',[]): print(u['message']['chat']['id'], u['message']['text'][:20])
"
```

---

## Step 3 — Store credentials in Keychain (mini terminal)

```bash
# Health Coach
security add-generic-password -a macBot -s "telegram-health-bot-token" -w "PASTE_TOKEN"
security add-generic-password -a macBot -s "telegram-health-chat-id" -w "PASTE_CHAT_ID"

# AutoDakota (if not already set from previous setup)
security add-generic-password -a macBot -s "telegram-bot-token" -w "PASTE_TOKEN"
security add-generic-password -a macBot -s "telegram-chat-id" -w "PASTE_CHAT_ID"
```

Verify:
```bash
security find-generic-password -a macBot -s "telegram-health-bot-token" -w
security find-generic-password -a macBot -s "telegram-bot-token" -w
```

---

## Step 4 — Test send (before starting pollers)

```bash
# Health Coach send test
cd ~/Work/coaches/health-coach/office/bot
python3 -c "
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('tg', 'telegram_notify.py')
tg = importlib.util.module_from_spec(spec); spec.loader.exec_module(tg)
print('configured:', tg.is_configured())
print('sent:', tg.send('Health Coach test — Telegram is live'))
"

# AutoDakota send test
cd ~/Work/dakota-software/bot
python3 -c "
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('tg', 'telegram_notify.py')
tg = importlib.util.module_from_spec(spec); spec.loader.exec_module(tg)
print('configured:', tg.is_configured())
print('sent:', tg.send('AutoDakota test — Telegram is live'))
"
```

---

## Step 5 — Start the interactive pollers (LaunchAgents)

```bash
# Health Coach poller
cp ~/Work/coaches/health-coach/office/bot/com.healthcoach.telegrampoller.plist \
   ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.healthcoach.telegrampoller.plist

# AutoDakota poller
cp ~/Work/dakota-software/bot/com.dakotaops.telegrampoller.plist \
   ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dakotaops.telegrampoller.plist

# Verify both running
launchctl list | grep -E "healthcoach|dakotaops"
```

---

## Step 6 — Test interactive mode

Send each bot a message from your phone:
- Health Coach: `how am I doing?`
- AutoDakota: `what's overdue?`

Both should reply within ~10 seconds.

---

## What each bot does

### Health Coach
- **6am**: AI-generated morning nudge based on GOALS.md + log.md
- **6:30pm**: Evening check-in (was broken — now fixed, uses Telegram)
- **Interactive**: ask questions, `log weight 182`, `show goals`, `+reset` to clear context

### AutoDakota
- **7am**: Daily standup digest → Telegram channel (already working via scan.py)
- **Interactive**: `what's overdue?`, `what's Devon working on?`, `generate digest`, `+reset`

---

## Log locations

| Bot | Log |
|-----|-----|
| Health Coach poller | `~/Work/coaches/health-coach/office/bot/logs/telegram-poller.log` |
| Health Coach 6am | `~/Work/coaches/health-coach/office/bot/logs/daily-nudge.log` |
| Health Coach 6:30pm | `~/Work/coaches/health-coach/office/bot/logs/daily.log` |
| AutoDakota poller | `~/Work/dakota-software/bot/logs/telegram-poller.log` |

---

## Inline commands (both bots)

- `+reset` — clear conversation history for this chat
- Health Coach only: `log weight [number]` — appends to weight-log.md

---

## Note on the 6:30pm fix

`daily.py` previously used AppleScript → timed out when screen locked.
Now: Telegram primary → iMessage fallback. No AppleScript dependency.
Screen state is irrelevant. Both 6am and 6:30pm bots now use this pattern.
