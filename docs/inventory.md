# Asset Inventory

Where everything lives and what it does.
Last updated: 2026-03-02

> **Note for Claude:** This file is a reference map only. Do NOT proactively read
> the files listed here unless explicitly needed for the current task. Know they exist,
> load them on demand.

---

## Repo (~/Work/test/ → github:MadMaxMini/test)

```
.claude/
  skills/
    mad-max/SKILL.md         # Mad Max persona — platform builder, dual-context startup

proposals/
  repo-structure.md          # Proposal: rename test→madmax, consolidate local/ into repo
  coach-architecture.md      # Proposal: encrypted coach workspaces + mailbox system
  sudo-permissions.md        # Proposal: targeted sudoers for Claude autonomy
  mad-max-concerns.md        # 4 open decisions blocking OpenBao init (NEEDS ROD)

docs/
  inventory.md               # this file

local-ai.md                  # Local AI roadmap — model tiers, phases, hardening checklist
harden.md                    # System hardening log — what's done, what's pending
claude-permissions.md        # Claude Code permissions — open questions + action plan
session-log.md               # Rolling session summary (newest first)
CLAUDE.md                    # Claude Code context — autonomy rules, stack, next steps
README.md                    # Repo overview
```

---

## Local Only — NOT in repo (~/Work/local/)

⚠️ These exist only on this machine. Lost on wipe. See proposals/repo-structure.md.

### Ollama (~/Work/local/ollama/)
```
scripts/
  status.sh          # Check Ollama status + loaded models
  pull-tier1.sh      # Pull all Tier 1 models at once
  switch.sh          # Swap loaded model
  test-api.sh        # Verify API responds
modelfiles/          # (empty — custom model configs go here)
```

### OpenBao (~/Work/local/openbao/)
```
docker-compose.yml         # OpenBao container (localhost:8200)
.env.example               # Token template
.gitignore                 # Ignores data/ and .env
scripts/
  init.sh                  # Initialize vault — plaintext key storage (Option C)
  init-keychain.sh         # Initialize vault — Keychain key storage (Option B) ← recommended
  unseal.sh                # Unseal after restart — reads from plaintext file
  unseal-keychain.sh       # Unseal after restart — reads from Keychain ← recommended
  status.sh                # Health check
  store-secret.sh          # Write a secret (path key value)
  get-secret.sh            # Read a secret (path key)
  setup-transit.sh         # Enable Transit engine + coach keys/policies
  setup-mailbox.sh         # Create coach workspace folder structure
  encrypt.sh               # Encrypt a file via Transit
  decrypt.sh               # Decrypt a file via Transit
data/                      # Vault storage (gitignored, persisted)
```

### Open WebUI (~/Work/local/open-webui/)
```
docker-compose.yml         # Chat UI on localhost:3000, connects to Ollama
```

### Tier 2 — Isolated Models (~/Work/local/tier2/)
```
docker-compose.yml         # Ollama in Docker, --network none
pull.sh                    # Pull a model into the isolated container
run.sh                     # Run a Tier 2 model interactively
```

### n8n — Workflow Automation (~/Work/local/n8n/)
```
docker-compose.yml         # n8n on localhost:5678 (Phase 4, not started yet)
```

---

## System Config (not in any repo)

| File | Purpose |
|------|---------|
| `~/.zshrc` | OLLAMA_HOST=127.0.0.1, Homebrew PATH, pipx PATH |
| `~/.zprofile` | Homebrew shellenv |
| `~/.ssh/config` | GitHub SSH key config |
| `~/.ssh/id_ed25519` | SSH key (MadMaxMini GitHub) |
| `~/.claude/settings.json` | Claude Code allowed tools |
| `~/.ollama/models/` | Model weights (not in git — too large) |

---

## Services & Ports

| Service | Port | Status |
|---------|------|--------|
| Ollama | 11434 | ✅ Running, localhost only |
| OpenBao | 8200 | ✅ Container up, not initialized |
| Open WebUI | 3000 | ⏳ Not started |
| Tier 2 Ollama | none | ⏳ Not started |
| n8n | 5678 | ⏳ Phase 4 |

---

## What's Missing / At Risk

| Item | Risk | Fix |
|------|------|-----|
| local/ scripts | Lost on wipe | Move into repo (proposal pending) |
| ~/.ssh/id_ed25519 | Lost on wipe | Back up private key securely |
| OpenBao data/ | Lost if Docker volume wiped | Backs up via OpenBao snapshot (future) |
| ~/.claude/settings.json | Lost on wipe | Add to repo or document |
