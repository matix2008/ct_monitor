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
   git clone https://github.com/your-org/ct_monitor.git
   cd ct_monitor
   ```

2. Установите зависимости:

   ```bash
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

## Docker

### Собрать изображение

```bash
docker build -t ct-monitor .
```

### Запустить с монтированными конфигами

```bash
docker run --rm \
  -v $PWD/config.json:/app/config.json \
  -v $PWD/.secrets.json:/app/.secrets.json \
  -v $PWD/logs:/app/logs \
  ct-monitor
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
