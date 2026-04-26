# Inventory

Current state of the mini platform — what's running, installed, and configured.

## Files

- **status.md** — Quick snapshot (models pulled, services running, agent repos cloned)
- **models.md** — Tier 1 + Tier 2 models, versions, checksums, memory footprint
- **services.md** — Ollama, OpenBao, Docker, ports, health status
- **agent-repos.md** — recruiting-coach, health-coach, etc., clone paths, last updated

## Update Schedule

- Before session start (manual check)
- After installing/updating models or services (immediate)
- After cloning or updating agent repos (immediate)

## Example (status.md)

```markdown
# Inventory Status — 2026-04-25

## Models (Ollama)

| Model | Status | Size | Last Pulled |
|-------|--------|------|-------------|
| Mistral 7B | ✓ running | 4.1 GB | 2026-04-20 |
| Gemma 27B | ✓ running | 17 GB | 2026-04-15 |
| Llama 3.1 | ✓ pulled | 4.9 GB | 2026-04-10 |
| DeepSeek | ✗ not pulled | 7.3 GB | — |

## Services

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| Ollama API | 11434 | ✓ running | localhost only |
| OpenBao | 8200 | ✓ unsealed | Docker running |
| Docker | — | ✓ running | Desktop app |

## Agent Repos

| Repo | Path | Status | Last Sync |
|------|------|--------|-----------|
| recruiting-coach | ~/Work/coaches/recruiting-coach | ✓ cloned | 2026-04-23 |
| health-coach | ~/Work/coaches/health-coach | ✓ cloned | 2026-04-22 |
```

See `models.md`, `services.md`, `agent-repos.md` for detailed tracking.
