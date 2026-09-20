"""Build and render the Petrolina foamboard prize boards.

    python build.py                 # build + render every variant
    python build.py cheque          # just the named variant(s)
    python build.py --html          # build HTML only, no rendering

Variants
    card            credit-card board with the low-poly helmet and flag
    card-no-helmet  same card, flag only
    cheque          re-imagined as a giant cheque
    cheque-limit-break  cheque with "LIMIT BREAK GAMING PRIZE" + Cyprus Comic Con and SmasCY logos
    cheque-limit-break-tekken  same, with the Tekken Cyprus logo in place of SmasCY

Reads : card.src.html, cheque.src.html, art.py, fonts/*.woff2, ../petrolina-logo.png,
        ../../assets/CCC Logo.png, SmasCY Logo.png, TekkenCY_Logo-1-TRSPRNT.png
Writes: petrolina-<variant>.html                self-contained, open in a browser
        output/petrolina-<variant>.png          rounded corners, transparent outside
        output/petrolina-<variant>-bleed.png    rectangular with bleed, for the printer
        output/petrolina-<variant>.pdf          vector (logo is the only raster)
        petrolina-logo-print.png                logo upscaled for print
"""
import base64
import os
import subprocess
import sys

import art

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
SOURCE_LOGO = os.path.join(HERE, "..", "petrolina-logo.png")
PRINT_LOGO = os.path.join(HERE, "petrolina-logo-print.png")
ASSETS = os.path.join(HERE, "..", "..", "assets")

BLEED = 36  # design px, matches body.bleed in the templates
LOGO_UPSCALE = 6

# name: (template, width, height, render scale, placeholder -> content factory)
VARIANTS = {
    "card": ("card.src.html", 1712, 1080, 4, {"__ART_SVG__": lambda: art.art_svg(helmet=True)}),
    "card-no-helmet": ("card.src.html", 1712, 1080, 4, {"__ART_SVG__": lambda: art.art_svg(helmet=False)}),
    "cheque": ("cheque.src.html", 2400, 1080, 3, {
        "__GUILLOCHE__": lambda: art.guilloche_svg(2400, 1080),
        "__SUBTITLE__": lambda: "OFFICIAL TOURNAMENT PRIZE",
        "__PARTNERS__": lambda: "",
    }),
    "cheque-limit-break": ("cheque.src.html", 2400, 1080, 3, {
        "__GUILLOCHE__": lambda: art.guilloche_svg(2400, 1080),
        "__SUBTITLE__": lambda: "LIMIT BREAK GAMING PRIZE",
        "__PARTNERS__": lambda: partners_html("SmasCY Logo.png", "smascy", "SmasCY"),
    }),
    "cheque-limit-break-tekken": ("cheque.src.html", 2400, 1080, 3, {
        "__GUILLOCHE__": lambda: art.guilloche_svg(2400, 1080),
        "__SUBTITLE__": lambda: "LIMIT BREAK GAMING PRIZE",
        "__PARTNERS__": lambda: partners_html("TekkenCY_Logo-1-TRSPRNT.png", "tekkency", "Tekken Cyprus"),
    }),
}

# Filled-in winner cheques: (game key, base variant, game name, date)
WINNER_GAMES = [
    ("ssbu", "cheque-limit-break", "Super Smash Bros Ultimate", "03/10/2026"),
    ("tekken", "cheque-limit-break-tekken", "Tekken 8", "04/10/2026"),
]
# (place key, payee suffix, amount, amount in words)
WINNER_PLACES = [
    ("champion", "Champion", "500", "Five Hundred Euros"),
    ("2nd", "2nd Place", "300", "Three Hundred Euros"),
    ("3rd", "3rd Place", "200", "Two Hundred Euros"),
]
_cheque_no = 0
for _game, _base, _name, _date in WINNER_GAMES:
    for _place, _suffix, _amount, _words in WINNER_PLACES:
        _cheque_no += 1
        _t, _w, _h, _s, _parts = VARIANTS[_base]
        VARIANTS["cheque-%s-%s" % (_game, _place)] = (_t, _w, _h, _s, dict(
            _parts,
            __CHEQUE_NO__=lambda n=_cheque_no: "%06d" % n,
            __PRINT_SPONSOR__=lambda: print_sponsor_html("kemanes.png", "Kemanes Print Shop"),
            __FILL__=lambda d=_date, p="%s - %s" % (_name, _suffix), a=_amount, w=_words: fill_html(d, p, a, w),
        ))


def print_sponsor_html(filename, alt):
    """Print-shop sponsor logo with a PRINTED BY caption, in the header beside the Petrolina logo."""
    return ('<div class="print-sponsor"><div class="divider"></div><div class="cap">PRINTED<br>BY</div>'
            '<img src="%s" alt="%s"></div>') % (asset_logo(filename), alt)


def fill_html(date, payee, amount, words, signature="Petrolina"):
    """Date, payee, amount and signature written onto the blank cheque fields."""
    from html import escape
    return (
        '<div class="fill v-date">%s</div>'
        '<div class="fill v-pay">%s</div>'
        '<div class="fill v-amount">%s</div>'
        '<div class="fill v-sum">%s</div>'
        '<div class="fill v-sig">%s</div>'
    ) % tuple(escape(v) for v in (date, payee, amount, words, signature))


