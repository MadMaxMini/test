#!/usr/bin/env python3
"""
auto-agent — executes an approved task from agent-queue.json.

Called by dispatcher.py when Rod replies "go N" or "go all".

What it does per task:
  1. Load task from queue by ID
  2. git worktree add /tmp/automax-<branch> <branch>  (safe — main untouched)
  3. Run: claude -p <prompt> --dangerously-skip-permissions in the worktree
  4. git add -A && git commit && git push origin <branch>
  5. Text Rod: result + branch name
  6. git worktree remove + prune
  7. Mark task done in queue

Usage:
  auto-agent.py <task_id>        — run one task
  auto-agent.py all              — run all pending tasks in sequence
"""

import json
import subprocess
import sys
import shutil
import tempfile
from datetime import datetime
from glob import glob
from pathlib import Path

HOME       = Path.home()
QUEUE_FILE = HOME / "Work/local/scripts/agent-queue.json"
NOTIFY     = HOME / "Work/local/scripts/notify.sh"
LOG_FILE   = HOME / "Work/local/scripts/auto-agent.log"
WORKTREE_BASE = Path("/tmp")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)


def notify_rod(msg):
    if NOTIFY.exists():
        subprocess.run([str(NOTIFY), msg], capture_output=True)


def find_claude_binary():
    pattern = str(HOME / ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")
    matches = sorted(glob(pattern))
    return matches[-1] if matches else None


def load_queue():
    if not QUEUE_FILE.exists():
        return None
    try:
        return json.loads(QUEUE_FILE.read_text())
    except Exception as e:
        log(f"queue load error: {e}")
        return None


def save_queue(queue):
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def mark_task(queue, task_id, status, note=""):
    for t in queue["tasks"]:
        if t["id"] == task_id:
            t["status"] = status
            if note:
                t["result"] = note
    save_queue(queue)


# ── Worktree helpers ──────────────────────────────────────────────────────────

def worktree_path(branch):
    slug = branch.replace("/", "-").replace(" ", "-")
    return WORKTREE_BASE / f"automax-{slug}"


def create_worktree(repo_path, branch):
    wt_path = worktree_path(branch)
    if wt_path.exists():
        shutil.rmtree(wt_path)

    # Create branch from main if it doesn't exist
    r = subprocess.run(
        ["git", "-C", repo_path, "ls-remote", "--heads", "origin", branch],
        capture_output=True, text=True
    )
    branch_exists = bool(r.stdout.strip())

    if branch_exists:
        subprocess.run(
            ["git", "-C", repo_path, "fetch", "origin", branch],
            capture_output=True, check=True
        )
        subprocess.run(
            ["git", "-C", repo_path, "worktree", "add", str(wt_path), branch],
            capture_output=True, check=True
        )
    else:
        subprocess.run(
            ["git", "-C", repo_path, "worktree", "add", "-b", branch, str(wt_path), "origin/main"],
            capture_output=True, check=True
        )

    return str(wt_path)


def remove_worktree(repo_path, branch):
    wt_path = worktree_path(branch)
    subprocess.run(
        ["git", "-C", repo_path, "worktree", "remove", "--force", str(wt_path)],
        capture_output=True
    )
    subprocess.run(
        ["git", "-C", repo_path, "worktree", "prune"],
        capture_output=True
    )
    if wt_path.exists():
        shutil.rmtree(wt_path, ignore_errors=True)


# ── Agent execution ────────────────────────────────────────────────────────────

def run_claude_in_worktree(worktree_path_str, prompt, task_description):
    binary = find_claude_binary()
    if not binary:
        return False, "claude binary not found"

    full_prompt = (
        f"You are working in a git worktree branch for autonomous task execution.\n"
        f"Task: {task_description}\n\n"
        f"Instructions:\n{prompt}\n\n"
        f"Rules:\n"
        f"- Make only the changes needed for this specific task\n"
        f"- Do not touch unrelated files\n"
        f"- Do not commit — the agent script handles git\n"
        f"- If you cannot complete the task safely, output: BLOCKED: <reason>"
    )

    log(f"running claude in {worktree_path_str}")
    try:
        r = subprocess.run(
            [binary, "-p", full_prompt, "--dangerously-skip-permissions"],
            capture_output=True, text=True, timeout=300,
            cwd=worktree_path_str
        )
        output = r.stdout.strip()
        if r.returncode != 0:
            return False, f"claude exited {r.returncode}: {r.stderr.strip()[:200]}"
        if output.startswith("BLOCKED:"):
            return False, output
        log(f"claude output: {output[:120]}")
        return True, output
    except subprocess.TimeoutExpired:
        return False, "claude timed out (5min limit)"
    except Exception as e:
        return False, str(e)


def commit_and_push(worktree_path_str, repo_path, branch, task_description):
    wt = worktree_path_str

    # Check if there are any changes
    r = subprocess.run(
        ["git", "-C", wt, "status", "--porcelain"],
        capture_output=True, text=True
    )
    if not r.stdout.strip():
        return False, "no changes made"

    subprocess.run(["git", "-C", wt, "add", "-A"], check=True, capture_output=True)
    msg = f"auto: {task_description[:70]}\n\nAutonomous change by AutoMax night agent.\nReview and merge if correct."
    subprocess.run(
        ["git", "-C", wt, "commit", "-m", msg],
        check=True, capture_output=True
    )
    r = subprocess.run(
        ["git", "-C", wt, "push", "origin", branch],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        # Try with -u for new branches
        r = subprocess.run(
            ["git", "-C", wt, "push", "-u", "origin", branch],
            capture_output=True, text=True
        )
    if r.returncode != 0:
        return False, f"push failed: {r.stderr.strip()[:150]}"

    return True, "committed and pushed"


def gh_pr_url(repo_path, branch):
    """Try to build a GitHub compare URL from the remote."""
    try:
        r = subprocess.run(
            ["git", "-C", repo_path, "remote", "get-url", "origin"],
            capture_output=True, text=True
        )
        remote = r.stdout.strip()
        # git@github.com:User/repo.git → https://github.com/User/repo/compare/branch
        if "github.com" in remote:
            if remote.startswith("git@"):
                path = remote.split("github.com:")[1].rstrip(".git")
            else:
                path = remote.split("github.com/")[1].rstrip(".git")
            return f"https://github.com/{path}/compare/{branch}"
    except Exception:
        pass
    return None


# ── Main task runner ──────────────────────────────────────────────────────────

def run_task(task):
    task_id   = task["id"]
    desc      = task["description"]
    repo_path = task["repo"]
    branch    = task["branch"]
    prompt    = task["prompt"]

    log(f"[task {task_id}] starting: {desc}")
    log(f"[task {task_id}] repo={repo_path} branch={branch}")

    # 1. Create worktree
    try:
        wt = create_worktree(repo_path, branch)
        log(f"[task {task_id}] worktree: {wt}")
    except Exception as e:
        msg = f"AutoMax [{task_id}] FAILED — worktree error: {e}"
        log(msg)
        notify_rod(msg)
        return False

    # 2. Run Claude
    success, claude_result = run_claude_in_worktree(wt, prompt, desc)
    if not success:
        remove_worktree(repo_path, branch)
        msg = f"AutoMax [{task_id}] BLOCKED — {claude_result}\nTask: {desc}"
        log(msg)
        notify_rod(msg)
        return False

    # 3. Commit + push
    pushed, push_result = commit_and_push(wt, repo_path, branch, desc)

    # 4. Cleanup worktree
    remove_worktree(repo_path, branch)

    if not pushed:
        msg = f"AutoMax [{task_id}] no changes — {push_result}\nTask: {desc}"
        log(msg)
        notify_rod(msg)
        return False

    # 5. Notify Rod
    pr_url = gh_pr_url(repo_path, branch)
    url_line = f"\nReview: {pr_url}" if pr_url else ""
    msg = f"AutoMax [{task_id}] done ✓\n{desc}\nBranch: {branch}{url_line}"
    log(msg)
    notify_rod(msg)
    return True


def main():
    ts = datetime.now().isoformat(timespec="seconds")
    log(f"[auto-agent] {ts} args={sys.argv[1:]}")

    if len(sys.argv) < 2:
        log("usage: auto-agent.py <task_id|all>")
        sys.exit(1)

    queue = load_queue()
    if not queue:
        log("no queue found")
        notify_rod("AutoMax: no task queue found — run night-planner manually?")
        sys.exit(1)

    arg = sys.argv[1].strip().lower()

    if arg == "all":
        pending = [t for t in queue["tasks"] if t["status"] == "pending"]
    else:
        try:
            task_id = int(arg)
            pending = [t for t in queue["tasks"] if t["id"] == task_id and t["status"] == "pending"]
        except ValueError:
            log(f"invalid task id: {arg}")
            sys.exit(1)

    if not pending:
        log("no pending tasks matching request")
        notify_rod("AutoMax: no pending tasks for that ID")
        sys.exit(0)

    for task in pending:
        queue = load_queue()  # reload in case of concurrent modification
        success = run_task(task)
        status  = "done" if success else "failed"
        mark_task(queue, task["id"], status)

    log("[auto-agent] done")


if __name__ == "__main__":
    main()
