from email import header
import pytest
from flask import current_app
from flask.testing import FlaskClient
from app import create_app, db
from app.models import User, Company, UserRole
from werkzeug.security import generate_password_hash
import jwt
from datetime import datetime, timedelta

mika = User(
    {
        "id": 1,
        "username": "mika_test",
        "password": generate_password_hash("mikamika"),
        "role": UserRole.user,
    }
)
zika = User(
    {
        "id": 2,
        "username": "zika_test",
        "password": generate_password_hash("zikazika"),
        "role": UserRole.user,
    }
)
admin = User(
    {
        "id": 3,
        "username": "admin_test",
        "password": generate_password_hash("adminadmin"),
        "role": UserRole.admin,
    }
)

def seed_db():

    users = [mika, zika, admin]

    db.session.bulk_save_objects(users)
    db.session.commit()


@pytest.fixture(scope="module")
def client() -> FlaskClient:
    """
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    """

    # setup
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()
        

    with app.test_client() as client:
        yield client

    # teardown
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def valid_co_data():
    return {
        'approved': False,
        'name': 'co4',
        'email': 'contact@co4.com',
        'location': 'ulica 4, Neki Grad',
        'website': 'website.co4.com',
        'description': 'best company ever'
    }

@pytest.fixture(scope="function")
def invalid_co_data():
    return {
        'approved': False,
        'name': 'co4',
        'email': 'contact@co4.com',
        'location': 'ulica 4, Neki Grad',
        'trash': 'trash'
    }


class TestCompany:
    '''Test case for unit tests for company.'''

    def get_headers_valid(self, user: User) -> dict:
        """Create headers for authentication and returns headers dictionary."""
        token = jwt.encode({'username': user.username, 'role': user.role.name, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                        key='secret',
                        algorithm='HS256')

        headers = {'authorization': f'Bearer {token}'}
        return headers

    def get_headers_invalid(self) -> dict:
        """Create invalid headers with non existing user and returns headers dictionary."""
        headers = {'authorization': f'Bearer 12345'}
        return headers


    def test_create_company_request_success(self, client: FlaskClient, valid_co_data:dict):
        response = client.post('/api/company', json=valid_co_data, headers=self.get_headers_valid(mika))
        assert response.status_code == 200
        assert response.json['approved'] == False
    

    def test_create_company_request_without_login(self, client: FlaskClient, valid_co_data:dict):
        '''Request should fail if user is not logged in.'''
        response = client.post('/api/company', json=valid_co_data)
        assert response.status_code == 403
    

    def test_create_company_request_with_invalid_data(self, client: FlaskClient, invalid_co_data:dict):
        '''Request should fail if invalid data.'''
        response = client.post('/api/company', json=invalid_co_data, headers=self.get_headers_valid(mika))
        assert response.status_code == 400


    def test_reject_company_registration(self, client: FlaskClient):
        '''Only admin can resolve company registration. When admin rejects, company is deleted.'''
        incoming_data = {'reject': True, 'username': mika.username}
        response = client.post('/api/company/resolve-registration', json=incoming_data, headers=self.get_headers_valid(admin))
        assert response.status_code == 200

    
    def test_accept_company_registration(self, client: FlaskClient, valid_co_data:dict):
        '''Only admin can resolve company registration. When admin accepts, company is approved and user becomes the owner.'''
        # make request first
        req_res = client.post('/api/company', json=valid_co_data, headers=self.get_headers_valid(zika))
        
        incoming_data = {'reject': False, 'username': zika.username}
        response = client.post('/api/company/resolve-registration', json=incoming_data, headers=self.get_headers_valid(admin))
        assert response.status_code == 200
        assert response.json['approved'] == True
        assert response.json['user']['company']['id'] == req_res.json['id']
        assert response.json['user']['role'] == UserRole.company_owner.value

    def test_accept_company_registration_with_wrong_role(self, client: FlaskClient, valid_co_data:dict):
        '''Only admin can resolve company registration. When admin accepts, company is approved and user becomes the owner.'''
        # make request first
        req_res = client.post('/api/company', json=valid_co_data, headers=self.get_headers_valid(zika))
        
        incoming_data = {'reject': False, 'username': zika.username}
        response = client.post('/api/company/resolve-registration', json=incoming_data, headers=self.get_headers_valid(zika))
        assert response.status_code == 403

    
    def test_get_all_companies(self, client: FlaskClient):
        '''Should return all companies'''
        response = client.get('/api/company/all', headers=self.get_headers_valid(admin))
        assert response.status_code == 200
        assert 2 == len(response.json)

    
    def test_get_all_approved_companies(self, client: FlaskClient):
        '''Should return all companies'''
        response = client.get('/api/company/approved', headers=self.get_headers_valid(admin))
        assert response.status_code == 200
        assert 1 == len(response.json)

    
    def test_get_all_not_resolved_companies(self, client: FlaskClient):
        '''Should return all companies'''
        response = client.get('/api/company/not-resolved', headers=self.get_headers_valid(admin))
        assert response.status_code == 200
        assert 1 == len(response.json)

    def test_create_comment_success(self, client: FlaskClient):
        '''Zika's company co4 is approved. For that company user mika can create comment.'''
        description = 'My name is Giovani Giorgio and I love woriking for co4.'
        company_id = 3
        response = client.post(f'/api/company/{company_id}/comment', json={'description': description}, headers=self.get_headers_valid(mika))
        assert response.status_code == 200
        assert description == response.json['description']
        assert mika.id == response.json['user_id']
        
    def test_create_comment_for_not_approved_company(self, client: FlaskClient):
        '''Comment cannot create for not approved company.'''
        description = 'My name is Giovani Giorgio and I love woriking for co4.'
        company_id = 4
        response = client.post(f'/api/company/{company_id}/comment', json={'description': description}, headers=self.get_headers_valid(mika))
        print(response.json)
        assert response.status_code == 400
        
    def test_create_comment_as_company_owner(self, client: FlaskClient):
        '''Comment cannot create company owner.'''
        description = 'My name is Giovani Giorgio and I love woriking for co4.'
        company_id = 3
        response = client.post(f'/api/company/{company_id}/comment', json={'description': description}, headers=self.get_headers_valid(zika))
        assert response.status_code == 403
        
    def test_add_grade(self, client: FlaskClient):
        '''Zika's company co4 is approved. For that company user mika can add grade.'''
        grade = 5;
        company_id = 3
        response = client.post(f'/api/company/{company_id}/grade', json={'grade': grade}, headers=self.get_headers_valid(mika))
        assert response.status_code == 200
        assert grade == response.json['grade']

    def test_add_grade_wrong_grade(self, client: FlaskClient):
        '''Zika's company co4 is approved. For that company user mika can add grade.'''
        grade = 100;
        company_id = 3
        response = client.post(f'/api/company/{company_id}/grade', json={'grade': grade}, headers=self.get_headers_valid(mika))
        print(response.json)
        assert response.status_code == 400
        
    def test_get_company_success(self, client: FlaskClient):
        company_id = 3
        response = client.get(f'/api/company/{company_id}', headers=self.get_headers_valid(mika))
        assert response.status_code == 200
        assert len(response.json['grades']) == 1