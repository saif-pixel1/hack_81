#!/usr/bin/env python3
"""
Regenerates images/light_mode.svg and images/dark_mode.svg from the
.svg.tpl templates, filling in:
  - live stats pulled from the GitHub API (repos, stars, forks,
    followers, commits, PRs, issues, top repo, languages, uptime,
    last-12-months contributions/reviews)
  - manually-edited fields from profile-config.yml (role, major,
    learning, location, email, twitter)

Run locally:  GITHUB_TOKEN=ghp_xxx python3 scripts/generate_card.py
In CI, GITHUB_TOKEN is provided automatically by GitHub Actions.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

try:
    import yaml  # PyYAML
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(REPO_ROOT, "profile-config.yml")
IMAGES_DIR = os.path.join(REPO_ROOT, "images")

TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


def api_get(path, params=None):
    url = f"{API}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def api_get_all_pages(path, params=None):
    items = []
    page = 1
    params = dict(params or {})
    while True:
        params["page"] = page
        params.setdefault("per_page", 100)
        batch = api_get(path, params)
        if not batch:
            break
        items.extend(batch)
        if len(batch) < params["per_page"]:
            break
        page += 1
        if page > 20:  # safety cap
            break
    return items


def graphql_query(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(GRAPHQL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def human_uptime(created_at_iso):
    created = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    days_total = (now - created).days
    years, rem_days = divmod(days_total, 365)
    months, days = divmod(rem_days, 30)
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    parts.append(f"{days} day{'s' if days != 1 else ''}")
    return ", ".join(parts)


def fetch_stats(username):
    user = api_get(f"/users/{username}")
    repos = api_get_all_pages(f"/users/{username}/repos", {"type": "owner"})
    repos = [r for r in repos if not r.get("fork")]

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    top_repo = max(repos, key=lambda r: r.get("stargazers_count", 0), default=None)
    top_repo_str = (
        f"{top_repo['name']} ({top_repo['stargazers_count']} \u2605)"
        if top_repo else "n/a"
    )

    # Aggregate languages across repos by byte count
    lang_bytes = {}
    for r in repos[:30]:  # cap to keep runtime reasonable
        try:
            langs = api_get(f"/repos/{username}/{r['name']}/languages")
        except Exception:
            continue
        for lang, count in langs.items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + count
    total_bytes = sum(lang_bytes.values()) or 1
    top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:2]
    languages_str = ", ".join(
        f"{lang} {round(100 * count / total_bytes)}%" for lang, count in top_langs
    ) or "n/a"

    prs = api_get(f"/search/issues", {"q": f"is:pr+author:{username}"}).get("total_count", 0)
    issues = api_get(f"/search/issues", {"q": f"is:issue+author:{username}"}).get("total_count", 0)
    commits = api_get(f"/search/commits", {"q": f"author:{username}"}).get("total_count", 0)

    contributions = 0
    reviews = 0
    if TOKEN:
        q = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
            }
          }
        }"""
        try:
            data = graphql_query(q, {"login": username})
            cc = data["data"]["user"]["contributionsCollection"]
            contributions = (
                cc["totalCommitContributions"]
                + cc["totalIssueContributions"]
                + cc["totalPullRequestContributions"]
                + cc["totalPullRequestReviewContributions"]
            )
            reviews = cc["totalPullRequestReviewContributions"]
        except Exception as e:
            print(f"warning: GraphQL contributions fetch failed: {e}", file=sys.stderr)

    return {
        "UPTIME": human_uptime(user["created_at"]),
        "LANGUAGES": languages_str,
        "GITHUB_URL": f"github.com/{username}",
        "REPOS": str(user.get("public_repos", len(repos))),
        "STARS": str(total_stars),
        "FORKS": str(total_forks),
        "FOLLOWERS": str(user.get("followers", 0)),
        "COMMITS": str(commits),
        "CONTRIBUTED": "0",
        "PRS": str(prs),
        "ISSUES": str(issues),
        "TOP_REPO": top_repo_str,
        "CONTRIBUTIONS": str(contributions),
        "REVIEWS": str(reviews),
    }


def render(template_path, output_path, values):
    with open(template_path) as f:
        content = f.read()
    for key, val in values.items():
        content = content.replace("{{" + key + "}}", str(val))
    leftover = re.findall(r"\{\{(\w+)\}\}", content)
    if leftover:
        print(f"warning: unresolved placeholders in {output_path}: {leftover}", file=sys.stderr)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"wrote {output_path}")


def main():
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    username = config["username"]
    values = fetch_stats(username)
    values["USERNAME"] = username
    values["ROLE"] = config.get("role", "")
    values["MAJOR"] = config.get("major", "")
    values["LEARNING"] = config.get("learning", "")
    values["LOCATION"] = config.get("location", "")
    values["EMAIL"] = config.get("email", "")
    values["TWITTER"] = config.get("twitter", "")

    render(os.path.join(IMAGES_DIR, "light_mode.svg.tpl"),
           os.path.join(IMAGES_DIR, "light_mode.svg"), values)
    render(os.path.join(IMAGES_DIR, "dark_mode.svg.tpl"),
           os.path.join(IMAGES_DIR, "dark_mode.svg"), values)


if __name__ == "__main__":
    main()
