from flask import Blueprint, jsonify, request

from app import database
from app.models import User
from app.services import auth_service
api = Blueprint('api', __name__)
import app.routes_utils
from sqlalchemy.exc import IntegrityError

@api.get('/test')
def test():
    user = User(username='pera',password='pera', id=1)
    database.add_or_update(user)
    user = database.find_by_username('pera')
    print(user.role.name)
    return jsonify(user.to_dict())


@api.post('/signup')
def signup():
    '''Registers new user on the system'''
    data = request.json
    if not data or not data.get('username') or not data.get('password'): 
        return 'did not receive username or password', 400 
    
    try:
        user = auth_service.signup(data.get('username'), data.get('password'))
        return jsonify(user.to_dict())
    except IntegrityError:
        return 'username not unique', 400


