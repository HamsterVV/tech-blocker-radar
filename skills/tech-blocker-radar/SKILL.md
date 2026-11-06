---
name: tech-blocker-radar
description: Helps users find how other projects solved a technical blocker when they are stuck, seeing errors, performance or compatibility issues, or need a reference implementation. Searches GitHub issues and PRs, Stack Overflow, source code, and official docs, then gives candidate solutions with version and platform constraints. This skill should be used when the user says "I'm stuck on X", "how did others solve X", "is there a workaround for X", pastes an error, or asks how a capability is implemented.
---

# Tech Blocker Radar

This skill helps you find how other projects solved a technical blocker and turn that into a verifiable plan.

## When to Use This Skill

Use this skill when the user:

- Says "I'm stuck", "this doesn't work", "I can't implement X", "it crashes", "it's slow", or "it's not compatible"
- Pastes an error, stack trace, log, screenshot, or minimal reproduction
- Asks "has anyone hit this", "how did others solve this", or "is there a workaround"
- Asks how a capability is implemented in other projects
- Needs a reference implementation, native workaround, or platform-specific fix
- Is choosing between technical approaches and wants evidence from real code

Do not use this skill for market research, competitor pricing, or product strategy.

## What This Skill Searches

- **GitHub issues and PRs** — exact errors, API names, framework and platform symptoms
- **Stack Overflow** — accepted answers, version caveats, minimal reproductions
- **Source code** — open-source implementations of the same capability
- **Official docs and release notes** — API existence, deprecations, breaking changes
- **Reference repositories** — active projects on the same OS, framework, and runtime

## How to Help Users Solve a Blocker

### Step 1: Build a Searchable Fingerprint

Turn "it's broken" into a query. Capture:

1. Symptom: exact error, wrong behavior, performance metric, screenshot
2. Environment: OS, runtime, framework, version, GPU, packaging
3. Reproduction: minimal steps, frequency, trigger conditions
4. Tried: what the user already attempted and what happened
5. Constraints: must stay on the current stack? no native modules? license or deadline?
6. Definition of solved: no error, interaction works, FPS, memory, startup time

Ask at most two clarifying questions. If you can make a reasonable assumption, state it and proceed.

Example:

```text
Symptom: a transparent always-on-top window captures clicks meant for the app below.
Environment: Windows 11, Tauri 2, WebView2, borderless + transparent + alwaysOnTop.
Repro: click a transparent region -> the app below receives no click.
Tried: setIgnoreCursorEvents(true) fixes clicks but breaks hover.
Solved: click-through and hover work together.
```

For a capability question, replace symptom and reproduction with: target behavior, current stack, performance and platform constraints, acceptance criteria.

### Step 2: Search Three Ways

Search by symptom or capability, not by product name.

```bash
python "<skill_dir>/scripts/tech_scan.py" "<symptom or API>" --max 8
python "<skill_dir>/scripts/tech_scan.py" "<symptom>" --repo owner/repo --max 8
python "<skill_dir>/scripts/tech_scan.py" "<capability>" --repos --max 8
python "<skill_dir>/scripts/tech_scan.py" "<API or symbol>" --code --max 8
```

`--repos` finds reference implementations. `--code` requires `GITHUB_TOKEN` or `gh auth login`; without auth it skips code search and says so.

Run the three channels in parallel:

1. GitHub issues and PRs
2. Stack Overflow
3. Source code, plus official docs and release notes

Example output:

```text
PR | open | comments=6 | 2026-10-20 | fix: clear click-through flag when cursor poll thread parks | https://github.com/owner/repo/pull/124
issue | open | comments=3 | 2026-10-12 | [Bug] Transparent regions can block clicks on the app below | https://github.com/owner/repo/issues/30
```

### Step 3: Read the Evidence

For each promising result, read the actual diff, answer, or source file. Record:

- What API, flag, library, or config was used
- Which OS, framework, and version it applies to
- Why it works, in one sentence
- What it costs: performance, compatibility, maintenance, license
- Whether the PR is merged, open, or a personal fork

Do not stop at the title. A PR title is a lead; the diff is the evidence.

### Step 4: Present Options

Give two or three candidate solutions, ordered by the user's constraints:

| Approach | How it works | Evidence | Fits when | Risk |
| --- | --- | --- | --- | --- |

Recommend one and state your confidence. If the evidence is weak, say so.

### Step 5: Offer a Verification Plan

Every recommendation needs a way to prove it:

