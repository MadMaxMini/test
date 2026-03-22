# Mad Max — Backlog

Priority scale:
- **P0** — review/triage item, needs classification
- **P1** — broken, fragile, or blocks real work landing soon
- **P2** — meaningful improvement, do soon
- **P3** — good idea, back burner

Last reviewed: 2026-03-22

---

## P0 — Needs Classification / Review

| Item | Notes |
|------|-------|
| Review all open proposals in `proposals/` | 9 files, some stale, some blocking |
| Pi 5 setup plan | Auto-unseal, watchdog, lightweight cron offload |
| Tier 2 model pulls (DeepSeek, MiniMax) | Docker-isolated, not started |
| Llama 3.3 70B pull | Large model, not pulled yet |
| Llama 3.1 8B pull | Was pulled, now missing from `ollama list` |
| Faith benchmark rerun | Add Devstral, professionalize format to match Dakota |
| **iMessage gateway — activate** | **P0/P1 — FDA grant → load plist → add Rod to msggateway-admin Keychain → smoke test ping. Script ready at `~/Work/local/scripts/msggateway.sh`.** |
| **iMessage permission model — decide** | **P1 — Option C (Rod admin only) active now. Monitor mode built: team texts logged to msggateway-inbox.md, surfaced at session start. Upgrade path to Option A (queue+approve) when team is stable.** |
| Wire image to standup send | Round-robin bot/assets/ on group text |
| Dakota inbox/ → Dropbox symlink | Sharon's drops need to land in repo inbox/ |
| Google Sheets CSV export | Feed bot financial context via Apps Script |
| Email bot (DE@DakotaAndLLC.com) | Apps Script → markdown log → bot picks up |
| **Sharon terminal unblock** | **P0 — Devon screen share, one-time setup. Nothing moves until team is in the repo.** |
| **GitHub invites** | **P0 — Sharon + Doc + Devon usernames needed. Blocks repo access for everyone.** |
| Team onboarding — VS Code + clone | P0 — bot standups are useless until they're reading them. This is the unlock. |

---

## P1 — Do Soon

| Item | Notes |
|------|-------|
| Per-agent OpenBao tokens | Narrow policies per agent — real secrets incoming, contains blast radius |
| AutoDakota_MultiTool shortcut | Weigh vs keeping dedicated Rod/Group shortcuts |
| Round 4 benchmark | 6 models — pending Gemma 3 27B + Mistral Small pulls |
| notify-group.sh wired to AutoDakota_Notify_Group | Updated in session 9, needs live test (Rod to confirm) |

---

## P2 — Do When Ready

| Item | Notes |
|------|-------|
| Bot pipeline architecture — per-person micro-bots + stitcher | Fix conflation failure mode. Each person bot gets tasks + role context, stitcher combines. Not a model capability issue — structural fix. See benchmark-2026-03-21.md. |
| Open WebUI first real use | Live at localhost:3000 |
| n8n setup | Phase 4 — workflow automation, docker-compose ready |
| OpenBao store HF token properly | Path confirmed: tokens/huggingface |
| Agent encryption — office/ folders | Transit keys set up, not yet wired to any agent |
| Recruit-coach agent | Repo exists, skill/office pattern, not active |
| Mixtral:8x7b keep vs remove | Useful for chat, times out on all benchmark tasks (26GB). Consider removing if disk needed. |
| Repo rename test → madmax | Proposal written, pending approval |
| Move local/ scripts into madmax repo | Already done 2026-03-02 per session log |

---

## P3 — Back Burner

| Item | Notes |
|------|-------|
| Pi 5 auto-unseal node | Valuable once OpenBao has real dependents |
| Plaid integration (Devon) | Financial data into repo |
| Tax package automation | Phase 2/3, needs Plaid first |
| Lease expiration alerts | Bot reads properties/ for dates |
| Tier 2 model evaluation | DeepSeek/MiniMax Docker isolated |
| Anthropic API (Bedrock or direct) | Claude CLI is free and working, revisit later |
| iMessage receive (Phase 3.5) | Promoted to P0 — see P0 section |

---

## Done (recent, for reference)

- ✅ Standup dedup guard — `standup-state.log`, FORCE_NOTIFY=1 override (2026-03-21)
- ✅ prep-standup text includes digest + top 3 inline, not just filename (2026-03-21)
- ✅ notify.sh → AutoDakota_Notify_Rod shortcut (2026-03-21)
- ✅ notify-group.sh → AutoDakota_Notify_Group shortcut (2026-03-21)
- ✅ AutoDakota_Notify_Rod + AutoDakota_Notify_Group shortcuts live (Rod)
- ✅ Standup pipeline live — 7pm draft, 7am group send, weekdays only
- ✅ Faith pipeline live — Friday 3pm + Wednesday 7am Lenten nudge
- ✅ Devstral 24B pulled (session 7)
- ✅ Open WebUI live at localhost:3000
- ✅ TEST_MODE flag for standup (Rod-only routing)
- ✅ scan.py honest logging (notify checks return code)
