# Proposal: Elevated Permissions for Mad Max

**Status:** Decision needed from Rod

## The Problem

Every session hits a sudo wall. Common blockers:
- Power settings (`pmset`)
- Remote login toggle (`systemsetup`)
- Removing system daemons (`launchctl`, `/Library/LaunchDaemons/`)
- `brew services` (some commands need sudo)

This forces Rod to intervene on tasks that are low-risk and well-defined.
The mini can't operate autonomously without this resolved.

## Options

**A — Targeted sudoers entries (recommended)**
Add specific commands to `/etc/sudoers.d/madmax`:
```
macBot ALL=(ALL) NOPASSWD: /usr/bin/pmset
macBot ALL=(ALL) NOPASSWD: /usr/bin/systemsetup
macBot ALL=(ALL) NOPASSWD: /bin/launchctl
```
Scoped, auditable, doesn't open broad sudo. Rod reviews and approves the list.

**B — Rod pastes sudo commands**
Keep current pattern. Mad Max surfaces a clean block of sudo commands,
Rod pastes them in. Works but requires Rod to be present for anything system-level.

**C — Broad sudo NOPASSWD**
`macBot ALL=(ALL) NOPASSWD: ALL` — too open, don't do this.

## Recommendation

Option A. Write a tight sudoers file scoped to the commands that actually come up.
Rod reviews it, runs `visudo` to install it once. Done.

## Decision Needed

Which option? If A, Mad Max drafts the sudoers file for Rod's review before install.
