"""Build the original, dependency-free SVG artwork for the GitHub profile README.

Run:  python3 scripts/build-profile.py

Every asset is generated twice: `assets/<name>.svg` (English) and
`assets/<name>-ja.svg` (Japanese). Edit the copy in the COPY dict below, never
the SVG files directly, so regeneration keeps your changes.

Essential information also lives as selectable text in README.md / README-ja.md;
these images are decoration plus a quick visual summary.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)

# Palette: yellow/black with red and cyan accents.
YELLOW, RED, CYAN = '#f3ed38', '#ff495c', '#67e8ed'
INK, PANEL, LINE = '#0b0e0e', '#111414', '#414638'
TEXT, MUTED = '#ededde', '#b8bdb1'

SANS = "'Arial Black',Arial,Helvetica,sans-serif"
SANS_JA = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Yu Gothic',Meiryo,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

W = 1000  # every banner shares one width so the page reads as one system


def t(x, y, value, size=18, color=TEXT, weight=400, font='sans', spacing=0, anchor='start', italic=False, cls=''):
    family = {'sans': SANS, 'ja': SANS_JA, 'mono': MONO}[font]
    style = ' font-style="italic"' if italic else ''
    klass = f' class="{cls}"' if cls else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" letter-spacing="{spacing}" text-anchor="{anchor}"{style}{klass}>{escape(value)}</text>')


def frame(height):
    """Angular panel with a faint grid and two yellow corner brackets."""
    clip = f'M1 1H{W-25}L{W-1} 25V{height-1}H25L1 {height-25}Z'
    return (f'<path d="{clip}" fill="{PANEL}" stroke="#5c5d36"/>'
            f'<path d="{clip}" fill="url(#grid)"/>'
            f'<path d="M1 60V1H60M{W-60} {height-1}H{W-1}V{height-60}" fill="none" stroke="{YELLOW}" stroke-width="2"/>')


def write(name, height, title, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
           f'role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>'
           '<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
           f'<path d="M24 0H0V24" fill="none" stroke="{YELLOW}" stroke-opacity=".05"/></pattern></defs>'
           '<style>.pulse{animation:pulse 2.4s ease-in-out infinite}'
           '@keyframes pulse{50%{opacity:.25}}'
           '@media(prefers-reduced-motion:reduce){.pulse{animation:none}}</style>'
           f'{body}</svg>\n')
    (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')


# --------------------------------------------------------------------------
# Copy. Keep facts in sync with README.md, README-ja.md and tanvirahamed.dev.
# --------------------------------------------------------------------------
COPY = {
    'en': {
        'font': 'sans',
        'hero_title': 'Tanvir Ahamed. Software engineer at AIZOTH in Tsukuba, Japan. '
                      'I build AI agents. Then I build the APIs they are allowed to touch.',
        'kicker': 'PLAYER ONE // PRESS START',
        'subname': '',
        'role': 'Software Engineer · AIZOTH · Tsukuba, Japan',
        'quote': ['I build AI agents. Then I build', 'the APIs they’re allowed to touch.'],
        'save': 'SAVE FILE // 01',
        'rows': [('MAIN QUEST', 'AI agents + RAG apps'),
                 ('SIDE QUEST', 'Kanji review app'),
                 ('ROUTE', 'Dhaka → Miyazaki → Tsukuba'),
                 ('LANGUAGES', 'Bengali · English · 日本語')],
        'footer': 'SINCE 2020 // SAVE OFTEN',

        'flow_title': 'Illustrative application flow: Flutter interface, FastAPI service, '
                      'retrieval and agent workflow, Google Cloud. A simplified example, not a disclosed architecture.',
        'flow_head': 'MAIN QUEST // EVERY LAYER PLAYS CO-OP',
        'flow_nodes': [('Flutter', 'interface'), ('FastAPI', 'service'),
                       ('Retrieval', '+ agent workflow'), ('Google Cloud', 'Cloud Run · Vertex AI')],
        'flow_note': 'ILLUSTRATIVE ONLY — the layers I work across, not an employer architecture',

        'loop_title': 'Side quest, in development: a Japanese study app. Build the review queue, '
                      'grade and schedule with a pure Dart scheduler, save the card, review log and stats in one Firestore transaction.',
        'loop_head': 'SIDE QUEST // JAPANESE, WITH SAVE FILES',
        'loop_tag': 'IN DEVELOPMENT',
        'loop_steps': [('01', 'BUILD THE QUEUE', 'due cards + daily new'),
                       ('02', 'GRADE + SCHEDULE', 'pure Dart: FSRS / SM-2'),
                       ('03', 'SAVE TOGETHER', 'one Firestore transaction')],
        'loop_back': 'NEXT REVIEW // the kanji respawns',
        'loop_stack': 'Flutter · Dart · Riverpod · Firestore',

        'map_title': 'World map, three sync points: Dhaka 2015 to 2023, Miyazaki 2024 to 2025, Tsukuba 2025 to now.',
        'map_head': 'WORLD MAP // SYNC POINTS',
        'map_points': [('Dhaka', '2015 – 2023', 'NSU · eSRD-Lab · B-JET'),
                       ('Miyazaki', '2024 – 2025', 'Have a Talk Inc.'),
                       ('Tsukuba', '2025 – now', 'AIZOTH Inc.')],
        'map_now': 'YOU ARE HERE',

        'party_title': 'Party invite: have a side quest that needs another engineer? Email Tanvir.',
        'party_kicker': 'PARTY INVITE // 1 SLOT OPEN',
        'party_lines': ['Have a side quest that', 'needs another engineer?'],
        'party_button': 'SEND INVITE',
    },
    'ja': {
        'font': 'ja',
        'hero_title': 'タンヴィル・アハメド。つくばのAIZOTHで働くソフトウェアエンジニア。'
                      'AIエージェントを作り、そのエージェントが触れてよいAPIも作っています。',
        'kicker': 'PLAYER ONE // PRESS START',
        'subname': 'タンヴィル・アハメド',
        'role': 'ソフトウェアエンジニア · AIZOTH · つくば',
        'quote': ['AIエージェントを作る。', 'そして、触れてよいAPIも作る。'],
        'save': 'SAVE FILE // 01',
        'rows': [('メインクエスト', 'AIエージェント + RAG'),
                 ('サイドクエスト', '漢字の復習アプリ'),
                 ('ルート', 'ダッカ → 宮崎 → つくば'),
                 ('言語', 'ベンガル語 · 英語 · 日本語')],
        'footer': '2020年から実務 // こまめにセーブ',

        'flow_title': '説明用のアプリ構成例：Flutterの画面、FastAPIのサービス、検索とエージェントの処理、Google Cloud。'
                      '実際の社内構成ではありません。',
        'flow_head': 'メインクエスト // 全レイヤーで協力プレイ',
        'flow_nodes': [('Flutter', '画面'), ('FastAPI', 'サービス'),
                       ('Retrieval', '+ エージェント処理'), ('Google Cloud', 'Cloud Run · Vertex AI')],
        'flow_note': '説明用の簡略図です。勤務先の実際の構成ではありません。',

        'loop_title': 'サイドクエスト（開発中）：日本語学習アプリ。復習キューを作り、純粋なDartのスケジューラで次回日時を決め、'
                      'カード・復習ログ・統計を一つのFirestoreトランザクションで保存します。',
        'loop_head': 'サイドクエスト // セーブ機能つき日本語学習',
        'loop_tag': '開発中',
        'loop_steps': [('01', 'キューを作る', '期限のカード + 今日の新規'),
                       ('02', '評価して予約', '純粋なDart：FSRS / SM-2'),
                       ('03', 'まとめて保存', 'Firestoreトランザクション')],
        'loop_back': '次の復習 // 漢字はまたリスポーンする',
        'loop_stack': 'Flutter · Dart · Riverpod · Firestore',

        'map_title': 'ワールドマップ。同期ポイントは三つ：ダッカ（2015〜2023）、宮崎（2024〜2025）、つくば（2025〜現在）。',
        'map_head': 'ワールドマップ // 同期ポイント',
        'map_points': [('ダッカ', '2015 – 2023', 'NSU · eSRD-Lab · B-JET'),
                       ('宮崎', '2024 – 2025', 'Have a Talk Inc.'),
                       ('つくば', '2025 – 現在', 'AIZOTH Inc.')],
        'map_now': '現在地',

        'party_title': 'パーティー募集：エンジニアが一人足りないサイドクエストがあれば、メールでご連絡ください。',
        'party_kicker': 'PARTY INVITE // 空きスロット 1',
        'party_lines': ['エンジニアが一人足りない', 'サイドクエスト、ありませんか？'],
        'party_button': '招待を送る',
    },
}


# Personal profile copy: interests lead; engineering is one part of the story.
COPY['en'].update({
    'hero_title': 'Tanvir Ahamed. Games, good stories, and an Avicii soundtrack. Tsukuba, Japan.',
    'role': 'Gamer · Software engineer · Tsukuba, Japan',
    'quote': ['Games, good stories,', 'and an Avicii soundtrack.'],
    'rows': [('GAMES', 'Dota 2 / Assassin’s Creed'),
             ('SOUNDTRACK', 'Avicii'),
             ('BASED IN', 'Tsukuba, Japan'),
             ('LANGUAGES', 'Bengali · English · Japanese')],
    'footer': 'WELCOME TO MY CORNER',
    'map_head': 'A FEW PLACES IN MY STORY',
    'map_points': [('Dhaka', '2015 – 2023', 'Bangladesh'),
                   ('Miyazaki', '2024 – 2025', 'Japan'),
                   ('Tsukuba', '2025 – now', 'Japan')],
    'party_title': 'Talk games, swap recommendations, or build something together. Say hello.',
    'party_kicker': 'GOOD CONVERSATIONS START HERE',
    'party_lines': ['Games. Music. Good stories.', 'Got a recommendation?'],
    'party_button': 'SAY HELLO',
})
COPY['ja'].update({
    'hero_title': 'タンヴィル・アハメド。ゲーム、物語、Aviciiの音楽。つくば在住。',
    'role': 'ゲーム好き · エンジニア · つくば',
    'quote': ['ゲームと、心に残る物語。', 'そして、Aviciiの音楽。'],
    'rows': [('ゲーム', 'Dota 2 / アサシン クリード'),
             ('音楽', 'Avicii'),
             ('暮らしの拠点', '茨城県つくば市'),
             ('言語', 'ベンガル語 · 英語 · 日本語')],
    'footer': '自分の小さな居場所へ、ようこそ',
    'map_head': 'これまで暮らしてきた場所',
    'map_points': [('ダッカ', '2015 – 2023', 'Bangladesh'),
                   ('宮崎', '2024 – 2025', 'Japan'),
                   ('つくば', '2025 – 現在', 'Japan')],
    'party_title': 'ゲームの話、おすすめの交換、一緒に何かを作る話。気軽にどうぞ。',
    'party_kicker': '好きなものの話から、はじめよう',
    'party_lines': ['ゲームの話も、おすすめの交換も。', '一緒に何かを作る話も。'],
    'party_button': 'メールする',
})


def hero(c, suffix):
    f = c['font']
    ja = f == 'ja'
    b = frame(440)
    # Yellow title slab with a clipped edge, dark save-file panel on the right.
    b += f'<path d="M0 0H600L630 30V440H0Z" fill="{YELLOW}"/>'
    b += f'<path d="M36 32H400L384 70H36Z" fill="{INK}"/>'
    b += t(50, 58, c['kicker'], 17, YELLOW, 700, 'mono', 2)
    if c['subname']:
        b += t(414, 58, c['subname'], 16, INK, 700, 'ja')
    b += t(30, 172, 'TANVIR', 112, INK, 900, 'sans', -5)
    b += t(30, 274, 'AHAMED', 112, INK, 900, 'sans', -5)
    # Small displaced slices: a quiet glitch, no flashing.
    b += f'<path d="M34 184h58v5H34M496 112h82v5h-82M220 286h70v5h-70" stroke="{RED}" stroke-width="3"/>'
    b += f'<path d="M30 300H590L572 336H30Z" fill="{INK}"/>'
    b += t(44, 326, c['role'], 19 if ja else 20, YELLOW, 700, f)
    b += t(32, 382, c['quote'][0], 23, INK, 900, f, italic=not ja)
    b += t(32, 414, c['quote'][1], 23, INK, 900, f, italic=not ja)
    # Save-file panel.
    b += t(664, 62, c['save'], 17, CYAN, 700, 'mono', 3)
    b += f'<path d="M664 78H960" stroke="{LINE}"/>'
    for i, (label, value) in enumerate(c['rows']):
        y = 116 + i * 70
        b += t(664, y, label, 14, MUTED, 700, 'ja' if ja else 'mono', 2)
        b += t(664, y + 30, value, 19, TEXT, 700, 'ja' if ja else 'sans')
    b += f'<rect class="pulse" x="664" y="397" width="10" height="10" fill="{CYAN}"/>'
    b += t(686, 407, c['footer'], 13, CYAN, 700, 'ja' if ja else 'mono', 1)
    write('hero' + suffix, 440, c['hero_title'], b)


def flow(c, suffix):
    f = c['font']
    b = frame(290)
    b += t(36, 52, c['flow_head'], 18, YELLOW, 700, f if f == 'ja' else 'mono', 2)
    colors = [YELLOW, CYAN, RED, YELLOW]
    for i, ((name, role), col) in enumerate(zip(c['flow_nodes'], colors)):
        x = 36 + i * 236
        b += f'<path d="M{x} 86H{x+190}L{x+206} 102V206H{x+16}L{x} 190Z" fill="{INK}" stroke="{col}" stroke-width="2"/>'
        b += f'<path d="M{x} 86H{x+64}L{x+52} 104H{x}Z" fill="{col}"/>'
        b += t(x + 10, 100, f'P{i+1}', 13, INK, 700, 'mono', 1)
        b += t(x + 18, 152, name, 27 if len(name) < 10 else 24, TEXT, 900, 'sans', -0.5)
        b += t(x + 18, 182, role, 15 if len(role) < 17 else 13, col, 700, f if f == 'ja' else 'mono')
        if i < 3:
            ax = x + 212
            b += f'<path d="M{ax} 146H{ax+24}M{ax+16} 138l8 8-8 8" fill="none" stroke="{MUTED}" stroke-width="2.5"/>'
    b += f'<path d="M36 236H964" stroke="{LINE}" stroke-dasharray="6 6"/>'
    b += t(36, 266, c['flow_note'], 14, MUTED, 400, f if f == 'ja' else 'mono', 1)
    write('main-quest' + suffix, 290, c['flow_title'], b)


def review_loop(c, suffix):
    f = c['font']
    ja = f == 'ja'
    b = frame(330)
    b += f'<path d="M0 0H640L616 52H0Z" fill="{YELLOW}"/>'
    b += t(30, 35, c['loop_head'], 19, INK, 900, f if ja else 'mono', 1)
    b += f'<path d="M780 18H966V50H764Z" fill="{RED}"/>'
    b += f'<rect class="pulse" x="782" y="29" width="10" height="10" fill="{INK}"/>'
    b += t(804, 40, c['loop_tag'], 15, INK, 900, f if ja else 'mono', 2)
    for i, (n, name, sub) in enumerate(c['loop_steps']):
        x = 36 + i * 318
        col = [CYAN, YELLOW, RED][i]
        b += f'<path d="M{x} 86H{x+262}L{x+282} 106V196H{x}Z" fill="{INK}" stroke="{col}" stroke-width="2"/>'
        b += t(x + 18, 126, n, 30, col, 900, 'mono')
        b += t(x + 70, 126, name, 18 if ja else 19, TEXT, 900, f if ja else 'mono', 0 if ja else 1)
        b += t(x + 18, 172, sub, 15, MUTED, 400, f if ja else 'mono')
        if i < 2:
            ax = x + 288
            b += f'<path d="M{ax} 141H{ax+24}M{ax+16} 133l8 8-8 8" fill="none" stroke="{MUTED}" stroke-width="2.5"/>'
    # Loop back from save to queue: the review never really ends.
    b += f'<path d="M918 196V236H177V204M169 214l8-10 8 10" fill="none" stroke="{CYAN}" stroke-width="2" stroke-dasharray="7 5"/>'
    b += f'<path d="M316 222H684V250H316Z" fill="{PANEL}"/>'
    b += t(500, 242, c['loop_back'], 14, CYAN, 700, f if ja else 'mono', 1, 'middle')
    b += t(36, 300, c['loop_stack'], 15, MUTED, 700, 'mono', 1)
    write('side-quest' + suffix, 330, c['loop_title'], b)


def world_map(c, suffix):
    f = c['font']
    ja = f == 'ja'
    b = frame(270)
    b += t(36, 52, c['map_head'], 18, YELLOW, 700, f if ja else 'mono', 2)
    xs = [170, 500, 830]
    b += f'<path d="M{xs[0]} 132H{xs[2]}" stroke="{LINE}" stroke-width="3" stroke-dasharray="10 8"/>'
    for i, ((city, years, what), x) in enumerate(zip(c['map_points'], xs)):
        current = i == 2
        col = CYAN if current else YELLOW
        # Diamond sync-point marker.
        b += f'<path d="M{x} 110L{x+22} 132L{x} 154L{x-22} 132Z" fill="{INK}" stroke="{col}" stroke-width="3"/>'
        pulse = 'class="pulse" ' if current else ''
        b += f'<path {pulse}d="M{x} 122L{x+10} 132L{x} 142L{x-10} 132Z" fill="{col}"/>'
        b += t(x, 96, f'SYNC 0{i+1}', 13, col, 700, 'mono', 2, 'middle')
        b += t(x, 194, city, 30, TEXT, 900, f, -0.5 if not ja else 0, 'middle')
        b += t(x, 222, years, 15, col, 700, 'mono', 1, 'middle')
        b += t(x, 246, what, 14, MUTED, 400, 'mono', 0, 'middle')
    b += f'<path d="M864 123H978L970 141H864Z" fill="{CYAN}"/>'
    b += t(870, 136, c['map_now'], 11, INK, 900, f if ja else 'mono', 0.5)
    write('world-map' + suffix, 270, c['map_title'], b)


def party(c, suffix):
    f = c['font']
    ja = f == 'ja'
    b = frame(210)
    b += t(36, 52, c['party_kicker'], 16, CYAN, 700, f if ja else 'mono', 2)
    b += t(36, 104, c['party_lines'][0], 28 if ja else 30, TEXT, 900, f)
    b += t(36, 150, c['party_lines'][1], 28 if ja else 30, TEXT, 900, f)
    # Five party slots: four taken, one open.
    for i in range(5):
        x = 640 + i * 62
        if i < 4:
            b += f'<path d="M{x} 70H{x+48}V118H{x}Z" fill="{YELLOW if i % 2 == 0 else CYAN}" fill-opacity=".9"/>'
        else:
            b += f'<path d="M{x} 70H{x+48}V118H{x}Z" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>'
            b += t(x + 24, 103, '?', 26, RED, 900, 'mono', 0, 'middle')
    b += f'<path d="M640 140H936L956 160V178H660L640 158Z" fill="{YELLOW}"/>'
    b += t(798, 166, c['party_button'] + ' →', 17, INK, 900, f if ja else 'mono', 2, 'middle')
    write('party-invite' + suffix, 210, c['party_title'], b)


for lang, copy in COPY.items():
    sfx = '' if lang == 'en' else '-ja'
    hero(copy, sfx)
    flow(copy, sfx)
    review_loop(copy, sfx)
    world_map(copy, sfx)
    party(copy, sfx)

print('Built', len(list(OUT.glob('*.svg'))), 'SVG files in', OUT.relative_to(ROOT))

# Keep the cyberpunk interest panels in the same reproducible build.
import runpy
runpy.run_path(str(ROOT / "scripts" / "build-interests.py"), run_name="__main__")
