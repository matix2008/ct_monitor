"""monitor/notifier.py - Абстрактный класс уведомителя"""

from abc import ABC, abstractmethod
from monitor.incident import Incident

class Notifier(ABC):
    """
    Абстрактный интерфейс для всех типов уведомителей.
    Реализации должны предоставлять методы для уведомления об инцидентах.
    """

    @abstractmethod
    def start(self):
        """Запускает уведомитель."""

    @abstractmethod
    async def notify_incident(self, incident: Incident):
        """Уведомить об открытии инцидента."""

    @abstractmethod
    async def notify_recovery(self, incident: Incident):
        """Уведомить о завершении инцидента."""

    @abstractmethod
    async def notify_info(self, message: str):
        """Уведомить о системном событии (например, запуск, остановка, сбой)."""
