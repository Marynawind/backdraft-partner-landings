# Backdraft Suppressors — Partner Landing Pages

Лендинги для четырёх партнёров магазина Backdraft Suppressors (BigCommerce, Stencil).

| # | Партнёр | URL | Статус |
|---|---------|-----|--------|
| 1 | Gun Owners of America | `backdraftsuppressors.com/GOA` | готово к вставке, ждёт публикации |
| 2 | Burris Optics | `backdraftsuppressors.com/Burris` (предв.) | не начато |
| 3 | Meprolight Optics | `backdraftsuppressors.com/Meprolight` (предв.) | не начато |
| 4 | MasterFFL | `backdraftsuppressors.com/MasterFFL` (предв.) | не начато |

## Структура

```
partners/goa/
  page.src.html           ← ИСХОДНИК, правится только он
  build.py                ← собирает из него два файла ниже (нужен только Python)
  bigcommerce-page.html   ← ГОТОВОЕ, вставлять в BigCommerce; картинки внутри
  preview.html            ← локальный превью с макетом шапки/футера магазина
  tools-cutout.py         ← готовит assets/ из assets/source/ (нужен Pillow)
  copy.md                 ← утверждённые тексты
  DEPLOY.md               ← инструкция по публикации
  assets/                 ← картинки, которые build.py вшивает в страницу
  assets/source/          ← исходники как скачаны с CDN Outlier, не трогать
  reference/              ← референсы стиля от клиента
brand/
  brand.md                ← цвета, шрифты, ссылки магазина
```

## Принцип

Один HTML-фрагмент на страницу. Весь CSS изолирован под классом `.bdg`
(для GOA), чтобы ничего не протекало в тему Stencil и наоборот.
Никакого JS — страница целиком статична и рендерится сразу; анимация
иллюстраций сделана на CSS и полностью отключается при
`prefers-reduced-motion: reduce`.

**Один файл на страницу.** Интеграция в BigCommerce — это вставка кода в поле
«Page Content», поэтому картинки зашиты в готовый файл как data URI: грузить
в магазин отдельно нечего, и страница не зависит ни от чьего CDN. Из-за base64
файл весит около 200 КБ, так что каждая картинка упоминается ровно один раз —
`build.py` это проверяет.
