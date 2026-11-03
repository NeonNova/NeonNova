"""Static profile art: header, section labels, lookbook, kit, footer.

    python3 scripts/build_assets.py   # writes assets/*-{dark,light}.svg
"""
import re
from html import escape
from pathlib import Path

from theme import THEMES, svg

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

SPEC = [("FOCUS", "RL POST-TRAINING DATA"), ("PREV", "BLACKROCK"),
        ("SIDE", "MACOS TOOLS"), ("STATUS", "BUILDING")]

TICKER = ("IF AI LABS ARE THE JET ENGINES, DATA IS THE OIL  ●  RL POST-TRAINING DATA  ●  "
          "AGENTIC ENVIRONMENTS  ●  PAPERMD — NATIVE MACOS  ●  L'ARDOISE — 52 WEEKS  ●  "
          "FOOD · FASHION · FILM · FOOTBALL  ●  ")

PROJECTS = [
    ("paperMD", "SWIFT", "2026", "a native macOS markdown editor.", "swiftui + nstextview. no electron.", "NeonNova/paperMD"),
    ("l'ardoise", "NEXT.JS · MDX", "2026", "a 52-week cooking school for two.", "one meal, every weekend.", "NeonNova/lardoise"),
    ("typify", "TYPESCRIPT", "2025", "a typing test you play to music.", "type to the beat.", "NeonNova/typify"),
    ("the rice", "SHELL · ZSH", "2026", "one palette, the whole desktop.", "a single command re-themes every app.", None),
]

KIT = [("claude", "CLAUDE", "MODEL + CODE"), ("t3", "T3 CODE", "AGENT COCKPIT"),
       ("ghostty", "GHOSTTY", "TERMINAL"), ("wispr", "WISPR FLOW", "VOICE")]


def header(t):
    w, h = 880, 290
    spec = ""
    for n, (k, v) in enumerate(SPEC):
        y = 104 + n * 22
        cur = f'<tspan class="c" fill="{t["accent"]}"> █</tspan>' if k == "STATUS" else ""
        spec += (f'<text x="640" y="{y}" class="ms" fill="{t["mute"]}">{k}</text>'
                 f'<text x="832" y="{y}" text-anchor="end" class="ms" fill="{t["ink"]}">{escape(v)}{cur}</text>')
    # ticker: the string twice in one run, slid by half its own width so it loops seamlessly
    tick = escape(TICKER * 2)
    ticker = (f'<style>.t{{transform-box:fill-box;animation:tk 55s linear infinite}}'
              f'@keyframes tk{{to{{transform:translateX(-50%)}}}}</style>'
              f'<clipPath id="cp"><rect x="48" y="230" width="784" height="30"/></clipPath>'
              f'<g clip-path="url(#cp)"><text x="48" y="249" class="m t" fill="{t["mute"]}">{tick}</text></g>')
    body = f'''
<text x="48" y="44" class="m" fill="{t["mute"]}">NEONNOVA / ARCHIVE</text>
<text x="440" y="44" text-anchor="middle" class="m" fill="{t["mute"]}">SPEC SHEET — 2026</text>
<text x="832" y="44" text-anchor="end" class="m" fill="{t["mute"]}">N° 26/11</text>
<line x1="48" y1="60" x2="832" y2="60" stroke="{t["rule"]}"/>
<text x="44" y="160" class="s" fill="{t["ink"]}">aditya washikar</text>
<text x="48" y="196" class="i" fill="{t["mute"]}">mostly post-training data.</text>
<line x1="620" y1="88" x2="620" y2="176" stroke="{t["rule"]}"/>
{spec}
<line x1="48" y1="226" x2="832" y2="226" stroke="{t["rule"]}"/>
{ticker}
<line x1="48" y1="264" x2="832" y2="264" stroke="{t["rule"]}"/>'''
    return svg(w, h, body)


def label(t, num, name, note=""):
    body = (f'<text x="0" y="22" class="m" fill="{t["ink"]}">§ {num} — {name}</text>'
            f'<text x="880" y="22" text-anchor="end" class="m" fill="{t["mute"]}">{escape(note)}</text>'
            f'<line x1="0" y1="34" x2="880" y2="34" stroke="{t["rule"]}"/>')
    return svg(880, 40, body)


