#!/usr/bin/env python3
"""
Weekly GTD review nudge — runs Friday at 4pm.
Counts open items across all coaches + backlog, texts Rod a summary with GitHub links.
"""

import subprocess
import re
from pathlib import Path
from datetime import date

WORK = Path.home() / "Work"
NOTIFY = WORK / "local/scripts/notify.sh"
BOTTLEMSG = Path.home() / "Library/CloudStorage/Dropbox/bottleMsg"


def send(msg: str):
    subprocess.run([str(NOTIFY), msg], check=False)


def count_backlog_items():
    backlog = WORK / "test/backlog.md"
    if not backlog.exists():
        return {}
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    current_p = None
    for line in backlog.read_text().splitlines():
        for p in counts:
            if f"## {p}" in line:
                current_p = p
        if current_p and line.strip().startswith("|") and "~~" not in line:
            parts = [x.strip() for x in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0] and parts[0] not in ("Item", "---", ""):
                counts[current_p] += 1
    return counts


def count_bottlemsg():
    if not BOTTLEMSG.exists():
        return 0
    return sum(
        1 for f in BOTTLEMSG.iterdir()
        if not f.name.startswith(".") and f.name != "archive" and f.name != "mini-control-guide.md"
        and not f.name.endswith(".kdbx")
    )


def count_proposals():
    proposals = WORK / "test/proposals"
    if not proposals.exists():
        return 0
    return sum(1 for f in proposals.glob("*.md"))


def count_hh_pipeline():
    pipeline = WORK / "coaches/elite-hh-bot/office/pipeline.md"
    if not pipeline.exists():
        return 0
    count = 0
    in_table = False
    for line in pipeline.read_text().splitlines():
        if "| #" in line and "Role" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0].isdigit():
                count += 1
        elif in_table and not line.startswith("|"):
            break
    return count


def main():
    today = date.today()
    date_str = today.strftime("%A, %b %-d")

    backlog = count_backlog_items()
    inbox = count_bottlemsg()
    proposals = count_proposals()
    hh = count_hh_pipeline()

    lines = [f"Mad Max — Weekly Review ({date_str})\n"]

    # Backlog summary
    p0 = backlog.get("P0", 0)
    p1 = backlog.get("P1", 0)
    lines.append(f"Backlog: {p0} P0  {p1} P1  {backlog.get('P2',0)} P2  {backlog.get('P3',0)} P3")
    if p0 + p1 > 0:
        lines.append(f"  → {p0+p1} items need attention")

    # bottleMsg
    if inbox > 0:
        lines.append(f"bottleMsg: {inbox} unprocessed item(s)")
    else:
        lines.append("bottleMsg: clean")

    # Proposals
    if proposals > 0:
        lines.append(f"Proposals open: {proposals}")

    # HH pipeline
    lines.append(f"HH pipeline: {hh} active role(s)")

    # GitHub links
    lines.append("\nLinks:")
    lines.append("  Backlog: https://github.com/MadMaxMini/test/blob/main/backlog.md")
    lines.append("  HH pipeline: https://github.com/Roderick-Clemente/elite-hh-bot/blob/main/office/pipeline.md")

    lines.append("\nOpen /mad-max for the full review.")

    send("\n".join(lines))


if __name__ == "__main__":
    main()
