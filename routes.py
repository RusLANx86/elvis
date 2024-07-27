import logging
from datetime import datetime, timedelta
from flask import jsonify, request
from sqlalchemy import func
from flasgger import swag_from

from models import User, Achievement, UserAchievement, db


def set_routes(app, logger):
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

    @app.route('/users', methods=['GET'])
    def get_users():
        """Получить список всех пользователей
        ---
        responses:
            200:
                description: Список пользователей
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            id:
                                type: integer
                                description: Идентификатор пользователя
                            username:
                                type: string
                                description: Имя пользователя
                            language:
                                type: string
                                description: Язык пользователя
        """
        users = User.query.all()
        users_list = [{'id': user.id, 'username': user.username, 'language': user.language} for user in users]
        return jsonify(users_list)

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
        # Пользователь с максимальным количеством достижений
        max_achievements_user = db.session.query(
            User.username,
            func.count(UserAchievement.id).label('total')
        ).join(UserAchievement).group_by(User.id, User.username).order_by(func.count(UserAchievement.id).desc()).first()

        # Пользователь с максимальным количеством очков
        max_points_user = db.session.query(
            User.username,
            func.sum(Achievement.points).label('total')
        ).select_from(User).join(UserAchievement, User.id == UserAchievement.user_id).join(Achievement,
                                                                                           UserAchievement.achievement_id == Achievement.id).group_by(
            User.id).order_by(func.sum(Achievement.points).desc()).first()

        # Пользователи с их суммой очков
        user_achievements = db.session.query(
            User.username,
            func.sum(Achievement.points).label('total')
        ).select_from(User).join(UserAchievement, User.id == UserAchievement.user_id).join(Achievement,
                                                                                           UserAchievement.achievement_id == Achievement.id).group_by(
            User.id).all()

        # Пользователи с максимальной разностью очков
        if len(user_achievements) > 1:
            max_diff_user1 = max(user_achievements, key=lambda x: x.total)
            max_diff_user2 = min(user_achievements, key=lambda x: x.total)
        else:
            max_diff_user1 = max_diff_user2 = None

        sorted_user_achievements = sorted(user_achievements, key=lambda l: l.total)
        min_diff_user1 = sorted_user_achievements[0]
        min_diff_user2 = sorted_user_achievements[1]
        min_length = min_diff_user2.total - min_diff_user1.total
        for i in range(2, len(sorted_user_achievements)):
            length = sorted_user_achievements[i].total - min_diff_user2.total
            if length < min_length:
                min_diff_user1 = min_diff_user2
                min_diff_user2 = sorted_user_achievements[i]
                min_length = length

        # Пользователи, которые получали достижения 7 дней подряд
        from collections import defaultdict

        def get_user_achievements_dict():
            users_achievements = db.session.query(
                User.id,
                User.username,
                UserAchievement.date_awarded
            ).join(UserAchievement).order_by(User.id, UserAchievement.date_awarded).all()

            user_achievements_dict = defaultdict(list)

            for user_id, username, date_awarded in users_achievements:
                user_achievements_dict[username].append(date_awarded)

            # функция, которая проверяет, есть ли в списке временных меток достижения в 7 последовательных дней
            def has_streak_of_seven_days(dates):
                # Сортируем даты на случай, если они не отсортированы
                sorted_dates = sorted(dates)

                streak = 1
                for i in range(1, len(sorted_dates)):
                    # Проверяем, является ли текущая дата следующей по отношению к предыдущей
                    if sorted_dates[i].date() - sorted_dates[i - 1].date() == timedelta(days=1):
                        streak += 1
                        # Если нашли 7 последовательных дней, возвращаем True
                        if streak == 7:
                            return True
                    else:
                        streak = 1

                return False

            streak_users = []
            for user_name, dates in user_achievements_dict.items():
                if has_streak_of_seven_days(dates):
                    streak_users.append(user_name)

            return streak_users

        streak_users = get_user_achievements_dict()

        # Сбор статистики
        stats = {
            'max_achievements_user': {
                'username': max_achievements_user.username if max_achievements_user else None,
                'total': max_achievements_user.total if max_achievements_user else 0
            },
            'max_points_user': {
                'username': max_points_user.username if max_points_user else None,
                'total': max_points_user.total if max_points_user else 0
            },
            'max_diff_users': {
                'username1': max_diff_user1.username if max_diff_user1 else None,
                'username2': max_diff_user2.username if max_diff_user2 else None,
                'total': max_diff_user1.total - max_diff_user2.total
            },
            'min_diff_users': {
                'username1': min_diff_user1.username if min_diff_user1 else None,
                'username2': min_diff_user2.username if min_diff_user2 else None,
                'total': min_length
            },
            'streak_users': [{'username': username} for username in streak_users]
        }

        return jsonify(stats)
