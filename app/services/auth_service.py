from werkzeug.security import generate_password_hash, check_password_hash
from app import database
from app.models import User
import jwt
from flask import current_app
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound


class AuthException(Exception):
    '''When authentication exception occurs.'''
    def __init__(self, message):            
        super().__init__(message)

def get_all_users():
    users = database.get_all(User)
    print(f"get users = {users}")
    return users

def signup(username: str, password: str):
    '''creates new user with given username and password. '''
    
    pass_hash = generate_password_hash(password)
    user = User({'username': username, 'password': pass_hash})
    return database.add_or_update(user)

def login(username: str, password: str):
    '''login with given username and password'''
    
    # find user
    user = database.find_by_username(username)
    if not user:
        raise NoResultFound(f"No user with given username: {username}")
    
    # check password
    is_password_correct = check_password_hash(user.password, password)
    if not is_password_correct:
        raise AuthException('wrong password provided')
    
    token = jwt.encode({'username': user.username, 'role': user.role.name, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                        current_app.config['SECRET_KEY'],
                        algorithm='HS256')
    
    return token

