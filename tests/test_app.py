from pathlib import Path

import pytest
from sqlalchemy import inspect

from project.extensions import db
from project.models import Post


def test_index(client):
    assert client.get("/").status_code == 200


def test_database(app):
    with app.app_context():
        assert Path(db.engine.url.database).is_file()
        assert "post" in inspect(db.engine).get_table_names()


def test_empty_db(client):
    assert b"No entries yet. Add some!" in client.get("/").data


def test_login_page(client):
    assert client.get("/login").status_code == 200


def test_login_logout(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    assert b"You were logged in" in response.data
    with client.session_transaction() as session:
        assert session["logged_in"] is True
    assert b"You were logged out" in client.get("/logout", follow_redirects=True).data
    with client.session_transaction() as session:
        assert "logged_in" not in session


@pytest.mark.parametrize(
    "username,password,error",
    [
        ("wrong", "admin", b"Invalid username"),
        ("admin", "wrong", b"Invalid password"),
        ("", "", b"Invalid username"),
    ],
)
def test_invalid_login(client, username, password, error):
    response = client.post("/login", data={"username": username, "password": password})
    assert error in response.data
    with client.session_transaction() as session:
        assert not session.get("logged_in")


def test_messages(logged_in, app):
    response = logged_in.post(
        "/add",
        data={"title": "<Hello>", "text": "<strong>HTML</strong> allowed here"},
        follow_redirects=True,
    )
    assert b"New entry was successfully posted" in response.data
    assert b"&lt;Hello&gt;" in response.data
    assert b"<strong>HTML</strong> allowed here" in response.data
    with app.app_context():
        assert db.session.scalar(db.select(Post)).title == "<Hello>"


def test_post_requires_login(client, app):
    assert (
        client.post("/add", data={"title": "Blocked", "text": "No"}).status_code == 401
    )
    with app.app_context():
        assert db.session.scalars(db.select(Post)).all() == []


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"title": "", "text": "Body"},
        {"title": "Title", "text": "   "},
        {"title": "x" * 201, "text": "Body"},
    ],
)
def test_reject_invalid_post(logged_in, app, data):
    assert logged_in.post("/add", data=data).status_code == 400
    with app.app_context():
        assert db.session.scalars(db.select(Post)).all() == []


def test_newest_post_first(logged_in):
    for title in ["Older", "Newer"]:
        logged_in.post("/add", data={"title": title, "text": "Body"})
    html = logged_in.get("/").data
    assert html.index(b"Newer") < html.index(b"Older")


def test_delete_message(logged_in, app):
    logged_in.post("/add", data={"title": "Delete me", "text": "Body"})
    with app.app_context():
        post_id = db.session.scalar(db.select(Post.id))
    response = logged_in.get(f"/delete/{post_id}")
    assert response.status_code == 200
    assert response.json == {"status": 1, "message": "Post Deleted"}
    with app.app_context():
        assert db.session.get(Post, post_id) is None


def test_delete_nonexistent_message(logged_in):
    response = logged_in.get("/delete/999999")
    assert response.status_code == 404
    assert response.json["status"] == 0


def test_html_sanitized(logged_in):
    logged_in.post(
        "/add",
        data={
            "title": "Safe title",
            "text": (
                "<strong>OK</strong><script>alert(1)</script>"
                "<img src=x onerror=alert(2)>"
            ),
        },
    )
    html = logged_in.get("/").data
    assert b"<strong>OK</strong>" in html
    assert b"<script>alert(1)</script>" not in html
    assert b"onerror=" not in html
