"""tests/test_monitor_thread.py - Тесты для потока мониторинга"""

import time
from unittest.mock import MagicMock
from monitor.monitor_thread import MonitorThread

class DummyEndpoint:
    """
    Заглушка для Endpoint, возвращающая последовательность кодов ответов.
    Используется для имитации состояния ресурса (ошибка или успех).
    """

    def __init__(self, name, statuses):
        self._name = name
        self._statuses = statuses  # список кодов: [500, 500, 500, 200, ...]
        self._index = 0

    def check_status(self):
        """Возвращает следующий статус из списка (True/False, код)."""
        if self._index < len(self._statuses):
            code = self._statuses[self._index]
            self._index += 1
        else:
            code = 200
        print(f"[Dummy] Возвращаю: {code}")
        return code == 200, code

    def get_name(self):
        """Возвращает имя точки мониторинга."""
        return self._name


def test_monitor_thread_triggers_incident():
    """
    Проверяет, что MonitorThread вызывает регистрацию инцидента
    при устойчивой ошибке ресурса (более 3-х подряд 500).
    """
    endpoint = DummyEndpoint("dummy", [500, 500, 500, 500, 500])
    incident_manager = MagicMock()

    config = {
        "check_interval": 0.1,
        "retry_interval": 0.05,
        "max_attempts": 3
    }

    thread = MonitorThread(endpoint, config, logger=None, incidents=incident_manager)
    thread.daemon = True
    thread.start()

    time.sleep(0.5)  # достаточно времени, чтобы отработали проверки
    thread.stop()
    thread.join()

    incident_manager.register_incident.assert_called_with("dummy")


def test_monitor_thread_resolves_incident():
    """
    Проверяет, что MonitorThread регистрирует и завершает инцидент,
    если ресурс сначала возвращает ошибки, а затем стабильные успехи.
    """
    # Добавляем одну успешную проверку, затем 4 ошибки, затем 3 успеха
    endpoint = DummyEndpoint("dummy", [200, 500, 500, 500, 500, 200, 200, 200])
    incident_manager = MagicMock()
    incident_manager.register_incident = \
        MagicMock(side_effect=lambda name: print(f"[MOCK] Зарегистрирован инцидент: {name}"))
    incident_manager.resolve_incident = \
        MagicMock(side_effect=lambda name: print(f"[MOCK] Завершён инцидент: {name}"))

    config = {
        "check_interval": 0.3,
        "retry_interval": 0.1,
        "max_attempts": 3
    }

    thread = MonitorThread(endpoint, config, logger=None, incidents=incident_manager)
    thread.daemon = True
    thread.start()

    time.sleep(2.0)  # увеличено для гарантии срабатывания
    thread.stop()
    thread.join()

    incident_manager.register_incident.assert_called_with("dummy")
    incident_manager.resolve_incident.assert_called_with("dummy")
