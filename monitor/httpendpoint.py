"""monitor/httpendpoint.py - Реализация HTTP-точки мониторинга"""

from typing import Tuple
from urllib.parse import urlparse
import requests
from monitor.endpoint import Endpoint

class HttpEndpoint(Endpoint):
    """
    Конкретная реализация точки мониторинга по HTTP.
    Выполняет HTTP-запросы и определяет доступность по статус-коду.
    """

    def __init__(self, config: dict):
        self.name = config["name"]
        self.url = config["url"]
        self.port = config.get("port", 80)
        self.method = config.get("method", "GET").upper()
        self.success_code = config.get("success_code", 200)
        self.error_code = config.get("error_code", 500)

    def get_name(self) -> str:
        """
        Возвращает имя точки мониторинга.
        """
        return self.name

    def build_full_url(self) -> str:
        """
        Формирует полный URL с учетом порта, если он явно задан.
        Если порт равен 0, считается что он уже включен в self.url.
        """
        if self.port == 0:
            return self.url

        parsed = urlparse(self.url)
        netloc = f"{parsed.hostname}:{self.port}"
        return parsed._replace(netloc=netloc).geturl()

    def check_status(self) -> Tuple[bool, int]:
        """
        Выполняет HTTP-запрос к точке и возвращает статус работоспособности.

        :return: кортеж (is_ok, status_code)
        """
        full_url = self.build_full_url()
        try:
            response = requests.request(self.method, full_url, timeout=5)
            code = response.status_code
            return code == self.success_code, code
        except requests.RequestException:
            return False, -1
