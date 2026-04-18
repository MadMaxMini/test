# Two-Tier Telegram Dispatch

**Status:** Proposal — needs Rod's review before building
**Date:** 2026-04-18
**Author:** Mad Max

---

## Problem

AutoDakota's Telegram poller currently handles every message the same way: send it to Claude with context, return the response. But messages range from "what's Sharon's status?" (5-second lookup) to "restructure the task files and push" (multi-minute skill invocation with file writes). The single-tier model means:

1. Quick questions wait behind expensive operations
2. The bot can't safely do write operations without a different permission model
3. No way to route messages to other skills (Health Coach, Mad Max) from one chat

## Proposed Architecture

### Tier 1: Quick Response (current behavior, tightened)

- **What:** Read-only lookups, status checks, simple Q&A
- **How:** Current poller sends message to Claude API with SYSTEM.md context
- **Latency:** < 10 seconds
- **Permissions:** Read-only. No file writes, no git, no shell commands.
- **Examples:** "What's overdue?" / "Who owns the Plaid task?" / "Summarize today's standup"

### Tier 2: Skill Invocation (new)

- **What:** Multi-step operations that require file access, git, or cross-repo work
- **How:** Poller detects a "big ask" and spawns `claude --cwd /path/to/repo` with the appropriate skill
- **Latency:** 30s–5min (async — bot sends "Working on it..." immediately, delivers result when done)
- **Permissions:** Full skill permissions (per CLAUDE.md of target repo)
- **Examples:** "Add a task for Sharon and commit" / "Run the standup prep" / "Check health coach logs"

## Detection: Big Ask vs Quick Question

### Explicit keyword triggers (highest priority)

| Trigger | Action | Target Repo |
|---------|--------|-------------|
| `+do` | Invoke AutoDakota skill (full permissions) | `~/Work/dakota-software` |
| `+coach` | Route to Health Coach skill | `~/Work/coaches/health-coach` |
| `+max` | Route to Mad Max skill | `~/Work/test` |
| `+task` | Write task via TASK tag (existing behavior) | `~/Work/dakota-software` |

### Auto-detection (fallback, conservative)

If no keyword trigger, classify by heuristics:

1. **Verb analysis:** "add", "create", "update", "commit", "push", "write", "delete", "restructure" → likely Tier 2
2. **Length:** Messages > 200 chars are more likely complex requests
3. **Multi-step indicators:** "and then", "after that", numbered lists → Tier 2
4. **Default:** If uncertain, stay Tier 1. False-negative (doing less) is safer than false-positive (doing more).

### Confirmation for Tier 2

Before executing Tier 2, the bot should:
1. Echo back what it understood: "I'll add a task for Sharon to check the CD spreadsheet, commit, and push. Go?"
2. Wait for Rod's confirmation (any affirmative) before spawning the skill
3. Send "Working on it..." once confirmed
4. Deliver the result (or error) when the skill completes

## Security Implications

### Write access risks

| Risk | Mitigation |
|------|------------|
| Bot commits bad code to git | Tier 2 always requires explicit `+do` or confirmation |
| Prompt injection via Telegram message | SYSTEM.md already constrains behavior; Tier 2 adds confirmation gate |
| Cross-repo access (health coach reading dakota data) | Each skill invocation uses `--cwd` to the target repo; skill boundaries enforce isolation |
| Runaway skill (hangs or loops) | Timeout on skill invocation (5min max), kill and report |
| Telegram token compromise | Tokens in Keychain, not env vars; bot only responds to Rod's chat_id |

### Principle: Rod is the gate

No Tier 2 action fires without Rod saying "go" (either via `+do` keyword or confirmation reply). The bot proposes, Rod disposes. This matches the existing CAN/CANNOT model.

### What this does NOT solve

- **Multi-user:** Only Rod's chat_id is authorized. Team members can't trigger actions.
- **Scheduling:** This is real-time dispatch only. Cron-based work stays in LaunchAgents.
- **Cross-bot routing in a single message:** "check health and update dakota" would need to be split. Start with one skill per message.

## Implementation Notes (for when Rod approves)

1. Add a `classify_message(text)` function to `telegram-poller.py` that returns `{tier: 1|2, target_repo: str, skill: str}`
2. For Tier 2: use `subprocess.run(["claude", "--cwd", repo, "-p", message])` with timeout
3. Add a "pending confirmation" state to the poller so it can wait for Rod's yes/no
4. Log all Tier 2 invocations to `bot/logs/tier2-dispatch.log` for audit
5. Backport claim detection to Health Coach and Mad Max pollers first (they need it before getting write access)

## Open Questions for Rod

1. **Confirmation always, or trust keywords?** Should `+do close the CD task` just execute, or still confirm?
2. **Timeout:** 5 minutes reasonable for skill invocations?
3. **Cross-bot:** Should `+coach` from AutoDakota's chat actually invoke Health Coach, or should Rod use the Health Coach bot directly?
4. **Priority:** Build this now, or focus on claim detection for the other two bots first?
