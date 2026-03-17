# Proposal: iMessage Notifications

**Status:** Done — 2026-03-17

## Why

iMessage is the right notification channel. AppleScript native, no third party,
rock solid once wired. Lets mini notify Rod async: model pull done, job finished,
needs attention. Without it, mini is silent until Rod opens a session.

Preference order: iMessage > Signal > Email
(ease of setup is backwards from ongoing value — iMessage wins long-term)

## What's Blocking It

1. `macbotpooterson@gmail.com` Apple ID not signed into mini yet
   - System Settings → Apple ID → sign in
   - 2FA will ping Rod's T-Mobile number
2. Messages app: enable iMessage after Apple ID is signed in
3. That's it.

## Once Wired

AppleScript send is trivial:
```applescript
tell application "Messages"
  send "message here" to buddy "+1RODNUMBER" of service "iMessage"
end tell
```

Mad Max wraps this in a notify.sh — one-liner to send from any script.

## Action

Rod sits at mini, signs in Apple ID, enables Messages.
Mad Max writes notify.sh immediately after.
