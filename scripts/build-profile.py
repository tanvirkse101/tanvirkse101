#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools==4.55.3"]
# ///
"""Build the retro-arcade artwork for the GitHub profile README.

    uv run scripts/build-profile.py

No network needed (fonts are vendored in scripts/fonts/), deterministic
output: running it twice produces byte-identical files. Never hand-edit the
SVGs in assets/; change the COPY / data below and rebuild.

Visual system
-------------
* One pixel grid. Shapes snap to whole pixels.
* Pixel fonts (SIL OFL, see scripts/fonts/OFL-*.txt), embedded per SVG as a
  WOFF subset of just the characters that SVG uses, so GitHub renders them
  identically everywhere:
    - Press Start 2P  -> arcade display labels (sizes on its 8px grid)
    - VT323           -> readable small text
    - DotGothic16     -> Japanese
  The build fails if a glyph is missing or a measured line overflows its box.
* Palette: midnight navy, electric-blue maze lines, arcade yellow, brick red,
  mint, cyan, cream.
* Influences, blended into one world: maze corridors + a small yellow
  chomper (route), brick platforms + pipes + coins (stages), interlocking
  falling blocks (toolbox). All artwork is original.
* Motion: a few slow loops, each on its own asset. Every SVG's un-animated
  state is the complete picture, and `prefers-reduced-motion: reduce` turns
  all animation off.

All essential information also lives as selectable text in README.md and
README-ja.md; the images are scenery plus a quick visual summary.
"""
import re
from base64 import b64encode
from html import escape, unescape
from io import BytesIO
from math import atan2, degrees, hypot
from pathlib import Path

from fontTools import subset as ftsubset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'

# --------------------------------------------------------------------------
# Palette
NAVY = '#0b1026'      # background
NAVY2 = '#131c42'     # panels
NAVY3 = '#1a2456'     # panel shading
BLUE = '#2f6bff'      # maze lines
BLUE_L = '#7fa4ff'
BLUE_D = '#1d3a9e'
YELLOW = '#ffcc33'
YELLOW_L = '#ffe58a'
YELLOW_D = '#c98d12'
RED = '#c8402f'       # brick
RED_L = '#e4694f'
RED_D = '#8e2a20'
MINT = '#5fe0a8'
MINT_L = '#a8f2d0'
MINT_D = '#2c9e6e'
CYAN = '#3fd0e6'
CYAN_L = '#9beaf5'
CYAN_D = '#1d93a8'
CREAM = '#f6ecd2'
MUTED = '#a9b0cf'
DOT_BLUE = '#4a78ff'  # used on transparent strips: readable on white and on #0d1117

FONT_DIR = ROOT / 'scripts' / 'fonts'
DISPLAY = "'Arcade Display',ui-monospace,monospace"
BODY = "'Arcade Body',ui-monospace,Menlo,monospace"
JA = "'Arcade JA','Hiragino Sans','Noto Sans JP',sans-serif"
FACES = {  # family stack -> (css name, file, weight range)
    DISPLAY: ('Arcade Display', 'PressStart2P-Regular.ttf', '400'),
    BODY: ('Arcade Body', 'VT323-Regular.ttf', '400'),
    JA: ('Arcade JA', 'DotGothic16-Regular.ttf', '400'),
}
_FONTS = {}


def _font(fam):
    if fam not in _FONTS:
        _FONTS[fam] = TTFont(FONT_DIR / FACES[fam][1], recalcTimestamp=False)
    return _FONTS[fam]


def measure(s, size, fam=BODY, weight=400):
    """Advance width of s in px."""
    t = _font(fam)
    cmap, hmtx, upm = t.getBestCmap(), t['hmtx'], t['head'].unitsPerEm
    missing = [ch for ch in s if ord(ch) not in cmap]
    if missing:
        raise ValueError(f'{FACES[fam][0]} has no glyph for {missing!r} in {s!r}')
    w = sum(hmtx[cmap[ord(ch)]][0] for ch in s) * size / upm
    return w


def font_css(body):
    """@font-face rules with WOFF subsets of exactly the glyphs this SVG uses."""
    css = []
    for fam, (name, file, weights) in FACES.items():
        key = re.escape(escape(fam, quote=True))
        chars = set()
        for m in re.finditer(r'<text[^>]*font-family="' + key + r'"[^>]*>(.*?)</text>', body):
            chars |= set(unescape(m.group(1)))
        if not chars:
            continue
        font = TTFont(FONT_DIR / file, recalcTimestamp=False)
        opts = ftsubset.Options()
        opts.flavor = 'woff'
        opts.notdef_outline = True
        opts.layout_features = []  # no ligatures/alternates: what you type is what renders
        sub = ftsubset.Subsetter(opts)
        sub.populate(text=''.join(sorted(chars)))
        sub.subset(font)
        buf = BytesIO()
        font.flavor = 'woff'
        font.save(buf)
        data = b64encode(buf.getvalue()).decode()
        css.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{data}) format('woff');"
                   f"font-weight:{weights}}}")
    return ''.join(css)

REDUCED = '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'


def f(v):
    """Compact number formatting for SVG attributes."""
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def pwidth(s, scale):
    """Width of display text drawn with ptext(..., scale)."""
    return round(measure(s, 8 * scale, DISPLAY))


def cells_path(cells, u, ox=0.0, oy=0.0):
    """Merge grid cells into horizontal runs -> compact path data."""
    rows = {}
    for c, r in cells:
        rows.setdefault(r, []).append(c)
    d = []
    for r in sorted(rows):
        cs = sorted(set(rows[r]))
        start = prev = cs[0]
        for c in cs[1:] + [None]:
            if c is not None and c == prev + 1:
                prev = c
                continue
            d.append(f'M{f(ox + start * u)} {f(oy + r * u)}h{f((prev - start + 1) * u)}v{f(u)}h{f(-(prev - start + 1) * u)}z')
            if c is not None:
                start = prev = c
    return ''.join(d)


def text(x, y, s, size=16, fill=CREAM, weight=400, font=BODY, anchor='start', maxw=None):
    weight = 400  # every embedded face ships one weight; never synthesize bold
    if maxw is not None and measure(s, size, font, weight) > maxw:
        raise ValueError(f'text overflows {maxw}px: {s!r} @ {size}px')
    measure(s, size, font, weight)  # glyph coverage check
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{escape(font, quote=True)}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')


