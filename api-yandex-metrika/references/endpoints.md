# Яндекс.Метрика API — Endpoints

Base URL: `https://api-metrika.yandex.net`

Все запросы требуют заголовок:
```
Authorization: OAuth {token}
```
⚠️ Именно `OAuth`, НЕ `Bearer`.

---

## Stat API — статистика

### `/stat/v1/data`

Главный endpoint для любой статистики.

```http
GET /stat/v1/data
  ?ids={counterId}
  &metrics=ym:s:visits,ym:s:users,...
  &dimensions=ym:s:date,...     # опционально
  &date1=2026-03-01
  &date2=2026-03-31
  &filters=ym:s:trafficSource=='ad'   # опционально
  &sort=-ym:s:visits              # опционально (- = по убыванию)
  &accuracy=full                  # full = точные данные
  &limit=100
```

**Response:**
```json
{
  "data": [
    {
      "dimensions": [{"name": "value_name", "id": "..."}],
      "metrics": [123.0, 456.0]
    }
  ],
  "totals": [sumVisits, sumUsers, ...],
  "total_rows": 42,
  "query": { /* эхо запроса */ }
}
```

Если `dimensions` не указан — `data` будет пустой, а `totals` — сумма по всем.

---

## Management API — настройки

### Список счётчиков аккаунта

```http
GET /management/v1/counters
```

### Цели счётчика

```http
GET /management/v1/counter/{counterId}/goals
```

Возвращает массив `goals[]` с `id`, `name`, `type`, `conditions`.

### Детали счётчика

```http
GET /management/v1/counter/{counterId}
```

---

## Logs API — сырой лог визитов (продвинутое)

```http
POST /management/v1/counter/{counterId}/logrequests
```

Для выгрузки всех визитов построчно. Процесс асинхронный: создать request → ждать статус `processed` → скачать parts.

Редко нужен — обычно хватает stat/v1/data.

---

## OAuth (получение токена)

```http
GET https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}
```

Пользователь авторизуется → редирект с `?code=...`:

```http
POST https://oauth.yandex.ru/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code={CODE}&client_id={ID}&client_secret={SECRET}
```

Response: `access_token`, `refresh_token`, `expires_in` (обычно 1 год).

### Refresh токена

```http
POST https://oauth.yandex.ru/token

grant_type=refresh_token&refresh_token={REFRESH}&client_id={ID}&client_secret={SECRET}
```

---

## Коды ошибок

- `401` — невалидный токен → обновить
- `403` — нет доступа к счётчику → проверить права OAuth приложения
- `429` — rate limit (редко, лимит щедрый ~30 req/sec)
- `400` — невалидные параметры (часто: неизвестная dimension/metric)

---

## Официальная документация

- https://yandex.ru/dev/metrika/ru/
- Список dimensions/metrics: https://yandex.ru/dev/metrika/ru/stat/api/api-fields
- Management: https://yandex.ru/dev/metrika/ru/management/
