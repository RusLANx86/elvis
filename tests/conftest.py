import pytest
from app import app, db
from flask import Flask
from sqlalchemy_utils import create_database, database_exists
import os


@pytest.fixture(scope='module')
def test_client():
    # Создание тестовой базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()
        os.remove('test.db')


@pytest.fixture(scope='module')
def test_app():
    return app
