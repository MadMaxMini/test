# Needs Rod

Items blocked on Rod's input.

---

| Date | Item | Context |
|------|------|---------|
| 2026-05-12 | **Coach roster triage decision** | Elite HH, Manager Coach, Health Coach, Faith, Recruiting — per coach decide: keep (with weekly output expectation), simplify (radically), or archive. Tied to 30-day pact success criterion #2. Suggested approach: one short session per coach where Rod names this week's expected output, or it goes. |
| 2026-05-12 | **OpenBao auto-unseal LaunchAgent — wire it up?** | No LaunchAgent for unseal-on-boot exists. Every Docker restart = vault sealed = every coach that needs a secret breaks silently. Symptom: 401 unauthorized on Telegram, DMG decrypt failures. Fix: ~5 min LaunchAgent that runs `unseal-keychain.sh` after Docker daemon starts. Pact-compatible (closing existing loop). |
| 2026-05-12 | **DNS poller bug — Elite HH + Health Coach Telegram inbound broken** | `[Errno 8] nodename nor servname provided` errors spinning constantly. Outbound nudges fire fine. Inbound chat dead since ~2026-05-08. Question for Rod: do you ever actually reply to those nudges via Telegram? If yes → real bug to fix. If no → cosmetic. Affects coach triage decision. |
| 2026-05-12 | OpenBao helper scripts broken | `store-secret.sh` and `get-secret.sh` look for token at `~/.openbao-init` plaintext file, not Keychain. Unusable from CLI until fixed (one-line edit: change source from file to `security find-generic-password -a "$USER" -s "openbao-root-token" -w`). Pact-compatible. |
| 2026-04-19 | `bkUp.kdbx` + `bkup2bkup.kdbx` in bottleMsg (permanent location TBD) | Confirmed 2026-05-10: belong here, NOT ambiguous. But Rod's not actively using KeePass and wants to start. Decisions: (1) permanent home for the .kdbx files (e.g., `~/Library/CloudStorage/Dropbox/keepass/`), (2) which is canonical (`bkUp` vs `bkup2bkup`), (3) KeePass app installed on phone? Mad Max recommendation: keep KeePass for Rod's personal passwords (UI on phone/laptop only) — automation secrets stay in OpenBao. Programmatic KeePass access requires master pw on disk = defeats the point. |
| 2026-04-19 | Mem Palace — encryption angle | 3 options: (1) laptop FileVault check, (2) encrypt palace dir beyond FileVault if Dropbox sync is a concern, (3) platform/security.md to document all device posture. Which matters most? |
| 2026-05-08 | `403 HVAC PROPOSAL/` directory in bottleMsg root | What is it? Where does it route — digest, archive, or somewhere else? |
| 2026-05-08 | `Appliance issues/` directory in bottleMsg root | Same question — context + route? |
| 2026-05-08 | `Rubrik_Zero_Trust_Cloud_and_Rivals.m4a` in bottleMsg | Audio recording. Transcribe with Whisper → digest, or just archive raw? |
| 2026-05-08 | Admin account refresh — `roderick` profile logged in 2026-05-08 | Should I save this to memory with a "remind early June" trigger so the admin account stays fresh? |
| 2026-05-10 | GTD sweep reply mismatch | Sweep instructs reply with `go` / `hold 2` / `move 4 archive` / `skip` but dispatcher regex requires `gtd ` prefix → bare replies fall through to LLM, nothing executes. Two fix options: (A) update sweep message text to match dispatcher (1 min, ugly UX), (B) dispatcher accepts bare commands when active proposal exists (10 min, natural UX). Recommend B. Also: proposal expires at 23:59 same day — extend to 48hr or send noon-next-day reminder? |
