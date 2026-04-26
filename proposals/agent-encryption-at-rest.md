# Proposal: Agent Repo Encryption at Rest

**Status:** P0 — Approved concept, awaiting Rod's go-ahead to build
**Date:** 2026-04-24
**Author:** Mad Max
**First target:** elite-hh-bot (resumes, pipeline, interview prep, company intel)

---

## Problem

Agent repos sit in plaintext on Rod's work machine. Anyone with filesystem access
(IT, shoulder surfer, unlocked screen) can browse resumes, job pipeline, interview
prep, and company-specific intel. Elite HH is the most sensitive — active job search
data on a corporate machine.

## Solution: Encrypted APFS Disk Image (DMG)

macOS-native encrypted container. The repo lives inside the DMG. When mounted,
everything works normally. When unmounted, it's an opaque blob.

### Why DMG over alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **Encrypted DMG** | macOS native, no tools, AES-256, scriptable mount/unmount | Must mount before use |
| git-crypt | Transparent in git | Working tree is still plaintext — doesn't solve the problem |
| age/sops | File-level encryption | Must decrypt/re-encrypt manually, breaks git diff |
| Encrypted APFS volume | Fast, native | Heavier — requires dedicated partition or volume |
| VeraCrypt | Cross-platform | Extra install, not macOS-native |

**DMG wins** — simplest, native, no dependencies, solves the problem.

---

## Architecture

```
Before:
~/Work/coaches/elite-hh-bot/         ← plaintext directory

After:
~/Work/coaches/elite-hh-bot.dmg      ← AES-256 encrypted sparse image (~500MB capacity)
~/Work/coaches/elite-hh-bot/          ← symlink to /Volumes/elite-hh-bot/ (only when mounted)
```

### Key storage

- DMG password generated (32-char random) and stored in macOS Keychain
- Keychain entry: service `elite-hh-dmg`, account `macBot`
- Keychain is unlocked by macOS login — same security boundary as SSH keys

### Mount/unmount commands

```bash
# Mount (pulls password from Keychain)
security find-generic-password -s "elite-hh-dmg" -w \
  | hdiutil attach ~/Work/coaches/elite-hh-bot.dmg -stdinpass

# Unmount
hdiutil detach /Volumes/elite-hh-bot
```

---

## Implementation Plan

### Phase 1: Build it (this session or next)

**Step 1 — Backup**
- Confirm elite-hh-bot is clean and pushed to remote
- Create branch `pre-encryption-backup` on remote as a safety net
- Verify: `git -C ~/Work/coaches/elite-hh-bot status && git -C ~/Work/coaches/elite-hh-bot push`

**Step 2 — Create encrypted DMG**
```bash
# Generate password, store in Keychain
PW=$(openssl rand -base64 32)
security add-generic-password -a macBot -s "elite-hh-dmg" -w "$PW"

# Create sparse image (500MB capacity, only uses actual space ~4MB)
hdiutil create -size 500m -type SPARSE -fs APFS \
  -encryption AES-256 -stdinpass \
  -volname "elite-hh-bot" \
  ~/Work/coaches/elite-hh-bot.sparseimage <<< "$PW"
```

**Step 3 — Move repo into DMG**
```bash
# Mount the empty DMG
security find-generic-password -s "elite-hh-dmg" -w \
  | hdiutil attach ~/Work/coaches/elite-hh-bot.sparseimage -stdinpass

# Move repo contents into mounted volume
mv ~/Work/coaches/elite-hh-bot ~/Work/coaches/elite-hh-bot-original
cp -a ~/Work/coaches/elite-hh-bot-original/ /Volumes/elite-hh-bot/

# Create symlink so paths don't break
ln -s /Volumes/elite-hh-bot ~/Work/coaches/elite-hh-bot

# Verify everything works
git -C ~/Work/coaches/elite-hh-bot status
ls ~/Work/coaches/elite-hh-bot/office/pipeline.md
```

**Step 4 — Test**
- Git operations (status, log, commit, push) through the symlink
- Telegram poller cron — does it still work?
- Claude agent invocation — can the skill read the repo?
- Unmount → verify directory is inaccessible
- Remount → verify everything comes back

**Step 5 — Clean up**
- Once verified, delete `elite-hh-bot-original/` (ask Rod first)
- Update cron jobs to mount before / unmount after poller runs
- Document in inventory.md

### Phase 2: Cron integration

Update the elite-hh-bot Telegram poller cron to:
1. Mount DMG (Keychain password)
2. Run poller
3. Unmount DMG

This way the repo is only decrypted while the bot is actively running.

### Phase 3: OpenBao on Pi (future)

Move the DMG password from Keychain to OpenBao running on a Raspberry Pi at Rod's house.
- Even with macOS login, the key isn't on the machine
- Rod can revoke access remotely
- Requires network path to Pi (Tailscale or home VPN)
- **Not needed for Phase 1** — Keychain is sufficient for "not easily visible"

