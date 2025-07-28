# Запуск CT Monitor в Docker

## Предварительные требования

1. Установленный Docker и Docker Compose
2. Telegram Bot Token (получить у @BotFather)

## Настройка

### 1. Настройка Telegram Bot

1. Создайте бота через @BotFather в Telegram
2. Получите токен бота
3. Отредактируйте файл `.secrets.json`:
   ```json
   {
     "telegram_token": "YOUR_ACTUAL_BOT_TOKEN_HERE"
   }
   ```

### 2. Настройка пользователей

Отредактируйте файл `config.json`:
- Замените `telegram_id` на реальные ID пользователей
- Настройте роли: "Admin", "Auditor", "Spectator"
- Добавьте нужные ресурсы для мониторинга

### 3. Проверка конфигурации

Убедитесь, что файлы находятся в корне проекта:
```
ct_monitor/
├── config.json          # Основная конфигурация
├── .secrets.json        # Telegram токен
├── docker-compose.yml   # Docker конфигурация
└── ...
```

## Запуск

### Сборка и запуск
```bash
# Собрать образ и запустить контейнер
docker-compose up -d --build

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

### Только запуск (если образ уже собран)
```bash
docker-compose up -d
```

### Проверка статуса
```bash
# Статус контейнера
docker-compose ps

# Логи в реальном времени
docker-compose logs -f ct_monitor
```

## Использование Telegram Bot

После запуска бот будет доступен в Telegram. Команды:

- `/start` - приветствие
- `/help` - справка по командам
- `/status` - статус всех ресурсов (Admin/Auditor)
- `/incidents` - текущие инциденты (Admin/Auditor)
- `/whoami` - ваша роль и ID
- `/refresh` - перечитать конфигурацию (Admin)

## Логи

Логи сохраняются в папку `logs/`:
- `logs/monitor.log` - логи приложения
- `logs/incidents.jsonl` - история инцидентов

## Устранение проблем

### Проверка конфигурации
```bash
# Войти в контейнер
docker-compose exec ct_monitor bash

# Проверить файлы
ls -la /monitor/
cat /monitor/config.json
```

### Перезапуск с пересборкой
```bash
docker-compose down
docker-compose up -d --build
```

### Очистка
```bash
# Удалить контейнер и образ
docker-compose down --rmi all

# Удалить логи
rm -rf logs/
``` 