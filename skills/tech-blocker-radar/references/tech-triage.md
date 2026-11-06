# Technical Blocker Search Playbook

Quick start: `python scripts/tech_scan.py "<symptom>" --max 8`. Use `--repos` for reference implementations and `--code` for source search (requires `GITHUB_TOKEN` or `gh auth login`).

## 1. Problem Fingerprint

Turn "it's broken" into a searchable fingerprint. Ask at most two questions; otherwise make a reasonable assumption and state it.

```text
Symptom: exact error / wrong behavior / performance metric / screenshot or recording
Environment: OS version, runtime, framework, version, GPU, packaging
Repro: minimal steps, frequency, trigger conditions
Tried: what was attempted and what happened
Constraints: current stack required? no native modules? license or deadline?
Solved: no error / interaction works / FPS / memory / startup time
```

If you do not have a full error, capture at least: **platform + framework + version + action + expected behavior**.

## 2. Query Construction

Search by symptom, not by product name. Use this formula:

```text
<framework or library> + <platform> + <API/flag/symbol> + <symptom>
```

- Quote the exact error: `"Failed to create window"`, `"WS_EX_LAYERED"`
- Use API, flag, or symbol names: `setIgnoreCursorEvents`, `WS_EX_TRANSPARENT`, `alwaysOnTop`, `focusable`
- Rotate synonyms: not working, fails, crash, freeze, flicker, ghost, click through, always on top, transparent, high CPU, memory leak, white screen, blurry, DPI, multi-monitor, tray, autostart, code signing
- Add versions: `tauri 2`, `electron 30`, `windows 11`, `webview2`
- Use GitHub qualifiers: `repo:owner/repo`, `is:issue`, `is:pr`, `state:open`, `comments:>3`, `created:>2025-01-01`

If two rounds do not hit, move to a broader term (platform + capability) or search the API name in official docs.

## 3. GitHub Issues and PRs

Works without authentication, about 10 requests per minute. Prefer merged PRs and issues with reproduction steps.

```bash
curl -sG "https://api.github.com/search/issues" \
  --data-urlencode "q=transparent window click through tauri" \
  --data-urlencode "per_page=10"
```

Scope by repository and type:

```text
q=mini floating widget repo:Splode/pomotroid is:issue
q=click through repo:tauri-apps/tauri is:pr
q=WS_EX_LAYERED is:pr comments:>3
```

What to look for:

- PR diff and merge state (merged, closed, draft)
- Issue reproduction steps, maintainer replies, linked PRs
- Last update time; re-verify answers older than two years
- Version tags or milestones; confirm they match the user's version

## 4. Stack Overflow

```bash
curl -sG "https://api.stackexchange.com/2.3/search/advanced" \
  --data-urlencode "order=desc" \
  --data-urlencode "sort=relevance" \
  --data-urlencode "q=tauri transparent window click through" \
  --data-urlencode "site=stackoverflow" \
  --data-urlencode "pagesize=10"
```

What to look for:

- Whether there is an accepted answer
- Answer date and version (old answers may no longer work)
- Comments saying "this no longer works on the new version"
- The minimal reproduction in the question, which can be adapted

## 5. Code Search

GitHub code search requires authentication; without it the API returns 401. Do not claim code-level search was performed when it was not.

```bash
gh auth login
gh search code "WS_EX_TRANSPARENT" --limit 20
gh search code "setIgnoreCursorEvents" --repo tauri-apps/tauri --limit 20
```

Or use the API (requires `GITHUB_TOKEN`):

