# api-yandex-direct — Claude Code Skill

Готовый скилл для работы с API Яндекс.Директа v5: месячные отчёты, реальные поисковые запросы, кампании, минус-фразы.

## Что умеет

- ✅ Месячный отчёт по кампаниям: расход, клики, показы, CTR, CPA, конверсии
- ✅ **Поисковые запросы** — по чему реально показывались объявления
- ✅ Автоматические кандидаты в минус-фразы (без конверсий, траты >100₽)
- ✅ Список всех кампаний (активных/архивных) с бюджетами
- ✅ Проверка баллов (Units) — остаток на сегодня
- ✅ Async polling для больших отчётов (201/202 → 200)
- ✅ gzip-сжатие ответов
- ✅ Поддержка агентских аккаунтов (Client-Login, Use-Operator-Units)

## Установка

Через Claude Code:
```
установи скилл из https://github.com/salto-agancy/api-yandex-direct-skill
```

Вручную:
```bash
git clone https://github.com/salto-agancy/api-yandex-direct-skill ~/.claude/skills/api-yandex-direct
```

## Настройка

1. Если **нет OAuth токена** — получить через Метрика-скилл (токен общий):
   ```bash
   python3 ~/.claude/skills/api-yandex-metrika/scripts/get_oauth_token.py
   ```
   **Важно**: при создании OAuth приложения добавь scope `direct:api-light`.

2. Создай `~/.config/yandex-direct/.env`:
   ```
   YANDEX_DIRECT_TOKEN=<OAuth token>
   YANDEX_DIRECT_LOGIN=<логин клиента, например devicedoctor24>
   ```

3. Проверь остаток Units:
   ```bash
   python3 scripts/units_check.py
   ```

## Быстрый старт

```bash
# Отчёт по кампаниям за март
python3 scripts/monthly_report.py 2026-03

# Поисковые запросы — топ-30 по расходу + кандидаты в минусы
python3 scripts/search_queries.py 2026-03

# Все поисковые запросы в CSV
python3 scripts/search_queries.py 2026-03 --csv

# Список кампаний
python3 scripts/campaigns_list.py

# С архивными
python3 scripts/campaigns_list.py --archived

# Сколько Units осталось
python3 scripts/units_check.py
```

## Структура

```
api-yandex-direct/
├── SKILL.md
├── README.md
├── scripts/
│   ├── reports.py               # универсальный Reports API с polling
│   ├── monthly_report.py        # CAMPAIGN_PERFORMANCE_REPORT
│   ├── search_queries.py        # SEARCH_QUERY_PERFORMANCE_REPORT + минусы
│   ├── campaigns_list.py        # список кампаний
│   └── units_check.py           # остаток баллов
├── examples/
│   ├── request_body.json        # пример тела запроса
│   └── response_tsv.md          # пример TSV ответа
└── references/
    ├── endpoints.md             # все endpoints
    ├── report_types.md          # 7 типов отчётов
    ├── fields.md                # поля отчётов
    └── rate_limits.md           # Units и параллельность
```

## Триггеры в Claude Code

Скилл автоматически загружается, когда пишешь:
- «директ», «расход директа», «отчёт директа»
- «CTR», «CPA», «конверсии рекламы»
- «какие запросы ищут», «поисковые запросы директа», «search queries»
- «минус-фразы», «собери минусы»
- «список кампаний»

## Units (rate limit)

Директ не считает запросы в минуту — считает **баллы**.
Следи за header `Units: spent/remaining/daily` в каждом ответе.
Ошибка = -20 Units.

Подробнее: `references/rate_limits.md`.

## Safety tips

- `skipColumnHeader: false` — первая строка TSV = имена полей (иначе непонятно, какие колонки)
- `returnMoneyInMicros: false` — числа в рублях, иначе × 1 000 000
- `ReportName` уникальный для каждого запроса (иначе ошибка)
- Sandbox (`api-sandbox.direct.yandex.com`) для разработки без трат Units

## Документация

- https://yandex.ru/dev/direct/
- Reports: https://yandex.ru/dev/direct/doc/ru/reports/reports
- Reference: https://yandex.ru/dev/direct/doc/ru/ref-v5/v5

## Лицензия

MIT

## Автор

Salto Agency — @salto_dima
