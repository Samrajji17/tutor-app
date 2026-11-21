import pytest

from app import create_app
from app.extensions import db
from app.models import Admin
from app.services import ratelimit
from config import TestConfig


@pytest.fixture()
def app():
    ratelimit.reset()
    app = create_app(TestConfig)
    with app.app_context():
        admin = Admin(username="teacher")
        admin.set_password("correct-horse-battery")
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(user="teacher", password="correct-horse-battery"):
        return client.post("/admin/login", data={"username": user, "password": password})
    return _login


VALID_FORM = {
    "student_name": "Anu Kumar", "student_class": "9", "school_name": "Govt Higher Secondary School",
    "subjects": ["Mathematics"], "parent_name": "Kumar S", "relationship": "Father",
    "mobile": "98765 43210", "mode": "Offline", "preferred_days": ["Mon", "Wed"],
    "preferred_time": "Evening", "email": "kumar@example.com",
}


@pytest.fixture()
def form_data():
    return dict(VALID_FORM)