---

## Rollback

If this doesn't work out:
1. Mount the DMG
2. Copy contents back to `~/Work/coaches/elite-hh-bot/`
3. Remove the symlink
4. Delete the DMG
5. Remote branch `pre-encryption-backup` still has the original state

Git history is preserved inside the DMG — nothing is lost.

---

## Rollout order (after elite-hh-bot proves the pattern)

1. **elite-hh-bot** ← this proposal (most sensitive — job search on work machine)
2. **health-coach** — personal health data
3. **manager-coach** — work relationship coaching
4. Others as needed

---

## Open questions for Rod

- [ ] Mount strategy: manual mount per session, or auto-mount at login + unmount at midnight?
- [ ] Should the `.dmg` file itself be gitignored or kept outside `~/Work/coaches/` entirely?
- [ ] Phase 3 timeline — is the Pi worth setting up now or is Keychain enough for months?

---

## Risks

| Risk | Mitigation |
|------|------------|
| Forget to mount before using agent | Script it / add to session startup |
| DMG corruption | Git remote has full history; `pre-encryption-backup` branch exists |
| Keychain compromised | Phase 3 moves key to OpenBao on Pi |
| Performance overhead | Negligible — APFS encryption is hardware-accelerated on Apple Silicon |
| Cron fails because DMG not mounted | Poller script checks mount status first, skips gracefully |

---

## Enhancements (after Phase 1 proves out)

- **Auto-mount on login, auto-unmount on idle** — LaunchAgent that mounts at login, a cron that unmounts after X minutes of no access. Rod never thinks about it.
- **Mount status in session startup** — Mad Max checks which DMGs are mounted at session start, reports status, mounts any that are needed for the session's work.
- **Encrypted backup to Dropbox** — the `.sparseimage` file itself could sync via Dropbox as an encrypted offsite backup. Nobody can open it without the Keychain/OpenBao key.
- **Per-agent mount scripts** — `~/Work/local/scripts/vault-mount.sh elite-hh` / `vault-unmount.sh elite-hh` so it's one command.
- **Health check cron** — nightly job that verifies all encrypted repos can mount/unmount cleanly, alerts Rod via Telegram if anything fails.
- **Multi-repo single DMG** — if we encrypt 3+ repos, consider one larger DMG for all sensitive coaches vs. one DMG per repo. Trade-off: all-or-nothing mount vs. granular access.

---

## Roadmap

| Phase | What | When | Depends on |
|-------|------|------|------------|
| **1** | Encrypted DMG for elite-hh-bot | Next session (Rod's go) | Nothing |
| **1b** | Mount/unmount helper scripts | Same session | Phase 1 |
| **1c** | Cron poller updated to auto-mount | Same session | Phase 1 |
| **2** | Roll out to health-coach | After 1 week of Phase 1 stability | Phase 1 proven |
| **2b** | Roll out to manager-coach | After health-coach works | Phase 2 |
| **3** | OpenBao on Raspberry Pi at home | TBD — Rod decides timing | Pi hardware, home network |
| **3b** | Migrate DMG passwords from Keychain → OpenBao | After Pi is live | Phase 3 |
| **4** | Remote revocation (lock from phone) | After Phase 3 stable | OpenBao API + Telegram bot |

---

## Threat Models — How the response differs

### Threat Model A: "Casual Discovery"

**Who:** IT asset scan, coworker borrowing the machine, shoulder surfer, someone browsing Finder while Rod steps away. They're not looking for Rod's data specifically — they stumble across it.

**What stops them:** They can't see the files. That's it. If `~/Work/coaches/elite-hh-bot/` doesn't show anything interesting (or doesn't exist), they move on.

**What's sufficient:**
- Encrypted DMG + Keychain password (Phase 1)
- Auto-unmount when not in use (so the window of exposure is small)
- No need for off-machine key storage — if they don't have Rod's macOS login, Keychain is locked anyway
- GitHub private repo is fine — they're not logging into Rod's GitHub

**Mount strategy:** Auto-mount at login, auto-unmount after idle timeout or on schedule (e.g., midnight). Convenience matters more than lockdown. The goal is "not visible most of the time," not "Fort Knox."

