"""Shared palette + type for every SVG on the profile.

Backgrounds are transparent and the neutrals are GitHub's own, so the art
sits on the page seamlessly; GitHub blue is the single accent.
"""

THEMES = {
    "dark": dict(ink="#f0f6fc", mute="#9198a1", rule="#3d444d", accent="#4493f8", page="#0d1117",
                 ramp=["#151b23", "#0c2d6b", "#1f6feb", "#4493f8", "#a5d6ff"]),
    "light": dict(ink="#1f2328", mute="#59636e", rule="#d1d9e0", accent="#0969da", page="#ffffff",
                  ramp=["#eff2f5", "#b6e3ff", "#54aeff", "#0969da", "#0a3069"]),
}

STYLE = """
.m{font:11px "SF Mono",ui-monospace,Menlo,Consolas,monospace;letter-spacing:.08em}
.ms{font:9.5px "SF Mono",ui-monospace,Menlo,Consolas,monospace;letter-spacing:.1em}
.s{font:400 60px "Cormorant Garamond","Didot","Bodoni 72",Georgia,serif;letter-spacing:-.01em}
.s3{font:400 40px "Cormorant Garamond","Didot","Bodoni 72",Georgia,serif}
.i{font:italic 400 19px "Cormorant Garamond","Didot","Bodoni 72",Georgia,serif}
.i2{font:italic 400 16px "Cormorant Garamond","Didot","Bodoni 72",Georgia,serif}
.c{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}
"""


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><style>{STYLE}</style>{body}</svg>\n')
