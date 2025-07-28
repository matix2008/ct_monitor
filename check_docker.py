#!/usr/bin/env python3
"""
Скрипт для проверки готовности к запуску в Docker
"""

import json
import os
from pathlib import Path
from jsonschema import validate

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        "config.json",
        ".secrets.json",
        "docker-compose.yml",
        "Dockerfile",
        "requirements.txt",
        "main.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Все необходимые файлы присутствуют")
        return True

def validate_config():
    """Проверяет валидность config.json"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        with open("monitor/config_schema.json", "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        validate(instance=config, schema=schema)
        print("✅ config.json валиден")
        return True
    except Exception as e:
        print(f"❌ Ошибка валидации config.json: {e}")
        return False

def check_secrets():
    """Проверяет наличие токена в .secrets.json"""
    try:
        with open(".secrets.json", "r", encoding="utf-8") as f:
            secrets = json.load(f)
        
        token = secrets.get("telegram_token", "")
        if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("⚠️  В .secrets.json не установлен реальный токен")
            return False
        else:
            print("✅ Telegram токен настроен")
            return True
    except Exception as e:
        print(f"❌ Ошибка чтения .secrets.json: {e}")
        return False

def check_docker_compose():
    """Проверяет docker-compose.yml"""
    try:
        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            content = f.read()
        
        if ".secrets.json" in content and "config.json" in content:
            print("✅ docker-compose.yml настроен правильно")
            return True
        else:
            print("❌ docker-compose.yml содержит ошибки в путях")
            return False
    except Exception as e:
        print(f"❌ Ошибка чтения docker-compose.yml: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🔍 Проверка готовности к запуску в Docker...\n")
    
    checks = [
        ("Файлы", check_files),
        ("Конфигурация", validate_config),
        ("Секреты", check_secrets),
        ("Docker Compose", check_docker_compose)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"Проверка {name}:")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 Все проверки пройдены! Можно запускать Docker.")
        print("\nКоманды для запуска:")
        print("  docker-compose up -d --build")
        print("  docker-compose logs -f")
    else:
        print("❌ Некоторые проверки не пройдены. Исправьте ошибки перед запуском.")
    
    return all_passed

if __name__ == "__main__":
    main() 