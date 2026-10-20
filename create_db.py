"""Create missing tables without deleting existing posts."""

from app import app
from project.extensions import db

with app.app_context():
    db.create_all()
    print("Database tables are ready.")
