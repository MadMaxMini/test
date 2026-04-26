# Claude Code Permissions & System Hardening

---

## Open Questions

1. Are you primarily running Claude via VS Code extension, CLI, or both?
2. Which prompts are most annoying — bash commands, file edits, web fetches, all of it?
3. Do you want sudo-level access (installs, system config) or just normal user-space freedom?
4. How locked down is the system currently — any existing sudoers rules, SIP status, etc.?
5. Hardening scope — just this machine, or part of a broader network/infra?

---

## Action Plan

### 1. Claude Code Permissions (reduce prompts)
- [ ] Audit current `~/.claude/settings.json` — see what's already allowed
- [ ] Configure `allowedTools` to whitelist bash, file edits, web search without prompting
- [ ] Write a project-level `CLAUDE.md` with explicit autonomy instructions per project
- [ ] Decide: scoped permissions per project vs global permissive mode
- [ ] Evaluate `--dangerously-skip-permissions` flag — nuclear option, discuss tradeoffs

### 2. System-Level Elevated Access
- [ ] Clarify what actions need elevation (installs, network config, cron, etc.)
- [ ] Configure sudoers for specific commands without password prompt (targeted, not blanket)
- [ ] Decide if Claude gets a dedicated user/group with specific privileges

### 3. System Hardening
- [ ] Check SIP (System Integrity Protection) status
- [ ] Review open ports and running services
- [ ] Set up firewall rules (Little Snitch or macOS built-in pf)
- [ ] SSH hardening if remote access is planned
- [ ] Audit installed software and startup items
- [ ] Consider disk encryption status (FileVault)

### 4. Local AI Privacy Layer
- [ ] Confirm no telemetry leaking from Ollama or Open WebUI
- [ ] Network-isolate local AI services where possible
- [ ] Document what does/doesn't phone home

---

## Reference

### Key Files & Paths
- Global Claude settings: `~/.claude/settings.json`
- Global Claude memory: `~/.claude/projects/-Users-macBot-Work-test/memory/MEMORY.md`
- Project instructions: `~/Work/<project>/CLAUDE.md`
- Ollama default model storage: `~/.ollama/models/`
- Local AI workspace: `~/Work/local/`

### Claude Code Permission Modes
- **Default**: prompts for unapproved tools
- **`allowedTools`** in settings.json: whitelist specific tools/commands permanently
- **`--dangerously-skip-permissions`**: CLI flag, skips all prompts (use with care)
- **CLAUDE.md**: project-scoped behavioral instructions, can grant broad autonomy per project

### Relevant Docs
- Claude Code settings: https://docs.anthropic.com/claude-code/settings
- CLAUDE.md reference: https://docs.anthropic.com/claude-code/claude-md
- macOS sudoers: `man sudoers`
- macOS pf firewall: `man pf`
