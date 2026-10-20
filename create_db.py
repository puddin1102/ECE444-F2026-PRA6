"""Create missing tables without deleting existing posts."""

from app import app
from project.extensions import db

with app.app_context():
    db.create_all()
    if db.engine.dialect.name == "postgresql":
        # Flask connects as the DB owner; anonymous Supabase API clients cannot.
        db.session.execute(db.text("ALTER TABLE post ENABLE ROW LEVEL SECURITY"))
        db.session.commit()
    print("Database tables are ready.")
