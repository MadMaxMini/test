# CLAUDE.md — Project Context for Claude Code

This machine (Mac mini M4, 32GB) is dedicated to Claude.
User: Roderick (MadMaxMini on GitHub)

---

## Autonomy & Permissions

Claude is authorized to:
- Read, write, and edit any files in ~/Work/
- Run bash commands freely (git, brew, pip, pipx, ollama, docker, ssh, curl)
- Commit and push to git repos
- Install packages via brew, pip, pipx
- Create and manage Docker containers

Claude should ask before:
- Deleting files or directories
- Running sudo commands
- Pushing to branches other than main
- Anything with blast radius beyond this machine

---

## Memory Rules
- System-wide memory (`~/.claude/projects/.../memory/MEMORY.md`): update only on explicit user request
- Project memory files: live in the current project folder
- Session logs: single unified `session-log.md` in repo root (newest entries first)

---

## Project Structure
```
~/Work/
  test/              # main repo, docs, session logs (this file lives here)
  local/
    ollama/
      modelfiles/    # custom Modelfiles
      scripts/       # start/stop/switch scripts
    open-webui/      # web UI config
    openbao/         # secrets manager (Docker)
      docker-compose.yml
      data/          # gitignored, persisted vault storage
```

---

## Stack Decisions
| Component | Choice | Reason |
|-----------|--------|--------|
| Local AI runner | Ollama (native) | Apple Silicon Metal GPU, best perf |
| Secrets manager | OpenBao (Docker) | Open source Vault fork, MPL 2.0 |
| Tier 2 models | Docker (--network none) | Isolation for Chinese/untrusted models |
| Model source | HuggingFace primary | Checksums, model cards, community audit |
| Package manager | Homebrew + pipx | Homebrew for system, pipx for Python CLIs |
| Git auth | SSH (ed25519) | No HTTPS credential friction |

---

## Local AI Model Tiers
- **Tier 1** (native Ollama): Llama 3.3, Mistral/Devstral, Qwen2.5-Coder, Gemma
- **Tier 2** (Docker isolated): DeepSeek, MiniMax — Chinese models, run with --network none

---

## Services & Ports
| Service | Port | Binding |
|---------|------|---------|
| Ollama API | 11434 | 127.0.0.1 only |
| OpenBao | 8200 | 127.0.0.1 only |
| Open WebUI | 3000 | 127.0.0.1 only (when set up) |
| Telegram (Max bot) | — | Cloud (Telegram API) |

---

## Telegram Commands (Mad Max Bot)

**Stage B shipped (2026-05-19)** — Read-only inbox browsing via `@madmax_mini_bot` direct chat.

| Command | What |
|---------|------|
| `/sweep` | 📬 bottleMsg items + 📧 recent emails, emoji-coded, saves browse state |
| `/inbox` | Quick count (bottleMsg items + email entries) |
| `/email [N]` | Last N emails (default 10, max 50), with tier icons 🔴🟡🔵⚪ |
| `/email pending` | Debounce batch about to flush |
| `/read N` | Read bottleMsg item N from `/sweep`, supports md/txt/PDF |
| `/digest [N]` | Browse learning material in bottleMsg/digest/ |
| `/dig keyword` | Search digest + inbox by keyword |
| `/status` | Machine health (Ollama, Docker, Vault) |
| `/models` | List loaded Ollama models |

**See [CAPABILITIES.md](CAPABILITIES.md) for full documentation and testing instructions.**

---

## Key Files
- Roadmap: `~/Work/test/local-ai.md`
- Hardening log: `~/Work/test/harden.md`
- Permissions plan: `~/Work/test/claude-permissions.md`
- OpenBao compose: `~/Work/local/openbao/docker-compose.yml`
- Ollama scripts: `~/Work/local/ollama/scripts/`
- Session logs: `~/Work/test/session-YYYY-MM-DD.md`

---

## Current Status (as of 2026-05-19)

**Infrastructure:**
- Ollama ✅ (native, localhost:11434, models loaded)
- OpenBao ✅ (Docker, localhost:8200, running)
- Docker Desktop ✅ (initialized)
- HuggingFace CLI ✅ (installed, account: madmaxmini)
- System hardened ✅ (SIP, FileVault, Firewall, Stealth mode)
- SSH GitHub ✅ (ed25519 key, MadMaxMini account)

**Daemons (Live):**
- email-poller ✅ (Gmail IMAP, classification, debounce, Telegram notify)
- telegram-poller ✅ (@madmax_mini_bot, dispatcher, Stage B commands)
- GTD sweep (on-demand via `/gtd` command)
- Night planner ✅ (10pm task proposals via Telegram)
- Auto-agent ✅ (approvals via `/go` commands)

**Telegram (Stage B):**
- `/sweep`, `/inbox`, `/email`, `/read` commands live
- Browse state for `/read N` references
- PDF reading via pdfplumber venv
- All read-only (no file actions yet — Stage C deferred 1 week)

**One-Week Observation Period:**
- Monitoring email-inbox.md + email-batch.json for anomalies
- Watching telegram-poller.log for errors
- Testing commands from phone daily
- See [CAPABILITIES.md](CAPABILITIES.md) for test procedures
