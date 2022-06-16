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

co1 = Company({
    'approved': False,
    'name': 'co1',
    'email': 'contact@co1.com',
    'location': 'ulica 1, Neki Grad',
    'website': 'website.co1.com',
    'description': 'best company ever'
})

co2 = Company({
    'approved': False,
    'name': 'co2',
    'email': 'contact@co2.com',
    'location': 'ulica 2, Neki Grad',
    'website': 'website.co2.com',
    'description': 'best company ever'
})
co3 = Company({
    'approved': False,
    'name': 'co3',
    'email': 'contact@co3.com',
    'location': 'ulica 2, Neki Grad',
    'website': 'website.co3.com',
    'description': 'best company ever'
})


def seed_db():

    companies = [co1, co2, co3]
    users = [mika, zika, admin]

    db.session.bulk_save_objects(users)
    db.session.bulk_save_objects(companies)
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

        print(token)
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
    