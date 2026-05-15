#!/usr/bin/env python3
# dispatcher.py — channel-agnostic command dispatcher
#
# Default model: mistral-small:latest (local Ollama)
# Three model switch modes:
#   - Temporary (default): /model gemma  → 2h TTL, then reverts
#   - Temporary custom:    /model gemma 30m or /model fast 4h
#   - Permanent:           /model mistral perm (explicit keyword)
#   - One-off:             "use claude" in message (this message only)
#
# Called by log-watcher.py (SMS) and email-poller.py (email).
# dispatch(body, reply_fn, context="text")

import subprocess
import logging
import re
import json
import urllib.request
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path

HOME     = Path.home()
LOG_FILE = HOME / "Work/test/local/scripts/dispatcher.log"
logging.basicConfig(
    filename=str(LOG_FILE), level=logging.INFO,
    format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
def log(msg): logging.info(msg)

OLLAMA_URL    = "http://127.0.0.1:11434/api/generate"
MODEL_DEFAULT = "mistral-small:latest"
MODEL_FAST    = "llama3.2:3b"
MODEL_GEMMA   = "gemma3:27b"

MODEL_STATE_FILE = HOME / "Work/test/local/scripts/dispatcher-model.state"
MODEL_TTL_STATE_FILE = HOME / "Work/test/local/scripts/dispatcher-model-ttl.state"

MODEL_NAMES = {
    "claude":  "Claude (Anthropic CLI)",
    "gemma":   "gemma3:27b (Ollama local)",
    "fast":    "llama3.2:3b (Ollama local)",
    "default": "mistral-small:latest (Ollama local)",
}

def get_persistent_model():
    try:    return MODEL_STATE_FILE.read_text().strip()
    except: return "default"

def set_persistent_model(label):
    MODEL_STATE_FILE.write_text(label)

def get_ttl_model():
    """Check TTL model state; return (label, remaining_mins) or (None, None) if expired/missing."""
    if not MODEL_TTL_STATE_FILE.exists():
        return None, None
    try:
        data = json.loads(MODEL_TTL_STATE_FILE.read_text())
        expires_at = datetime.fromisoformat(data["expires_at"])
        now = datetime.now()
        if now > expires_at:
            MODEL_TTL_STATE_FILE.unlink()
            return None, None
        remaining = (expires_at - now).total_seconds() / 60
        return data["label"], remaining
    except Exception:
        return None, None

def set_ttl_model(label, minutes):
    """Set temporary model switch; expires in minutes."""
    expires_at = datetime.now() + timedelta(minutes=minutes)
    data = {"label": label, "expires_at": expires_at.isoformat()}
    MODEL_TTL_STATE_FILE.write_text(json.dumps(data))

def _load_soul(context="text"):
    if context == "telegram":
        soul_path = HOME / "Work/local/scripts/SOUL-telegram.md"
    else:
        soul_path = HOME / "Work/test/SOUL.md"
    try:
        return soul_path.read_text().strip()
    except:
        return ""

_SOUL_TEXT = _load_soul("text")
_SOUL_TELEGRAM = _load_soul("telegram")

SYSTEM_STATIC_FALLBACK = """You are Mad Max — the automation bot on Rod Clemente's Mac mini (M4, 32GB, macOS).

WHO YOU ARE:
- You run on this machine 24/7, monitoring SMS and email
- You can answer questions, summarize context, and suggest commands — but you cannot execute anything
- If Rod asks you to do something on the machine, tell him the command to run, don't claim you did it
- Reply in plain text, 2-5 sentences max — this goes to Rod's phone

THE SETUP:
- Rod runs Dakota Enterprises LLC — real estate team: Rod, Devon (brother, dclemen87@gmail.com), Doc (father, +19739704525), Sharon (Philippines, +639451631830)
- iMessage gateway reads incoming texts from Rod, routes to you
- Email poller watches macbotpooterson@gmail.com for @dakotaentllc.com mail
- Daily standup fires 7am weekdays — sends to Dakota group
- Night planner fires 10pm — picks tasks, texts Rod for approval
- Secrets in OpenBao (http://127.0.0.1:8200), local AI via Ollama (http://127.0.0.1:11434)

KEY PATHS:
- Backlog: ~/Work/test/backlog.md
- Session log: ~/Work/test/session-log.md
- Dakota team tasks: ~/Work/dakota-software/people/*/tasks.md
- Scripts: ~/Work/local/scripts/
- Agent queue: ~/Work/local/scripts/agent-queue.json
- Contacts (mini-local): ~/Work/local/scripts/contacts.md

MODEL SWITCHING (3 modes):
- Permanent: /model mistral (sticks until changed)
- Temporary: /model gemma 2h (expires in 2 hours, then reverts)
- One-off: "use claude" in message (this message only, then reverts)
- Query: /model? → report current active model

NIGHT AGENT COMMANDS (when Rod replies to AutoMax task proposals):
- "go 1" / "go 2" → approve and run that task
- "go all" → approve and run all pending tasks
- "skip 1" / "skip 2" → skip that task
- "stop" → cancel all pending tasks

RULES:
- If Rod asks you to do something → do it, report back concisely
- If you need one piece of info → ask it
- Never claim you can't access files or run commands — you can
- Don't pad replies"""


def _get_system_prompt(context="text"):
    if context in ("telegram", "group") and _SOUL_TELEGRAM:
        return _SOUL_TELEGRAM
    return _SOUL_TEXT or SYSTEM_STATIC_FALLBACK


QUEUE_FILE    = HOME / "Work/local/scripts/agent-queue.json"
AUTO_AGENT    = HOME / "Work/local/scripts/auto-agent.py"
NIGHT_PLANNER = HOME / "Work/local/scripts/night-planner.py"


def build_live_context():
    """Read live machine state and return as a string to inject into prompts."""
    parts = [f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]

    # Backlog P0/P1
    backlog = HOME / "Work/test/backlog.md"
    if backlog.exists():
        lines = backlog.read_text().splitlines()
        # Grab everything up to P2
        section = []
        for line in lines:
            if "## P2" in line:
                break
            section.append(line)
        parts.append("BACKLOG (P0/P1):\n" + "\n".join(section[:50]))

    # Running dakotaops services
    try:
        r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        running = [l.split()[-1] for l in r.stdout.splitlines()
                   if "dakotaops" in l and not l.startswith("-")]
        if running:
            parts.append("Running services: " + ", ".join(running))
    except Exception:
        pass

    # Last session log entry (first 20 lines of most recent)
    session_log = HOME / "Work/test/session-log.md"
    if session_log.exists():
        lines = session_log.read_text().splitlines()
        entry = []
        in_entry = False
        for line in lines:
            if line.startswith("## 202"):
                if in_entry:
                    break
                in_entry = True
            if in_entry:
                entry.append(line)
            if len(entry) > 20:
                break
        if entry:
            parts.append("LAST SESSION:\n" + "\n".join(entry))

    return "\n\n".join(parts)


# ── Model calls ───────────────────────────────────────────────────────────────

def call_ollama(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 500, "temperature": 0.4}
    }).encode()
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except Exception as e:
        log(f"[dispatcher] ollama error ({model}): {e}")
        return None


