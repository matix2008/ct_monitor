"""monitor/config.py - Работа с конфигурацией"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from jsonschema import validate, ValidationError

# Значения по умолчанию для путей к конфигурационным файлам
DEFAULT_CONFIG_PATH = Path("monitor/config.json")
DEFAULT_SECRETS_PATH = Path("monitor/.secrets.json")
DEFAULT_SCHEMA_PATH = Path("monitor/config_schema.json")

class ConfigError(Exception):
    """Исключение, выбрасываемое при ошибке загрузки или валидации конфигурации."""

class ConfigLoader:
    """
    Класс для загрузки и валидации конфигурационных файлов проекта:
    - config.json: основная конфигурация
    - .secrets.json: чувствительные данные (например, токены)
    """
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.secrets: Dict[str, Any] = {}

    def load(
        self,
        config_path: Path = DEFAULT_CONFIG_PATH,
        secrets_path: Path = DEFAULT_SECRETS_PATH,
        schema_path: Optional[Path] = DEFAULT_SCHEMA_PATH
    ):
        """
        Загружает и валидирует конфигурационные файлы.

        :param config_path: путь к config.json
        :param secrets_path: путь к .secrets.json
        :param schema_path: путь к схеме config_schema.json (опционально)
        """
        self.config = self._load_json(config_path, schema_path=schema_path)
        self.secrets = self._load_json(secrets_path)

    def _load_json(self, path: Path, schema_path: Path = None) -> Dict[str, Any]:
        """
        Загружает JSON-файл и валидирует его при наличии схемы.

        :param path: путь к JSON-файлу
        :param schema_path: путь к JSON-схеме (необязательный)
        :return: словарь с данными
        :raises ConfigError: если файл не найден, некорректен или не прошел валидацию
        """
        if not path.exists():
            raise ConfigError(f"Файл не найден: {path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка парсинга JSON в {path}: {e}") from e

        if schema_path:
            try:
                with schema_path.open("r", encoding="utf-8") as s:
                    schema = json.load(s)
                validate(instance=data, schema=schema)
            except (json.JSONDecodeError, ValidationError) as e:
                raise ConfigError(f"Ошибка валидации {path} по схеме {schema_path}: {e}") from e

        return data

    def get(self, key: str, default: Any = None) -> Any:
        """Возвращает значение по ключу из основной конфигурации."""
        return self.config.get(key, default)

    def get_telegram_token(self) -> str:
        """Возвращает Telegram токен из secrets-файла."""
        return self.secrets.get("telegram_token", "")

    def get_resources(self) -> list:
        """Возвращает список точек мониторинга."""
        return self.config.get("resources", [])

    def get_users(self) -> list:
        """Возвращает список пользователей Telegram с ролями."""
        return self.config.get("telegram_users", [])

    def get_log_level(self) -> str:
        """Возвращает уровень логирования (по умолчанию INFO)."""
        return self.config.get("log_level", "INFO")
