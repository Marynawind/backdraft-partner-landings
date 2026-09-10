#!/usr/bin/env python3
"""Cut the black ground off the Outlier line art.

`assets/source/` holds the files exactly as downloaded from the Outlier CDN:
brass line art drawn on a near-black panel. The page used to hide that panel
with `mix-blend-mode: screen`, which only works while the artwork sits on a
black backdrop and forbids any transform on a parent (a transform makes a
stacking context and the blend stops applying — the black square comes back).

The art is additive light on a flat ground, so screen blending has an exact
inverse: subtract the ground, take alpha from what is left, un-premultiply.
The result is a real transparent cut-out that renders identically on the dark
page, survives being animated, and would also work on a light background.

The drawing is one brass hue whose tonal variation lives entirely in the
alpha channel, so RGB is flattened to that hue — visually identical, and it
roughly halves the file because a constant colour plane costs nothing.

It also re-encodes the poster: the page is pasted into BigCommerce with every
image inlined as a data URI, and base64 costs another third on top, so the
poster is squeezed to the width the layout actually uses.

Needs Pillow. Run from partners/masterffl:  python3 tools-cutout.py
"""
from PIL import Image, ImageDraw
import poster_layout
import pathlib

FLOOR = 24      # brightness at or below this is backdrop, not ink
FULL  = 168     # brightness that counts as fully opaque brass

SRC = pathlib.Path(__file__).parent / "assets" / "source"
OUT = pathlib.Path(__file__).parent / "assets"
# step-2 also serves the hero, where it is shown at ~470 CSS px, so it stays big.
# The other three appear only in the reel at ~230 px and are squeezed hard: the
# alpha channel is what costs, and every kilobyte here becomes a third more
# after base64 inlining. Checked at display size — the alpha error stays under
# 3 levels, well below what the eye picks up.
HERO = "step-2-suppressor"
REEL = ["step-1-visit", "step-3-hub-adapter", "step-4-rebate-code"]
NAMES = [HERO] + REEL
REEL_W, REEL_Q, REEL_AQ = 440, 80, 70

# Инфографика идёт целиком, но четыре карточки с шагами из неё стёрты: те же
# шаги теперь живым текстом под картинкой, растром они не читались на телефоне
# и не попадали в поиск. Заливаем чёрным — после блендинга screen это ровно
# фон страницы.
POSTER = "redemption-infographic"
# Рамка снята замером по самим карточкам: рамки стоят на x=78 и x=1119,
# верхняя граница y=510, нижняя y=891. Берём с запасом в 2 px, иначе от
# карточек остаются куски рамок и обрывки букв — так и было до этой правки.
# Выше зоны декоративная линейка под подзаголовком (y≈486) — её сохраняем,
# ниже блок-сноска (с y=909) — его тоже.
POSTER_W = 1300   # колонка контента не шире 1112 px
POSTER_Q = 82
POSTER_BLACK = 16 # чёрная точка, см. ниже

# Низ инфографики перебран целиком: четыре карточки Outlier стёрты, на их месте
# шесть шагов клиента списком, под ними компактная полоса апгрейда со сноской.
# Раскладка и набор — в poster_layout.py.
STRIP = "upgrade-strip"


def cut(src: pathlib.Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    W, H = im.size
    out = Image.new("RGBA", (W, H))
    sp, op = im.load(), out.load()
    span = FULL - FLOOR
    for y in range(H):
        for x in range(W):
            r, g, b = sp[x, y]
            r = r - FLOOR if r > FLOOR else 0
            g = g - FLOOR if g > FLOOR else 0
            b = b - FLOOR if b > FLOOR else 0
            l = max(r, g, b)
            if not l:
                continue
            a = min(1.0, l / span)
            op[x, y] = (min(255, int(r / a + .5)), min(255, int(g / a + .5)),
                        min(255, int(b / a + .5)), int(a * 255 + .5))
    return out


def flatten(im: Image.Image) -> Image.Image:
    """Replace RGB with the average hue of the solid ink; alpha carries the drawing."""
    px, (W, H) = im.load(), im.size
    ink = [px[x, y][:3] for y in range(0, H, 3) for x in range(0, W, 3) if px[x, y][3] > 128]
    hue = tuple(sum(c[i] for c in ink) // len(ink) for i in range(3))
    flat = Image.new("RGBA", (W, H), hue + (0,))
    flat.putalpha(im.getchannel("A"))
    return flat, hue


if __name__ == "__main__":
    for name in NAMES:
        src, dst = SRC / f"{name}.webp", OUT / f"{name}.webp"
        flat, hue = flatten(cut(src))
        if name in REEL:
            flat = flat.resize((REEL_W, REEL_W), Image.LANCZOS)
            flat.save(dst, "WEBP", quality=REEL_Q, method=6, alpha_quality=REEL_AQ)
        else:
            flat.save(dst, "WEBP", quality=90, method=6, alpha_quality=100)
        print(f"{name:22} {src.stat().st_size/1024:5.1f} KB -> {dst.stat().st_size/1024:5.1f} KB"
              f"   {flat.size[0]}px  ink rgb{hue}")

    # The poster cannot be cut out the way the line art can: its dark tones are
    # content, not ground. The suppressor is a photographed dark object, the
    # step panels are barely lighter than the page, and the notice plate is
    # darker still — a brightness threshold eats 57% / 80% / 88% of them, and a
    # flood fill from the edges leaks straight into the product photo.
    #
    # So the black is dropped at render time instead, with mix-blend-mode:screen
    # (see .bdg-poster). Screen only cancels the ground exactly where the ground
    # is exactly black, so the black point is pulled down here first: without it
    # the poster keeps a faintly lighter rectangle over the page gradient.
    src, dst = SRC / f"{POSTER}.webp", OUT / f"{POSTER}.webp"
    im = Image.open(src).convert("RGB")
    im = poster_layout.compose(im, Image.open(SRC / f"{STRIP}.png").convert("RGB"))
    im = im.resize((POSTER_W, round(POSTER_W * im.size[1] / im.size[0])), Image.LANCZOS)
    scale = 255 / (255 - POSTER_BLACK)
    im = im.point(lambda v: min(255, round((v - POSTER_BLACK) * scale)) if v > POSTER_BLACK else 0)
    im.save(dst, "WEBP", quality=POSTER_Q, method=6)
    print(f"{POSTER:22} {src.stat().st_size/1024:5.1f} KB -> {dst.stat().st_size/1024:5.1f} KB   {im.size[0]}x{im.size[1]}, низ перебран")
