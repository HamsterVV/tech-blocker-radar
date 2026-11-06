#!/usr/bin/env python3
"""Validate the published skill before pushing."""

import pathlib
import re
import sys

SKILL_DIR = pathlib.Path("skills/tech-blocker-radar")
SKILL = SKILL_DIR / "SKILL.md"


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

for path in SKILL_DIR.rglob("*"):
    if path.suffix not in {".md", ".py"}:
        continue
    content = path.read_text(encoding="utf-8")
    if re.search(r"[\u4e00-\u9fff]", content):
        fail(f"{path} contains CJK characters; this skill is English-only")
    if "Case Study" in content:
        fail(f"{path} contains a case study; keep the skill concise")

print("SKILL.md validation passed")