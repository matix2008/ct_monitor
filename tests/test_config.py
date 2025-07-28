"""tests/test_config.py"""
# tests/test_config.py

import json
import pytest
from monitor.config import ConfigLoader, ConfigError


def test_valid_config_load(tmp_path):
    """Проверяет успешную загрузку валидной конфигурации с валидацией по схеме."""
    secret_data = {
        "telegram_token": "123456:ABC"
    }
    config_data = {
        "telegram_users": [{"telegram_id": 1, "name": "Test User", "role": "Admin"}],
        "resources": [
            {
                "id": "r1",
                "name": "Test Resource",
                "url": "http://localhost",
                "method": "GET",
                "port": 80,
                "error_code": 500,
                "success_code": 200,
                "interval_main": 300,
                "interval_retry": 7,
                "max_attempts": 5
            }
        ]
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config_data), encoding="utf-8")

    secret_path = tmp_path / ".secrets.json"
    secret_path.write_text(json.dumps(secret_data), encoding="utf-8")

    # Минимальная JSON-схема для успешной валидации
    schema_data = {
        "type": "object",
        "properties": {
            "users": {"type": "array"},
            "resources": {"type": "array"}
        },
        "required": ["telegram_users", "resources"]
    }
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema_data), encoding="utf-8")

    loader = ConfigLoader()
    loader.load(config_path, secret_path, schema_path)

    assert loader.get_telegram_token() == "123456:ABC"
    assert len(loader.get_users()) == 1
    assert len(loader.get_resources()) == 1


def test_missing_fields(tmp_path):
    """Проверяет ошибку при отсутствии обязательных полей с валидацией."""
    secret_data = {
        "telegram_token": "123456:ABC"
    }
    bad_config = {
        "resources": [
            {
                "id": "r1",
                "name": "Test Resource",
                "url": "http://localhost",
                "method": "GET",
                "port": 80,
                "error_code": 500,
                "success_code": 200,
                "interval_main": 300,
                "interval_retry": 7,
                "max_attempts": 5
            }
        ]
    }

    config_path = tmp_path / "bad_config.json"
    config_path.write_text(json.dumps(bad_config), encoding="utf-8")

    secret_path = tmp_path / ".secrets.json"
    secret_path.write_text(json.dumps(secret_data), encoding="utf-8")

    schema_data = {
        "type": "object",
        "properties": {
            "telegram_users": {"type": "array"},
            "resources": {"type": "array"}
        },
        "required": ["telegram_users", "resources"]
    }
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema_data), encoding="utf-8")

    loader = ConfigLoader()
    with pytest.raises(ConfigError):
        loader.load(config_path, secret_path, schema_path)


def test_invalid_json(tmp_path):
    """Проверяет ошибку при невалидном JSON."""
    secret_data = {
        "telegram_token": "123456:ABC"
    }
    broken = '{ telegram_token: "abc" '
    config_path = tmp_path / "invalid.json"
    config_path.write_text(broken, encoding="utf-8")

    secret_path = tmp_path / ".secrets.json"
    secret_path.write_text(json.dumps(secret_data), encoding="utf-8")

    loader = ConfigLoader()
    with pytest.raises(ConfigError):
        loader.load(config_path, secret_path, None)
