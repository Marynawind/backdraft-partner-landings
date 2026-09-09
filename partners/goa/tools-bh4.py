#!/usr/bin/env python3
"""Заменить гравировку BP4 на BH4 на иллюстрациях Outlier.

Текст на картинках повёрнут вместе с корпусом глушителя, поэтому буква ищется
так: картинка выпрямляется поворотом, в выпрямленном виде OCR даёт бокс строки,
глифы разбираются на связные компоненты, второй по счёту — искомая «P».
Её четыре угла отображаются обратно в исходные координаты, и «H» рисуется уже
там, без поворота всей картинки — иначе размылся бы весь рисунок.

Штрихи рисуются с четырёхкратным суперсэмплингом: глиф всего 17x23 px, без
сглаживания края были бы ступенчатыми и заметно грубее соседних букв.

Запуск из partners/goa:  python3 tools-bh4.py
"""
from PIL import Image, ImageDraw, ImageFilter
from collections import deque
import math, pathlib, sys

SRC = pathlib.Path(__file__).parent / "assets" / "source"
SS = 4                      # кратность суперсэмплинга


def affine_to_rotated(size, angle):
    """Аффинное преобразование исходных координат в координаты повёрнутой
    картинки и обратно — снимается замерами, а не выводится из формул PIL."""
    W, H = size
    pts = [(W * .1, H * .1), (W * .9, H * .1), (W * .1, H * .9)]
    found = []
    for p in pts:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=255)
        r = m.rotate(angle, resample=Image.BILINEAR, expand=True, fillcolor=0)
        px = r.load(); tot = sx = sy = 0
        for y in range(r.size[1]):
            for x in range(r.size[0]):
                v = px[x, y]
                if v > 40: tot += v; sx += x*v; sy += y*v
        found.append((sx/tot, sy/tot))
    (x1,y1),(x2,y2),(x3,y3) = pts
    (u1,v1),(u2,v2),(u3,v3) = found
    den = (x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)
    a = ((u2-u1)*(y3-y1) - (u3-u1)*(y2-y1))/den
    b = ((u3-u1)*(x2-x1) - (u2-u1)*(x3-x1))/den
    c = u1 - a*x1 - b*y1
    d = ((v2-v1)*(y3-y1) - (v3-v1)*(y2-y1))/den
    e = ((v3-v1)*(x2-x1) - (v2-v1)*(x3-x1))/den
    f = v1 - d*x1 - e*y1
    det = a*e - b*d
    ia, ib = e/det, -b/det; ic = -(ia*c + ib*f)
    id_, ie = -d/det, a/det; if_ = -(id_*c + ie*f)
    return lambda u, v: (ia*u + ib*v + ic, id_*u + ie*v + if_)


def glyph_boxes(rot, box, thr):
    """Связные компоненты внутри бокса строки — по одному на глиф."""
    x, y, w, h = box; pad = 6
    c = rot.crop((x-pad, y-pad, x+w+pad, y+h+pad)); px = c.load(); cw, ch = c.size
    seen = [[0]*cw for _ in range(ch)]; comps = []
    for j in range(ch):
        for i in range(cw):
            if max(px[i, j]) > thr and not seen[j][i]:
                q = deque([(i, j)]); seen[j][i] = 1; pts = []
                while q:
                    a, b = q.popleft(); pts.append((a, b))
                    for da, db in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                        na, nb = a+da, b+db
                        if 0 <= na < cw and 0 <= nb < ch and max(px[na, nb]) > thr and not seen[nb][na]:
                            seen[nb][na] = 1; q.append((na, nb))
                if len(pts) > 12: comps.append(pts)
    comps.sort(key=lambda p: min(a for a, _ in p))
    out = []
    for p in comps:
        xs = [a for a, _ in p]; ys = [b for _, b in p]
        out.append((x-pad+min(xs), y-pad+min(ys), max(xs)-min(xs)+1, max(ys)-min(ys)+1))
    return out


