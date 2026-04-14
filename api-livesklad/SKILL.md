---
name: api-livesklad
description: "LiveSklad CRM API — заказы, источники клиентов, себестоимость, продажи. Для сервисных центров. Триггеры: livesklad, лайвсклад, заказы из crm, источники клиентов, howKnow, себестоимость ремонтов, ремонтная crm"
---

# LiveSklad API — Skill

Работа с API LiveSklad CRM (api.livesklad.com) — получение заказов, деталей, источников клиентов, продаж.

**Подтверждено на практике** с боевым аккаунтом (сервисный центр в Москве, 113 заказов/месяц).

## Когда использовать

- Выгрузить отчёт по заказам за период
- Посчитать выручку, средний чек, себестоимость, маржу
- Разбивка клиентов по источникам (howKnow)
- Топ брендов, моделей, проблем
- Сверить продажи аксессуаров (sales ≠ orders)

## Быстрый старт

1. Положи креды в `~/.config/livesklad/.env`:
   ```
   LIVESKLAD_API_LOGIN=<login из кабинета>
   LIVESKLAD_API_PASSWORD=<password>
   LIVESKLAD_SHOP_ID=<shop_id, взять из /shops>
   ```
2. Запусти пример:
   ```
   python3 scripts/fetch_monthly_report.py 2026-03
   ```

## Структура

```
api-livesklad/
├── SKILL.md                         # этот файл
├── README.md                        # для публичного шаринга
├── scripts/
│   ├── auth.py                      # auth + retry, используется остальными
│   ├── fetch_orders_list.py         # список заказов за период
│   ├── fetch_order_details.py       # все детали 1 заказа (howKnow, positions)
│   ├── fetch_monthly_report.py      # ВСЁ за месяц: список + детали + аналитика
│   └── fetch_how_knows.py           # справочник источников
├── examples/
│   ├── response_order_list.json     # пример ответа list endpoint
│   ├── response_order_detail.json   # пример ответа detail endpoint
│   └── response_how_knows.json      # пример справочника
└── references/
    ├── endpoints.md                 # полный список endpoints + поля
    ├── rate_limits.md               # стратегия обхода rate limit
    └── gotchas.md                   # подводные камни
```

## Главное — что не очевидно

1. **Detail endpoint — `/orders/{id}` (БЕЗ `/shops/`)** — остальное (`/shops/{shop}/orders/{id}`) даёт 404
2. **`howKnow` и `positions` только в detail** — в list их нет
3. **`summ.purchasePrice` только в detail** — себестоимость недоступна в list
4. **Rate limit: 100 запросов / 15 мин** — после исчерпания 429 на 15 минут
5. **Token в header без Bearer** — просто `Authorization: {token}`
6. **Даты в `dateCreate` — Unix ms в квадратных скобках URL-encoded**: `dateCreate=%5B{start_ms}%2C{end_ms}%5D`

## Rate Limit — самый частый косяк

При 100 запросах / 15 мин на 113 заказов (1 auth + 3 list + 113 detail = 117) будет 1 пауза. Стратегия:
- Сохранять промежуточные результаты каждые 20 заказов
- При remaining ≤ 3 — ждать 70 сек и re-auth
- При 429 на auth — экспоненциальный бэкофф (65s, 130s, 195s...)

См. `references/rate_limits.md` и `scripts/fetch_monthly_report.py`.

## Типичные метрики из 113 заказов/месяц

- Выручка (soldPrice), себестоимость (purchasePriceSumm из positions), маржа
- Источники (howKnow): Яндекс карты, Повторное обращение, 2ГиС, Директ, Авито, Флаер, Совет знакомых
- Бренды (brand в detail): Apple, Samsung, Xiaomi, Huawei, Tecno...
- Проблемы (problem[]): Разбит дисплей, Не включается, АКБ, Не заряжается
- Категории (typeOrder): Смартфон/планшет, Ноутбук/ПК, Заказ без приёма, Гарантия

## Документация

Официальная: https://developer.livesklad.com/
- [Orders](https://developer.livesklad.com/api/order)
- [Shops](https://developer.livesklad.com/api/shop)
- [How-knows](https://developer.livesklad.com/api/how-know)

## Безопасность

Скилл читает креды ТОЛЬКО из `~/.config/livesklad/.env`. В коде и логах пароли не печатаются. Для публичного репо — нет захардкоженных токенов.
