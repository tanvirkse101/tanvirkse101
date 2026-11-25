"""Original animated cyberpunk UI around the owner's portfolio interests.
Artwork: respective owners; source images from tanvirahamed.dev/about/.
Run directly or through build-profile.py. No network required to regenerate.
"""
from pathlib import Path
from html import escape
import base64

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
Y,C,R='#f3ed38','#67e8ed','#ff495c'
STYLE='''<style>
.scan{animation:scan 8s linear infinite}.orbit{transform-origin:340px 135px;animation:orbit 24s linear infinite}.eq{transform-box:fill-box;transform-origin:bottom;animation:eq 2.4s ease-in-out infinite alternate}.trace{stroke-dasharray:10 14;animation:trace 7s linear infinite}
@keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(175px)}}@keyframes orbit{to{transform:rotate(360deg)}}@keyframes eq{from{transform:scaleY(.3)}to{transform:scaleY(1)}}@keyframes trace{to{stroke-dashoffset:-240}}
@media(prefers-reduced-motion:reduce){.scan,.orbit,.eq,.trace{animation:none}}
</style>'''
def text(x,y,s,size=18,color='#edefdf',weight=400):
 return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" font-family="Arial,Helvetica,sans-serif">{escape(s)}</text>'
def save(name,w,h,title,b):
 (OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>{STYLE}{b}</svg>')
def frame(w,h,col=Y):
 return f'<path d="M1 1H{w-24}L{w-1} 24V{h-1}H24L1 {h-24}Z" fill="#101414" stroke="{col}"/>'
hero=(ROOT/'scripts/templates/cyberdeck.svg').read_text()
hero=hero.replace('WRITE CODE. BREAK LIMITS.','GAMES. STORIES. SOUNDTRACKS.').replace('BUILD THE NEXT SYSTEM.','WELCOME TO MY WORLD.')
hero=hero.replace('</svg>',STYLE+f'<path class="trace" d="M33 508H670" stroke="{R}" stroke-width="3" fill="none"/></svg>')
(OUT/'code-runner.svg').write_text(hero)

for name,num,title,sub in [
 ('games','01','GAME LIBRARY','DOTA 2 / ASSASSIN’S CREED'),
 ('media','02','AFTER HOURS','ANIME / SERIES / FILM / MUSIC'),
 ('life','03','WORLD MAP','DHAKA > MIYAZAKI > TSUKUBA'),
 ('work','04','ENGINEER MODE','A SMALL LOOK AT WHAT I BUILD'),
 ('arcade','05','BONUS STAGE','THE CONTRIBUTION SNAKE IS BACK')]:
 b=frame(1000,110)+f'<path d="M0 0H1000V65H710L690 85H0Z" fill="{Y}"/>'
 b+=text(24,47,num+' / '+title,34,'#101414',900)+text(25,102,sub,13,'#b8bdb1')
 b+=f'<path class="trace" d="M755 90h220" fill="none" stroke="{C}" stroke-width="2"/>'
 save('heading-'+name,1000,110,title,b)

cards=[
 ('dota2','DOTA 2','MULTIPLAYER / MOBA','FIVE HEROES. ONE ANCIENT.',R),
 ('assassins-creed','ASSASSIN’S CREED','ACTION / ADVENTURE','HISTORY. ROOFTOPS. EXPLORATION.',Y),
 ('attack-on-titan','ATTACK ON TITAN','ANIME','FROM MY ANIME SHELF.',R),
 ('dragon-ball','DRAGON BALL Z','ANIME','FROM MY ANIME SHELF.',Y),
 ('the-office','THE OFFICE','SERIES','OFFICE HOURS, THE OTHER KIND.',C),
 ('breaking-bad','BREAKING BAD','SERIES','ANOTHER FAVORITE ON THE SHELF.',Y),
 ('interstellar','INTERSTELLAR','FILM','A LITTLE FURTHER FROM HOME.',C),
 ('avicii','AVICII','MUSIC','THE SOUNDTRACK SLOT.',Y),
]
for idx,(slug,title,category,tagline,col) in enumerate(cards):
 b=frame(480,330,col)
 b+=text(22,30,category,13,col,700)+text(22,105,f'{idx+1:02}',64,'#303a37',900)
 b+=text(24,139,'TANVIR’S',14,'#b8bdb1',700)+text(24,161,'FAVORITES',14,col,700)
 if slug!='avicii':
  data=base64.b64encode((OUT/'interests'/(slug+'.webp')).read_bytes()).decode()
  b+=f'<image href="data:image/webp;base64,{data}" x="190" y="44" width="266" height="184" preserveAspectRatio="xMidYMid slice"/>'
  b+=f'<path class="scan" d="M190 47H456" stroke="{col}" stroke-width="2" opacity=".55"/>'
 else:
  for j,h in enumerate([42,90,62,120,78,142,100,64,112,48]):
   b+=f'<rect class="eq" x="{200+j*25}" y="{210-h}" width="14" height="{h}" fill="{col if j%2 else C}" style="animation-delay:-{j*.27}s"/>'
 b+=f'<path d="M20 243H460" stroke="{col}"/>'
 b+=text(22,279,title,27 if len(title)>14 else 31,'#edefdf',900)
 b+=text(22,310,tagline,12,'#b8bdb1',700)
 save('interest-'+slug,480,330,title+' — '+category,b)

b=frame(1000,235)
b+=text(28,38,'CURRENT ROLE // AIZOTH · TSUKUBA',16,C,700)
b+=text(28,87,'SOFTWARE ENGINEER',37,'#edefdf',900)
b+=text(28,123,'AI applications · Python · FastAPI · Flutter · Google Cloud',20)
b+=f'<path class="trace" d="M28 149H970" stroke="{Y}" fill="none"/>'
b+=text(28,181,'PERSONAL SIDE QUEST',13,Y,700)
b+=text(28,214,'Japanese-learning app / vocabulary + kanji / in development',20)
save('engineer-mode',1000,235,'Engineer at AIZOTH. Python, FastAPI, Flutter, Google Cloud. Japanese-learning app in development.',b)
print('Built animated cyberpunk hero, section headers, eight interest cards, and engineering panel.')
