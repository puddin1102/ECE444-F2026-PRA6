import os
from functools import wraps
from pathlib import Path

import bleach
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.pool import NullPool

from project.extensions import db
from project.models import Post


def login_required(view):
    """Protect a view while preserving its name for Flask's URL routing."""

    @wraps(view)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify(status=0, message="Please log in."), 401
        return view(*args, **kwargs)

    return decorated


def create_app(test_config=None):
    load_dotenv()
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, static_folder=str(root / "public"), static_url_path="")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{root / 'flaskr.db'}")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "local-development-only"),
        USERNAME=os.getenv("ADMIN_USERNAME", "admin"),
        PASSWORD=os.getenv("ADMIN_PASSWORD", "admin"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=bool(os.getenv("VERCEL")),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if os.getenv("VERCEL") and not app.config.get("TESTING"):
        if not os.getenv("DATABASE_URL") or database_url.startswith("sqlite"):
            raise RuntimeError("Vercel requires an external Postgres DATABASE_URL.")
        if not os.getenv("SECRET_KEY") or not os.getenv("ADMIN_PASSWORD"):
            raise RuntimeError("Set SECRET_KEY and ADMIN_PASSWORD in Vercel.")
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
        # Avoid retaining idle DB connections across serverless invocations.
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "poolclass": NullPool,
            "connect_args": {"sslmode": "require", "connect_timeout": 10},
        }
    db.init_app(app)

    @app.template_filter("safe_post")
    def safe_post(text):
        # Keep the tutorial's formatting feature without allowing scripts/events.
        return bleach.clean(
            text,
            tags={"p", "br", "strong", "em", "b", "i", "ul", "ol", "li"},
            attributes={},
            strip=True,
        )

    @app.get("/")
    def index():
        entries = db.session.scalars(db.select(Post).order_by(Post.id.desc())).all()
        return render_template("index.html", entries=entries)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            if request.form.get("username") != app.config["USERNAME"]:
                error = "Invalid username"
            elif request.form.get("password") != app.config["PASSWORD"]:
                error = "Invalid password"
            else:
                session.clear()
                session["logged_in"] = True
                flash("You were logged in")
                return redirect(url_for("index"))
        return render_template("login.html", error=error)

    @app.get("/logout")
    def logout():
        session.clear()
        flash("You were logged out")
        return redirect(url_for("index"))

    @app.post("/add")
    @login_required
    def add_entry():
        title = request.form.get("title", "").strip()
        text = request.form.get("text", "").strip()
        if not title or not text or len(title) > 200:
            return (
                render_template(
                    "error.html",
                    message="Enter a title (1-200 characters) and post text.",
                ),
                400,
            )
        db.session.add(Post(title=title, text=text))
        db.session.commit()
        flash("New entry was successfully posted")
        return redirect(url_for("index"))

    @app.get("/delete/<int:post_id>")
    @login_required
    def delete_entry(post_id):
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify(status=0, message="Post not found"), 404
        db.session.delete(post)
        db.session.commit()
        flash("The entry was deleted.")
        return jsonify(status=1, message="Post Deleted")

    @app.get("/search/")
    def search():
        query = request.args.get("query", "").strip()
        entries = []
        if query:
            statement = (
                db.select(Post)
                .where(
                    db.or_(
                        Post.title.icontains(query, autoescape=True),
                        Post.text.icontains(query, autoescape=True),
                    )
                )
                .order_by(Post.id.desc())
            )
            entries = db.session.scalars(statement).all()
        return render_template("search.html", query=query, entries=entries)

    return app
