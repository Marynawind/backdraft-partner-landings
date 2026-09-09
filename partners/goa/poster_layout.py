"""Перебирает низ инфографики: шесть шагов списком и компактная полоса под ними.

Клиент попросил перенести шаги со страницы в картинку. Четырёх карточек Outlier
для шести шагов не хватает, а тексты стали длиннее, поэтому шаги набираются
заново — списком с латунными номерами, как в прежней живой вёрстке.

Шрифт — Barlow, основной шрифт темы магазина (`brand/brand.md`). Он же ближе
всех к обычному начертанию самой инфографики: замер по трём строкам известной
ширины даёт расхождение 3,3%, тогда как всё, что стоит в системе, расходится
сильнее. Файлы шрифта лежат в `assets/source/fonts/`, чтобы сборка не зависела
от интернета и от того, что установлено на машине.

Полоса апгрейда и сноска сведены в одну строку из трёх колонок и уехали вниз,
под шаги. Иконки взяты из исходников: диск со стрелкой и щит со звездой — из
полосы, щит с галочкой — из самой инфографики.

Оба блока набраны по одной сетке: номер шага и иконка полосы стоят в колонке
одной ширины, текст в обоих начинается с одного и того же x, волоски между
шагами тянутся ровно на ширину рамки полосы. Цвета не выдуманы, а сняты замером
с самой инфографики — см. константы ниже.
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "assets" / "source" / "fonts"
REG, BOLD = FONTS / "barlow-400.ttf", FONTS / "barlow-600.ttf"

SS = 3                      # суперсэмплинг текста
CONTENT = (78, 1140)        # колонка контента в исходнике 1536 px
ZONE_TOP = 512              # сразу под латунной линейкой, где начинались карточки

# общая сетка обоих блоков
PAD = 18                    # от края колонки до номера и до иконки
MARK_COL = 48               # ширина колонки под номер шага и под иконку полосы
GUTTER = 14                 # от колонки со знаком до текста
TEXT_X = CONTENT[0] + PAD + MARK_COL + GUTTER

# палитра снята с самой инфографики: рамка карточки, цифры карточек, их текст
LINE = (63, 57, 54)
BRASS = (178, 131, 75)
INK = (199, 199, 199)

# Кегль задан от того, как текст виден на странице: картинка показывается
# не шире 1112 CSS px при исходнике 1536, то есть уменьшается в 0,72 раза.
# Прописная 21 px даёт на экране 15 px — примерно как основной текст страницы.
STEP_CAP, STEP_LEAD, STEP_GAP = 21, 33, 13   # высота прописной, интерлиньяж, поля пункта
NUM_CAP = 23
STRIP_CAP, STRIP_LEAD = 15, 22               # полоса — сноска, поэтому мельче шагов
ICON_H = 50
RADIUS = 11                                  # радиус рамки, снят с прежней плашки сноски
BOTTOM = 24                                  # поле от рамки до низа картинки

STEPS = [
    "Visit BackdraftSuppressors.com",
    'Select a 4" Hunter, or upgrade to 6", 8", or steel Poacher for an additional cost.',
    "Select the required HUB Adapter.",
    "Enter the rebate code at checkout.",
    "Select your preferred FFL/SOT for suppressor transfer.",
    "Complete checkout and pay all required charges, including any upgrade cost, "
    "HUB Adapter, shipping, and taxes.",
]
COLUMNS = [
    ("arrow", "WANT MORE PERFORMANCE?",
     'Upgrade to a 4" or 6" or 8" suppressor for more length, better sound reduction, '
     "and even more performance."),
    ("star", "GO FULL AUTO. GO STAINLESS.",
     "Upgrade to our stainless steel, full auto rated suppressor options built for "
     "the most demanding use."),
    ("check", None,
     "Suppressor transfers follow all applicable ATF/NFA requirements. Shipping, "
     "transfer, tax, and required adapter costs apply.*"),
]
ICON_SRC = {                       # откуда режем иконки, замер по исходникам
    "arrow": ("strip", (16, 17, 115, 118)),
    "star": ("strip", (712, 22, 782, 106)),
    "check": ("poster", (80, 911, 159, 994)),
}
ERASE = (76, 508, 1142, 1012)      # карточки Outlier и прежняя плашка сноски


def sized(path: pathlib.Path, cap: int) -> ImageFont.FreeTypeFont:
    """Шрифт кеглем под заданную высоту прописной — в пикселях исходника×SS."""
    probe = ImageFont.truetype(str(path), 400)
    b = probe.getbbox("H")
    return ImageFont.truetype(str(path), round(400 * cap * SS / (b[3] - b[1])))


def wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) <= width * SS or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def compose(poster: Image.Image, strip_src: Image.Image) -> Image.Image:
    x0, x1 = CONTENT
    f_step, f_num = sized(REG, STEP_CAP), sized(BOLD, NUM_CAP)
    f_head, f_body = sized(BOLD, STRIP_CAP), sized(REG, STRIP_CAP)

    icons = {}
    for key, (where, box) in ICON_SRC.items():
        img = (strip_src if where == "strip" else poster).crop(box)
        icons[key] = img.resize((round(img.width * ICON_H / img.height), ICON_H), Image.LANCZOS)

    # высота холста считается от содержимого: шесть шагов крупнее прежних четырёх
    # карточек, и в исходные 1024 px они не помещаются. Дорощенные снизу строки
    # чёрные — там и так только затухающая тень рендера, а на странице картинка
    # накладывается блендингом screen, так что чёрное не видно вовсе.
    steps_h = sum(2 * STEP_GAP + STEP_LEAD * len(wrap(t, f_step, x1 - PAD - TEXT_X))
                  for t in STEPS) + len(STEPS) - 1
    col_w = (x1 - x0 + 1) // 3
    inner = col_w - 2 * PAD - MARK_COL - GUTTER
    rows = max(len(wrap(b, f_body, inner)) + (1 if h else 0) for _, h, b in COLUMNS)
    box_h = 2 * PAD + max(rows * STRIP_LEAD, ICON_H) + 4
    need = ZONE_TOP + steps_h + STEP_GAP * 2 + box_h + BOTTOM
    if need > poster.height:
        grown = Image.new("RGB", (poster.width, need), (0, 0, 0))
        grown.paste(poster, (0, 0))
        poster = grown

    draw = ImageDraw.Draw(poster)
    draw.rectangle((ERASE[0], ERASE[1], ERASE[2], poster.height), fill=(0, 0, 0))

    # текст рисуем на отдельном слое в SS раз крупнее и уменьшаем: так мелкий
    # кегль выходит мягким, как набранный, а не ступенчатым
    layer = Image.new("RGB", (poster.width * SS, poster.height * SS), (0, 0, 0))
    ink = ImageDraw.Draw(layer)

    def put(x, y, text, font, fill):
        ink.text((x * SS, y * SS), text, font=font, fill=fill, anchor="lt")

    y = ZONE_TOP
    for i, step in enumerate(STEPS, 1):
        lines = wrap(step, f_step, x1 - PAD - TEXT_X)
        top = y + STEP_GAP
        num = f"{i}."
        nx = x0 + PAD + (MARK_COL - f_num.getlength(num) / SS) / 2
        put(nx, top + STEP_CAP - NUM_CAP, num, f_num, BRASS)
        for j, line in enumerate(lines):
            put(TEXT_X, top + j * STEP_LEAD, line, f_step, INK)
        y = top + len(lines) * STEP_LEAD + STEP_GAP
        if i < len(STEPS):
            draw.line((x0, y, x1, y), fill=LINE)
            y += 1
    steps_bottom = y

    # компактная полоса: три колонки в одной строке
    blocks = [(key, head, wrap(body, f_body, inner)) for key, head, body in COLUMNS]
    box_y = poster.height - BOTTOM - box_h

    mask = Image.new("L", ((x1 - x0 + 1) * 4, box_h * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle((2, 2, mask.size[0] - 3, mask.size[1] - 3),
                                           radius=RADIUS * 4, outline=255, width=5)
    mask = mask.resize((x1 - x0 + 1, box_h), Image.LANCZOS)
    poster.paste(Image.new("RGB", mask.size, LINE), (x0, box_y), mask)

    for n, (key, head, lines) in enumerate(blocks):
        cx = x0 + n * col_w
        if n:
            draw.line((cx, box_y + PAD, cx, box_y + box_h - PAD - 1), fill=LINE)
        icon = icons[key]
        poster.paste(icon, (round(cx + PAD + (MARK_COL - icon.width) / 2), box_y + PAD))
        tx, ty = cx + PAD + MARK_COL + GUTTER, box_y + PAD - 1
        if head:
            put(tx, ty, head, f_head, INK)
            ty += STRIP_LEAD
        for line in lines:
            put(tx, ty, line, f_body, INK)
            ty += STRIP_LEAD

    assert steps_bottom < box_y, f"шаги ({steps_bottom}) налезают на полосу ({box_y})"

    layer = layer.resize(poster.size, Image.LANCZOS)
    px, lp = poster.load(), layer.load()
    for yy in range(ZONE_TOP - 4, poster.height):
        for xx in range(x0, x1 + 1):
            s = lp[xx, yy]
            if s[0] or s[1] or s[2]:
                d = px[xx, yy]
                px[xx, yy] = tuple(255 - (255 - d[i]) * (255 - s[i]) // 255 for i in range(3))
    print(f"  холст {poster.width}x{poster.height}, шаги {ZONE_TOP}..{steps_bottom},"
          f" полоса {box_y}..{box_y + box_h - 1}, зазор {box_y - steps_bottom} px,"
          f" текст с x={TEXT_X} в обоих блоках")
    return poster
