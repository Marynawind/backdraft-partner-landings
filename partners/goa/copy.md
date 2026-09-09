# /GOA — тексты страницы

Формулировки из ТЗ клиента даны дословно. Шаги редемпшена — дословно
с https://getoutlier.com/redemption; условия (раздел 6) с 09.09.2026 заменены
собственной версией клиента и с этой страницей больше не совпадают.

## 1. Welcome (hero)
**Наверху:** логотип Gun Owners of America (без подписи рядом)

**H1:** Welcome, Gun Owners of America Members!

Thank you for your continued support of Gun Owners of America and for standing up for our Second Amendment rights.

As a GOA member, you're eligible to redeem your **Free Suppressor Rebate**.

**CTA:** How to Redeem Your Rebate · Shop Suppressors

## 2. Rebate at a glance — блок удалён

Строка из четырёх фактов (сумма рибейта, что положено, срок, срок действия
кода) снята по просьбе клиента 09.09.2026.

⚠️ **Следствие:** сумма $189.99 теперь встречается на странице ровно один раз —
в тексте Terms. Срок «8–12 недель» и годичный срок действия кода тоже остались
только в условиях и на инфографике. Раньше эти четыре факта были видны сразу,
без чтения условий.

## 3. How to Redeem Your Rebate
*Use your rebate code at checkout to redeem your 4" Hunter Suppressor (non-magnum).*

Четыре шага показаны одной инфографикой клиента (`assets/redemption-infographic.webp`),
дословно как на getoutlier.com/redemption:

1. **Visit the Website** — Start your rebate redemption online at BackdraftSuppressors.com.
2. **Select Your Suppressor** — Choose your free 4" Hunter Suppressor (non-magnum).
3. **Add Required HUB Adapter\*** — Select the required HUB thread adapter for your suppressor.
4. **Enter Your Rebate Code** — Apply your code at checkout and choose your preferred FFL/SOT for transfer.

Раньше эти же шаги дублировались под инфографикой четырьмя карточками —
карточки убраны по решению клиента. Поэтому текст шагов теперь существует
только внутри картинки: он полностью продублирован в её `alt`, иначе шаги
не читались бы ни поиском, ни скринридером. **При замене инфографики нужно
обновить и `alt`.**

Подпись под инфографикой (видна только на узких экранах):
**Swipe the graphic sideways to read all four steps.**

### Бегущая строка «How it works»

Под инфографикой — лента: те же четыре шага едут справа налево, круг 22 с.
Тексты шагов дословно те же, что в списке выше. Подписи в шапке блока:

- **How it works**
- **Four steps**

Иллюстрации — те самые, из убранных карточек. При выключенной анимации
(`prefers-reduced-motion`) лента становится обычной сеткой 2×2.

**Ready to Redeem?** Choose your 4" Hunter Suppressor, add the required HUB Adapter, and enter your rebate code at checkout.
**Кнопка:** Redeem Your Suppressor Now → `/backdraft-hunter/`

## 4. Please Note

**\* Paid by the customer** — Shipping/Handling, the required HUB Adapter, applicable taxes, transfer taxes, and any FFL/SOT or ATF/NFA-related fees are the responsibility of the customer.

Список: HUB Adapter · Shipping and handling · Applicable taxes · Transfer taxes · ATF/NFA-related fees · FFL/SOT transfer fees

## 5. Close
We appreciate your support and are proud to offer this exclusive benefit to fellow Second Amendment supporters.

**CTA:** Redeem Your Rebate → `backdraftsuppressors.com/backdraft-hunter/` ·
Visit the Website → `backdraftsuppressors.com`

Все ссылки на странице абсолютные, на `https://backdraftsuppressors.com`.

## 6. Terms & Conditions

Заголовок: **Terms & Conditions**, дальше три сплошных абзаца — текст клиента
дословно, получен 09.09.2026.

Абзацы по темам:
1. Что покрывает рибейт и что нет, правила использования кода.
2. Ответственность покупателя, передача через FFL/SOT, HUB-адаптер,
   законность, право отозвать рибейт.
3. Возвраты и отмены, право менять условия промо.

⚠️ **Прежняя версия заменена целиком.** До этого здесь были 18 нумерованных
разделов (Important Customer Responsibility Notice … Severability) плюс блок
Customer Acknowledgement. Всё удалено: новый первый абзац начинается с той же
формулировки про согласие и заменяет собой Acknowledgement.

⚠️ **Раньше условия обязаны были совпадать с getoutlier.com/redemption.**
Новый текст короче и сформулирован иначе — это версия клиента, и она
расходится с тем, что опубликовано на getoutlier.com. Если обе страницы должны
говорить одно и то же, синхронизировать их — задача клиента.

## Открытые вопросы к клиенту
- Логотип GOA поставлен наверх страницы по решению клиента (09.09.2026).
  Использование товарного знака партнёра согласовывает клиент — вопрос
  закрыт с его стороны, не техническая часть.
- Есть ли отдельный эксклюзивный код для членов GOA, который нужно показать?
- Нужна ли форма сбора e-mail членов GOA?
- Инфографика на мобильном листается вбок — читаемо, но не идеально.
  Если клиент даст вертикальную версию картинки под узкий экран, её можно
  подставить через `<picture>` и убрать боковую прокрутку.
