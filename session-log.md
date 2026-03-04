# Session Log

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
