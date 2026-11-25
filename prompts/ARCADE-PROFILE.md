# Arcade profile — design brief

The profile at github.com/tanvirkse101 is a small retro arcade world. It replaced the
earlier Cyberpunk design, which the owner rejected. Keep extending this direction rather
than going back to that one.

## Facts (recheck https://tanvirahamed.dev/about/ before changing them)

Tanvir Ahamed. Software engineer at AIZOTH, Tsukuba, Japan. Originally from Bangladesh.
Route: Dhaka → Miyazaki → Tsukuba. Speaks Bengali, English, and Japanese.
Side project: a Japanese-learning app (vocabulary, kanji, spaced repetition). It is in
development and has no public demo.
Favorites: Dota 2 and Assassin's Creed (games), Attack on Titan and Dragon Ball Z (anime),
The Office and Breaking Bad (series), Interstellar (film), Avicii (music).
Do not invent ranks, main heroes, playtime, metrics, achievements, or demos.
The maze, platform, and block games are design influences only. Never present them as
the owner's favorite games.

## Visual system

- Palette: navy `#0b1026`, maze blue `#2f6bff`, arcade yellow `#ffcc33`,
  brick `#c8402f`, mint `#5fe0a8`, cyan `#3fd0e6`, cream `#f6ecd2`.
- One pixel grid. Fonts are embedded in each SVG as subsets, all SIL OFL and
  vendored in `scripts/fonts/`: Press Start 2P for arcade labels, VT323 for small
  text, DotGothic16 for Japanese. Pixelify Sans was tried and rejected because its
  c/o, B/8 and Z/2 look too alike at small sizes.
- Maze double-line walls and dotted routes connect sections. Brick platforms, pipes,
  and coins frame content. Bevelled blocks interlock for the toolbox.
  All artwork is original. No official logos or art.
- Only a few slow loops: the hero chomper, the stage coin, the toolbox block drop, the
  route marker, and the continue cursor. Every SVG is complete when static.
  `prefers-reduced-motion` stops all of them.
- No neon gradients, Cyberpunk vocabulary, skill bars, XP, or stats invented for flavor.

## Working on it

- Run `uv run scripts/build-profile.py`. It installs the pinned fontTools and
  rebuilds every SVG in `assets/` deterministically. The build fails on a missing
  glyph or on text that overflows its box. Edit `COPY` in the script, never the SVGs.
- README.md and README-ja.md hold every essential fact as selectable text.
  Keep them in sync with each other.
- Optional follow-up: a contribution-based maze animation would need a new
  workflow, for example a third-party contribution-graph action. Until that
  exists, the snake stays labeled as a snake.
