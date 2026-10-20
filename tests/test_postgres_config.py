"""Catch the driver mismatch discovered by the first Postgres cloud build."""

import pytest

from project.app import create_app
from project.extensions import db


@pytest.mark.parametrize("scheme", ["postgres", "postgresql"])
def test_postgres_selects_installed_psycopg2_driver(monkeypatch, scheme):
    monkeypatch.setenv("DATABASE_URL", f"{scheme}://test:fake@localhost/test")
    app = create_app({"TESTING": True})
    with app.app_context():
        # Engine creation must select the installed adapter without connecting.
        assert db.engine.driver == "psycopg2"
        assert db.engine.pool.__class__.__name__ == "NullPool"
        db.engine.dispose()
