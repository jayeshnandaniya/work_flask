from unittest.mock import patch
import pytest
import datetime


@pytest.fixture
def users():
    from src.resources import users
    return users


@pytest.fixture
def auth():
    from src.resources import authentication
    return authentication


@pytest.fixture
def notifications():
    from src.resources import notifications
    return notifications


@pytest.fixture
def request_json():
    return {
        'email': 'some@mail.com',
        'password': '12345',
        'handle': 'queenb',
        'image_is_local': True,
        'image_url': 'http://someimage.jpg'
    }
import argon2
ph = argon2.PasswordHasher(hash_len=64, salt_len=32)

@pytest.fixture
def model_user():

    class User():
        id = 42
        name = 'Jorge'
        email = 'gg@mail.com'
        handle = 'JorgeTheBoy'
        image_url = ''
        created_at = datetime.time()
        expo_push_token = ''
        availability = ''
        password_hash = ph.hash("password")

    return User


@pytest.fixture
def model_notification():

    class Notification():
        id = 8
        user_id = 42
        only_read = True
        only_unread = False
        before = datetime.time()
        after = datetime.time()
        created_at = datetime.time()
        category = 'apples'
        text = 'notify or be notified'
        data = 'XYZ'
        is_read = True

    return Notification
