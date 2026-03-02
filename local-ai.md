# Local AI Roadmap

## Goals
- Full privacy-first local AI stack on M4 Mac mini (32GB)
- Ability to bounce context between local models and Claude
- Explore both US/EU and Chinese models safely
- Zero cloud dependency for sensitive work

---

## Security Model: Trust Tiers

### Why tiers matter
Model weights are not "neutral math" — training data, RLHF, and alignment processes
can embed behaviors you can't easily inspect. A model can't exfiltrate data on its own,
but it can steer outputs, respond to hidden triggers (sleeper agents), or behave
differently in agentic contexts than in chat. Trust level should reflect training
transparency, not just country of origin.

### Tier 1 — Trusted (Native Ollama)
Open training pipelines, reproducible, widely independently audited.
Run natively for full Apple Silicon / Metal GPU performance.

| Model | Source | Best For |
|-------|--------|----------|
| Llama 3.3 70B | Meta / HuggingFace | General, large context |
| Mistral / Devstral 24B | Mistral AI / HuggingFace | Coding, agents |
| Gemma 3 | Google / HuggingFace | Lightweight, fast |
| Qwen2.5-Coder 14B | Alibaba / HuggingFace | Code (widely audited) |

### Tier 2 — Exploratory (Docker-gated)
Less transparent training, geopolitical considerations, or limited independent audits.
Worth exploring for capability comparison — run isolated in Docker with no network access.

| Model | Source | Notes |
|-------|--------|-------|
| DeepSeek R1 / R2 | DeepSeek / HuggingFace | Strong reasoning, jailbreak-prone |
| MiniMax M2.x | MiniMax AI / HuggingFace | Strong coding + agentic, newer |

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │        Your Machine          │
                    │                              │
  Tier 1            │   Ollama (localhost:11434)   │
  Trusted ─────────►│   Native Metal GPU           │
  Models            │   No external network        │
                    │                              │
  Tier 2            │   Docker (no-network)        │
  Exploratory ─────►│   Ollama in container        │
  Models            │   Process-isolated           │
                    │                              │
                    │   Open WebUI (localhost)     │
                    │   Chat UI for both           │
                    └─────────────────────────────┘
```

### Why not Docker everything?
On Apple Silicon, Docker doesn't have direct Metal GPU access. Native Ollama runs
Tier 1 models significantly faster (10-15 tok/s vs much slower in Docker).
The tradeoff is worth it for Tier 2 where we're accepting slower speed for isolation.

### Source: HuggingFace First
- Download weights from HuggingFace where possible — model cards, changelogs, and
  community scrutiny provide more signal than pulling blindly from Ollama registry
- Verify SHA checksums when published by model authors
- Ollama registry is fine for Tier 1 convenience pulls

---

## Phases

### Phase 1 — Foundation (now)
- [x] Install Ollama (native, macOS)
- [x] Lock Ollama to localhost:11434
- [x] Create folder structure ~/Work/local/
- [ ] Harden system firewall (pf / Little Snitch)
- [ ] Configure Claude Code permissions (reduce prompts)
- [ ] Pull first Tier 1 model and test API

### Phase 2 — Tier 1 Models
- [ ] Pull Llama 3.3 70B (Q4) — general purpose
- [ ] Pull Devstral 24B — coding + agentic
- [ ] Pull Qwen2.5-Coder 14B — fast coding
- [ ] Set up Open WebUI on localhost
- [ ] Test bouncing context between local models and Claude

### Phase 3 — Docker + Tier 2
- [ ] Set up Docker with no-network Ollama container
- [ ] Pull DeepSeek R1 into Docker environment
- [ ] Pull MiniMax M2.x into Docker environment
- [ ] Benchmark Tier 2 vs Tier 1 on same prompts
- [ ] Document behavioral differences and red flags found

### Phase 4 — Workflow Integration
- [ ] Build scripts in ~/Work/local/ollama/scripts/ for model switching
- [ ] Create custom Modelfiles for specialized personas/configs
- [ ] Set up Claude ↔ local model handoff workflow
- [ ] Explore MCP server or API bridge between local models and Claude

---

## Hardening Checklist
- [ ] Ollama bound to 127.0.0.1 (done — verified)
- [ ] macOS firewall enabled
- [ ] Port 11434 blocked externally (pf rules)
- [ ] Open WebUI auth enabled if exposed beyond localhost
- [ ] Docker network isolation for Tier 2 (--network none)
- [ ] FileVault disk encryption verified
- [ ] SIP status checked
- [ ] Ollama telemetry audited (OLLAMA_NOPRUNE, network monitor)
- [ ] No model output piped directly to shell without review

---

## Key Paths
- Ollama models: `~/.ollama/models/`
- Scripts & Modelfiles: `~/Work/local/ollama/`
- Open WebUI config: `~/Work/local/open-webui/`
- This roadmap: `~/Work/test/local-ai.md`
- Permissions & hardening plan: `~/Work/test/claude-permissions.md`
