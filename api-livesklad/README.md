# api-livesklad — Claude Code Skill

Готовый скилл для работы с API [LiveSklad](https://livesklad.com) — CRM для сервисных центров.

Позволяет Claude Code в одну команду выгружать заказы, считать выручку/маржу, разбивать клиентов по источникам (howKnow), топить бренды и проблемы — без ручной работы в админке.

## Что умеет

- ✅ Полный отчёт за месяц: 113+ заказов с автоматическим обходом rate limit
- ✅ Источники клиентов (Яндекс карты, 2ГиС, Директ, повторные и т.д.)
- ✅ Выручка, себестоимость, маржа (из `positions[].purchasePriceSumm`)
- ✅ Топ брендов, моделей, проблем
- ✅ Инкрементальное кэширование — не теряет прогресс при падении
- ✅ Работает напрямую через `urllib` — без зависимостей

## Установка

**Через Claude Code одной командой:**
```
установи скилл из https://github.com/salto-agancy/api-livesklad-skill
```

**Вручную:**
```bash
git clone https://github.com/salto-agancy/api-livesklad-skill ~/.claude/skills/api-livesklad
```

## Настройка

1. Создай `~/.config/livesklad/.env`:
   ```
   LIVESKLAD_API_LOGIN=<login из кабинета>
   LIVESKLAD_API_PASSWORD=<password>
   LIVESKLAD_SHOP_ID=<shop_id>
   ```

2. Где взять креды:
   - Кабинет LiveSklad → Настройки → API
   - `LIVESKLAD_SHOP_ID`: запусти `python3 scripts/fetch_how_knows.py` после auth — увидишь в логах, или выгрузи через `GET /shops`

3. Проверь:
   ```bash
   python3 scripts/auth.py
   # Auth OK. Token (first 10 chars): abc123... Remaining: 99
   ```

## Быстрый старт

```bash
# Прошлый месяц, полный отчёт
python3 scripts/fetch_monthly_report.py

# Конкретный месяц
python3 scripts/fetch_monthly_report.py 2026-03

# Произвольный диапазон
python3 scripts/fetch_monthly_report.py 2026-03-01 2026-03-15
```

**Вывод:**
```
============================================================
  LiveSklad отчёт: 2026-03-01 → 2026-04-01
============================================================
Всего заказов: 113
Выручка:           695 550 ₽
Себестоимость:     178 200 ₽
Маржа:             517 350 ₽ (74.4%)
Средний чек:         6 155 ₽

--- Источники клиентов (howKnow) ---
  Яндекс карты                          42
  Повторное обращение                   28
  Проходил мимо                         15
  2ГиС                                  12
  ...

--- Бренды устройств ---
  Apple                   33
  Samsung                 17
  Xiaomi                  11
  ...
```

Данные сохраняются в `~/.cache/livesklad/` — следующий запуск не перекачает ничего.

## Структура

- `SKILL.md` — инструкция для Claude (загружается автоматически при триггерах)
- `scripts/` — готовые Python скрипты
- `references/` — глубокая документация: endpoints, rate limits, gotchas
- `examples/` — примеры ответов API

## Триггеры Claude Code

Скилл активируется автоматически когда пишешь:
- "выгрузи заказы из livesklad"
- "посчитай выручку за март"
- "откуда приходят клиенты"
- "себестоимость ремонтов"
- "аналитика по livesklad"

## Безопасность

- ✅ Креды только в `~/.config/livesklad/.env` (не в git)
- ✅ Скрипты не логируют пароли
- ✅ `.gitignore` блокирует `.env` и `~/.cache/`
- ⚠️ Не коммить `~/.cache/livesklad/*.json` — там могут быть ПДн клиентов

## Ограничения API

- Rate limit: **100 запросов / 15 мин** (обходится через re-auth каждые 70 сек)
- `howKnow` и `purchasePrice` доступны **только** в `GET /orders/{id}`, не в list
- Для отчёта за месяц с 200 заказами — ~3 минуты из-за пауз

Подробнее в `references/rate_limits.md` и `references/gotchas.md`.

## Официальная документация

https://developer.livesklad.com/

## Лицензия

MIT — используй, модифицируй, шарь.

## Автор

Salto Agency — @dimamakesalto  
Вопросы и предложения: telegram @salto_dima

---

**Проверено на практике** на боевом аккаунте сервисного центра в Москве (113 заказов/мес, 75% маржа, источники от Яндекс.Карт до "Проходил мимо").
