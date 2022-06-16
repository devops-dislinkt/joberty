from flask import Blueprint, jsonify, request

from app import database
from app.models import User
from app.services import auth_service
from app.services import company_service
from app.services.company_service import NotApproved
from app.services.auth_service import AuthException 
from sqlalchemy.exc import IntegrityError


api = Blueprint('api', __name__)
from app.routes_utils import check_token, required_roles, get_logged_in_user

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


@api.post('/login')
def login():
    '''login on system'''
    data = request.json
    if not data or not data.get('username') or not data.get('password'): 
        return 'did not receive username or password', 400 
    
    username = data['username']
    password = data['password']

    try:
        token = auth_service.login(username, password)
        return jsonify(token)
    except AuthException as e:
        return jsonify(str(e)), 400


@api.put('/company/resolve-registration')
@check_token
def resolve_company_registration():
    # TODO: ADMIN ODOBRAVA ILI ODBIJA REGISTRACIJU za kompaniju
    data = request.json
    if not data or not data.get('reject'):
        return 'did not receive reject status.', 400
    
    user = get_logged_in_user(request)
    reject = data.get('reject')
    user = auth_service.resolve_company_registration(user, reject)
    if not user:
        return 'user already approved.'
    pass

@api.post('/company')
@check_token
def create_company_registration():
    data = request.json
    if not data:
        return 'did not receive data.', 400

    user = get_logged_in_user(request)    
    try: 
        company = company_service.create_company_registration(user, data)
        return jsonify(company.to_dict())

    except IntegrityError as e:
        return jsonify(str(e)), 400
    