#!/usr/bin/env python3
"""
Mad Max task registry.

Reads tasks/active/*.md, parses frontmatter, renders views (blockers, by-area, standup).
Mad Max flavor: area (models, services, agents, infra, skill, doc) instead of property+workstream.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frontmatter


VALID_STATUS = {"open", "blocked", "done", "dropped"}
VALID_PRIORITY = {"P0", "P1", "P2"}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
URGENCY_ORDER = {
    "time-sensitive": 0,
    "blocker": 1,
    "ops-risk": 2,
    "context-sync": 3,
    "waiting": 4,
}
FIELD_ORDER = [
    "id",
    "title",
    "owner",
    "status",
    "priority",
    "urgency",
    "area",
    "waiting_on",
    "watchers",
    "source",
    "updated",
    "completed",
    "next_action",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def today() -> str:
    return date.today().isoformat()


def title_slug(title: str) -> str:
    """Convert title to slug for task ID."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60].strip("-") or "task"


@dataclass
class Task:
    path: Path
    meta: dict[str, object]
    body: str

    @property
    def id(self) -> str:
        return str(self.meta.get("id", self.path.stem))

    @property
    def title(self) -> str:
        return str(self.meta.get("title", self.id))

    @property
    def owner(self) -> str:
        return str(self.meta.get("owner", "")).lower()

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "open")).lower()

    @property
    def priority(self) -> str:
        return str(self.meta.get("priority", "P2")).upper()

    @property
    def urgency(self) -> str:
        return str(self.meta.get("urgency", "waiting")).lower()

    @property
    def area(self) -> str:
        return str(self.meta.get("area", "general")).lower()

    @property
    def waiting_on(self) -> str:
        return str(self.meta.get("waiting_on", "")).strip()

    @property
    def watchers(self) -> list[str]:
        value = self.meta.get("watchers", [])
        if isinstance(value, list):
            return [str(v).lower() for v in value if str(v).strip()]
        if isinstance(value, str) and value:
            return [value.lower()]
        return []

    @property
    def next_action(self) -> str:
        lines = self.body.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
        return self.title

    def write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fields = [field for field in FIELD_ORDER if field in self.meta]
        fields.extend(sorted(field for field in self.meta if field not in FIELD_ORDER))

        lines = ["---"]
        for field in fields:
            lines.append(f"{field}: {frontmatter.format_value(self.meta[field])}")
        lines.append("---")
        lines.append("")
        if self.body:
            lines.append(self.body.rstrip())
        lines.append("")
        self.path.write_text("\n".join(lines))


def parse_task(path: Path) -> Task:
    """Parse a task file."""
    text = path.read_text()
    meta, body = frontmatter.split_front_matter(text)
    if not meta:
        raise ValueError(f"{path}: missing frontmatter")
    return Task(path=path, meta=meta, body=body)


def load_all_tasks(root: Path, include_done: bool = False) -> list[Task]:
    """Load all tasks."""
    active = root / "tasks" / "active"
    done = root / "tasks" / "done"
    paths = list(active.glob("*.md")) if active.exists() else []
    if include_done and done.exists():
        paths.extend(done.glob("*/*.md"))
    return [parse_task(path) for path in sorted(paths)]


def load_open_tasks(root: Path) -> list[Task]:
    """Load open and blocked tasks."""
    return [task for task in load_all_tasks(root) if task.status in {"open", "blocked"}]


def sort_key(task: Task) -> tuple[int, int, str, str]:
    """Sort key: priority, urgency, area, title."""
    return (
        PRIORITY_ORDER.get(task.priority, 99),
        URGENCY_ORDER.get(task.urgency, 99),
        task.area,
        task.title.lower(),
    )


def task_link(task: Task) -> str:
    """Markdown link to task file."""
    return f"[{task.id}](../active/{task.path.name})"


def render_task_line(task: Task, show_priority: bool = True) -> str:
    """Render a single task as a line."""
    parts = []
    if show_priority:
        parts.append(f"[{task.priority}]")
    parts.append(f"**{task.title}**")
    if task.urgency and task.urgency != "waiting":
        parts.append(f"({task.urgency})")
    if task.next_action:
        parts.append(f"- {task.next_action}")
    parts.append(task_link(task))
    return " ".join(parts)


def render_blockers_view(tasks: list[Task]) -> str:
    """Render P0 + P1 blockers only."""
    blockers = [t for t in tasks if t.priority in {"P0", "P1"}]
    blockers.sort(key=sort_key)

    lines = [
        "# Blockers",
        "",
        "_Generated from `tasks/active/`. Do not edit directly._",
        "",
    ]
    if not blockers:
        lines.append("No blockers.")
    else:
        for task in blockers:
            lines.append(f"- {render_task_line(task)}")
    lines.append("")
    return "\n".join(lines)


def render_by_area_view(tasks: list[Task]) -> str:
    """Render tasks grouped by area."""
    groups: dict[str, list[Task]] = {}
    for task in tasks:
        area = task.area
        if area not in groups:
            groups[area] = []
        groups[area].append(task)

    lines = [
        "# Tasks by Area",
        "",
        "_Generated from `tasks/active/`. Do not edit directly._",
        "",
    ]
    for area in sorted(groups.keys()):
        area_tasks = sorted(groups[area], key=sort_key)
        lines.append(f"## {area.title()}")
        lines.append("")
        for task in area_tasks:
            lines.append(f"- {render_task_line(task)}")
        lines.append("")

    return "\n".join(lines)


def render_standup_view(tasks: list[Task]) -> str:
    """Render standup view: all open tasks grouped by priority then area."""
    lines = [
        "# Standup View",
        "",
        "_Generated from `tasks/active/`. Do not edit directly._",
        "",
    ]
    for priority in ["P0", "P1", "P2"]:
        group = [t for t in tasks if t.priority == priority]
        if not group:
            continue
        lines.append(f"## {priority}")
        lines.append("")
        group.sort(key=sort_key)
        for task in group:
            lines.append(f"- **{task.area.title()}:** {task.title}")
            if task.next_action:
                lines.append(f"  - Next: {task.next_action}")
            if task.waiting_on:
                lines.append(f"  - Waiting: {task.waiting_on}")
            lines.append(f"  - {task_link(task)}")
        lines.append("")

    return "\n".join(lines)


def render_all_views(root: Path) -> None:
    """Render all views to tasks/views/."""
    tasks = load_open_tasks(root)
    views_dir = root / "tasks" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)

    (views_dir / "blockers.md").write_text(render_blockers_view(tasks))
    (views_dir / "by-area.md").write_text(render_by_area_view(tasks))
    (views_dir / "standup.md").write_text(render_standup_view(tasks))


def main():
    parser = argparse.ArgumentParser(description="Mad Max task registry")
    parser.add_argument("command", nargs="?", default="render", help="render, list, or show")
    parser.add_argument("task_id", nargs="?", help="Task ID (for show)")
    args = parser.parse_args()

    root = repo_root()

    if args.command == "render":
        render_all_views(root)
        print("Views rendered.")
    elif args.command == "list":
        tasks = load_open_tasks(root)
        for task in sorted(tasks, key=sort_key):
            print(f"{task.id} [{task.priority}] {task.title} ({task.area})")
    elif args.command == "show" and args.task_id:
        for task in load_all_tasks(root, include_done=True):
            if task.id == args.task_id or task.path.stem == args.task_id:
                print(task.path.read_text())
                return
        print(f"Task not found: {args.task_id}", file=sys.stderr)
        sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
