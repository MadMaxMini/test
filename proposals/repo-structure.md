# Proposal: Repo & Folder Structure

## Problem
- Current repo named `test` — meaningless, inconsistent with skill expectations
- Skill file already references `~/Work/madmax/` — local path is `~/Work/test/`
- `local/` tooling is untracked, sits outside the repo
- No clear separation between docs, logs, and scripts at repo root

---

## Proposed Structure

### GitHub
- Rename `MadMaxMini/test` → `MadMaxMini/madmax`
- Git handles remote URL redirect automatically

### Local
```
~/Work/
  madmax/                        # main repo (was: test)
    .claude/
      skills/
        mad-max/                 # Mad Max skill (canonical)
        recruiting/              # next migration
        [future coaches]
    docs/                        # all roadmaps, decisions, reference
      local-ai.md
      harden.md
      claude-permissions.md
    proposals/                   # pre-decision docs (this folder)
    sessions/                    # full dated session archives
      2026-03-01.md
      2026-03-02.md
    session-log.md               # rolling summary, last ~10 sessions
    CLAUDE.md
    README.md

  local/                         # included in madmax repo
    ollama/
      modelfiles/
      scripts/
    openbao/
      docker-compose.yml
      scripts/
      data/                      # gitignored — vault storage
    open-webui/
    [future: n8n/, tier2/]
```

### Why include `local/` in the repo
- Scripts are code — they belong in version control
- Easy to restore after a wipe or migration to Pi
- `.gitignore` handles data/, .env, secrets

---

## Migration Steps
1. Rename repo on GitHub: Settings → Rename → `madmax`
2. Update local remote: `git remote set-url origin git@github.com:MadMaxMini/madmax.git`
3. Move local folder: `mv ~/Work/test ~/Work/madmax`
4. Move `~/Work/local/` contents into `~/Work/madmax/local/`
5. Update all path references in CLAUDE.md, skill file, docs
6. Update laptop symlink: claude-life `.claude/skills/mad-max/` → new path

---

## Decision
- [ ] Approved
- [ ] Changes requested
