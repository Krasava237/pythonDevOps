from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'non.existent@mail.com'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Sergey Sergeev',
        'email': 's.s.sergeev@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    user_id = response.json()
    assert isinstance(user_id, int)

    # Проверка, что пользователь создан
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    user_data = get_response.json()
    assert user_data['name'] == new_user['name']
    assert user_data['email'] == new_user['email']
    assert user_data['id'] == user_id

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = users[0]
    new_user = {
        'name': 'Duplicate',
        'email': existing_user['email']
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with this email already exists'}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создадим пользователя, чтобы потом удалить
    new_user = {
        'name': 'Temp User',
        'email': 'temp.user@mail.com'
    }
    create_response = client.post("/api/v1/user", json=new_user)
    assert create_response.status_code == 201
    user_id = create_response.json()

    # Удаление по email через query-параметр
    delete_response = client.delete("/api/v1/user", params={'email': new_user['email']})
    assert delete_response.status_code == 204

    # Проверка, что пользователя больше нет
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 404
