# Reset Note — 2026-03-17

Fresh eyes after ski week. Here's what's actually true.

---

## What Went Wrong

We built 6 sessions of infrastructure before getting a single model running.
The mini is a sophisticated empty box. That's the trap.

Specific mistake: session 6 added remote access (Tailscale + CRD + Chrome)
to solve a problem that didn't exist yet, and degraded security doing it.

---

## Immediate Cleanup

**Remote access — tear it all down:**
- [ ] `brew uninstall --cask tailscale-app google-chrome`
- [ ] Run `/Applications/Chrome Remote Desktop Host Uninstaller.app`
- [ ] Remove Google Keystone daemons (sudo required — Rod runs these)
- [ ] Revert power settings (sudo): `sudo pmset -a sleep 30 autorestart 0`
- [ ] Archive/delete `enable-ssh.txt` from bottleMsg (never ran it — good)
- [ ] Update MEMORY.md: remove remote access plan entry

---

## Priority Reset

The only thing that matters right now: **get a model running and talk to it.**

1. Start Docker → spin up OpenBao → unseal
2. Pull one Tier 1 model (Qwen2.5-Coder or Llama 3.3)
3. Hit the API, get a response
4. Done. Everything else is deferred until that works.

Deferred until after local AI is actually running:
- Mailbox architecture
- Coach path reorg
- n8n
- HuggingFace account
- Repo rename

---

## Skill Needs Fixing

See discussion — Mad Max skill needs a principle it was missing:
**working software before infrastructure.**

The skill says "bias toward doing" but didn't specify doing the *right* thing first.
Needs a current-phase anchor so it doesn't get ahead of itself.
