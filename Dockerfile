# Используем официальную минимальную версию Python 3.10 на базе Debian Bullseye
FROM python:3.10-slim-bullseye

# Обновляем пакеты для устранения известных уязвимостей
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Создаем рабочую папку
# WORKDIR /app

# Копируем файлы проекта
COPY ./requirements.txt /app/requirements.txt
COPY ./main.py /main.py
COPY ./monitor /app/monitor

# Убедимся, что директория для логов существует
RUN mkdir -p /app/logs

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Порт, если захочешь сделать healthcheck через Docker-сетку
EXPOSE 8080

# Точка входа
CMD ["python", "main.py"]
