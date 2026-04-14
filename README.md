# Salto API Skills — сборник скиллов для Claude Code

Готовые скиллы для работы с внешними API, которые нужны агентству / клиенту:

| Скилл | Что делает | Готовность |
|-------|------------|------------|
| [api-livesklad](./api-livesklad/) | LiveSklad CRM — заказы, источники, себестоимость | ✅ |
| [api-yandex-metrika](./api-yandex-metrika/) | Яндекс.Метрика — трафик, цели, Яндекс.Бизнес | ✅ |
| [api-yandex-direct](./api-yandex-direct/) | Яндекс.Директ — расход, CTR, поисковые запросы | ✅ |
| [api-onlinepbx](./api-onlinepbx/) | OnlinePBX — звонки, записи, история | 🔜 |

## Кому полезно

- **Сервисным центрам**: livesklad + onlinepbx + метрика + директ = месячный отчёт автоматом
- **Агентствам**: шаблоны для всех клиентов по одному стандарту
- **Маркетологам**: всё что можно вытащить из кабинетов — одной командой

## Установка

### Все скиллы сразу

```bash
git clone https://github.com/salto-agancy/salto-api-skills ~/salto-api-skills
for s in api-livesklad api-yandex-metrika api-yandex-direct; do
  ln -s ~/salto-api-skills/$s ~/.claude/skills/$s
done
```

### Отдельный скилл

```bash
git clone https://github.com/salto-agancy/api-livesklad-skill ~/.claude/skills/api-livesklad
```

Или через Claude Code:
```
установи скилл из https://github.com/salto-agancy/api-livesklad-skill
```

## Единый подход

Все скиллы следуют одной схеме:

```
api-<name>/
├── SKILL.md            # инструкция для Claude (автозагрузка по триггерам)
├── README.md           # для публичного шаринга (GitHub)
├── scripts/            # рабочие Python скрипты (готовые к запуску)
├── examples/           # примеры JSON/TSV ответов API
└── references/         # глубокая документация (endpoints, поля, rate limits)
```

Креды всегда в `~/.config/<api-name>/.env` (не в коде, не в git).

## Безопасность

- Все `.env` в `.gitignore`
- Токены не логируются
- `chmod 600` на creds-файлах
- Open source = любой может проверить, что шлётся в API

## Совместимость

- **Python 3.9+** (используется только stdlib — `urllib`, `json`, `datetime`)
- Claude Code всех версий, поддерживающих SKILL.md формат
- macOS / Linux (Windows не тестировали)

## Поддержка

- Сальто Сообщество (Telegram): обсуждения, пример использования
- Issues на GitHub: баги, фичи
- Автор: [@salto_dima](https://t.me/salto_dima) (Дмитрий Сальченко, Salto Agency)

## Лицензия

MIT — используй в коммерческих проектах, модифицируй, шарь.

## Roadmap

- [x] api-livesklad
- [x] api-yandex-metrika
- [x] api-yandex-direct
- [ ] api-onlinepbx (в работе)
- [ ] api-deepgram (транскрипция звонков)
- [ ] api-google-sheets (выгрузка отчётов)
- [ ] api-timeweb (хостинг, домены)
