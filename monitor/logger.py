"""monitor/logger.py - Настройка логгера с ротацией логов"""

import logging
import logging.handlers

def setup_logger(name: str, log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Настраивает и возвращает логгер с заданным именем, уровнем логирования и файловой ротацией.

    :param name: имя логгера
    :param log_file: путь к файлу лога
    :param level: уровень логирования (например, 'INFO', 'DEBUG')
    :return: настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s')

    # Ротация логов ежедневно, хранение до 7 дней
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        backupCount=7,
        encoding='utf-8'
    )
    handler.setFormatter(formatter)

    # Добавляем обработчик только если он еще не добавлен
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
