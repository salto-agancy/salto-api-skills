---
name: api-yandex-metrika
description: "Яндекс.Метрика API — визиты, источники трафика, цели, рекламная статистика, Яндекс.Бизнес карточка. Триггеры: метрика, яндекс метрика, визиты сайта, трафик, цели метрики, яндекс бизнес, карточка организации, статистика сайта"
---

# Яндекс.Метрика API — Skill

Работа с API Яндекс.Метрики (api-metrika.yandex.net) — визиты, цели, источники трафика, метрики карточки Яндекс.Бизнес.

Один и тот же OAuth-токен работает для Метрики и Директа.

---

## Workflow для Claude (всё под ключ)

### Если пользователь впервые работает со скиллом

Проверь: есть ли `~/.config/yandex-metrika/.env` с `YANDEX_METRIKA_TOKEN`?

```bash
test -f ~/.config/yandex-metrika/.env && grep -q YANDEX_METRIKA_TOKEN ~/.config/yandex-metrika/.env && echo "есть" || echo "нет"
```

**Если нет токена** — запусти процесс настройки (см. ниже).

**Если есть** — переходи сразу к запросу пользователя.

### Процесс настройки OAuth (Claude ведёт)

Цель: пользователь не должен лазить в терминал. Claude:
1. Сам открывает страницы Яндекса через `open <url>` (macOS) или `xdg-open` (Linux)
2. Подсказывает что выбрать на каждой странице
3. Просит у пользователя только то что Claude сам не может узнать (логин-пароль он сам не получит — это вводит пользователь в браузере)
4. Получает короткие данные через диалог (ClientID, Client Secret, 7-значный код)
5. Сам сохраняет креды и токен в `.env`

Шаги:

#### Шаг 1: Создание OAuth-приложения

Спроси у пользователя: *«Есть уже OAuth-приложение Яндекса? (Если не уверен — нет.)»*

**Если нет**:
1. Открой страницу создания: `open https://oauth.yandex.ru/client/new`
2. Сообщи пользователю текстом:
   > Открыл страницу создания приложения. Заполни так:
   > - **Название**: «Salto Reports» (любое)
   > - **Платформа**: Веб-сервисы
   > - **Redirect URI**: `https://oauth.yandex.ru/verification_code` (скопируй точно)
   > - **Доступ**: отметь «Яндекс.Метрика → Получение статистики» и «Яндекс.Директ → Использование API в режиме чтения»
   > - Нажми «Создать приложение»
   >
   > Когда создашь — пришли мне ClientID и Client Secret из карточки приложения (по 32 символа).
3. Дождись от пользователя ClientID и Client Secret.
4. Сохрани:
   ```bash
   mkdir -p ~/.config/yandex-metrika && chmod 700 ~/.config/yandex-metrika
   cat > ~/.config/yandex-metrika/.env <<'EOF'
   YANDEX_CLIENT_ID=<from user>
   YANDEX_CLIENT_SECRET=<from user>
   EOF
   chmod 600 ~/.config/yandex-metrika/.env
   ```

**Если есть** — попроси у пользователя ClientID и Client Secret из карточки существующего приложения, сохрани так же.

#### Шаг 2: Авторизация и получение кода

1. Открой страницу авторизации:
   ```bash
   open "https://oauth.yandex.ru/authorize?response_type=code&client_id=<CLIENT_ID>"
   ```
2. Сообщи пользователю:
   > Открыл страницу авторизации Яндекса. Войди в нужный аккаунт (тот, к которому привязаны счётчики Метрики), нажми «Разрешить».
   > После этого Яндекс покажет 7-значный КОД ПОДТВЕРЖДЕНИЯ. Пришли его мне.
3. Дождись 7-значного кода от пользователя.

#### Шаг 3: Обмен кода на токен

```bash
CODE=<7 цифр от пользователя>
CLIENT_ID=$(grep YANDEX_CLIENT_ID ~/.config/yandex-metrika/.env | cut -d= -f2)
CLIENT_SECRET=$(grep YANDEX_CLIENT_SECRET ~/.config/yandex-metrika/.env | cut -d= -f2)

curl -s -X POST https://oauth.yandex.ru/token \
  -d grant_type=authorization_code \
  -d code=$CODE \
  -d client_id=$CLIENT_ID \
  -d client_secret=$CLIENT_SECRET
```

Получишь JSON с `access_token`, `refresh_token`, `expires_in`.

#### Шаг 4: Сохранение токена

```bash
TOKEN=<access_token из ответа>
EXPIRES=<вычислить дату через expires_in секунд от сегодня>

# Метрика
cat >> ~/.config/yandex-metrika/.env <<EOF
YANDEX_METRIKA_TOKEN=$TOKEN
YANDEX_METRIKA_TOKEN_EXPIRES=$EXPIRES
YANDEX_METRIKA_REFRESH_TOKEN=<refresh_token>
EOF

# Директ — тот же токен
mkdir -p ~/.config/yandex-direct && chmod 700 ~/.config/yandex-direct
cat > ~/.config/yandex-direct/.env <<EOF
YANDEX_DIRECT_TOKEN=$TOKEN
EOF
chmod 600 ~/.config/yandex-direct/.env
```

#### Шаг 5: Проверка

```bash
python3 scripts/list_counters.py
```

Покажи пользователю список его счётчиков. Спроси: «Какой считаем?»

Если есть запасной CLI-вариант: `scripts/get_oauth_token.py` (интерактивный) — но в большинстве случаев Claude должен оркестрировать процесс сам, как описано выше.

---

## Что делает скилл (после настройки)

- Месячный отчёт: визиты, пользователи, отказы, глубина, время на сайте
- Разбивка по источникам (реклама / поиск / прямые / соцсети)
- Только рекламный трафик (фильтр `trafficSource=='ad'`)
- Топ городов (отделяет ботов из зарубежья)
- Цели Метрики: список + достижения + конверсии
- Яндекс.Бизнес карточка: клики по телефону, маршруты, переходы на сайт
- Сравнение двух периодов одним запросом
- Logs API — выгрузка сырых визитов

## Безопасность

- ✅ У каждого пользователя СВОЙ ClientID + Client Secret. Скилл не использует общее приложение
- ✅ Креды только в `~/.config/yandex-metrika/.env` (`chmod 600`)
- ✅ В git не уходят (`.gitignore`)
- ✅ Скрипт открытый — можно проверить что отправляется только в Яндекс
- ⚠️ Client Secret — это пароль приложения, не выкладывать в публичные репо

## Документация

- https://yandex.ru/dev/metrika/ru/
- Поля API: https://yandex.ru/dev/metrika/ru/stat/api/api-fields
- OAuth Яндекса: https://yandex.ru/dev/id/doc/dg/oauth/

См. также:
- `references/create_yandex_app.md` — пошаговая регистрация приложения (если Claude нужно сослаться)
- `references/endpoints.md` — все API endpoints
- `references/dimensions_metrics.md` — поля для запросов
- `references/filters.md` — синтаксис фильтров
- `references/yandex_business.md` — особенности карточки Я.Бизнес
- `references/advanced.md` — атрибуция, drill-down, Logs API
