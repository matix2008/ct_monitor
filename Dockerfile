# Используем официальную минимальную версию Python 3.10 на базе Debian Bullseye
FROM python:3.10-slim-bullseye

# Обновляем пакеты для устранения известных уязвимостей
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Копируем файлы проекта
COPY ./requirements.txt /requirements.txt
COPY ./main.py /main.py
COPY ./monitor /monitor

# Убедимся, что директория для логов существует
RUN mkdir -p /logs

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /requirements.txt

# Точка входа
CMD ["python", "main.py"]

