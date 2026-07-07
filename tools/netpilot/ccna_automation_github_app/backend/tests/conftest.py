import os
from pathlib import Path

import pytest

TEST_DB = Path(__file__).resolve().parent / "_test_ccna.db"


@pytest.fixture(autouse=True)
def test_database(monkeypatch: pytest.MonkeyPatch) -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()
    monkeypatch.setenv("DATABASE_PATH", str(TEST_DB))
    from app.db import init_database

    init_database()
