# Prize Boards — Foamboard (Petrolina)

Giant prize boards for the winners' photo, themed after Petrolina's palette and
the motorsport look of the replay stinger. There are five variants.

**Name and amount are left blank on purpose. Fill them in by hand.**

| Variant | Size (design px) | What it is |
| --- | --- | --- |
| `card` | 1712 × 1080 | Credit-card layout like last year's board (`example/ecommbx card.jpg`), with a low-poly racing helmet on a chequered flag. |
| `card-no-helmet` | 1712 × 1080 | The same card without the helmet. The chequered flag sweeps across the right side instead. |
| `cheque` | 2400 × 1080 | Re-imagined as a real cheque: Petrolina-blue header, chequered-flag rule, guilloche security pattern. It has blank DATE, PAY TO THE ORDER OF, € amount box, THE SUM OF and AUTHORISED SIGNATURE fields. |
| `cheque-limit-break` | 2400 × 1080 | The same cheque, but the subtitle reads **LIMIT BREAK GAMING PRIZE**. It adds the Cyprus Comic Con and SmasCY logos (`assets/CCC Logo.png`, `assets/SmasCY Logo.png`) bottom left. The cheque-number line moves to the middle. |
| `cheque-limit-break-tekken` | 2400 × 1080 | Identical to `cheque-limit-break`, with the Tekken Cyprus logo (`assets/TekkenCY_Logo-1-TRSPRNT.png`) in place of SmasCY. |
| `cheque-ssbu-champion` / `-2nd` / `-3rd` | 2400 × 1080 | `cheque-limit-break`, filled in: "Super Smash Bros Ultimate - Champion" / "- 2nd Place" / "- 3rd Place", €500 / €300 / €200, dated 03/10/2026, signed "Petrolina". Cheque numbers 000001–000003. |
| `cheque-tekken-champion` / `-2nd` / `-3rd` | 2400 × 1080 | `cheque-limit-break-tekken`, filled in the same way for "Tekken 8", dated 04/10/2026. Cheque numbers 000004–000006. |

The six winner cheques also carry the print sponsor, Kemanes Print Shop (`assets/kemanes.png`), in the header beside the Petrolina logo with a PRINTED BY caption. The filled-in text is set in `WINNER_GAMES` / `WINNER_PLACES` in `build.py`. The signature uses Mrs Saint Delafield (`fonts/mrs-saint-delafield-400.woff2`, SIL OFL).

Each variant produces the following in `output/`:

| File | Use |
| --- | --- |
| `petrolina-<variant>-bleed.png` | **Send this to the printer.** Rectangular, 36 px bleed on every side. |
| `petrolina-<variant>.png` | Rounded corners, transparent outside. This is the cut shape/proof. |
| `petrolina-<variant>.pdf` | Vector version. The logo is the only raster in it. |

Render sizes: the cards are 6848 × 4320 (~174 dpi at 100 × 63 cm). The cheque is
7200 × 3240 (~183 dpi at 100 × 45 cm).

## Sources

| File | What it is |
| --- | --- |
| `card.src.html` | Card layout template (both card variants). |
| `cheque.src.html` | Cheque layout template. |
| `art.py` | Low-poly helmet and flag, plus the cheque's guilloche pattern. |
| `build.py` | Builds `petrolina-<variant>.html` and renders PNG/PDF with headless Chrome. |
| `fonts/` | Saira Semi Condensed 700/800, embedded so rendering doesn't depend on the network. |

## Logo

The only Petrolina logo in the repo is 492 px wide. `build.py` upscales it 6×
by re-thresholding the flat artwork, which gives crisp edges. Still, **ask
Petrolina for a vector logo (SVG/AI/EPS) before final print**. Then point the
`__LOGO__` image in the templates at the vector file.

## Rebuild

```
python build.py                  # every variant
python build.py cheque           # one variant
python build.py --html           # HTML only
```

Needs Python with Pillow + NumPy, and Chrome or Edge.
