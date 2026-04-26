# System Hardening Log

## Machine
- Model: Mac mini, Apple M4, 10-core, 32GB
- OS: macOS Darwin 25.3.0
- User: macBot

---

## Completed

### SIP (System Integrity Protection)
- **Status:** Enabled (default, verified)
- Protects core OS files from modification even by root

### FileVault
- **Status:** On (default, verified)
- Full disk encryption — data unreadable without login

### macOS Firewall
- **Status:** Enabled (verified)
- **Stealth Mode:** Enabled manually
  - Machine will not respond to ping or unsolicited port scans
  ```bash
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
  ```

### Ollama API Lockdown
- **Status:** Bound to 127.0.0.1:11434 (localhost only)
- Verified via `lsof -i :11434` — not exposed on network interfaces
- `OLLAMA_HOST=127.0.0.1` added to `~/.zshrc` for persistence
- Prevents LLMjacking / unauthorized GPU usage from network

### SSH
- Generated ed25519 key: `~/.ssh/id_ed25519`
- Added to GitHub account (MadMaxMini)
- SSH config written to `~/.ssh/config` — key persists across reboots via agent
- Git remote switched from HTTPS to SSH for all repos

### Open Ports Audit
- Only external-facing port found: `symptomsd` on 53893
- **Verdict:** Legitimate Apple system daemon (`_networkd` user)
  - Part of `Symptoms.framework` — monitors network health/diagnostics
  - No config, not meant to be touched, leave as-is

---

## Pending

- [ ] Sudoers config — targeted rules for Claude to run specific commands without password
- [ ] Docker no-network setup for Tier 2 (Chinese) model isolation
- [ ] Open WebUI auth — if/when exposed beyond localhost
- [ ] Periodic port audit (add to cron or launchd)
- [ ] Review firewall allowed apps list
- [ ] Monitor Ollama network activity (confirm no telemetry)
- [ ] Little Snitch — evaluate for per-app outbound control

---

## Reference Commands

```bash
# Check SIP
csrutil status

# Check FileVault
fdesetup status

# Check firewall
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Check stealth mode
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode

# Enable stealth mode
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on

# Check what's listening externally
netstat -an | grep LISTEN | grep -v "127.0.0.1\|::1"

# Check specific port
sudo lsof -i :<port>

# Check Ollama binding
lsof -i :11434
```
