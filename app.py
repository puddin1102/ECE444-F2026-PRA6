"""WSGI entrypoint discovered automatically by Vercel."""

from project.app import create_app

app = create_app()
