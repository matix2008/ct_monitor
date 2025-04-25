"""tests/test_incident_manager.py"""

import json
from monitor.incident_manager import IncidentManager, Incident


def test_register_and_resolve_incident(tmp_path):
    """Проверяет регистрацию и закрытие инцидента с логированием."""
    log_file = tmp_path / "incidents.jsonl"
    manager = IncidentManager(log_file=str(log_file))

    manager.register_incident("test_resource")
    active = manager.get_active()
    assert len(active) == 1
    assert active[0].resource_name == "test_resource"
    assert active[0].end_time is None

    manager.resolve_incident("test_resource")
    assert len(manager.get_active()) == 0

    with open(log_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    assert len(lines) == 2
    assert lines[0]["resource_name"] == "test_resource"
    assert lines[0]["end_time"] is None
    assert lines[1]["end_time"] is not None


def test_reload_active_incidents(tmp_path):
    """Проверяет восстановление активных инцидентов из журнала."""
    log_file = tmp_path / "incidents.jsonl"
    manager = IncidentManager(log_file=str(log_file))

    manager.register_incident("res1")

    incident = Incident("res2")
    incident.close()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(incident.to_dict()) + "\n")

    with open(log_file, "r", encoding="utf-8") as f:
        assert sum(1 for _ in f) == 2

    new_manager = IncidentManager(log_file=str(log_file))
    active = new_manager.get_active()
    assert len(active) == 1
    assert active[0].resource_name == "res1"


def test_double_registration(tmp_path):
    """Проверяет защиту от повторной регистрации одного и того же инцидента."""
    log_file = tmp_path / "incidents.jsonl"
    manager = IncidentManager(log_file=str(log_file))
    manager.register_incident("r1")
    manager.register_incident("r1")
    assert len(manager.get_active()) == 1
