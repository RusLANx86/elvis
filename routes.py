import logging
from datetime import datetime
from flask import jsonify, request
from sqlalchemy import func
from flasgger import swag_from

from models import User, Achievement, UserAchievement, db

logger = logging.getLogger(__name__)


def set_routes(app):
    @app.route('/')
    def index():
        return '<h1>Started Page</h1>'

    @app.route('/user', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'language': {'type': 'string', 'enum': ['ru', 'en']}
                    },
                    'required': ['username', 'language']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'User created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'user_id': {'type': 'integer'}
                    }
                }
            },
            400: {
                'description': 'Invalid input',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def add_user():
        """Добавляет нового пользователя."""
        data = request.get_json()
        if 'username' not in data or 'language' not in data:
            logger.warning('Invalid input data for user creation')
            return jsonify({'error': 'Invalid input'}), 400

        new_user = User(
            username=data['username'],
            language=data['language']
        )
        db.session.add(new_user)
        db.session.commit()
        logger.info(f'User {data["username"]} added successfully')
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201

    @app.route('/user/<int:user_id>', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID пользователя'
            }
        ],
        'responses': {
            200: {
                'description': 'Пользователь найден',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'language': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'Пользователь не найден',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def get_user(user_id):
        """Возвращает информацию о пользователе по его ID."""
        user = User.query.get(user_id)
        if not user:
            logger.warning(f'User with id {user_id} not found')
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'username': user.username, 'language': user.language})

    @app.route('/achievements', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Список достижений',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'points': {'type': 'integer'},
                            'description': {'type': 'string'}
                        }
                    }
                }
            }
        }
    })
    def get_achievements():
        """Возвращает список всех достижений."""
        achievements = Achievement.query.all()
        return jsonify([{
            'name': achievement.name,
            'points': achievement.points,
            'description': achievement.description
        } for achievement in achievements])

    @app.route('/achievement', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'points': {'type': 'integer'},
                        'description': {'type': 'string'}
                    },
                    'required': ['name', 'points', 'description']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Achievement added successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def add_achievement():
        """Добавляет новое достижение."""
        data = request.get_json()
        new_achievement = Achievement(
            name=data['name'],
            points=data['points'],
            description=data['description']
        )
        db.session.add(new_achievement)
        db.session.commit()
        logger.info(f'Achievement {data["name"]} added successfully')
        return jsonify({'message': 'Achievement added successfully'}), 201

    @app.route('/user/<int:user_id>/achieve/<int:achievement_id>', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID пользователя'
            },
            {
                'name': 'achievement_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID достижения'
            }
        ],
        'responses': {
            201: {
                'description': 'Achievement awarded successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'User or Achievement not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def award_achievement(user_id, achievement_id):
        """Выдаёт достижение пользователю."""
        user = User.query.get(user_id)
        achievement = Achievement.query.get(achievement_id)
        if not user or not achievement:
            logger.warning(f'User or Achievement not found (user_id={user_id}, achievement_id={achievement_id})')
            return jsonify({'error': 'User or Achievement not found'}), 404
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            date_awarded=datetime.utcnow()
        )
        db.session.add(user_achievement)
        db.session.commit()
        logger.info(f'Achievement {achievement_id} awarded to user {user_id}')
        return jsonify({'message': 'Achievement awarded successfully'}), 201

    @app.route('/user/<int:user_id>/achievements', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID пользователя'
            }
        ],
        'responses': {
            200: {
                'description': 'List of user achievements',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'points': {'type': 'integer'},
                            'description': {'type': 'string'},
                            'date_awarded': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            },
            404: {
                'description': 'User not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def get_user_achievements(user_id):
        """Возвращает список достижений пользователя."""
        user = User.query.get(user_id)
        if not user:
            logger.warning(f'User with id {user_id} not found')
            return jsonify({'error': 'User not found'}), 404
        achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        user_achievements = []
        for ua in achievements:
            achievement = Achievement.query.get(ua.achievement_id)
            user_achievements.append({
                'name': achievement.name,
                'points': achievement.points,
                'description': achievement.description,
                'date_awarded': ua.date_awarded.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(user_achievements)

    @app.route('/stats', methods=['GET'])
    def get_stats():
        x = func.count(UserAchievement.id)
        max_achievements_user = db.session.query(User, func.count(UserAchievement.id).label('total')).join(
            UserAchievement).group_by(User.id).order_by(func.count(UserAchievement.id).desc()).first()
        max_points_user = db.session.query(User, func.sum(Achievement.points).label('total')).join(
            UserAchievement).join(
            Achievement).group_by(User.id).order_by(func.sum(Achievement.points).desc()).first()

        user_achievements = db.session.query(User.id, func.sum(Achievement.points).label('total')).join(
            UserAchievement).join(Achievement).group_by(User.id).all()

        max_diff_users = max(user_achievements, key=lambda x: x.total, default=None)
        min_diff_users = min(user_achievements, key=lambda x: x.total, default=None)

        streak_users = db.session.query(User).join(UserAchievement).group_by(User.id).having(
            func.count(func.distinct(func.date(UserAchievement.date_awarded))) >= 7).all()

        stats = {
            'max_achievements_user': {'username': max_achievements_user.User.username,
                                      'total': max_achievements_user.total} if max_achievements_user else None,
            'max_points_user': {'username': max_points_user.User.username,
                                'total': max_points_user.total} if max_points_user else None,
            'max_diff_users': {'username': max_diff_users.User.username,
                               'total': max_diff_users.total} if max_diff_users else None,
            'min_diff_users': {'username': min_diff_users.User.username,
                               'total': min_diff_users.total} if min_diff_users else None,
            'streak_users': [{'username': user.username} for user in streak_users]
        }

        return jsonify(stats)
