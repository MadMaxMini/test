# Proposal: Targeted Sudo Permissions for Claude

## Problem
Claude can't run certain system commands without a password prompt,
which blocks autonomous operation for firewall management, port auditing,
and service control.

---

## Requested Permissions

| Command | Path | Why |
|---------|------|-----|
| `socketfilterfw` | `/usr/libexec/ApplicationFirewall/socketfilterfw` | Firewall rules, stealth mode toggling |
| `pfctl` | `/sbin/pfctl` | pf firewall — block ports externally (e.g. 11434) |
| `launchctl` | `/bin/launchctl` | Start/stop system services (Ollama, future daemons) |
| `lsof` | `/usr/sbin/lsof` | Port auditing — identify what's listening |

---

## What This Does NOT Include
- No blanket `NOPASSWD: ALL`
- No `rm`, `dd`, `mkfs`, or destructive commands
- No network config changes beyond firewall rules
- No user/group management
- No package installs (brew doesn't need sudo anyway)

---

## Implementation
Add to `/etc/sudoers.d/claude` via `sudo visudo -f /etc/sudoers.d/claude`:

```
macBot ALL=(ALL) NOPASSWD: /usr/libexec/ApplicationFirewall/socketfilterfw
macBot ALL=(ALL) NOPASSWD: /sbin/pfctl
macBot ALL=(ALL) NOPASSWD: /bin/launchctl
macBot ALL=(ALL) NOPASSWD: /usr/sbin/lsof
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `pfctl` could block legitimate traffic | Scoped to specific rules; Claude documents all changes in harden.md |
| `launchctl` could stop services | Claude asks before stopping anything not explicitly in scope |
| Sudoers misconfiguration locks out sudo | Use `visudo` (validates syntax before saving), never edit directly |

---

## Alternatives Considered
- **Blanket NOPASSWD** — rejected, too broad
- **Separate Claude user with elevated group** — overkill for single machine
- **Stay as-is** — means Claude stops and asks for password on firewall/port work

---

## Decision
- [ ] Approved — run `sudo visudo -f /etc/sudoers.d/claude` and paste rules
- [ ] Approved with changes
- [ ] Rejected — Claude stays at user-level only
