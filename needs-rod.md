# Needs Rod

Items blocked on Rod's input.

---

| Date | Item | Context |
|------|------|---------|
| 2026-04-19 | `bkUp.kdbx` + `bkup2bkup.kdbx` in bottleMsg (permanent location TBD) | Confirmed 2026-05-10: belong here, NOT ambiguous. But Rod's not actively using KeePass and wants to start. Decisions: (1) permanent home for the .kdbx files (e.g., `~/Library/CloudStorage/Dropbox/keepass/`), (2) which is canonical (`bkUp` vs `bkup2bkup`), (3) KeePass app installed on phone? Mad Max recommendation: keep KeePass for Rod's personal passwords (UI on phone/laptop only) — automation secrets stay in OpenBao. Programmatic KeePass access requires master pw on disk = defeats the point. |
| 2026-04-19 | Mem Palace — encryption angle | 3 options: (1) laptop FileVault check, (2) encrypt palace dir beyond FileVault if Dropbox sync is a concern, (3) platform/security.md to document all device posture. Which matters most? |
| 2026-05-08 | `403 HVAC PROPOSAL/` directory in bottleMsg root | What is it? Where does it route — digest, archive, or somewhere else? |
| 2026-05-08 | `Appliance issues/` directory in bottleMsg root | Same question — context + route? |
| 2026-05-08 | `Rubrik_Zero_Trust_Cloud_and_Rivals.m4a` in bottleMsg | Audio recording. Transcribe with Whisper → digest, or just archive raw? |
| 2026-05-08 | Admin account refresh — `roderick` profile logged in 2026-05-08 | Should I save this to memory with a "remind early June" trigger so the admin account stays fresh? |
| 2026-05-10 | GTD sweep reply mismatch | Sweep instructs reply with `go` / `hold 2` / `move 4 archive` / `skip` but dispatcher regex requires `gtd ` prefix → bare replies fall through to LLM, nothing executes. Two fix options: (A) update sweep message text to match dispatcher (1 min, ugly UX), (B) dispatcher accepts bare commands when active proposal exists (10 min, natural UX). Recommend B. Also: proposal expires at 23:59 same day — extend to 48hr or send noon-next-day reminder? |
