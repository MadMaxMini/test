# Telegram Ops — How-To Reference

Read this file when doing Telegram setup tasks. Not every session.

---

## What I can do via Telegram.app on this machine

- Open Telegram.app and navigate to any chat
- Drive BotFather to register new bots
- Read tokens from the screen (screenshots + zoom)
- Get chat_ids via curl after user messages the bot
- Send messages, set bot descriptions/commands

Telegram.app is at `/Applications/Telegram.app`. Rod's account is already logged in.

---

## Registering a new bot via BotFather

```python
# 1. Open Telegram and search BotFather
import subprocess

subprocess.run(['open', '-a', 'Telegram'])
# wait ~2s for app to focus

# 2. Drive via AppleScript
osascript_steps = [
    # Open search / jump to chat
    'tell application "System Events" to tell process "Telegram" to keystroke "k" using command down',
    # Type BotFather
    'tell application "System Events" to tell process "Telegram" to keystroke "BotFather"',
    # Select and open
    'tell application "System Events" to tell process "Telegram" to key code 36',
    # Send /newbot
    'tell application "System Events" to tell process "Telegram" to keystroke "/newbot"',
    'tell application "System Events" to tell process "Telegram" to key code 36',
]
for step in osascript_steps:
    subprocess.run(['osascript', '-e', step])
    time.sleep(1)
```

Or as bash one-liners (easier to run step by step):
```bash
open -a Telegram && sleep 2

# Open search
osascript -e 'tell application "System Events" to tell process "Telegram" to keystroke "k" using command down'
sleep 1

# Type BotFather
osascript -e 'tell application "System Events" to tell process "Telegram" to keystroke "BotFather"'
sleep 2

# Enter to open chat
osascript -e 'tell application "System Events" to tell process "Telegram" to key code 36'
sleep 1

# Send /newbot
osascript -e 'tell application "System Events" to tell process "Telegram" to keystroke "/newbot"'
osascript -e 'tell application "System Events" to tell process "Telegram" to key code 36'
sleep 2
```

BotFather will ask: **name** then **username** (must end in `bot`).

Type each response:
```bash
osascript -e 'tell application "System Events" to tell process "Telegram" to keystroke "Bot Name Here"'
osascript -e 'tell application "System Events" to tell process "Telegram" to key code 36'
sleep 2

osascript -e 'tell application "System Events" to tell process "Telegram" to keystroke "bot_username_here"'
osascript -e 'tell application "System Events" to tell process "Telegram" to key code 36'
```

---

## Reading the token from the screen

Take a series of screenshots zooming into the BotFather response:

```bash
# Full window
screencapture -x /tmp/tg-state.png

# Zoom into BotFather chat panel (right side ~x=1050-1750, adjust to display)
screencapture -x -R "1050,400,700,500" /tmp/tg-zoom.png

# Zoom into token line specifically
screencapture -x -R "1100,620,650,120" /tmp/tg-token.png
```

Use `Read` tool on each screenshot image to visually parse the token.

**Token format:** `<10-digit-number>:AAE<base64-string>` (about 46 chars total)

If the token wraps across lines in the screenshot, zoom in on each line separately and concatenate.

**Validate immediately:**
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
# Should return {"ok":true,"result":{"username":"your_bot_username",...}}
```

---

## Getting Rod's chat_id

After bot is created, Rod needs to message the bot once (from his phone or the Telegram app):

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for u in d.get('result', []):
    msg = u.get('message', {})
    print('chat_id:', msg.get('chat', {}).get('id'))
    print('text:', msg.get('text', ''))
"
```

If no updates: Rod hasn't messaged the bot yet. Wait and retry.

---

## Storing credentials

**Always store in both Keychain (runtime) and OpenBao (canonical).**

```bash
# Keychain
security add-generic-password -a macBot -s "telegram-<botname>-bot-token" -w "<TOKEN>"
security add-generic-password -a macBot -s "telegram-<botname>-chat-id" -w "<CHAT_ID>"

# OpenBao (requires unsealed vault)
vault kv put secret/telegram/<botname> token="<TOKEN>" chat_id="<CHAT_ID>"
# or via curl if vault CLI not in path:
curl -s -H "X-Vault-Token: $(security find-generic-password -a macBot -s openbao-root-token -w)" \
  -X POST -d "{\"data\":{\"token\":\"<TOKEN>\",\"chat_id\":\"<CHAT_ID>\"}}" \
  http://127.0.0.1:8200/v1/secret/data/telegram/<botname>
```

Verify Keychain:
```bash
security find-generic-password -a macBot -s "telegram-<botname>-bot-token" -w
```

---

## Keychain naming convention

| Bot | Token key | Chat ID key |
|-----|-----------|-------------|
| Mad Max | `telegram-max-bot-token` | `telegram-max-chat-id` |
| Health Coach | `telegram-health-bot-token` | `telegram-health-chat-id` |
| AutoDakota | `telegram-bot-token` | `telegram-chat-id` |

---

## Loading a LaunchAgent poller

```bash
# Copy plist to LaunchAgents
cp ~/Work/<repo>/bot/com.<label>.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/com.<label>.plist

# Verify running
launchctl list | grep <label>

# Check logs
tail -f ~/Work/<repo>/bot/logs/telegram-poller.log
```

---

## Navigating Telegram.app — notes

- `Cmd+K` opens the jump-to-chat search
- `Enter` (key code 36) confirms selection or sends a message
- The chat panel is on the right side of the window (~x=1050+ at 1920px width)
- Screenshots: use `-R "x,y,width,height"` with `screencapture -x` to isolate the panel
- `cliclick` (homebrew) is available for right-clicking: `cliclick rc:x,y`
- If Telegram loses focus mid-script: add `tell application "Telegram" to activate` before keystrokes

---

## Bots currently registered (as of 2026-04-16)

| Bot | Username | Keychain token key | Keychain chat_id key |
|-----|----------|--------------------|----------------------|
| Mad Max | @madmax_mini_bot | `telegram-max-bot-token` | `telegram-max-chat-id` |
| Health Coach | @healthcoach_rod_bot | `telegram-health-bot-token` | `telegram-health-chat-id` |
| AutoDakota | @autodakota_mini_bot (pending) | `telegram-bot-token` | `telegram-chat-id` |
