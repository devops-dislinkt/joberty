from flask import Blueprint, jsonify, request
from sqlalchemy import Integer

from app import database
from app.models import User
from app.services import auth_service
from app.services import company_service
from app.services.company_service import NotApproved
from app.services.auth_service import AuthException 
from sqlalchemy.exc import IntegrityError

from app import db
    
api = Blueprint('api', __name__)
from app.routes_utils import check_token, required_roles, get_logged_in_user

@api.get('/test')
def test():
    #user = User(username='pera',password='pera', id=1)
    #database.add_or_update(user)
    #user = database.find_by_username('pera')
    #print(user.role.name)
    #return jsonify(user.to_dict())
    print("delete all new")
    db.drop_all()
    db.create_all()
    return jsonify({})

@api.get('/allusers')
def get_users():
    users = auth_service.get_all_users()
    return jsonify([user.to_dict() for user in users])

@api.get('/allcomments')
def get_comments():
    comments = company_service.get_all_comments()
    return jsonify([c.to_dict() for c in comments])

@api.get('/allinterviewcomments')
def get_interview_comments():
    comments = company_service.get_all_interview()
    return jsonify([c.to_dict() for c in comments])
    
@api.get('/allsalaries')
def get_salaries():
    salaries = company_service.get_all_salaries()
    return jsonify([c.to_dict() for c in salaries])

@api.get('/companies')
def get_companies():
    companies = company_service.get_all_companies('all')
    return jsonify([c.to_dict() for c in companies])

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


@api.post('/company/resolve-registration')
@check_token
@required_roles(['admin'])
def resolve_company_registration():
    '''Only admin role can resolve registration request.'''

    data = request.json
    if not data or data.get('reject') == None or data.get('username') == None:
        return 'did not receive reject status or username.', 400
    
    company = company_service.resolve_company_registration(username=data.get('username'),
                                                            reject=data.get('reject'))
    if company == True:
        return 'successfully deleted.', 200
    
    return jsonify(company.to_dict())


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

@api.get('/get-company/<int:company_id>')
def get_one_company(company_id:int):
    '''Returns all/approved/not-resolved companies. Type param can be: all, appproved or not-resolved.'''
    if not company_id:
        return 'did not receive data.', 400
    print("get company route")
    company = company_service.get_one_company(company_id)
    return jsonify(company.to_dict())

@api.get('/company/<string:type>')
@check_token
@required_roles(['admin'])
def get_company(type:str):
    '''Returns all/approved/not-resolved companies. Type param can be: all, appproved or not-resolved.'''
    if not type:
        return 'did not receive data.', 400

    companies = company_service.get_all_companies(type)
    return jsonify([company.to_dict() for company in companies])

@api.get('/get-company-comments/<int:company_id>')
def get_company_comments(company_id:int):
    comments = company_service.get_company_comments(company_id)
    return jsonify([c.to_dict() for c in comments])

@api.post('/company/<int:company_id>/comment')
#@check_token
#@required_roles(['user'])
def create_comment(company_id: int):
    '''
    Logged in user (ony as user role) creates comment for specified (only approved) company. 
    Returns created comment.
    '''
    data = request.json
    if not data or not data.get('rating'):
        return 'did not receive data.', 400
    print(f"comment data = {data}")
    
    user = get_logged_in_user(request)
    try: 
        comment = company_service.create_comment(user, company_id, data)
        return jsonify(comment.to_dict())
    except NotApproved as e:
        return jsonify(str(e)), 400
    except Exception as e:
        return jsonify(str(e)), 403

@api.post('/company/<int:company_id>/interview')
#@check_token
#@required_roles(['user'])
def create_interview_comment(company_id: int):
    '''
    Logged in user (ony as user role) creates interview comment for specified (only approved) company. 
    Returns created interview comment.
    '''
    data = request.json
    if not data or not data.get('rating'):
        return 'did not receive data.', 400
    print(f"interview comment data = {data}")
    
    user = get_logged_in_user(request)
    try: 
        comment = company_service.create_interview_comment(user, company_id, data)
        return jsonify(comment.to_dict())
    except NotApproved as e:
        return jsonify(str(e)), 400
    except Exception as e:
        return jsonify(str(e)), 403

@api.post('/company/<int:company_id>/salary')
#@check_token
#@required_roles(['user'])
def create_salary(company_id: int):
    '''
    Logged in user (ony as user role) creates salary for specified (only approved) company. 
    Returns created salary.
    '''
    data = request.json
    if not data or not data.get('salary'):
        return 'did not receive data.', 400
    print(f"salary data = {data}")
    
    user = get_logged_in_user(request)
    try: 
        comment = company_service.create_salary(user, company_id, data)
        return jsonify(comment.to_dict())
    except NotApproved as e:
        return jsonify(str(e)), 400
    except Exception as e:
        return jsonify(str(e)), 403