def partners_html(second_file, second_class, second_alt):
    """Cyprus Comic Con plus one community logo, bottom left of the cheque."""
    return (
        '<div class="partners">'
        '<img class="ccc" src="%s" alt="Cyprus Comic Con">'
        '<div class="divider"></div>'
        '<img class="%s" src="%s" alt="%s">'
        '</div>'
        '<script>document.querySelector(".cheque").classList.add("has-partners", "with-%s");</script>'
    ) % (asset_logo("CCC Logo.png"), second_class, asset_logo(second_file), second_alt, second_class)

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

BLUE = (0x00, 0x52, 0x9B)


def make_print_logo():
    """The only logo we have is 492 px wide. It's flat two-colour artwork
    (Petrolina blue on white), so upscale the coverage masks and re-threshold
    them: edges come out crisp instead of blurry."""
    import numpy as np
    from PIL import Image

    im = Image.open(SOURCE_LOGO).convert("RGBA")
    im = im.crop(im.getbbox())
    arr = np.asarray(im).astype(np.float32) / 255.0
    alpha = arr[..., 3]
    # 0 = white, 1 = blue. Fully transparent pixels count as blue so the outer
    # outline doesn't pick up a white fringe.
    blue = np.where(alpha > 0.02, 1.0 - arr[..., 0], 1.0)

    w, h = im.size
    size = (w * LOGO_UPSCALE, h * LOGO_UPSCALE)

    def up(ch):
        img = Image.fromarray((ch * 255).astype(np.uint8), "L").resize(size, Image.LANCZOS)
        v = np.asarray(img).astype(np.float32) / 255.0
        # ~1.5 output px anti-aliasing ramp
        return np.clip((v - 0.5) * (LOGO_UPSCALE / 1.5) + 0.5, 0, 1)

    a2 = up(alpha)
    b2 = up(blue)
    rgb = np.empty((size[1], size[0], 3), np.float32)
    for i, c in enumerate(BLUE):
        rgb[..., i] = 255 + (c - 255) * b2
    out = np.dstack([rgb, a2 * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(PRINT_LOGO, optimize=True)
    return PRINT_LOGO


def asset_logo(filename, max_height=900):
    """Trim a transparent logo from /assets and embed it as a PNG data URI."""
    from io import BytesIO
    from PIL import Image

    im = Image.open(os.path.join(ASSETS, filename)).convert("RGBA")
    # trim by alpha only: invisible pixels can still carry colour and fool getbbox()
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    if im.height > max_height:
        im = im.resize((round(im.width * max_height / im.height), max_height), Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def data_uri(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode("ascii"))


def build_html(name, logo_uri, fonts):
    template, _, _, _, parts = VARIANTS[name]
    with open(os.path.join(HERE, template), encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__FONT_800__", fonts[800]).replace("__FONT_700__", fonts[700])
    html = html.replace("__FONT_SIG__", fonts["sig"])
    html = html.replace("__LOGO__", logo_uri)
    for key, make in parts.items():
        html = html.replace(key, make())
    html = html.replace("__FILL__", "")  # blank variants: fields left for handwriting
    html = html.replace("__CHEQUE_NO__", "000001")
    html = html.replace("__PRINT_SPONSOR__", "")
    path = os.path.join(HERE, "petrolina-%s.html" % name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", os.path.relpath(path, HERE))
    return path


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    sys.exit("Chrome/Edge not found - open the HTML and export manually.")


def render(name, html):
    _, w, h, scale, _ = VARIANTS[name]
    os.makedirs(OUT, exist_ok=True)
    url = "file:///" + html.replace("\\", "/")
    exe = chrome()
    common = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
              "--force-device-scale-factor=%d" % scale, "--default-background-color=00000000",
              "--virtual-time-budget=4000"]

    jobs = [
        ("petrolina-%s.png" % name, url, w, h),
        # bleed mode is switched on by the hash; the page reads it on load
        ("petrolina-%s-bleed.png" % name, url + "#bleed", w + 2 * BLEED, h + 2 * BLEED),
    ]
    for fname, page, ww, hh in jobs:
        target = os.path.join(OUT, fname)
        subprocess.run(common + ["--window-size=%d,%d" % (ww, hh), "--screenshot=" + target, page],
                       check=True, capture_output=True)
        print("wrote", os.path.relpath(target, HERE))

    pdf = os.path.join(OUT, "petrolina-%s.pdf" % name)
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=4000", "--print-to-pdf=" + pdf, url],
                   check=True, capture_output=True)
    print("wrote", os.path.relpath(pdf, HERE))


if __name__ == "__main__":
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")] or list(VARIANTS)
    for n in wanted:
        if n not in VARIANTS:
            sys.exit("unknown variant %r (choose from %s)" % (n, ", ".join(VARIANTS)))

    logo = data_uri(make_print_logo(), "image/png")
    fonts = {wt: data_uri(os.path.join(HERE, "fonts", "saira-semi-condensed-%d.woff2" % wt), "font/woff2")
             for wt in (700, 800)}
    fonts["sig"] = data_uri(os.path.join(HERE, "fonts", "mrs-saint-delafield-400.woff2"), "font/woff2")
    for n in wanted:
        page = build_html(n, logo, fonts)
        if "--html" not in sys.argv:
            render(n, page)
