# Proposal: Mad Max Skill Tweaks

**Status:** Draft — discuss with Rod before editing skill file

## What's Missing

### 1. Working software before infrastructure

The skill says "bias toward doing" but doesn't say doing *what first*.
Result: 6 sessions of scaffolding before a single model ran.
The mini is a sophisticated empty box.

Fix: add a principle — **don't build infrastructure for something that doesn't exist yet.**
Get the payoff first (model running, talking to it), then layer in the scaffolding.

### 2. Phase awareness

The skill has no sense of "where are we in the build?"
Mad Max should load current phase at session start and not get ahead of it.

Suggested phases:
- Phase 0: Core working (model running, API responding) ← WE ARE HERE
- Phase 1: Secrets + vault operational
- Phase 2: Coach agents running on local AI
- Phase 3: Async ops (notifications, mailbox, n8n)

### 3. Permission wall handling

When Mad Max hits a sudo blocker, current behavior: note it and move on.
Better behavior: batch all sudo-required actions, surface them as a single
clean block for Rod to run, then continue. Don't let one sudo blocker
stall the whole session.

### 4. iMessage as first-class infrastructure

Notifications aren't Phase 3 optional. They're what makes the mini useful async.
Should be treated like OpenBao — establish early, everything else builds on it.

### 5. iMessage vs Dropbox communication rule

iMessage = one text, 2-4 lines per item, everything in one message.
Dropbox = only if there's reference material worth going back to.
Never split one message into multiple texts. Never use Dropbox as a longer version of a text.

## What NOT to Change

- Session start/end ceremony (load files, log, commit, push) — this is working
- Routing table — correct
- Decision log pattern — useful
- Mini vs laptop mode split — correct