1. Minimal reproduction: under 30 lines, only the trigger
2. Target environment: the user's actual OS, framework, and version
3. Control test: change one variable and confirm the fix
4. Metrics: functionality, FPS, memory, startup time, idle CPU
5. Boundaries: multi-monitor, DPI scaling, sleep and wake, antivirus and signing
6. Rollback: a flag or branch so a failed fix can be reverted

### Step 6: Write the Technical Memo

```markdown
## Problem

Symptom / environment / minimal repro / constraints / definition of solved

## Recommendation

Recommended approach + one-line reason + confidence

## Options

| Approach | How it works | Evidence | Fits when | Risk |

## Code-Level Evidence

- Repo / PR / issue / Stack Overflow links
- Key API, flags, or code snippets
- Version and platform constraints

## Verification

1. Minimal repro
2. Target environment
3. Metrics and rollback

## Unknowns

- Unverified versions or platforms
- Closed-source behavior inferred, not read
- Information still needed from the user
```

## Common Blocker Categories

| Category | Example queries |
| --- | --- |
| Transparent windows | `transparent window`, `click through`, `hit test`, `WS_EX_LAYERED`, `setIgnoreCursorEvents` |
| Always on top | `always on top`, `focus stealing`, `WS_EX_NOACTIVATE` |
| Dragging and animation | `drag jitter`, `ghosting`, `flicker`, `repaint` |
| Multi-monitor and DPI | `multi monitor`, `DPI scaling`, `blurry` |
| Rendering performance | `high CPU`, `requestAnimationFrame`, `WebView2 animation` |
| Tray and taskbar | `tray icon`, `taskbar`, `click disappears` |
| Packaging and signing | `code signing`, `SmartScreen`, `antivirus false positive` |
| Memory and handles | `memory leak`, `handle leak`, `GDI object leak` |
| Single instance and hotkeys | `single instance`, `global shortcut conflict` |

## Tips for Effective Searches

1. **Quote the exact error.** `"Failed to create window"` is better than "window error".
2. **Search API and flag names.** `setIgnoreCursorEvents`, `WS_EX_TRANSPARENT`, `WS_EX_LAYERED`.
3. **Add the platform and version.** `tauri 2 windows 11`, `webview2`, `electron 30`.
4. **Try synonyms.** `not working`, `fails`, `crash`, `freeze`, `flicker`, `ghost`, `click through`.
5. **Use GitHub qualifiers.** `repo:owner/repo`, `is:issue`, `is:pr`, `state:open`, `comments:>3`.
6. **Read the source, not only the answer.** A merged PR or a working repo beats a blog post.

## When No Solution Is Found

If two rounds of search produce nothing useful:

1. Say clearly that no direct solution was found.
2. Report what was checked: issues, Stack Overflow, code, docs.
3. Offer the closest evidence and explain why it may not apply.
4. Propose a fallback: a broader platform-level search, a minimal experiment, or a native workaround.
5. Do not invent an API, version, or fix.

Example:

```text
I searched GitHub issues, Stack Overflow, and source code for "X" and did not find a direct fix.
The closest evidence is [link], but it targets [different version or platform].
I can help you build a minimal reproduction to isolate whether the cause is [A] or [B].
```

## Quality Rules

1. Every fact needs a URL and access date. Separate facts from inferences.
2. Do not invent APIs, versions, or fixes. Write "not found" when you cannot verify.
3. Check the version and platform. A merged PR does not prove it works on the user's version.
4. Prefer accepted answers, merged PRs, and official docs. Treat open PRs as leads.
5. Do not provide ways to bypass security controls or license restrictions. Check the license before reusing code.
6. Do not clone, install, or run candidate projects without the user's permission.
7. When a page fails to load, write "not retrieved", not "does not exist".
8. Every recommendation must be verifiable: minimal repro, target environment, metric, rollback.

## Budget and Stopping Conditions

- Run one round of GitHub issues plus Stack Overflow, then broaden or check docs.
- Stop at one verifiable primary approach plus one backup.
- Code search requires auth; if unavailable, state that code-level search was not performed.
- With `--repos`, scan three to five candidates and read only the finalists.

## Resources

Paths are relative to this skill's directory (`<skill_dir>`):

- `references/tech-triage.md` — query templates, evidence extraction, verification checklist, and a desktop-pet blocker table
- `scripts/tech_scan.py` — GitHub issues and PRs, repos, Stack Overflow, optional code search; zero dependencies