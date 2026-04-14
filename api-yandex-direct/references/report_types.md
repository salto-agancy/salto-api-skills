# 7 типов отчётов Директа

## ACCOUNT_PERFORMANCE_REPORT
Весь аккаунт одной строкой (по дням можно через `Date` в FieldNames).

**Когда**: общий итог «сколько потратили и получили за месяц».

**Fields**: `Date, Impressions, Clicks, Cost, Conversions, Ctr, AvgCpc`

## CAMPAIGN_PERFORMANCE_REPORT
По кампаниям.

**Когда**: найти неэффективные кампании, распределить бюджет.

**Fields**: `CampaignName, CampaignId, CampaignType, Impressions, Clicks, Cost, Ctr, AvgCpc, Conversions, CostPerConversion, ConversionRate`

## ADGROUP_PERFORMANCE_REPORT
По группам объявлений (внутри кампаний).

**Когда**: глубже, чем кампания — увидеть какая группа работает.

**Fields**: +`AdGroupName, AdGroupId`

## AD_PERFORMANCE_REPORT
По отдельным объявлениям.

**Когда**: A/B тесты объявлений, понять какой креатив работает лучше.

**Fields**: +`AdId, AdFormat`

## CRITERIA_PERFORMANCE_REPORT
По условиям показа (ключевые фразы, ретаргетинг, интересы).

**Когда**: оптимизация ставок на конкретные ключи.

**Fields**: `CriterionId, Criterion, CriterionType, CampaignName, Impressions, Clicks, Cost, Conversions`

## SEARCH_QUERY_PERFORMANCE_REPORT ⭐
**Реальные поисковые запросы** пользователей.

**Когда**: САМЫЙ ценный отчёт:
- Собрать минус-фразы (нерелевантные дорогие запросы)
- Найти новые ключи (запросы с конверсиями, которых нет в семантике)
- Понять как клиент ищет

**Fields**: `Query, MatchType, CampaignName, AdGroupName, Keyword, Impressions, Clicks, Cost, Conversions`

## CUSTOM_REPORT
Произвольные группировки. Можно комбинировать практически любые поля из всех отчётов.

**Когда**: нужен специфичный срез, которого нет в готовых.

---

## Как выбрать тип

| Задача | Отчёт |
|--------|-------|
| Общий расход за месяц | `ACCOUNT_PERFORMANCE_REPORT` |
| Какая кампания эффективнее | `CAMPAIGN_PERFORMANCE_REPORT` |
| Какое объявление лучше кликают | `AD_PERFORMANCE_REPORT` |
| Какие ключи приносят заявки | `CRITERIA_PERFORMANCE_REPORT` |
| Что реально ищут клиенты | `SEARCH_QUERY_PERFORMANCE_REPORT` |
| Свой специфичный срез | `CUSTOM_REPORT` |
