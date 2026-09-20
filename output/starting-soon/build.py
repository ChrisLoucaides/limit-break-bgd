"""Inline the headline font into the template to produce a self-contained page.

    python build.py

Reads : saira-semi-condensed-800.woff2   (headline font)
        starting-soon.src.html           (template)
Writes: starting-soon.html               (point OBS at this)
"""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

FONT = os.path.join(HERE, "saira-semi-condensed-800.woff2")
TEMPLATE = os.path.join(HERE, "starting-soon.src.html")
OUTPUT = os.path.join(HERE, "starting-soon.html")


def data_uri(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())


def main():
    html = open(TEMPLATE, encoding="utf-8").read()
    assert "__FONT_URI__" in html, "font placeholder missing"
    html = html.replace("__FONT_URI__", data_uri(FONT, "font/woff2"))

    leftover = re.findall(r"__[A-Z_]+_URI__", html)
    assert not leftover, "unfilled placeholders " + ", ".join(set(leftover))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUTPUT, os.path.getsize(OUTPUT), "bytes")


if __name__ == "__main__":
    main()
