import pytest

from project.app import create_app
from project.extensions import db


@pytest.fixture
def app(tmp_path):
    """Each test gets its own app and SQLite file, never the deployment DB."""
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "USERNAME": "admin",
            "PASSWORD": "admin",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "SESSION_COOKIE_SECURE": False,
        }
    )
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in(client):
    client.post("/login", data={"username": "admin", "password": "admin"})
    return client
