# api-yandex-metrika — Claude Code Skill

Готовый скилл для работы с API Яндекс.Метрики: визиты, цели, источники трафика, карточка Яндекс.Бизнес, сравнение периодов, Logs API.

## Что умеет

- ✅ Месячный отчёт: визиты, пользователи, отказы, глубина, время на сайте
- ✅ Разбивка по источникам (реклама / поиск / прямые / соцсети)
- ✅ Только рекламный трафик (фильтр `trafficSource=='ad'`) + UTM-breakdown
- ✅ Топ городов (отделяет ботов из зарубежья)
- ✅ Цели: список + достижения + конверсии
- ✅ Яндекс.Бизнес карточка: клики по телефону, маршруты, переходы на сайт
- ✅ **Сравнение двух периодов** одним запросом (comparison API)
- ✅ **Logs API** — выгрузка сырых визитов для глубокого анализа
- ✅ OAuth flow для получения токена

## Установка

Через Claude Code:
```
установи скилл из https://github.com/salto-agancy/api-yandex-metrika-skill
```

Вручную:
```bash
git clone https://github.com/salto-agancy/api-yandex-metrika-skill ~/.claude/skills/api-yandex-metrika
```

## Настройка

1. Создай OAuth приложение на https://oauth.yandex.ru/client/new
   - Scopes: `metrika:read` (для Метрики) + `direct:api-light` (если нужен Директ)
2. Запусти OAuth flow:
   ```bash
   python3 scripts/get_oauth_token.py
   ```
3. Скрипт сохранит токен в `~/.config/yandex-metrika/.env`:
   ```
   YANDEX_METRIKA_TOKEN=<token>
   YANDEX_METRIKA_REFRESH_TOKEN=<refresh>
   YANDEX_METRIKA_TOKEN_EXPIRES=<date>
   YANDEX_CLIENT_ID=<id>
   YANDEX_CLIENT_SECRET=<secret>
   ```
4. Проверь:
   ```bash
   python3 scripts/list_counters.py
   ```

## Быстрый старт

```bash
# Список счётчиков
python3 scripts/list_counters.py

# Месячный отчёт
python3 scripts/monthly_report.py 12345678 2026-03

# Источники трафика
python3 scripts/traffic_sources.py 12345678 2026-03

# Только реклама + UTM
python3 scripts/ads_only.py 12345678 2026-03

# Яндекс.Бизнес карточка
python3 scripts/business_card.py 97281982 2026-03

# Топ городов (фильтр ботов)
python3 scripts/cities.py 12345678 2026-03

# Цели
python3 scripts/goals_report.py 12345678 2026-03

# Сравнение март vs февраль
python3 scripts/compare_periods.py 12345678 2026-03 2026-02

# Сырой лог визитов (для ClickHouse и т.п.)
python3 scripts/logs_export.py 12345678 2026-03-01 2026-03-31
```

## Структура

```
api-yandex-metrika/
├── SKILL.md                      # инструкция для Claude
├── README.md                     # этот файл
├── scripts/
│   ├── query.py                  # универсальный query helper
│   ├── get_oauth_token.py        # OAuth flow
│   ├── list_counters.py          # список счётчиков
│   ├── monthly_report.py         # базовый отчёт за месяц
│   ├── traffic_sources.py        # источники (organic/ad/direct/...)
│   ├── ads_only.py               # только реклама + UTM
│   ├── business_card.py          # Я.Бизнес карточка
│   ├── cities.py                 # города, фильтр ботов
│   ├── goals_report.py           # цели + конверсии
│   ├── compare_periods.py        # сравнение двух периодов
│   └── logs_export.py            # Logs API — сырые визиты
├── examples/
│   └── response_stat_v1.json     # пример ответа stat API
└── references/
    ├── endpoints.md              # все endpoints
    ├── dimensions_metrics.md     # шпаргалка по полям
    ├── filters.md                # синтаксис filters
    ├── yandex_business.md        # особенности карточки ЯБ
    └── advanced.md               # атрибуция, drill-down, Logs API, мульти-счётчик
```

## Триггеры в Claude Code

Скилл автоматически загружается, когда пишешь:
- «метрика», «статистика сайта», «визиты», «конверсия»
- «откуда трафик», «рекламный трафик»
- «карточка яндекс бизнес», «клики по телефону карточки»
- «сравни март и февраль по метрике»

## Безопасность

- Токен только в `~/.config/yandex-metrika/.env` (`.gitignore` блокирует)
- Никаких токенов в коде и логах
- Права токена по-минимуму: `metrika:read` достаточно для всех читающих скриптов

## Rate limits

| API | Лимит |
|-----|-------|
| `/stat/v1/data` | 200 req / 5 мин, 5000 / сутки, 30 RPS |
| Logs API | 10 RPS |
| Параллельно | 3 одновременных |

## Документация

- https://yandex.ru/dev/metrika/ru/
- Поля: https://yandex.ru/dev/metrika/ru/stat/api/api-fields

## Лицензия

MIT

## Автор

Salto Agency — @salto_dima (Telegram)

---

**Проверено в продакшене** на клиентских счётчиках агентства.
