# Attendance Breakdown — OBS browser source

Animated 1920x1080 version of `output/ssbu-attendance-breakdown-1000x1000.png`.
Self-contained: the page only loads files from `assets/` (fonts, flags, logos, background), so the folder can be copied anywhere and works offline.

## OBS setup

1. Add a **Browser** source → tick **Local file** → pick `index.html`.
2. Width `1920`, height `1080`.
3. Tick **Refresh browser when scene becomes active** so the intro replays each time you cut to the scene.

## Options

Local files can't take a query string in OBS, so for these untick *Local file* and use a URL like
`file:///C:/path/to/attendance-breakdown/index.html?bg=0&loop=30`.

| param    | effect |
|----------|--------|
| `bg=0`   | transparent background, to layer over your own scene |
| `loop=N` | replay the intro every N seconds |
| `hold=1` | no intro, show the finished graphic |
| `t=N`    | freeze the intro at N seconds (preview / screenshots) |

## Timeline

~0.3s logos slide in → ~0.5s title glitches in → ~1.1s card rises → rows cascade in with bars growing and counts ticking up → ~2.8s totals bar. After ~4s it idles: shine runs along the bars and the title glitches every 6s.

## Editing

Change the numbers in the `ROWS` list in `index.html`. Rows are sorted by count, totals are summed automatically, and `HOME` (`cy`) gets the large top row. New countries need a matching `assets/flags/<code>.svg` (from the flag-icons set on jsDelivr: `https://cdn.jsdelivr.net/npm/flag-icons@7.2.3/flags/4x3/<code>.svg`).
