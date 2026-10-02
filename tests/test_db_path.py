import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("configured", [None, "", "budget.db", "nested/budget.db", "absolute"])
def test_database_path_configuration(configured, tmp_path):
    expected = "data/budget.db" if not configured else configured
    if configured == "absolute":
        configured = str(tmp_path / "absolute" / "budget.db")
        expected = configured
    environment = os.environ.copy()
    environment.pop("BUDGET_DB_PATH", None)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    if configured is not None:
        environment["BUDGET_DB_PATH"] = configured
    result = subprocess.run(
        [sys.executable, "-c", "import json,main; main.init_db(); "
         "main.update_tokens_used(3); "
         "print(json.dumps([main.DB_PATH, main.get_budget()]))"],
        cwd=tmp_path, env=environment, capture_output=True, text=True, check=True,
    )
    path, budget = json.loads(result.stdout)
    assert path == expected
    assert budget == [3, 100]
    assert (tmp_path / path).is_file()
