"""monitor/incident_manager.py - Управление инцидентами"""

import json
import os
from typing import Dict, List
from monitor.endpoint import Endpoint
from monitor.incident import Incident
from monitor.notifier import Notifier

class IncidentManager:
    """
    Управляет регистрацией, закрытием и хранением инцидентов.
    """

    def __init__(self, log_file: str = "logs/incidents.jsonl"):
        self.log_file = log_file
        self.notifier = None
        self.all_endpoints = None
        self.active_incidents: Dict[str, Incident] = {}
        self._load_active_incidents()

    def register_incident(self, resource_name: str, code: int):
        """Открывает инцидент, если он ещё не активен."""
        if resource_name not in self.active_incidents:
            incident = Incident(resource_name, code)
            self.active_incidents[resource_name] = incident
            self._append_to_log(incident.to_dict())
            if self.notifier:
                self.notifier.send_task(self.notifier.notify_incident(incident))

    def resolve_incident(self, resource_name: str):
        """Закрывает активный инцидент, если он существует."""
        incident = self.active_incidents.get(resource_name)
        if incident:
            incident.close()
            self._append_to_log(incident.to_dict())
            del self.active_incidents[resource_name]
            if self.notifier:
                self.notifier.send_task(self.notifier.notify_recovery(incident))

    def set_notifier(self, notifier: Notifier):
        """Устанавливает уведомитель."""
        self.notifier = notifier

    def set_endpoints(self, all_endpoints: List[Endpoint]):
        """Устанавливает точки мониторинга."""
        self.all_endpoints = all_endpoints

    def get_active(self) -> List[Incident]:
        """Возвращает список всех активных инцидентов."""
        return list(self.active_incidents.values())

    def get_all_ep_names(self) -> List[str]:
        """Возвращает список всех уникальных имён ресурсов."""
        return [ep.get_name() for ep in self.all_endpoints]

    def reload_active_incidents(self):
        """Переоткрывает активные инциденты из журнала."""
        self._load_active_incidents()

    def _append_to_log(self, record: dict):
        """Добавляет запись об инциденте в журнал (формат JSONL)."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")

    def _load_active_incidents(self):
        """Загружает только активные (не завершённые) инциденты из журнала."""
        self.active_incidents.clear()
        if not os.path.exists(self.log_file):
            return
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("end_time") is None:
                        incident = Incident(data["resource_name"],data["code"])
                        incident.start_time = data["start_time"]
                        self.active_incidents[data["resource_name"]] = incident
                except (json.JSONDecodeError, KeyError):
                    continue
