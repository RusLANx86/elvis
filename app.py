import logging
from flask import Flask
from sqlalchemy_utils import database_exists, create_database
from flask_migrate import Migrate

import os
from flasgger import Swagger

from models import db
from routes import set_routes

app = Flask(__name__)

# Инициализация приложения Flask и конфигурации базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:q1w2e3r4@localhost:5432/achievements_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.dirname(__file__)}/achievements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
set_routes(app)

# Инициализация базы данных и миграций
if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()
    db.session.commit()

migrate = Migrate(app, db)
Swagger(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    app.run(debug=True)
