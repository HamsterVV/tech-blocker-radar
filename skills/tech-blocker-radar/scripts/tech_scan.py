#!/usr/bin/env python3
"""Scan GitHub issues/PRs, repos, Stack Overflow and optionally GitHub code for a technical blocker.

Zero dependencies. Usage:
    python scripts/tech_scan.py "transparent window click through tauri"
    python scripts/tech_scan.py "mini floating widget" --repo Splode/pomotroid
    python scripts/tech_scan.py "desktop pet" --repos
    python scripts/tech_scan.py "WS_EX_TRANSPARENT" --code
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "tech-blocker-radar-scan/1.0"
DEFAULT_TIMEOUT = 20


def get_github_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def fetch_json(url, headers=None, timeout=DEFAULT_TIMEOUT):
    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def clean(value, limit=140):
    if value is None:
        return ""
    text = " ".join(str(value).split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def print_section(title):
    print("\n== {} ==".format(title))


def scan_github_issues(query, repo, limit, token, timeout, sort="relevance"):
    print_section("GitHub issues / PRs (kind | state | comments | updated | title | url)")
    q = query
    if repo:
        q = "{} repo:{}".format(query, repo)
    params_dict = {"q": q, "per_page": limit}
    if sort != "relevance":
        params_dict["sort"] = sort
        params_dict["order"] = "desc"
    params = urllib.parse.urlencode(params_dict)
    headers = {}
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    try:
        data = fetch_json(
            "https://api.github.com/search/issues?{}".format(params),
            headers=headers,
            timeout=timeout,
        )
    except urllib.error.HTTPError as exc:
        remaining = "?"
        if exc.headers is not None:
            remaining = exc.headers.get("X-RateLimit-Remaining", "?")
        print("[error] HTTP {}; rate limit remaining={}. "
              "Set GITHUB_TOKEN or run `gh auth login`.".format(exc.code, remaining))
        return
    except Exception as exc:
        print("[error] {}".format(clean(exc, 160)))
        return

    items = data.get("items", [])
    if not items:
        print("[no results] try broader terms, remove version numbers, "
              "or search the exact error text")
        return
    for item in items:
        kind = "PR" if "pull_request" in item else "issue"
        state = item.get("state", "")
        comments = item.get("comments", 0)
        updated = (item.get("updated_at") or "")[:10]
        print("{} | {} | comments={} | {} | {} | {}".format(
            kind,
            state,
            comments,
            updated,
            clean(item.get("title"), 120),
            item.get("html_url", ""),
        ))


def scan_github_repos(query, limit, timeout):
    print_section("GitHub repos (stars | pushed | license | repo | description)")
    params = urllib.parse.urlencode({
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    })
    try:
        data = fetch_json(
            "https://api.github.com/search/repositories?{}".format(params),
            timeout=timeout,
        )
    except urllib.error.HTTPError as exc:
        remaining = "?"
        if exc.headers is not None:
            remaining = exc.headers.get("X-RateLimit-Remaining", "?")
        print("[error] HTTP {}; rate limit remaining={}.".format(exc.code, remaining))
        return
    except Exception as exc:
        print("[error] {}".format(clean(exc, 160)))
        return

    items = data.get("items", [])
    if not items:
        print("[no results] try capability keywords, not product names")
        return
    for item in items:
        license_info = item.get("license") or {}
        license_id = license_info.get("spdx_id") or license_info.get("key") or "none"
        print("{} | {} | {} | {} | {}".format(
            item.get("stargazers_count", 0),
            (item.get("pushed_at") or "")[:10],
            license_id,
            item.get("full_name", ""),
            clean(item.get("description"), 120),
        ))


def scan_stackoverflow(query, limit, timeout):
    print_section("Stack Overflow (score | answers | accepted | last activity | title | url)")
    params = urllib.parse.urlencode({
        "order": "desc",
        "sort": "relevance",
        "q": query,
        "site": "stackoverflow",
        "pagesize": limit,
    })
    try:
        data = fetch_json(
            "https://api.stackexchange.com/2.3/search/advanced?{}".format(params),
            timeout=timeout,
        )
    except Exception as exc:
        print("[error] {}".format(clean(exc, 160)))
        return

    items = data.get("items", [])
    if not items:
        print("[no results] try the exact error text or the API/flag name")
        return
    for item in items:
        accepted = "yes" if item.get("is_answered") else "no"
        try:
            last = datetime.datetime.fromtimestamp(
                item.get("last_activity_date", 0), datetime.timezone.utc
            ).strftime("%Y-%m-%d")
        except Exception:
            last = ""
        print("{} | {} | accepted={} | {} | {} | {}".format(
            item.get("score", 0),
            item.get("answer_count", 0),
            accepted,
            last,
            clean(item.get("title"), 120),
            item.get("link", ""),
        ))


def scan_github_code(query, repo, limit, token, timeout):
    print_section("GitHub code (repo | path | url)")
    if not token:
        print("[skip] code search requires GITHUB_TOKEN or `gh auth login`; "
              "use WebSearch `site:github.com \"{}\"` instead".format(query))
        return
    q = query
    if repo:
        q = "{} repo:{}".format(query, repo)
    params = urllib.parse.urlencode({"q": q, "per_page": limit})
    try:
        data = fetch_json(
            "https://api.github.com/search/code?{}".format(params),
            headers={
                "Authorization": "Bearer {}".format(token),
                "Accept": "application/vnd.github.text-match+json",
            },
            timeout=timeout,
        )
    except urllib.error.HTTPError as exc:
        print("[error] HTTP {}; code search needs a token with repo scope".format(exc.code))
        return
    except Exception as exc:
        print("[error] {}".format(clean(exc, 160)))
        return

    items = data.get("items", [])
    if not items:
        print("[no results]")
        return
    for item in items:
        repo_name = (item.get("repository") or {}).get("full_name", "")
        print("{} | {} | {}".format(
            repo_name,
            item.get("path", ""),
            item.get("html_url", ""),
        ))


def main():
    parser = argparse.ArgumentParser(
        description="Scan GitHub issues/PRs, repos, Stack Overflow and optionally GitHub code "
                    "for a technical blocker.")
    parser.add_argument("query", help="Symptom, error text, API name or flag")
    parser.add_argument("--repo", default="", help="Limit to a repo, e.g. owner/repo")
    parser.add_argument("--max", type=int, default=8, help="Results per source (default: 8)")
    parser.add_argument("--repos", action="store_true",
                        help="Also search GitHub repositories for reference implementations")
    parser.add_argument("--code", action="store_true",
                        help="Also run GitHub code search (requires auth)")
    parser.add_argument("--sort", default="relevance",
                        choices=["relevance", "comments", "created", "updated"],
                        help="GitHub issue sort (default: relevance)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="Per-request timeout in seconds")
    args = parser.parse_args()

    query = args.query.strip()
    if not query:
        parser.error("query must not be empty")
    limit = max(1, min(args.max, 30))

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    token = get_github_token()
    print("Query: {}".format(query))
    if args.repo:
        print("Repo filter: {}".format(args.repo))
    print("GitHub auth: {}".format(
        "yes" if token else "no (issues search still works; code search will be skipped)"))

    scan_github_issues(query, args.repo, limit, token, args.timeout, args.sort)
    if args.repos:
        scan_github_repos(query, limit, args.timeout)
    scan_stackoverflow(query, limit, args.timeout)
    if args.code:
        scan_github_code(query, args.repo, limit, token, args.timeout)

    print("\nTip: read the merged PR diff, then verify on your actual OS/framework version. "
          "A PR merged is not proof it works on your version.")


if __name__ == "__main__":
    main()