import pytest
from app import app as flask_app
from database.db import init_db


@pytest.fixture
def app():
    flask_app.config.update({'TESTING': True, 'DATABASE': ':memory:'})
    with flask_app.app_context():
        init_db()
        yield flask_app
