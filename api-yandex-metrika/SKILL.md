---
name: api-yandex-metrika
description: "Яндекс.Метрика API — визиты, источники трафика, цели, рекламная статистика, Яндекс.Бизнес карточка. Триггеры: метрика, яндекс метрика, визиты сайта, трафик, цели метрики, яндекс бизнес, карточка организации, статистика сайта"
---

# Яндекс.Метрика API — Skill

Работа с API Яндекс.Метрики (api-metrika.yandex.net) — визиты, цели, источники трафика, фильтры по городам, по устройствам.

Также — метрики карточки Яндекс.Бизнес (переходы в профиль, клики по телефону, маршруты, переходы на сайт).

## Когда использовать

- Отчёт по визитам/пользователям за период
- Разбивка трафика по источникам (реклама, поиск, прямые, соцсети)
- Яндекс.Бизнес — метрики карточки организации
- Цели Метрики (заявки, клики по телефону)
- Фильтрация ботов/сканеров (для новых сайтов)
- Сравнение мобилки vs десктопа

## Быстрый старт

1. Создай `~/.config/yandex-metrika/.env`:
   ```
   YANDEX_METRIKA_TOKEN=<OAuth token>
   YANDEX_CLIENT_ID=<client_id (для refresh)>
   YANDEX_CLIENT_SECRET=<client_secret (для refresh)>
   ```
2. Запусти:
   ```bash
   python3 scripts/monthly_report.py <counter_id> 2026-03
   ```

## OAuth получение токена

Если токена нет, см. `scripts/get_oauth_token.py` — полный flow:
1. Создать приложение на https://oauth.yandex.ru/client/new (scope: metrika:read)
2. Запустить скрипт, открыть выданный URL, авторизоваться
3. Вставить code обратно в скрипт — он обменяет на токен

## Структура

```
api-yandex-metrika/
├── SKILL.md
├── README.md
├── scripts/
│   ├── get_oauth_token.py           # OAuth flow для получения токена
│   ├── query.py                     # универсальный query helper
│   ├── monthly_report.py            # визиты/пользователи/отказы за период
│   ├── traffic_sources.py           # разбивка по источникам (ad/organic/direct)
│   ├── ads_only.py                  # только рекламный трафик
│   ├── goals_report.py              # цели (заявки, звонки)
│   ├── business_card.py             # метрики карточки Яндекс.Бизнес
│   ├── cities.py                    # топ городов (фильтр ботов)
│   └── list_counters.py             # все счётчики аккаунта
├── examples/
│   ├── response_stat_v1.json        # пример ответа /stat/v1/data
│   └── dimensions_metrics.md        # популярные dimensions и metrics
└── references/
    ├── endpoints.md
    ├── dimensions_metrics.md        # шпаргалка по полям
    ├── filters.md                   # синтаксис фильтров
    └── yandex_business.md           # особенности карточки ЯБ
```

## Главное — что не очевидно

1. **Header**: `Authorization: OAuth {token}` — **именно `OAuth`**, не `Bearer`
2. **Токен один и тот же** для Метрики, Директа и Яндекс.Бизнес API (единый OAuth Яндекса)
3. **Яндекс.Бизнес метрики** получаются через Метрику карточки (отдельный счётчик на карточку)
4. **Показы рекламы ≠ визиты Метрики**. Показы — это Impressions Директа
5. **Боты**: новые сайты получают много ботов из Франкфурта/Амстердама/Бангкока. Фильтруй по `regionCity` для реальной картины
6. **Цели**: `goalreaches` — сумма всех целей, `goal<N>reaches` — конкретная цель по ID

## Счётчики в компании

В конфиге храни маппинг типа:
```
# ~/.config/yandex-metrika/counters.json
{
  "client-a-site": "12345678",
  "client-a-yandex-business": "87654321",
  "client-b-site": "11223344"
}
```

Удобно использовать в `scripts/monthly_report.py client-a-site 2026-03`.

## Документация

- https://yandex.ru/dev/metrika/ru/
- https://yandex.ru/dev/metrika/ru/stat/v1/
- Список полей: https://yandex.ru/dev/metrika/ru/stat/api/api-fields

## Безопасность

Скилл читает токен ТОЛЬКО из `~/.config/yandex-metrika/.env`. В коде и логах токен не печатается.
