# LiveSklad API — Endpoints Reference

Base URL: `https://api.livesklad.com`

Все запросы (кроме `/auth`) требуют заголовок:
```
Authorization: {token}
```
⚠️ **БЕЗ** префикса `Bearer`!

---

## Auth

```http
POST /auth
Content-Type: application/x-www-form-urlencoded

login=<login>&password=<password>
```

**Response:**
```json
{
  "token": "abc123...",
  "ttl": 900,
  "remainRequest": 100,
  "expireDate": "2026-04-13T16:31:28.000Z"
}
```

- TTL: 15 минут (900 секунд)
- Rate limit: 100 запросов / 15 минут

---

## Shops

### List

```http
GET /shops
```

Возвращает магазины, к которым привязан аккаунт.

```json
{
  "data": [
    {
      "id": "655ca363dfbb6b05c5343bb0",
      "name": "Мастерская",
      "color": "#ff6666",
      "address": "",
      "phones": []
    }
  ]
}
```

---

## Orders

### List (базовые поля)

```http
GET /shops/{shopId}/orders?dateCreate=[<startMs>,<endMs>]&page=1&pageSize=50
```

URL-encoded: `dateCreate=%5B<start>%2C<end>%5D`

**Response keys:**
- `data[]` — заказы (базовые поля)
- `total` — всего заказов
- `page`, `pageSize`
- `remainRequest`, `expireDate`

**Поля заказа в list (неполные!):**
- `id`, `number` (например, "Б001761"), `dateCreate`, `deadline`
- `status` — `{ id, name, type: closed|open, color }`
- `counteragent` — `{ id, name, phones[] }`
- `typeOrder` — `{ id, name }` (категория: "1. Смартфон, планшет")
- `typeDevice` — строка ("Смартфон", "Ноутбук")
- `device` — строка ("Samsung A54") — **не объект!**
- `problem[]` — массив описаний
- `summ` — `{ price, soldPrice }` — **без purchasePrice!**
- `cash` — `{ summ }`

### Detail (ПОЛНЫЕ поля)

```http
GET /orders/{orderId}
```

⚠️ **НЕ** `/shops/{shopId}/orders/{id}` — тот эндпоинт 404!

**Response:**
```json
{
  "data": { /* полный заказ */ },
  "remainRequest": 99,
  "expireDate": "..."
}
```

**Дополнительные поля (которых НЕТ в list):**
- `howKnow` — `{ id, name }` (источник клиента)
- `brand` — строка ("Samsung") — отдельно от model
- `model` — строка ("A54")
- `positions[]` — работы и запчасти с ценами:
  ```json
  {
    "name": "Замена дисплея",
    "count": 1,
    "soldPriceSumm": 5000,
    "purchasePriceSumm": 2000,
    "modifyId": "..."
  }
  ```
- `appearance[]` — состояние устройства: "царапины", "потёртости"
- `completeSet[]` — комплектация: "устройство", "зарядка"
- `customFields[]` — произвольные поля
- `createManager`, `closeManager` — `{ id, name }`
- `cash.elements[]` — история платежей

---

## How-Knows (справочник источников)

```http
GET /how-knows
```

```json
{
  "data": [
    { "id": "655ca363dfbb6b05c5343b7c", "name": "2ГиС", "isRepeat": false },
    { "id": "655ca363dfbb6b05c5343b7d", "name": "Повторное обращение", "isRepeat": true },
    { "id": "66aa7bbb9ff95975053eca8b", "name": "Яндекс карты", "isRepeat": false }
  ]
}
```

---

## Sales (продажи товаров)

```http
GET /shops/{shopId}/sales?date=[<startMs>,<endMs>]&page=1&pageSize=50
```

⚠️ Фильтр `date` (не `dateCreate`!) — это продажи товаров/аксессуаров, а не ремонты.

---

## Другие endpoints (не проверено)

- `GET /positions` — справочник работ/запчастей
- `GET /counteragents` — клиенты
- `GET /statuses` — статусы заказов
- `GET /managers` — сотрудники

Полная документация: https://developer.livesklad.com/
