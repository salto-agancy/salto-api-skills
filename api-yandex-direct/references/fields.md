# Поля отчётов Reports API

Полный список: https://yandex.ru/dev/direct/doc/ru/reports/fields-list

## Dimensions (группировка) — можно указывать в FieldNames

| Поле | Описание |
|------|----------|
| `Date` | Дата (группировка по дням) |
| `CampaignId`, `CampaignName`, `CampaignType` | Кампания |
| `AdGroupId`, `AdGroupName` | Группа |
| `AdId`, `AdFormat` | Объявление |
| `CriterionId`, `Criterion`, `CriterionType`, `Keyword` | Условие показа |
| `Query` | Поисковый запрос (только в `SEARCH_QUERY_PERFORMANCE_REPORT`) |
| `MatchType` | Тип соответствия (точное, фразовое, ...) |
| `Device` | Устройство: `DESKTOP`, `MOBILE`, `TABLET` |
| `Placement` | Площадка (рекламная сеть) |
| `LocationOfPresence` | Регион показа |
| `Gender` | Пол (если отслеживается) |
| `Age` | Возрастная группа |

## Metrics (числовые) — тоже в FieldNames

| Поле | Описание |
|------|----------|
| `Impressions` | Показы |
| `Clicks` | Клики |
| `Cost` | Расход (с НДС если IncludeVAT:YES) |
| `Ctr` | CTR в % |
| `AvgCpc` | Средняя цена клика (₽) |
| `AvgImpressionPosition` | Средняя позиция показа |
| `AvgClickPosition` | Средняя позиция клика |
| `Conversions` | Конверсии (нужна цель Метрики привязана к Директу) |
| `CostPerConversion` | CPA |
| `ConversionRate` | Конверсия в % |
| `Revenue` | Доход (если передаётся в цели) |
| `Profit` | Прибыль (Revenue - Cost) |
| `Bounces` | Отказы (из Метрики, привязанной к Директу) |
| `BounceRate` | % отказов |
| `AvgPageviews` | Глубина |
| `AvgTrafficVolume` | Средний объём трафика (ставки) |

## Goals-specific metrics

С параметром `Goals: [12345]`:
- `Goals_<goalId>_Conversions` — достижения конкретной цели
- `Goals_<goalId>_CostPerConversion`
- `Goals_<goalId>_ConversionRate`
- `Goals_<goalId>_Revenue`

## Attribution-specific

С параметром `AttributionModels: ["LC"]`:
- `LC_Conversions` — последний клик
- `FC_Conversions` — первый клик
- `LYDC_Conversions` — последний значимый
- `AUTO_Conversions` — автомодель Яндекса

## Фильтры в SelectionCriteria

```json
"Filter": [
  {"Field": "Impressions", "Operator": "GREATER_THAN", "Values": ["10"]},
  {"Field": "CampaignType", "Operator": "EQUALS", "Values": ["TEXT_CAMPAIGN"]}
]
```

**Operators**:
- `EQUALS`, `NOT_EQUALS`
- `IN`, `NOT_IN` (несколько значений)
- `LESS_THAN`, `GREATER_THAN`
- `LESS_OR_EQUAL`, `GREATER_OR_EQUAL`
- `STARTS_WITH_IGNORE_CASE`

## Примеры

### Топ-10 кампаний по расходу
```json
{
  "FieldNames": ["CampaignName", "Impressions", "Clicks", "Cost"],
  "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
  "OrderBy": [{"Field": "Cost", "SortOrder": "DESCENDING"}],
  "Page": {"Limit": 10}
}
```

### Только с конверсиями
```json
"Filter": [{"Field": "Conversions", "Operator": "GREATER_THAN", "Values": ["0"]}]
```

### Поисковые запросы с достижениями конкретной цели
```json
{
  "FieldNames": ["Query", "Clicks", "Cost", "Goals_12345_Conversions"],
  "Goals": ["12345"],
  "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT"
}
```
