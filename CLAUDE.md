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
- Session logs: `session-YYYY-MM-DD.md` in `~/Work/test/`

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

---

## Key Files
- Roadmap: `~/Work/test/local-ai.md`
- Hardening log: `~/Work/test/harden.md`
- Permissions plan: `~/Work/test/claude-permissions.md`
- OpenBao compose: `~/Work/local/openbao/docker-compose.yml`
- Ollama scripts: `~/Work/local/ollama/scripts/`
- Session logs: `~/Work/test/session-YYYY-MM-DD.md`

---

## Current Status (as of 2026-03-01)
- Ollama installed, localhost-only, no models pulled yet
- Docker Desktop installed, needs to be launched once to initialize
- OpenBao compose file ready, waiting for Docker to be up
- HuggingFace CLI installed (`hf`), account not created yet
- System hardened: SIP ✅ FileVault ✅ Firewall ✅ Stealth mode ✅
- SSH configured for GitHub ✅

## Next Session Checklist
1. Open Docker.app (initialize engine)
2. `cd ~/Work/local/openbao && docker compose up -d`
3. Initialize and unseal OpenBao (scripts ready in `openbao/scripts/`)
4. Create HuggingFace account → generate token → store in OpenBao
5. Pull first Tier 1 model via Ollama
6. Test API end to end
