from werkzeug.security import generate_password_hash, check_password_hash
from app import database
from app.models import User

def signup(username: str, password: str):
    '''creates new user with given username and password. '''
    
    pass_hash = generate_password_hash(password)
    user = User({'username': username, 'password': pass_hash})
    return database.add_or_update(user)