```bash
curl -sG "https://api.github.com/search/code" \
  --data-urlencode "q=WS_EX_TRANSPARENT" \
  --data-urlencode "per_page=10" \
  -H "Accept: application/vnd.github.text-match+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

Without a token:

- Use WebSearch: `site:github.com "WS_EX_TRANSPARENT"`
- Find candidate repositories first, then read specific files
- Use `grep` in repositories you already cloned; do not clone many repositories just to search

## 6. Repository Search

If you know the capability but not the API, find reference implementations first:

```bash
python scripts/tech_scan.py "transparent overlay window" --repos --max 8
```

What to look for:

- Stars and recent commits: is it active?
- License: can it be used commercially?
- README and architecture: close to the user's platform and framework?
- Issues: has anyone hit the same problem?

Read code for three to five finalists only. Do not clone everything.

## 7. Official Docs and Release Notes

Beyond code and issues, check the official docs:

- Does the API exist, is it deprecated, what is the minimum version?
- Did release notes or migration guides change the default behavior?
- Are there platform limits (Windows, macOS, Linux differences)?
- Are there known issues or breaking changes?

When fetching docs, prefer the page for the user's version, not the latest page.

## 8. Solution Extraction Template

For each candidate:

```text
Source: repo / PR / issue / Stack Overflow (URL + date)
Approach: API, flag, library, or config used
Conditions: OS, framework version, dependency version
Why it works: one sentence
Cost: performance, compatibility, maintenance, license
Risk: known bugs, platform differences, unmerged or personal fork
```

"The project uses X" is not enough. Record **which version, under what conditions, and why it works**.

## 9. Verification Checklist

1. **Minimal reproduction**: under 30 lines, only the trigger.
2. **Target environment**: run on the user's actual OS and framework version, not "latest".
3. **Control test**: change one variable and confirm it caused the fix.
4. **Metrics**: functionality, FPS, memory, startup time, idle CPU.
5. **Boundaries**: multi-monitor, DPI scaling, sleep and wake, window switching, antivirus and signing.
6. **Rollback**: keep a flag or branch so a failed fix can be reverted.

## 10. Common Desktop Pet Blockers

| Blocker | Symptom keywords | Check first |
| --- | --- | --- |
| Transparent windows / click-through | transparent window, click through, hit test, WS_EX_LAYERED, WS_EX_TRANSPARENT, setIgnoreCursorEvents | Tauri window config, winit, Win32 layered windows, related PRs |
| Always on top / focus stealing | always on top, focus stealing, no activate, WS_EX_NOACTIVATE, focusable false | Window manager, Tauri and Electron config |
| Drag jitter / ghosting | drag jitter, ghosting, flicker, repaint, transparent drag | Compositor, DWM, requestAnimationFrame, double buffering |
| Multi-monitor / DPI | multi monitor, DPI scaling, per-monitor DPI, blurry | Manifest, Tauri and Electron DPI APIs |
| Animation performance | high CPU, GPU, requestAnimationFrame, canvas, WebView2 animation | Profiler, CSS vs canvas, WebView2 flags |
| Tray / taskbar | tray icon, taskbar, click disappears, hide on click | Tray library, window styles, hit testing |
| Autostart / permissions | autostart, admin, UAC, startup folder, registry | OS docs, installer |
| Packaging / signing / antivirus | code signing, SmartScreen, antivirus false positive, NSIS, MSI | Signing, reputation, installer |
| Memory / handle leaks | memory leak, handle leak, GDI object leak, long running | Profiler, resource cleanup, soak testing |
| Single instance / hotkeys | single instance, global shortcut conflict | Plugins, system APIs |

## 11. Common Misjudgments

- Treating an open PR as merged; check `merged` state and date.
- Treating an old answer as universal; verify framework and OS versions.
- Treating a closed-source product's behavior as implementation evidence; say "observed behavior", not "read the code".
- Treating "someone filed an issue" as solved; check maintainer replies and linked PRs.
- Ignoring platform differences: Windows 10 vs 11, WebView2 versions, macOS permissions, Linux compositors.
- Copying GPL or AGPL code into a closed-source product; check the LICENSE and compliance.
- Bypassing signing or antivirus instead of using legitimate signing and distribution.
- Giving an approach without verification; every technical blocker must end in a minimal repro and a target-environment test.

