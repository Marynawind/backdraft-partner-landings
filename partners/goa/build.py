#!/usr/bin/env python3
"""Build the two output files from page.src.html.

BigCommerce integration is a copy-paste into the page's HTML source box, so the
page that ships has to be one self-contained file: markup, CSS and images all
in it, nothing to upload alongside. Every asset reference is therefore replaced
by a data URI.

Base64 costs a third on top of the file size, so page.src.html is written to
name each asset exactly once — the hero artwork is a CSS background rather than
an <img> precisely so the sheen mask can reuse the same custom property instead
of carrying a second copy of the same 58 KB.

Outputs:
  bigcommerce-page.html  paste this into BigCommerce
  preview.html           the same page plus a mock store header/footer

Stdlib only. Run from partners/goa:  python3 build.py
"""
import base64
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
PAGE = HERE / "page.src.html"
POSTER_MAP = HERE / "assets" / "poster-map.json"
LINK_MARKER = "<!--poster-links-->"
HEAD_MARKER = "POSTER_HEAD_RATIO"
HEAD_WIDTH_MARKER = "POSTER_HEAD_WIDTH"

PREVIEW_HEAD = """<title>GOA Member Rebate</title>
<style>
  body{margin:0;background:#fff;color:#333;font-family:Manrope,Helvetica,Arial,sans-serif;}
  .mock-note{background:#17181B;color:#B27B29;font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;padding:9px 20px;text-align:center;border-bottom:1px solid #26282D;}
  .mock-footer{border-top:1px solid #ebebeb;padding:26px 24px;text-align:center;font-size:13px;color:#989898;}
</style>
<div class="mock-note">Preview mock &mdash; the store header and footer are rendered by the BigCommerce theme</div>
"""
PREVIEW_FOOT = '<div class="mock-footer">&copy; 2026 Backdraft Suppressors &mdash; preview mock of the store footer</div>\n'


def poster(page: str) -> str:
    """Подставить всё, что зависит от раскладки инфографики.

    Карту пишет poster_layout.py при сборке картинки: доли рамок клика, высоту
    шапки для обрезки на узком экране и сам текст шагов. Текст сверяется с живым
    списком на странице — он показывается вместо картинки на узких экранах,
    и разъехаться эти два набора не должны.
    """
    if page.count(LINK_MARKER) != 1:
        raise SystemExit(f"{LINK_MARKER} must appear exactly once in page.src.html")
    for marker in (HEAD_MARKER, HEAD_WIDTH_MARKER):
        if page.count(marker) != 1:
            raise SystemExit(f"{marker} must appear exactly once in page.src.html")
    m = json.loads(POSTER_MAP.read_text(encoding="utf-8"))
    spots = m["links"]
    if not spots:
        raise SystemExit("poster-map.json has no links — run tools-cutout.py first")

    live = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", li))).strip()
            for li in re.findall(r"<li><p>(.*?)</p></li>", page, re.S)]
    baked = [s.replace("\u2033", '"') for s in m["steps"]]
    live_cmp = [s.replace("\u2033", '"') for s in live]
    if live_cmp != baked:
        pairs = [f"\n  картинка: {b}\n  страница: {l}"
                 for b, l in zip(baked, live_cmp + [""] * len(baked)) if b != l]
        raise SystemExit("шаги на странице разошлись с шагами в картинке:" + "".join(pairs))

    head = m["head"]
    page = page.replace(HEAD_MARKER, f'{head["w"]}/{head["h"]}')
    # картинка шире контейнера ровно настолько, чтобы правая часть с рендером
    # ушла за край: контейнер её обрезает
    page = page.replace(HEAD_WIDTH_MARKER, f'{head["w"] / head["right"] * 100:.3f}%')
    tags = "\n".join(
        '      <a class="bdg-hot" href="{href}" aria-label="{label}"'
        ' style="left:{left}%;top:{top}%;width:{width}%;height:{height}%"></a>'.format(
            href=s["href"], label=html.escape(s["label"], quote=True),
            left=s["left"], top=s["top"], width=s["width"], height=s["height"])
        for s in spots)
    print(f"  {len(spots)} ссылок поверх инфографики: "
          + ", ".join(s["label"] for s in spots)
          + f"; шаги на странице сверены с картинкой ({len(baked)})")
    return page.replace(LINK_MARKER, tags.strip())


def inline(page: str) -> str:
    """Replace every assets/… reference with the file's data URI."""
    refs = sorted(set(re.findall(r"assets/[\w.-]+\.webp", page)))
    if not refs:
        raise SystemExit("no asset references found — did the paths change?")
    for ref in refs:
        blob = (HERE / ref).read_bytes()
        uri = "data:image/webp;base64," + base64.b64encode(blob).decode()
        used = page.count(ref)
        if used > 1:
            raise SystemExit(
                f"{ref} is referenced {used} times; each extra copy adds "
                f"{len(uri)/1024:.0f} KB to the paste — reference it once")
        page = page.replace(ref, uri)
        print(f"  inlined {ref:38} {len(blob)/1024:5.1f} KB -> {len(uri)/1024:5.1f} KB base64")
    left = re.findall(r"assets/[\w.-]+\.webp", page)
    if left:
        raise SystemExit(f"an asset reference survived inlining: {left[0]}")
    return page


if __name__ == "__main__":
    standalone = inline(poster(PAGE.read_text(encoding="utf-8")))
    for name, body in (("bigcommerce-page.html", standalone),
                       ("preview.html", PREVIEW_HEAD + standalone + PREVIEW_FOOT)):
        out = HERE / name
        out.write_text(body, encoding="utf-8")
        print(f"{name:24} {out.stat().st_size/1024:6.1f} KB")
