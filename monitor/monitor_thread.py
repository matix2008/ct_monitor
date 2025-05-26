"""monitor/monitor_thread.py - Поток мониторинга точки"""

import threading
import time
import logging
from typing import Optional
from monitor.incident_manager import IncidentManager

class MonitorThread(threading.Thread):
    """
    Поток мониторинга одной точки.
    Выполняет периодический опрос и проверку устойчивости отказов или восстановления.
    """

    def __init__(self, endpoint, resource_config: dict, \
                 logger: Optional[logging.Logger] = None, \
                 incidents: Optional[IncidentManager] = None):
        super().__init__(daemon=True)
        self.endpoint = endpoint
        self.name = endpoint.get_name()
        self.logger = logger or logging.getLogger(__name__)
        self.incidents = incidents
        self._stop_event = threading.Event()

        # Настройки опроса
        self.check_interval = resource_config['check_interval']
        self.retry_interval = resource_config['retry_interval']
        self.max_attempts = resource_config['max_attempts']

        # Состояние
        self.in_incident = False

    def stop(self):
        """Останавливает поток мониторинга."""
        self._stop_event.set()

    def run(self):
        """Основной цикл опроса ресурса."""
        self.logger.info("Поток %s запущен", self.name)
        try:
            while not self._stop_event.is_set():
                # Проверяем состояние точки
                status, code, resp = self.endpoint.check_status()

                if not self.in_incident and not status:
                    self.logger.warning("%s — ошибка %s, %s. Начинаем повторные попытки...", \
                                        self.name, code, resp)
                    if self._check_stability(expected=False):
                        self.logger.warning("%s — подтвержденный сбой. Открываем инцидент.", \
                                        self.name)
                        self.in_incident = True
                        if self.incidents:
                            self.incidents.register_incident(self.name, code, resp)

                elif self.in_incident and status:
                    self.logger.info("%s — получен ответ %s, %s. Проверка восстановления...", \
                                    self.name, code, resp)
                    if self._check_stability(expected=True):
                        self.logger.warning("%s — инцидент закрыт. Устойчивое восстановление.", \
                                        self.name)
                        self.in_incident = False
                        if self.incidents:
                            self.incidents.resolve_incident(self.name)

                else:
                    self.logger.debug("%s — стабильное состояние: код %s", self.name, code)

                self._sleep(self.retry_interval)
        except Exception as e:
            self.logger.error("%s — ошибка в потоке: %s", self.name, e)
        finally:
            self.logger.info("Поток %s завершён", self.name)

    def _check_stability(self, expected: bool) -> bool:
        """
        Проверяет устойчивость состояния (ошибки или восстановления).
        :param expected: ожидаемое состояние (True для восстановления, False для ошибки)
        :return: True, если устойчивость подтверждена
        """
        success_count = 0
        for attempt in range(self.max_attempts):
            if self._stop_event.is_set():
                self.logger.debug("%s — остановка потока", self.name)
                return False

            # Проверяем состояние точки
            status, code, _ = self.endpoint.check_status()
            self.logger.debug("%s — попытка %d: код %s, ожидаем %s", \
                              self.name, attempt + 1, code, expected)

            if status == expected:
                success_count += 1
            else:
                success_count = 0

            if success_count >= self.max_attempts:
                self.logger.debug("%s — устойчивое состояние достигнуто (%s)", self.name, expected)
                return True

            self._sleep(self.retry_interval)

        self.logger.debug("%s — устойчивое состояние НЕ достигнуто (%s)", self.name, expected)
        return False

    def _sleep(self, seconds: int, max_seconds: int = 5):
        """
        Усыпляет поток на заданное количество секунд с проверкой флага остановки.

        Если seconds <= max_seconds — спит один раз на указанное число секунд.
        Если seconds > max_seconds — делит паузу на шаги с длиной не более max_seconds, 
        проверяя флаг self._stop_event перед каждым шагом.

        :param seconds: общее время сна
        :param max_seconds: максимальный шаг сна (по умолчанию 5 секунд)
        """
        remaining_time = seconds
        while remaining_time > 0 and not self._stop_event.is_set():
            sleep_time = min(remaining_time, max_seconds)
            time.sleep(sleep_time)
            remaining_time -= sleep_time
