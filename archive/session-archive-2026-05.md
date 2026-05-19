# Session Archive — 2026-05

## 2026-05-12 (distilled)
- Shipped Phase 1 with formula guard + scope-down (commits f020bd1, 37d6027, 2af58c0)
- Patched sheets_bridge.py: MORTGAGE_FIELD_SPECS 4→1, added formula-as-payment guard to skip alerts on formulaic payments
- Reviewed all 6 May 12 statements (401K, 403K, Grand Pines, Piney, La Estancia, Via Verona); 1 dedup'd as real duplicate
- Identified + fixed Piney Point formula trap (C20 =C19+C4 causing false alerts)
- Decision: Bridge scope = C21 (Balance) + D21 (date) only; reads C20 for change-detect, never writes
- Decision: Sheets API re-wire deferred to Phase 2
- Phase 1 untested live—awaiting June statements for first real validation early June
- Open: Sharon pending with real May Via Verona; June statements to validate new code behavior

## 2026-05-12 (distilled)
- Added temporary TTL mode (1-2h expiration) to dispatcher with three priority levels: one-off > TTL > persistent > default
- Flipped defaults: `/model X` now temporary 2h with auto-revert, `/model X perm` for persistent
- Updated `/model?` query to show TTL remaining
- Rewrote `/help` documentation
- Made commits 8be6d52, ac76a1f, 8517c5c
- Decision: 2h temporary default correct—most switches are temporary, permanent is exception

## 2026-05-12 (distilled)
- Full start sweep completed, FDA fix + Piney Point dedup verified working
- OpenBao unsealed via unseal-keychain.sh, R/W test passed
- 30-day no-build pact written and saved to memory (active through 2026-06-10, requires explicit override clause)
- Dakota mortgage pipeline classified as franchise; coaches overhead
- Coaches not dead but inbound Telegram pollers broken with DNS errors since 2026-05-08
- OpenBao token handling broken (scripts hunt ~/.openbao-init plaintext instead of Keychain, unusable from CLI)
- No auto-unseal LaunchAgent — Docker restart silently breaks coaches with secrets
- Watcher dedup leaves dupes in inbox instead of moving to processed/
- Next priorities (pact-aware): auto-unseal LaunchAgent, coach roster triage, DNS poller fix, Phase 2 Dakota

## 2026-05-10 (distilled)
- Integrated @madmax_mini_bot into Dakota Automation Team Telegram group (previously unmonitored)
- Added group commands: `/ping`, `/status`, `/models`, `/tasks [name]`, `/standup`, `@madmax_mini_bot [question]`
- Upgraded tg_send with explicit chat_id parameter; added tg_send_chunked for message chunking (3 msgs × 4000 chars per para boundary)
- Fixed `/tasks` command to read from canonical tasks/views/{p}.md path (was reading legacy people/{p}/tasks.md)
- Enabled group session history via sessions_mod.Session(GROUP_CHAT_ID)
- Decided: Max Bot owns group interactions; AutoDakota owns 1-on-1 interactions

## 2026-05-08 (distilled)
- Identified good vs stale Via Verona sheets via Playwright; configured label_column per sheet (Via Verona=G, Kickapoo=J)
- Discovered and fixed escrow mismatch: account balance was writing to monthly-payment row instead of separate account
- Added new "Escrow Balance" row 24 and wired config to route escrow data correctly
- Integrated Via Verona into property_map.json and SHEET_MAP
- Executed live run: 6 cells written successfully (balance, escrow, dates)
- All 6 properties now online
- Decision: Escrow balance is a separate row from monthly payment row

## 2026-05-06 (distilled)
- Completed full HuggingFace/Ollama audit: 6 models, 74GB total, reviewed March benchmarks
- Created ~/Work/local/scripts/reference-models.md with speed charts, scorecards, failure modes, verdicts
- Wired `models` + `models detail` commands into dispatcher for on-demand pulls
- Bumped Telegram bot depth from 10 to 20
- Bumped Ollama output cap from 200 to 500 tokens
- Decided: Mixtral = dead weight (26GB, timeouts) — candidate for removal
- Decided: Mistral Small as dispatcher default

## 2026-05-13 (distilled)
- Phase 3 Chase→Cash Tracking bridge shipped to PROD: March 2026 reconciled $14,629.85 exact, 3 rows landed (r15-17), idempotent verified (commit 048417f on phase-3-chase-cash-tracking)
- Phase 2 scope corrected from alerting/long-polling to asset inventory + flowchart + refactoring audit; roadmap.md rewritten (L28-72)
- Phase 3 authorized under no-build pact as core Dakota automation; Phase 4 will bundle PM statements + alerting hardening
- Bridge design locked: balance-only, dedup by (year-month, amount, prefix), drift thresholds $500/$2000/$200 (mortgage/dist/CC)
- Phase 2 to use fresh agent for clean design context; prompts drafted
- Blocker: Sharon waiting on Via Verona May statement from ServiceMac (P0)
- Open v1.6 checklist: CSV dedup test, folder rename, auto-watcher integration, partial-mortgage completion, drift refinement, 7 Sharon questions
- Uncommitted in dakota-software: roadmap.md, phase-2-inventory.md (887L), alert-system-design.md (324L) — Rod owns commit
- Next: Rod spins fresh agent for Phase 2 inventory; monitor June statements for Phase 1 validation

## 2026-05-15 (distilled)
- Audited email system end-to-end; confirmed pdftotext + pdfplumber already available, no new Phase 2 deps needed
- Filed Phase 2 walkthrough (Stages A/B/C) to dakota-software/docs/2026-05-15-email-system-status-phase-2.md (c5b5e5a, pushed); copied to bottleMsg; summary sent via AutoDakota_Notify_Group
- Shipped Stage A: extended `_get_system_prompt` to route context="group" → SOUL-telegram.md; added Dakota team awareness section; restarted telegram-poller; verified 3 contexts route correctly
- Decided: skip poppler install, shell-out to existing pdfplumber venv; build order Stage A → B → observe → C only if B used; group context shares SOUL-telegram.md with direct telegram
- Open: 4 Phase 2 decisions pending Rod (Stage B approval, confirmation flow, pdfplumber approach, nudge cadence)
- Open: morning brief 14 days stale (since 2026-05-01) — nightly triage may be broken
- Open: EliteHH coach STALE 119h, ManagerCoach STALE 132h; 19 bottleMsg items pending GTD sweep
- Note: `~/Work/test/local/scripts/` is out-of-sync mirror of `~/Work/local/scripts/`
- Next: observe group chat behavior; await Rod's call on Stage B
