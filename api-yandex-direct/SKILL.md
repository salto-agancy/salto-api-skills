---
name: api-yandex-direct
description: "Яндекс.Директ API v5 — расход, клики, показы, конверсии, кампании, поисковые запросы. Триггеры: директ, яндекс директ, отчёт директ, CTR, CPA, CPC, кампании директа, поисковые запросы, search queries, минус-фразы, direct report"
---

# Яндекс.Директ API v5 — Skill

Работа с API Яндекс.Директа: отчёты по кампаниям, объявлениям, поисковым запросам, минус-фразы, проверка баллов (Units).

Один OAuth-токен работает и для Метрики, и для Директа.

---

## Workflow для Claude (всё под ключ)

### Если пользователь впервые работает со скиллом

1. Проверь токен:
   ```bash
   test -f ~/.config/yandex-direct/.env && grep -q YANDEX_DIRECT_TOKEN ~/.config/yandex-direct/.env && echo "есть" || echo "нет"
   ```

2. **Если нет токена**:
   - Если есть скилл `api-yandex-metrika` — дёрни оттуда workflow OAuth (он создаст токен один раз для Метрики + Директа).
   - Если только Директ нужен — повтори те же шаги OAuth, см. `references/create_yandex_app.md` в скилле api-yandex-metrika.

3. Дополнительно для Директа: спроси у пользователя **логин клиента** (если Директ агентский):
   ```bash
   echo "YANDEX_DIRECT_LOGIN=<логин клиента в Директе>" >> ~/.config/yandex-direct/.env
   ```
   
   **Как узнать логин**: спроси пользователя — это логин кабинета Директа клиента (НЕ агентский!). У агентств видно в Direct Pro в списке клиентов.

4. Проверка:
   ```bash
   python3 scripts/units_check.py
   ```
   Если показывает баланс Units — значит токен и логин рабочие.

### Если пользователь хочет отчёт

Просто запусти нужный скрипт:

```bash
python3 scripts/monthly_report.py 2026-03           # CAMPAIGN_PERFORMANCE_REPORT
python3 scripts/search_queries.py 2026-03           # реальные поисковые фразы + кандидаты в минус-слова
python3 scripts/campaigns_list.py                   # список кампаний с бюджетами
python3 scripts/units_check.py                       # сколько баллов осталось
```

---

## Что важно знать (для Claude)

### Headers Reports API (все обязательны!)

```
Authorization: Bearer {token}
Client-Login: {логин клиента}      # без него = данные агентства
Accept-Language: ru
processingMode: auto
returnMoneyInMicros: false          # деньги в рублях, иначе ×1 000 000
skipReportHeader: true              # без этого в TSV мусор
skipColumnHeader: false             # оставляем — нужны имена колонок
skipReportSummary: true
Accept-Encoding: gzip               # ответы большие
```

### Async polling

Reports API может вернуть `201/202` — значит «формируется, приди позже». Заголовок `retryIn` — секунд до следующей попытки. Скрипт `scripts/reports.py` это делает автоматически.

### Units (баллы) вместо req/sec

В Директе нет лимита запросов в минуту — есть **дневной лимит баллов**. Каждый запрос = 1+ Units, ошибки = 20 Units. Следи за `Units: spent/remaining/daily` в header ответа.

### `ReportName` уникален

Каждый запрос отчёта должен иметь уникальный `ReportName` (timestamp в имени), иначе 400.

### `Use-Operator-Units: true` для агентств

Списывает баллы с агентского аккаунта, а не с клиентского. Полезно если делаешь отчёты пачкой.

---

## Типы отчётов (`ReportType`)

| Type | Что показывает |
|------|---------------|
| `ACCOUNT_PERFORMANCE_REPORT` | Весь аккаунт |
| `CAMPAIGN_PERFORMANCE_REPORT` | По кампаниям |
| `ADGROUP_PERFORMANCE_REPORT` | По группам объявлений |
| `AD_PERFORMANCE_REPORT` | По объявлениям |
| `CRITERIA_PERFORMANCE_REPORT` | По ключам |
| `SEARCH_QUERY_PERFORMANCE_REPORT` | **Реальные поисковые запросы** ⭐ |
| `CUSTOM_REPORT` | Произвольные группировки |

## Безопасность

- ✅ Токен только в `~/.config/yandex-direct/.env` (`chmod 600`)
- ✅ Скилл не использует общее приложение Salto — у каждого свой ClientID
- ✅ В git ничего не уходит
- ⚠️ Токен и логин клиента — не публиковать

## Документация

- https://yandex.ru/dev/direct/
- Reports: https://yandex.ru/dev/direct/doc/ru/reports/reports
- Reference v5: https://yandex.ru/dev/direct/doc/ru/ref-v5/v5

См. также:
- `references/endpoints.md` — все endpoints
- `references/report_types.md` — 7 типов отчётов
- `references/fields.md` — поля и фильтры
- `references/rate_limits.md` — Units и параллельность
