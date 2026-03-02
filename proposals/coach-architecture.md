# Proposal: Coach Architecture — Encrypted Workspaces + Mailbox

## Vision
Each coach is an isolated, encrypted agent with its own workspace.
OpenBao governs all key access. Coaches communicate via a simple
file-based mailbox. n8n can enhance or automate routing later.

---

## Workspace Design

### Per-Coach Workspace
Each coach gets an isolated workspace, encrypted at rest via OpenBao's
Transit engine (encryption-as-a-service — coaches never hold raw keys).

```
~/Work/madmax/
  coaches/
    mad-max/
      workspace/           # encrypted at rest (OpenBao Transit)
      inbox/               # incoming mail
      outbox/              # sent mail (archive)
    recruiting/
      workspace/
      inbox/
      outbox/
    life-coach/            # laptop-side, same pattern
      workspace/
      inbox/
      outbox/
    [future coaches]
  shared/
    assets/                # encrypted shared resources (all coaches can read)
    inbox/                 # external input to the system (Dropbox sync lands here)
```

### Encryption Model
- **OpenBao Transit engine** — encryption-as-a-service
  - Each coach has its own named key in OpenBao (`transit/keys/mad-max`, etc.)
  - Coach requests encrypt/decrypt from OpenBao, never stores raw key
  - OpenBao controls who can access which key (policy-based)
  - Shared assets use a shared key all coaches have read access to
- **At-rest**: workspace files encrypted before write, decrypted on read
- **In-flight**: mailbox messages optionally encrypted (sender encrypts for recipient)

---

## Mailbox System

### How it works
```
Coach A writes message → drops file in Coach B's inbox/
Coach B reads inbox/ → processes → optionally replies to Coach A's inbox/
```

### Message format
```
inbox/
  2026-03-02T14:30-from-mad-max-re-model-pull.md
```

Simple markdown files. No broker, no daemon required. Just files.

### Routing conventions
- `shared/inbox/` — external world → system (Dropbox, webhooks, manual drops)
- `coaches/[name]/inbox/` — coach-to-coach messages
- `coaches/[name]/outbox/` — archive of sent messages

---

## n8n Integration (Phase 4)
n8n watches folders via filesystem trigger and can:
- Auto-route messages based on content/tags
- Trigger coach workflows on new inbox items
- Chain: `input → local model → Claude → output → inbox`
- Replace manual Dropbox sync with proper event-driven flow

Until n8n is set up, the mailbox works fine as pure files. No dependency.

---

## OpenBao Policy Design

```
# mad-max policy — can encrypt/decrypt its own workspace + read shared
path "transit/encrypt/mad-max" { capabilities = ["update"] }
path "transit/decrypt/mad-max" { capabilities = ["update"] }
path "transit/encrypt/shared"  { capabilities = ["update"] }
path "transit/decrypt/shared"  { capabilities = ["update"] }

# recruiting policy — same pattern, own key only
path "transit/encrypt/recruiting" { capabilities = ["update"] }
path "transit/decrypt/recruiting" { capabilities = ["update"] }
path "transit/encrypt/shared"     { capabilities = ["update"] }
path "transit/decrypt/shared"     { capabilities = ["update"] }
```

Each coach gets a token with its policy attached. Token stored nowhere
plaintext — retrieved at session start from OpenBao itself.

---

## Implementation Order
1. OpenBao up and initialized (already planned)
2. Enable Transit secrets engine
3. Create keys per coach (`mad-max`, `recruiting`, `shared`)
4. Write policies per coach
5. Create folder structure (`coaches/`, `shared/`)
6. Write encrypt/decrypt helper scripts per coach
7. Wire into session start (load token → decrypt workspace)
8. n8n folder watchers (Phase 4)

---

## Decision
- [ ] Approved
- [ ] Changes requested
