"""monitor/incident.py - Инцидент"""


from datetime import datetime, timezone

class Incident:
    """
    Представляет инцидент для конкретного ресурса.
    """

    def __init__(self, resource_name: str, code: int, response: str = None):
        """ Инициализирует инцидент с именем ресурса, кодом ответа и временем начала.
        :param resource_name: Имя ресурса, связанного с инцидентом.
        :param code: Код ответа, связанный с инцидентом.
        :param response: Ответ, связанный с инцидентом.
        """
        self.resource_name = resource_name
        self.code = code
        self.response = response
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.end_time = None

    def close(self):
        """Закрывает инцидент, устанавливая время окончания."""
        self.end_time = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        """Преобразует инцидент в словарь для сериализации."""
        return {
            "resource_name": self.resource_name,
            "code": self.code,
            "response": self.response,
            "start_time": self.start_time,
            "end_time": self.end_time
        }

    def __str__(self):
        return f"{self.resource_name} код ответа \
            {self.code}, {self.response} {self.start_time} → {self.end_time or '...'}"

    def __repr__(self):
        return f"<Incident {self.resource_name} \
            {self.code} {self.response} {self.start_time} → {self.end_time or '...'}>"
