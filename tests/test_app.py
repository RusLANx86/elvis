import pytest
from app import app, db
from models import User, Achievement, UserAchievement


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_hello(client):
    response = client.get('/user/1')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'User not found'


def test_add_user(client):
    user = User(username="testuser", language="en")
    db.session.add(user)
    db.session.commit()

    response = client.get('/user/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testuser'
    assert data['language'] == 'en'
