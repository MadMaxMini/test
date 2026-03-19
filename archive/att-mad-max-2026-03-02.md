# ATT: Mad Max — Recruiting Coach Repo

**Date:** 2026-03-02

New repo is live on GitHub under the Roderick-Clemente account:

```
git@github.com:Roderick-Clemente/recruiting-coach.git
```

Clone it to the mini:
```bash
git clone git@github.com:Roderick-Clemente/recruiting-coach.git ~/Work/recruiting-coach
```

**Note:** This uses the Roderick-Clemente GitHub account, not MadMaxMini. You'll need an SSH key that has access to that account, OR Rod can add the MadMaxMini key as a deploy key on the repo. Check with Rod before trying to clone.

---

## What's in it

- `.claude/skills/recruiting-coach/SKILL.md` — full recruiting methodology (portable)
- `office/` — Harness-specific context: active pipeline, Rod's interview style (v1.0, 6 sessions), sell doc, templates
- `CLAUDE.md` — context file for Claude Code, autonomy rules, key file map
- `README.md` — repo overview + skill/office architecture explanation

## Architecture Note

Skill = general methodology (how to run SE recruiting for any company).
Office = Harness-specific data (live pipeline, Rod's actual style, comp context).

This is the pattern for future agent repos — portable skill, org-specific office.

---

## This Is the First Agent

This is the first standalone agent in the v2 system. Runs on Claude (cloud) now.
When local AI is ready, test against Llama 3.3 70B or Devstral 24B via Ollama.

---

*Sent from laptop (Rod/Claude) to mini (Mad Max)*
