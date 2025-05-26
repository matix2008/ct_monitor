"""monitor/endpoint.py - Абстрактная точка мониторинга"""

from abc import ABC, abstractmethod
from typing import Tuple

class Endpoint(ABC):
    """
    Абстрактный базовый класс для точки мониторинга.
    Все реализации должны предоставлять методы для проверки состояния и получения имени.
    """

    @abstractmethod
    def check_status(self) -> Tuple[bool, int, str]:
        """
        Проверяет доступность ресурса.
        :return: кортеж (успех: bool, http-код: int, response: str)
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Возвращает уникальное имя точки мониторинга.
        """
