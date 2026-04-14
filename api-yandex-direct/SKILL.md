---
name: api-yandex-direct
description: "Яндекс.Директ API v5 — расход, клики, показы, конверсии, кампании, поисковые запросы. Для агентств и рекламодателей. Триггеры: директ, яндекс директ, отчёт директ, CTR, CPA, CPC, кампании директа, поисковые запросы, search queries, direct report"
---

# Яндекс.Директ API v5 — Skill

Работа с API Яндекс.Директа: отчёты по кампаниям, объявлениям, поисковым запросам; список кампаний, ставки, баллы (Units).

## Когда использовать

- Месячный отчёт: расход, клики, показы, CTR, CPA, CPC, конверсии
- Разбивка по кампаниям, группам, объявлениям, ключевым фразам
- **Поисковые запросы** — по чем реально показывались объявления (goldmine для SEO и минус-фраз)
- Список кампаний, статусы, бюджеты
- Работа с субаккаунтами (агентства) — через `Client-Login`

## Быстрый старт

1. Токен — такой же как для Метрики (единый OAuth Яндекса).
   Если не получен — `python3 ~/.claude/skills/api-yandex-metrika/scripts/get_oauth_token.py`
   (добавь scope `direct:api-light` при создании OAuth приложения)

2. Создай `~/.config/yandex-direct/.env`:
   ```
   YANDEX_DIRECT_TOKEN=<OAuth token>  # тот же что метрика, если был получен с нужным scope
   YANDEX_DIRECT_LOGIN=<логин клиента> # например devicedoctor24
   ```

3. Запусти отчёт:
   ```bash
   python3 scripts/monthly_report.py 2026-03
   ```

## Главное что не очевидно

1. **Headers — обязательны все четыре** для Reports API:
   ```
   Authorization: Bearer {token}
   Client-Login: {login субаккаунта}
   processingMode: auto
   returnMoneyInMicros: false        # деньги в рублях, иначе x1 000 000
   skipReportHeader: true            # без этого в TSV мусор
   skipColumnHeader: true            # ...
   skipReportSummary: true
   Accept-Encoding: gzip             # ответы большие
   ```

2. **Async polling для больших отчётов**: API может вернуть `201/202` — значит «формируется, приди позже». Скрипт должен ждать в цикле.

3. **`ReportName` уникален для каждого запроса** — иначе 400

4. **Units (баллы)** — у каждого запроса динамический лимит баллов; в ответе header `Units: spent/remaining/daily`. Ошибки стоят 20 баллов. Следи за `remaining`.

5. **Client-Login** — критично для агентств. Без него ответ = данные самого агентского аккаунта. С ним — данные конкретного клиента.

6. **Use-Operator-Units: true** — для агентства: баллы списываются с агентского аккаунта, а не клиента.

## Структура

```
api-yandex-direct/
├── SKILL.md
├── README.md
├── scripts/
│   ├── reports.py               # универсальный запрос Reports API с polling
│   ├── monthly_report.py        # CAMPAIGN_PERFORMANCE_REPORT за месяц
│   ├── search_queries.py        # реальные поисковые запросы (SEARCH_QUERY_PERFORMANCE_REPORT)
│   ├── campaigns_list.py        # список всех кампаний
│   └── units_check.py           # проверить остаток баллов
├── examples/
│   ├── request_body.json        # пример POST /reports body
│   └── response_tsv.md          # пример TSV ответа
└── references/
    ├── endpoints.md             # все endpoints
    ├── report_types.md          # 7 типов отчётов
    ├── fields.md                # поля отчётов
    └── rate_limits.md           # Units и параллельность
```

## Типы отчётов (report types)

| Type | Что показывает |
|------|---------------|
| `ACCOUNT_PERFORMANCE_REPORT` | Весь аккаунт одной строкой |
| `CAMPAIGN_PERFORMANCE_REPORT` | По кампаниям |
| `ADGROUP_PERFORMANCE_REPORT` | По группам объявлений |
| `AD_PERFORMANCE_REPORT` | По объявлениям |
| `CRITERIA_PERFORMANCE_REPORT` | По ключам (условия показа) |
| `SEARCH_QUERY_PERFORMANCE_REPORT` | **Реальные поисковые запросы** — самое ценное |
| `CUSTOM_REPORT` | Произвольные группировки |

## Документация

- https://yandex.ru/dev/direct/
- Reports: https://yandex.ru/dev/direct/doc/reports/reports.html
- Units: https://yandex.ru/dev/direct/doc/dg/concepts/limits.html
