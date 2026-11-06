# Tech Blocker Radar

**Find how other projects solved the same technical blocker — with evidence, not guesses.**

[![License: MIT](https://img.shields.io/github/license/HamsterVV/tech-blocker-radar)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/HamsterVV/tech-blocker-radar)](https://github.com/HamsterVV/tech-blocker-radar/stargazers)
[![Validate](https://github.com/HamsterVV/tech-blocker-radar/actions/workflows/validate.yml/badge.svg)](https://github.com/HamsterVV/tech-blocker-radar/actions/workflows/validate.yml)
[![Agent Skill](https://img.shields.io/badge/agent--skill-SKILL.md-blue)](https://agentskills.io)
[![skills.sh](https://img.shields.io/badge/skills.sh-listed-blue)](https://skills.sh/hamstervv/tech-blocker-radar)

Tech Blocker Radar is an agent skill for the moment you are stuck: a platform bug, a version-specific API, a rendering artifact, a packaging failure. It turns the symptom into a searchable fingerprint, searches GitHub issues and PRs, Stack Overflow, source code, and official docs, then returns candidate approaches with version and platform constraints and a verification plan.

## Install for Claude Code

### Option A: npx skills (recommended)

Requires Node.js 22.20+.

```bash
npx skills add HamsterVV/tech-blocker-radar --skill tech-blocker-radar -a claude-code -g -y
```

### Option B: manual

```bash
git clone https://github.com/HamsterVV/tech-blocker-radar.git
mkdir -p ~/.claude/skills
cp -r tech-blocker-radar/skills/tech-blocker-radar ~/.claude/skills/
```

Restart Claude Code if the skill does not appear in its skills list.

For other SKILL.md-compatible agents, use the same `npx skills add` command without `-a claude-code`, or copy the skill into that agent's skills directory.

## Why

Most coding agents answer from memory. That is fast, but memory produces plausible fixes that do not match your OS, framework version, or exact symptom. This skill forces evidence:

- Search by symptom, not by product name.
- Read the actual PR diff, issue thread, or accepted answer.
- Separate facts from inferences.
- End with a minimal reproduction and a target-environment verification plan.

## Requirements

- Python 3.9+ for `scripts/tech_scan.py`.
- Optional: `gh auth login` or `GITHUB_TOKEN` for GitHub code search. Without it, issue/PR and Stack Overflow search still work, and the skill states that code search was skipped.

## Usage

Ask in natural language:

- "My Tauri 2 transparent window captures clicks meant for the app below. How did others solve it?"
- "My sprite edges are noisy after green-screen keying and downscaling to 120px."
- "WebView2 shows white bars during resize on Windows 11."
- "How do desktop pets implement click-through and dragging in the same window?"

The skill produces a technical memo:

```text
## Problem
Symptom / environment / minimal repro / constraints / definition of solved

## Recommendation
Recommended approach + one-line reason + confidence

## Options
| Approach | How it works | Evidence | Fits when | Risk |

## Code-Level Evidence
Repo / PR / issue / Stack Overflow links, key APIs, version constraints

## Verification
1. Minimal repro
2. Target environment
3. Metrics and rollback

## Unknowns
Unverified versions, inferred behavior, missing information
```

## What it does

1. Builds a searchable problem fingerprint.
2. Searches GitHub issues and PRs, Stack Overflow, source code, and docs.
3. Reads the actual diff, answer, or source file.
4. Presents two or three approaches with evidence and costs.
5. Gives a minimal verification plan and rollback.
6. Writes a compact technical memo.

## What it does not do

- It does not debug your code, run your app, or replace logs and a minimal reproduction.
- It does not search market size, competitors, pricing, or product strategy.
- It does not invent APIs, versions, or fixes. When evidence is missing, it says so.

## Repository layout

```text
skills/tech-blocker-radar/
├── SKILL.md
├── references/tech-triage.md
└── scripts/tech_scan.py
```

`tools/validate_skill.py` checks the `SKILL.md` frontmatter.

## Contributing

Open an issue with a real blocker, the environment, and what you already tried. PRs should keep `SKILL.md` concise and focused on the search workflow.

## License

MIT