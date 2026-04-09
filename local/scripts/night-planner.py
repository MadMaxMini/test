#!/usr/bin/env python3
"""
night-planner — autonomous task picker. Runs at 10pm nightly.

What it does:
  1. Read backlog.md P0/P1 items + dakota-software tasks
  2. Filter to automatable tasks (code changes, doc updates, config fixes)
  3. Pick top 1-2 tasks using local model
  4. Write agent-queue.json with pending tasks + prompts
  5. Text Rod for approval: "go 1", "go all", "skip 1", "stop"
  6. If no response by midnight → auto-expire queue

Approval is handled by dispatcher.py when Rod replies via iMessage.
auto-agent.py executes the actual work when approved.
"""

import json
import subprocess
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from glob import glob

HOME         = Path.home()
WORK         = HOME / "Work"
QUEUE_FILE   = HOME / "Work/local/scripts/agent-queue.json"
NOTIFY       = HOME / "Work/local/scripts/notify.sh"
LOG_FILE     = HOME / "Work/local/scripts/night-planner.log"
BACKLOG      = WORK / "test/backlog.md"
DAKOTA_TASKS = WORK / "dakota-software/people"

OLLAMA_URL   = "http://127.0.0.1:11434/api/generate"
MODEL        = "mistral-small:latest"
MODEL_FAST   = "llama3.2:3b"

REPOS = {
    "test":             str(WORK / "test"),
    "dakota-software":  str(WORK / "dakota-software"),
    "coaches/faith":    str(WORK / "coaches/faith"),
    "coaches/job":      str(WORK / "coaches/job"),
    "coaches/health":   str(WORK / "coaches/health"),
}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)


# ── Task collection ────────────────────────────────────────────────────────────

def read_backlog_p0_p1():
    if not BACKLOG.exists():
        return []
    lines = BACKLOG.read_text().splitlines()
    tasks = []
    in_p0_p1 = False
    for line in lines:
        if line.startswith("## P0") or line.startswith("## P1"):
            in_p0_p1 = True
        elif line.startswith("## P2"):
            break
        if in_p0_p1 and line.strip().startswith("-"):
            tasks.append(("test", line.strip()))
    return tasks


def read_dakota_tasks():
    tasks = []
    for tasks_file in sorted(DAKOTA_TASKS.glob("*/tasks.md")):
        person = tasks_file.parent.name
        lines = tasks_file.read_text().splitlines()
        for line in lines:
            if line.strip().startswith("- [ ]"):
                tasks.append((f"dakota-software/{person}", line.strip()))
    return tasks[:20]  # cap — don't flood the picker


def collect_all_tasks():
    backlog = read_backlog_p0_p1()
    dakota  = read_dakota_tasks()
    return backlog[:10] + dakota[:10]


# ── AI picker ─────────────────────────────────────────────────────────────────

PICKER_SYSTEM = """You are an automation triage bot. Given a list of tasks, pick the 1-2 best candidates for FULLY AUTONOMOUS execution by a coding agent tonight.

Automatable = the agent can make a concrete, testable change with no human input needed:
- Bug fixes with clear root cause
- Adding missing config or documentation
- Script improvements (error handling, logging, dedup)
- Updating stale content in markdown files
- Refactoring a specific function

NOT automatable:
- Tasks needing Rod's decision or approval
- Tasks requiring external access (APIs, credentials not on machine)
- Vague tasks ("improve X", "think about Y")
- Anything touching production systems without a clear, reversible change

For each picked task, output:
TASK: <short description>
REPO: <repo name from the list>
BRANCH: auto/<slug-3-5-words>
PROMPT: <single paragraph Claude coding prompt — specific, complete, self-contained>
REASON: <one sentence why this is safe to automate>

If nothing is safely automatable, output: NONE"""


def call_ollama(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 600, "temperature": 0.3}
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
        log(f"ollama error ({model}): {e}")
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
            [binary, "-p", prompt, "--dangerously-skip-permissions"],
            capture_output=True, text=True, timeout=90
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception as e:
        log(f"claude error: {e}")
    return None


