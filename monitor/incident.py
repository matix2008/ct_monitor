"""monitor/incident.py - Инцидент"""


from datetime import datetime, timezone

class Incident:
    """
    Представляет инцидент для конкретного ресурса.
    """

    def __init__(self, resource_name: str, code: int):
        self.resource_name = resource_name
        self.code = code
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
            "start_time": self.start_time,
            "end_time": self.end_time
        }

    def __str__(self):
        return f"{self.resource_name} код ответа \
            {self.code} {self.start_time} → {self.end_time or '...'}"

    def __repr__(self):
        return f"<Incident {self.resource_name} \
            {self.code} {self.start_time} → {self.end_time or '...'}>"
