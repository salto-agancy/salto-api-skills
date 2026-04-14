# Яндекс.Директ API v5 — Endpoints

Base URL: `https://api.direct.yandex.com/json/v5`

Песочница: `https://api-sandbox.direct.yandex.com/json/v5`

## Общие headers

```
Authorization: Bearer {token}
Client-Login: {логин рекламодателя}   # для агентств — обязательно
Accept-Language: ru
Content-Type: application/json; charset=utf-8
Accept-Encoding: gzip                  # ответы большие
```

Для агентств:
```
Use-Operator-Units: true    # баллы спишутся с агентского аккаунта
```

## Reports API

### POST /reports

Единственный endpoint для всех отчётов.

**Headers (специфичные):**
```
processingMode: auto         | online | offline | offline_batch
returnMoneyInMicros: false   | true (иначе числа в микрорублях)
skipReportHeader: true       | false
skipColumnHeader: false      | true (если false — первая строка = имена полей)
skipReportSummary: true      | false (Total row)
```

**Body:**
```json
{
  "params": {
    "SelectionCriteria": {
      "DateFrom": "2026-03-01",
      "DateTo": "2026-03-31",
      "Filter": [
        {"Field": "Impressions", "Operator": "GREATER_THAN", "Values": ["0"]}
      ]
    },
    "FieldNames": ["CampaignName", "Impressions", "Clicks", "Cost"],
    "Goals": ["12345", "67890"],     
    "AttributionModels": ["LC", "FC", "LYDC"],
    "OrderBy": [{"Field": "Clicks", "SortOrder": "DESCENDING"}],
    "ReportName": "unique-name-1234567890",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "CUSTOM_DATE",
    "Format": "TSV",
    "IncludeVAT": "YES",
    "IncludeDiscount": "NO",
    "Page": {"Limit": 1000, "Offset": 0}
  }
}
```

**Response:**
- `200 OK` — TSV в body (парсить)
- `201 Created` — поставлен в очередь. Header `retryIn` — сек до следующей попытки
- `202 Accepted` — формируется. Header `retryIn`
- `400 Bad Request` — ошибки в параметрах
- `500/502/503` — попробовать позже

Polling: на 201/202 — ждать `retryIn` секунд, повторять тот же запрос.

### DateRangeType варианты

Вместо `CUSTOM_DATE` можно:
- `TODAY`, `YESTERDAY`
- `LAST_WEEK`, `THIS_WEEK`
- `LAST_MONTH`, `THIS_MONTH`
- `LAST_5_DAYS`, `LAST_30_DAYS`, `LAST_90_DAYS`
- `LAST_365_DAYS`, `AUTO`

С `AUTO` нужен DateFrom/DateTo в SelectionCriteria.

## Campaigns

### POST /campaigns — метод `get`

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [12345, 67890],
      "States": ["ON", "SUSPENDED"],
      "Types": ["TEXT_CAMPAIGN", "SMART_CAMPAIGN"]
    },
    "FieldNames": ["Id", "Name", "Type", "Status", "State",
                   "StartDate", "EndDate", "DailyBudget", "Funds"],
    "TextCampaignFieldNames": ["BiddingStrategy", "CounterIds"]
  }
}
```

## Ads

### POST /ads — `get`
Список объявлений. Аналогично Campaigns.

## AdGroups

### POST /adgroups — `get`

## Keywords

### POST /keywords — `get`
Ключевые фразы.

## Changes

### POST /changes — `check`

Проверка изменений с timestamp. Полезно для инкрементальных sync:
```json
{
  "method": "check",
  "params": {
    "Timestamp": "2026-03-13T12:00:00Z",
    "CampaignIds": [12345]
  }
}
```

## Dictionaries

### POST /dictionaries

Справочники: регионы, валюты, языки, типы устройств и т.п.

## AgencyClients (для агентств)

### POST /agencyclients — `get`

Список всех клиентов агентства с их логинами (для `Client-Login` header).

## Документация

- https://yandex.ru/dev/direct/doc/ru/reports/reports
- https://yandex.ru/dev/direct/doc/ru/concepts/about
- Reference: https://yandex.ru/dev/direct/doc/ru/ref-v5/v5
