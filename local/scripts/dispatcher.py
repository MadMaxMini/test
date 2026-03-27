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
- You can run terminal commands, read/edit files, check git, query databases, manage services
- Reply in plain text, 2-5 sentences max — this goes to Rod's phone

THE SETUP:
- Rod runs Dakota Enterprises LLC — real estate team: Rod, Devon (brother, dclemen87@gmail.com), Doc (father, +19739704525), Sharon (Philippines, +639451631830)
- iMessage gateway reads incoming texts from Rod, routes to you
- Email poller watches macbotpooterson@gmail.com for @dakotaentllc.com mail
- Daily standup fires 7am weekdays — currently texts Rod only (group send disabled)
- Secrets in OpenBao (http://127.0.0.1:8200), local AI via Ollama (http://127.0.0.1:11434)

KEY PATHS:
- Backlog: ~/Work/test/backlog.md
- Session log: ~/Work/test/session-log.md
- Dakota team tasks: ~/Work/dakota-software/people/*/tasks.md
- Scripts: ~/Work/test/local/scripts/
- Contacts (mini-local): ~/Work/test/local/scripts/contacts.md

RULES:
- If Rod asks you to do something → do it, report back concisely
- If you need one piece of info → ask it
- Never claim you can't access files or run commands — you can
- Don't pad replies"""


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

    reply_fn(run_model(body, context))