def ptext(x, y, s, scale=3, fill=CREAM, shadow=None, anchor='start'):
    """Arcade display text on the 8px grid. (x, y) is the top of the capitals."""
    size, base = 8 * scale, y + 7 * scale
    out = text(x, base + scale, s, size, shadow, 400, DISPLAY, anchor) if shadow else ''
    return out + text(x, base, s, size, fill, 400, DISPLAY, anchor)


def ptext_c(cx, y, s, scale=3, fill=CREAM, shadow=None):
    return ptext(cx, y, s, scale, fill, shadow, 'middle')


def sprite(rows, colors, x, y, u):
    """Multi-colour pixel sprite from strings; '.' is transparent."""
    by = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != '.':
                by.setdefault(ch, []).append((c, r))
    return ''.join(f'<path fill="{colors[k]}" d="{cells_path(v, u, x, y)}"/>' for k, v in sorted(by.items()))


def notched(w, h, fill=NAVY, edge=BLUE_D):
    """Pixel-cornered screen background with a 2px inner frame."""
    d = (f'M8 0H{w-8}V4H{w-4}V8H{w}V{h-8}H{w-4}V{h-4}H{w-8}V{h}H8V{h-4}H4V{h-8}H0V8H4V4H8Z')
    e = (f'M10 6H{w-10}V8H{w-8}V10H{w-6}V{h-10}H{w-8}V{h-8}H{w-10}V{h-6}H10V{h-8}H8V{h-10}H6V10H8V8H10Z')
    return f'<path fill="{fill}" d="{d}"/><path fill="none" stroke="{edge}" stroke-width="2" d="{e}"/>'


def rounded(points, r, closed=True):
    """Polyline/polygon with rounded corners (quadratic joins) - maze walls."""
    n = len(points)
    d = []
    rng = range(n) if closed else range(1, n - 1)
    if not closed:
        d.append(f'M{f(points[0][0])} {f(points[0][1])}')
    for i in rng:
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        l1 = hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
        l2 = hypot(p2[0] - p1[0], p2[1] - p1[1]) or 1
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] - (p1[0] - p0[0]) / l1 * rr, p1[1] - (p1[1] - p0[1]) / l1 * rr)
        b = (p1[0] + (p2[0] - p1[0]) / l2 * rr, p1[1] + (p2[1] - p1[1]) / l2 * rr)
        d.append(f'{"M" if (closed and i == 0) else "L"}{f(a[0])} {f(a[1])}Q{f(p1[0])} {f(p1[1])} {f(b[0])} {f(b[1])}')
    if closed:
        d.append('Z')
    else:
        d.append(f'L{f(points[-1][0])} {f(points[-1][1])}')
    return ''.join(d)


def maze_wall(d, fill='none'):
    """Classic double-line wall: a wide blue stroke with a thin dark core."""
    return (f'<path d="{d}" fill="{fill}" stroke="{BLUE}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{NAVY}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')


def bricks(x, y, w, h, row=12, brick=24):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{RED}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="2" fill="{RED_L}"/>']
    d = []
    for i, yy in enumerate(range(y + row, y + h, row)):
        d.append(f'M{x} {yy}h{w}v2h-{w}z')
    for i, yy in enumerate(range(y, y + h, row)):
        off = 0 if i % 2 == 0 else brick // 2
        for xx in range(x + off + brick, x + w, brick):
            d.append(f'M{xx} {yy + 2}h2v{min(row, y + h - yy) - 2}h-2z')
    out.append(f'<path fill="{RED_D}" d="{"".join(d)}"/>')
    return ''.join(out)


BLOCK = {
    'Y': (YELLOW, YELLOW_L, YELLOW_D),
    'R': (RED, RED_L, RED_D),
    'M': (MINT, MINT_L, MINT_D),
    'C': (CYAN, CYAN_L, CYAN_D),
    'B': (BLUE, BLUE_L, BLUE_D),
}