**What you DON'T need:**
- OpenBao on Pi (overkill)
- git-crypt on the remote (they're not on GitHub)
- Remote revocation (they're not persistent)

**Residual risk you accept:** If Rod's macOS session is unlocked and the DMG is mounted, files are visible. That's a ~minutes window during active use. Acceptable for this threat.

---

### Threat Model B: "Targeted Investigation"

**Who:** IT department actively investigating Rod's machine. HR-initiated. Corporate forensics. MDM remote access. They're looking specifically at Rod's activity, possibly with admin-level access to the machine.

**What they can do:**
- Access the filesystem remotely via MDM or screen sharing
- Dump Keychain entries if they have admin access or Rod's login
- Read process lists, see what's mounted, check bash history
- Access any running process's memory
- Image the disk entirely

**What Phase 1 alone does NOT stop:**
- If they have Rod's macOS password (or admin override), they can read Keychain → get DMG password → mount it
- If the DMG is mounted during the investigation, the files are plaintext at `/Volumes/`
- `bash_history` or shell logs may show mount commands, file paths, git operations
- Spotlight / `mds` indexes may have cached file names and contents from when the DMG was mounted

**What's required (Phase 1 + hardening):**
- Everything from Threat Model A, PLUS:
- **Exclude from Spotlight:** `mdutil -i off /Volumes/elite-hh-bot` or add to Spotlight privacy list
- **Shell history hygiene:** Don't log mount commands (or use a wrapper that doesn't hit history)
- **Shorter mount windows:** Mount only during active agent runs, unmount immediately after. Cron mounts for 60 seconds, runs poller, unmounts.
- **Review MDM exposure:** What does the company MDM see? File listings? Process lists? If MDM can see `/Volumes/` contents, the mount window matters a lot.

**What Phase 3 adds (OpenBao on Pi):**
- DMG password is NOT on the machine at all. It's fetched from a Pi at Rod's house over an encrypted tunnel.
- Even with full admin access to the Mac mini, they cannot decrypt the DMG — the key isn't there.
- Rod can revoke the key remotely (kill the OpenBao lease from his phone) if he suspects investigation.
- This is the "I'm confident even under forensic examination" tier.

**What Phase 3 still doesn't cover:**
- If they image the disk while the DMG is mounted (files are plaintext in memory / on the APFS layer)
- RAM forensics while mounted
- Keylogger capturing the mount password (irrelevant if key comes from network, but relevant if they intercept the API call)

**Mount strategy:** Strictly on-demand. No auto-mount at login. Cron poller mounts → runs → unmounts in <60 seconds. Manual mount only when Rod is actively in a session. Every minute mounted is a minute of exposure.

**Additional hardening for this model:**
- `history -d` or `HISTIGNORE` patterns for mount/security commands
- Spotlight exclusion for the volume
- Consider whether the `.sparseimage` file name itself is suspicious — could rename to something innocuous
- Consider moving the `.sparseimage` to an external drive that's only connected during sessions
- git-crypt on the GitHub remote (so even if they access Rod's GitHub, the repo contents are encrypted)
- Audit: which processes access `/Volumes/elite-hh-bot` (use `fs_usage` or `opensnoop` to understand exposure surface)

---

### Decision matrix

| Concern | Model A (casual) | Model B (targeted) |
|---------|-------------------|---------------------|
| DMG encryption | Yes | Yes |
| Key in Keychain | Sufficient | Insufficient — need off-machine (Phase 3) |
| Mount strategy | Auto-mount, idle-unmount | On-demand only, minimal windows |
| Spotlight indexing | Nice to disable | Must disable |
| Shell history | Don't worry | Scrub mount commands |
| GitHub remote | Private repo fine | git-crypt or encrypted remote |
| MDM awareness | Not a factor | Must understand what MDM sees |
| Remote revocation | Not needed | Critical (Phase 3/4) |
| Dropbox backup | Nice to have | Useful — encrypted blob offsite |
| Timeline to secure | Phase 1 is enough | Need Phase 1 now + Phase 3 soon |

---

## Questions for Rod to sit with

1. **Which threat model is yours?** Be honest. If this is "I don't want someone casually seeing my resumes," Phase 1 ships today and you're done for months. If this is "I think IT might look at my machine," we need to move faster on Phase 3 and harden more aggressively.

2. **Does your company run MDM?** If yes, what does it see? This changes the mount strategy entirely.

3. **How often do you actually close the lid on the mini?** If it's always-on and logged in, the DMG being mounted most of the time means it's only protected during the unmount windows. Is that enough, or do you want it locked tighter?

4. **Do you want the agents to be able to self-mount?** The cron poller could mount, run, unmount automatically — but that means the password is retrievable by any process running as your user. That's the current Keychain model anyway, but worth being explicit about.

5. **Dropbox as encrypted backup?** The `.sparseimage` file could live in Dropbox as an offsite backup. It's encrypted, so Dropbox sees nothing. But it's ~500MB per repo syncing. Worth it?

6. **What about the git remote?** The GitHub repo (Roderick-Clemente/elite-hh-bot) is still plaintext on GitHub's servers. Encryption at rest on the mini doesn't protect the remote. Is the private repo on GitHub sufficient, or do you eventually want the remote encrypted too (e.g., git-crypt for the remote copy)?

7. **Pi timeline** — do you already have a Pi, or is this a purchase? If you're serious about Phase 3, we should spec the hardware and get it ordered so it's ready when you are.