def draw_h(im, quad, ink, bg, stroke, margin=2.0):
    """Стереть букву и нарисовать на её месте H тремя штрихами."""
    (ox, oy), (ax, ay), _, (dx, dy) = quad
    ux, uy = ax-ox, ay-oy;  wl = math.hypot(ux, uy); ux, uy = ux/wl, uy/wl
    vx, vy = dx-ox, dy-oy;  hl = math.hypot(vx, vy); vx, vy = vx/hl, vy/hl

    def P(a, b, s=1):        # буквенные координаты -> координаты картинки
        return ((ox + ux*a + vx*b)*s, (oy + uy*a + vy*b)*s)

    # стереть: заливаем прямоугольник фоном. Запас по краям нужен, чтобы
    # не осталось ореола, но на мелком тексте буквы стоят вплотную и запас
    # съедает соседнюю цифру — поэтому он настраивается.
    m = -margin
    erase = [P(m, m), P(wl-m, m), P(wl-m, hl-m), P(m, hl-m)]
    ImageDraw.Draw(im).polygon(erase, fill=bg)

    # нарисовать H на увеличенном слое и вернуть с даунскейлом — ради сглаживания
    W, H = im.size
    lay = Image.new("RGBA", (W*SS, H*SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = stroke
    bars = [(0, 0, s, hl),                       # левая стойка
            (wl-s, 0, wl, hl),                   # правая стойка
            (0, (hl-s)/2, wl, (hl+s)/2)]         # перекладина
    for a0, b0, a1, b1 in bars:
        d.polygon([P(a0, b0, SS), P(a1, b0, SS), P(a1, b1, SS), P(a0, b1, SS)],
                  fill=ink + (255,))
    lay = lay.resize((W, H), Image.LANCZOS)
    lay = lay.filter(ImageFilter.GaussianBlur(0.5))   # смягчить под соседние буквы
    im.paste(Image.new("RGB", im.size, ink), (0, 0), lay.getchannel("A"))
    return im


def patch(name, angle, ocr_box, thr=70, glyph_box=None, margin=2.0, region=None):
    """region — работать не со всей картинкой, а с её куском. Нужно для мелких
    надписей: на полном размере OCR их не разрешает, а в вырезе — да, и заодно
    координаты остаются маленькими."""
    src = SRC / f"{name}.webp"
    full = Image.open(src).convert("RGB")
    im = full.crop(region) if region else full
    inv = affine_to_rotated(im.size, angle)
    rot = im.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0))
    if glyph_box:
        # на мелком тексте «B» и «P» слипаются в один компонент, и второй по
        # счёту оказывается уже цифрой — тогда бокс буквы задаётся руками
        gx, gy, gw, gh = glyph_box
    else:
        boxes = glyph_boxes(rot, ocr_box, thr)
        if len(boxes) < 2:
            sys.exit(f"{name}: глифы не разобрались, найдено {len(boxes)}")
        gx, gy, gw, gh = boxes[1]                # второй глиф — это «P»
    quad = [inv(gx, gy), inv(gx+gw, gy), inv(gx+gw, gy+gh), inv(gx, gy+gh)]

    rp = rot.load()
    # цвет штриха берём как медиану самых ярких 40% пикселей глифа, а не по
    # фиксированному порогу: на мелких надписях чернила заметно темнее, и
    # жёсткий порог не находил ни одного пикселя
    cell = [rp[x, y] for y in range(gy, gy+gh) for x in range(gx, gx+gw)]
    cell.sort(key=max, reverse=True)
    ink_px = cell[:max(4, len(cell)*2//5)]
    ring = [rp[x, y] for y in range(gy-8, gy-3) for x in range(gx-4, gx+gw+4) if max(rp[x, y]) <= thr]
    ink = tuple(sorted(c[i] for c in ink_px)[len(ink_px)//2] for i in range(3))
    bg = tuple(sorted(c[i] for c in ring)[len(ring)//2] for i in range(3)) if ring else (0, 0, 0)

    # доля ширины глифа. Жёсткого минимума быть не должно: на глифе 5x5
    # штрих в 3 px превращает букву в сплошное пятно
    stroke = max(1.0, round(gw * 0.30, 1))
    print(f"{name}: глиф {gw}x{gh}, штрих {stroke}, чернила {ink}, фон {bg}")
    out = draw_h(im, quad, ink, bg, stroke, margin)
    if region:
        full.paste(out, region[:2]); out = full
    out.save(src, "WEBP", quality=95, method=6)
    return src




def patch_flat(name, ocr_box, thr=110, quality=92):
    """Вариант для горизонтального текста на фотореалистичном рендере.

    Здесь фон нельзя заливать одним цветом: вдоль надписи идёт блик, яркость
    гуляет втрое. Поэтому он восстанавливается по столбцам — для каждого
    столбца берутся полосы над и под буквой и линейно интерполируются сквозь
    неё. Так сохраняется и горизонтальный градиент блика, и вертикальная
    затенённость корпуса."""
    src = SRC / f"{name}.webp"
    im = Image.open(src).convert("RGB")
    boxes = glyph_boxes(im, ocr_box, thr)
    if len(boxes) < 2:
        sys.exit(f"{name}: глифы не разобрались, найдено {len(boxes)}")
    gx, gy, gw, gh = boxes[1]
    px = im.load()

    ink_px = [px[x, y] for y in range(gy, gy+gh) for x in range(gx, gx+gw) if max(px[x, y]) > 140]
    ink = tuple(sorted(c[i] for c in ink_px)[len(ink_px)//2] for i in range(3))

    pad = 3
    x0, x1 = gx-pad, gx+gw+pad
    y0, y1 = gy-pad, gy+gh+pad
    band = 5
    for x in range(x0, x1):
        top = [px[x, y] for y in range(y0-band, y0)]
        bot = [px[x, y] for y in range(y1, y1+band)]
        ct = tuple(sum(c[i] for c in top)//len(top) for i in range(3))
        cb = tuple(sum(c[i] for c in bot)//len(bot) for i in range(3))
        for y in range(y0, y1):
            t = (y - y0) / (y1 - y0 - 1)
            px[x, y] = tuple(round(ct[i] + (cb[i]-ct[i])*t) for i in range(3))

    quad = [(gx, gy), (gx+gw, gy), (gx+gw, gy+gh), (gx, gy+gh)]
    stroke = max(3.0, round(gw * 0.26, 1))
    print(f"{name}: глиф {gw}x{gh}, штрих {stroke}, чернила {ink}, фон восстановлен интерполяцией")

    W, H = im.size
    lay = Image.new("RGBA", (W*SS, H*SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay); s = stroke
    for a0, b0, a1, b1 in [(0, 0, s, gh), (gw-s, 0, gw, gh), (0, (gh-s)/2, gw, (gh+s)/2)]:
        d.rectangle([(gx+a0)*SS, (gy+b0)*SS, (gx+a1)*SS, (gy+b1)*SS], fill=ink + (255,))
    lay = lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.4))
    im.paste(Image.new("RGB", im.size, ink), (0, 0), lay.getchannel("A"))
    im.save(src, "WEBP", quality=quality, method=6)

if __name__ == "__main__":
    patch("step-2-suppressor", 44, (616, 598, 171, 33))
    patch_flat("redemption-infographic", (1230, 390, 160, 29))
    # на странице сейчас не используется, но набор ассетов держим согласованным
    patch("step-4-rebate-code", -10, (553, 438, 114, 24), glyph_box=(568, 439, 12, 17), margin=0.3)
    # вторая, мелкая гравировка на инфографике — в карточке шага 2. Буквы там
    # по 4-5 px: на странице это ~4 px высотой и глазом не читается, правится
    # ради согласованности ассета, а не ради того, что увидит посетитель.
    patch("redemption-infographic", -90, (43, 58, 46, 11), thr=60,
          glyph_box=(48, 61, 5, 5), margin=0.2, region=(440, 560, 580, 700))