def card(t, n, p):
    name, lang, year, d1, d2, repo = p
    w, h = 430, 210
    return f'''
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{t["rule"]}"/>
<text x="24" y="34" class="ms" fill="{t["accent"]}">LOOK {n:02d}</text>
<text x="{w - 24}" y="34" text-anchor="end" class="ms" fill="{t["mute"]}">{escape(lang)} · {year}</text>
<text x="22" y="98" class="s3" fill="{t["ink"]}">{escape(name)}</text>
<text x="24" y="128" class="i2" fill="{t["mute"]}">{escape(d1)}</text>
<text x="24" y="148" class="i2" fill="{t["mute"]}">{escape(d2)}</text>
<line x1="24" y1="170" x2="{w - 24}" y2="170" stroke="{t["rule"]}"/>
<text x="24" y="190" class="ms" fill="{t["mute"]}">{escape(f"GITHUB.COM/{repo}".upper()) if repo else "PRIVATE — DOTFILES"}</text>
<text x="{w - 24}" y="190" text-anchor="end" class="ms" fill="{t["accent"]}">{"→" if repo else "○"}</text>'''


def lookbook(t):
    cw, ch, gap = 430, 210, 20
    body = ""
    for n, p in enumerate(PROJECTS):
        x, y = (n % 2) * (cw + gap), (n // 2) * (ch + gap)
        body += f'<g transform="translate({x} {y})">{card(t, n + 1, p)}</g>'
    return svg(2 * cw + gap, 2 * ch + gap, body)


def icon(t, slug, size=40):
    """Brand mark from scripts/icons/, fitted into a size x size box and tinted with the accent.

    claude + ghostty: simple-icons (CC0). t3: from t3.codes. wispr: redrawn from its app icon.
    """
    src = (ROOT / "scripts" / "icons" / f"{slug}.svg").read_text()
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', src).group(1).split())
    inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner)
    k = size / max(vw, vh)
    dx, dy = (size - vw * k) / 2 - vx * k, (size - vh * k) / 2 - vy * k
    return f'<g transform="translate({dx:.2f} {dy:.2f}) scale({k:.4f})" fill="{t["accent"]}">{inner}</g>'


def kit(t):
    body = ""
    for i, (slug, name, role) in enumerate(KIT):
        x = i * 225
        body += (f'<g transform="translate({x} 12)">{icon(t, slug)}</g>'
                 f'<text x="{x + 58}" y="30" class="m" fill="{t["ink"]}">{name}</text>'
                 f'<text x="{x + 58}" y="48" class="ms" fill="{t["mute"]}">{role}</text>')
    body += (f'<line x1="0" y1="80" x2="880" y2="80" stroke="{t["rule"]}"/>'
             f'<text x="0" y="112" class="ms" fill="{t["mute"]}">OFF-SCREEN</text>'
             f'<text x="120" y="114" class="i" fill="{t["ink"]}">food · fashion · film · football</text>')
    return svg(880, 130, body)


def footer(t):
    nums = ""
    for i in range(24):
        x = 12 + i * (856 / 23)
        if i == 10:
            nums += f'<circle cx="{x}" cy="26" r="12" fill="none" stroke="{t["accent"]}"/>'
        fill = t["accent"] if i == 10 else t["mute"]
        nums += f'<text x="{x}" y="30" text-anchor="middle" class="m" fill="{fill}">{i}</text>'
    body = (f'<line x1="0" y1="0.5" x2="880" y2="0.5" stroke="{t["rule"]}"/>'
            f'<g transform="translate(0 14)">{nums}</g>'
            f'<text x="0" y="96" class="i2" fill="{t["mute"]}">that&#8217;s it. thanks for stopping by.</text>'
            f'<text x="880" y="96" text-anchor="end" class="ms" fill="{t["mute"]}">END OF FILE</text>')
    return svg(880, 110, body)


def main():
    OUT.mkdir(exist_ok=True)
    for mode, t in THEMES.items():
        files = {
            "header": header(t),
            "label-work": label(t, "01", "SELECTED WORK", "4 LOOKS"),
            "lookbook": lookbook(t),
            "label-ledger": label(t, "02", "LEDGER", "LIVE · REFRESHED EVERY 12H"),
            "label-activity": label(t, "03", "ACTIVITY", "LAST 52 WEEKS"),
            "label-kit": label(t, "04", "KIT", "WHAT I WORK WITH"),
            "kit": kit(t),
            "footer": footer(t),
        }
        for name, s in files.items():
            (OUT / f"{name}-{mode}.svg").write_text(s)


if __name__ == "__main__":
    main()
