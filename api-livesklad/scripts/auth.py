"""
LiveSklad auth helper. Reads credentials from ~/.config/livesklad/.env
Returns (token, remaining_requests). Handles 429 with exponential backoff.
"""
import urllib.request
import urllib.parse
import json
import os
import time
import sys


BASE = 'https://api.livesklad.com'


def load_env():
    path = os.path.expanduser('~/.config/livesklad/.env')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Создай {path} с LIVESKLAD_API_LOGIN, LIVESKLAD_API_PASSWORD, LIVESKLAD_SHOP_ID'
        )
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"\'')
    return env


def auth(max_retries=8, verbose=True):
    env = load_env()
    login = env['LIVESKLAD_API_LOGIN']
    password = env['LIVESKLAD_API_PASSWORD']

    for attempt in range(max_retries):
        try:
            data = urllib.parse.urlencode({'login': login, 'password': password}).encode()
            req = urllib.request.Request(f'{BASE}/auth', data=data, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())

            if 'error' in resp:
                err = resp['error']
                if err.get('statusCode') == 429:
                    wait = 65 * (attempt + 1)
                    if verbose:
                        print(f'  429 (rate limit), attempt {attempt + 1}, waiting {wait}s...', flush=True)
                    time.sleep(wait)
                    continue
                raise Exception(f'Auth error: {err}')

            token = resp['token']
            remaining = resp.get('remainRequest', 100)
            ttl = resp.get('ttl', 900)
            if verbose:
                print(f'  Token ok, {remaining}/100 requests left, ttl={ttl}s', flush=True)
            return token, remaining

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 65 * (attempt + 1)
                if verbose:
                    print(f'  429 HTTP, attempt {attempt + 1}, waiting {wait}s...', flush=True)
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            if '429' in str(e):
                wait = 65 * (attempt + 1)
                if verbose:
                    print(f'  429 (exception), attempt {attempt + 1}, waiting {wait}s...', flush=True)
                time.sleep(wait)
            else:
                raise

    raise Exception(f'Could not auth after {max_retries} attempts')


def get(url, token, timeout=30):
    """GET with Authorization header (NO Bearer prefix for LiveSklad)."""
    req = urllib.request.Request(url)
    req.add_header('Authorization', token)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


if __name__ == '__main__':
    token, remaining = auth()
    print(f'Auth OK. Token (first 10 chars): {token[:10]}... Remaining: {remaining}')
