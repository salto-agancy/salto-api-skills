# Метрика API — продвинутые фичи

## Мульти-счётчик

Можно запросить сразу несколько счётчиков через `ids=1,2,3`:
```
GET /stat/v1/data?ids=12345,67890&metrics=ym:s:visits
```
Данные агрегируются. Удобно для холдингов с несколькими сайтами.

## Атрибуция

Параметр `attribution` в dimension влияет на определение источника трафика:

| Значение | Смысл |
|----------|-------|
| `lastsign` | Последний значимый (default) |
| `first` | Первый клик (для оценки привлечения) |
| `last` | Последний клик |
| `cross` | Кросс-девайс |
| `automatic` | Яндекс решает автоматически |

Используется префиксом в имени dimension:
```
ym:s:lastsignTrafficSource
ym:s:firstUTMSource
```

Пример: определить какие **первые** источники привели к покупке
```
dimensions=ym:s:firstTrafficSource
filters=ym:s:goalreaches>0
```

## Drill-down

`/stat/v1/data/drilldown` — раскрытие измерения на следующий уровень:
```
GET /stat/v1/data/drilldown
  ?ids={counter}
  &dimensions=ym:s:trafficSource,ym:s:sourceEngine,ym:s:UTMCampaign
  &parent_id=ad,Yandex,spring-sale-2026
```
Удобно для интерактивных дашбордов.

## Сравнение периодов

`/stat/v1/data/comparison` — A vs B в одном запросе:
```
?date1_a=2026-03-01&date2_a=2026-03-31
&date1_b=2026-02-01&date2_b=2026-02-28
&filters_a=...   # опционально, разные фильтры для A и B
&filters_b=...
```

См. `scripts/compare_periods.py`.

## Logs API

Сырые визиты построчно. Медленнее, чем stat. Нужен для:
- Глубокий анализ по session_id
- Импорт в ClickHouse/BigQuery
- Custom cohort analysis

Процесс (см. `scripts/logs_export.py`):
1. `evaluate` — проверить возможность запроса
2. `create` → получить request_id
3. Ждать `status='processed'`
4. Скачивать parts по одному
5. Почистить запрос (`clean`)

Лимит: 10 RPS по IP. Данные доступны через ~3 часа после визита.

## Rate limits

| API | Лимит |
|-----|-------|
| `/stat/v1/data` | 200 req / 5 мин на пользователя, 5000 / сутки, 30 RPS с IP |
| Logs API | 10 RPS с IP |
| Параллельных | 3 одновременных на аккаунт |

При 429 — backoff 30+ сек.

## Data Import API

Загрузка офлайн-конверсий (звонки из колл-трекинга, покупки из CRM):
```
POST /management/v1/counter/{counter}/offline_conversions/upload
```

CSV с колонками: `UserId, Target, DateTime, Price, Currency`.

## Когда НЕ использовать Метрику

- Real-time события (<1 час) — используй встроенный JS API Метрики
- Воронки с кастомной логикой (без предустановленных целей) — создай цель заранее в UI
- Вебвизор — нет публичного API, только UI
