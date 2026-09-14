"""Inline assets into the stinger templates to produce self-contained files.

    python build.py

Reads : references/Limit Break Large.png  -> limit-break-logo.png (cropped/resized)
        petrolina/foamboard-check/petrolina-logo-print.png -> petrolina-logo.png (cropped/resized)
        saira-semi-condensed-800.woff2    (headline font, Perfect Game stinger)
        impact.mp3 / .wav / .ogg / .m4a   (optional impact sound, this folder)
        stinger.src.html, perfect-game.src.html (templates)
Writes: limit-break-stinger.html          (the standard transition)
        perfect-game-stinger.html         (SSBU 3-stock / perfect game transition)

Drop an audio file named `impact.<ext>` next to this script and re-run to swap
the synthesised thud for your own sample.
"""
import base64
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

SOURCE_LOGO = os.path.join(ROOT, "references", "Limit Break Large.png")
LOGO = os.path.join(HERE, "limit-break-logo.png")
SOURCE_SPONSOR = os.path.join(ROOT, "petrolina", "foamboard-check", "petrolina-logo-print.png")
SPONSOR = os.path.join(HERE, "petrolina-logo.png")
FONT = os.path.join(HERE, "saira-semi-condensed-800.woff2")

TARGETS = [
    ("stinger.src.html", "limit-break-stinger.html"),
    ("perfect-game.src.html", "perfect-game-stinger.html"),
]

LOGO_WIDTH = 1200  # plenty for a 1920-wide canvas, keeps the data URI small
SPONSOR_WIDTH = 900

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


def make_image(source, dest, width):
    from PIL import Image

    im = Image.open(source).convert("RGBA")
    im = im.crop(im.getbbox())  # strip the transparent margin
    w, h = im.size
    im = im.resize((width, round(h * width / w)), Image.LANCZOS)
    im.save(dest, optimize=True)
    return im.size


def data_uri(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())


def main():
    if not os.path.exists(LOGO):
        make_image(SOURCE_LOGO, LOGO, LOGO_WIDTH)
    if not os.path.exists(SPONSOR):
        make_image(SOURCE_SPONSOR, SPONSOR, SPONSOR_WIDTH)

    impact_uri, impact_path = find_impact()
    if impact_path:
        print("impact sound:", os.path.basename(impact_path),
              "(%.0f KB)" % (os.path.getsize(impact_path) / 1024))
    else:
        print("impact sound: none found - using the synthesised thud.")
        print("              drop impact.mp3 / .wav / .ogg / .m4a here and re-run.")

    values = {
        "__LOGO_DATA_URI__": lambda: data_uri(LOGO, "image/png"),
        "__SPONSOR_LOGO_URI__": lambda: data_uri(SPONSOR, "image/png"),
        "__FONT_URI__": lambda: data_uri(FONT, "font/woff2"),
        "__IMPACT_AUDIO_URI__": lambda: impact_uri,
    }

    for template, output in TARGETS:
        html = open(os.path.join(HERE, template), encoding="utf-8").read()
        assert "__LOGO_DATA_URI__" in html, template + ": logo placeholder missing"
        assert "__IMPACT_AUDIO_URI__" in html, template + ": impact placeholder missing"
        for key, value in values.items():
            if key in html:
                html = html.replace(key, value())
        leftover = re.findall(r"__[A-Z_]+_URI__", html)
        assert not leftover, template + ": unfilled placeholders " + ", ".join(set(leftover))

        out = os.path.join(HERE, output)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
