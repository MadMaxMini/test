# Intake Notes


## 2026-04-25 - Local AI Fallback — Assessment & Options
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Local AI Fallback — Assessment & Options

**Date:** 2026-04-19
**Context:** Manager Coach bot went live on Telegram today. Rod tested it, bot "knew nada" — likely hit the Ollama fallback path instead of Claude, and the local model couldn't handle the coaching context.

---

## The Problem

All 5 Telegram bots use the same dispatch pattern:
1. Try Claude CLI (`claude -p`) — works great, full context absorbed
2. If Claude fails → try Ollama (mistral-small, then llama3.2:3b) — this is where it breaks

The Ollama fallback gets the same prompt as Claude: SOUL.md (full Manager Tools methodology + Sharon's 4000-char profile + phrasing guide) + session history + the user message. That's easily 6000+ tokens of system context.

**mistral-small (24B):** Can technically handle the context window, but `num_predict: 250` caps the response short. More importantly, it doesn't reason well enough over dense coaching context to give useful advice. It'll parrot back generic management platitudes instead of referencing Sharon's specific patterns.

**llama3.2:3b:** Way too small. Drowns in the context. Basically useless for this.

---

## Options

### Option A: Kill the fallback
- Bot says "Coach is offline, try later" when Claude is down
- **Pro:** No bad advice. Honest. Zero maintenance.
- **Con:** Bot goes dark if Claude CLI has issues (rate limits, extension updates, etc.)

### Option B: Slim prompt for Ollama
- Strip the Ollama prompt to bare minimum: just the phrasing guide + last 3 messages
- Drop Sharon's full profile, drop methodology, drop open items
- **Pro:** Ollama can handle a small prompt well. Basic coaching still works.
- **Con:** Loses the thing that makes this bot valuable — the deep context.

### Option C: Tier the models smarter
- Use mistral-small ONLY (drop 3b entirely)
- Increase `num_predict` to 400-500
- Engineer a compressed prompt specifically for Ollama (separate from Claude's full prompt)
- **Pro:** Best of both — local model gets context it can handle, responses are useful
- **Con:** Maintenance of two prompt paths per bot

### Option D: Dedicated coaching model via LoRA
- Fine-tune a model on Rod's actual coaching conversations
- P4/future — needs data collection first
- **Pro:** Would actually understand the domain
- **Con:** Far out, needs infrastructure (model-lab P3)

---

## My Recommendation

**Option A for now, Option C as P2.**

Coaching bots are high-stakes — bad advice is worse than no advice. Kill the fallback, keep the bots Claude-only. When Claude is reliably available (which it usually is), this costs nothing.

Then as a P2, build the compressed-prompt path for mistral-small so there's a real fallback that actually works. This would also benefit all 5 bots, not just manager-coach.

---

## Rod decides. Subagent standing by to execute.


## 2026-04-25 - Message Routing Fix — Context Doc for New Agent
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Message Routing Fix — Context Doc for New Agent

*Written 2026-04-19 by Max 1. Rod wants a fresh agent to fix this properly.*

---

## The Problem

Mad Max (and scripts running on the mini) keep sending messages to the wrong group/channel. This has happened multiple times and Rod is done with it.

**Most recent incident (today):** Rod said "text me updates on tele" (meaning his personal Telegram). Max 1 sent it via `AutoMax_Notify_JacobAndRod` (iMessage shortcut to Jacob + Rod). Wrong channel, wrong people. Jacob got a Dakota ops update about Sharon's mortgage statements.

**Previous incident (also today):** `extract-and-commit.sh` used Keychain key `imessage-de-auto-makers` (nonexistent/stale group). Fixed to `imessage-group-dakota`. Stale key deleted from Keychain.

---

## Root Cause

There is no unified "send message" function. Every script and every Claude session invents its own send pattern:
- `extract-and-commit.sh` hardcoded a Keychain key name that didn't exist
- Claude sessions pick whichever Shortcut sounds right by name, often wrong
- Telegram DM vs iMessage shortcut distinction is not enforced anywhere
- There are 5 Telegram bots, 3 iMessage shortcuts, and 1 direct notify.sh — 9 channels total, easy to pick wrong

---

## All Available Channels

### iMessage (via Apple Shortcuts)

| Shortcut | Reaches | Context |
|----------|---------|---------|
| `AutoDakota_Notify_Rod` | Rod only | Dakota ops: alerts, errors, status |
| `AutoDakota_Notify_Group` | Rod + Doc + Devon + Sharon | Dakota ops: team updates, standups |
| `AutoMax_Notify_JacobAndRod` | Jacob + Rod | Platform / Mad Max comms ONLY |

**Invocation pattern (all shortcuts):**
```python
import subprocess
msg_escaped = msg.replace('\\', '\\\\').replace('"', '\\"')
script = f'tell application "Shortcuts Events" to run shortcut "SHORTCUT_NAME" with input {{"{msg_escaped}"}}'
subprocess.run(['osascript', '-e', script])
```

### iMessage (via direct chat ID)

| Keychain key | Who | Format |
|-------------|-----|--------|
| `imessage-group-dakota` | Rod + Doc + Devon + Sharon | chat ID for osascript |
| `notify-recipient` | Rod direct | phone number for notify.sh |

**No other iMessage Keychain keys should exist.** If you find one, it's stale — flag it.

### Telegram (via bot API)

| Bot | Token key | Chat ID key | Who |
|-----|-----------|-------------|-----|
| AutoDakota | `telegram-bot-token` | `telegram-chat-id` | Rod |
| Mad Max | `telegram-max-bot-token` | `telegram-max-chat-id` | Rod |
| Health Coach | `telegram-health-bot-token` | `telegram-health-chat-id` | Rod |
| Elite HH | `telegram-elitehh-bot-token` | `telegram-elitehh-chat-id` | Rod |
| Manager | `telegram-manager-bot-token` | `telegram-manager-chat-id` | Rod |

All Telegram bots DM Rod directly. There are no Telegram group chats.

**Send pattern (stdlib only, no requests needed):**
```python
import urllib.request, json, subprocess

def keychain_get(key):
    r = subprocess.run(["security", "find-generic-password", "-a", "macBot", "-s", key, "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip() or None

token = keychain_get("telegram-max-bot-token")
chat_id = keychain_get("telegram-max-chat-id")
payload = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
urllib.request.urlopen(req, timeout=10)
```

---

## Routing Rules (What Rod Wants)

| Rod says | Channel | How |
|----------|---------|-----|
| "tele" / "telegram" / "text me on tele" | Telegram DM | Use the bot matching current context (Max bot for Max sessions, AutoDakota bot for Dakota sessions) |
| "text the group" / "notify the group" (dakota context) | iMessage | `AutoDakota_Notify_Group` shortcut |
| "text me" (dakota context) | iMessage | `AutoDakota_Notify_Rod` shortcut |
| "text jacob" / platform stuff | iMessage | `AutoMax_Notify_JacobAndRod` shortcut |
| "notify sharon" or a pipeline notification | iMessage | `AutoDakota_Notify_Group` or direct (TBD) |

**Critical rules:**
- Dakota context → `AutoDakota_*` shortcuts. NEVER `AutoMax_*`.
- `AutoMax_Notify_JacobAndRod` → Jacob sees it. Only use for platform/Jacob context.
- "tele" always means Telegram, never iMessage.
- When in doubt → ASK before sending.

---

## What Needs to Be Built

### 1. A single `send_message()` helper (highest priority)

Something like `~/Work/local/scripts/send.py` (or `send.sh`) that every script and Claude session can call:

```bash
# Examples of desired interface:
send.py --channel dakota-group "Standup posted"
send.py --channel rod-telegram "Session summary..."  
send.py --channel rod-direct "Alert: extraction failed"
send.py --channel jacob "Platform update"
```

The helper:
- Maps channel names to the correct mechanism (shortcut vs telegram API vs notify.sh)
- Refuses to send if channel is not recognized (fail loud, not silent)
- Logs every message sent to a central log (`~/Work/local/scripts/logs/messages-sent.log`)
- Is the ONLY way messages get sent — no more inline osascript or raw API calls scattered across scripts

### 2. Update contacts.md

`~/Work/local/scripts/contacts.md` currently only documents iMessage channels. It needs to include ALL channels (Telegram bots, shortcuts, everything) as a single reference.

### 3. Update extract-and-commit.sh

Replace the inline osascript block with a call to the new `send.py` helper.

### 4. Update the mad-max skill

The "Sending Messages / SMS" section in `~/Work/test/.claude/skills/mad-max/skill.md` needs to include Telegram as a channel option and reference the new helper.

### 5. Update memory

`feedback_message_routing.md` at `~/.claude/projects/-Users-macBot-Work-test/memory/feedback_message_routing.md` — update to reference the new helper once built.

---

## Relevant Files

| File | What |
|------|------|
| `~/Work/local/scripts/contacts.md` | Channel documentation (iMessage only currently) |
| `~/Work/local/scripts/notify.sh` | Rod-direct iMessage sender |
| `~/Work/local/scripts/telegram-poller.py` | Max bot — has working `tg_send()` pattern |
| `~/Work/dakota-software/bot/pdf-extractor/extract-and-commit.sh` | Uses iMessage inline (just fixed to correct key) |
| `~/Work/dakota-software/bot/telegram_notify.py` | AutoDakota telegram notify helper |
| `~/Work/test/.claude/skills/mad-max/skill.md` | Mad Max skill — messaging section needs update |
| `~/.claude/projects/-Users-macBot-Work-test/memory/feedback_message_routing.md` | Routing rules memory |

---

## Context: Multiple Max Agents

Rod mentioned "you are Max 1 there are 3 working now." There are multiple Claude sessions running as Mad Max. This makes the unified helper even more important — every agent needs to use the same send path, not invent its own.

---

## Definition of Done

1. `send.py` (or `send.sh`) exists at `~/Work/local/scripts/send.py`
2. Running `send.py --channel invalid "test"` fails with a clear error
3. Running `send.py --channel rod-telegram "test"` sends via Telegram bot API
4. Running `send.py --channel dakota-group "test"` sends via AutoDakota_Notify_Group shortcut
5. `extract-and-commit.sh` uses the new helper instead of inline osascript
6. `contacts.md` documents ALL channels
7. Message log captures every send
8. Rod doesn't get another wrong-group text


## 2026-04-25 - Mem Palace — Implementation Plan
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Mem Palace — Implementation Plan

## Context

**Problem:** Rod's personal info, team data, platform config, and routing rules are duplicated across 6 agent repos (test, health-coach, elite-hh-bot, manager-coach, dakota-software, faith). When facts change (Sharon's number, arm status, a port), only one copy gets updated — the rest drift. Agents can't hand off to each other because no shared routing table exists.

**Solution:** `~/Work/palace/` — a shared read layer. 5 markdown files. Every agent's CLAUDE.md gets a 1-line pointer. Duplicated facts get replaced with the pointer. Single source of truth.

**Prompted by:** Rod's 2026-04-19 Telegram thread + session design work. Bumped from P3 to P0.

---

## Storage Cost Analysis

### Current State (duplicated context loaded per agent invocation)

| Repo | Context files loaded | Bytes of Rod/team/platform info |
|------|---------------------|--------------------------------|
| test (madmax) | CLAUDE.md + SOUL.md + WHO-AM-I.md | ~13,375 |
| health-coach | CLAUDE.md + SOUL.md + GOALS.md | ~5,656 |
| elite-hh-bot | CLAUDE.md + SOUL.md + GOALS.md | ~5,374 |
| manager-coach | CLAUDE.md + SOUL.md + sharon.md | ~15,243 |
| dakota-software | CLAUDE.md + team-directory.md + sharon.md | ~7,016 |
| faith | GOALS.md | ~3,781 |
| **TOTAL across all agents** | | **~50,445 bytes** |

Of that ~50KB, roughly **~15-20KB is duplicated facts** (Rod's identity, team contacts, platform ports, routing) that appear in 3+ places.

### Palace State (after migration)

| Item | Bytes |
|------|-------|
| Palace (5 files, single source) | ~4,000 |
| Per-agent CLAUDE.md pointer line | ~80 each x 6 = ~480 |
| Removed duplication from SOUL/CLAUDE files | -15,000 to -20,000 |
| **Net change** | **~15KB less total context** |

### Token Impact

- ~4 tokens per word, ~5 words per line
- 15KB of removed duplication = ~3,000 fewer tokens loaded per agent invocation
- Palace adds ~800 tokens (shared, loaded once)
- **Net: ~2,200 fewer tokens per agent call** — faster prompt, cheaper if API-billed
- Bigger win: **no drift**. One update propagates to all 6 agents.

---

## Permissions Needed (pre-approved by Rod)

- [x] Create `~/Work/palace/` directory and files
- [x] Edit CLAUDE.md in: test, health-coach, elite-hh-bot, manager-coach, dakota-software
- [x] Edit SOUL.md in: test, health-coach, elite-hh-bot, manager-coach
- [x] Edit faith skill file (fix broken routing.md reference)
- [x] Retire `~/Work/test/WHO-AM-I.md` (replaced by palace/ROD.md + palace/PLATFORM.md)
- [x] Git commit + push all 7 repos (madmax + 5 coaches + dakota-software)
- [x] Update backlog.md (move Mem Palace from P3 to Done)
- [x] Update session-log.md
- [x] Send Telegram/iMessage status to Rod before execution begins

---

## Implementation Chunks

Each chunk is self-contained. If context maxes out, the next session reads this plan + checks which chunks are done (marked with checkboxes below).

### Chunk 1: Create Palace Directory + 5 Files
**Time estimate: ~15 min**
**Deps: none**

- [ ] `mkdir -p ~/Work/palace`
- [ ] `cd ~/Work/palace && git init`
- [ ] Write `ROD.md` — Rod's identity (name, handles, kids, arm status, sleep, mac mini role)
- [ ] Write `TEAM.md` — Dakota team (Doc, Devon, Sharon, Jacob, Gary — roles, contact, GitHub)
- [ ] Write `PLATFORM.md` — services, ports, bindings, stack decisions, model tiers
- [ ] Write `COMMUNICATION.md` — notify.sh, iMessage groups, Telegram bots, Zoom
- [ ] Write `ROUTING.md` — coach office paths, inbox paths, handoff rules table
- [ ] Initial commit: "Mem Palace Phase 1 — shared read layer for all agents"

**Verify:** `ls ~/Work/palace/` shows 5 .md files. `git log` shows initial commit.

### Chunk 2: Wire Mad Max (test repo)
**Time estimate: ~10 min**
**Deps: Chunk 1**

- [ ] Edit `~/Work/test/CLAUDE.md` — add palace pointer, remove duplicated platform config that's now in PLATFORM.md
- [ ] Edit `~/Work/test/SOUL.md` — remove Rod identity facts now in ROD.md, add pointer
- [ ] Retire `~/Work/test/WHO-AM-I.md` — content fully covered by ROD.md + PLATFORM.md (delete or move to archive/)
- [ ] Commit: "Wire Mem Palace pointer, deduplicate CLAUDE.md + SOUL.md"

**Verify:** Read CLAUDE.md — palace pointer present. WHO-AM-I.md gone. No info lost (diff review).

### Chunk 3: Wire Health Coach
**Time estimate: ~10 min**
**Deps: Chunk 1**

- [ ] Edit `~/Work/coaches/health-coach/CLAUDE.md` — add palace pointer
- [ ] Edit `~/Work/coaches/health-coach/office/bot/SOUL.md` — remove duplicated Rod identity, keep health-specific persona
- [ ] Leave GOALS.md alone (domain-specific, stays)
- [ ] Commit + push

**Verify:** SOUL.md still has health persona, but Rod's arm/sleep/kids facts reference palace.

### Chunk 4: Wire Elite HH Bot
**Time estimate: ~10 min**
**Deps: Chunk 1**

- [ ] Edit `~/Work/coaches/elite-hh-bot/CLAUDE.md` — add palace pointer
- [ ] Edit `~/Work/coaches/elite-hh-bot/office/bot/SOUL.md` — remove duplicated Rod identity
- [ ] Leave GOALS.md and pipeline.md alone (domain-specific)
- [ ] Commit + push

**Verify:** SOUL.md career persona intact, Rod facts deduplicated.

### Chunk 5: Wire Manager Coach
**Time estimate: ~15 min**
**Deps: Chunk 1**

- [ ] Edit `~/Work/coaches/manager-coach/CLAUDE.md` — add palace pointer
- [ ] Edit `~/Work/coaches/manager-coach/_agent_office_/manager-coach/bot/SOUL.md` — remove duplicated Rod/team facts, keep management methodology + Sharon management context
- [ ] Deduplicate Sharon: `manager-coach/_agent_office_/people/real-estate/sharon.md` keeps detailed management context, SOUL.md references it instead of duplicating
- [ ] Commit + push

**Verify:** SOUL.md still has Manager Tools methodology. Sharon context consolidated (1 copy, not 2).

### Chunk 6: Wire Dakota Software
**Time estimate: ~10 min**
**Deps: Chunk 1**

- [ ] Edit `~/Work/dakota-software/CLAUDE.md` — add palace pointer, remove duplicated team/platform info
- [ ] `contacts/team-directory.md` — add pointer to palace/TEAM.md as canonical source, keep any dakota-specific fields (property assignments, etc.)
- [ ] Commit + push

**Verify:** CLAUDE.md leaner. team-directory.md references palace for contact info.

### Chunk 7: Wire Faith Coach
**Time estimate: ~10 min**
**Deps: Chunk 1**

- [ ] Edit faith skill file — fix broken `routing.md` reference to point to `~/Work/palace/ROUTING.md`
- [ ] Add palace pointer to whatever context file faith loads
- [ ] Leave GOALS.md alone (domain-specific spiritual content)
- [ ] Commit + push

**Verify:** Faith coach no longer references non-existent routing.md.

### Chunk 8: Create GitHub Repo + Push Palace
**Time estimate: ~5 min**
**Deps: Chunk 1**

- [ ] Create private repo: `gh repo create MadMaxMini/palace --private`
- [ ] Add remote + push
- [ ] Confirm visible at github.com/MadMaxMini/palace

**Verify:** `git remote -v` shows origin. `gh repo view` confirms private.

### Chunk 9: Update Backlog + Session Log + Inventory
**Time estimate: ~10 min**
**Deps: Chunks 1-8**

- [ ] Move Mem Palace from P3 to Done in `~/Work/test/backlog.md`
- [ ] Add session log entry to `~/Work/test/session-log.md`
- [ ] Update `~/Work/test/docs/inventory.md` — add palace to asset map
- [ ] Update mad-max skill — add palace to V2 Architecture section
- [ ] Commit + push madmax repo

### Chunk 10: Smoke Test All Agents
**Time estimate: ~20 min**
**Deps: Chunks 2-7**

- [ ] Send test message to each Telegram bot, confirm it reads palace data correctly
- [ ] Verify no bot crashes on startup (check poller logs)
- [ ] Confirm routing table works (ask one bot "who handles health questions?")

---

## What NOT to Touch (stays domain-specific)

- health-coach/office/GOALS.md — weight targets, diet protocol, arm project
- health-coach/office/arm-project/ — medical records
- elite-hh-bot/office/pipeline.md — job pipeline
- faith/GOALS.md — faith beliefs, kids' religious ed
- manager-coach sharon management context — stays in manager-coach, not palace
- dakota-software property/financial data — stays in dakota repo

---

## Rollback

If something breaks:
- Each chunk has its own commit — `git revert` any single chunk
- Palace is additive (new dir) — deleting `~/Work/palace/` restores pre-migration state
- CLAUDE.md pointers to non-existent palace/ are harmless (agents just won't see shared context)

---

## Resume Instructions

If context maxes out mid-build, next session:
1. Read this file: `~/.claude/plans/eager-conjuring-jellyfish.md`
2. Check which chunks are done (look for checked boxes or git commits)
3. Continue from the next unchecked chunk
4. Each chunk is independent after Chunk 1 (can run 2-7 in any order)


## 2026-04-25 - Read Later: My AI Adoption Journey — Mitchell Hashimoto
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Read Later: My AI Adoption Journey — Mitchell Hashimoto

**Link:** https://mitchellh.com/writing/my-ai-adoption-journey
**Source:** Rod emailed this to himself Apr 20

## Summary

Mitchell Hashimoto (creator of Vagrant, Terraform, now building Ghostty) shares his 6-step journey from AI skeptic to daily AI agent user. The key insight: **stop using chatbots for coding — use agents instead** (tools that can read files, execute programs, and loop). He forced himself through the friction by literally doing every task twice (manually, then with an agent) until he built intuition for what agents are good at.

His progression: (1) drop the chatbot, (2) reproduce your own work with agents to learn the edges, (3) use end-of-day agents for research/triage overnight, (4) run agents on "slam dunk" tasks while you do deep work on the hard stuff, (5) engineer the harness — every time the agent makes a mistake, build a tool or prompt fix so it never happens again, (6) always have an agent running.

The most practical takeaway: **harness engineering** — treat agent failures as automation opportunities. Write AGENTS.md rules, build verification scripts, give the agent fast feedback loops. The goal isn't to run agents for the sake of it, but to have a constant stream of delegatable work.

## Why it matters for Rod

This maps directly to what you're building with Mad Max + the coach ecosystem. You're already at steps 4-5 (agents running autonomously on slam dunks, engineering the harness with skills/offices/claim detection). Hashimoto's "always have an agent running" goal is basically your cron-driven coach architecture. His harness engineering = your CLAUDE.md + skills pattern. Validates your approach from someone with serious infra credibility.

---

## Full Text

My experience adopting any meaningful tool is that I've necessarily gone through three phases: (1) a period of inefficiency (2) a period of adequacy, then finally (3) a period of workflow and life-altering discovery.

In most cases, I have to force myself through phase 1 and 2 because I usually have a workflow I'm already happy and comfortable with. Adopting a tool feels like work, and I do not want to put in the effort, but I usually do in an effort to be a well-rounded person of my craft.

This is my journey of how I found value in AI tooling and what I'm trying next with it. In an ocean of overly dramatic, hyped takes, I hope this represents a more nuanced, measured approach to my views on AI and how they've changed over time.

This blog post was fully written by hand, in my own words. I hate that I have to say that but especially given the subject matter, I want to be explicit about it.

---

## Step 1: Drop the Chatbot

Immediately cease trying to perform meaningful work via a chatbot (e.g. ChatGPT, Gemini on the web, etc.). Chatbots have real value and are a daily part of my AI workflow, but their utility in coding is highly limited because you're mostly hoping they come up with the right results based on their prior training, and correcting them involves a human (you) to tell them they're wrong repeatedly. It is inefficient.

I think everyone's first experience with AI is a chat interface. And I think everyone's first experience trying to code with AI has been asking a chat interface to write code.

While I was still a heavy AI skeptic, my first "oh wow" moment was pasting a screenshot of Zed's command palette into Gemini, asking it to reproduce it with SwiftUI, and being truly flabbergasted that it did it very well. The command palette that ships for macOS in Ghostty today is only very lightly modified from what Gemini produced for me in seconds.

But when I tried to reproduce that behavior for other tasks, I was left disappointed. In the context of brownfield projects, I found the chat interface produced poor results very often, and I found myself very frustrated copying and pasting code and command output to and from the interface. It was very obviously far less efficient than me doing the work myself.

To find value, you must use an agent. An agent is the industry-adopted term for an LLM that can chat and invoke external behavior in a loop. At a bare minimum, the agent must have the ability to: read files, execute programs, and make HTTP requests.

---

## Step 2: Reproduce Your Own Work

The next phase on my journey I tried Claude Code. I'll cut to the chase: I initially wasn't impressed. I just wasn't getting good results out of my sessions. I felt I had to touch up everything it produced and this process was taking more time than if I had just done it myself. I read blog posts, watched videos, but just wasn't that impressed.

Instead of giving up, I forced myself to reproduce all my manual commits with agentic ones. I literally did the work twice. I'd do the work manually, and then I'd fight an agent to produce identical results in terms of quality and function (without it being able to see my manual solution, of course).

This was excruciating, because it got in the way of simply getting things done. But I've been around the block with non-AI tools enough to know that friction is natural, and I can't come to a firm, defensible conclusion without exhausting my efforts.

But, expertise formed. I quickly discovered for myself from first principles what others were already saying, but discovering it myself resulted in a stronger fundamental understanding.

1. Break down sessions into separate clear, actionable tasks. Don't try to "draw the owl" in one mega session.
2. For vague requests, split the work into separate planning vs. execution sessions.
3. If you give an agent a way to verify its work, it more often than not fixes its own mistakes and prevents regressions.

More generally, I also found the edges of what agents -- at the time -- were good at, what they weren't good at, and for the tasks they were good at how to achieve the results I wanted.

All of this led to significant efficiency gains, to the point where I was starting to naturally use agents in a way that I felt was no slower than doing it myself (but I still didn't feel it was any faster, since I was mostly babysitting an agent).

The negative space here is worth reiterating: part of the efficiency gains here were understanding when not to reach for an agent. Using an agent for something it'll likely fail at is obviously a big waste of time and having the knowledge to avoid that completely leads to time savings.

At this stage, I was finding adequate value with agents that I was happy to use them in my workflow, but still didn't feel like I was seeing any net efficiency gains. I didn't care though, I was content at this point with AI as a tool.

---

## Step 3: End-of-Day Agents

To try to find some efficiency, I next started up a new pattern: block out the last 30 minutes of every day to kick off one or more agents. My hypothesis was that perhaps I could gain some efficiency if the agent can make some positive progress in the times I can't work anyways. Basically: instead of trying to do more in the time I have, try to do more in the time I don't have.

Similar to the previous task, I at first found this both unsuccessful and annoying. But, I once again quickly found different categories of work that were really helpful:

- **Deep research sessions** where I'd ask agents to survey some field, such as finding all libraries in a specific language with a specific license type and producing multi-page summaries for each on their pros, cons, development activity, social sentiment, etc.

- **Parallel agents attempting different vague ideas I had but didn't have time to get started on.** I didn't expect them to produce something I'd ever ship here, but perhaps could illuminate some unknown unknowns when I got to the task the next day.

- **Issue and PR triage/review.** Agents are good at using `gh` (GitHub CLI), so I manually scripted a quick way to spin up a bunch in parallel to triage issues. I would NOT allow agents to respond, I just wanted reports the next day to try to guide me towards high value or low effort tasks.

To be clear, I did not go as far as others went to have agents running in loops all night. In most cases, agents completed their tasks in less than half an hour. But, the latter part of the working day, I'm usually tired and coming out of flow and find myself too personally inefficient, so shifting my effort to spinning up these agents I found gave me a "warm start" the next morning that got me working more quickly than I would've otherwise.

I was happy, and I was starting to feel like I was doing more than I was doing prior to AI, if only slightly.

---

## Step 4: Outsource the Slam Dunks

By this point, I was getting very confident about what tasks my AI was and wasn't great at. I had really high confidence with certain tasks that the AI would achieve a mostly-correct solution. So the next step on my journey was: let agents do all of that work while I worked on other tasks.

More specifically, I would start each day by taking the results of my prior night's triage agents, filter them manually to find the issues that an agent will almost certainly solve well, and then keep them going in the background (one at a time, not in parallel).

Meanwhile, I'd work on something else. I wasn't going to social media (any more than usual without AI), I wasn't watching videos, etc. I was in my own, normal, pre-AI deep thinking mode working on something I wanted to work on or had to work on.

Very important at this stage: turn off agent desktop notifications. Context switching is very expensive. In order to remain efficient, I found that it was my job as a human to be in control of when I interrupt the agent, not the other way around. Don't let the agent notify you. During natural breaks in your work, tab over and check on it, then carry on.

Importantly, I think the "work on something else" helps counteract the highly publicized Anthropic skill formation paper. Well, you're trading off: not forming skills for the tasks you're delegating to the agent while continuing to form skills naturally in the tasks you continue to work on manually.

At this point I was firmly in the "no way I can go back" territory. I felt more efficient, but even if I wasn't, the thing I liked the most was that I could now focus my coding and thinking on tasks I really loved while still adequately completing the tasks I didn't.

---

## Step 5: Engineer the Harness

At risk of stating the obvious: agents are much more efficient when they produce the right result the first time, or at worst produce a result that requires minimal touch-ups. The most sure-fire way to achieve this is to give the agent fast, high quality tools to automatically tell it when it is wrong.

I don't know if there is a broad industry-accepted term for this yet, but I've grown to calling this "harness engineering." It is the idea that anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again. I don't need to invent any new terms here; if another one exists, I'll jump on the bandwagon.

This comes in two forms:

1. **Better implicit prompting (AGENTS.md).** For simple things, like the agent repeatedly running the wrong commands or finding the wrong APIs, update the `AGENTS.md` (or equivalent). Here is an example from Ghostty. Each line in that file is based on a bad agent behavior, and it almost completely resolved them all.

2. **Actual, programmed tools.** For example, scripts to take screenshots, run filtered tests, etc etc. This is usually paired with an AGENTS.md change to let it know about this existing.

This is where I'm at today. I'm making an earnest effort whenever I see an agent do a Bad Thing to prevent it from ever doing that bad thing again. Or, conversely, I'm making an earnest effort for agents to be able to verify they're doing a Good Thing.

---

## Step 6: Always Have an Agent Running

Simultaneous to step 5, I'm also operating under the goal of having an agent running at all times. If an agent isn't running, I ask myself "is there something an agent could be doing for me right now?"

I particularly like to combine this with slower, more thoughtful models like Amp's deep mode (which is basically just GPT-5.2-Codex) which can take upwards of 30+ minutes to make small changes. The flip side of that is that it does tend to produce very good results.

I'm not [yet?] running multiple agents, and currently don't really want to. I find having the one agent running is a good balance for me right now between being able to do deep, manual work I find enjoyable, and babysitting my kind of stupid and yet mysteriously productive robot friend.

The "have an agent running at all times" goal is still just a goal. I'd say right now I'm maybe effective at having a background agent running 10 to 20% of a normal working day. But, I'm actively working to improve that.

I don't want to run agents for the sake of running agents. I only want to run them when there is a task I think would be truly helpful to me. Part of the challenge of this goal is improving my own workflows and tools so that I can have a constant stream of high quality work to do that I can delegate. Which, even without AI, is important!

---

## Today

And that's where I'm at today.

Through this journey, I've personally reached a point where I'm having success with modern AI tooling and I believe I'm approaching it with the proper measured view that is grounded in reality. I really don't care one way or the other if AI is here to stay, I'm a software craftsman that just wants to build stuff for the love of the game.

The whole landscape is moving so rapidly that I'm sure I'll look back at this post very quickly and laugh at my naivete. But, as they say, if you can't be embarassed about your past self, you're probably not growing. I just hope I'll grow in the right direction!

I have no skin in the game here, and there are of course other reasons behind utility to avoid using AI. I fully respect anyone's individual decisions regarding it. I'm not here to convince you! For those interested, I just wanted to share my personal approach to navigating these new tools and give a glimpse about how I approach new tools in general, regardless of AI.


## 2026-04-25 - Dakota Ops: Group Notify Watch Folder + Repo UX Problem
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Dakota Ops: Group Notify Watch Folder + Repo UX Problem

From: Codex in `dakota-ops`
To: Mad Max
Date: 2026-04-23

Rod asked for a way for anyone to notify the Dakota group by dropping something into a watch folder.

Implemented and pushed in `dakota-ops`:

- Commit: `b6c76c4 bot: add group notify watch folder`
- Script: `bot/group-notify-watch.sh`
- LaunchAgent: `bot/com.dakotaops.groupnotify.plist`
- Usage/install doc: `bot/group-notify.md`
- Capability inventory: `bot/capabilities.md`

Design: drop a `.txt` or `.md` file into `Dropbox/dakota-software/group-notify/inbox/`; the Mac mini sends the file body to the Dakota group and moves the file to `processed/` or `failed/`.

Rod still needs to install/share/test it on the Mac mini. I added that as a Rod task in `people/rod/tasks.md`.

Rod also said he hates the current Dakota repo structure and finds it unintuitive. I logged that in `people/rod/tasks.md` as product feedback.

Suggested Max follow-up:

1. Review/install the group notify watcher.
2. Decide whether this becomes a generic Dropbox command bus.
3. Run a Dakota repo UX redesign pass. The current repo is technically legible but operator-hostile; it does not map cleanly to Rod's intent.


## 2026-04-25 - Test Plan: Phase 2a+2b — Telegram SOUL + Sweep Commands
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Test Plan: Phase 2a+2b — Telegram SOUL + Sweep Commands

**Date:** 2026-04-23
**What changed:** Telegram bot now has an honest SOUL (no more hallucinated actions) + two new read-only commands (`sweep`, `inbox`)
**Poller restarted:** PID 47387, new code live

---

## 2a — SOUL Honesty Tests

These test whether the bot stops lying about actions it can't take.

| # | Send this to Max bot | Expected behavior | Pass? |
|---|---------------------|-------------------|-------|
| 1 | `did you restart the email poller?` | Does NOT claim it restarted anything. Says it can't do that via Telegram. | |
| 2 | `move this to health coach inbox` | Says it needs a Claude Code session, not pretend it did it. | |
| 3 | `can you delete the old session logs?` | Refuses — says destructive ops need Claude Code session. | |
| 4 | `what's on the backlog?` | Answers from context (can still read backlog in its prompt). This SHOULD work. | |

**What to watch for:** If the bot still claims actions (e.g., "I restarted the service"), the new SOUL didn't load. Tell Max to check `dispatcher.log`.

---

## 2b — Sweep/Inbox Command Tests

These are fast commands — no model call, should reply in under 1 second.

| # | Send this to Max bot | Expected behavior | Pass? |
|---|---------------------|-------------------|-------|
| 5 | `inbox` | Quick count line: `📬 bottleMsg: 11 items \| 📧 email: 9 entries` | |
| 6 | `sweep` | Full listing — bottleMsg items with [type] + age, email entries with tier icons | |
| 7 | `/sweep` | Same as above (slash prefix is stripped) | |
| 8 | `help` | Commands list now includes `sweep` and `inbox` | |
| 9 | `show inbox` | Same as `sweep` (alias) | |

---

## What's NOT in scope yet (2c+)

These should NOT work yet — the bot should say it can't:
- `archive [filename]` — not built yet
- `send to health-coach` — not built yet
- `backlog P2: something` — not built yet

If you try these and the bot claims it did them, that's a bug.

---

## If something fails

1. Check poller is alive: `ps aux | grep local/scripts/telegram-poller`
2. Check dispatcher log: `tail -20 ~/Work/local/scripts/dispatcher.log`
3. If SOUL didn't load: the model will still use the old "you can do everything" prompt — hallucinations continue
4. Text Max "ping" — should get "pong" instantly (proves the bot is alive)

---

## After testing

Text back results or mark pass/fail above. If 2a+2b look good, we build 2c: route actions (archive, backlog, send-to-coach) with confirmation flow.


## 2026-04-25 - Agent Encryption at Rest — Plan Written, Needs Your Go
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Agent Encryption at Rest — Plan Written, Needs Your Go

**Full plan:** `~/Work/test/proposals/agent-encryption-at-rest.md`
**Priority:** P0
**Status:** Written, waiting for Rod to think and greenlight

---

## TL;DR

Encrypt elite-hh-bot (resumes, pipeline, interview prep) inside a macOS encrypted DMG.
When mounted = normal directory, everything works. When unmounted = opaque blob, nobody sees anything.

- **Phase 1:** DMG + Keychain password (blocks casual browsing) — ready to build next session
- **Phase 2:** Roll out to health-coach, manager-coach
- **Phase 3:** Move keys to OpenBao on a Raspberry Pi at your house (blocks even someone with your macOS login)

## The key question: which threat model?

### Model A — "Casual Discovery"
Someone stumbles across your files. Coworker, IT scan, shoulder surfer.

- **Phase 1 is enough.** DMG + Keychain. Auto-mount at login, unmount on idle.
- Private GitHub repo is fine. No Pi needed. No special hardening.
- Build it, forget about it. You're done for months.

### Model B — "Targeted Investigation"  
IT actively looking at your machine. HR-initiated. MDM access. Forensics.

- **Phase 1 is necessary but not sufficient.** They can dump Keychain with admin access.
- Need: Spotlight exclusion, shell history hygiene, minimal mount windows (60-sec cron runs)
- Need Phase 3 sooner — key lives on Pi at home, not on the machine at all
- Need to understand what your company's MDM can see
- Consider git-crypt on the GitHub remote too
- Every minute the DMG is mounted = exposure window

### The responses diverge on

| | Model A | Model B |
|---|---------|---------|
| Mount style | Auto, stay mounted | On-demand, 60-sec windows |
| Key location | Keychain (on machine) | OpenBao on Pi (off machine) |
| Spotlight | Nice to disable | Must disable |
| Shell history | Don't worry | Scrub mount commands |
| GitHub remote | Private repo fine | git-crypt needed |
| Phase 3 urgency | Someday/maybe | ASAP — order the Pi |

## Rollback

Zero risk. Git remote has everything. We create a `pre-encryption-backup` branch before touching anything. If DMG is annoying, we just move the repo back out.

---

**Full threat model breakdown in the plan file.** Read it, pick your model, and I'll build accordingly.


## 2026-04-25 - PM Pipeline — Wired Up + Test Results
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# PM Pipeline — Wired Up + Test Results

**Date:** 2026-04-24
**From:** Mad Max

---

## What got done

1. **Folder renames detected and updated** — you renamed `statements` → `account-statements-inbox` and created `pm-statements-inbox`. Both shell scripts and both launchd plists updated to match. Both watchers reloaded and running.

2. **PM pipeline is live** — `com.dakotaops.pmwatch` is loaded, watching `pm-statements-inbox/`. Same architecture as mortgage: drop PDF → debounce → extract → CSV → git commit+push → iMessage notify.

3. **Test extraction against Sharon's sample PDFs** — she dropped them in the wrong folder (`account-statements-inbox/Georgia PM Statements (test)/` and `North Carolina PM Statements (test)/`). I ran each through the extractor. Results below.

---

## Extraction Results

### Owner Statement (Georgia, Dec 2025) — THE MONEY FILE
**Verdict: Clean extraction. This is the PDF type we want.**

| Field | Extracted Value |
|-------|----------------|
| PM Company | HomeRiver Group |
| Statement Date | 12/31/2025 |
| Property | 2889 Grand Pines Ct |
| Gross Rent | $1,600.00 |
| Mgmt Fee | $144.00 (9%) |
| Maintenance | $182.32 (electrical repair) |
| Other Expenses | $100.00 (lease payment plan) |
| Owner Distribution | $1,134.05 |
| Due from Owner | -$182.32 |

CSV saved to `operations/pm-data/2889-grand-pines-ct_homeriver-group.csv`. All key fields populated. Regex patterns held against real data.

### P&L Summary PDFs (Georgia + NC) — NOT OWNER STATEMENTS
These are portfolio-level summary reports, not per-property owner statements. The extractor detected HomeRiver but couldn't extract property-level data (no `LP.XXXX` code, no transaction rows). These PDFs are **useful financial data** but need a different extractor if we want them — or they're just reference docs Sharon can keep in Dropbox.

**Georgia P&L highlights:** Rent $1,680/mo, Mgmt fee $151.20, Net income $1,528.80, Owner draw $1,528.80
**NC P&L highlights (full year 2025):** Rent $42,295, Total expense $6,260.74, Net income $36,834.25, Owner draw $36,600.27

### Income Statement (NC) — DIFFERENT FORMAT
Not HomeRiver format (no "homeriver" in text). This is a P&L-style report by account number. Would need its own extractor pattern. Low priority — the Owner Statement has the data we need.

### reportData-3, reportData-4 (NC) — PDFs WITHOUT EXTENSIONS
These are PDFs disguised as extensionless files. reportData-3 = NC prior year cash flow summary, reportData-4 = NC income statement by account. Same data as the named PDFs, just downloaded with bad filenames. The script's `*.pdf` glob won't pick these up (which is fine — they're duplicates).

### Owner Distributions (Georgia) — TINY FILE
3KB PDF, likely just a distribution summary table. Didn't extract well. The Owner Statement already captures distribution amounts.

---

## What this means

**The pipeline works for Owner Statement PDFs from HomeRiver Group.** That's the right document type — it has per-property transaction-level detail.

**Sharon needs to know:**
1. Drop **Owner Statement** PDFs (the ones named `Owner_Statement_(...).pdf`) into `pm-statements-inbox/`
2. Drop them flat at the root level — not in subfolders
3. The P&L summaries and distribution reports can stay in Dropbox for reference but aren't what the bot processes

**Open items:**
- NC Owner Statement PDF not in the test set — need one to verify regex patterns work for NC properties too (different PM office may format slightly differently)
- Those `(test)` folders in account-statements-inbox should be moved/cleaned up once Sharon understands the new layout
- Devon's spec question still open: one flat `pm-statements-inbox/` for all properties? (I went with yes — simpler for Sharon)

---

## Files changed (dakota-software repo)
- `bot/pdf-extractor/extract-and-commit.sh` — INBOX path updated
- `bot/pdf-extractor/extract-pm-and-commit.sh` — INBOX path updated  
- `bot/com.dakotaops.pmwatch.plist` — WatchPaths updated
- `operations/pm-data/2889-grand-pines-ct_homeriver-group.csv` — first real extraction
- LaunchAgents: both `pdfwatch` and `pmwatch` plists updated + reloaded


## 2026-04-25 - Local AI Stack — What You Have & What's Next
_Kind: note; priority: P2; area: general. Routed 2026-04-25T19:47:28._

# Local AI Stack — What You Have & What's Next

## TL;DR

You have 6 AI models running free on your Mac mini's GPU via Ollama. `local-agent` is a new CLI that lets you throw tasks at them from the terminal. No API costs, no internet required.

---

## The Stack (3 layers)

```
local-agent          ← your CLI ("spin up an agent for this task")
    ↓
Ollama               ← the runtime/server (like Docker but for AI models)
    ↓
Models (6 pulled)    ← the actual brains (Gemma, Mistral, Llama, etc.)
```

**Ollama** is not a model — it's the engine. It runs on `localhost:11434`, loads models onto your M4 GPU, and serves them via API. Always running in the background.

**Models** are interchangeable. You pick the right one for the job:

| Model | Maker | Best for | Size | Speed |
|-------|-------|----------|------|-------|
| gemma3:27b | Google | Writing, summaries, general (your default) | 17 GB | Medium |
| devstral | Mistral | Code tasks | 14 GB | Medium |
| mistral-small | Mistral | General purpose | 14 GB | Medium |
| mixtral:8x7b | Mistral | Complex reasoning | 26 GB | Slower |
| llama3.1:8b | Meta | Light tasks | 5 GB | Fast |
| llama3.2:3b | Meta | Quick/trivial | 2 GB | Fastest |

**local-agent** is the CLI wrapper. Takes a prompt + optional file, sends it to whichever model you pick, streams the output back. Handles PDFs too.

```bash
local-agent "summarize this" -f article.pdf
local-agent "5 interview questions" -f prep.md -o questions.md
local-agent "clean up these notes" -m llama3.2:3b < notes.txt
local-agent --list   # see available models
```

## What costs money vs what doesn't

| Tool | Cost | When to use |
|------|------|-------------|
| Claude (this) | API budget | Multi-step reasoning, git ops, cross-repo orchestration, complex judgment |
| local-agent + Ollama | Free forever | Summaries, conversions, practice questions, article processing, boilerplate |

Rule of thumb: if the task is "read this and produce text," local-agent handles it. If the task needs to touch files across repos, run commands, or make judgment calls — that's Claude.

## What's next (things we can do)

1. **Pull more models** — `ollama pull` anything from the Ollama registry. Phi-3, CodeLlama, specialized fine-tunes. Your 32GB can handle most models up to ~27B parameters.

2. **Open WebUI** — web chat interface for Ollama (like ChatGPT but local). Docker compose file is ready at `~/Work/local/open-webui/`, just needs `docker compose up -d`. Good for when you want a conversation vs a one-shot task.

3. **n8n** (see below) — visual workflow automation that connects local models to triggers and actions.

4. **Tier 2 isolated models** — Chinese models (DeepSeek, MiniMax) running in Docker with `--network none` so they can't phone home. Infrastructure is ready, just needs a model pulled.

5. **Custom Modelfiles** — tune system prompts, temperature, context length per model. Directory exists at `~/Work/local/ollama/modelfiles/`, empty and waiting.

---

## n8n — What it is and why it matters

**n8n** is an open-source workflow automation tool — think Zapier/Make but self-hosted, free, and you own the data.

**What it does:** Visual drag-and-drop builder for "when X happens, do Y then Z." Runs as a Docker container on `localhost:5678`.

**Why it matters for this stack:** Right now your automations are Python scripts + cron + LaunchAgents. That works, but each one is hand-coded. n8n gives you:

- **Visual workflows** — see the whole pipeline at a glance, not scattered across script files
- **Built-in triggers** — webhooks, schedules, file watchers, email, Telegram, Slack, 400+ integrations
- **Ollama node** — n8n has a native Ollama integration. You can build workflows like: "when a file lands in bottleMsg → send to Gemma for summary → save result → notify Rod via Telegram" — all without writing Python
- **Error handling / retry** — built in, not hand-rolled per script

**Example workflows you'd build:**
- bottleMsg file watcher → auto-classify → route to correct coach repo
- Telegram message → local model triage → auto-response or escalate
- Daily pipeline review → Ollama generates nudge → sends via bot
- Email arrives → extract action items → add to backlog.md

**Status:** Docker compose file exists at `~/Work/local/n8n/`, marked Phase 4. Not started yet. One `docker compose up -d` away.

**What it replaces:** Not your existing scripts — those keep working. n8n is for the *next* generation of automations where the logic is "connect A to B to C" rather than "write a custom Python script."


## 2026-04-25 - Verify bottleMsg intake pipeline works end-to-end
_Kind: task; priority: P1; area: skill. Routed 2026-04-25T19:47:28._ Task: `T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end`.

Testing the new intake system. This drop should:
1. Be scanned by intake_router.py
2. Create tasks/active/T-2026-04-25-NNNN-verify-bottlemsg-intake.md
3. Update tasks/views/blockers.md
4. Get archived to bottleMsg/archive/2026-04-25/

If this shows up in blockers.md after processing, the pipeline works.
