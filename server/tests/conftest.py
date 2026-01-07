"""Pytest configuration and fixtures for server tests."""

import os

import pytest

# Set test database before any imports that use database
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_befora.db")
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    """Initialize the test database before any tests run."""
    from server.db.database import initialize_db

    initialize_db()
    yield
    # Cleanup: remove test database file
    import os
    from pathlib import Path

    test_db_path = Path("./test_befora.db").resolve()
    if test_db_path.exists():
        os.remove(test_db_path)
