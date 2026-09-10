"""Правит размеры глушителей на полосе Outlier «Want more performance».

Клиент прислал полосу скриншотом (`reference/2026-09-09-outlier-upgrade-strip.jpg`)
и попросил заменить «5" or 6"» на «4" or 6" or 8"». Исходника вёрстки нет,
править приходится растр.

В две строки новый текст не влезает: он длиннее прежнего примерно на шесть
знаков, а справа в 22 px стоит разделитель колонок. Поэтому левая колонка
переливается в три строки — ровно столько же, сколько в правой.

Слова не перерисовываются, а переносятся кусками пикселей: фон полосы плоский
(медиана 2-3 из 255), поэтому блок вместе со своим фоном садится на новое место
без шва, и каждое слово остаётся оригинальным. Заново рисуются только «4» и «8» —
этих цифр в картинке нет. Шрифт для них подобран перебором: у кандидата
сравнивались с оригиналом «5» и «6», Helvetica совпала по габаритам глифа
(14×20 px) и по форме.

Запускать из partners/masterffl:  python3 tools-upgrade-strip.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "reference" / "2026-09-09-outlier-upgrade-strip.jpg"
DST = HERE / "assets" / "source" / "upgrade-strip.png"

FONT, FONT_INDEX = "/System/Library/Fonts/Helvetica.ttc", 0
SIZE, SS, BLUR = 25.0, 4, 0.55   # кегль подобран по «5» и «6» из самой картинки
INK = (216, 216, 218)            # цвет текста полосы

LEAD = 31        # межстрочный шаг
LEFT = 138       # левое поле текста
GAP = 7          # просвет между словами, снят замером с оригинала
Y1, Y2 = 66, 97  # верх блоков первой и второй строки
BH = 34          # высота блока со словом
BASE = [92, 123, 154]                 # базовые линии трёх новых строк
CLEAR = (130, 64, 682, 168)           # правее 682 идёт разделитель колонок
CLEAN_ROW, CLEAN_H = 136, 28          # чистая полоса фона, которой затираем текст

# слово -> (левая граница чернил, правая, строка-источник)
WORDS = {
    "Upgrade": (138, 224, 1), "to": (231, 252, 1), "a": (259, 271, 1),
    "or": (309, 330, 1), '6"': (337, 361, 1), "suppressor": (369, 480, 1),
    "for": (487, 515, 1), "more1": (523, 573, 1), "length,": (582, 649, 1),
    "better": (138, 198, 2), "sound": (205, 265, 2), "reduction,": (273, 371, 2),
    "and": (379, 414, 2), "even": (423, 468, 2), "more2": (477, 526, 2),
    "performance.": (534, 665, 2),
    "quote": (352, 361, 1),           # кавычка из «6"», берётся к нарисованным цифрам
}
LINES = [
    ["Upgrade", "to", "a", "#4", "or", '6"', "or", "#8", "suppressor"],
    ["for", "more1", "length,", "better", "sound", "reduction,"],
    ["and", "even", "more2", "performance."],
]


def digit(ch: str) -> Image.Image:
    """Глиф цифры в размер и мягкость соседних цифр картинки."""
    f = ImageFont.truetype(FONT, int(SIZE * SS), index=FONT_INDEX)
    b = f.getbbox(ch)
    g = Image.new("L", (b[2] - b[0] + 16 * SS, b[3] - b[1] + 16 * SS), 0)
    ImageDraw.Draw(g).text((8 * SS - b[0], 8 * SS - b[1]), ch, font=f, fill=255)
    g = g.resize((g.width // SS, g.height // SS), Image.LANCZOS)
    g = g.filter(ImageFilter.GaussianBlur(BLUR))
    p = g.load()
    xs = [x for x in range(g.width) if any(p[x, y] > 18 for y in range(g.height))]
    ys = [y for y in range(g.height) if any(p[x, y] > 18 for x in range(g.width))]
    return g.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    orig = im.copy()
    px = im.load()

    # 1. стереть старый текст, сохранив зерно фона
    for y in range(CLEAR[1], CLEAR[3]):
        sy = CLEAN_ROW + (y - CLEAR[1]) % CLEAN_H
        for x in range(CLEAR[0], CLEAR[2]):
            px[x, y] = px[x, sy]

    def block(x0, x1, line):
        top = Y1 if line == 1 else Y2
        return orig.crop((x0, top, x1 + 1, top + BH))

    def put_word(name, x, base):
        x0, x1, line = WORDS[name]
        top_src, base_src = (Y1, 92) if line == 1 else (Y2, 123)
        im.paste(block(x0, x1, line), (x, base - (base_src - top_src)))
        return x1 - x0 + 1

    glyphs = {c: digit(c) for c in "48"}

    def put_digit(ch, x, base):
        g = glyphs[ch]
        gp = g.load()
        for yy in range(g.height):
            for xx in range(g.width):
                a = gp[xx, yy] / 255
                if a <= 0.004:
                    continue
                dx, dy = x + xx, base - g.height + yy
                b = px[dx, dy]
                px[dx, dy] = tuple(int(b[i] * (1 - a) + INK[i] * a) for i in range(3))
        qx0, qx1, _ = WORDS["quote"]
        im.paste(block(qx0, qx1, 1), (x + g.width + 1, base - (92 - Y1)))
        return g.width + 1 + (qx1 - qx0 + 1)

    for line, base in zip(LINES, BASE):
        x = LEFT
        for tok in line:
            x += (put_digit(tok[1], x, base) if tok.startswith("#") else put_word(tok, x, base)) + GAP
        width = x - GAP - LEFT
        print(f"  базовая {base}: ширина {width} px, правый край {LEFT + width}")

    im.save(DST)
    print(f'{"upgrade-strip":22} {DST.stat().st_size/1024:5.1f} KB   {im.size[0]}x{im.size[1]},'
          f' «5" or 6"» -> «4" or 6" or 8"»')


if __name__ == "__main__":
    main()
