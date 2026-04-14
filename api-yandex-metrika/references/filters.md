# Filters — синтаксис фильтров

Параметр `filters` в запросе к `/stat/v1/data`.

## Операторы

| Оператор | Значение | Пример |
|----------|----------|--------|
| `==` | Равно | `ym:s:trafficSource=='ad'` |
| `!=` | Не равно | `ym:s:regionCity!='Москва'` |
| `>`, `<`, `>=`, `<=` | Сравнение (числа) | `ym:s:pageDepth>=3` |
| `=@` | Содержит подстроку | `ym:pv:URL=@'/contact'` |
| `!@` | Не содержит | `ym:s:sourceEngine!@'bot'` |
| `=~` | Регулярное выражение | `ym:pv:URL=~'/(cart\|checkout)/'` |
| `=*` | Начинается с | `ym:s:UTMSource=*'yandex'` |

## Логика: AND / OR / NOT

| Комбинатор | Пример |
|------------|--------|
| `AND` | `ym:s:trafficSource=='ad' AND ym:s:regionCountry=='Россия'` |
| `OR` | `ym:s:trafficSource=='ad' OR ym:s:trafficSource=='direct'` |
| `NOT` | `NOT ym:s:regionCity=='Москва'` |

Скобки для приоритета:
```
(ym:s:trafficSource=='ad' AND ym:s:bounceRate<50) OR ym:s:goalreaches>0
```

## Кавычки и экранирование

- Строки — в одинарных кавычках: `'value'`
- Для апострофа внутри: экранируй `\'`
- URL-encode весь filter в запросе

## Примеры

### Только рекламный трафик из России
```
ym:s:trafficSource=='ad' AND ym:s:regionCountry=='Россия'
```

### Посетители из Москвы с мобильных
```
ym:s:regionCity=='Москва' AND ym:s:deviceCategory=='mobile'
```

### Визиты с конкретной UTM-кампанией
```
ym:s:UTMCampaign=='spring-2026-sale'
```

### Страница корзины
```
ym:pv:URL=@'/cart'
```

### Исключить внутренние переходы
```
ym:s:trafficSource!='internal'
```

### Конверсионные визиты (достигли цели)
```
ym:s:goalreaches>0
```

### Брендовый трафик (фраза содержит бренд)
```
ym:s:searchPhrase=@'название_бренда'
```

## URL-encoding

В Python:
```python
import urllib.parse
filters_raw = "ym:s:trafficSource=='ad' AND ym:s:regionCountry=='Россия'"
filters_enc = urllib.parse.quote(filters_raw)
# Или проще — через urllib.parse.urlencode({'filters': filters_raw})
```

## Типичные ошибки

- ❌ `ym:s:trafficSource=="ad"` — двойные кавычки (должны быть одинарные)
- ❌ `trafficSource=='ad'` — забыт префикс `ym:s:`
- ❌ `ym:s:visits>100` — **метрики нельзя** в filters, только dimensions
- ❌ `ym:s:date>'2026-03-01'` — для дат используй `date1`/`date2`, не filter
