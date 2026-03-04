# Proposal: Mailbox Architecture for Inter-Agent Communication

**Date:** 2026-03-04
**Status:** Pending Rod's decision
**Context:** Raised during OpenBao init session — need to decide before running setup-mailbox.sh

---

## The Question

Where do agent mailboxes live, and how does routing work?

Current `setup-mailbox.sh` centralizes everything under `~/Work/test/coaches/` — written before the separate-repo-per-agent pattern was decided. That script is **on hold** pending this decision.

---

## Options

### Option A — Hub (current script behavior)
```
~/Work/test/coaches/
  mad-max/inbox   outbox   workspace
  recruiting/inbox   outbox   workspace
  life-coach/inbox   outbox   workspace
```
- Simple, one repo, one git history
- All inter-agent traffic auditable in one place
- **Problem:** recruiting-coach has a hidden dependency on madmax repo path — breaks self-encapsulation

### Option B — Distributed + Mad-Max Routing Registry (recommended)
```
~/Work/recruiting-coach/mailbox/inbox    outbox   ← agent owns this
~/Work/life-coach/mailbox/inbox    outbox
~/Work/test/mailbox/inbox    outbox               ← mad-max's own

~/Work/test/routing.yml                           ← mad-max knows the map
  recruiting: ~/Work/recruiting-coach/mailbox
  life-coach: ~/Work/life-coach/mailbox
  mad-max: ~/Work/test/mailbox
```
- Full self-encapsulation — each agent repo is a complete deployable unit
- Security isolation — breach of one agent doesn't expose others
- Mad-max as postman: reads routing.yml, writes to correct path, agents don't need to know each other's locations
- Clean n8n integration — each agent repo has its own watcher
- **Cost:** slightly more setup; routing.yml must be kept current

### Option C — Pure Hub, Encrypted
Same as A but all messages encrypted with shared Transit key.
- Fixes the content exposure risk but not metadata (who talks to who, when)
- Still breaks self-encapsulation

---

## Tradeoff Summary

| Dimension | Hub (A) | Distributed+Registry (B) |
|-----------|---------|--------------------------|
| Self-encapsulation | ❌ | ✅ |
| Security isolation | ❌ | ✅ |
| Simplicity now | ✅ | ✓ (small cost) |
| Auditability | ✅ | ✓ (split across repos) |
| n8n integration | simpler | cleaner long-term |
| Invocability | works | works, more autonomous |

---

## Recommendation

**Option B.** Mad-max owns the routing registry, agents own their mailboxes. Mailbox creation becomes part of the agent repo setup pattern — every new agent repo gets `mailbox/inbox` and `mailbox/outbox` on init, and mad-max's `routing.yml` gets a new entry.

`setup-mailbox.sh` needs to be rewritten to:
1. Create only mad-max's own `mailbox/inbox` + `mailbox/outbox`
2. Create `routing.yml` with known agent paths
3. (Each agent repo handles its own mailbox on setup)

---

## What's Blocked

- `setup-mailbox.sh` — do not run until this is decided
- recruiting-coach mailbox setup — pending this decision
- Agent repo setup template — should include mailbox creation

---

*Discussed: 2026-03-04 mini session 4*
