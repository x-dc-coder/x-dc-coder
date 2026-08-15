#!/usr/bin/env python3
"""Refresh the dynamic "最近更新" section of the profile README.

Reads the user's public repos via gh api, renders the top 5 by recent
activity, and swaps them into the section between the START/END markers.
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone

README = "README.md"
START, END = "<!--START_SECTION:repos-->", "<!--END_SECTION:repos-->"


def gh_api(*args):
    return subprocess.check_output(["gh", "api", *args], text=True)


def main() -> None:
    data = json.loads(
        gh_api(
            "users/x-dc-coder/repos?per_page=100&sort=updated&direction=desc",
            "--jq", "[.[] | {name, description, language, html_url, updated_at}]",
        )
    )
    # Only public repos are returned without repo scope; skip helper repos.
    repos = [r for r in data if not r["name"].endswith(".github")][:5]

    lines = []
    for r in repos:
        desc = (r["description"] or "").strip()
        lang = r["language"] or ""
        when = datetime.fromisoformat(
            r["updated_at"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d")
        if desc:
            lines.append(f"- [{r['name']}]({r['html_url']}) — {desc} · {lang} · {when}")
        else:
            lines.append(f"- [{r['name']}]({r['html_url']}) · {lang} · {when}")

    section = "\n".join(lines)

    with open(README, encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        rf"{START}.*?{END}",
        f"{START}\n{section}\n{END}",
        content,
        flags=re.S,
    )
    if new_content == content:
        print("No changes")
        return

    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README updated")


if __name__ == "__main__":
    main()
