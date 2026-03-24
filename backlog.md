# Mad Max — Backlog

Priority scale:
- **P0** — review/triage item, needs classification
- **P1** — broken, fragile, or blocks real work landing soon
- **P2** — meaningful improvement, do soon
- **P3** — good idea, back burner

Last reviewed: 2026-03-23

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
| Wire image to standup send | Round-robin bot/assets/ on group text |
| Dakota inbox/ → Dropbox symlink | Sharon's drops need to land in repo inbox/ — deprioritized, laptop handles for now |
| Google Sheets CSV export | Feed bot financial context via Apps Script |
| Email bot (DE@DakotaAndLLC.com) | Apps Script → markdown log → bot picks up |
| **Sharon terminal unblock** | **Status unknown — Devon screen share was 2026-03-22. Follow up.** |
| Team onboarding — VS Code + clone | Bot standups useless until team reads them |

---

## P1 — Do Soon

| Item | Notes |
|------|-------|
| **Dakota software repo structure redesign** | Inbox, contact tracking, property tracking all need rethinking. Rod to define vision, Mad Max builds. Early idea: inbox/ file drops trigger group texts. Flagged 2026-03-23. |
| **Standup redesign — two-part message** | iMessage (plain text): business top priority, each person's #1 task only, celebrations, blockers, + link to full standup in GitHub. Repo (markdown): top 3 per person, full detail, renders via GitHub app. Rod's design, waiting for group feedback before building. 2026-03-24. |
| **Sharon engagement** | She hasn't responded yet. Mission: get her plugged in and liking the system. Low spam. Warm messaging only at Rod's word. |
| **ba8715bc ghost group deletion** | Rod+Devon+Sharon+Doc duplicate, Sharon number without +. Rod deletes in Messages. |
| **iMessage group creation via AppleScript** | Currently blocked (-1700 error). Workaround: Rod creates group, I use the chat ID. Need a better path — investigate alternatives. |
| Outbound network monitoring | Jacob flagged — log/alert on unexpected outbound connections. macOS pf/lulu or lightweight script. |
| Per-agent OpenBao tokens | Narrow policies per agent — real secrets incoming, contains blast radius |
| Round 4 benchmark | 6 models — pending Gemma 3 27B + Mistral Small pulls |
| notify-group.sh live test | Updated session 9, needs Rod to confirm group actually receives |
| Add Rjclemente as collaborator to dakota-software | Still pending — needs gh token or browser |

---

## P2 — Do When Ready

| Item | Notes |
|------|-------|
| Bot pipeline architecture — per-person micro-bots + stitcher | Fix conflation failure mode. Each person bot gets tasks + role context, stitcher combines. Structural fix. |
| Open WebUI first real use | Live at localhost:3000 |
| n8n setup | Phase 4 — workflow automation, docker-compose ready |
| OpenBao store HF token properly | Path confirmed: tokens/huggingface |
| Agent encryption — office/ folders | Transit keys set up, not yet wired to any agent |
| Recruit-coach agent | Repo exists, skill/office pattern, not active |
| Mixtral:8x7b keep vs remove | Times out on all benchmark tasks (26GB). Remove if disk needed. |
| Repo rename test → madmax | Proposal written, pending Rod approval |
| AutoDakota_MultiTool shortcut | Weigh vs keeping dedicated Rod/Group shortcuts |
| 6am standup review gate | Review before group send — flagged S17 |

---

## P3 — Back Burner

| Item | Notes |
|------|-------|
| Pi 5 auto-unseal node | Valuable once OpenBao has real dependents |
| Plaid integration (Devon) | Financial data into repo |
| Tax package automation | Phase 2/3, needs Plaid first |
| Lease expiration alerts | Bot reads properties/ for dates |
| Tier 2 model evaluation | DeepSeek/MiniMax Docker isolated |
| Anthropic API (Bedrock or direct) | Claude CLI free and working, revisit later |
| Session timeout — skip blocked prompts | If Claude Code prompt gets no answer, move on. UX improvement. |

---

## Done (recent, for reference)

- ✅ iMessage gateway LIVE — C binary, FDA granted, polling every 30s (2026-03-23 S17)
- ✅ attributed_body decode fix in msggateway.py — typedstream regex fallback (2026-03-23 S18)
- ✅ Wins bot, send_msg.py rate limiter (2026-03-23 S17)
- ✅ Team directory created — dakota-software/team/directory.md (S17)
- ✅ Rod+Sharon iMessage group created by Rod (f0641ba091334238a03126835280dc23) (S18)
- ✅ Devon content strategy notes recovered — people/devon/notes.md (S18)
- ✅ iMessage gateway permission model — Option C (Rod admin), monitor tier built (S12)
- ✅ Doc GitHub = Rjclemente confirmed (S17)
- ✅ Devon GitHub = devonclemente confirmed (S12)
- ✅ Standup dedup guard — standup-state.log, FORCE_NOTIFY=1 override (2026-03-21)
- ✅ notify.sh → AutoDakota_Notify_Rod shortcut (2026-03-21)
- ✅ notify-group.sh → AutoDakota_Notify_Group shortcut (2026-03-21)
- ✅ Standup pipeline live — 7pm draft, 7am group send, weekdays only
- ✅ Faith pipeline live — Friday 3pm + Wednesday 7am Lenten nudge
- ✅ Open WebUI live at localhost:3000
- ✅ Devstral 24B pulled (S7)
