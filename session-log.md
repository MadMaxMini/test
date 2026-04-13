# Session Log

---

## 2026-04-13 (mini) — health-coach consolidation

### Done
- **health-coach repo consolidated** — discovered `~/Work/coaches/health/` had real content from laptop (Apr 8) that was never git-tracked; `health-coach/` git repo was still empty scaffold
- **Merged `health/` → `health-coach/office/`** — ported CLAUDE.md, GOALS.md, log.md, roadmap.md, session-log.md, bot/daily-nudge.py
- **Deleted orphaned `~/Work/coaches/health/`** — nothing points to it anymore
- **Fixed launchd plists** — `com.dakotaops.healthnudge` updated to point to new path in `health-coach/office/bot/`; both plists reloaded and confirmed running
- **Added `git pull` to `daily-nudge.py`** — 6am script now pulls latest from origin before reading GOALS.md, so laptop pushes auto-update the morning texts
- **Pushed all changes** to `git@github.com:Roderick-Clemente/health-coach.git`

### Waiting on Rod
- Fill in `office/GOALS.md` — weight target, workout routine, diet protocol, sleep. Until then, 6am nudges are generic fallbacks.

---

## 2026-04-02 (mini) — session 26

### Done (continued pt2)
- **notify-group.sh re-enabled** — was deliberately disabled, Rod approved turning back on
- **scan.py group text fixed** — was sending old digest format; now sends agreed format: top 1 per person + wins + GH link
- **Wins dedup fixed** — one win per person, 55-char truncation, no duplicates
- **Standup manually sent** to Dakota group with `FORCE_NOTIFY=1`
- **standup-system-deets.md** dropped in bottleMsg — full architecture writeup, Rod texted

### Done (continued)
- **bottleMsg inbox processed** — 9 items, GTD loop: routed model intel → local-ai.md, model-lab → backlog P2 + folder created, screenshots archived
- **GTD inbox loop built into mad-max skill** — collect→clarify→organize→table→archive. Runs every session start.
- **Weekly review cron** — Friday 4pm, texts Rod backlog counts + bottleMsg status + HH pipeline + GitHub links. `com.madmax.weeklyreview` loaded.
- **Qwen3.5-35B-A3B added to local-ai.md** — strong agentic candidate, 3B active params, fits 32GB, HF CTO-endorsed
- **LLMFit + GGUF tooling section added to local-ai.md**
- **model-lab/ folder created** at `~/Work/model-lab/` per Rod's kickoff doc
- **Decision log updated** in mad-max SKILL.md — 3 new entries

### Done
- **elite-hh-bot repo live** — migrated `~/Work/coaches/job/` into skill/office structure, pushed to `git@github.com:Roderick-Clemente/elite-hh-bot.git`, local at `~/Work/coaches/elite-hh-bot`
- **health-coach repo live** — skeleton scaffolded and pushed to `git@github.com:Roderick-Clemente/health-coach.git`, local at `~/Work/coaches/health-coach`. Content to port from Rod's laptop.
- **Daily crons wired (launchd)**:
  - `com.elitehhbot.daily` — 6:30am, runs `office/bot/daily.py`, texts Rod pipeline + homework
  - `com.healthcoach.daily` — 6:30pm, texts "still empty, port from laptop" until GOALS.md is populated
- **Dakota standup format updated** — text message now shows top task per person + quick wins + GitHub link instead of digest+top3
- **Inventory updated** — both new repos added, local paths corrected

### Decisions
- elite-hh-bot uses skill/office split (matches recruiting-coach pattern)
- health-coach daily bot is "port reminder" until content arrives — auto-upgrades to real check-in after GOALS.md populated
- Full autonomy by default in both new repos — ask only on deletes

### Waiting on Rod
- Port health coach content from laptop to `~/Work/coaches/health-coach/office/`
- Scale AI job URL for pipeline.md

### Next Session — START HERE
1. **bottleMsg processing** — read open-model-tuning-kickoff.md + screenshots, build better inbox system
2. **Devon PDF automator handoff** — confirm Rod gave Devon the code
3. **Sharon terminal status** — check if she replied, install auto-commit if unblocked
4. **Dispatcher conversation history** — P1, Rod to decide how many messages back
5. Multi-channel notifications design (P1)

---

## 2026-03-27 (mini) — session 25

### Done
- **Dispatcher overhauled** — default switched to `mistral-small:latest`, dropped `llama3.1:8b` from rotation
- **Persistent model switching** — text `model claude|gemma|fast|local` to switch, sticks until changed. `model?` to check current. One-off overrides (`use claude` etc.) still work per-message.
- **Model self-awareness** — active model name injected into system prompt. Tested: "what model are you?" → "Mistral Small 3" ✅
- **Backlog updated** — P1: dispatcher conversation history. P0: dispatcher model self-awareness (done, can mark closed).

