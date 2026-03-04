# Mad Max — Concerns for Review

Items flagged during plan review. Needs Rod's decisions before proceeding.

---

## 1. Unseal Key Storage — Plaintext on Disk

**What the current plan does:**
When you run `init.sh`, OpenBao generates an unseal key and root token.
The script saves both to `~/.openbao-init` as a plain text file on your disk.

**Why that's a problem:**
FileVault protects you when the machine is OFF. When it's on and logged in,
`~/.openbao-init` is readable by any process running as your user — including
anything that might compromise your session. The vault's whole job is to protect
secrets, so storing the vault's own keys in plaintext next to it undermines that.

**Better options (pick one):**
- **A) Print once, write it down, delete the file** — you store the unseal key
  in a physical notebook or password manager (1Password, Bitwarden). Most secure.
- **B) Store in macOS Keychain** — script writes to Keychain instead of a flat file.
  Protected by your login password, much better than plaintext.
- **C) Accept the risk for now** — this machine is dedicated, FileVault is on,
  low real-world risk for a personal setup. Revisit when threat model changes.

**Recommendation:** Option B (Keychain) — best balance of security and usability.

---

## 2. macOS Account Architecture

**Current state:**
- Main admin account (your primary account on this machine?)
- `macBot` account — admin sub-account, Claude runs here

**The concern:**
If Claude (running as `macBot`) is compromised or does something dumb,
it has admin rights — meaning it could affect the whole machine, not just its sandbox.

**Options:**

| Setup | Security | Friction |
|-------|----------|---------|
| Keep macBot as admin | Low | Zero |
| Make macBot standard user | Higher | Some — can't brew install, etc. |
| macBot standard + sudoers for specific cmds | Best balance | Low — targeted rules |
| Separate non-admin `claude` user | Strong isolation | Medium — more setup |

**Recommendation:** Keep `macBot` as admin for now (this is a dedicated machine,
not shared), but revisit if Claude gets internet-facing capabilities or
you add other users. The targeted sudoers proposal already limits blast radius.

**The real question:** Is there a "main" account on this machine separate from macBot,
or is macBot your only account? If macBot IS your main account, no change needed.

---

## 3. Auto-Unseal on Boot — What and Why

**What "sealed" means:**
Every time OpenBao's Docker container restarts (after a reboot, Docker restart, etc.),
the vault starts in a "sealed" state — completely locked, serving nothing.
You have to manually run `unseal.sh` every time before it works.

**Why that's annoying:**
If the machine reboots overnight and a script tries to pull a secret from OpenBao,
it fails silently because the vault is sealed. Nothing works until you manually unseal.

**Auto-unseal options:**

- **A) launchd script** — macOS runs `unseal.sh` automatically at login.
  Simple, works, but unseal key needs to be accessible (see Concern #1 — circular problem).
- **B) Manual unseal (accept it)** — you unseal once per session when you sit down.
  For a personal machine this is totally reasonable. Low friction in practice.
- **C) OpenBao auto-unseal via cloud KMS** — use AWS KMS or similar to auto-unseal.
  Overkill for this setup, introduces cloud dependency.
- **D) Raspberry Pi as always-on unseal node** — Pi holds the unseal key,
  Mac mini pings Pi to unseal on startup. Clean architecture, already in the roadmap.

**Recommendation:** Option B for now (manual unseal is fine for a personal machine),
Option D when the Pi is set up — it solves this elegantly and is already planned.

---

## 4. What's in local/ Now

Scripts only — no data yet. Everything is uncommitted (not in git). Would be lost on a wipe.

```
~/Work/local/
  ollama/scripts/
    status.sh          # check Ollama status + loaded models
    pull-tier1.sh      # pull all Tier 1 models at once
    switch.sh          # swap loaded model
    test-api.sh        # verify API responds

  openbao/
    docker-compose.yml # OpenBao container config
    .env.example       # token template
    .gitignore         # ignores data/ and .env
    scripts/
      init.sh          # initialize vault (run once)
      unseal.sh        # unseal after restart
      status.sh        # health check
      store-secret.sh  # write a secret
      get-secret.sh    # read a secret
      setup-transit.sh # enable Transit engine + coach keys/policies
      setup-mailbox.sh # create coach workspace folder structure
      encrypt.sh       # encrypt a file via Transit
      decrypt.sh       # decrypt a file via Transit
```

**Action needed:** Move `local/` into the `madmax` repo so scripts are version controlled.
Currently at risk of being lost.

---

## Decision Checklist

- [x] **#1 Unseal key:** Combo A+B+paper — Keychain on mini (scripts), KeePass on Dropbox (laptop access), paper (fallback)
- [x] **#2 Account:** rod (owner) + macBot (admin, agent work) — keep as-is. Add dedicated standard automation user when n8n goes live (Phase 4).
- [x] **#3 Auto-unseal:** Manual for now (B). Wire launchd when overnight automations need vault access.
- [x] **#4 local/ in git:** Yes — copied into ~/Work/test/local/, committed to git.

## Future Hardening (deferred — revisit when system is running)
- Create dedicated non-admin macOS sub-account for running automation daemons (n8n, cron, etc.)
- Drop macBot from admin once automation account is in place
- Goal: limit blast radius if agent session is compromised