def block_cells(cells, u, ox, oy, key, bevel=None):
    """Bevelled falling-block cells: base, light top/left, dark bottom/right."""
    base, light, dark = BLOCK[key]
    bv = bevel or max(2, u // 9)
    base_d = cells_path(cells, u, ox, oy)
    hl, sh = [], []
    for c, r in cells:
        x, y = ox + c * u, oy + r * u
        hl.append(f'M{f(x)} {f(y)}h{f(u)}v{bv}h{f(-u + bv)}v{f(u - bv)}h{-bv}z')
        sh.append(f'M{f(x + u)} {f(y + u)}h{f(-u)}v{-bv}h{f(u - bv)}v{f(-u + bv)}h{bv}z')
    return (f'<path fill="{base}" d="{base_d}"/><path fill="{light}" d="{"".join(hl)}"/>'
            f'<path fill="{dark}" d="{"".join(sh)}"/>')


def stack(rows, u, ox, oy):
    """Small decorative block stack from strings of colour keys."""
    by = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != '.':
                by.setdefault(ch, []).append((c, r))
    return ''.join(block_cells(v, u, ox, oy, k) for k, v in sorted(by.items()))


# --------------------------------------------------------------------------
# Sprites
COIN = ['.YYYY.', 'YLYYYY', 'YLYDYY', 'YYYDYY', 'YYYDYY', 'YYYDYY', 'YYYYDY', '.YYYY.']
COIN_C = {'Y': YELLOW, 'L': YELLOW_L, 'D': YELLOW_D}
CLOUD = ['.....CCC........', '...CCCCCC..CC...', '..CCCCCCCCCCCC..', '.CCCCCCCCCCCCCC.',
         'CCCCCCCCCCCCCCCC', '.SSSSSSSSSSSSSS.']
CLOUD_C = {'C': CREAM, 'S': MUTED}
PIN = ['.RRRR.', 'RRWWRR', 'RWWWWR', 'RRWWRR', '.RRRR.', '..RR..', '..RR..', '...R..']
PIN_C = {'R': RED_L, 'W': CREAM}
PAD = ['.BBBBBBBBB.', 'BBWBBBBBRBB', 'BWWWBBBMBRB', 'BBWBBBBBMBB', 'BBBBB.BBBBB', '.BBB...BBB.']
PAD_C = {'B': BLUE_L, 'W': CREAM, 'R': RED_L, 'M': MINT}
STAR = ['...Y...', '...Y...', 'YYYYYYY', '.YYYYY.', '..YYY..', '.YY.YY.', 'YY...YY']
STAR_C = {'Y': YELLOW}
TPIECE = ['CCC', '.C.']


def chomper(u, color=YELLOW, eye=NAVY):
    """Original 13x13 round chomper centred on (0, 0), facing right.

    Two frames: mouth open (animated class `mo`) drawn over mouth closed.
    """
    n, c = 13, 6
    body_open, body_closed = [], []
    for j in range(n):
        for i in range(n):
            dx, dy = i - c, j - c
            if dx * dx + dy * dy > 6.4 ** 2:
                continue
            if (dx, dy) == (0, -3):
                continue
            if not (dx > 0 and abs(dy) <= dx * 0.85):
                body_open.append((i, j))
            if not (dx > 2 and dy == 0):
                body_closed.append((i, j))
    o = -n * u / 2
    eye_d = cells_path([(c, c - 3)], u, o, o)
    return (f'<path fill="{color}" d="{cells_path(body_closed, u, o, o)}"/>'
            f'<g class="mo"><path fill="{NAVY}" d="{cells_path([(i, j) for (i, j) in body_closed if (i, j) not in set(body_open)], u, o, o)}"/></g>'
            f'<path fill="{eye}" d="{eye_d}"/>')


CHOMP_CSS = ('.mo{animation:mo .5s steps(1,end) infinite}'
             '@keyframes mo{50%{opacity:0}}')


class Route:
    """Waypoint path + keyframes for a traveller that eats the dots it passes."""

    def __init__(self, name, waypoints, speed=62.0, fade=0.45, gap=1.2, hold_start=0.3):
        self.name, self.pts = name, [(x, y) for x, y, _ in waypoints]
        holds = [h for _, _, h in waypoints]
        frames = []  # (t, x, y, angle, opacity)
        t, s = 0.0, 0.0
        self.seg = []  # (s0, s1, t0, t1, p0, p1)
        ang0 = self._ang(0)
        frames.append((t, *self.pts[0], ang0, 0))
        t += fade
        frames.append((t, *self.pts[0], ang0, 1))
        t += hold_start + holds[0]
        frames.append((t, *self.pts[0], ang0, 1))
        for i in range(len(self.pts) - 1):
            p0, p1 = self.pts[i], self.pts[i + 1]
            L = hypot(p1[0] - p0[0], p1[1] - p0[1])
            a = self._ang(i)
            if frames[-1][3] != a:
                frames.append((t + 0.001, *p0, a, 1))
            t1 = t + L / speed
            self.seg.append((s, s + L, t, t1, p0, p1))
            frames.append((t1, *p1, a, 1))
            s += L
            t = t1
            if holds[i + 1]:
                t += holds[i + 1]
                frames.append((t, *p1, a, 1))
        self.length = s
        t += fade
        frames.append((t, *self.pts[-1], frames[-1][3], 0))
        self.fade_out_end = t
        t += gap
        frames.append((t, *self.pts[-1], frames[-1][3], 0))
        self.total = t
        self.frames = frames

    def _ang(self, i):
        p0, p1 = self.pts[i], self.pts[i + 1]
        return round(degrees(atan2(p1[1] - p0[1], p1[0] - p0[0])))

    def pct(self, t):
        return f(100 * t / self.total)

    def time_at(self, s):
        for s0, s1, t0, t1, _, _ in self.seg:
            if s0 <= s <= s1:
                return t0 + (t1 - t0) * (s - s0) / (s1 - s0)
        return self.seg[-1][3]

    def point_at(self, s):
        for s0, s1, _, _, p0, p1 in self.seg:
            if s0 <= s <= s1:
                k = (s - s0) / (s1 - s0)
                return p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k
        return self.pts[-1]

    def css(self):
        kf = ''.join(f'{self.pct(t)}%{{transform:translate({f(x)}px,{f(y)}px) rotate({a}deg);opacity:{o}}}'
                     for t, x, y, a, o in self.frames)
        return (f'.{self.name}{{animation:{self.name} {f(self.total)}s linear infinite}}'
                f'@keyframes {self.name}{{{kf}}}')

    def dots(self, step=20, first=22, until=None, size=4, color=CREAM, eat=True):
        """Dots along the path; each disappears when the traveller reaches it."""
        out, css = [], []
        s = first
        end = self.length if until is None else until
        i = 0
        while s <= end + 0.01:
            x, y = self.point_at(s)
            cls = ''
            if eat:
                p = 100 * self.time_at(s) / self.total
                back = 100 * self.fade_out_end / self.total
                cls = f' class="{self.name}d{i}"'
                css.append(f'.{self.name}d{i}{{animation:{self.name}d{i} {f(self.total)}s linear infinite}}'
                           f'@keyframes {self.name}d{i}{{0%,{f(p)}%{{opacity:1}}{f(p + .1)}%,{f(back)}%{{opacity:0}}'
                           f'{f(min(back + 4, 100))}%,100%{{opacity:1}}}}')
            h = size / 2
            out.append(f'<rect{cls} x="{f(round(x - h))}" y="{f(round(y - h))}" width="{size}" height="{size}" fill="{color}"/>')
            s += step
            i += 1
        return ''.join(out), ''.join(css)

    def traveller(self, u):
        x, y = self.pts[0]
        # The transform attribute is the static frame; the CSS animation overrides it.
        return f'<g class="{self.name}" transform="translate({f(x)} {f(y)})">{chomper(u)}</g>'


def write(name, w, h, title, desc, body, css=''):
    fonts = font_css(body)
    style = f'<style>{fonts}{css}{REDUCED if css else ""}</style>' if (css or fonts) else ''
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
           f'{style}<g shape-rendering="crispEdges">{body}</g></svg>\n')
    (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    return name


# --------------------------------------------------------------------------
# Copy. Keep facts in sync with README.md, README-ja.md and tanvirahamed.dev.
COPY = {
    'en': {
        'font': BODY,
        'hero_title': 'TANVIR AHAMED — Software engineer · Tsukuba, Japan',
        'hero_desc': ('Pixel title screen. A small yellow chomper follows a dotted maze route that flows into a '
                      'landscape of brick platforms, a green pipe, coins and stacked blocks. '
                      'Tagline: Building things. Exploring worlds. Saving progress.'),
        'subtitle': 'Software engineer · Tsukuba, Japan',
        'heads': {
            'player': ('1-1 PLAYER', ''),
            'stage': ('1-2 CURRENT STAGE', ''),
            'toolbox': ('1-3 TOOLBOX', ''),
            'route': ('1-4 WORLD ROUTE', ''),
            'after': ('1-5 AFTER HOURS', ''),
            'bonus': ('1-6 BONUS STAGE', ''),
        },
        'stage_title': 'Current stage: day job at AIZOTH and a Japanese-learning side project',
        'stage_desc': ('Two signposts on brick platforms joined by a dotted route with a bobbing coin. '
                       'Left: Day job, AI applications at AIZOTH, Python, FastAPI, Flutter, Google Cloud. '
                       'Right: Side project, Japanese-learning app, vocabulary, kanji and spaced repetition, in development.'),
        'job': ['AI applications at AIZOTH', 'Python · FastAPI · Flutter · Google Cloud'],
        'side': ['Japanese-learning app', 'Vocabulary · kanji · spaced repetition'],
        'tag': ('IN DEVELOPMENT', 'pixel'),
        'route_title': 'World route: Dhaka, Miyazaki, Tsukuba',
        'route_desc': ('Three stops on a dotted maze corridor: Dhaka in Bangladesh (flag), Miyazaki in Kyushu (palm tree '
                       'and sun) and Tsukuba (twin-peaked mountain). A small chomper travels from stop to stop.'),
        'stops': ['Bangladesh', 'Kyushu, Japan', 'Ibaraki · today'],
        'shelf_title': 'After hours: Dota 2, Assassin’s Creed and a shelf of favorites',
        'shelf_desc': ('Arcade game-select screen. Two large featured cartridges: Dota 2 (selected, pixel three-lane map) '
                       'and Assassin’s Creed (pixel rooftops and a bird). Below, six smaller slots: Attack on Titan and '
                       'Dragon Ball Z (anime), The Office and Breaking Bad (series), Interstellar (film), Avicii (music).'),
        'feat_sub': ['multiplayer · strategy', 'action · adventure'],
        'feat_ja': ['', ''],
        'shelf': [('Attack on Titan', 'anime'), ('Dragon Ball Z', 'anime'), ('The Office', 'series'),
                  ('Breaking Bad', 'series'), ('Interstellar', 'film'), ('Avicii', 'music')],
        'select': 'P1 SELECT',
        'cont_title': 'Continue? Say hello',
        'cont_desc': ('Pixel continue screen with a slowly fading cursor next to SAY HELLO. '
                      'Talk about games, recommendations or building things.'),
        'cont_opt': ('SAY HELLO', 'pixel'),
        'cont_sub': 'games · recommendations · building things',
    },
    'ja': {
        'font': JA,
        'hero_title': 'TANVIR AHAMED（タンヴィル・アハメド）— ソフトウェアエンジニア · 茨城県つくば市',
        'hero_desc': ('ピクセルのタイトル画面。小さな黄色いキャラクターが迷路の点線ルートをたどり、ルートはレンガの足場、'
                      '緑の土管、コイン、積み上がったブロックの風景へとつながります。キャッチコピー：つくる。めぐる。セーブする。'),
        'subtitle': 'ソフトウェアエンジニア · 茨城県つくば市',
        'heads': {
            'player': ('1-1 PLAYER', 'プレイヤー'),
            'stage': ('1-2 CURRENT STAGE', 'いまのステージ'),
            'toolbox': ('1-3 TOOLBOX', '道具箱'),
            'route': ('1-4 WORLD ROUTE', 'ルート'),
            'after': ('1-5 AFTER HOURS', 'オフの時間'),
            'bonus': ('1-6 BONUS STAGE', 'ボーナス'),
        },
        'stage_title': 'いまのステージ：AIZOTHでの仕事と、個人開発の日本語学習アプリ',
        'stage_desc': ('点線のルートと浮かぶコインでつながった、レンガの足場の上の二つの看板。'
                       '左：本業、AIZOTHでAIアプリケーション開発、Python・FastAPI・Flutter・Google Cloud。'
                       '右：個人開発、日本語学習アプリ、語彙・漢字・間隔反復、開発中。'),
        'job': ['AIZOTHでAIアプリケーション開発', 'Python · FastAPI · Flutter · Google Cloud'],
        'side': ['日本語学習アプリ', '語彙 · 漢字 · 間隔反復'],
        'tag': ('開発中', 'ja'),
        'route_title': 'ルート：ダッカ、宮崎、つくば',
        'route_desc': ('迷路の通路でつながった三つの地点：バングラデシュのダッカ（国旗）、九州の宮崎（ヤシの木と太陽）、'
                       'つくば（二つの峰の山）。小さなキャラクターが地点から地点へ移動します。'),
        'stops': ['バングラデシュ', '九州 · 宮崎', '茨城 · いま'],
        'shelf_title': 'オフの時間：Dota 2、アサシン クリード、そして好きな作品の棚',
        'shelf_desc': ('アーケードのゲーム選択画面。大きなカートリッジが二つ：Dota 2（選択中、三本のレーンの地図）と'
                       'アサシン クリード（屋根の街並みと鳥）。下に小さな枠が六つ：進撃の巨人、ドラゴンボールZ（アニメ）、'
                       'ジ・オフィス、ブレイキング・バッド（ドラマ）、インターステラー（映画）、Avicii（音楽）。'),
        'feat_sub': ['マルチプレイ · 戦略', 'アクション · アドベンチャー'],
        'feat_ja': ['', 'アサシン クリード'],
        'shelf': [('進撃の巨人', 'アニメ'), ('ドラゴンボールZ', 'アニメ'), ('ジ・オフィス', 'ドラマ'),
                  ('ブレイキング・バッド', 'ドラマ'), ('インターステラー', '映画'), ('Avicii', '音楽')],
        'select': 'P1 SELECT',
        'cont_title': 'コンティニュー？ 気軽に声をかけてください',
        'cont_desc': 'ピクセルのコンティニュー画面。「はなしかける」の横でカーソルがゆっくり点滅します。ゲーム、おすすめ、ものづくりの話をどうぞ。',
        'cont_opt': ('はなしかける', 'ja'),
        'cont_sub': 'ゲーム · おすすめ · ものづくり',
    },
}

W = 960
STARS = [(34, 22), (190, 18), (226, 96), (744, 20), (930, 120), (612, 132), (140, 120),
         (478, 146), (880, 96), (760, 140), (300, 130), (40, 92)]


# --------------------------------------------------------------------------
# 1. Title screen
def build_hero(lang, c):
    H = 300
    b = [notched(W, H)]
    b.append(''.join(f'<rect x="{x}" y="{y}" width="2" height="2" fill="{MUTED}" opacity=".55"/>' for x, y in STARS))
    b.append(sprite(CLOUD, CLOUD_C, 52, 30, 4))
    b.append(sprite(CLOUD, CLOUD_C, 838, 44, 4))
    b.append(ptext_c(W / 2, 30, 'TANVIR AHAMED', 6, CREAM, shadow=BLUE_D))
    if lang == 'ja':
        b.append(text(W / 2, 104, 'タンヴィル・アハメド  ·  ' + c['subtitle'], 16, MUTED, 400, JA, 'middle', maxw=880))
        b.append(text(W / 2, 134, 'つくる。めぐる。セーブする。', 16, YELLOW, 400, JA, 'middle'))
    else:
        b.append(text(W / 2, 106, c['subtitle'], 24, MUTED, 400, BODY, 'middle'))
        b.append(ptext_c(W / 2, 120, 'BUILDING THINGS. EXPLORING WORLDS. SAVING PROGRESS.', 2, YELLOW))

    # Maze: outer border open on the right, islands inside.
    border = rounded([(440, 175), (440, 155), (12, 155), (12, 292), (440, 292), (440, 215)], 10, closed=False)
    b.append(maze_wall(border))
    for poly in ([(36, 195), (160, 195), (160, 272), (36, 272)],
                 [(200, 175), (310, 175), (310, 220), (200, 220)],
                 [(180, 260), (420, 260), (420, 272), (180, 272)],
                 [(350, 215), (420, 215), (420, 240), (350, 240)]):
        b.append(maze_wall(rounded(poly, 8), fill=NAVY))

    # Platform world
    b.append(bricks(446, 209, 160, 16, row=8, brick=16))
    b.append(bricks(446, 272, 498, 20, row=10, brick=20))
    # pipe
    b.append(f'<rect x="700" y="238" width="44" height="34" fill="{MINT}"/><rect x="706" y="238" width="6" height="34" fill="{MINT_L}"/>'
             f'<rect x="734" y="238" width="10" height="34" fill="{MINT_D}"/>'
             f'<rect x="694" y="224" width="56" height="16" fill="{MINT}"/><rect x="698" y="226" width="6" height="12" fill="{MINT_L}"/>'
             f'<rect x="740" y="224" width="10" height="16" fill="{MINT_D}"/><rect x="694" y="238" width="56" height="2" fill="{NAVY}" opacity=".5"/>')
    for x, y in ((666, 186), (713, 172), (760, 186)):
        b.append(sprite(COIN, COIN_C, x, y, 3))
    b.append(stack(['...R....', '..RRR.C.', 'YYMM..C.', 'YMMBB.CC'], 18, 800, 200))
    b.append(sprite(['..MM..', '.MMMM.', 'MMMMMM', '..DD..', '..DD..'], {'M': MINT_D, 'D': YELLOW_D}, 620, 257, 3))

    r = Route('hc', [(40, 175, 0), (180, 175, 0), (180, 240, 0), (330, 240, 0), (330, 195, 0), (600, 195, 1.6)],
              speed=64, gap=1.4)
    dots, dcss = r.dots(step=20, first=22, until=r.length - 4)
    b.append(dots)
    b.append(r.traveller(2))
    return write('hero' + ('-ja' if lang == 'ja' else ''), W, H, c['hero_title'], c['hero_desc'], ''.join(b),
                 CHOMP_CSS + r.css() + dcss)


# --------------------------------------------------------------------------
# Section strips (transparent; readable on GitHub light and dark)
ICONS = {
    'player': lambda x, y: f'<g transform="translate({x + 13} {y + 13})">{chomper(2).replace(chr(60) + "g class=" + chr(34) + "mo" + chr(34) + ">", "<g>")}</g>',
    'stage': lambda x, y: sprite(COIN, COIN_C, x + 4, y + 1, 3),
    'toolbox': lambda x, y: stack(['YYY', '.Y.'], 9, x - 1, y + 4),
    'route': lambda x, y: sprite(PIN, PIN_C, x + 4, y + 1, 3),
    'after': lambda x, y: sprite(PAD, PAD_C, x - 4, y + 4, 3),
    'bonus': lambda x, y: sprite(STAR, STAR_C, x + 2, y + 2, 3),
}


def build_head(lang, key, label, ja):
    H = 52
    jw = round(measure(ja, 16, JA)) + 16 if ja else 0
    tile_w = 52 + pwidth(label, 3) + jw + 18
    b = [f'<path fill="{NAVY}" d="M4 6H{tile_w - 4}V10H{tile_w}V42H{tile_w - 4}V46H4V42H0V10H4Z"/>',
         f'<path fill="none" stroke="{BLUE}" stroke-width="2" d="M6 9H{tile_w - 6}V13H{tile_w - 3}V39H{tile_w - 6}V43H6V39H3V13H6Z"/>',
         ICONS[key](12, 13)]
    b.append(ptext(52, 16, label, 3, CREAM))
    if ja:
        b.append(text(52 + pwidth(label, 3) + 16, 34, ja, 16, YELLOW, 400, JA))
    d = []
    x = tile_w + 14
    while x < W - 16:
        d.append(f'M{x} 24h4v4h-4z')
        x += 16
    for y in (24, 36, 48):
        d.append(f'M{W - 12} {y}h4v4h-4z')
    b.append(f'<path fill="{DOT_BLUE}" d="{"".join(d)}"/>')
    title = label + (f' / {ja}' if ja else '')
    name = f'head-{key}' + ('-ja' if lang == 'ja' else '')
    return write(name, W, H, title, 'Section marker with a dotted route leading to the next section.', ''.join(b))


# --------------------------------------------------------------------------
# 3. Current stage
def tag(x, y, label, kind):
    if kind == 'pixel':
        w = pwidth(label, 2) + 20
        return (f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="{RED}"/><rect x="{x}" y="{y}" width="{w}" height="2" fill="{RED_L}"/>'
                f'<rect x="{x}" y="{y + 24}" width="{w}" height="2" fill="{RED_D}"/>' + ptext(x + 10, y + 6, label, 2, CREAM)), w
    w = round(measure(label, 16, JA)) + 24
    return (f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="{RED}"/><rect x="{x}" y="{y}" width="{w}" height="2" fill="{RED_L}"/>'
            f'<rect x="{x}" y="{y + 24}" width="{w}" height="2" fill="{RED_D}"/>' + text(x + 12, y + 19, label, 16, CREAM, 400, JA)), w


def signboard(x, y, w, h, title, color, lines, font):
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{NAVY2}"/>',
         maze_wall(rounded([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 10))]
    b.append(ptext(x + 24, y + 20, title, 3, color))
    b.append(text(x + 24, y + 70, lines[0], 24 if font == BODY else 16, CREAM, 700, font, maxw=w - 40))
    b.append(text(x + 24, y + 94, lines[1], 20 if font == BODY else 16, MUTED, 400, font, maxw=w - 40))
    return ''.join(b)


def build_stage(lang, c):
    H = 214
    font = c['font']
    b = [notched(W, H)]
    b.append(''.join(f'<rect x="{x}" y="{y // 2 + 8}" width="2" height="2" fill="{MUTED}" opacity=".45"/>' for x, y in STARS[:8]))
    b.append(bricks(8, 186, W - 16, 20, row=10, brick=20))
    # left destination
    b.append(f'<path fill="{BLUE_D}" d="M140 132h8v28h-8zM316 132h8v28h-8z"/>')
    b.append(bricks(96, 160, 272, 16, row=8, brick=16))
    b.append(signboard(32, 24, 396, 108, 'DAY JOB', YELLOW, c['job'], font))
    # right destination
    b.append(f'<path fill="{BLUE_D}" d="M640 132h8v28h-8zM816 132h8v28h-8z"/>')
    b.append(bricks(592, 160, 272, 16, row=8, brick=16))
    b.append(signboard(532, 24, 396, 108, 'SIDE PROJECT', MINT, c['side'], font))
    t, tw = tag(0, 0, *c['tag'])
    b.append(f'<g transform="translate({928 - 16 - tw} 11)">{t}</g>')
    # pipe + stack scenery
    b.append(f'<rect x="38" y="160" width="36" height="26" fill="{MINT}"/><rect x="42" y="160" width="5" height="26" fill="{MINT_L}"/>'
             f'<rect x="66" y="160" width="8" height="26" fill="{MINT_D}"/><rect x="32" y="148" width="48" height="14" fill="{MINT}"/>'
             f'<rect x="72" y="148" width="8" height="14" fill="{MINT_D}"/>')
    b.append(stack(['.C.', 'RCC', 'RRY'], 14, 880, 144))
    # middle: kana block, bobbing coin, dotted route
    b.append(stack(['Y'], 40, 460, 40))
    b.append(text(480, 71, 'あ', 32, NAVY, 400, JA, 'middle'))
    b.append(f'<g class="bob">{sprite(COIN, COIN_C, 471, 104, 3)}</g>')
    b.append(f'<path fill="{CREAM}" d="' + ''.join(f'M{x} 166h4v4h-4z' for x in range(376, 590, 16)) + '"/>')
    css = ('.bob{animation:bob 2.8s ease-in-out infinite}'
           '@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}')
    return write('stage' + ('-ja' if lang == 'ja' else ''), W, H, c['stage_title'], c['stage_desc'], ''.join(b), css)


# --------------------------------------------------------------------------
# 4. Toolbox: one interlocking stack; the last piece drops into place.
TOOLS = [('Y', 'Python', 'FastAPI'), ('C', 'Flutter', 'Dart'), ('M', 'AI agents', 'RAG'), ('R', 'Google Cloud', 'Docker')]
TOOL_TITLE = 'Toolbox: Python / FastAPI, Flutter / Dart, AI agents / RAG, Google Cloud / Docker'
TOOL_DESC = ('Four interlocking falling-block pieces in one stack: yellow Python and FastAPI, cyan Flutter and Dart, '
             'mint AI agents and RAG, red Google Cloud and Docker. The red piece drops into place, pauses, and repeats.')


def _cells(spec):
    out = []
    for r, (c0, c1) in spec:
        out += [(c, r) for c in range(c0, c1 + 1)]
    return out


def _toolbox(name, cols, rows, u, ox, oy, pieces, labels, w, h):
    b = [notched(w, h)]
    well = rounded([(ox - 8, oy - 6), (ox - 8, oy + rows * u + 6), (ox + cols * u + 8, oy + rows * u + 6),
                    (ox + cols * u + 8, oy - 6)], 8, closed=False)
    b.append(maze_wall(well))
    # faint grid in the empty rows
    b.append(f'<path fill="{NAVY3}" d="' + ''.join(
        f'M{ox + cc * u + u // 2 - 1} {oy + rr * u + u // 2 - 1}h2v2h-2z' for rr in range(rows) for cc in range(cols)) + '"/>')
    last = len(pieces) - 1
    for i, ((key, l1, l2), cells, (lx, ly)) in enumerate(zip(TOOLS, pieces, labels)):
        ink = CREAM if key == 'R' else NAVY
        g = block_cells(cells, u, ox, oy, key)
        g += text(lx, ly, l1, 28, ink, 400, maxw=168) + text(lx, ly + 24, l2, 22, ink, 400, maxw=168)
        b.append(f'<g class="drop">{g}</g>' if i == last else g)
    dy = 2 * u
    css = (f'.drop{{animation:drop 7s linear infinite}}'
           f'@keyframes drop{{0%{{transform:translateY(-{dy}px);opacity:0}}5%{{transform:translateY(-{dy}px);opacity:1}}'
           f'18%{{transform:translateY(-{dy}px)}}18.1%{{transform:translateY(-{u}px)}}30%{{transform:translateY(-{u}px)}}'
           f'30.1%,90%{{transform:translateY(0);opacity:1}}96%,100%{{transform:translateY(0);opacity:0}}}}')
    return write(name, w, h, TOOL_TITLE, TOOL_DESC, ''.join(b), css)


def build_toolbox():
    u, ox, oy = 38, 24, 26
    pieces = [_cells([(4, (0, 6)), (3, (0, 5)), (2, (0, 1))]),
              _cells([(4, (7, 13)), (3, (6, 12)), (2, (10, 12))]),
              _cells([(4, (14, 18)), (3, (13, 17)), (2, (13, 14))]),
              _cells([(4, (19, 23)), (3, (18, 23)), (2, (20, 23))])]
    base = oy + 3 * u + 31
    # x = first column the piece owns in BOTH label rows, so text never crosses a neighbour
    labels = [(ox + c * u + 14, base) for c in (0, 7, 14, 19)]
    _toolbox('toolbox', 24, 5, u, ox, oy, pieces, labels, W, oy + 5 * u + 26)



# --------------------------------------------------------------------------
# 5. World route
def _circle_cells(cx, cy, r):
    return [(i, j) for j in range(cy - r, cy + r + 1) for i in range(cx - r, cx + r + 1)
            if (i - cx) ** 2 + (j - cy) ** 2 <= r * r + r * 0.6]


def build_route(lang, c):
    H = 186
    font = c['font']
    xs = (140, 480, 820)
    b = [notched(W, H)]
    names = ('DHAKA', 'MIYAZAKI', 'TSUKUBA')
    for x, n, sub in zip(xs, names, c['stops']):
        b.append(ptext_c(x, 20, n, 3, CREAM))
        b.append(text(x, 64, sub, 20 if font == BODY else 16, MUTED, 400, font, 'middle', maxw=300))
        b.append(bricks(x - 60, 120, 120, 12, row=6, brick=12))
    # Dhaka: Bangladesh flag (green field, red disc)
    b.append(f'<rect x="112" y="72" width="4" height="48" fill="{MUTED}"/>')
    b.append(f'<rect x="116" y="74" width="48" height="30" fill="#1f8a5b"/>')
    b.append(f'<path fill="#e0473a" d="{cells_path(_circle_cells(0, 0, 4), 2, 136, 89)}"/>')
    # Miyazaki: palm and sun
    b.append(sprite(['.YYYY.', 'YYYYYY', 'YYYYYY', 'YYYYYY', 'YYYYYY', '.YYYY.'], {'Y': YELLOW}, 500, 70, 4))
    b.append(sprite(['..MMM..MMM..', '.M...MM...M.', 'M...MTTM...M', '....M.TM....', '......T.....',
                     '......T.....', '.....T......', '.....T......', '.....T......', '.....T......',
                     '....TT......'], {'M': MINT, 'T': YELLOW_D}, 446, 76, 4))
    # Tsukuba: twin-peaked mountain
    peaks = []
    for row in range(11):
        for col in range(26):
            h1 = 10 - abs(col - 8) if abs(col - 8) <= 10 else -1
            h2 = 10 - abs(col - 17) + 1 if abs(col - 17) <= 11 else -1
            if 10 - row <= max(h1, h2):
                peaks.append((col, row))
    b.append(f'<path fill="{MINT_D}" d="{cells_path(peaks, 4, 768, 76)}"/>')
    b.append(f'<path fill="{MINT}" d="{cells_path([(cc, r) for cc, r in peaks if r < 4], 4, 768, 76)}"/>')
    # corridor
    b.append(maze_wall(rounded([(70, 140), (890, 140), (890, 166), (70, 166)], 13)))
    r = Route('rt', [(100, 153, 0), (xs[1], 153, 1.4), (860, 153, 1.6)], speed=80, gap=1.0)
    dots, dcss = r.dots(step=16, first=20, until=r.length - 2, size=4)
    b.append(dots)
    # stations: short connectors from each platform down to the corridor
    b.append(f'<path fill="{BLUE_D}" d="' + ''.join(f'M{x - 6} 132h12v6h-12z' for x in xs) + '"/>')
    b.append(r.traveller(1.5))
    return write('route' + ('-ja' if lang == 'ja' else ''), W, H, c['route_title'], c['route_desc'], ''.join(b),
                 CHOMP_CSS + r.css() + dcss)


# --------------------------------------------------------------------------
# 6. After hours shelf
def _dota_art(x, y):
    n, u = 15, 7
    lane, river, ground, base_g, base_r = [], [], [], [], []
    for j in range(n):
        for i in range(n):
            if i <= 2 and j >= 12:
                base_g.append((i, j))
            elif i >= 12 and j <= 2:
                base_r.append((i, j))
            elif (i == 1 and 1 <= j <= 13) or (j == 1 and 1 <= i <= 13) or (j == 13 and 1 <= i <= 13) \
                    or (i == 13 and 1 <= j <= 13) or (i + j == 14):
                lane.append((i, j))
            elif abs(i - j) <= 0 and 2 < i < 12:
                river.append((i, j))
            else:
                ground.append((i, j))
    return (f'<path fill="#173a2c" d="{cells_path(ground, u, x, y)}"/>'
            f'<path fill="{BLUE}" d="{cells_path(river, u, x, y)}"/>'
            f'<path fill="#c9b98f" d="{cells_path(lane, u, x, y)}"/>'
            f'<path fill="{MINT}" d="{cells_path(base_g, u, x, y)}"/>'
            f'<path fill="{RED_L}" d="{cells_path(base_r, u, x, y)}"/>')


def _rooftops_art(x, y):
    b = [f'<rect x="{x}" y="{y}" width="150" height="108" fill="#101a4a"/>']
    b.append(sprite(['.CC.', 'CC..', 'CC..', '.CC.'], {'C': CREAM}, x + 116, y + 10, 4))  # crescent
    b.append(sprite(['C.....C', '.C...C.', '..C.C..'], {'C': CREAM}, x + 58, y + 22, 3))  # bird
    sky = [(0, 70, 30), (28, 58, 26), (52, 80, 30), (100, 64, 30), (126, 76, 24)]
    for bx, top, w in sky:
        b.append(f'<rect x="{x + bx}" y="{y + top}" width="{w}" height="{108 - top}" fill="{BLUE_D}"/>'
                 f'<rect x="{x + bx}" y="{y + top}" width="{w}" height="4" fill="{RED}"/>')
    b.append(f'<rect x="{x + 80}" y="{y + 30}" width="20" height="78" fill="{NAVY3}"/>'
             f'<path fill="{RED}" d="M{x + 78} {y + 30}h24v-4h-4v-4h-4v-6h-8v6h-4v4h-4z"/>'
             f'<rect x="{x + 86}" y="{y + 42}" width="8" height="10" fill="{YELLOW}"/>')
    b.append(f'<path fill="{YELLOW_D}" d="M{x + 10} {y + 108}v-8h4v-4h4v-4h14v4h4v4h4v8z"/>')
    b.append(f'<path fill="{YELLOW}" d="M{x + 18} {y + 96}h4v4h-4zM{x + 28} {y + 100}h4v4h-4z"/>')
    return ''.join(b)


def _bars(x, y):
    out = []
    for i, (hgt, col) in enumerate(zip((3, 6, 4, 8, 5), (MINT, CYAN, YELLOW, RED_L, MINT))):
        out.append(f'<rect x="{x + i * 5}" y="{y + 24 - hgt * 3}" width="4" height="{hgt * 3}" fill="{col}"/>')
    return ''.join(out)


SHELF_ICONS = [
    lambda x, y: sprite(['C.C.C.C.', 'CCCCCCCC', 'CDCCCDCC', 'CCCCCCCC', 'CCDCCCDC', 'CCC..CCC', 'CCC..CCC',
                         'CCC..CCC'], {'C': '#d8c9a3', 'D': '#9f8f6a'}, x, y, 3),
    lambda x, y: sprite(['..OOOO..', '.OWOOOO.', 'OWOOROOO', 'OOORRROO', 'OOOOROOO', 'OOOOOOOO', '.OOOOOO.',
                         '..OOOO..'], {'O': '#f2a33a', 'R': RED, 'W': CREAM}, x, y, 3),
    lambda x, y: sprite(['..S.S...', '.S.S....', 'WWWWWW..', 'WWWWWWWW', 'WBBWWW.W', 'WWWWWWWW', 'WWWWWW..',
                         '.WWWW...'], {'S': MUTED, 'W': CREAM, 'B': BLUE}, x, y, 3),
    lambda x, y: sprite(['..WWWW..', '...WW...', '...WW...', '..WMMW..', '.WMMMMW.', 'WMMMMMMW', 'WMMMMMMW',
                         '.WWWWWW.'], {'W': CREAM, 'M': CYAN}, x, y, 3),
    lambda x, y: sprite(['........', '..BBBB..', '.BBLBBB.', 'YYYYYYYY', '.BBBBBB.', '..BBBB..', '........',
                         '........'], {'B': BLUE_L, 'L': CREAM, 'Y': YELLOW}, x, y + 3, 3),
    lambda x, y: _bars(x, y),
]


def build_shelf(lang, c):
    H = 316
    font = c['font']
    b = [notched(W, H)]
    b.append(ptext(28, 18, c['select'], 2, MUTED))
    feats = [('DOTA 2',), ('ASSASSIN\'S', 'CREED')]
    for i, (tx, title) in enumerate(zip((24, 492), feats)):
        y0, w, h = 40, 444, 136
        b.append(f'<rect x="{tx}" y="{y0}" width="{w}" height="{h}" rx="10" fill="{NAVY2}"/>')
        edge = rounded([(tx, y0), (tx + w, y0), (tx + w, y0 + h), (tx, y0 + h)], 10)
        if i == 0:
            b.append(f'<path d="{edge}" fill="none" stroke="{YELLOW}" stroke-width="4"/>')
        else:
            b.append(maze_wall(edge))
        ax, ay = tx + 14, y0 + 14
        b.append(f'<rect x="{ax}" y="{ay}" width="150" height="108" fill="#0e1640"/>')
        b.append(_dota_art(ax + 22, ay + 1) if i == 0 else _rooftops_art(ax, ay))
        for k, line in enumerate(title):
            b.append(ptext(tx + 184, y0 + 20 + k * 32, line, 3, CREAM))
        if c['feat_ja'][i]:
            b.append(text(tx + 184, y0 + 96, c['feat_ja'][i], 16, MUTED, 400, JA, maxw=250))
        b.append(text(tx + 184, y0 + 118, c['feat_sub'][i], 22 if font == BODY else 16, YELLOW if i == 0 else MINT, 700, font, maxw=250))
    b.append(ptext(10, 100, '>', 2, YELLOW))
    for k, ((name, cat), icon) in enumerate(zip(c['shelf'], SHELF_ICONS)):
        col, row = k % 3, k // 3
        x, y = 24 + col * 308, 192 + row * 58
        b.append(f'<rect x="{x}" y="{y}" width="296" height="48" rx="6" fill="{NAVY2}" stroke="{BLUE_D}" stroke-width="2"/>')
        b.append(icon(x + 12, y + 12))
        nf = JA if (lang == 'ja' and name != 'Avicii') else BODY
        b.append(text(x + 52, y + 23, name, 22 if nf == BODY else 16, CREAM, 700, nf, maxw=232))
        b.append(text(x + 52, y + 41, cat, 18 if font == BODY else 13, MUTED, 400, font))
    return write('shelf' + ('-ja' if lang == 'ja' else ''), W, H, c['shelf_title'], c['shelf_desc'], ''.join(b))


# --------------------------------------------------------------------------
# 7. Continue?
def build_continue(lang, c):
    H = 204
    b = [notched(W, H)]
    b.append(''.join(f'<rect x="{x}" y="{y}" width="2" height="2" fill="{MUTED}" opacity=".5"/>' for x, y in STARS[:7]))
    b.append(ptext_c(W / 2, 28, 'CONTINUE?', 6, CREAM, shadow=BLUE_D))
    label, kind = c['cont_opt']
    if kind == 'pixel':
        gw = pwidth('>', 3) + 14 + pwidth(label, 3)
        x0 = round((W - gw) / 2)
        b.append(ptext(x0 + pwidth('>', 3) + 14, 98, label, 3, YELLOW))
    else:
        gw = pwidth('>', 3) + 14 + round(measure(label, 24, JA))
        x0 = round((W - gw) / 2)
        b.append(text(x0 + pwidth('>', 3) + 14, 120, label, 24, YELLOW, 400, JA))
    b.append(f'<g class="cur">{ptext(x0, 98, ">", 3, YELLOW)}</g>')
    b.append(text(W / 2, 152, c['cont_sub'], 22 if c['font'] == BODY else 16, MUTED, 400, c['font'], 'middle'))
    b.append(bricks(8, 176, W - 16, 20, row=10, brick=20))
    b.append(f'<g transform="translate(96 162)">{chomper(2).replace("<g class=" + chr(34) + "mo" + chr(34) + ">", "<g>")}</g>')
    b.append(sprite(COIN, COIN_C, 140, 140, 3))
    b.append(stack(['..M.', 'CMMR', 'CCRR'], 18, 838, 122))
    css = ('.cur{animation:cur 1.8s ease-in-out infinite alternate}'
           '@keyframes cur{from{opacity:1}to{opacity:.25}}')
    return write('continue' + ('-ja' if lang == 'ja' else ''), W, H, c['cont_title'], c['cont_desc'], ''.join(b), css)


def main():
    OUT.mkdir(exist_ok=True)
    built = []
    for lang, c in COPY.items():
        built.append(build_hero(lang, c))
        for key, (label, ja) in c['heads'].items():
            built.append(build_head(lang, key, label, ja))
        built.append(build_stage(lang, c))
        built.append(build_route(lang, c))
        built.append(build_shelf(lang, c))
        built.append(build_continue(lang, c))
    build_toolbox()
    built.append('toolbox')
    print(f'Built {len(built)} SVGs in {OUT.relative_to(ROOT)}/')


if __name__ == '__main__':
    main()
