#!/usr/bin/env python3
# dispatcher.py — channel-agnostic command dispatcher
#
# Default model: mistral-small:latest (local Ollama)
# Persistent switch: text "model claude|gemma|fast|local"
# One-off override: say "use claude", "use gemma", "use fast" in any message
#
# Called by log-watcher.py (SMS) and email-poller.py (email).
# dispatch(body, reply_fn, context="text")

import subprocess
import logging
import re
import json
import urllib.request
from datetime import datetime
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

SYSTEM_STATIC = """You are Mad Max — the automation bot on Rod Clemente's Mac mini (M4, 32GB, macOS).

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

MODEL SWITCHING:
- Default model: mistral-small:latest
- "model claude|gemma|fast|local" → persistent switch until changed
- "use claude / use gemma / use fast" in a message → one-shot, that message only, then reverts
- "model?" → report current active model

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
        "options": {"num_predict": 200, "temperature": 0.4}
    }).encode()
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
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


def run_model(body, context="text"):
    cmd_lower = body.lower()

    # One-off override keywords take priority over persistent state
    if "use claude" in cmd_lower or "ask claude" in cmd_lower:
        model_label = "claude"
    elif "use gemma" in cmd_lower or "ask gemma" in cmd_lower:
        model_label = "gemma"
    elif "use fast" in cmd_lower or "use small" in cmd_lower:
        model_label = "fast"
    else:
        model_label = get_persistent_model()

    live_ctx = build_live_context()
    full_prompt = f"{SYSTEM_STATIC}\n\nActive model: {MODEL_NAMES.get(model_label, model_label)}\n\n{live_ctx}\n\nChannel: {context}\nRod says: {body}"

    if model_label == "claude":
        log(f"[dispatcher] → claude")
        result = call_claude(full_prompt)
        if result:
            return result

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
        return result

    # Final fallback: claude
    log(f"[dispatcher] ollama failed, falling back to claude")
    result = call_claude(full_prompt)
    if result:
        return result

    return "No model responded. Check ollama and claude. Run 'status' for diagnostics."


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


# ── Main entry point ──────────────────────────────────────────────────────────

def dispatch(body, reply_fn, context="text"):
    body = (body or "").strip()
    if not body:
        return

    cmd = body.lower().strip()
    log(f"[dispatcher] [{context}] {body[:100]}")

    if cmd == "ping":
        reply_fn("pong — mini is alive")
        return

    if cmd == "status":
        reply_fn(cmd_status())
        return

    if cmd in ("help", "commands"):
        reply_fn("commands: ping, status, pull <model>, model <claude|gemma|fast|local>. One-off: prefix any message with 'use claude', 'use gemma', 'use fast'.")
        return

    m = re.match(r"model\s*\??\s*$", cmd)
    if m:
        current = get_persistent_model()
        reply_fn(f"Active model: {MODEL_NAMES.get(current, current)}")
        return

    m = re.match(r"model\s+(claude|gemma|fast|local|default)", cmd)
    if m:
        label = m.group(1)
        if label in ("local", "default"):
            label = "default"
        set_persistent_model(label)
        reply_fn(f"Switched to {MODEL_NAMES.get(label, label)}. Sticks until you change it.")
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

    reply_fn(run_model(body, context))
