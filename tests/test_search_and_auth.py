"""Additional tests designed for the tutorial's Search and Login Required tasks."""
import pytest

from project.extensions import db
from project.models import Post


@pytest.fixture
def posts(app):
    with app.app_context():
        db.session.add_all([
            Post(title="Flask tips", text="Test-driven development"),
            Post(title="Database notes", text="Postgres works with FLASK"),
            Post(title="Other idea", text="Unrelated content"),
        ])
        db.session.commit()


def test_search_page_without_query(client, posts):
    response = client.get("/search/")
    assert response.status_code == 200
    assert b"Search posts" in response.data
    assert b"Flask tips" not in response.data


@pytest.mark.parametrize("query,expected,excluded", [
    ("flask", [b"Flask tips", b"Database notes"], [b"Other idea"]),
    ("TEST-DRIVEN", [b"Flask tips"], [b"Database notes", b"Other idea"]),
    ("  postgres  ", [b"Database notes"], [b"Flask tips", b"Other idea"]),
])
def test_search_title_and_body_case_insensitive(client, posts, query, expected, excluded):
    response = client.get("/search/", query_string={"query": query})
    assert response.status_code == 200
    for title in expected:
        assert title in response.data
    for title in excluded:
        assert title not in response.data


def test_search_no_matches(client, posts):
    assert b"No matching entries." in client.get("/search/?query=missing").data


def test_search_treats_wildcards_as_text(client, posts):
    assert b"No matching entries." in client.get("/search/?query=%25").data


def test_search_escapes_query(client):
    html = client.get("/search/", query_string={"query": '<script>alert("x")</script>'}).data
    assert b"<script>alert(" not in html
    assert b"&lt;script&gt;" in html


def test_anonymous_delete_denied_and_post_preserved(client, app, posts):
    with app.app_context():
        post_id = db.session.scalar(db.select(Post.id))
    response = client.get(f"/delete/{post_id}")
    assert response.status_code == 401
    assert response.json == {"status": 0, "message": "Please log in."}
    with app.app_context():
        assert db.session.get(Post, post_id) is not None


def test_logout_revokes_delete_access(logged_in, app, posts):
    with app.app_context():
        post_id = db.session.scalar(db.select(Post.id))
    logged_in.get("/logout")
    assert logged_in.get(f"/delete/{post_id}").status_code == 401
    with app.app_context():
        assert db.session.get(Post, post_id) is not None


def test_anonymous_missing_post_still_requires_login(client):
    assert client.get("/delete/999999").status_code == 401
