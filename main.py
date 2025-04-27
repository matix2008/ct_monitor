"""monitor/main.py - Главный файл для запуска мониторинга"""

import sys
import os
from monitor.config import ConfigLoader
from monitor.logger import setup_logger
from monitor.incident_manager import IncidentManager
from monitor.telegram_notifier import TelegramNotifier
from monitor.httpendpoint import HttpEndpoint
from monitor.monitor_thread import MonitorThread

def main():
    """
    Главная функция для запуска мониторинга.
    Загружает конфигурацию, настраивает логирование и запускает потоки мониторинга.
    """
    threads = []
    notifier = None
    logger = None

    try:
        os.makedirs("logs", exist_ok=True)
        config_loader = ConfigLoader()
        config_loader.load()

        logger = setup_logger("monitor", "logs/monitor.log", config_loader.get_log_level())
        logger.info("Запуск монитора...")

        # Срздаем экземпляр IncidentManager для управления инцидентами
        incidents = IncidentManager()
        # Создаем экземпляр TelegramNotifier для отправки уведомлений в Telegram
        if "--test" not in sys.argv:
            notifier = TelegramNotifier(
                token=config_loader.get_telegram_token(),
                users=config_loader.get_users(),
                incidents=incidents,
                logger=logger
        )
        # Установить уведомитель в менеджер инцидентов
        # Это позволяет менеджеру инцидентов отправлять уведомления через указанный уведомитель
        incidents.set_notifier(notifier)

        # Получить список ресурсов из конфигурации и запустить потоки мониторинга
        endpoints = []
        resources = config_loader.get_resources()
        for resource_config in resources:
            if "--test" in sys.argv:
                resource_config["check_interval"] = 1
                resource_config["retry_interval"] = 1
            # Создать экземпляр HttpEndpoint и MonitorThread для каждого ресурса
            endpoint = HttpEndpoint(resource_config)
            endpoints.append(endpoint)
            thread = MonitorThread(endpoint, resource_config, logger, incidents)
            thread.start()
            threads.append(thread)

        # Установить все точки мониторинга в менеджер инцидентов
        incidents.set_endpoints(endpoints)

        # Запустить уведомитель, если не в тестовом режиме
        # Если в тестовом режиме, пропустить запуск уведомителя
        if notifier:
            notifier.start()

    finally:
        if logger:
            logger.info("Завершение работы монитора...")

        # Остановка всех потоков мониторинга
        for thread in threads:
            thread.stop()
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()

        if logger:
            logger.info("Монитор завершил работу.")

if __name__ == "__main__":
    main()
