# Mad Max — Backlog

Priority scale:
- **P0** — on fire or blocking Rod's life right now
- **P1** — active sprint, build this week/session
- **P2** — next sprint, ready to queue for night agent
- **P3** — backlog, good idea, not urgent
- **P4** — shelve until trigger event

Last reviewed: 2026-04-20

---

## P0 — On Fire

| Item | Why Now |
|------|---------|
| **Job search — GOALS.md + career-doc.md** | 5 live targets in pipeline (LangChain, Darktrace, Scale AI, ScaleOps, Rubrik). Resume v8 exists. Profile docs (GOALS.md, career-doc.md) are empty templates — bot can't do strategic positioning without them. Rod to fill via interview session with Elite HH coach. |
| **Scale AI job URL** | Mentioned as target #3, never tracked in pipeline.md |

AND Hit me up next session — we can enrich the /models command so the bots actually know model strengths and can discuss tradeoffs with you in chat.

AND how do I use my local AI in the console when Claude dies, is there a plugin for that? 

AND can i start Claude in Haiku, for chatting and loading context and then bump up to opus when we're ready to go? or vice versa that? 

---

## P1 — This Week

| Item | Notes |
|------|-------|
| **7:15am pre-session brief** | Mini sends Rod a Telegram brief every morning at 7:15am: top P0/P1 items, what was done last session, what's blocked waiting on Rod. So Rod comes in with context instead of having to ask. LaunchAgent + script. Fires after 7am Dakota standup. |
| **Accessibility/GUI automation — brainstorm use cases** | I can drive any macOS app via AppleScript + screencapture (proven with Telegram/BotFather). Brainstorm: browser automation (form fills, scraping without API, OAuth flows), driving other desktop apps (Messages, Calendar, Finder), vs MCP browser tools — when to use which. Output: capabilities doc + P2/P3 task list |
| **local/scripts → GitHub (private)** | night-planner, auto-agent, dispatcher committed locally but not backed up. Need .gitignore first (contacts.md, logs, state files), then create private MadMaxMini repo |
| **Night agent — first real run** | Live but untested end-to-end. 10pm tonight is first shot. Watch: `tail -f ~/Work/local/scripts/night-planner.log` |
| **Job coach GitHub repo** | Rod creates repo → I wire it up (5 min). Files at `~/Work/coaches/job/` waiting |
| **Telegram bot + per-coach channels** | One bot (@MadMaxMiniBot) as command interface. Private channels per domain: Health, AutoMax, Job, Dakota. Bot posts to channels + DMs Rod when action needed. Per-channel DND settings in Telegram app. Token → OpenBao. Replaces SMS for everything except Dakota group (they're not on Telegram). Start with one bot, wire channels one at a time |
| **Dispatcher conversation history + context** | Every SMS/Telegram message is stateless — bot forgets you the moment you reply. Fix: per-chat history file (`history-<chat_id>.json`), append every message, inject last N messages into every prompt before "Rod says: ...". Rod decides N (suggest 10). Works for both SMS dispatcher and Telegram bot. Tradeoff: richer convo vs token cost on local models |
| **Calendar bot — fuzzy search** | FTS5 is exact keyword match. "Chik Fil A" misses "Chick-fil-A", "Dominos" misses "Domino's". Need alias/synonym layer or fuzzy matching. Test with 10 known company names, measure miss rate, then fix. Blocks: reliable follow-up queries. |
| **Sharon engagement** | Still dark. Standup going to her, no signal she's reading it. Low spam, warm only at Rod's word |
| **ba8715bc ghost group deletion** | Rod+Devon+Sharon+Doc duplicate with Sharon number without +. Rod deletes in Messages |
| **pm-statements folder + plist setup** | Devon waiting: create `/pm-statements/` folder in Dropbox + install plist on Mac mini before pipeline goes live. Rod to do at office. (From Apr 23 conversation w/ Devon) |
| **Kindle de-Amazon + KOReader setup** | Jailbreak old Kindle (7in 300PPI display, IPX8, 8wk battery) + install KOReader for offline document reading. Supports PDF/EPUB natively (vs Kindle's limitations). Hardware ready, process documented. |
| **Permissions cleanup — per-device, per-repo** | Mini = open (build machine), laptop = tighter. Clean up madmax settings.json (has accumulated dakota/cross-repo perms). Move broad perms to global, keep repo-specific in project settings. Each coach repo gets its own scoped settings. |
| **Mem Palace — ~/Work/palace/** | Shared read layer for all agents. 5 files: ROD, TEAM, PLATFORM, COMMUNICATION, ROUTING. Replaces ~15KB duplication across 6 repos with ~4KB single source. Full chunked plan: `~/.claude/plans/eager-conjuring-jellyfish.md` + copy in bottleMsg. 10 chunks, ~2hr build session. Design done 2026-04-19, plan done 2026-04-20. Trigger to P0: first time an agent gives wrong info due to stale duplicate. |

---

## P2 — Next Sprint (night agent candidates)

| Item | Notes |
|------|-------|
| **Standup redesign — two-part message** | iMessage (plain text): 1 priority per person + link to GitHub. Repo (markdown): full detail. Rod's design, waiting on group feedback before building |
| **Email poller — wire credentials** | email-poller.py built. Needs: email address (Max@dakotaentllc.com?), app password → Keychain, launchd plist installed |
| **Migrate coaches to Telegram channels** | Once Telegram bot is live (P1), migrate health/job/automax notifications off SMS. SMS stays for Dakota group only |
| **Telegram context layer** | Add `sessions/` JSONL per channel to dispatcher. Default 3-msg history, cap 20. Inline: `+context N`, `+reset`, `+model X Ym`. See bottleMsg/2026-04-11-telegram-context-architecture.md |
| **bottleMsg cleanup bot** | Daily scan → classify items → text Rod proposed action list → Rod replies go/skip → archive. Human-in-the-loop via SMS until trusted. Same approval-gate pattern as night-planner |
| **Per-agent OpenBao tokens** | Real secrets in vault now. Narrow each agent's policy before something bleeds. Contains blast radius |
| **GitLab mirror backup** | Second remote for all repos. Scripts ready, needs GitLab account + remotes added |
| **Standup quality — richer sources** | Currently only tasks.md + git commits. Misses deals, calls, texts, email, verbal agreements |
| **msggateway_bin surface reduction** | Strip C binary to read-only chat.db sensor. Move keychain lookups, notify calls, inbox writes to Python. Recompiles rare → FDA stays stable |
| **Outbound network monitoring** | Jacob flagged — log/alert on unexpected outbound connections. macOS pf/lulu or lightweight script |
| **6am standup review gate** | Review before group send — flagged S17 |
| **Recruit-coach agent** | Repo exists, skill/office pattern, not yet active |

---

## P3 — Backlog

| Item | Notes |
|------|-------|
| **Pi 5 setup** | Auto-unseal, watchdog, lightweight cron offload, rsync nightly backup of ~/Work/ |
| **model-lab — LoRA/SFT pipeline** | Fine-tune open coding model on our data. Stack: Unsloth/Axolotl. Rented GPU for training. Start with 100-500 clean examples. Folder at ~/Work/model-lab/ |
| **Dakota folder refactor** | Rethink repo structure — inbox, contact tracking, property tracking, bot layout. Rod defines vision, Max builds |
| **Bot pipeline — per-person micro-bots** | Fix standup conflation. Each person bot gets tasks + role context, stitcher combines. Structural fix |
| **Google Sheets CSV export** | Apps Script → CSV → bot picks up for financial context |
| **iMessage group creation via AppleScript** | Blocked (-1700 error). Workaround: Rod creates group, I use chat ID. Investigate alternatives |
| **Open WebUI — first real use** | Live at localhost:3000, untouched |
| **n8n setup** | Phase 4 workflow automation, docker-compose ready |
| **Benchmark round 4** | 6 models — pending Gemma 3 27B + Mistral Small pulls |
| **Tier 2 models** | DeepSeek, MiniMax in Docker isolated (--network none) |
| **Repo rename test → madmax** | Proposal written, pending Rod approval |
| **Add Rjclemente as collaborator to dakota-software** | Needs gh token or browser |
| **Dispatcher model feature flag** | Env var in launchd plist to switch Claude CLI vs Ollama default. One-line flip |
| **OpenBao store HF token** | Path confirmed: tokens/huggingface |
| **Agent encryption — office/ folders** | Transit keys set up, not yet wired to any agent |
| **Session-log rolling + semantic memory** | session-log.md stays last 3 days, rolls to archive/session-archive-YYYY-MM.md. Mem0 + Qdrant for semantic extraction. Design doc: bottleMsg/2026-04-13-memory-architecture.md |
| **bottleMsg watcher** | Watch ~/Dropbox/bottleMsg/ for new .md files, text Rod on drop. Generic — not just cheat-sheet failures. LaunchAgent (WatchPaths or poll). Delivery: iMessage shortcut or Telegram. |

---

## P4 — Shelve Until Trigger

| Item | Trigger |
|------|---------|
| **Anthropic API direct** | Claude CLI rate limits become a real problem |
| **Plaid integration** | Devon buys in |
| **Tax package automation** | Plaid first |
| **Lease expiration alerts** | Properties folder has real data |
| **LoRA fine-tuning** | model-lab scaffolded + 500 clean examples ready |
| **Pi 5 auto-unseal node** | OpenBao has real dependents |
| **Tier 2 model evaluation** | Disk space available, use case defined |
| **Session timeout — skip blocked prompts** | UX improvement, low urgency |

---

## Done (recent)

- ✅ Night agent system — night-planner.py + auto-agent.py + dispatcher approval flow (2026-04-08 S26)
- ✅ Health coach scaffold + 6am daily nudge via launchd (2026-04-08 S26)
- ✅ Job coach scaffold — pipeline.md seeded with LangChain, Darktrace (2026-04-08 S26)
- ✅ Standup dedup fix — failed sends now write 'failed' state (2026-04-08 S26)
- ✅ Git pull/push pinned to origin main across all bot scripts (2026-04-08 S26)
- ✅ Permissions revamp — global + project settings.local.json cleaned (2026-04-08 S26)
- ✅ Stale faith clone deleted, recruiting-coach moved to coaches/ (2026-04-08 S26)
- ✅ Dispatcher model switching + self-awareness live (2026-03-27)
- ✅ iMessage gateway LIVE — C binary, FDA granted, polling every 30s (2026-03-23 S17)
- ✅ attributed_body decode fix in msggateway.py (2026-03-23 S18)
- ✅ Standup dedup guard — standup-state.log, FORCE_NOTIFY=1 override (2026-03-21)
- ✅ notify.sh → AutoDakota_Notify_Rod shortcut (2026-03-21)
- ✅ notify-group.sh → AutoDakota_Notify_Group shortcut (2026-03-21)
- ✅ Standup pipeline live — 7pm draft, 7am group send, weekdays only
- ✅ Faith pipeline live — Friday 3pm + Wednesday 7am Lenten nudge
- ✅ Open WebUI live at localhost:3000
- ✅ Devstral 24B pulled (S7)
