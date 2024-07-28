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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:q1w2e3r4@db/achievements_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.dirname(__file__)}/achievements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'Тестовое задание. Разработка API для работы с достижениями',
    'uiversion': 3,
    'description': 'Это простой сервер для работы с достижениями пользователей. Вы можете добавлять пользователей, добавлять достижения и выдавать их пользователям.',
    'termsOfService': 'http://example.com/terms/',
    'contact': {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    },
    'license': {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
}
# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w')
logger = logging.getLogger(__name__)

db.init_app(app)
set_routes(app, logger)

# Инициализация базы данных и миграций
if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()
    db.session.commit()

migrate = Migrate(app, db)
Swagger(app)

if __name__ == '__main__':
    app.run(debug=True)