def pick_tasks(all_tasks):
    if not all_tasks:
        return []

    task_list = "\n".join(
        f"[{i+1}] ({repo}) {task}"
        for i, (repo, task) in enumerate(all_tasks)
    )
    repos_list = ", ".join(REPOS.keys())

    prompt = (
        f"{PICKER_SYSTEM}\n\n"
        f"Available repos: {repos_list}\n\n"
        f"TASKS:\n{task_list}\n\n"
        f"Pick up to 2 automatable tasks:"
    )

    raw = call_ollama(MODEL, prompt) or call_ollama(MODEL_FAST, prompt) or call_claude(prompt)
    if not raw:
        log("picker: no model responded")
        return []
    if "NONE" in raw.upper():
        log("picker: nothing automatable tonight")
        return []

    return parse_picker_output(raw)


def parse_picker_output(raw):
    tasks = []
    blocks = raw.strip().split("\n\n")
    for block in blocks:
        lines = {
            k.strip(): v.strip()
            for line in block.splitlines()
            if ": " in line
            for k, v in [line.split(": ", 1)]
        }
        if "TASK" in lines and "REPO" in lines and "PROMPT" in lines:
            repo_name = lines["REPO"].strip()
            repo_path = REPOS.get(repo_name, str(WORK / repo_name))
            tasks.append({
                "description": lines["TASK"],
                "repo":        repo_path,
                "repo_name":   repo_name,
                "branch":      lines.get("BRANCH", f"auto/task-{len(tasks)+1}"),
                "prompt":      lines["PROMPT"],
                "reason":      lines.get("REASON", ""),
                "status":      "pending",
            })
        if len(tasks) >= 2:
            break
    return tasks


# ── Queue management ──────────────────────────────────────────────────────────

def write_queue(tasks):
    now     = datetime.now()
    expires = (now.replace(hour=0, minute=0, second=0) + timedelta(days=1)).isoformat()
    queue   = {
        "date":    now.strftime("%Y-%m-%d"),
        "created": now.isoformat(timespec="seconds"),
        "expires": expires,
        "tasks":   [{"id": i+1, **t} for i, t in enumerate(tasks)],
    }
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))
    log(f"queue written: {len(tasks)} task(s)")
    return queue


def notify_rod(tasks):
    if not NOTIFY.exists():
        log("notify.sh not found")
        return
    lines = ["AutoMax tonight:"]
    for t in tasks:
        lines.append(f"  [{t['id']}] {t['description']} ({t['repo_name']})")
    lines.append("")
    lines.append("Reply: go 1 / go all / skip 1 / stop")
    msg = "\n".join(lines)
    r = subprocess.run([str(NOTIFY), msg], capture_output=True, text=True)
    if r.returncode == 0:
        log("✓ texted Rod")
    else:
        log(f"✗ notify failed: {r.stderr.strip()[:80]}")


def queue_is_active():
    """True if a non-expired queue exists with pending tasks."""
    if not QUEUE_FILE.exists():
        return False
    try:
        q = json.loads(QUEUE_FILE.read_text())
        if datetime.fromisoformat(q["expires"]) < datetime.now():
            return False
        return any(t["status"] == "pending" for t in q.get("tasks", []))
    except Exception:
        return False


def expire_old_queue():
    if not QUEUE_FILE.exists():
        return
    try:
        q = json.loads(QUEUE_FILE.read_text())
        if datetime.fromisoformat(q["expires"]) < datetime.now():
            for t in q["tasks"]:
                if t["status"] == "pending":
                    t["status"] = "expired"
            QUEUE_FILE.write_text(json.dumps(q, indent=2))
            log("expired old queue")
    except Exception:
        pass


def main():
    ts = datetime.now().isoformat(timespec="seconds")
    log(f"[night-planner] {ts}")

    expire_old_queue()

    if queue_is_active():
        log("queue already active — skipping tonight")
        return

    tasks = collect_all_tasks()
    log(f"collected {len(tasks)} candidate task(s)")

    picked = pick_tasks(tasks)
    if not picked:
        log("nothing to queue tonight")
        return

    queue = write_queue(picked)
    notify_rod(queue["tasks"])
    log("[night-planner] done")


if __name__ == "__main__":
    main()
