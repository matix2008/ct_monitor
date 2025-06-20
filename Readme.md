# CT Monitor

**CT Monitor** — это система мониторинга HTTP-ресурсов с уведомлениями через Telegram. Программа отслеживает доступность заданных ресурсов, регистрирует инциденты и оповещает пользователей в реальном времени.

---

## Содержимое

- [Возможности](#возможности)
- [Структура проекта](#структура)
- [Установка](#установка)
- [Запуск](#запуск)
- [Конфигурация](#конфигурация)
- [Тесты](#тесты)
- [Docker](#docker)

---

## Возможности

- Мониторинг HTTP/контрольных точек
- Обработка нестабильных и устойчивых ошибок
- Telegram-уведомления:
  - об инциденте (-тах)
  - о восстановлении
  - о системных событиях (запуск, сбой, завершение)
- Telegram-бот: команды `/start`, `/status`, `/incidents`, `/refresh`, `/whoami`, `/help`
- Ролевая модель: Admin, Auditor, Spectator

---

## Структура

```markdown
ct_monitor/
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── main.py (точка входа)
├── monitor/
│   ├── config.py (работа с конфигурацией)
│   ├── logger.py (настройка и абстракция логирования)
│   ├── endpoint.py (абстрактная точка контроля)
│   ├── httpendpoint.py (конкретная реализация HTTP-точки)
│   ├── monitor_thread.py (поток мониторинга для одной точки)
│   ├── incident.py (инцидент)
│   ├── incident_manager.py (учет и регистрация инцидентов)
│   ├── notifier.py (абстрактный способ уведомления)
│   ├── telegram_notifier.py (уведомления через телеграм)
├── logs/
│   ├── monitor.log
│   └── incidents.jsonl
├── tests/
│   ├── test_config.py (тест загрузки и валидации)
│   ├── test_monitor_thread.py (тест логики опроса)
│   ├── test_incident_manager.py (тест регистрации/закрытия инцидента)
│   ├── test_telegram.py (тест команды /status (с моком))
└── README.md
```

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/matix2008/ct_monitor
   cd ct_monitor
   ```

2. Установите зависимости:

   ```bash
   sudo apt update
   sudo apt install python3-venv

   python3 -m venv .venv
   sudo source .venv/bin/activate

   pip install -r requirements.txt
   ```

---

## Запуск

```bash
python main.py
```

Для тестового запуска (Telegram-бот не запускается):

```bash
python main.py --test
```

---

## Конфигурация

### config.json

```json
{
  "users": [
    {"telegram_id": 123456789, "name": "Admin", "role": "Admin"}
  ],
  "resources": [
    {
      "id": "site1",
      "name": "Боевой сайт",
      "url": "http://example.com",
      "method": "GET",
      "port": 80,
      "error_code": 500,
      "success_code": 200,
      "interval_main": 300,
      "interval_retry": 7,
      "max_attempts": 5
    }
  ]
}
```

### .secrets.json

```json
{
  "telegram_token": "123456:ABC-DEF"
}
```

---

## Тесты

```bash
pytest tests/
```

---

## Docker и docker-compose

### Убедиться в правильной структуре проекта

ct_monitor/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
├── config.json
├── .secrets.json
├── monitor/
│   ├── __init__.py
│   └── ...
├── logs/              # Папка для логов (может быть создана автоматически)

*Файлы config.json, .secrets.json должны лежать в корне.*

### Собрать изображение

```bash
docker-compose build
```

или вручную (менее предпочтительно)

```bash
docker build -t ct-monitor .
```

### Запустить

```bash
docker-compose up -d
```

или сразу со сборкой

```bash
docker-compose up -d --build
```

Запуск и остановка

```bash
docker-compose up -d --build

docker-compose down
```

---

## Логи

- `logs/monitor.log` — журнал работы системы
- `logs/incidents.jsonl` — инциденты в формате JSONL

---

## Авторы

- Batasov Herman, Telegram: @herman_ba

---

Спасибо за использование CT Monitor! Свяжитесь, если нужно добавить новые типы мониторов, уведомлений или поддержку других мессенджеров.
