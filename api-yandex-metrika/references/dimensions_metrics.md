# Dimensions & Metrics — шпаргалка

Все поля имеют префикс пространства: `ym:s:` (визиты), `ym:pv:` (просмотры), `ym:u:` (пользователи).

90% отчётов строится на `ym:s:*`.

## Метрики (числовые показатели)

| Метрика | Что показывает |
|---------|---------------|
| `ym:s:visits` | Визиты |
| `ym:s:users` | Уникальные пользователи |
| `ym:s:pageviews` | Просмотры страниц |
| `ym:s:bounceRate` | Отказы (% визитов с 1 просмотром и <15 сек) |
| `ym:s:pageDepth` | Средняя глубина (страниц на визит) |
| `ym:s:avgVisitDurationSeconds` | Среднее время на сайте, сек |
| `ym:s:goalreaches` | Достижений ВСЕХ целей |
| `ym:s:goal<N>reaches` | Достижений конкретной цели N |
| `ym:s:goalConversion` | Общая конверсия в цель, % |
| `ym:s:goal<N>conversion` | Конверсия конкретной цели |
| `ym:s:newUsers` | Новые пользователи |
| `ym:s:returnUsersCount` | Вернувшиеся |
| `ym:s:ecommercePurchases` | Транзакции (для интернет-магазинов) |
| `ym:s:ecommerceRevenue` | Доход в рублях |

## Dimensions (группировки)

| Dimension | Группировка по… |
|-----------|-----------------|
| `ym:s:date` | Дате (YYYY-MM-DD) |
| `ym:s:datePeriod<month\|week\|day>` | По месяцам/неделям/дням |
| `ym:s:trafficSource` | Источнику: `organic`, `ad`, `direct`, `referral`, `social`, `internal`, `recommend`, `saved`, `mailing` |
| `ym:s:sourceEngine` | Конкретный источник: Yandex, Google, VK, Direct, email... |
| `ym:s:UTMSource` | utm_source (yandex, google, vk_ads, ...) |
| `ym:s:UTMMedium` | utm_medium (cpc, cpm, email, ...) |
| `ym:s:UTMCampaign` | utm_campaign |
| `ym:s:UTMContent` | utm_content |
| `ym:s:searchPhrase` | Поисковой фразе (где возможно) |
| `ym:s:searchEngineRoot` | Корневому поисковику (Yandex, Google, Mail...) |
| `ym:s:searchEngine` | Конкретному поисковику с указанием площадки (`Yandex, search results`, `Google, search results`, `Yandex.Maps`, `DuckDuckGo`) |
| `ym:s:startURL` | Странице входа (landing page) — куда зашёл визит. ⚠️ Не `ym:s:landingPage` — этого поля нет, API вернёт 400 |
| `ym:s:endURL` | Странице выхода |
| `ym:s:regionCountry` | Страна |
| `ym:s:regionCity` | Город |
| `ym:s:deviceCategory` | desktop / mobile / tablet |
| `ym:s:browser` | Браузер |
| `ym:s:operatingSystem` | ОС |
| `ym:s:pageViews` | Группировка по глубине (1, 2-3, 4-10, >10) |

## Типичные запросы

### Визиты с Директа за месяц
```
metrics=ym:s:visits
filters=ym:s:trafficSource=='ad'
date1=2026-03-01&date2=2026-03-31
```

### Визиты по дням
```
metrics=ym:s:visits,ym:s:users
dimensions=ym:s:date
date1=2026-03-01&date2=2026-03-31
sort=ym:s:date
```

### Топ страниц
```
metrics=ym:pv:pageviews
dimensions=ym:pv:URL
sort=-ym:pv:pageviews
limit=20
```
⚠️ Тут `ym:pv:` — пространство просмотров, не визитов!

### Конверсия рекламы
```
metrics=ym:s:visits,ym:s:goalreaches,ym:s:goalConversion
filters=ym:s:trafficSource=='ad'
```

### Реальные посетители (без зарубежных ботов)
```
metrics=ym:s:visits
dimensions=ym:s:regionCity
filters=ym:s:regionCountry=='Россия'
sort=-ym:s:visits
```

## Типичные ошибки и грабли

- ❌ `ym:s:landingPage` — **такого поля НЕТ.** API вернёт HTTP 400. Правильное: `ym:s:startURL`.
- ❌ `ym:s:goalConversion` без настроенных целей в счётчике → HTTP 400. У сайтов клиентов часто Метрика подключена без целей. Перед запросом проверь `scripts/goals_report.py <counter>` — если список пустой, не запрашивай конверсию.
- ❌ `ym:s:visits>100` — метрики нельзя в `filters`, только dimensions/значения dim.
- ❌ Несовместимые пространства: `ym:pv:URL` (просмотры) и `ym:s:visits` (визиты) — в одном запросе **нельзя**. Под URL страниц → метрики `ym:pv:*`. Под URL входа в визит → `ym:s:startURL` + `ym:s:visits`.

## Полный список полей

https://yandex.ru/dev/metrika/ru/stat/api/api-fields
