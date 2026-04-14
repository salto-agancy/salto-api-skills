"""
Получение OAuth-токена для Яндекс.Метрики и Яндекс.Директа.

Один токен работает для обоих API (если приложение зарегистрировано
с двумя scopes: metrika:read + direct:api-light).

ПЕРЕД ЗАПУСКОМ:
1. Создай OAuth-приложение на https://oauth.yandex.ru/client/new
2. Подробная инструкция: references/create_yandex_app.md (5 минут)
3. Скопируй ClientID и Client Secret из карточки приложения

Скрипт:
  - Спросит ClientID и Client Secret
  - Откроет браузер на странице авторизации
  - Попросит ввести 7-значный код
  - Сохранит токен в ~/.config/yandex-metrika/.env
  - Сохранит тот же токен в ~/.config/yandex-direct/.env
"""
import os
import sys
import webbrowser
import urllib.request
import urllib.parse
import json
import datetime


METRIKA_DIR = os.path.expanduser('~/.config/yandex-metrika')
DIRECT_DIR = os.path.expanduser('~/.config/yandex-direct')


def save_env(env_path, updates):
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    existing = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    existing[k] = v
    existing.update(updates)
    with open(env_path, 'w') as f:
        for k, v in existing.items():
            f.write(f'{k}={v}\n')
    os.chmod(env_path, 0o600)


def main():
    print('=' * 60)
    print('  Получение OAuth-токена Яндекс.Метрика + Директ')
    print('=' * 60)
    print()
    print('Перед запуском нужно создать OAuth-приложение на Яндексе.')
    print('Если ещё не создал — открой инструкцию:')
    print('  references/create_yandex_app.md')
    print('или https://oauth.yandex.ru/client/new')
    print()

    # Шаг 1: креды приложения
    print('Шаг 1. Введи данные приложения')
    print('-' * 40)
    client_id = input('ClientID (32 символа из карточки приложения): ').strip()
    if not client_id or len(client_id) < 30:
        print('Похоже на неправильный ClientID. Должно быть 32 символа.')
        sys.exit(1)

    client_secret = input('Client Secret (32 символа из карточки): ').strip()
    if not client_secret or len(client_secret) < 30:
        print('Похоже на неправильный Client Secret. Должно быть 32 символа.')
        sys.exit(1)

    # Сохраняем сразу — пригодится для refresh
    save_env(f'{METRIKA_DIR}/.env', {
        'YANDEX_CLIENT_ID': client_id,
        'YANDEX_CLIENT_SECRET': client_secret,
    })

    # Шаг 2: открываем браузер
    auth_url = f'https://oauth.yandex.ru/authorize?response_type=code&client_id={client_id}'

    print()
    print('Шаг 2. Авторизация в браузере')
    print('-' * 40)
    print('Сейчас откроется страница Яндекса.')
    print('Войди в нужный аккаунт (тот, к которому привязаны счётчики Метрики).')
    print('Нажми "Разрешить".')
    print()
    print(f'URL (если браузер не откроется автоматически):')
    print(f'  {auth_url}')
    print()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    input('Когда нажмёшь "Разрешить" — продолжи (Enter)...')

    # Шаг 3: ввод verification code
    print()
    print('Шаг 3. Введи 7-значный код')
    print('-' * 40)
    print('После согласия Яндекс показал страницу с кодом подтверждения.')
    print('Это 7 цифр, что-то вроде 1234567.')
    print()
    code = input('Введи код: ').strip()
    if not code or not code.isdigit() or len(code) != 7:
        print(f'Подозрительный код: "{code}". Должно быть 7 цифр.')
        retry = input('Всё равно попробовать? (y/N): ').strip().lower()
        if retry != 'y':
            sys.exit(1)

    # Обмен кода на токен
    print()
    print('Получаю токен от Яндекса...')

    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
    }).encode()

    req = urllib.request.Request('https://oauth.yandex.ru/token', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', errors='ignore')
        print(f'Ошибка {e.code}: {err}')
        print()
        print('Возможные причины:')
        print('  - неправильный код (попробуй ещё раз)')
        print('  - код уже использован (получи новый код через тот же URL)')
        print('  - неправильный ClientID или Client Secret (проверь карточку приложения)')
        sys.exit(1)

    if 'error' in resp:
        print(f'Ошибка: {resp}')
        sys.exit(1)

    token = resp['access_token']
    expires_in = resp.get('expires_in', 31536000)  # 1 год
    refresh = resp.get('refresh_token', '')
    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=expires_in)).date()

    # Сохраняем для Метрики
    metrika_update = {
        'YANDEX_METRIKA_TOKEN': token,
        'YANDEX_METRIKA_TOKEN_EXPIRES': expires_at.isoformat(),
    }
    if refresh:
        metrika_update['YANDEX_METRIKA_REFRESH_TOKEN'] = refresh
    save_env(f'{METRIKA_DIR}/.env', metrika_update)

    # Сохраняем для Директа (тот же токен)
    save_env(f'{DIRECT_DIR}/.env', {
        'YANDEX_DIRECT_TOKEN': token,
    })

    print()
    print('=' * 60)
    print('  ✓ Готово!')
    print('=' * 60)
    print(f'Токен сохранён:')
    print(f'  {METRIKA_DIR}/.env  (для Метрики)')
    print(f'  {DIRECT_DIR}/.env   (для Директа)')
    print(f'Действует до: {expires_at}')
    if refresh:
        print(f'Refresh token сохранён — токен можно автообновлять')
    print()

    # Быстрая проверка
    test = input('Проверить токен на счётчике? Введи counter_id (Enter — пропустить): ').strip()
    if test:
        try:
            from query import stat_query
            r = stat_query(test, 'ym:s:visits',
                          date1='2026-03-01', date2='2026-03-31', token=token)
            print(f'✓ Визиты за март 2026: {r["totals"][0]:,.0f}')
        except Exception as e:
            print(f'Ошибка проверки: {e}')
            print('Возможно, у этого аккаунта нет доступа к счётчику {test}.')


if __name__ == '__main__':
    main()
