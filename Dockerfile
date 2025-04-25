# Используем официальный образ Python
FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app

# Копируем только нужные файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY main.py .
COPY monitor/ monitor/

# Создаем каталог логов
RUN mkdir -p logs

# Точка входа
CMD ["python", "main.py"]
