"""Inline the logo into stinger.src.html to produce a single self-contained file.

    python build.py

Reads : references/Limit Break Large.png  -> limit-break-logo.png (cropped/resized)
        impact.mp3 / .wav / .ogg / .m4a   (optional impact sound, this folder)
        stinger.src.html                  (template)
Writes: limit-break-stinger.html          (what you point OBS at)

Drop an audio file named `impact.<ext>` next to this script and re-run to swap
the synthesised thud for your own sample.
"""
import base64
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

SOURCE_LOGO = os.path.join(ROOT, "references", "Limit Break Large.png")
LOGO = os.path.join(HERE, "limit-break-logo.png")
TEMPLATE = os.path.join(HERE, "stinger.src.html")
OUTPUT = os.path.join(HERE, "limit-break-stinger.html")

LOGO_WIDTH = 1200  # plenty for a 1920-wide canvas, keeps the data URI small

MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
}


def audio_files():
    return [p for p in sorted(glob.glob(os.path.join(HERE, "*")))
            if os.path.splitext(p)[1].lower() in MIME]


def find_impact():
    """Locate the impact sound. Returns (data_uri, path), or ('', None).

    Priority: an explicit path on the command line, then `impact.<ext>`, then
    the only audio file in this folder if there happens to be exactly one.
    """
    path = None
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    found = audio_files()

    if args:
        path = args[0] if os.path.isabs(args[0]) else os.path.join(HERE, args[0])
        if not os.path.exists(path):
            raise SystemExit("no such audio file: " + path)
    else:
        named = [p for p in found
                 if os.path.splitext(os.path.basename(p))[0].lower() == "impact"]
        if named:
            path = named[0]
        elif len(found) == 1:
            path = found[0]
        elif len(found) > 1:
            raise SystemExit(
                "several audio files here, so I can't guess which is the impact:\n  "
                + "\n  ".join(os.path.basename(p) for p in found)
                + "\nPass one explicitly:  python build.py <filename>")

    if not path:
        return "", None
    ext = os.path.splitext(path)[1].lower()
    data = base64.b64encode(open(path, "rb").read()).decode()
    return "data:%s;base64,%s" % (MIME[ext], data), path


def make_logo():
    from PIL import Image

    im = Image.open(SOURCE_LOGO).convert("RGBA")
    im = im.crop(im.getbbox())  # strip the transparent margin
    w, h = im.size
    im = im.resize((LOGO_WIDTH, round(h * LOGO_WIDTH / w)), Image.LANCZOS)
    im.save(LOGO, optimize=True)
    return im.size


def main():
    if not os.path.exists(LOGO):
        make_logo()

    data = base64.b64encode(open(LOGO, "rb").read()).decode()
    html = open(TEMPLATE, encoding="utf-8").read()
    assert "__LOGO_DATA_URI__" in html, "template placeholder missing"
    html = html.replace("__LOGO_DATA_URI__", "data:image/png;base64," + data)

    impact_uri, impact_path = find_impact()
    assert "__IMPACT_AUDIO_URI__" in html, "impact placeholder missing"
    html = html.replace("__IMPACT_AUDIO_URI__", impact_uri)
    if impact_path:
        print("impact sound:", os.path.basename(impact_path),
              "(%.0f KB)" % (os.path.getsize(impact_path) / 1024))
    else:
        print("impact sound: none found - using the synthesised thud.")
        print("              drop impact.mp3 / .wav / .ogg / .m4a here and re-run.")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUTPUT, os.path.getsize(OUTPUT), "bytes")


if __name__ == "__main__":
    main()
