# /GOA — тексты страницы

Формулировки из ТЗ клиента даны дословно. Шаги редемпшена и мелкий шрифт —
дословно с https://getoutlier.com/redemption.

## 1. Welcome (hero)
**Наверху:** логотип Gun Owners of America (без подписи рядом)

**H1:** Welcome, Gun Owners of America Members!

Thank you for your continued support of Gun Owners of America and for standing up for our Second Amendment rights.

As a GOA member, you're eligible to redeem your **Free Suppressor Rebate**.

**CTA:** How to Redeem Your Rebate · Shop Suppressors

## 2. Rebate at a glance
| Rebate value | Eligible suppressor | Estimated lead time | Code validity |
|---|---|---|---|
| $189.99 — applied toward the eligible suppressor | 4" Hunter — non-magnum only | 8–12 weeks — after checkout and payment; not guaranteed | 1 year — from the date it is received or issued |

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

## 6. Terms and Conditions
Заголовок документа: **Backdraft Suppressors Free Suppressor Rebate — Customer Acknowledgement of Required Rebate Terms**, подзаголовок **Terms and Conditions**.

Полный текст условий свёрстан в `bigcommerce-page.html` (секция `.bdg-legal`),
18 разделов: Important Customer Responsibility Notice · Eligible Rebate Item ·
Rebate Code Use · Rebate Expiration · How to Redeem · Required HUB Adapter ·
Customer Fees, Taxes, and Transfer Costs · FFL/SOT Transfer Process ·
Lead Time and Fulfillment · Availability and Substitutions ·
No Stacking or Cash Redemption · Returns, Cancellations, and Refunds ·
Eligibility and Legal Compliance · Misuse, Fraud, and Revocation ·
Program Changes · Errors and Technical Issues · Severability.

Текст дословный, предоставлен клиентом. Любая правка должна вноситься
одновременно здесь и на getoutlier.com/redemption — иначе условия разойдутся.

## Открытые вопросы к клиенту
- Логотип GOA поставлен наверх страницы по решению клиента (09.09.2026).
  Использование товарного знака партнёра согласовывает клиент — вопрос
  закрыт с его стороны, не техническая часть.
- Есть ли отдельный эксклюзивный код для членов GOA, который нужно показать?
- Нужна ли форма сбора e-mail членов GOA?
- Инфографика на мобильном листается вбок — читаемо, но не идеально.
  Если клиент даст вертикальную версию картинки под узкий экран, её можно
  подставить через `<picture>` и убрать боковую прокрутку.
