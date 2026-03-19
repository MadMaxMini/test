# Session Log

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
