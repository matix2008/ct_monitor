"""
Тестирование запуска main.py без ошибок в минимальной конфигурации.
"""

import subprocess
import sys
from pathlib import Path


def test_main_runs_without_errors():
    """
    Проверяет, что main.py запускается без ошибок на минимальной конфигурации.
    """
    project_root = Path(__file__).resolve().parent.parent
    main_path = project_root / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_path), "--test"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=project_root,
        timeout=30,
        check=True
    )

    assert result.returncode == 0, f"main.py завершился с кодом {result.returncode}\
        \nSTDERR:\n{result.stderr.decode()}\nSTDOUT:\n{result.stdout.decode()}"
