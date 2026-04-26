#!/usr/bin/env python3
"""
Shared frontmatter parser for task_registry and intake_router.

Handles parsing and formatting of YAML-like frontmatter in .md files.
"""

from __future__ import annotations

import re
from typing import Any


def parse_value(raw: str) -> object:
    """Parse a frontmatter value (handles lists, strings, etc.)."""
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",")]
    return value.strip("\"'")


def format_value(value: object) -> str:
    """Format a value back to frontmatter representation."""
    if isinstance(value, list):
        return "[" + ", ".join(str(item) for item in value) + "]"
    return str(value)


def split_front_matter(text: str) -> tuple[dict[str, object], str]:
    """
    Split text into frontmatter metadata and body.

    Returns (meta_dict, body_text).
    If no valid frontmatter found, returns ({}, original_text).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()

    meta: dict[str, object] = {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        meta[key.strip()] = parse_value(raw)

    if end is None:
        return {}, text.strip()

    return meta, "\n".join(lines[end + 1:]).strip()


def format_front_matter(meta: dict[str, object], body: str = "") -> str:
    """Format metadata and body back into a complete .md file."""
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {format_value(value)}")
    lines.append("---")
    lines.append("")
    if body:
        lines.append(body.rstrip())
    lines.append("")
    return "\n".join(lines)
