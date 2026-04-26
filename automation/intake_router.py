#!/usr/bin/env python3
"""
Mad Max intake router.

Scans ~/Library/CloudStorage/Dropbox/bottleMsg/ for work drops and routes them
into the task registry with fixes:
- Push failure retry + notify on failure
- Shared frontmatter parser (no duplication)
- Deterministic kind inference (prefers explicit type)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import frontmatter
import task_registry


BOTTLEMSG = Path.home() / "Library" / "CloudStorage" / "Dropbox" / "bottleMsg"
DROP_EXTS = {".md", ".txt"}
SKIP_NAMES = {"README.md", ".DS_Store", "mini-control-guide.md"}
KNOWN_PRIORITIES = {"P0", "P1", "P2"}
VALID_AREAS = {"models", "services", "agents", "infra", "skill", "doc", "general"}


@dataclass
class Drop:
    path: Path
    meta: dict[str, object]
    body: str

    @property
    def title(self) -> str:
        """Extract title from frontmatter or body."""
        explicit = str(self.meta.get("title", "")).strip()
        if explicit:
            return explicit
        for line in self.body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
            if stripped:
                return stripped[:80]
        return self.path.stem.replace("-", " ").replace("_", " ").title()

    @property
    def kind(self) -> str:
        """Infer task vs. note. Prefers explicit type."""
        explicit = str(self.meta.get("type", self.meta.get("kind", ""))).lower().strip()
        if explicit:
            return explicit
        # Heuristic: if has task metadata, treat as task
        if self.meta.get("priority") or self.meta.get("area") or self.meta.get("next_action"):
            return "task"
        return "note"

    @property
    def priority(self) -> str:
        """Extract priority, default P2."""
        raw = str(self.meta.get("priority", "")).upper().strip()
        if raw in KNOWN_PRIORITIES:
            return raw
        return "P2"

    @property
    def area(self) -> str:
        """Extract area, default general."""
        raw = str(self.meta.get("area", "")).lower().strip()
        if raw in VALID_AREAS:
            return raw
        return "general"

    @property
    def urgency(self) -> str:
        """Extract urgency, default waiting."""
        raw = str(self.meta.get("urgency", "")).lower().strip()
        valid = {"time-sensitive", "blocker", "ops-risk", "context-sync", "waiting"}
        if raw in valid:
            return raw
        return "waiting"

    @property
    def owner(self) -> str:
        """Extract owner, default rod."""
        return str(self.meta.get("owner", "rod")).lower().strip() or "rod"

    @property
    def waiting_on(self) -> str:
        """Extract waiting_on field."""
        return str(self.meta.get("waiting_on", "")).strip()

    @property
    def next_action(self) -> str:
        """Extract next_action."""
        return str(self.meta.get("next_action", "")).strip()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def iter_drops() -> list[Drop]:
    """Scan bottleMsg for unprocessed drops."""
    drops: list[Drop] = []
    if not BOTTLEMSG.exists():
        return drops

    for path in sorted(BOTTLEMSG.iterdir()):
        if not path.is_file():
            continue
        if path.name in SKIP_NAMES or path.name.startswith("."):
            continue
        if path.suffix.lower() not in DROP_EXTS:
            continue
        meta, body = frontmatter.split_front_matter(path.read_text())
        drops.append(Drop(path=path, meta=meta, body=body))

    return drops


def parse_drop_description(drop: Drop) -> str:
    """One-line description of a drop for logging."""
    return f"{drop.kind.upper()}: {drop.title}"


def create_task(root: Path, drop: Drop) -> str:
    """Create a canonical task from a drop."""
    # Generate unique task ID
    base = f"T-{today()}-{task_registry.title_slug(drop.title)}"
    existing = {t.id for t in task_registry.load_all_tasks(root, include_done=True)}
    task_id = base
    i = 2
    while task_id in existing:
        task_id = f"{base}-{i}"
        i += 1

    # Create task
    meta = {
        "id": task_id,
        "title": drop.title,
        "owner": drop.owner,
        "status": "open",
        "priority": drop.priority,
        "urgency": drop.urgency,
        "area": drop.area,
        "waiting_on": drop.waiting_on,
        "watchers": [],
        "source": f"intake: bottleMsg/{drop.path.name}",
        "updated": today(),
    }
    if drop.next_action:
        meta["next_action"] = drop.next_action

    task_path = root / "tasks" / "active" / f"{task_id}.md"
    task = task_registry.Task(path=task_path, meta=meta, body=drop.body)
    task.write()

    return task_id


def append_intake_note(root: Path, drop: Drop, task_id: str | None = None) -> None:
    """Append drop to inbox/notes.md."""
    notes_path = root / "inbox" / "notes.md"
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    if not notes_path.exists():
        notes_path.write_text("# Intake Notes\n")

    header = f"## {today()} - {drop.title}"
    meta_line = f"_Kind: {drop.kind}; priority: {drop.priority}; area: {drop.area}. Routed {timestamp()}._"
    if task_id:
        meta_line += f" Task: `{task_id}`."

    with notes_path.open("a") as f:
        f.write("\n\n")
        f.write(header)
        f.write("\n")
        f.write(meta_line)
        f.write("\n\n")
        f.write(drop.body if drop.body else "(no content)")
        f.write("\n")


def archive_drop(drop: Drop) -> Path:
    """Move processed drop to bottleMsg/archive/."""
    archive = BOTTLEMSG / "archive" / today()
    archive.mkdir(parents=True, exist_ok=True)
    target = archive / drop.path.name
    if target.exists():
        stem, suffix = target.stem, target.suffix
        i = 2
        while (archive / f"{stem}-{i}{suffix}").exists():
            i += 1
        target = archive / f"{stem}-{i}{suffix}"
    shutil.move(str(drop.path), str(target))
    return target


def git_pull_rebase(root: Path) -> bool:
    """Pull with rebase. Return True if successful."""
    try:
        subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=30,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def git_push(root: Path) -> bool:
    """Push to origin. Return True if successful."""
    try:
        subprocess.run(
            ["git", "push"],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=30,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def notify_failure(message: str) -> None:
    """Send alert via notify.sh if available."""
    notify_sh = Path.home() / "Work" / "local" / "scripts" / "notify.sh"
    if notify_sh.exists():
        try:
            subprocess.run(
                [str(notify_sh), message],
                timeout=5,
                capture_output=True,
            )
        except Exception:
            pass  # Best effort


def process_drops(root: Path, dry_run: bool = False, pull_first: bool = False, push_after: bool = False) -> None:
    """Process all drops."""
    drops = iter_drops()
    if not drops:
        print("No drops found.")
        return

    log_lines = []

    try:
        if pull_first:
            print("Pulling latest...")
            if not git_pull_rebase(root):
                print("Warning: pull --rebase failed. Continuing anyway.", file=sys.stderr)
                log_lines.append("WARN: pull --rebase failed")

        for drop in drops:
            print(f"Processing: {parse_drop_description(drop)}")

            if drop.kind == "task":
                task_id = create_task(root, drop)
                append_intake_note(root, drop, task_id)
                log_lines.append(f"Created task {task_id}: {drop.title}")
            else:
                append_intake_note(root, drop, None)
                log_lines.append(f"Appended note: {drop.title}")

            if not dry_run:
                archive_drop(drop)

        # Re-render views
        print("Rendering views...")
        task_registry.render_all_views(root)

        if not dry_run and push_after:
            print("Committing...")
            subprocess.run(
                ["git", "add", "-A"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Intake: {len(drops)} drop(s) processed"],
                cwd=root,
                check=True,
                capture_output=True,
            )

            print("Pushing...")
            if not git_push(root):
                print("Push failed. Retrying with pull --rebase...", file=sys.stderr)
                if git_pull_rebase(root) and git_push(root):
                    print("Retry succeeded.")
                    log_lines.append("RETRY: push succeeded after pull --rebase")
                else:
                    msg = f"Intake router: push failed after retry ({len(drops)} drops committed locally)"
                    print(f"ERROR: {msg}", file=sys.stderr)
                    notify_failure(msg)
                    log_lines.append(f"ERROR: {msg}")
                    sys.exit(1)

    finally:
        if log_lines:
            append_intake_log(root, log_lines)


def append_intake_log(root: Path, lines: list[str]) -> None:
    """Append to bot/intake-log.md."""
    if not lines:
        return
    log_path = root / "automation" / "logs" / "intake-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if not log_path.exists():
        log_path.write_text("# Intake Log\n")

    with log_path.open("a") as f:
        f.write(f"\n## {timestamp()}\n")
        for line in lines:
            f.write(f"- {line}\n")


def main():
    parser = argparse.ArgumentParser(description="Mad Max intake router")
    parser.add_argument("command", nargs="?", default="scan", help="scan, process")
    parser.add_argument("--dry-run", action="store_true", help="Process without archiving or pushing")
    parser.add_argument("--pull", action="store_true", help="Pull before processing")
    parser.add_argument("--push", action="store_true", help="Push after processing")
    args = parser.parse_args()

    root = repo_root()

    if args.command == "scan":
        drops = iter_drops()
        if not drops:
            print("No drops found.")
        else:
            for drop in drops:
                print(f"  {parse_drop_description(drop)}")

    elif args.command == "process":
        process_drops(root, dry_run=args.dry_run, pull_first=args.pull, push_after=args.push)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