### Decisions
- mistral-small over llama3.1:8b as default — better quality, ~10s, already benchmarked well
- No auto-reset on model switch — Rod controls it explicitly
- Conversation history deferred to P1 (token cost tradeoff needs Rod's input on N)

### Next Session — START HERE
1. **bottleMsg processing** — read open-model-tuning-kickoff.md + screenshots, build better inbox system
2. **Devon PDF automator handoff** — confirm Rod gave Devon the code
3. **Sharon terminal status** — check if she replied, install auto-commit if unblocked
4. **Dispatcher conversation history** — P1, Rod to decide how many messages back
5. Multi-channel notifications design (P1)

---

## 2026-03-26 (mini) — session 24

### Done
- **iMessage receive pipeline restored** — msggateway_bin lost FDA (likely after binary recompile on Mar 23). Re-granted FDA, restarted service. Incoming texts flowing again.
- **log-watcher path mismatch fixed** — test/log-watcher.py was watching `test/local/scripts/msggateway.log` (empty) instead of `local/scripts/msggateway.log` (actual). Fixed paths, reset state offset, restarted watcher. Free-form dispatch working.
- **Backlog updated** — P2: msggateway_bin surface area reduction. P3: dispatcher model feature flag.

### Decisions
- FDA root cause unclear (no reboot since Mar 22, TCC log shows nothing) — watch for recurrence
- msggateway_bin surface area reduction is right call long-term, P2 for now
- Model feature flag (Claude vs Ollama) added to P3

### Next Session — START HERE
1. **bottleMsg processing** — read open-model-tuning-kickoff.md + screenshots, build better inbox system
2. **Devon PDF automator handoff** — confirm Rod gave Devon the code
3. **Sharon terminal status** — check if she replied, install auto-commit if unblocked
4. **Standup format review** — sparse format is live, bot output now matches it
5. Multi-channel notifications design (P1)
6. model-lab/ kickoff

---

## 2026-03-26 (mini) — session 23

### Done
- **Dakota overhaul grokked** — 20+ commits from last night understood: skill rewrite, contacts scaffold, mortgage-view loaded, La Estancia added, inbox killed, Codex compat (AGENTS.md + .codex/), VS Code tasks, scripts/coach launcher
- **Rod #1 task set** — give Devon the PDF automator today (added to rod/tasks.md)
- **Sharon terminal check** — note in repo + direct iMessage sent to +639451631830
- **overdue.md fixed** — moved from inbox/ to bot/ (bot was writing there, inbox is dead)
- **dakota-software permissions fixed** — was narrow per-path list, now `Edit(**)` + `Write(**)` across the board
- **AGENTS.md fixed** — hardcoded laptop paths → relative paths
- **auto-commit.sh built** — idle-aware, 15min interval, 10min idle guard, `auto:` tag, `git add -u`
- **install-autocommit.sh built** — one command to wire up on Sharon/Doc's machines
- **Notify path confirmed fixed** (8am this morning) — bot will text group correctly tomorrow

### Decisions
- Auto-commit: 15min run, skip if staged or files touched in last 10min, `git add -u` only, `auto:` prefix
- Sharon/Doc = auto-commit when terminal is unblocked. Devon = manual. Rod = separate flow.
- bottleMsg `2026-03-24-open-model-tuning-kickoff.md` — P1 next session, build better inbox processing system then

### Next Session — START HERE
1. **bottleMsg processing** — read open-model-tuning-kickoff.md + screenshots, build better inbox system
2. **Devon PDF automator handoff** — confirm Rod gave Devon the code
3. **Sharon terminal status** — check if she replied, install auto-commit if unblocked
4. **Standup format review** — sparse format is live, bot output now matches it
5. Multi-channel notifications design (P1)
6. model-lab/ kickoff

---

## 2026-03-25 (mini) — session 21

### Done
- **dispatcher.py** — channel-agnostic freeform → Claude CLI. Rod texts anything, mini replies. Context-aware (knows the stack, repos, team).
- **log-watcher.py** — tails msggateway.log, catches Rod's texts in real-time, routes unknown commands to dispatcher, replies via Messages.app direct. Live as `com.dakotaops.logwatcher`.
- **notify.sh fixed** — was using broken pipe→Shortcuts pattern (dropped message body). Now Messages.app direct with explicit iMessage service. Rod-direct texts working.
- **notify-group.sh fixed** — was using Shortcuts participant-match (non-deterministic, hit ghost group). Now uses chat ID from Keychain directly. Confirmed hitting `223693c9` (Dakota Enterprises). **Currently disabled** — Rod said no group texts until further notice.
- **Ghost group (`ba8715bc`) confirmed** — was getting 7am standups instead of correct group. Rod deleted it. notify-group.sh now immune to this bug via chat ID routing.
- **email-poller.py** — Rod's emails now dispatched to Claude, not just logged.
- **Shortcuts wrong-group bug confirmed** — Apple-confirmed bug: Shortcuts can't target group by ID, only participant list. Non-deterministic when multiple matching groups exist. Documented in backlog.
- **Dropbox Screenshots path** saved to SKILL.md (`~/Library/CloudStorage/Dropbox/Screenshots/`)
- **Backlog updated** — 3 new P1s: multi-channel bot notifications, standup quality, Dakota folder refactor

### Decisions
- notify.sh/notify-group.sh: bypass Shortcuts entirely, Messages.app osascript direct — more reliable, no Shortcuts dependency
- Group sends disabled until Rod says go — bot works solo, texts Rod only
- log-watcher pattern: C binary keeps FDA, Python watcher reads log — no System Settings change needed

### Next
- Re-enable group send when Rod is ready (one line change in notify-group.sh)
- Fix ba8715bc in chat.db — still there (iOS delete doesn't remove from Mac DB), but irrelevant now that we use chat ID
- standup quality improvement — catch work outside tasks.md (P1)
- Multi-channel notifications design — Telegram vs Pushover vs other (P1)
- Dakota folder refactor — Rod to define vision
- model-lab/ setup — open model fine-tuning kickoff (from bottleMsg)
- Rod's email address for dispatcher — confirm `roderick.clemente@protonmail.com` is right

### Blocked
- Group send disabled by Rod

---

## 2026-03-24 (mini) — session 20

### Done
- Built email-poller.py — Gmail IMAP, polls every 5 min, batch notify, readonly
- Credentials stored in OpenBao (secret/email/gmail) — username + app password
- Filter: only logs/notifies for emails addressed to @dakotaentllc.com
- Daemon installed and live — com.dakotaops.emailpoller launchd agent
- State set to uid=38, inbox clean, watching for new mail only
- Added to backlog: GitLab mirror backup (P2), Pi rsync backup (P2), email wiring (P2 → done)
- backup-repos.sh + plist written (Pi rsync, ready when Pi SSH is set up)

### Decisions
- Email account: macbotpooterson@gmail.com (bot account), forward @dakotaentllc.com there when ready
- Credentials in OpenBao (not Keychain) for email — sets the pattern for future integrations
- Filter on To: header (not From:) — right call, catches forwarded mail too

### Also Done (continued)
- Built send_email.py — SMTP from macbotpooterson@gmail.com, creds from OpenBao
- Calendar invites via .ics attachment — works with any email client (Proton, Gmail, Apple Mail)
- Contact shorthand: rod, devon, doc, sharon, dakota (team emails TBD, fill in contacts dict)
- Sharon: email-forwarding-setup.md + task added, email triage discussion added as low-priority group task
- Test invite sent to roderick.clemente@protonmail.com ✅

### Also Done (end of session)
- Sharon's direct number pulled from chat.db, stored in Keychain as imessage-sharon (+639451631830)
- Group text sent to Dakota — Sharon notified of repo updates + email ask
- contacts.md lives at ~/Work/local/scripts/contacts.md (mini-local, not in git)

### Next
- Set up mail forwarding from Max@dakotaentllc.com → macbotpooterson@gmail.com
- GitLab account + mirror remotes for all repos
- Pi SSH setup → activate backup-repos.sh daemon
- Rotate the app password that was sent in plaintext in chat (Google → App Passwords → delete mini-poller → recreate)
- Fill in Devon + Doc + Sharon emails in send_email.py CONTACTS once Sharon responds
- Update contacts.md to document imessage-sharon keychain key

### Done
- FDA re-granted for `msggateway_bin` (remove + re-add, toggle alone doesn't work) — gateway live, PID confirmed, ping/pong verified ✅
- SMS audit: mapped all 12 chat threads, identified ghost groups and active chats
- Root cause found: `AutoDakota_Notify_Group` shortcut was configured to `ba8715bc` (ghost group) — standups were going there instead of Dakota Enterprises chat (`223693c9`)
- Rod fixed shortcut — re-added Sharon with correct number, manually verified send hits correct group ✅
- Sent warning message to ghost group (`ba8715bc`): "WRONG GHOST GROUP - DO NOT SEND MESSAGES HERE PLEASE"
- Ghost group `ba8715bc` NOT deleted yet — Rod wants to keep for now
- Standup redesign vision logged as P1: two-part message — plain text iMessage (top priority, each person's #1 task, celebrations, blockers, GitHub link) + full markdown standup in repo. GitHub deep-link approach already proven in prep-standup.py. Waiting on group feedback before building.
- notify-group.sh live test: ✅ confirmed — standup hit correct group after shortcut fix
- Rjclemente collaborator: ✅ already confirmed added (session 18+19)

### Decisions
- Ghost group `ba8715bc`: keep for now, label only, delete later
- Standup redesign: Rod's design validated, build after group feedback

### Next Session — START HERE
1. Email bot — new conversation started (DE@DakotaAndLLC.com, P0 in backlog)
2. Tomorrow 7am standup — verify it hits correct group (first live test of fixed shortcut)
3. Ghost group `ba8715bc` — revisit deletion when Rod is ready
4. Sharon — check Rod+Sharon group for any reply

---

## 2026-03-23 (mini) — session 18+19 — CLOSED

### Done
- SMS thread full audit — reviewed every thread in chat.db
- Deleted: macbotpooterson self-test, Rod+Devon ghost group, Devon 1:1 (Rod deleted), Doc 1:1 (Rod deleted), Rod 1:1 history (Rod cleared), Jacob 1:1 (Rod deleted)
- Identified all contacts: Rod, Devon (brother, primary tech partner), Doc (+19739704525, Rod's father Roderick J Clemente), Sharon (+639451631830, Philippines), Jacob (+15122399285, friend, low priority for bot)
- Rules locked: Devon/Doc/Jacob solo texts = rare, Rod's explicit word only; Jacob group only
- Sent apology to Rod+Jacob group for accidental 1:1 send
- Rod created Rod+Sharon group (f0641ba091334238a03126835280dc23) — primary Sharon channel going forward
- Sharon warm message sent — mission: get her plugged in and liking the system
- Dakota software structure redesign flagged as P1 — logged in Rod's tasks.md (inbox trigger, contact tracking, property tracking)
- Devon content strategy notes recovered from deleted thread — saved to people/devon/notes.md. 4 open questions blocking Devon, needs Rod's green light
- attributed_body gap fixed in msggateway.py — was missing messages stored as typedstream; now decodes via regex fallback
- Pins not visible in chat.db (stored in separate Apple system DB)

### Decisions
- Jacob: bot never texts 1:1, group only, low priority
- Devon/Doc: solo texts allowed but rare, Rod's word only
- Sharon primary channel: f0641ba091334238a03126835280dc23 (Rod+Sharon group)
- attributed_body decode: typedstream regex, not plistlib (it's not a plist)

### Additional work (post-shutdown)
- C gateway: attributed_body decode + whitespace trim bug fixed, recompiled + signed
- ~/Work/local/ initialized as git repo — gateway source now tracked
- Backlog overhauled — stale items cleaned, current P0/P1 accurate
- gh CLI installed + authed by Rod
- Dakota-software collaborators confirmed: Rjclemente ✅ devonclemente ✅ MadMaxMini ✅ faithsv79-tech (Sharon?) ✅
- **DO NOT TEXT ANYONE until Rod returns** — explicit instruction

### Blocked — needs Rod
- **Gateway receive is DOWN** — FDA wiped by recompile. Fix: System Settings → Full Disk Access → remove msggateway_bin → re-add it. Rod will do when back.
- Ghost group cleanup (ba8715bc) — Rod wants to think about it first

### Next Session — START HERE
1. **FDA re-grant** for msggateway_bin (remove + re-add, toggle not enough)
2. Ghost group decision — Rod has a preference, needs to decide which to keep
3. Sharon response — check Rod+Sharon group for reply
4. Dakota software structure design conversation
5. `gh auth login` done ✅ — now can manage collaborators autonomously

---

## 2026-03-23 (mini) — session 17 — CLOSED

### Done
- iMessage gateway: plist reloaded to run C binary, FDA granted by Rod — gateway LIVE, polling every 30s ✅
- Standup bot: wins section added (scan recent [x] tasks, emoji by person, bottom of standup + iMessage)
- Doc tasks updated: VS Code + GitHub marked done (Devon set up 2026-03-22)
- Team directory created: `~/Work/dakota-software/team/directory.md` — contacts, GitHub usernames, gateway tiers
- Backlog: outbound monitoring added as P1 (Jacob flagged)
- Monitor whitelist: Jacob + Devon + Sharon + Doc added to msggateway-monitor keychain
- send_msg.py: outbound rate limiter built — 2/recipient/hr, 5 global/hr, --live mode (20/40), auto-expires 60min
- Sharon's duplicate group chat root cause found: +63 number registered without + prefix in one thread
- Corrected Doc commit identity: "Roderick J Clemente" = Doc (Devon configured), GitHub = Rjclemente

### Decisions
- No outbound messages without Rod's explicit authorization during SMS review sessions
- Default bot limits: 2/recipient/hr, 5 global/hr. Live mode: 20/recipient, 40/hr, 60min TTL

### Next Session — START HERE
- SMS review: pull all active threads, review together, Rod decides what to clean up / adjust
- Adjust messaging tone + primary channels + what triggers a message vs staying silent
- Add Rjclemente as collaborator to dakota-software (needs browser or token)
- 6am standup check script (review gate before group send)

---

## 2026-03-22 (mini) — session 16 — CLOSED

### Done
- Gateway FDA root cause fully diagnosed: TCC checks the responsible process. MsgGateway.app is unsigned so FDA doesn't propagate. Terminal (as responsible process) works; launchd doesn't.
- All alternatives tested: AppleScript (-1700, Messages doesn't expose received content), compiled C binary, Python sqlite3 — all blocked at TCC layer without proper responsible process
- Gateway now working from Terminal: Terminal + sqlite3 + VS Code + claude all in FDA
- Fixed "itself: unbound variable" bug — multi-line message bodies (from Devon's email) caused `while IFS='|' read` to feed continuation lines as fake records; integer check added
- Jacob (+15122399285) texted asking "Which MacOS firewall options should be enabled?" — answered via AutoMax_Notify_JacobAndRod ✓
- ROBOT SHUTDOWN command added to both msggateway.sh and msggateway.py — creates /tmp/msggateway_shutdown flag, silences responses until flag deleted
- Gateway rewritten in Python (msggateway.py) — uses Python's sqlite3 module in-process, no sqlite3 subprocess
- Launchd plist updated to run python3 directly — when python3 has FDA, TCC attributes access correctly without Terminal
- FDA current state: Terminal ✓, VS Code ✓, sqlite3 ✓, MsgGateway.app ✓, msggateway ✓, claude ✓, python3 ✗ (needed for launchd fix)
- Rod wants to downgrade privileges eventually — plan: compile C binary with FDA once stable, remove broad grants
- Dropbox Screenshots folder confirmed at ~/Library/CloudStorage/Dropbox/Screenshots/ — checking mid-session now ✓

### Decisions
- launchd gateway: use python3 directly (not bash wrapper) — python3 + FDA = headless operation without Terminal
- ROBOT SHUTDOWN: flag file at /tmp/msggateway_shutdown, deleted manually (requires physical presence by design)
- Jacob is an active contact — should be added to monitor tier or given a proper role
- Dropbox Screenshots: I now monitor this folder during sessions (Rod drops screenshots there to communicate)

### Next Session — START HERE (one action needed from Rod)
1. **Grant FDA to compiled binary**: System Settings → Full Disk Access → `+` → `Cmd+Shift+G` → paste `/Users/macBot/Work/local/scripts/msggateway_bin` → Open → toggle ON
2. **Reload gateway**: `launchctl unload ~/Library/LaunchAgents/com.dakotaops.msggateway.plist && launchctl load ~/Library/LaunchAgents/com.dakotaops.msggateway.plist`
3. **Verify**: `launchctl list | grep msggateway` → should show PID (not `-`)
4. **Ping test**: text "ping" → expect "pong — mini is alive"
5. **After confirmed working**: remove Terminal, VS Code, sqlite3, python3 from FDA — only `msggateway_bin` needs it
6. **Jacob**: decide his tier (monitor or admin?) — he's actively texting the mini
7. **Team onboarding**: Sharon + Doc GitHub usernames still needed
8. **KeePass backups in bottleMsg**: what to do with bkUp.kdbx + bkup2bkup.kdbx?

### What was built this session
- `msggateway.py` — Python port (backup, works from Terminal)
- `msggateway.c` + `msggateway_bin` — compiled C binary, ad-hoc signed as `com.dakotaops.msggateway`
- ROBOT SHUTDOWN command in both .sh and .py versions
- launchd plist updated to run `msggateway_bin` directly
- Jacob answered re: macOS firewall options
- Dropbox Screenshots folder confirmed as real-time comms channel

---

## 2026-03-22 (mini) — session 13 — CLOSED

### Done
- Sent Jacob a Mac hardening guide via `AutoMax_Notify_JacobAndRod` (iMessage)
- Debugged shortcut invocation: `shortcuts run --input-path /dev/stdin` silently drops input (false exit 0). Correct pattern: AppleScript `with input {"..."}` via osascript
- Updated SKILL.md: added Sending Messages section with all 3 shortcuts (`AutoDakota_Notify_Rod`, `AutoDakota_Notify_Group`, `AutoMax_Notify_JacobAndRod`), invoke pattern, and fallbacks
- Updated memory: `feedback_automax_notify_shortcut.md` — AppleScript pattern documented for future sessions
- Discussed RAG vs skill file for reference data — current scale (3 shortcuts) doesn't justify RAG; revisit at Phase 4+

### Decisions
- Shortcut invocation: always AppleScript `with input {"..."}`, never CLI flags
- Skill file is the right home for shortcut reference at current scale (not RAG)

### Next Session — START HERE
1. **Gateway `.app` bundle** — wrap msggateway.sh in Automator shell script app → grant FDA to that app → restart gateway → ping test
2. **Team onboarding** — Devon screen share with Sharon (P0), get GitHub usernames for Sharon + Doc + Devon
3. **notify-group.sh live test** — confirm Rod+group actually receives (P1)
4. **Per-agent OpenBao tokens** (P1)

---

## 2026-03-22 (mini) — session 12 — CLOSED

### Done
- Triaged bottleMsg inbox: processed REVIEW-2026-03-18, mini-status-2026-03-19, Honda.txt — all archived
- Backlog overhauled: team onboarding P0, Mixtral → P2, inbox/Dropbox deprioritized (laptop handles), iMessage receive elevated
- iMessage gateway: whitelist wired (admin = Rod only, monitor = empty for now), plist installed + running (PID confirmed)
- Gateway BLOCKED: launchd can't read chat.db — FDA not flowing to launchd process. Fix: wrap in Automator .app bundle → grant FDA to that app. Added to P1 backlog.
- Security posture locked: paranoid by default, unknown senders flagged + Rod notified. Rod tells me to calm down, not the other way.
- Permission model decided: Option C (Rod admin only) now. Monitor mode built (team texts logged to inbox). Upgrade path to Option A (queue+approve) when team is stable.
- Noon text scheduled to Dakota group (Devon good luck + Google Doc link)
- Noon text script: `~/Work/local/scripts/noon-devon-2026-03-22.sh` + `at` job

### Decisions
- iMessage permission tiers: Rod = admin (full commands), team = monitor (logged, not executed), unknown = SUSPICIOUS → notify Rod immediately
- Gateway FDA fix: `.app` bundle approach, not `/bin/bash` FDA (too broad)
- Backlog is canonical roadmap — not ad-hoc TODO lists

### Next Session — START HERE
1. **Gateway `.app` bundle** — wrap msggateway.sh in Automator shell script app → grant FDA to that app → restart gateway → ping test
2. **Team onboarding** — Devon screen share with Sharon (P0), get GitHub usernames for Sharon + Doc + Devon
3. **notify-group.sh live test** — confirm Rod+group actually receives (P1)
4. **Per-agent OpenBao tokens** (P1)

---

## 2026-03-21 (mini) — session 10 — CLOSED

### Done
- Wrote `WHO-AM-I.md` — full self-portrait of Mad Max: persona, hardware, stack, what's been built, roadmap, open decisions, principles
- Filed under repo root for easy reference
- GPU expansion research — eGPU, distributed inference, upgrade path (triggered by Mixtral 8x7B hitting 32GB ceiling at 0.4 tok/s)
  - **eGPU: dead end.** Apple Silicon dropped Metal eGPU support entirely. No path via Ollama/llama.cpp.
  - **Distributed / TB cluster (exo): technically works, practically slow on base M4.** Two 32GB nodes over TCP/IP = 2–5 t/s on 70B. RDMA requires TB5 (M4 Pro) + macOS Tahoe 26.2 — not available on base M4.
  - **Best path: single 64GB M4 Pro mini (~$1,799).** Runs 70B Q4 at ~5 t/s solo, TB5 for future clustering.
  - Sweet spot at 32GB: up to ~34B Q4. 70B needs 64GB+.
- Mixtral MoE deep-dive: no config fixes it at 32GB. All 8 expert tensors must be resident (router selects per token). Expert offloading exists in llama.cpp but is slower at 32GB, not faster. Mistral Small 22B (dense, 14GB) is strictly better on this hardware.
- Open WebUI confirmed running at localhost:3000 — all models available in dropdown
- Community model rankings research (HuggingFace leaderboards, LocalLLaMA, Chatbot Arena):
  - Gemma 3 27B: actually top-tier globally (Elo 1339, competes with o1-preview). Best general-purpose model on the mini. Hallucination was task-fit issue, not a dumb model — use for chat/reasoning, not structured ops output.
  - Mistral Small 3.1: community pick for "one model on 32GB hardware." Best balance of quality + speed + Apache 2.0 license. Best ops pipeline model.
  - Devstral 24B: coding specialist only. #1 open-source coding agent at this size (46.8% SWE-Bench). Degrades on general chat.
  - Mixtral 8x7B: obsolete in 2026. Llama 3.1 8B beats it on most tasks at 1/3 the RAM.
  - Llama 3.2 3B: best in 3B class, only useful for ultra-low-RAM/edge scenarios.
- Pi + Llama discussion: Llama 3.2 3B runs on Pi 5 (8GB) at ~1-2 tok/s CPU-only. Larger models don't work well. Pi stays earmarked for OpenBao/watchdog — not inference.

### Next Session — START HERE
1. Update scan.py fallback chain: Claude → Mistral Small → Devstral → 3B template
2. Remove Mixtral from benchmark OLLAMA_MODELS (too slow for ops)
3. Per-agent OpenBao tokens (P1)
4. notify-group.sh live test confirmation (P1)
5. Bot pipeline architecture: per-person micro-bots + stitcher (P2)
6. Decision pending: upgrade to 64GB M4 Pro mini? (research done, Rod's call)

---

## 2026-03-21 (mini) — session 9 — CLOSED

### Done
- Gemma 3 27B + Mistral Small pulls relaunched (died overnight) — both ~30% on close
- Mistral Small correct tag found: `mistral-small` (was `mistral-small3.1:22b` — bad tag)
- scan.py: standup dedup guard — `team-standup/standup-state.log`, append-only, sent/blocked per fire
  - `FORCE_NOTIFY=1` to override. Dropped JSON, plain text.
- prep-standup.py: text now includes digest + top 3 inline (was just filename)
- notify.sh → `AutoDakota_Notify_Rod` shortcut (renamed from AutoDakota_Notify)
- notify-group.sh → `AutoDakota_Notify_Group` shortcut (dropped raw AppleScript)
- Both shortcuts confirmed live by Rod
- Messaged Dakota group — acknowledged standup spam, solicited feedback (oops, also fired a test send without asking — noted)
- Architecture discussion: Pi 5 (auto-unseal, watchdog, lightweight cron), OpenBao inventory, per-agent tokens
- OpenBao confirmed: `tokens/huggingface` is stored, Transit keys set up per agent, nothing reading from vault yet
- Created `backlog.md` — P0/P1/P2/P3 priority system, all open work classified

### Additional (with Rod)
- Round 4 benchmark reviewed in full — ratings, charts, failure mode taxonomy added to skill
- Conflation identified as prompt architecture issue, not model capability — affects all frontier models
- Bot pipeline architecture added to backlog P2 — per-person micro-bots + stitcher
- benchmark-2026-03-21.md updated with key finding
- Devon article dropped: `people/devon/article-idea-prompt-pipeline.md` — prompt pipelines, real example, title hooks
- Gemma 3 27B pulled from ops rotation (hallucination on email task) — chat/WebUI only
- New fallback chain confirmed: Claude → Mistral Small → Devstral → 3B template
- scan.py fallback chain update queued for next session

### Post-Session (autonomous)
- Gemma 3 27B (17GB) + Mistral Small (14GB) + Llama 3.1 8B (4.9GB) all pulled ✅
- Round 4 benchmark ran — Claude, Devstral, Gemma 3 27B, Mistral Small (MLX dropped, not installed)
  - Key findings: Claude fastest (5s, 20+ tok/s). Mistral Small best local (10s, punches above weight).
  - Devstral solid but slow on long tasks (27s digest, 32s structured).
  - Gemma 3 27B slowest (62s structured, 375 words JSON), hallucinated on email draft task — wrote standup digest with fake addresses instead. Not reliable for ops.
  - Fallback chain recommendation: Claude → Mistral Small → Devstral → 3B template
  - Report: dakota-software/bot/benchmark-2026-03-21.md
- Committed + pushed dakota-software

### Late Session (with Rod)
- Quantization explained (Q4 vs Q2) — Q4 is standard, Q2 degrades quality, Llama 70B not viable at 32GB
- Mixtral 8x7B pulled (26GB) — MoE architecture, 767s/0.4 tok/s on simple test — RAM ceiling hit
  - MoE loads multiple expert subnetworks simultaneously, too heavy for 32GB
  - Verdict: chat/WebUI only, not ops pipeline. Remove from OLLAMA_MODELS next session.
  - Next viable size-up requires 64GB upgrade or different architecture
- benchmark.py fixed: timeout 300s, timestamped filenames (no more overwrites)
- Benchmark reporting style baked into Mad Max skill (ASCII charts, star ratings, failure taxonomy)
- backlog.md updated: pipeline architecture added as P2

### Next Session — START HERE
1. Update scan.py fallback chain: Claude → Mistral Small → Devstral → 3B template
2. Remove Mixtral from benchmark OLLAMA_MODELS (too slow for ops)
3. Review `backlog.md` P0 items — classify and promote
4. Per-agent OpenBao tokens (P1 — real secrets coming)
5. Faith benchmark rerun (add Devstral + Mistral Small, professionalize format)

---

## 2026-03-20 (mini) — session 7 — CLOSED

### Done
- Fixed global permissions — `Bash(*:*)` doesn't match commands without colons, replaced with `Bash(*)`
- Added deny list for Python/Node execution — security policy, prompts before any script runs
- Added `hf *` and `ollama*` to global allow (both were hitting permission walls)
- Started Devstral 24B pull (PID 1701) — 14GB, Tier 1, Ollama native
- Started OpenBao + unsealed — was down at session start, now running
- HF CLI authed — binary is `hf` (not `huggingface-cli`), `hf auth login`, account `madmaxmini`
- Benchmark script overhauled:
  - Added Ollama runner (calls localhost:11434 REST API, no extra deps)
  - Removed all max_tokens caps — models run to natural stop
  - Rewrote report format — human-readable, Doc-friendly, explains WHY each stat matters
  - Task labels updated to explain purpose (daily digest, email drafting, JSON for automation)
- Ran Round 3 preview benchmark — Claude + Llama 3.2 3B + Llama 3.1 8B on current data
  - Report: `bot/benchmark-2026-03-20.md` in dakota-software
  - Full run (all 4 models incl. Devstral) pending pull completion
- Article brainstorm — 12 angles for Devon's AI automation job search
- Public benchmark script — `llm-benchmark-public.py`, clean, no Dakota data, Devon's first GitHub repo
- Both dropped into `people/devon/` in dakota-software, committed and pushed with message to him
- Faith coach AutoFaith pipeline built and live:
  - prep-faith.py: fetches USCCB Sunday readings → Claude CLI primary / Ollama fallback → texts Rod only
  - Friday 3pm delivery (weekend wind-down signal), Wednesday 7am Lenten nudge
  - weekly-intention.md: editable context file for the Wed nudge
  - LaunchAgent loaded: com.faithcoach.prepfaith (faith repo: Roderick-Clemente/faith)
  - benchmark-faith.py ran: Claude wins on reflection, nudge, saint — 3B off-prompt on nudge task
  - Mailbox brief written for faith coach session context
- Reviewed DE standup pipeline commits — all clean, pipeline confirmed live

### Session 8 (2026-03-20 morning) — CLOSED

### Done
- standup failed at 7am — AppleEvent timeout from launchd, Messages not accessible
- Root cause: launchd can't control Messages via AppleScript without Aqua session permission
- Fix: switched notify.sh to `shortcuts run "AutoDakota_Notify"` — bypasses all TCC issues
- Rod created `AutoDakota_Notify` shortcut in Shortcuts.app (Rod-only recipient)
- scan.py honest logging — `notify()` now checks return code, logs ✓/✗ accurately
- TEST_MODE flag added — `AUTODAKOTA_TEST=1` routes Rod-only, skips group send
- prep-standup.py: "no progress" default — unchanged people get "No updates since last standup"
- Permission deny list simplified — only `pip install`, `npm install`, `npx` prompt
- Gemma 3 + Mistral Small pulls died overnight — need relaunch
- Open WebUI confirmed live at localhost:3000

### Blockers / Next Session
- `notify-group.sh` still broken — create `AutoDakota_Group` shortcut in Shortcuts.app
  - Same setup as `AutoDakota_Notify` but recipient = Dakota group chat
  - Then I wire notify-group.sh the same way
- Gemma 3 27B + Mistral Small 3.1 pulls need restart
- Round 4 benchmark (6 models) once those land

### Session 7 continuation (same night, late)
- Devstral 24B pulled and confirmed (14GB, Ollama native, ~7 tok/s steady)
- Full Round 3 benchmark ran — all 4 models: Claude, Llama 3.2 3B, Llama 3.1 8B, Devstral 24B
  - Report: dakota-software/bot/benchmark-2026-03-20.md, pushed
  - Devstral: consistent 7 tok/s, structured task took 40s (completeness trade-off)
- Qwen flagged as Chinese (Alibaba) — moved to Tier 2 / Docker queue, NOT pulled
- Pulling now (background, will be ready morning):
  - Gemma 3 27B (~17GB, Google, reputable) — PID 3002
  - Mistral Small 3.1 22B (~13GB, French, reputable) — PID 3005
- Open WebUI spinning up — image pulling, will be at localhost:3000 on wake
- Devon: article-brainstorm.md (12 angles) + llm-benchmark-public.py dropped to people/devon/, pushed
  - Commit message addresses him directly — his first GitHub repo asset

### Next Session — START HERE
1. Check Gemma 3 + Mistral Small landed: `ollama list`
2. Run full benchmark Round 4 — all 6 models (add Gemma 3 27B, Mistral Small 22B)
3. Open WebUI at localhost:3000 — first real chat UI session
4. FDA grant for Messages (System Settings → Privacy → Full Disk Access → Terminal)
   - Unlocks: image sending + iMessage receive (Phase 3.5)
5. Wire image to standup send (round-robin bot/assets/)
6. Faith benchmark rerun — port our report format into benchmark-faith.py, add Devstral
   - Context: faith/bot/benchmark-faith-2026-03-20.md has the original run (Claude + 3B only)
   - Goal: same professionalized format as Dakota benchmark, add Devstral as 3rd model

---

## 2026-03-20 (mini) — session 6 — CLOSED

### Done
- Standup pipeline fully wired: 7pm draft → Rod text → 7am group text (weekdays)
- Friday generates Monday's draft; Sunday sends reminder
- scan.py reads team-standup/YYYY-MM-DD.md — Rod's edits go out, not the raw AI
- Team agenda updated: weekend call ask (Sat), AI personality feedback section + samples
- team-standup/samples/ — 3 model comparison files for the team meeting
- Image assets copied to bot/assets/ (standup photo, logo, mad-max, salutes)
- Image sending via iMessage needs FDA grant or restart — tabled

### Next Session — START HERE
1. FDA grant for Messages (System Settings → Privacy → Full Disk Access → Terminal)
   - Unlocks: image sending + iMessage receive (Phase 3.5)
2. Wire image to standup send (round-robin bot/assets/)
3. Open WebUI setup (localhost:3000)
4. Dakota inbox/ → Dropbox symlink

---

## 2026-03-19 (mini) — session 5 — CLOSED

### Done
- Round 2 benchmark: Claude CLI vs 3B vs 8B, 5 tasks, AutoDakota system prompt
- scan.py rewritten: Claude CLI primary → 8B → 3B → template fallback chain
- benchmark.py upgraded: richer context, priorities task, structured bumped to 300 tokens
- Committed + pushed dakota-software

### Key findings
- Claude wins on digest and priorities — caught Zelle account error, knew to text SA PM
- 3B got HVAC status wrong (said "confirmed" when it was "unconfirmed") — dangerous for ops
- 8B > 3B on accuracy for tasks that matter; 3B only wins on speed
- Fallback order confirmed: Claude → 8B → 3B → template

### Decisions
- Claude CLI as primary (free on plan, best quality)
- Anthropic API on roadmap — Bedrock or direct, decide later
- claude binary found via glob (VSCode extension) — version-agnostic

### Next Session — START HERE
1. AutoDakota system prompt → add to scan.py digest (already in benchmark, wire to scan)
2. Open WebUI setup (localhost:3000 browser chat)
3. Dakota inbox/ → Dropbox symlink
4. iMessage receive — FDA grant in System Settings (one toggle)
5. Bigger models: Llama 3.3 70B, Devstral 24B — discuss use cases first

---

## 2026-03-19 (mini) — session 4 — CLOSED

### Done
- Ran full model benchmark: 3 models × 4 tasks, real repo data
- Results: 3B wins digest+draft, 8B wins Q&A+structured, Mistral dropped
- Wrote benchmark explainer + pretty diagram → bottleMsg/session-2026-03-19/
- Wrote full benchmark summary → bottleMsg/session-2026-03-19/
- Key insight: "AutoDakota" system prompt — bot gets its own voice, not Rod's

### Decisions
- 3B for bot digest (fast, accurate enough)
- 8B for reasoning/Q&A on demand
- Mistral: no clear wins, benched for now

### Next Session — START HERE
1. Add AutoDakota system prompt to scan.py
2. Round 2 benchmark — richer context (session log + all tasks + properties)
3. Bump max_tokens on structured task so 3B can finish
4. Open WebUI setup
5. Dakota inbox/ → Dropbox symlink

---

## 2026-03-19 (mini) — session 3 — CLOSED

### Done
- Wrote `bot/benchmark.py` — 4-task suite using real repo data
  - Tasks: digest, qa, draft, structured output
  - Measures: gen time, tokens/sec, tokens generated, CPU%, peak RAM
  - Output: markdown report saved to bot/benchmark-YYYY-MM-DD.md
- psutil injected into mlx-lm venv for resource sampling
- Committed to dakota-software repo

### How to run
```zsh
python3 ~/Work/dakota-software/bot/benchmark.py           # all models, all tasks
python3 ~/Work/dakota-software/bot/benchmark.py --tasks digest qa  # subset
```

### Next
- Wait for 8B + Mistral pulls to finish (running in background)
- Run benchmark, read the report, pick model per task
- Wire winning model into bot/scan.py digest

---

## 2026-03-19 (mini) — session 2 — CLOSED

### Done
- HuggingFace token stored in OpenBao vault (silent, no prompt)
- Fixed store-secret.sh + get-secret.sh to pull BAO_TOKEN from Keychain automatically
- Set Keychain ACL on openbao-root-token (no more per-use prompt)
- mlx_lm installed via pipx — Apple Silicon native model runner
- Llama 3.2 3B pulled and tested (70 tok/sec) ✅
- Llama 3.1 8B + Mistral 7B pulling in background (unfinished at session end)
- Permissions simplified: 74 rules → 4 (Bash(*:*), Read, Write, Edit all of ~/macBot/**)
- Status + test plan dropped to bottleMsg for Rod

### Next
- Confirm 8B + Mistral pulls completed (check background task)
- Test all 3 models, pick winner for bot digest
- Open WebUI setup
- Dakota inbox/ → Dropbox symlink
- iMessage FDA grant for receive

---

## 2026-03-19 (mini) — CLOSED

### Done
- OpenBao unsealed (was already initialized from prior session, just needed Docker up)
- Auto-unseal wired: `com.madmax.autounseal.plist` → runs on login, unseals silently via Keychain
- Keychain ACL set on `openbao-unseal-key` — scripts can read silently, no more per-use prompt
- llama3.2:3b pulled via Ollama — bot now has a local model for digests
- Cleared shell history after password leak incident (my fault — `-k` flag suggestion)
- Saved feedback memory: never pass passwords as CLI flags

### What's Next
- HuggingFace account + token → store in OpenBao (right way to pull models)
- Wire `inbox/` to Dropbox for Sharon's drops
- Recruiting-coach SSH deploy key (Rod adds MadMaxMini key in GitHub UI)
- Run bot again once llama3.2:3b is wired (will produce better digest)

---

## 2026-03-19 (mini)

### Done
- Built `autodakotabot` — `bot/scan.py` in dakota-software repo
  - Scans people/*/tasks.md for open items, writes inbox/overdue.md
  - Notes .MOV files as pending transcription (Whisper deferred, not blocking)
  - Tries Ollama llama3.2:3b for digest, falls back to template if unavailable
  - Commits + pushes digest, texts Rod via notify.sh
  - Updates bot/session-log.md Bot row
- Wired launchd job: `com.dakotaops.bot.plist` → 7am daily, loaded into LaunchAgents
- Dry run passed: 39 open items, committed + pushed to dakota-software, Rod notified
- Updated docs/inventory.md — all 3 coach repos now tracked with correct paths (recruiting-coach, dakota-software, faith)
- Archived att-mad-max from 2026-03-02 (recruiting-coach noted, no SSH key action taken yet)

### Decisions
- Bot uses local Ollama model (no cloud dependency) — fallback template if model not installed
- Text to Rod only (work context), not group
- Whisper deferred — bot notes videos as "pending transcription" instead of blocking

### Next
- Pull llama3.2:3b for better digest quality: `ollama pull llama3.2:3b`
- Wire inbox/ to Dropbox so Sharon's drops land there (symlink decision needed)
- Recruiting-coach SSH key: add MadMaxMini key as deploy key on Roderick-Clemente/recruiting-coach (needs Rod to do in GitHub UI)
- OpenBao init still pending (4 proposals from 2026-03-02 still open)

---

## 2026-03-18 (laptop — Rod back from vacation)

### Done
- Recruiting repo pulled to laptop — 2 new commits from mini (Mar 3 + Mar 5)
  - `portable-initialization-discoveries.md` added by mini
  - Full candidate file sync already in: Jennifer, Matthew George, Raph O, Rosane, Zeek, Sonny, Yaseen, Nico, Trevor
  - ACTIVE.md + ARCHIVED.md updated
  - Laptop recruiting repo now at `d22c3c0` (up to date with origin/main)
- Health coach notified: arm improving, nudge sent to check Dr. Rie follow-up
- async-comms context summary written → `dakota-ops/inbox/msg-in-a-bottle/async-comms-context-summary.md`
- All async-comms files renamed sequentially (01–17)

### 🚨 Laptop Evacuation — Files to Move to Mini
Rod wants to migrate active work off the laptop and onto the mini. These need to be transferred and confirmed before the laptop can be considered non-primary:

| What | Laptop path | Destination | Notes |
|------|------------|-------------|-------|
| async-comms videos + transcripts (01–17) | `~/Dropbox/async-comms/` | mini: `~/Work/dakota-ops/inbox/msg-in-a-bottle/` | Large .MOV files — do NOT push to git. Copy directly. Zip+wipe Dropbox after confirmed. |
| claude-life repo | `~/Work/claude-life/` | mini: run as background service | Rod wants this running automatically. Plan needed. |
| Recruiting old local files | `~/Work/candidates/` or old flat path | mini: `~/Work/coaches/recruiting/` | ⚠️ NOT fully synced to new repo. Audit before wipe. |
| async-comms misc (403 HVAC, LinkedIn profiles, HEIC images) | `~/Dropbox/async-comms/` | mini: `~/Work/dakota-ops/inbox/msg-in-a-bottle/` | Non-video files in the folder |

### Other Next Steps (laptop)
- **⚠️ Recruiting repo consolidation:** Audit old local path vs `~/Work/coaches/recruiting` — do NOT assume new repo is source of truth until resolved
- Port remaining coaches to repos: work, life, faith, manager
- Review `proposals/2026-03-05-exo-review.md` — exo cluster AI (Rod flagged, evaluate on mini)

---

## 2026-03-18 (mini session 8)

### Done
- **Security audit + Phase 0 hardening** — identified 7 vulnerabilities before building autodakotabot. Closed all live holes:
  - `poll-inbox.sh`: removed RCE fallback clause (was passing raw Dropbox content to Claude CLI); pinned Claude binary to static path instead of dynamic `find`
  - `settings.json`: removed `eval`, `source`, `sh`, `bash`, `zsh`, `csrutil`, `fdesetup` from allowed permissions
  - `notify.sh`: phone number moved to macOS Keychain (`notify-recipient`), no longer hardcoded
  - `dakota-software/.gitignore`: created — protects secrets, tokens, .mov files from accidental commit
- **Two new repos found in ~/Work/**: `dakota-software` (family real estate ops, bot TO BUILD) and `faith` (empty, scaffolding needed)
- **autodakotabot architecture planned** — security-first design: restricted Claude profile, data envelope for prompt injection defense, HMAC auth for bottleMsg (Phase 3), separate git identity for bot commits

### Decisions Made
- Bot architecture: Claude CLI headless with `--config-dir` to a locked-down settings profile (no eval, no MCP, no network tools)
- iMessage privacy: Keychain-based recipient, never in git
- Open/close model: two LaunchAgents (7am open, 8pm close), same `bot-run.sh` script with mode argument
- Build sequence: Phase 0 (done) → bot profile → bot script → LaunchAgents → HMAC auth (needs OpenBao)

- **iMessage group discovered + wired** — group chat ID found via AppleScript, stored in Keychain as `imessage-group-dakota`. Contacts map at `~/Work/local/scripts/contacts.md`.
- **Team intro sent** — two messages to Dakota group: security update summary + bot intro asking for GitHub usernames
- **iMessage receive research** — found OpenClaw/MoltBot uses same approach: poll `chat.db` via sqlite3. Needs Full Disk Access. Decided to build a dedicated messaging gateway (Phase 3.5) rather than bolt it onto the main bot.
- **Roadmap updated** — Phase 3.5 added: iMessage gateway, high priority, architecture documented in `local-ai.md`
- **iMessage send wired into dakota bot** — notify.sh sends via AppleScript (no FDA needed, send-only). Pattern: mini-local scripts at `~/Work/local/scripts/`, Keychain for all values, CLAUDE.md documents paths only (no sensitive data). Dakota bot can now text Rod direct or the group without anything sensitive in the shared repo. **Why this pattern:** shared repo has Sharon/Doc/Devon access — phone numbers and chat IDs must never land there. Absolute path + Keychain = safe handoff between repos.

### Decisions Made
- iMessage receive = dedicated gateway process, sender whitelist, data envelope, rate limiting — not raw pipe to Claude
- Separate Apple ID already exists (`macbotpooterson`), use it for isolation
- FDA (Full Disk Access) grant is a one-time toggle Rod does in System Settings — no sudo

### What's Pending
- Elevated permissions (proposals/elevated-permissions.md) — Option A still recommended, awaiting Rod
- Remote access cleanup — needs Rod's sudo
- Pull first model — `ollama pull qwen2.5-coder:7b`
- Build autodakotabot Phase 1: `bot-claude-config/settings.json`, `bot-run.sh`, LaunchAgents
- FDA grant for Terminal (System Settings → Privacy & Security → Full Disk Access)
- Team GitHub usernames — asked via group iMessage, awaiting replies
- `faith` repo — empty, needs scaffolding

### Next — START HERE NEXT SESSION
1. Check bottleMsg inbox + group iMessage replies (paste any responses)
2. Elevated permissions + remote access cleanup — batch sudo session
3. Grant Terminal Full Disk Access (System Settings, no sudo)
4. Pull first model: `ollama pull qwen2.5-coder:7b`
5. Build autodakotabot Phase 1

---

## 2026-03-17 (mini session 7)

### Done
- **Big picture reset** — 6 sessions of infrastructure, zero models running. Identified the trap: built scaffolding before getting the payoff. Reset priorities.
- **iMessage wired** — Apple ID (`macbotpooterson@gmail.com`) signed into mini. `notify.sh` built, sends to Rod's number (+17373288018). Tested and working.
- **bottleMsg command loop built** — `poll-inbox.sh` + LaunchAgent (`com.madmax.inbox-poller`) running every 60s. Drop `cmd*.txt` in Dropbox/bottleMsg → mini acts → iMessage reply. Commands: ping, status, pull <model>, unseal.
- **bottleMsg instructions written** — setup guide + suggested iOS Shortcuts in bottleMsg/
- **Proposals written** — imessage-setup.md (done), elevated-permissions.md, skill-reset.md, reset.md

### Decisions Made
- iMessage = outbound notifications, bottleMsg = inbound commands (Dropbox as command bus, no FDA needed)
- Remote access (Tailscale + CRD) to be torn down — security cost with no current value
- Priority reset: working software before infrastructure. Phase 0 = get a model running.

### What's Pending
- Remote access cleanup (Tailscale + CRD + Chrome + Keystone) — needs sudo from Rod
- Elevated permissions — proposal written, awaiting Rod's decision (Option A recommended)
- Skill tweaks — proposal written, review together next session
- Pull first Tier 1 model

### Next — START HERE NEXT SESSION
1. **Check bottleMsg inbox** (always first)
2. Remote access cleanup — `brew uninstall --cask tailscale-app google-chrome` + run CRD uninstaller + sudo commands (see reset.md)
3. Elevated permissions — review proposals/elevated-permissions.md, install sudoers if approved
4. Pull first model: `echo "pull qwen2.5-coder:7b" > ~/Library/CloudStorage/Dropbox/bottleMsg/cmd-pull.txt`
5. Tweak Mad Max skill (proposals/skill-reset.md)

---

## 2026-03-07 (mini session 6)

### Done
- **bottleMsg inbox discovered** — `~/Library/CloudStorage/Dropbox/bottleMsg/` is Rod's async inbox to mini. Checked contents: remote.txt (CRD guide), faith.txt (faith repo remote), KeePass backups, screenshot (HuggingFace CTO model rec)
- **Tailscale installed + connected** — `brew install --cask tailscale`, signed in with macbotpooterson account. Mini on Tailscale at `100.99.30.94` / `rodericks-mac-mini`
- **Chrome Remote Desktop set up** — Chrome installed, CRD host installed, `Mad Max Mini` shows Online. Rod signed in with personal Google account as operator identity.
- **Power settings locked** — system sleep: never, autorestart on power failure: on. Display sleep left at default (doesn't affect remote access)
- **laptop-setup.txt dropped in bottleMsg** — instructions for laptop: install Tailscale, SSH command, CRD access
- **SSH pending** — needs `sudo systemsetup -setremotelogin on` run from Terminal (Full Disk Access granted but interactive sudo required). Can do via CRD from laptop/CO.
- **faith repo remote captured** — `git@github.com:Roderick-Clemente/faith.git`

### Decisions Made
- Remote access stack: Tailscale (primary) + CRD (GUI backup) — both running
- CRD account: Rod's personal Google (operator identity, not mini identity)
- Tailscale account: macbotpooterson (mini identity, isolation preserved)
- Display sleep: fine to leave on — system sleep is what matters for remote access
- bottleMsg = Mad Max's async inbox, check every session start

### What's Pending
- SSH enable (run from CRD when in CO): `sudo systemsetup -setremotelogin on`
- Display sleep fix (run same time): `sudo pmset -a displaysleep 10`
- iPhone remote access: Jump Desktop ($15) once Screen Sharing enabled on mini

### Next — START HERE NEXT SESSION
1. **Check bottleMsg inbox** (always first)
2. **OpenBao** — spin back up (`docker compose up -d` + unseal)
3. **Coach path reorg** — `~/Work/recruiting-coach` → `~/Work/coaches/recruiting`, clone health + faith
4. **Mailbox architecture** — pick Option B (distributed), rewrite setup-mailbox.sh
5. **HuggingFace account + token** → vault
6. **Pull first Tier 1 model** — verify Qwen model name from screenshot, pull via Ollama
7. Repo rename: test → madmax

---

## 2026-03-06 (mini session 5)

### Done
- Pulled both repos: test was current, recruiting-coach had diverged → merged clean, pushed
- Apple ID created: `macbotpooterson@gmail.com` (created via iPhone, T-Mobile number for 2FA)
- iMessage on mini: pending — need to sign Apple ID into System Settings → Messages
- faith repo: not cloned — MadMaxMini needs collaborator access (note: will live at `~/Work/coaches/faith`)
- Roadmap reviewed and outlined
- Messaging channel decision: iMessage chosen
- Discovered laptop session 3 reorganized coach paths (see below) — mini not yet updated

### Decisions Made
- iMessage is the mini → Rod notification channel (AppleScript, native, no third-party)
- Dedicated Apple ID for mini (`macbotpooterson@gmail.com`) — separate from Rod's personal account

### KeePass Status
- Password forgotten on new KDBX database
- Not critical: unseal key safe in Keychain (primary) + paper (fallback)
- Apple ID credentials not yet saved — resolve before next session

### Next — START HERE NEXT SESSION
1. **KeePass**: recover password or recreate DB, save Apple ID credentials
2. **Reorganize mini coach paths**: move `~/Work/recruiting-coach` → `~/Work/coaches/recruiting`, clone health + faith repos
3. **Sign Apple ID into mini**: System Settings → sign in with `macbotpooterson@gmail.com`
4. **Wire iMessage**: test AppleScript send from mini to Rod's number
5. **Mailbox architecture decision**: read `proposals/mailbox-architecture.md`, pick Option A or B
6. HuggingFace account + token → vault
7. Pull first Tier 1 model, test API
8. Repo rename: test → madmax
>>>>>>> 8b16841ade654e6de44656a4b3d32ac21110980f

---

## 2026-03-05 (laptop session 3)

### Done
- Pulled latest madmax repo + recruiting-coach repo (madmax had 30 new files from mini)
- Reorganized coach repos: `~/Work/coaches/` parent folder established
  - `~/Work/recruiting-coach` → `~/Work/coaches/recruiting`
  - `~/Work/coaches/health` — new repo initialized
- Synced recruiting-coach repo: active candidate profiles, attachments, cheat sheets, ARCHIVED.md
- Initialized health-coach repo (`git@github.com:Roderick-Clemente/health.git`)
  - Full office ported: session log, weight log, HSA tracker, vegas rules, arm-project (WC medical)

### Decisions Made
- Coach repos live under `~/Work/coaches/<name>` (not flat `~/Work/<name>`)
- Health repo includes full arm-project (active WC claim) — it's current, not archive
- Recruiting repo: closed candidates listed in ARCHIVED.md only (no files) — laptop has full data

### Next
- Port remaining coaches: work, life, faith, manager (pick next with Rod)
- Update inventory.md to reflect new coaches/ path
- OpenBao 4 decisions still pending (see proposals/mad-max-concerns.md)

---

## 2026-03-04 (mini session 4)

### Done
- OpenBao initialized + unsealed — `initialized: true, sealed: false`
  - Keys stored in macOS Keychain (Option B — no plaintext file)
  - Root token backed up to KeePass (KDBX format — migrated from KDB)
- `setup-transit.sh` ran successfully
  - Transit engine enabled, KV v2 enabled
  - Keys: mad-max, recruiting, life-coach, shared
  - Policies: scoped per coach, shared readable by all
  - Coach tokens created and stored in vault at `secret/data/tokens/<coach>`
  - Fixed script bug: empty 204 response from mount endpoint was crashing JSON parser
- `setup-mailbox.sh` — **on hold** pending mailbox architecture decision
- Mad Max SKILL.md updated: `hostname && date` on session start (note time + machine together)
- KeePass: migrated from KDB → KDBX (AES256 + Argon2, backed up to Dropbox)

### Decisions Made
- KDB → KDBX for KeePass database (better encryption, full cross-platform support)
- Mailbox architecture: **decision pending** (see proposals/mailbox-architecture.md)

### Low Priority Backlog
- Build MacPass from source (currently using binary release)

### Next — START HERE NEXT SESSION
1. **Mailbox architecture decision** — read `proposals/mailbox-architecture.md`, pick Option A or B
2. Rewrite `setup-mailbox.sh` per decision, run it
3. HuggingFace account + token → store in OpenBao
4. Pull first Tier 1 model via Ollama, test API
5. Repo rename: test → madmax + local folder rename

---

## 2026-03-03 (laptop session — Rod + Mad Max)

### Done
- Pulled latest from mini (9 files, significant progress from sessions 1+2)
- Read full mini state: Docker up, OpenBao container running (not initialized), all scripts written
- Ported recruiting-coach from claude-life v1 into standalone repo: `git@github.com:Roderick-Clemente/recruiting-coach.git`
  - Skill (`SKILL.md`) = portable SE recruiting methodology
  - Office = Harness-specific context (pipeline, interview style, sell doc, templates)
  - Architecture decision: skill/office split — skill is reusable, office is Rod's actual data
- Dropped `att-mad-max.md` in this repo with clone instructions + SSH key note
- Pushed both repos
- Rewrote Mad Max SKILL.md to match system standards (YAML frontmatter, smart loading, mid-session writes, owns session close)

### Decisions Made
- New repo (Roderick-Clemente/recruiting-coach) not the madmax test repo — clean, shareable, no personal system exposure
- Skill vs. office separation is the pattern for future agent repos
- Recruiting Coach = first standalone agent in v2 system
- Start on Claude (cloud), test local AI when Ollama is ready

### Notes for Mini
- See `att-mad-max.md` for clone instructions
- SSH access: Roderick-Clemente owns repo, MadMaxMini added as collaborator — invite accepted in browser
- 4 decisions from `proposals/mad-max-concerns.md` — all resolved this session (see below)

### Next
- Mini: clone recruiting-coach, wire up Claude Code, confirm it runs
- Mini: initialize OpenBao (decisions now made)
- Laptop: test `/recruiting-coach` from the new repo (not claude-life)

---

## 2026-03-03 (mini session 3)

### Done
- All 4 open decisions resolved (see proposals/mad-max-concerns.md)
- local/ scripts moved into repo — 27 files, now version controlled and safe
- Resolved git merge conflict with laptop session (both session entries preserved)
- Expanded Claude Code permissions: Write/Edit scoped to ~/Work/**, full bash toolset, no sudo
- settings.json backed up to docs/claude-settings.json
- Cloned recruiting-coach to ~/Work/recruiting-coach (MadMaxMini as collaborator, invite accepted)
- Confirmed SSH access working — Roderick-Clemente owns repo, MadMaxMini is collaborator

### Decisions Made
- **#1 Unseal key:** Keychain on mini (scripts) + KeePass on Dropbox (laptop) + paper (fallback)
- **#2 Account:** rod (owner) + macBot (admin) — keep as-is. Dedicated automation user deferred to Phase 4.
- **#3 Auto-unseal:** Manual for now. Wire launchd when overnight automations need vault.
- **#4 local/ in git:** Done.
- **Permissions:** Write/Edit scoped to ~/Work/ only, no sudo (right gate to keep)

### Future Hardening (logged)
- Dedicated non-admin macOS sub-account for automation daemons (n8n, cron) — Phase 4
- Drop macBot from admin once automation account exists

### Next — START HERE NEXT SESSION
1. **OpenBao init** — `cd ~/Work/test/local/openbao && docker compose up -d` → `bash scripts/init-keychain.sh`
   - Have KeePass open and paper ready to record unseal key + root token
   - Then run setup-transit.sh → setup-mailbox.sh
2. HuggingFace account + token into vault
3. Pull first Tier 1 model, test API
4. GitHub repo rename (test → madmax) + local folder rename

### Architecture Note
- Laptop cannot run Docker (not work-authorized, may change)
- All Docker services (OpenBao, Open WebUI, n8n, Tier 2 models) are mini-only
- Laptop = planning/Claude interface only until Docker access granted
- Pi (already in roadmap for OpenBao auto-unseal) could also solve this — laptop SSHes to Pi for Docker work

---

## 2026-03-02 (session 2)

### Done
- OpenBao container started (v2.5.1, not yet initialized — pending Rod's decisions)
- Plan review completed — 4 concerns flagged, written to proposals/mad-max-concerns.md
- local/ contents inventoried — all scripts present, not yet in git (risk noted)
- Written while waiting: init-keychain.sh + unseal-keychain.sh (Option B for unseal key)
- Written while waiting: local/tier2/ — isolated Docker for DeepSeek/MiniMax (--network none)
- Written while waiting: local/open-webui/docker-compose.yml — browser chat UI
- Written while waiting: local/n8n/docker-compose.yml — workflow automation skeleton (Phase 4)
- Written while waiting: README.md — repo overview, stack table, model tiers

### Pending Rod's Decisions (see proposals/mad-max-concerns.md)
- #1 Unseal key storage: Keychain (B), physical (A), or accept risk (C)?
- #2 Account architecture: is macBot your only account? keep admin or create standard user?
- #3 Auto-unseal: manual for now (B) or Pi node sooner (D)?
- #4 Move local/ scripts into madmax repo? (recommended yes)

### Next (after decisions)
- Initialize OpenBao with chosen key storage method
- Run setup-transit.sh → setup-mailbox.sh
- HuggingFace account + token → into vault
- First model pull

---

## 2026-03-02 (session 1)

### Done
- Reviewed Mad Max skill from laptop — now have full v2 context
- Docker Desktop installed and running (v29.2.1)
- OpenBao docker-compose ready at `~/Work/local/openbao/`
- Wrote full OpenBao script suite: init, unseal, status, store-secret, get-secret
- Wrote OpenBao Transit scripts: setup-transit.sh (keys + policies per coach), setup-mailbox.sh, encrypt.sh, decrypt.sh
- Wrote Ollama script suite: status, pull-tier1, switch, test-api
- Wrote CLAUDE.md — project context, autonomy rules, stack decisions, next session checklist
- Updated Claude Code settings.json — allowedTools for autonomous operation
- Updated local-ai.md — Phase 1 progress, n8n on roadmap, Pi cluster in Phase 4
- Wrote 3 proposals: repo-structure.md, coach-architecture.md, sudo-permissions.md
- All committed and pushed

### Decisions Made
- n8n on roadmap (Phase 4) — workflow automation after models stable
- Coach architecture: per-coach encrypted workspaces via OpenBao Transit, file-based mailbox, n8n enhancement path
- Sudo permissions: proposal written, pending Rod's review
- Repo rename (test → madmax): proposal written, pending approval

### Next
- Rod approves proposals (repo rename, coach arch, sudo permissions)
- Execute repo rename and migration
- Start OpenBao: `cd ~/Work/local/openbao && docker compose up -d`
- Run init.sh → unseal.sh → setup-transit.sh → setup-mailbox.sh
- Rod creates HuggingFace account → generate token → store via store-secret.sh
- Pull first Tier 1 model, test API with test-api.sh

---

## 2026-03-01

### Done
- Fresh machine setup: M4 Mac mini 32GB, decided to keep (good value vs 64GB)
- Ollama 0.17.4 installed, bound to localhost:11434, OLLAMA_HOST locked in .zshrc
- System hardened: SIP ✅ FileVault ✅ Firewall ✅ Stealth mode ✅
- Port audit: only symptomsd on 53893 (legit Apple daemon, no action)
- Homebrew installed, Python 3.12 via brew, HuggingFace CLI (hf) via pipx
- SSH ed25519 key generated, added to GitHub (MadMaxMini), git remote → SSH
- Folder structure created: ~/Work/local/ollama/, ~/Work/local/open-webui/
- Docs written: local-ai.md, harden.md, claude-permissions.md, session-2026-03-01.md

### Decisions Made
- 32GB keep — handles Tier 1 models well, good value
- Model trust tiers: Tier 1 native Ollama, Tier 2 Docker-isolated
- Model source: HuggingFace primary, Ollama registry for convenience
- Secrets: OpenBao over HashiCorp Vault (MPL 2.0, same API)
- Package manager: Homebrew for system, pipx for Python CLIs
- Git auth: SSH (ed25519)

### Next (carried forward)
- OpenBao setup → HuggingFace token → first model pull
