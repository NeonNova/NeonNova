"""Live stats card, rendered from the GitHub GraphQL API.

    GITHUB_TOKEN=... python3 scripts/ledger.py <out_dir> [login]

Writes ledger-dark.svg and ledger-light.svg. Only public, non-fork repos
feed the language mix, so private work never leaks into the card.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from theme import THEMES, svg

# notebooks and markup swamp byte counts without saying much about the work
SKIP_LANGS = {"Jupyter Notebook", "HTML", "CSS", "SCSS"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if res.get("errors") or not (res.get("data") or {}).get("user"):
        sys.exit(f"ledger: GraphQL error: {res.get('errors')}")
    return res["data"]["user"]


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # today may still be empty — the streak is alive until tomorrow
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def summarise(u):
    cc = u["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    last30 = sum(d["contributionCount"] for d in days[-30:])
    prior30 = sum(d["contributionCount"] for d in days[-60:-30])
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            if e["node"]["name"] in SKIP_LANGS:
                continue
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return dict(
        total=cc["contributionCalendar"]["totalContributions"],
        commits=cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        prs=cc["totalPullRequestContributions"],
        active=sum(1 for d in days if d["contributionCount"]),
        current=current, longest=longest, last30=last30, prior30=prior30,
        repos=u["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        followers=u["followers"]["totalCount"],
        weekly=[sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks][-52:],
        langs=sorted(langs.items(), key=lambda kv: -kv[1]),
    )


def delta(now, before):
    if not before:
        return "NEW ACTIVITY" if now else "FLAT"
    pct = round((now - before) / before * 100)
    return f"{'▲' if pct >= 0 else '▼'} {abs(pct)}% VS PRIOR 30D"


def render(s, t, stamp):
    w = 880
    cols = [
        ("CONTRIBUTIONS / 365D", f"{s['total']:,}", delta(s["last30"], s["prior30"])),
        ("CURRENT STREAK", f"{s['current']}d", f"LONGEST {s['longest']}D"),
        ("COMMITS / 365D", f"{s['commits']:,}", f"ACTIVE DAYS {s['active']}"),
        ("PUBLIC REPOS", f"{s['repos']}", f"★ {s['stars']} · {s['followers']} FOLLOWERS"),
    ]
    body = (f'<text x="24" y="30" class="ms" fill="{t["mute"]}">NEONNOVA — ACTIVITY LEDGER</text>'
            f'<text x="{w - 24}" y="30" text-anchor="end" class="ms" fill="{t["mute"]}">AS OF {stamp}</text>'
            f'<line x1="24" y1="44" x2="{w - 24}" y2="44" stroke="{t["rule"]}"/>')
    cw = (w - 48) / 4
    for i, (lab, big, sub) in enumerate(cols):
        x = 24 + i * cw
        if i:
            body += f'<line x1="{x}" y1="60" x2="{x}" y2="140" stroke="{t["rule"]}"/>'
        px = x + (0 if i == 0 else 18)
        body += (f'<text x="{px}" y="72" class="ms" fill="{t["mute"]}">{lab}</text>'
                 f'<text x="{px - 2}" y="116" class="s3" fill="{t["ink"]}">{escape(big)}</text>'
                 f'<text x="{px}" y="138" class="ms" fill="{t["ink"]}">{escape(sub)}</text>')
    # weekly bars
    body += f'<line x1="24" y1="160" x2="{w - 24}" y2="160" stroke="{t["rule"]}"/>'
    body += f'<text x="24" y="182" class="ms" fill="{t["mute"]}">WEEKLY</text>'
    top = max(s["weekly"] or [0]) or 1
    bx, bw, base, bh = 104, (w - 24 - 104) / 52, 236, 54
    for i, v in enumerate(s["weekly"]):
        h = max(1, v / top * bh)
        body += f'<rect x="{bx + i * bw + 1:.1f}" y="{base - h:.1f}" width="{bw - 3:.1f}" height="{h:.1f}" fill="{t["accent"] if v else t["rule"]}"/>'
    body += f'<text x="24" y="236" class="ms" fill="{t["mute"]}">PEAK {top}</text>'
    # language mix
    body += f'<line x1="24" y1="256" x2="{w - 24}" y2="256" stroke="{t["rule"]}"/>'
    langs = s["langs"]
    total = sum(v for _, v in langs) or 1
    shown = langs[:5]
    rest = total - sum(v for _, v in shown)
    if rest:
        shown.append(("Other", rest))
    shades = [t["accent"], t["ramp"][2], t["ramp"][4], t["ramp"][1], t["mute"], t["rule"]]
    x = 24
    legend = ""
    for i, (name, v) in enumerate(shown):
        seg = (w - 48) * v / total
        body += f'<rect x="{x:.1f}" y="274" width="{seg:.1f}" height="6" fill="{shades[i]}"/>'
        x += seg
        lx = 24 + i * ((w - 48) / 6)
        legend += (f'<rect x="{lx}" y="296" width="8" height="8" fill="{shades[i]}" stroke="{t["rule"]}"/>'
                   f'<text x="{lx + 14}" y="304" class="ms" fill="{t["ink"]}">{escape(name.upper())}</text>'
                   f'<text x="{lx + 14}" y="320" class="ms" fill="{t["mute"]}">{v / total * 100:.1f}%</text>')
    body += legend
    return svg(w, 340, body)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    login = sys.argv[2] if len(sys.argv) > 2 else "NeonNova"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("ledger: GITHUB_TOKEN is not set")
    s = summarise(fetch(login, token))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out.mkdir(parents=True, exist_ok=True)
    for mode, t in THEMES.items():
        (out / f"ledger-{mode}.svg").write_text(render(s, t, stamp))
    print(f"ledger: {s['total']} contributions, streak {s['current']}d, {len(s['langs'])} languages")


if __name__ == "__main__":
    main()
