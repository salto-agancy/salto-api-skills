# LiveSklad Rate Limits — стратегия обхода

## Лимит

**100 запросов на 15 минут** per аккаунт. После исчерпания — HTTP 429 до истечения окна.

Каждый ответ содержит поля:
- `remainRequest` — сколько осталось
- `expireDate` — когда сбросится окно

## Типичный сценарий

Отчёт за месяц в сервисном центре среднего размера:
- 1 запрос `/auth`
- 2-3 запроса `GET /shops/{shop}/orders` (пагинация по 50)
- **100-150 запросов `GET /orders/{id}`** (детали по каждому заказу)

Итого: ~120 запросов → 1 пауза 15 минут **или** 1 re-auth после 70 сек.

## Стратегия

### 1. Re-auth вместо ожидания 15 минут

Старый токен продолжает отдавать 429 пока не истечёт expireDate. **Но можно получить новый токен через 70 сек после первого 429** — лимит привязан к IP/аккаунту, а не токену. Новый токен даст свежие 100 запросов.

```python
if remaining <= 3:
    time.sleep(70)
    token, remaining = auth()  # fresh 100 reqs
```

### 2. Инкрементальное сохранение

Не теряй прогресс при падении скрипта:

```python
saved = {}
if os.path.exists(out_path):
    with open(out_path) as f:
        saved = {o['id']: o for o in json.load(f)}

for oid in todo:
    # ... fetch ...
    saved[oid] = detail
    if len(saved) % 20 == 0:
        with open(out_path, 'w') as f:
            json.dump(list(saved.values()), f)
```

### 3. Backoff на 429 при auth

Если **сам auth** отдал 429 (слишком много попыток auth подряд) — экспоненциальный бэкофф:

```python
for attempt in range(8):
    try:
        auth()
    except Http429:
        time.sleep(65 * (attempt + 1))  # 65, 130, 195, 260, ...
```

### 4. Порядок операций

Оптимально:
1. Auth → 99 reqs left
2. List pages (2-3 запроса) → 96-97 left
3. Detail × ~93 → 3 left
4. **Re-auth** → 99 fresh
5. Остальные детали

Это даёт один re-auth вместо паузы 15 минут.

## Чего НЕ делать

- ❌ Не делать auth в цикле — «на всякий случай». Один auth дорогой, re-use token.
- ❌ Не retry-ить детали заказов в tight loop при 429 — попадёшь на бан 403 на часы.
- ❌ Не делать пакетные детали без пауз — лимит страйкнёт через 90 сек работы.

## Мониторинг

```python
print(f'{done}/{total} | remaining={remaining} | ttl_left={ttl}s')
```

Всегда логируй `remaining` — помогает понять, когда вставлять `time.sleep(70)`.
