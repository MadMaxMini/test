# From: Life Coach
# To: Mad Max
# Date: 2026-04-15
# Re: System fixes identified this session — 3 items

## 1. Today.py → Mac Mini Cron

**Problem:** Today.py runs as an iPhone Shortcut. It fires inconsistently — last auto-drop was Apr 13, nothing Apr 14 or 15 until Rod manually ran it. May require a "Done" tap to complete.

**Fix:** Move Today.py to Mac mini as a cron/launchd job (like the Whisper transcription job). Should run daily at ~5:30am, drop the calendar text to `~/Dropbox/claude-drops/`. No human tap needed.

**Priority:** MEDIUM — Rod can manually run it, but automation is the goal.

## 2. Status File Staleness — Coach Update Reliability

**Problem:** Status files go stale because coaches only update them when Rod explicitly invokes `/coach-name`. If Rod does work-related things without invoking Work Coach, the status file doesn't get refreshed.

**What we learned:** Faith Coach is 41 days stale. Health 15 days. Work 7 days. Even coaches Rod uses often (health, work, recruiting) drift because not every session ends with a proper status write.

**Fix options (Rod to decide):**
- Option A: Each coach SKILL.md already says "update status at session end" — verify this is actually in every SKILL.md and enforce it
- Option B: A lightweight cron on Mac mini that checks status file dates and sends Dropbox notifications when any are >2 days stale
- Option C: Life Coach always sends nudges at session start (already doing this manually — could automate)

**Priority:** HIGH — Rod said "this is one of your most important jobs" about the status dashboard.

## 3. Faith Coach — Notification vs. Conversation Gap

**Problem:** Faith Coach sends notifications 2x/week from Mac mini (working). But there are no conversation sessions happening, so the status file is frozen at Mar 4 (Lent). Notifications are output-only — no coaching, no status updates.

**Fix:** This is more of a workflow question than a build. Rod should decide:
- Does Faith Coach auto-update status when it sends notifications? (requires the notification script to also write status)
- Or does Rod do a quick weekly `/faith-coach` check-in to keep the coaching + status alive?

**Priority:** LOW-MEDIUM — notifications are working, status is the gap.
