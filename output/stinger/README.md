# Limit Break — Stinger Transition (OBS Browser Transition)

A brand-matched stinger built as a single self-contained HTML page, driven by
[Exeldro's **Browser Transition**](https://obsproject.com/forum/resources/browser-transition.1653/)
plugin for OBS Studio.

| File | What it is |
| --- | --- |
| `limit-break-stinger.html` | **Point OBS at this.** Self-contained — logo is embedded, no external files, no network. |
| `preview.gif` | What it looks like (640×360, scene A → scene B). |
| `stinger.src.html` | Editable source template (`__LOGO_DATA_URI__` placeholder). |
| `build.py` | Regenerates `limit-break-stinger.html` (and the logo) from the template. |
| `limit-break-logo.png` | Logo cropped/resized from `references/Limit Break Large.png`. |
| `limit-break-ff7.mp3` | Sound played when the logo lands. See **Impact sound** below. |

## The animation

1. Seven skewed neon shards sweep in from the right, staggered, cyan → magenta
   across the screen. Their leading edges glow in the brand gradient.
2. The synthwave backdrop fades up behind them — radial cyan/magenta glow,
   drifting grid, scanlines.
3. The logo slams in with motion blur, an overshoot settle, a chromatic
   (RGB-split) ghost that converges, a shockwave ring, speed streaks and a
   white impact flash.
4. **Screen is 100% opaque here — this is where OBS swaps the scene.**
5. The logo glitches and rips away to the left, and the shards continue their
   sweep off-screen, revealing the new scene.

## OBS setup

1. Install the **Browser Transition** plugin (OBS 28+).
2. `Scene Transitions` → `+` → **Browser Transition**, name it `Limit Break`.
3. In its properties:
   - **Local file** — tick it, and pick `limit-break-stinger.html`.
   - **Width / Height** — match your canvas (e.g. `1920` × `1080`).
   - **FPS** — 60 if your stream is 60fps, otherwise 30.
   - **Duration** — `1400` ms (recommended; anything 900–2000 works).
   - **Transition Point Type** — `Percentage`.
   - **Transition Point** — `50` %.
   - **Shutdown source when not visible** — leave **unticked**.
   - **Refresh browser when scene becomes active** — leave **unticked**.
   - **Control audio via OBS** — tick this, or the whoosh/impact never reaches
     the stream.
   - **Audio Volume** — the simplest loudness control for the whole stinger.
     **Audio Monitoring** decides whether you also hear it locally.
4. **Use a Track Matte** — leave **unticked**. This stinger covers the screen
   with real opaque pixels, so no matte is needed.

The page reads `duration` and `transitionPoint` straight off the plugin's
`transitionStart` event, so the animation always retimes itself to whatever you
set in step 3 — no need to edit the file.

### Verified coverage

At the transition point the page renders fully opaque (alpha = 255 on every
pixel), so the scene swap is never visible. The opaque window runs from
73% of the cover phase until 26% into the reveal phase — checked at both
50% and 25% transition points.

## Impact sound

Two whooshes (shards in, shards out) are synthesised with the Web Audio API and
need no files. The **impact** — the hit when the logo lands — is
`limit-break-ff7.mp3`, base64-embedded into the page so it stays a single
portable file.

To swap it for a different sound: drop the file in this folder and run
`python build.py`. It picks up `impact.<ext>`, or the only audio file present,
or whatever you name on the command line (`python build.py my-sound.wav`).
Supported: mp3, wav, ogg, m4a, aac, flac, webm. With no audio file at all it
falls back to a synthesised thud, and it does the same at runtime if decoding
ever fails — audio problems can't break the visuals.

The sample is decoded once at page load, and two things are measured off it so
any sound you drop in just works:

- **Peak normalisation.** The FF7 clip peaks at 0.072 (about −23 dBFS), which
  would be inaudible next to the whooshes, so it's scaled up 12.5× to sit at a
  consistent level. `impactVolume` is applied on top of that.
- **Lead-in compensation.** The clip has 157 ms of near-silence before its
  audible hit, so playback starts 157 ms early and the hit lands exactly on the
  logo impact frame instead of trailing it.

Tuning, without rebuilding:

- `?impactVolume=90` — sample level, % of the normalised level (0–400).
  Defaults to `75`.
- `?impactOffset=-60` — nudge the hit earlier/later, ms.
- `?impactAlign=0` — disable lead-in compensation; play the sample from its
  first sample.
- `?impact=synth` — ignore the sample, use the thud.

## Options (query string)

These can't go in the **Local file** picker — that's a file chooser and the
path won't resolve with `?...` on the end. Untick **Local file** and put a full
URL in the **URL** field instead (forward slashes):

```
file:///C:/Users/Christos/Documents/Software/git/limit-break-bgd/output/stinger/limit-break-stinger.html?volume=40
```

Refresh the browser cache after changing it.

| Param | Default | Meaning |
| --- | --- | --- |
| `sound` | `1` | `0` disables all audio. |
| `volume` | `60` | Master audio level, 0–100. |
| `impactVolume` | `75` | Impact sample level, % of the normalised level. |
| `impactOffset` | `0` | Shift the impact hit, ms (negative = earlier). |
| `impactAlign` | `1` | `0` disables automatic lead-in compensation. |
| `impact` | `auto` | `synth` forces the built-in thud even if a sample is embedded. |
| `duration` | `1400` | Fallback length in ms (only used if the plugin doesn't report one). |
| `tp` | `50` | Fallback transition point in %. |
| `preview` | – | `1` forces preview mode: mock scenes + auto-replay loop. |
| `autostart` | – | `1` plays once shortly after load. Only needed if you insist on reloading the source per transition. |

## Preview it without OBS

Open `limit-break-stinger.html` in a browser. It detects it isn't in OBS,
shows mock "SCENE A / SCENE B" backgrounds, and loops. Press **Space** to
replay. To check a specific timing:

```
limit-break-stinger.html?preview=1&duration=1000&tp=40
```

## Editing

Edit `stinger.src.html`, then:

```
python build.py
```

Timing is expressed entirely in fractions of two custom properties, so it
scales to any duration/transition point:

- `--in`  = `duration × transitionPoint` — the cover phase
- `--out` = `duration × (1 − transitionPoint)` — the reveal phase

Every animation is written as `calc(var(--in) * <fraction>)`. If you retime
something, keep the last shard landing before `--in` and the first shard
leaving after it, or the scene swap will show through.
