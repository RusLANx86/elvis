import json
import pytest


def test_add_user(test_client):
    """Тест добавления нового пользователя."""
    response = test_client.post('/user', json={
        'username': 'testuser',
        'language': 'en'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User created successfully'
    assert 'user_id' in data


def test_get_users(test_client):
    """Тест получения списка пользователей."""
    test_client.post('/user', json={
        'username': 'testuser',
        'language': 'en'
    })
    response = test_client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['username'] == 'testuser'


def test_get_user(test_client):
    """Тест получения пользователя по ID."""
    response = test_client.post('/user', json={
        'username': 'testuser',
        'language': 'en'
    })
    user_id = json.loads(response.data)['user_id']
    response = test_client.get(f'/user/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'testuser'


def test_add_achievement(test_client):
    """Тест добавления нового достижения."""
    response = test_client.post('/achievement', json={
        'name': 'Test Achievement',
        'points': 10,
        'description': 'Test description'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Achievement added successfully'


def test_award_achievement(test_client):
    """Тест выдачи достижения пользователю."""
    user_response = test_client.post('/user', json={
        'username': 'testuser',
        'language': 'en'
    })
    user_id = json.loads(user_response.data)['user_id']

    achievement_response = test_client.post('/achievement', json={
        'name': 'Test Achievement',
        'points': 10,
        'description': 'Test description'
    })
    achievement_id = json.loads(achievement_response.data)['id']

    response = test_client.post(f'/user/{user_id}/achieve/{achievement_id}')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Achievement awarded successfully'


def test_get_user_achievements(test_client):
    """Тест получения списка достижений пользователя."""
    user_response = test_client.post('/user', json={
        'username': 'testuser',
        'language': 'en'
    })
    user_id = json.loads(user_response.data)['user_id']

    achievement_response = test_client.post('/achievement', json={
        'name': 'Test Achievement',
        'points': 10,
        'description': 'Test description'
    })
    achievement_id = json.loads(achievement_response.data)['id']

    test_client.post(f'/user/{user_id}/achieve/{achievement_id}')

    response = test_client.get(f'/user/{user_id}/achievements')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['name'] == 'Test Achievement'


def test_get_stats(test_client):
    """Тест получения статистических данных."""
    response = test_client.get('/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'max_achievements_user' in data
    assert 'max_points_user' in data
    assert 'max_diff_users' in data
    assert 'min_diff_users' in data
    assert 'streak_users' in data
