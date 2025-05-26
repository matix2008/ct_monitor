"""monitor/httpendpoint.py - Реализация HTTP-точки мониторинга"""

from typing import Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
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

    def check_status(self) -> Tuple[bool, int, str]:
        """
        Выполняет HTTP-запрос к точке и возвращает статус работоспособности.

        :return: кортеж (is_ok, status_code)
        """
        full_url = self.build_full_url()
        try:
            response = requests.request(self.method, full_url, timeout=5)
            code = response.status_code
            resp_text = self.extract_text_from_response(response)
            return code == self.success_code, code, resp_text
        except requests.RequestException:
            return False, -1, ""

    def extract_text_from_response(self, response: requests.Response) -> str:
        """
        Возвращает чистый текст из ответа в зависимости от типа содержимого.
        """
        content_type = response.headers.get("Content-Type", "").lower()

        try:
            if "application/json" in content_type:
                # Преобразуем JSON-ответ в строку
                json_data = response.json()
                return str(json_data)

            elif "text/html" in content_type:
                # Удаляем HTML-теги
                soup = BeautifulSoup(response.text, "lxml")
                return soup.get_text(separator=",", strip=True)

            elif "text/plain" in content_type:
                return response.text.strip()

            else:
                # Для всех других типов пробуем вывести
                # часть текста (например, XML, markdown и т.д.)
                return response.text.strip()

        except Exception as e:
            return f"[Ошибка при обработке ответа]: {e}"
