# madmax

Rod's v2 personal automation platform. Built on the Mac mini M4, dedicated Claude machine.

## What This Is

A privacy-first local AI + automation stack. Local models, encrypted secrets, agent coaches with isolated workspaces, file-based inter-agent messaging.

## Structure

```
.claude/skills/mad-max/     # Mad Max skill — platform builder persona
docs/                       # roadmaps, decisions, reference (coming)
proposals/                  # pre-decision docs, pending review
sessions/                   # full dated session archives
session-log.md              # rolling session summary
CLAUDE.md                   # Claude Code context + autonomy rules
```

## Local Stack (~/Work/local/)

| Service | Port | Purpose |
|---------|------|---------|
| Ollama | 11434 | Tier 1 local AI models (native Metal GPU) |
| OpenBao | 8200 | Secrets vault (open source Vault fork) |
| Open WebUI | 3000 | Browser chat UI for local models |
| Tier 2 (Docker) | none | Isolated Chinese/untrusted models |
| n8n | 5678 | Workflow automation (Phase 4) |

## Model Tiers

- **Tier 1** — Trusted (Meta, Mistral, Google, Alibaba): native Ollama, full Metal GPU
- **Tier 2** — Exploratory (DeepSeek, MiniMax): Docker, `--network none`, isolated

## Key Docs

- [local-ai.md](local-ai.md) — model roadmap and trust tiers
- [harden.md](harden.md) — system hardening log
- [session-log.md](session-log.md) — what's been done
- [proposals/](proposals/) — pending decisions

## Status

Phase 1 — Foundation (in progress). See [local-ai.md](local-ai.md) for checklist.
