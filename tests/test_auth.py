import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture
def app():
    class TestConfig:
        TESTING=True
        SECRET_KEY='test-secret'
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS=False
        WTF_CSRF_ENABLED=False
    app=create_app(TestConfig)
    with app.app_context(): db.create_all(); yield app; db.drop_all()

@pytest.fixture
def client(app): return app.test_client()

def test_teacher_registration(client):
    r=client.post('/auth/register',data={'full_name':'Guru','email':'guru@example.com','password':'password123','confirm_password':'password123'},follow_redirects=True)
    assert r.status_code==200
    with client.application.app_context():
        u=db.session.scalar(db.select(User).where(User.email=='guru@example.com'))
        assert u and u.role=='TEACHER' and u.password_hash!='password123' and u.check_password('password123')

def test_public_registration_cannot_create_admin(client):
    client.post('/auth/register',data={'full_name':'Admin','email':'admin@example.com','password':'password123','confirm_password':'password123'})
    with client.application.app_context():
        u=db.session.scalar(db.select(User).where(User.email=='admin@example.com'))
        assert u.role=='TEACHER'
