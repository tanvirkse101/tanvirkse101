"""Build original, dependency-free SVG HUD assets for the GitHub profile."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
MINT, PINK, PURPLE, GOLD = '#f3ed38', '#ff495c', '#67e8ed', '#f3ed38'

def text(x, y, value, size=18, color='#ededde', weight=400, spacing=0):
    return f'<text font-family="{"Arial,Helvetica,sans-serif" if size >= 25 else "monospace"}" font-style="{"italic" if size >= 25 else "normal"}" x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}">{escape(value)}</text>'

def svg(name, width, height, title, body):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>
<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#f3ed38" stroke-opacity=".04"/></pattern></defs>
<style>.signal{{animation:signal 5s ease-in-out infinite}}@keyframes signal{{50%{{opacity:.4}}}}@media(prefers-reduced-motion:reduce){{.signal{{animation:none}}}}</style>
<path d="M1 1H{width-25}L{width-1} 25V{height-1}H25L1 {height-25}Z" fill="#111414" stroke="#5c5d36"/>
<path d="M1 1H{width-25}L{width-1} 25V{height-1}H25L1 {height-25}Z" fill="url(#grid)"/>
<path d="M1 70V1H70M{width-70} {height-1}H{width-1}V{height-70}" fill="none" stroke="#f3ed38" stroke-width="2"/>{body}</svg>''' 
    (OUT / f'{name}.svg').write_text(content)

def section(name, number, title, subtitle, color=MINT):
    body = '<path d="M0 0H1100V72H765L739 98H0Z" fill="#f3ed38"/>'
    body += text(24, 51, number + ' / ' + title, 38, '#0b0e0e', 900, -1)
    body += text(27, 128, subtitle, 16, '#bcbfaa', 400, 1)
    body += text(865, 48, 'SYS://101', 19, '#0b0e0e', 700)
    svg(name, 1100, 150, title + ' — ' + subtitle, body)

section('section-player', '01', 'OPERATOR DOSSIER', 'IDENTITY VERIFIED // ENGINEER. GAMER. BUILDER.')
section('section-skills', '02', 'CYBERWARE / LOADOUT', 'TECH STACK REGISTERED // SIX MODULES INSTALLED.')
section('section-missions', '03', 'GIG BOARD', 'PUBLIC SOURCE // SELECT A CONTRACT TO INSPECT.')
section('section-career', '04', 'LIFEPATH ARCHIVE', 'BANGLADESH > JAPAN // EVERY CHECKPOINT COUNTS.')
section('section-arcade', '05', 'NEURAL FEED', 'CONTRIBUTION SIGNAL // VISUALIZING THE TRACE.')

icons = {
 'backend': '<path d="M24 15L5 32l19 17m28-34 19 17-19 17M44 6L32 57"/>',
 'interface': '<rect x="15" y="2" width="43" height="61" rx="7"/><path d="M29 10h15M31 54h10M23 21h27v22H23Z"/>',
 'ai': '<path d="M36 5L6 22v25l30 16 30-16V22ZM6 22l30 17 30-17M36 39v24M36 5v18"/><circle cx="36" cy="29" r="6"/>',
 'cloud': '<path d="M17 47C-3 47 0 24 15 23 14 0 48-3 53 19 76 14 84 47 61 47ZM36 32v31m-12-12 12 12 12-12"/>',
 'data': '<ellipse cx="36" cy="12" rx="29" ry="10"/><path d="M7 12v40c0 14 58 14 58 0V12M7 31c0 14 58 14 58 0"/>',
 'secondary': '<path d="M18 3h40v48L38 66 18 51ZM28 19h20M28 30h20M28 41h12"/>'
}
skills = [
 ('backend', '01', 'EXECUTION ENGINE', 'BACKEND // CORE SYSTEM', MINT, ['Python', 'Django / Flask / FastAPI'], 'LOGIC LOADED. SYSTEMS READY.'),
 ('interface', '02', 'OPTICAL INTERFACE', 'FRONTEND // DISPLAY SYSTEM', PINK, ['Flutter / Dart', 'TypeScript / Angular'], 'RENDER THE IDEA. SHIP THE INTERFACE.'),
 ('ai', '03', 'NEURAL PROCESSOR', 'AI + ML // PATTERN RECOGNITION', PURPLE, ['PyTorch / TensorFlow', 'scikit-learn / Pandas / NumPy'], 'READ THE SIGNAL. BUILD THE PIPELINE.'),
 ('cloud', '04', 'DEPLOYMENT LINK', 'CLOUD // REMOTE SYSTEMS', GOLD, ['GCP / Firebase / AWS', 'Docker / Linux / CI/CD'], 'LOCAL BUILD > LIVE INFRASTRUCTURE.'),
 ('data', '05', 'MEMORY BANK', 'DATA // PERSISTENT STORAGE', MINT, ['PostgreSQL / MySQL', 'MongoDB / Redis / Firestore'], 'PERSIST THE STATE. RECOVER THE STORY.'),
 ('secondary', '06', 'EXPANSION BUS', 'FRAMEWORKS // EXTENSION PORT', PURPLE, ['Laravel / Rails', 'Spring Boot'], 'NEW ENVIRONMENT. ADAPT THE TOOLSET.'),
]
for key, n, title, label, color, lines, tagline in skills:
    body = f'<path d="M1 1H515L539 25V43H1Z" fill="{color}"/>'
    body += text(20, 29, 'CYBERWARE_' + n + ' // INSTALLED', 15, '#0b0e0e', 700, 1)
    body += text(20, 88, title, 29, '#ededde', 900, -1)
    body += text(20, 117, label, 13, color)
    body += f'<path d="M20 144H380l22 22h118" fill="none" stroke="{color}"/>'
    body += f'<g transform="translate(437 189) scale(.9)" stroke="{color}" stroke-width="2" fill="none">{icons[key]}</g>'
    for i, line in enumerate(lines):
        body += text(20, 190 + i * 34, line, 20, color if i == 0 else '#ededde', 700 if i == 0 else 400)
    body += text(20, 285, tagline, 13, '#aeb4ab')
    for j in range(28):
        body += f'<path d="M{22+j*5} 313v12" stroke="{color}" stroke-width="{1+j%3}"/>'
    body += text(348, 324, 'MODULE / ' + n, 13, color)
    svg('skill-' + key, 540, 344, title + ': ' + ', '.join(lines), body)

body = text(32, 45, 'TANVIR AHAMED', 32, '#ededde', 700, 1)
body += text(33, 77, '@tanvirkse101 / SOFTWARE ENGINEER', 17, MINT)
body += '<path d="M32 102H1068" stroke="#414638"/>'
for i, (label, value) in enumerate([('ACTIVE ASSIGNMENT', 'AI products @ AIZOTH Inc.'), ('CURRENT SECTOR', 'Tsukuba, Japan'), ('LIFEPATH', 'Bangladesh -> Japan')]):
    y = 137 + i*65
    body += text(32, y, label, 13, '#b8bdb1', 700, 2) + text(32, y+28, value, 23)
for i, (label, value) in enumerate([('COMMS PROTOCOLS', 'English / Japanese / Bengali'), ('AFTER HOURS', 'Games / Anime / Music'), ('RESEARCH TARGETS', 'ML systems / Cloud architecture')]):
    y = 137 + i*65
    body += text(600, y, label, 13, '#b8bdb1', 700, 2) + text(600, y+28, value, 21)
body += f'<circle class="signal" cx="1035" cy="51" r="7" fill="{MINT}"/>'
svg('player-card', 1100, 325, 'Tanvir Ahamed — engineer at AIZOTH, Tsukuba. Games, anime, music. English, Japanese, Bengali.', body)

missions = [
 ('commerce', '01', 'COMMERCE PROTOCOL', 'ecommerce-backend', 'PYTHON / BACKEND', MINT),
 ('translator', '02', 'TRANSLATION LINK', 'python-translator', 'PYTHON', PURPLE),
 ('api', '03', 'API CONSTRUCT', 'Go-CRUD-API', 'GO / API', GOLD),
 ('fraud', '04', 'ANOMALY SCANNER', 'CSE445_Credit_Card_Fraud', 'PYTHON / COURSEWORK', PINK),
 ('contest', '05', 'CODE TRIALS', 'B-jet-Programming-Contest', 'PYTHON / PRACTICE', MINT),
 ('blog', '06', 'PUBLISHER NODE', 'blog-app', 'PHP / TECHNICAL TEST', PURPLE),
]
for key, n, title, repo, label, color in missions:
    body = f'<path d="M1 1H80V72L60 92H1Z" fill="{color}"/>'
    body += text(13, 54, n, 42, '#0b0e0e', 900)
    body += text(101, 32, 'PUBLIC GIG // SOURCE AVAILABLE', 12, color)
    body += text(101, 68, title, 25, '#ededde', 900, -1)
    body += text(23, 124, repo, 18, '#c5c8bd')
    body += '<path d="M23 149H517" stroke="#414638"/>'
    body += text(23, 184, label, 13, color, 700)
    body += f'<path d="M357 161h160v38H345v-26Z" fill="{color}"/>'
    body += text(369, 186, 'JACK IN >', 16, '#0b0e0e', 700)
    svg('mission-' + key, 540, 221, title + ' — ' + repo + ' — ' + label, body)

body = '<path d="M55 58V492" stroke="#77783c" stroke-width="3"/>'
checkpoints = [
 ('00', '2020', 'NORTH SOUTH UNIVERSITY', 'B.Sc. Computer Engineering', '#b8bdb1'),
 ('01', '2020 - 2023', 'eSRD-LAB', 'Django / Flask / Dashboards / Data platforms', MINT),
 ('02', '2023', 'B-JET', 'Japanese language + engineering training', PURPLE),
 ('03', '2024 - 2025', 'HAVE A TALK INC.', 'APIs / Authentication / Cloud infrastructure', GOLD),
 ('04', '2025 - PRESENT', 'AIZOTH INC.', 'AI products / Python / Flutter / GCP', PINK),
]
for i, (n, year, title, desc, color) in enumerate(checkpoints):
    y=28+i*101
    body += f'<rect x="36" y="{y+15}" width="38" height="38" rx="0" fill="#111414" stroke="{color}"/>'
    body += text(43, y+41, n, 20, color, 700)
    body += text(100, y+29, year, 16, color, 700)
    body += text(305, y+30, title, 25, '#ededde', 700)
    body += text(305, y+62, desc, 18, '#b8bdb1')
svg('campaign-map', 1100, 540, 'Career campaign: NSU, eSRD-Lab, B-JET, Have a Talk, AIZOTH.', body)
body = text(35, 48, 'OPEN COMMS CHANNEL', 15, MINT, 700, 3)
body += text(35, 99, 'GOT A SYSTEM WORTH BUILDING?', 34, '#ededde', 700)
body += text(35, 139, "SEND THE BRIEF. LET'S BUILD SOMETHING REAL.", 20, '#b8bdb1')
body += f'<path d="M940 72h70m-35-35v70" stroke="{MINT}" stroke-width="8"/><circle cx="975" cy="72" r="52" fill="none" stroke="#77783c"/>'
svg('coop', 1100, 180, 'Co-op mode. Got a quest worth building? Contact Tanvir.', body)

# Original industrial title plate and cyberdeck schematic (no external artwork).
body = '<path d="M0 0H1100V493L1063 530H0Z" fill="#f3ed38"/>'
body += '<path d="M720 0H1100V493L1063 530H720L745 505V25Z" fill="#101414"/>'
body += text(32, 42, 'PERSONAL SYSTEM // TANVIRKSE101', 16, '#111414', 700, 1)
body += text(32, 80, 'ソフトウェアエンジニア', 19, '#111414', 700)
body += text(30, 193, 'TANVIR', 116, '#111414', 900, -7)
body += text(29, 294, 'AHAMED', 110, '#111414', 900, -7)
# Small displaced slices suggest signal corruption without flashing animation.
body += '<path d="M32 203h44v5H32m377-43h110v4H409M294 253h85v4H294" stroke="#ff495c" stroke-width="3"/>'
body += '<path d="M33 320H670l-21 21H33Z" fill="#111414"/>'
body += text(46, 335, 'SOFTWARE ENGINEER / GAMER / BUILDER', 14, '#f3ed38', 700, 1)
body += text(33, 391, 'WRITE CODE. BREAK LIMITS.', 29, '#111414', 900, -1)
body += text(34, 422, 'BUILD THE NEXT SYSTEM.', 29, '#111414', 900, -1)
body += text(34, 485, 'BD > JP   /   TSUKUBA SECTOR', 17, '#111414', 700)
for j in range(40):
    body += f'<path d="M{450+j*5} 466v23" stroke="#111414" stroke-width="{1+j%3}"/>'
body += text(775, 43, 'CUSTOM CYBERDECK', 16, '#67e8ed', 700, 2)
body += text(775, 69, 'UNIT_101 // ENGINEERING', 12, '#9ba8a0')
body += '<g fill="none" stroke="#53605a" stroke-width="1"><path d="M777 110h270v280H777Z M765 150h294M765 350h294M815 96v308M1010 96v308"/></g>'
# A geometric faceplate mounted inside a circuit assembly.
body += '<path d="M842 132h138l38 38v126l-61 70h-48l-67-70Z" fill="#202a29" stroke="#67e8ed" stroke-width="2"/>'
body += '<path d="M858 154h105l34 31-17 41H866l-17-41Z" fill="#111414" stroke="#5d6e65"/>'
body += '<path d="M856 240l57 12-12 20-37-9Zm139 0-57 12 12 20 37-9Z" fill="#f3ed38"/>'
body += '<path d="M925 255l-16 41h32ZM891 309h68l-17 27h-34Z" fill="#101414" stroke="#67e8ed"/>'
body += '<path d="M777 200h44l21 21M1018 280h29m-205 16-27 26h-38m241-137 18-18h21M925 132V99" fill="none" stroke="#67e8ed" stroke-width="2"/>'
for x,y in [(777,200),(1047,280),(777,322),(1057,167),(925,99)]:
    body += f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="#ff495c"/>'
body += text(783, 424, 'PYTHON / FLUTTER', 20, '#f3ed38', 700)
body += text(783, 453, 'AI / CLOUD SYSTEMS', 18, '#ededde')
body += '<circle class="signal" cx="788" cy="489" r="4" fill="#67e8ed"/>'
body += text(803, 494, 'READY FOR THE NEXT BUILD', 12, '#67e8ed')
svg('code-runner', 1100, 530, 'Tanvir Ahamed — software engineer, gamer, builder. Original yellow and black cyberdeck title screen.', body)

print('Built', len(list(OUT.glob('*.svg'))), 'SVG assets')
