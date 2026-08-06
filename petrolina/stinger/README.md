# Instant Replay — Stinger Transition (Powered by Petrolina)

A motorsport-themed replay stinger for the
[Browser Transition](https://obsproject.com/forum/resources/browser-transition.1653/)
plugin, carrying Petrolina sponsor branding.

| File | What it is |
| --- | --- |
| `instant-replay-stinger.html` | **Point OBS at this.** Self-contained — logo embedded, no external files, no network. |
| `preview.gif` | What it looks like (640×360, scene A → scene B). |
| `stinger.src.html` | Editable source template. |
| `build.py` | Regenerates `instant-replay-stinger.html` from the template. |
| `petrolina-logo.png` | Trimmed/resized from `../petrolina-logo.png`. |

## Branding

Palette taken from the supplied logo and petrolina.com.cy's own stylesheet:

| | Hex | Used for |
| --- | --- | --- |
| Logo blue | `#00529B` | Racing stripes, band edges |
| Accent | `#009CDE` | Replay arrow, leading edges, glows, speed marks |
| Deep blue | `#003087` | Headline underglow |
| White | `#FFFFFF` | Headline, checkered flag, stripes |
| Base | `#04101F` | Track surface |

`#009CDE` and `#003087` are the two dominant custom colours in their site CSS;
`#00529B` is sampled from the logo artwork itself.

Racing treatment: horizontal speed bands sweeping the frame, scrolling
checkered-flag strips top and bottom, raked racing stripes, motion streaks, and
slanted speed marks in the rule. The whole frame is tilted ~2.4° so nothing
sits on a level horizon.

## The animation

1. Six speed bands whip in from the right, staggered top to bottom, each with a
   bright leading edge and internal motion streaks.
2. Track dressing fades up — blue glow, racing stripes, checkered flag strips
   scrolling in opposite directions top and bottom.
3. The lockup rises into place, element by element: anticlockwise replay arrow
   (spins in and draws its stroke round), **INSTANT REPLAY**, speed-mark rule,
   **POWERED BY**, Petrolina logo. A white flash hits as the headline lands.
4. **Screen is 100% opaque here — this is where OBS swaps the scene.**
5. The lockup blurs away left and the bands continue their sweep off-screen,
   revealing the replay.

## OBS setup

1. `Scene Transitions` → `+` → **Browser Transition**, name it `Instant Replay`.
2. Properties:
   - **Local file** — tick it, pick `instant-replay-stinger.html`.
   - **Width / Height** — match your canvas (e.g. `1920` × `1080`).
   - **FPS** — 60 if your stream is 60fps, otherwise 30.
   - **Duration** — `1400` ms. This one carries a sponsor logo, so consider
     `1800`–`2200` to give it more dwell time on screen.
   - **Transition Point Type** — `Percentage`, **Transition Point** — `50`%.
   - **Shutdown source when not visible** — leave **unticked**.
   - **Control audio via OBS** — tick it, or the audio never reaches the stream.
     **Audio Volume** is the simplest loudness control.
3. **Use a Track Matte** — leave **unticked**; the page covers with real opaque
   pixels.

Because it's a transition rather than a scene, trigger it by switching to your
replay scene with this transition selected — a transition override on the
replay scene is the usual way to wire that up.

### Verified coverage

Fully opaque (alpha 255 on every pixel) across the swap window, checked at both
50% and 25% transition points. The opaque window runs from ~74% of the cover
phase to ~26% into the reveal phase, so the scene swap is never visible.

## Audio

Two whooshes only — one as the bands sweep in, one as they sweep out —
synthesised with the Web Audio API, no files needed. **There is no impact
sound**; nothing hits when the headline lands.

If you ever want one, drop an audio file in this folder and run
`python build.py`. It picks up `impact.<ext>`, the only audio file present, or
whatever you name on the command line (`python build.py my-sound.wav`), and
embeds it. The sample is peak-normalised and its lead-in silence measured, so
the hit lands on the headline regardless of how the file was mastered. With no
file embedded, no impact plays at all.

## Options (query string)

These can't go in the **Local file** picker. Untick **Local file** and use the
**URL** field with a full `file:///` URL (forward slashes):

```
file:///C:/Users/Christos/Documents/Software/git/limit-break-bgd/petrolina/stinger/instant-replay-stinger.html?volume=40
```

| Param | Default | Meaning |
| --- | --- | --- |
| `sound` | `1` | `0` disables all audio. |
| `volume` | `60` | Master audio level, 0–100. |
| `impactVolume` | `75` | Impact level, % of the normalised level. Only applies if you've embedded a sample. |
| `impactOffset` | `0` | Shift the impact hit, ms (negative = earlier). |
| `impactAlign` | `1` | `0` disables automatic lead-in compensation. |
| `impact` | `auto` | `off` silences an embedded impact sample. |
| `duration` | `1400` | Fallback length in ms if the plugin doesn't report one. |
| `tp` | `50` | Fallback transition point, %. |
| `preview` | – | `1` forces preview mode: mock scenes + auto-replay loop. |
| `autostart` | – | `1` plays once shortly after load. |

## Preview without OBS

Open `instant-replay-stinger.html` in a browser — it detects it isn't in OBS,
shows mock scenes and loops. **Space** replays.

## Editing

Edit `stinger.src.html`, then `python build.py`.

Timing is expressed in fractions of `--in` (`duration × transitionPoint`) and
`--out` (`duration × (1 − transitionPoint)`), so it scales to any duration and
transition point. If you retime anything, keep the last band landing before
`--in` and the first band leaving after it, or the swap will show through.

**Fonts:** the headline uses `Arial Black` with `Segoe UI Black`, `Arial Bold`
and `Impact` as fallbacks — all standard on Windows. Nothing is downloaded, so
it renders identically offline.