def find_claude_binary():
    pattern = str(HOME / ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")
    matches = sorted(glob(pattern))
    return matches[-1] if matches else None


def call_claude(prompt):
    binary = find_claude_binary()
    if not binary:
        return None
    try:
        r = subprocess.run(
            [binary, "-p", prompt],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()[:500]
    except Exception as e:
        log(f"[dispatcher] claude error: {e}")
    return None


def run_model(body, context="text", history=""):
    cmd_lower = body.lower()

    # Priority order: one-off > TTL > persistent > default
    # One-off override keywords take priority over all state
    if "use claude" in cmd_lower or "ask claude" in cmd_lower:
        model_label = "claude"
    elif "use gemma" in cmd_lower or "ask gemma" in cmd_lower:
        model_label = "gemma"
    elif "use fast" in cmd_lower or "use small" in cmd_lower:
        model_label = "fast"
    elif "use mistral" in cmd_lower or "use local" in cmd_lower:
        model_label = "default"
    else:
        # Check TTL model (temporary, expires in 1-2 hours)
        ttl_label, remaining_mins = get_ttl_model()
        if ttl_label:
            model_label = ttl_label
        else:
            # Check persistent model (permanent until changed)
            persistent = get_persistent_model()
            if persistent in (None, "", "default") and context == "text":
                # iMessage default = Claude (better conversational nuance).
                # Mistral kicks in via fallback chain below if Claude fails.
                model_label = "claude"
            else:
                model_label = persistent or "default"

    live_ctx = build_live_context()
    history_block = f"\n\nRecent conversation:\n{history}" if history else ""
    system_prompt = _get_system_prompt(context)
    full_prompt = f"{system_prompt}\n\nActive model: {MODEL_NAMES.get(model_label, model_label)}\n\n{live_ctx}{history_block}\n\nChannel: {context}\nRod says: {body}"

    claude_attempted = False  # track for fallback notification

    if model_label == "claude":
        log(f"[dispatcher] → claude")
        claude_attempted = True
        result = call_claude(full_prompt)
        if result:
            return result
        log(f"[dispatcher] claude failed — falling back to mistral")

    if model_label == "gemma":
        log(f"[dispatcher] → gemma3:27b")
        result = call_ollama(MODEL_GEMMA, full_prompt)
        if result:
            return result

    if model_label == "fast":
        log(f"[dispatcher] → llama3.2:3b")
        result = call_ollama(MODEL_FAST, full_prompt)
        if result:
            return result

    # Default: mistral-small
    log(f"[dispatcher] → mistral-small:latest")
    result = call_ollama(MODEL_DEFAULT, full_prompt)
    if result:
        if claude_attempted:
            return f"⚠️ Claude unavailable — replied via Mistral.\n\n{result}"
        return result

    # Final fallback: claude (skip if we already tried it above)
    if not claude_attempted:
        log(f"[dispatcher] ollama failed, falling back to claude")
        result = call_claude(full_prompt)
        if result:
            return result

    return "⚠️ All models down. Both Claude and Mistral failed. Check ollama, network, and Claude CLI."


# ── Fast commands ─────────────────────────────────────────────────────────────

def cmd_status():
    parts = []
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        models = [l.split()[0] for l in r.stdout.strip().splitlines()[1:] if l.strip()]
        parts.append(f"ollama: {', '.join(models) if models else 'none'}")
    except Exception:
        parts.append("ollama: error")
    try:
        r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=10)
        containers = r.stdout.strip().replace("\n", ", ") or "none"
        parts.append(f"docker: {containers}")
    except Exception:
        parts.append("docker: error")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8200/v1/sys/health", timeout=3) as resp:
            d = json.loads(resp.read())
            parts.append("vault: " + ("sealed" if d.get("sealed") else "open"))
    except Exception:
        parts.append("vault: down")
    return " | ".join(parts)


def cmd_pull(model):
    try:
        r = subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=300)
        return f"pulled {model} ✓" if r.returncode == 0 else f"pull failed: {r.stderr.strip()[:80]}"
    except Exception as e:
        return f"pull error: {e}"


