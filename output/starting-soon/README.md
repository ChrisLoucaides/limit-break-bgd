# Limit Break — "Stream Starting Soon" (OBS Browser source)

The headline block from the starting-soon key art, rebuilt as a live overlay:
white **STREAM / STARTING / SOON** in the brand's heavy oblique condensed, with
a counting-down clock next to it in the logo's cyan → magenta gradient.

| File | What it is |
| --- | --- |
| `starting-soon.html` | **Point OBS at this.** Self-contained — font embedded, no external files, no network. |
| `top-starting-soon.html` | The same overlay reading **TOP 8 / STARTING / SOON**. Hand-kept copy, not produced by `build.py`. |
| `thanks-for-watching.html` | Two-line **THANKS FOR / WATCHING** outro, no clock. Hand-kept copy too. |
| `starting-soon.src.html` | Editable source template (`__FONT_URI__` placeholder). |
| `build.py` | Regenerates `starting-soon.html` from the template. |
| `saira-semi-condensed-800.woff2` | The headline font, embedded into the build. |

The background is **transparent**, so drop it on top of your scene art (the
FF7/petrolina still, a looping video, whatever) rather than replacing it.

## OBS setup

1. `Sources` → `+` → **Browser**.
2. **Local file** — tick it, pick `starting-soon.html`.
3. **Width / Height** — match your canvas, e.g. `1920` × `1080`.
4. Leave *Shutdown source when not visible* **off** and
   *Refresh browser when scene becomes active* **on** if you want the 10-minute
   countdown to restart every time you switch to the starting-soon scene.
   (Or use `?persist=1`, below, to have it survive a refresh.)

To pass options, put them after the filename in the **URL** field instead of
using Local file:

```
file:///C:/Users/Christos/Documents/Software/git/limit-break-bgd/output/starting-soon/starting-soon.html?m=15&after=Now
```

## Options

All optional, all query-string:

| Param | Default | What it does |
| --- | --- | --- |
| `m` | `10` | Minutes on the clock. |
| `s` | `0` | Extra seconds on top of `m`. |
| `at` | — | Count down to a wall-clock time instead, `?at=19:30` (24h, rolls to tomorrow if already past). |
| `after` | — | What the clock shows at zero, e.g. `?after=Now`. Without it, it rests on `00:00`. |
| `persist` | `0` | `1` keeps the deadline across a browser-source refresh instead of restarting. Add `&reset=1` once to force a fresh start. |
| `text` | `Stream Starting Soon` | Headline, up to three lines. With no separator it is one word per line (`?text=Back%20In%20A%20Bit` → *Back / In / A*). Use `|` or `/` to put more than one word on a line: `?text=Top%208|Starting|Soon`. Extra lines are dropped; two lines hides the third. |
| `size` | `1` | Overall scale multiplier, e.g. `?size=0.8`. |
| `x` | `8` | Left margin, % of width. |
| `y` | `50` | Vertical centre of the block, % of height. |
| `skew` | `-9` | Oblique angle in degrees; `?skew=0` for upright. |
| `tilt` | `-2.2` | Anticlockwise lift of the whole block, in degrees; `?tilt=0` for level. |
| `indent` | `0.26` | How far line 2 (*STARTING*) sits right of the others, in em. |
| `gap` | `0.15` | Space between *SOON* and the clock, in em of the clock. |
| `lift` | `0.7` | How far the clock sits above the *SOON* baseline, in em. |
| `grad` | `-45` | Angle of the clock's gradient, in degrees (CSS: 0 = up, 90 = right). `?grad=135` runs cyan → magenta the other way. |
| `frame` | `0` | `1` draws the thin gradient inset frame from the key art. |

Over an hour the clock switches to `H:MM:SS` on its own.

## Notes

- Sizing is proportional to a 16:9 box fitted to the source, so the layout holds
  at any browser-source resolution — no re-tuning between 1920×1080 and 1280×720.
- The oblique is a CSS skew: Saira SemiCondensed ships no italic, and the key art's
  slant is a faux-italic too. On top of it the block is rotated ~2° anticlockwise,
  and the dark edge is an 8-way outline plus an offset hard shadow (`--outline`,
  `--dx`, `--dy` at the top of the source).
- Colours come straight from `brand-guidelines.css` — cyan `#00D4FF`,
  magenta `#EE00CC`.
- Edit `starting-soon.src.html`, then `python build.py` to regenerate. Don't edit
  `starting-soon.html` by hand; it is overwritten.
