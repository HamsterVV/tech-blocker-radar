#!/usr/bin/env python3
"""Validate the published skill before pushing."""

import pathlib
import re
import sys

SKILL = pathlib.Path("skills/tech-blocker-radar/SKILL.md")


def fail(message: str) -> None:
    sys.exit(f"validation failed: {message}")


text = SKILL.read_text(encoding="utf-8")
if not text.startswith("---"):
    fail("SKILL.md must start with YAML frontmatter")

match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not match:
    fail("SKILL.md frontmatter is malformed")

fields = dict(re.findall(r"^([a-z_-]+):\s*(.+)$", match.group(1), re.M))
if fields.get("name") != "tech-blocker-radar":
    fail("frontmatter name must be tech-blocker-radar")
description = fields.get("description", "")
if not description:
    fail("frontmatter description is required")
if len(description) > 1024:
    fail("description must be 1024 characters or fewer")

print("SKILL.md validation passed")