# ── Night agent queue commands ─────────────────────────────────────────────────

def load_agent_queue():
    try:
        return json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else None
    except Exception:
        return None


def save_agent_queue(q):
    QUEUE_FILE.write_text(json.dumps(q, indent=2))


def cmd_agent_go(task_id_or_all):
    """Approve and launch auto-agent for one task or all."""
    q = load_agent_queue()
    if not q:
        return "No task queue found. Night planner runs at 10pm."

    from datetime import datetime as _dt
    if _dt.fromisoformat(q["expires"]) < _dt.now():
        return "Queue expired. Night planner will queue new tasks at 10pm."

    if task_id_or_all == "all":
        pending = [t for t in q["tasks"] if t["status"] == "pending"]
    else:
        try:
            tid = int(task_id_or_all)
            pending = [t for t in q["tasks"] if t["id"] == tid and t["status"] == "pending"]
        except ValueError:
            return f"Invalid task ID: {task_id_or_all}"

    if not pending:
        return "No pending tasks for that ID."

    ids = [str(t["id"]) for t in pending]
    arg = "all" if task_id_or_all == "all" else ids[0]

    # Mark as in-progress before launching
    for t in pending:
        t["status"] = "running"
    save_agent_queue(q)

    # Launch auto-agent in background
    subprocess.Popen(
        ["/usr/bin/python3", str(AUTO_AGENT), arg],
        stdout=open(str(HOME / "Work/local/scripts/auto-agent.log"), "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    names = [t["description"][:40] for t in pending]
    return f"AutoMax launched: {', '.join(names)}. I'll text you when done."


def cmd_agent_skip(task_id_or_all):
    """Skip one task or all pending."""
    q = load_agent_queue()
    if not q:
        return "No queue."

    if task_id_or_all == "all":
        skipped = 0
        for t in q["tasks"]:
            if t["status"] == "pending":
                t["status"] = "skipped"
                skipped += 1
        save_agent_queue(q)
        return f"Skipped {skipped} task(s)."
    else:
        try:
            tid = int(task_id_or_all)
        except ValueError:
            return f"Invalid ID: {task_id_or_all}"
        for t in q["tasks"]:
            if t["id"] == tid:
                t["status"] = "skipped"
                save_agent_queue(q)
                return f"Skipped task {tid}."
        return f"Task {tid} not found."


def cmd_agent_stop():
    """Cancel all pending tasks."""
    q = load_agent_queue()
    if not q:
        return "No active queue."
    count = 0
    for t in q["tasks"]:
        if t["status"] == "pending":
            t["status"] = "cancelled"
            count += 1
    save_agent_queue(q)
    return f"Cancelled {count} pending task(s). Queue cleared."


def cmd_agent_queue():
    """Show current queue status."""
    q = load_agent_queue()
    if not q:
        return "No queue. Night planner runs at 10pm."
    lines = [f"Queue ({q['date']}):"]
    for t in q["tasks"]:
        icon = {"pending": "⏳", "running": "🔄", "done": "✓", "failed": "✗",
                "skipped": "—", "cancelled": "✕", "expired": "💀"}.get(t["status"], "?")
        lines.append(f"  [{t['id']}] {icon} {t['description'][:50]}")
    return "\n".join(lines)


def cmd_agent_plan():
    """Manually trigger night planner."""
    subprocess.Popen(
        ["/usr/bin/python3", str(NIGHT_PLANNER)],
        stdout=open(str(HOME / "Work/local/scripts/night-planner.log"), "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    return "Night planner running — I'll text you the plan in a minute."


# ── Sweep / inbox commands (read-only) ────────────────────────────────────────

REFERENCE_MODELS = HOME / "Work/local/scripts/reference-models.md"
BOTTLEMSG_DIR = HOME / "Library/CloudStorage/Dropbox/bottleMsg"
EMAIL_INBOX   = HOME / "Work/local/scripts/email-inbox.md"

BOTTLEMSG_SKIP = {"archive", "mini-control-guide.md", "reviews", ".DS_Store"}


def _list_bottlemsg():
    """List actionable items in bottleMsg (skip archive, permanent files)."""
    if not BOTTLEMSG_DIR.exists():
        return []
    items = []
    for p in sorted(BOTTLEMSG_DIR.iterdir()):
        if p.name in BOTTLEMSG_SKIP or p.name.startswith("."):
            continue
        if p.is_dir():
            continue
        age_hrs = (datetime.now().timestamp() - p.stat().st_mtime) / 3600
        suffix = p.suffix.lower()
        if suffix in (".md", ".txt"):
            kind = "note"
        elif suffix in (".png", ".jpg", ".jpeg", ".heic"):
            kind = "screenshot"
        elif suffix in (".m4a", ".mp3", ".wav"):
            kind = "audio"
        elif suffix in (".pdf",):
            kind = "pdf"
        elif suffix in (".kdbx",):
            kind = "keypass"
        else:
            kind = "file"
        items.append({"name": p.name, "kind": kind, "age_hrs": age_hrs})
    return items


def _list_email_inbox():
    """List unprocessed entries from email-inbox.md."""
    if not EMAIL_INBOX.exists():
        return []
    items = []
    for line in EMAIL_INBOX.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ["):
            items.append(line)
    return items


def _fmt_age(hrs):
    if hrs < 1:
        return f"{int(hrs * 60)}m"
    if hrs < 24:
        return f"{hrs:.0f}h"
    return f"{hrs / 24:.0f}d"


def cmd_sweep():
    """Show pending items across bottleMsg and email inbox."""
    btl = _list_bottlemsg()
    emails = _list_email_inbox()

    if not btl and not emails:
        return "Inbox zero. Nothing in bottleMsg or email inbox."

    parts = []
    if btl:
        parts.append(f"📬 bottleMsg ({len(btl)} items):")
        for i, item in enumerate(btl, 1):
            parts.append(f"  {i}. [{item['kind']}] {item['name']} ({_fmt_age(item['age_hrs'])} old)")

    if emails:
        parts.append(f"\n📧 Email inbox ({len(emails)} entries):")
        for line in emails[:10]:  # cap at 10 to keep message short
            parts.append(f"  {line[:120]}")
        if len(emails) > 10:
            parts.append(f"  ... and {len(emails) - 10} more")

    parts.append(f"\nTotal: {len(btl)} bottleMsg + {len(emails)} email")
    parts.append("(Read-only view — use a Claude Code session to process items)")
    return "\n".join(parts)


def cmd_inbox():
    """Quick count of pending items."""
    btl = _list_bottlemsg()
    emails = _list_email_inbox()
    return f"📬 bottleMsg: {len(btl)} items | 📧 email: {len(emails)} entries"


# ── Digest browser (bottleMsg/digest content navigation) ─────────────────────

BROWSE_STATE = HOME / "Work/local/scripts/digest-browse-state.json"

def _first_meaningful_line(p, maxlen=80):
    """Return the first non-empty, non-frontmatter line of a file."""
    if p.suffix.lower() not in (".md", ".txt"):
        return ""
    try:
        text = p.read_text(errors="ignore")
    except Exception:
        return ""
    in_frontmatter = False
    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if i == 0 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if not line or line.startswith("#"):
            # take H1/H2 if no other content
            if line.startswith("#") and not line.lstrip("#").strip() == "":
                return line.lstrip("#").strip()[:maxlen]
            continue
        return line[:maxlen]
    return ""

def _save_browse(items):
    """Save current browse list so /read N references it."""
    BROWSE_STATE.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "items": [str(p) for p in items],
    }))

def _load_browse():
    if not BROWSE_STATE.exists():
        return None
    try:
        return json.loads(BROWSE_STATE.read_text())
    except Exception:
        return None

def cmd_digest(args):
    """List items in bottleMsg/digest, sorted by newest. Args: N | today | topic."""
    digest = BOTTLEMSG_DIR / "digest"
    if not digest.exists():
        return "No digest folder."

    files = [p for p in digest.iterdir() if p.is_file() and not p.name.startswith(".")]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not files:
        return "📭 digest is empty."

    arg = (args or "").strip().lower()
    today = None
    n = 5

    if arg == "today":
        today = datetime.now().date()
        files = [p for p in files if datetime.fromtimestamp(p.stat().st_mtime).date() == today]
        if not files:
            return "📭 nothing in digest from today."
    elif arg == "topic":
        # Group by leading date prefix or first word
        groups = {}
        for p in files:
            slug = p.stem
            for prefix in ["2026-", "2025-"]:
                if slug.startswith(prefix):
                    slug = slug[11:]  # strip YYYY-MM-DD-
                    break
            key = slug.split("-")[0] if "-" in slug else slug.split("_")[0] if "_" in slug else slug[:20]
            groups.setdefault(key.lower(), []).append(p)
        lines = ["📚 digest by topic:\n"]
        for key in sorted(groups.keys(), key=lambda k: -len(groups[k])):
            lines.append(f"• {key} ({len(groups[key])})")
        lines.append("\nTo see one: /dig <keyword>")
        return "\n".join(lines)
    elif arg.isdigit():
        n = int(arg)

    files = files[:n]
    _save_browse(files)

    lines = [f"📚 digest — {len(files)} {'newest' if not today else 'today'}:\n"]
    for i, p in enumerate(files, 1):
        age_hrs = (datetime.now().timestamp() - p.stat().st_mtime) / 3600
        preview = _first_meaningful_line(p)
        lines.append(f"{i}. {p.name}  ({_fmt_age(age_hrs)})")
        if preview:
            lines.append(f"   ↳ {preview}")
    lines.append("\nReply: /read N (open one) · /dig <keyword> (search)")
    return "\n".join(lines)


def cmd_dig(keyword):
    """Search across digest + inbox for keyword in filename or content."""
    keyword = (keyword or "").strip()
    if not keyword:
        return "Usage: /dig <keyword>"
    kw = keyword.lower()

    matches = []
    for folder in ("digest", "inbox"):
        d = BOTTLEMSG_DIR / folder
        if not d.exists():
            continue
        for p in d.iterdir():
            if not p.is_file() or p.name.startswith("."):
                continue
            if kw in p.name.lower():
                matches.append((p, "filename"))
                continue
            if p.suffix.lower() in (".md", ".txt"):
                try:
                    if kw in p.read_text(errors="ignore").lower():
                        matches.append((p, "content"))
                except Exception:
                    pass

    if not matches:
        return f"🔍 No matches for '{keyword}'."

    matches.sort(key=lambda mp: mp[0].stat().st_mtime, reverse=True)
    paths = [mp[0] for mp in matches]
    _save_browse(paths[:20])

    lines = [f"🔍 '{keyword}' — {len(matches)} match{'es' if len(matches) != 1 else ''}:\n"]
    for i, (p, where) in enumerate(matches[:20], 1):
        age_hrs = (datetime.now().timestamp() - p.stat().st_mtime) / 3600
        lines.append(f"{i}. {p.parent.name}/{p.name}  [{where}]  ({_fmt_age(age_hrs)})")
    if len(matches) > 20:
        lines.append(f"\n... and {len(matches) - 20} more")
    lines.append("\nReply: /read N to open one")
    return "\n".join(lines)


def cmd_read(arg):
    """Read file content by browse-list number or filename."""
    arg = (arg or "").strip()
    if not arg:
        return "Usage: /read N or /read <filename>"

    target = None
    if arg.isdigit():
        state = _load_browse()
        if not state:
            return "No active browse list. Try /digest or /dig <keyword> first."
        idx = int(arg) - 1
        if idx < 0 or idx >= len(state["items"]):
            return f"Item {arg} not in browse list (have {len(state['items'])})."
        target = Path(state["items"][idx])
    else:
        # Try to find by filename match
        for folder in ("digest", "inbox", "archive"):
            d = BOTTLEMSG_DIR / folder
            if not d.exists():
                continue
            for p in d.iterdir():
                if p.is_file() and arg.lower() in p.name.lower():
                    target = p
                    break
            if target:
                break

    if not target or not target.exists():
        return f"Couldn't find '{arg}'."

    if target.suffix.lower() not in (".md", ".txt"):
        return f"📎 {target.name} — not a text file ({target.suffix}). Open in Dropbox."

    try:
        content = target.read_text(errors="ignore")
    except Exception as e:
        return f"Read failed: {e}"

    # Keep under Telegram limit (~4000 chars per message; poller chunks bigger)
    header = f"📄 {target.parent.name}/{target.name}\n{'─' * 30}\n"
    return header + content


# ── GTD sweep commands ───────────────────────────────────────────────────────

GTD_SWEEP_SCRIPT = HOME / "Work/local/scripts/gtd-sweep.py"
GTD_STATE_FILE   = HOME / "Work/local/scripts/gtd-sweep-state.json"

# ── Meme support (Telegram only) ─────────────────────────────────────────────
import random

MEME_PATHS = {
    "boom":   HOME / "Downloads/boom",
    "vanish": HOME / "Downloads/vanish",
    "hold":   HOME / "Downloads/hold",
}

def _send_meme(category, caption=None):
    """Pick a random image/gif from category folder and send to Rod's Telegram. Silent no-op if folder missing/empty."""
    folder = MEME_PATHS.get(category)
    if not folder or not folder.exists():
        return
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in (".gif", ".jpg", ".jpeg", ".png", ".mp4", ".webp")]
    if not files:
        return
    pick = random.choice(files)
    try:
        token = subprocess.check_output(["security", "find-generic-password", "-a", "macBot", "-s", "telegram-max-bot-token", "-w"], text=True).strip()
        chat_id = subprocess.check_output(["security", "find-generic-password", "-a", "macBot", "-s", "telegram-max-chat-id", "-w"], text=True).strip()
    except Exception as e:
        log(f"[meme] keychain lookup failed: {e}")
        return
    endpoint = "sendAnimation" if pick.suffix.lower() in (".gif", ".mp4") else "sendPhoto"
    field    = "animation"    if pick.suffix.lower() in (".gif", ".mp4") else "photo"
    cmd = ["curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{token}/{endpoint}",
           "-F", f"chat_id={chat_id}", "-F", f"{field}=@{pick}"]
    if caption:
        cmd += ["-F", f"caption={caption}"]
    try:
        subprocess.run(cmd, capture_output=True, timeout=20)
        log(f"[meme] sent {category}/{pick.name}")
    except Exception as e:
        log(f"[meme] send failed: {e}")


def _load_gtd_state():
    if not GTD_STATE_FILE.exists():
        return None
    try:
        state = json.loads(GTD_STATE_FILE.read_text())
        expires = datetime.fromisoformat(state["expires"])
        if datetime.now() > expires:
            GTD_STATE_FILE.unlink()
            return None
        return state
    except Exception:
        return None


def _clear_gtd_state():
    if GTD_STATE_FILE.exists():
        GTD_STATE_FILE.unlink()


def cmd_gtd_sweep():
    """Trigger a GTD sweep now."""
    subprocess.Popen(
        ["/usr/bin/python3", str(GTD_SWEEP_SCRIPT)],
        stdout=open(str(HOME / "Work/local/scripts/gtd-sweep.log"), "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    return "GTD sweep running — table incoming."


def _load_gtd_module():
    """Dynamic-load gtd-sweep.py so we can call record_correct/record_correction."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gtd_sweep", str(GTD_SWEEP_SCRIPT))
    gtd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gtd)
    return gtd


def cmd_gtd_go(nums=None):
    """Approve and execute moves. nums=None means all."""
    state = _load_gtd_state()
    if not state:
        return "No active GTD sweep. Send `gtd` to start one."

    items = state["items"]
    if nums:
        to_move = [i for i in items if i["num"] in nums]
        if not to_move:
            return f"No items match numbers: {nums}"
    else:
        to_move = [i for i in items if i["route"] != "stays"]

    gtd = _load_gtd_module()
    moved, failed = gtd.execute_moves(to_move)

    # Learning: items that successfully moved at their proposed route = correct guess
    moved_names = set(moved) if isinstance(moved, list) and moved and isinstance(moved[0], str) else set()
    for item in to_move:
        if item["name"] in moved_names or any(item["name"] in m for m in moved):
            gtd.record_correct()

    parts = []
    if moved:
        parts.append(f"💥 BOOM — moved {len(moved)} item{'s' if len(moved)!=1 else ''}:")
        for m in moved:
            parts.append(f"  ✨ {m}")
        # Streak badge if applicable
        badge = gtd.streak_badge()
        if badge:
            parts.append(badge)
        _send_meme("boom")
    if failed:
        parts.append(f"💀 Failed ({len(failed)}):")
        for f in failed:
            parts.append(f"  ⚠️ {f}")
    if not moved and not failed:
        parts.append("🤷 Nothing to move.")

    _clear_gtd_state()
    return "\n".join(parts)


def cmd_gtd_hold(nums):
    """Hold items — remove them from the proposal so they stay in inbox."""
    state = _load_gtd_state()
    if not state:
        return "No active GTD sweep."

    gtd = _load_gtd_module()
    held = []
    for item in state["items"]:
        if item["num"] in nums:
            # Log Rod-correction before flipping route
            gtd.record_correction(item["path"], item["route"], "stays")
            item["route"] = "stays"
            held.append(item["name"])

    GTD_STATE_FILE.write_text(json.dumps(state, indent=2))
    if held:
        return f"✋ Holding: {', '.join(held)}\nReply 'go' to move the rest."
    return f"No items match numbers: {nums}"


def cmd_gtd_move(num, dest):
    """Override the route for a single item."""
    state = _load_gtd_state()
    if not state:
        return "No active GTD sweep."

    gtd = _load_gtd_module()
    for item in state["items"]:
        if item["num"] == num:
            new_route = f"{dest}/"
            # Log Rod-correction (he overrode the proposed route)
            if item["route"] != new_route:
                gtd.record_correction(item["path"], item["route"], new_route)
            item["route"] = new_route
            GTD_STATE_FILE.write_text(json.dumps(state, indent=2))
            return f"↗️ #{num} ({item['name']}) → {dest}/\nReply 'go' to execute."

    return f"No item #{num} in current sweep."


def cmd_gtd_skip():
    """Dismiss the current sweep without moving anything."""
    _clear_gtd_state()
    return "👻 Poof! GTD sweep dismissed. Nothing moved."


# ── Main entry point ──────────────────────────────────────────────────────────

def dispatch(body, reply_fn, context="text", history=""):
    body = (body or "").strip()
    if not body:
        return

    # Strip leading slash so /status == status, /model == model, etc.
    cmd = body.lower().strip().lstrip("/")
    log(f"[dispatcher] [{context}] {body[:100]}")

    if cmd == "ping":
        reply_fn("pong — mini is alive")
        return

    if cmd == "status":
        reply_fn(cmd_status())
        return

    if cmd in ("help", "commands"):
        reply_fn(
            "🤖 Mad Max — Commands\n"
            "\n"
            "🗂 GTD (bottleMsg inbox)\n"
            "  /gtd            sweep + propose moves\n"
            "  /inbox          list current items\n"
            "\n"
            "  After /gtd, reply with one of:\n"
            "    go              execute ALL items\n"
            "    go 1            execute only item 1\n"
            "    go 1,3,5        execute items 1, 3, 5\n"
            "    hold 2          skip item 2 (move rest)\n"
            "    move 4 archive  override item 4's destination\n"
            "    skip            dismiss proposal\n"
            "\n"
            "📊 System\n"
            "  /status         services + last session\n"
            "  /models         list local models\n"
            "  /model?         show active model\n"
            "  /pull <name>    pull a new local model\n"
            "  /reset          clear conversation context\n"
            "  /context        show current context depth\n"
            "  /btl            write this chat to bottleMsg\n"
            "  ping            check alive\n"
            "\n"
            "🔧 Model Switching (3 modes)\n"
            "  TEMPORARY (default):  /model gemma\n"
            "    → 2h default, then reverts to permanent/default\n"
            "    → Custom duration: /model fast 30m  or  /model gemma 4h\n"
            "    → Units: Nm (minutes) or Nh (hours)\n"
            "\n"
            "  PERMANENT:  /model mistral perm\n"
            "    → Sticks until changed (add `perm` keyword)\n"
            "\n"
            "  ONE-OFF:    use claude ... (any message)\n"
            "    → This message only, reverts after\n"
            "\n"
            "  Options: claude / gemma / fast / mistral (local)\n"
            "  Check:   /model?  (shows active + remaining time)\n"
            "\n"
            "💡 Inline overrides (mid-message)\n"
            "  +context full   use full memory for this msg"
        )
        return

    if cmd in ("models", "models detail", "model audit", "model inventory", "what models"):
        if not REFERENCE_MODELS.exists():
            reply_fn("reference-models.md not found. Run a benchmark session to generate it.")
            return
        content = REFERENCE_MODELS.read_text()
        if cmd == "models detail":
            # Full file — send in chunks if needed
            if len(content) > 4000:
                # Send in chunks to avoid Telegram message limits
                chunks = [content[i:i+4000] for i in range(0, len(content), 4000)]
                for chunk in chunks:
                    reply_fn(chunk)
            else:
                reply_fn(content)
        else:
            # Summary view — installed models + verdicts only
            lines = content.splitlines()
            summary_parts = []
            in_section = False
            target_sections = ("## Installed Models", "## Speed Chart", "## Verdicts", "## Failure Modes Found")
            for line in lines:
                if any(line.startswith(s) for s in target_sections):
                    in_section = True
                    summary_parts.append(line)
                    continue
                if in_section and line.startswith("## "):
                    in_section = False
                if in_section:
                    summary_parts.append(line)
            reply_fn("\n".join(summary_parts) if summary_parts else content[:2000])
        return

    if cmd in ("sweep", "inbox sweep", "show inbox"):
        reply_fn(cmd_sweep())
        return

    if cmd == "inbox":
        reply_fn(cmd_inbox())
        return

    m = re.match(r"model\s*\??\s*$", cmd)
    if m:
        ttl_label, remaining_mins = get_ttl_model()
        if ttl_label:
            reply_fn(f"Active model: {MODEL_NAMES.get(ttl_label, ttl_label)} (temporary, expires in {remaining_mins:.0f}m)")
        else:
            current = get_persistent_model()
            reply_fn(f"Active model: {MODEL_NAMES.get(current, current)} (permanent)")
        return

    # /model X perm|permanent — explicit permanent switch
    m = re.match(r"model\s+(claude|gemma|fast|local|default|mistral)\s+(perm|permanent|forever|sticky)$", cmd)
    if m:
        label = m.group(1)
        if label in ("local", "default", "mistral"):
            label = "default"
        # Clear any TTL so persistent takes effect immediately
        if MODEL_TTL_STATE_FILE.exists():
            MODEL_TTL_STATE_FILE.unlink()
        set_persistent_model(label)
        reply_fn(f"Switched to {MODEL_NAMES.get(label, label)} permanently. Sticks until you change it.")
        return

    # /model X duration — temporary switch with explicit duration
    # Examples: /model gemma 30m, /model mistral 2h
    m = re.match(r"model\s+(claude|gemma|fast|local|default|mistral)\s+(\d+)([mh])$", cmd)
    if m:
        label = m.group(1)
        if label in ("local", "default", "mistral"):
            label = "default"
        duration = int(m.group(2))
        unit = m.group(3)
        minutes = duration * 60 if unit == "h" else duration
        set_ttl_model(label, minutes)
        reply_fn(f"Switched to {MODEL_NAMES.get(label, label)} for {duration}{unit}. Expires then reverts.")
        return

    # /model X — temporary switch with default 2h TTL (the common case)
    m = re.match(r"model\s+(claude|gemma|fast|local|default|mistral)$", cmd)
    if m:
        label = m.group(1)
        if label in ("local", "default", "mistral"):
            label = "default"
        set_ttl_model(label, 120)
        reply_fn(f"Switched to {MODEL_NAMES.get(label, label)} for 2h (default). Add `perm` to make permanent, or e.g. `30m`/`4h` for custom duration.")
        return

    m = re.match(r"pull\s+(.+)", cmd)
    if m:
        reply_fn(f"pulling {m.group(1).strip()}...")
        reply_fn(cmd_pull(m.group(1).strip()))
        return

    if re.search(r"robot\s+shutdown", cmd):
        Path("/tmp/msggateway_shutdown").write_text("shutdown")
        reply_fn("Gateway silenced. Text 'robot resume' to bring it back.")
        return

    if re.search(r"robot\s+resume", cmd):
        p = Path("/tmp/msggateway_shutdown")
        if p.exists():
            p.unlink()
        reply_fn("Back online.")
        return

    # ── Night agent approval commands ──────────────────────────────────────────

    m = re.match(r"go\s+(all|\d+)$", cmd)
    if m:
        reply_fn(cmd_agent_go(m.group(1)))
        return

    m = re.match(r"skip\s+(all|\d+)$", cmd)
    if m:
        reply_fn(cmd_agent_skip(m.group(1)))
        return

    if cmd in ("stop", "stop all", "cancel", "cancel all"):
        reply_fn(cmd_agent_stop())
        return

    if cmd in ("queue", "tasks", "agent queue", "what's queued", "whats queued"):
        reply_fn(cmd_agent_queue())
        return

    if cmd in ("plan", "plan tonight", "run planner", "night plan"):
        reply_fn(cmd_agent_plan())
        return

    # ── GTD sweep commands ────────────────────────────────────────────────────

    if cmd in ("gtd", "gtd sweep"):
        reply_fn(cmd_gtd_sweep())
        return

    # ── Digest browser ────────────────────────────────────────────────────────

    m_digest = re.match(r"^digest(?:\s+(.+))?$", cmd)
    if m_digest:
        reply_fn(cmd_digest(m_digest.group(1)))
        return

    m_dig = re.match(r"^dig\s+(.+)$", cmd)
    if m_dig:
        reply_fn(cmd_dig(m_dig.group(1)))
        return

    m_read = re.match(r"^read\s+(.+)$", cmd)
    if m_read:
        reply_fn(cmd_read(m_read.group(1)))
        return

    if re.match(r"gtd\s+go(\s|$)", cmd) or cmd == "gtd go":
        m_nums = re.match(r"gtd\s+go\s+([\d,\s]+)", cmd)
        nums = None
        if m_nums:
            nums = [int(x.strip()) for x in m_nums.group(1).split(",") if x.strip().isdigit()]
        reply_fn(cmd_gtd_go(nums))
        return

    m_hold = re.match(r"gtd\s+hold\s+([\d,\s]+)", cmd)
    if m_hold:
        nums = [int(x.strip()) for x in m_hold.group(1).split(",") if x.strip().isdigit()]
        reply_fn(cmd_gtd_hold(nums))
        return

    m_move = re.match(r"gtd\s+move\s+(\d+)\s+(archive|digest|inbox)", cmd)
    if m_move:
        reply_fn(cmd_gtd_move(int(m_move.group(1)), m_move.group(2)))
        return

    if cmd in ("gtd skip", "gtd dismiss"):
        reply_fn(cmd_gtd_skip())
        return

    # ── Context-aware bare commands when active proposal exists ───────────────
    # If Rod replied to a GTD sweep with bare "go" / "hold 2" / "move 4 archive" / "skip",
    # route as GTD command instead of falling through to the LLM.
    if _load_gtd_state():
        if cmd == "go":
            reply_fn(cmd_gtd_go(None))
            return
        m_bare_go = re.match(r"^go\s+([\d,\s]+)$", cmd)
        if m_bare_go:
            nums = [int(x.strip()) for x in m_bare_go.group(1).split(",") if x.strip().isdigit()]
            reply_fn(cmd_gtd_go(nums))
            return
        m_bare_hold = re.match(r"^hold\s+([\d,\s]+)$", cmd)
        if m_bare_hold:
            nums = [int(x.strip()) for x in m_bare_hold.group(1).split(",") if x.strip().isdigit()]
            reply_fn(cmd_gtd_hold(nums))
            return
        m_bare_move = re.match(r"^move\s+(\d+)\s+(archive|digest|inbox)$", cmd)
        if m_bare_move:
            reply_fn(cmd_gtd_move(int(m_bare_move.group(1)), m_bare_move.group(2)))
            return
        if cmd in ("skip", "dismiss"):
            reply_fn(cmd_gtd_skip())
            return

    reply_fn(run_model(body, context, history=history))
