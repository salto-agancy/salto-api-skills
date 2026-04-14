"""
OAuth flow для получения токена Яндекс.Метрика + Директ (единый OAuth).

Шаги:
1. Создай приложение на https://oauth.yandex.ru/client/new
   Scopes:
   - metrika:read         (Метрика)
   - direct:api-light     (Директ, опционально)
2. Скопируй Client ID и Client Secret
3. Запусти этот скрипт — он откроет URL, авторизуйся, вставь code обратно
4. Скрипт сохранит токен в ~/.config/yandex-metrika/.env
"""
import os
import sys
import webbrowser
import urllib.request
import urllib.parse
import json


CONFIG_DIR = os.path.expanduser('~/.config/yandex-metrika')
ENV_PATH = f'{CONFIG_DIR}/.env'


def save_env(d):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    existing = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    existing[k] = v
    existing.update(d)
    with open(ENV_PATH, 'w') as f:
        for k, v in existing.items():
            f.write(f'{k}={v}\n')
    os.chmod(ENV_PATH, 0o600)


def main():
    print(__doc__)

    client_id = input('Client ID: ').strip()
    client_secret = input('Client Secret: ').strip()

    # Save immediately
    save_env({
        'YANDEX_CLIENT_ID': client_id,
        'YANDEX_CLIENT_SECRET': client_secret,
    })

    # Open authorize URL
    auth_url = f'https://oauth.yandex.ru/authorize?response_type=code&client_id={client_id}'
    print(f'\nОткрою в браузере:\n{auth_url}\n')
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print('Авторизуйся, разреши доступ. После редиректа скопируй значение code из URL.')
    code = input('Вставь code: ').strip()

    # Exchange code
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
    }).encode()
    req = urllib.request.Request('https://oauth.yandex.ru/token', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())

    if 'error' in resp:
        print(f'Ошибка: {resp}')
        sys.exit(1)

    token = resp['access_token']
    expires_in = resp.get('expires_in', 0)
    refresh = resp.get('refresh_token', '')

    import datetime
    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=expires_in)).date()

    save_env({
        'YANDEX_METRIKA_TOKEN': token,
        'YANDEX_METRIKA_REFRESH_TOKEN': refresh,
        'YANDEX_METRIKA_TOKEN_EXPIRES': expires_at.isoformat(),
    })

    print(f'\n✓ Токен сохранён в {ENV_PATH}')
    print(f'  Действует до: {expires_at}')
    print(f'  Refresh token также сохранён')

    # Test
    test = input('\nПроверить на счётчике (оставь пустым чтобы пропустить)? counter_id: ').strip()
    if test:
        from query import stat_query
        try:
            r = stat_query(test, 'ym:s:visits', date1='2026-03-01', date2='2026-03-31', token=token)
            print(f'✓ Визиты за март 2026: {r["totals"][0]:,.0f}')
        except Exception as e:
            print(f'Ошибка: {e}')


if __name__ == '__main__':
    main()
