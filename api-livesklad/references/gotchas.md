# LiveSklad — подводные камни

Всё, на чём можно потерять несколько часов.

## 1. `/orders/{id}` а не `/shops/{shopId}/orders/{id}`

**Самое частое**: endpoint для деталей заказа — **без `/shops/`**.

```
❌ GET /shops/{shopId}/orders/{id}   → 404 Not Found
✅ GET /orders/{id}                    → полный заказ с howKnow, positions
```

List endpoint — наоборот, с `/shops/`:
```
GET /shops/{shopId}/orders   ← list
GET /orders/{id}              ← detail
```

## 2. Формат dateCreate

Это **массив в URL**, не два отдельных параметра:

```
✅ dateCreate=[1740787200000,1743465600000]
   (URL-encoded: dateCreate=%5B1740787200000%2C1743465600000%5D)

Альтернатива (тоже работает):
✅ dateCreate[]=1740787200000&dateCreate[]=1743465600000

❌ dateFrom=...&dateTo=...    ← не работает, будет 500 или пустой ответ
```

## 3. Unix ms, не секунды

```python
start_ms = int(datetime.datetime(2026, 3, 1).timestamp() * 1000)  # * 1000!
```

## 4. `Authorization: {token}` БЕЗ Bearer

```python
req.add_header('Authorization', token)  # ✅
# НЕ
req.add_header('Authorization', f'Bearer {token}')  # ❌ 401
```

## 5. `summ` — dict, не число

```python
# list:
summ = order['summ']  # { price, soldPrice }
# detail:
summ = order['summ']  # { price, soldPrice, purchasePrice }
```

Всегда `summ.get('soldPrice')`, не `order['summ']`.

## 6. `summ.purchasePrice` только в detail

В list endpoint нет себестоимости. Для маржи нужны детали каждого заказа.

Есть 2 варианта источника себестоимости в detail:
- `summ.purchasePrice` — общая себестоимость заказа
- `positions[].purchasePriceSumm` — по каждой работе/запчасти отдельно

Суммы по positions должны сходиться с `summ.purchasePrice`. На практике бывают расхождения (скидки, надбавки) — доверяй `summ.purchasePrice`.

## 7. `howKnow` только в detail

В list endpoint нет источника клиента. Для отчёта по источникам надо качать все детали.

Иногда `howKnow` null — клиент не заполнил или выбрал "-" (пустой источник).

## 8. `device` в list — строка, в detail — разбитая

```
list:   "device": "Samsung A54"
detail: "brand": "Samsung", "model": "A54"
```

Для нормализации — всегда используй detail.brand/model. В list можно грубо `device.split()[0]` как fallback.

## 9. Статусы `type`

```
status.type == 'closed'  → ВЫДАН, ОТКАЗ, НЕ ПОЧИНЕНО
status.type == 'open'    → в работе
```

Для выручки фильтруй по `type == 'closed'` И `status.name == 'ВЫДАН'` (не отказ).

## 10. `remainRequest` может "отставать"

В одном токене remainRequest инкрементально уменьшается на каждый запрос. Но если параллельно сделать второй токен — они делят общий лимит аккаунта.

**Не делай параллельных запросов** — лимит один на весь аккаунт.

## 11. При 429 на auth — это защита от bruteforce

5 попыток auth с неправильным паролем → 429 на 5-15 минут. Проверь creds в `.env`.

## 12. Пустые заказы

Заказы со статусом "Гарантия" часто имеют `summ.soldPrice = 0`. Учитывай при подсчёте среднего чека (фильтруй `> 0`).
