import pytest
from flask.testing import FlaskClient
from app import create_app, db
from app import database
from app.services import auth_service
from app.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

def seed_db():
    pera = User(
        {
            "username": "pera_test",
            "password": generate_password_hash("perapera"),

        }
    )
    mika = User(
        {
            "username": "mika_test",
            "password": generate_password_hash("mikamika")
        }
    )
    zika = User(
        {
            "username": "zika_test",
            "password": generate_password_hash("zikazika")
        }
    )
    kiki = User(
        {
            "username": "kiki_test",
            "password": generate_password_hash("kikikiki")
        }
    )

    users = [pera, mika, zika, kiki]
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



class TestSignup:
    '''Test case for integration tests for signup.'''
    def test_signup_success(self, client: FlaskClient):
        incoming_data = {'username': 'pera', 'password': 'perapera'}
        response = client.post('/api/signup', json=incoming_data)
        assert response.status_code == 200
        assert incoming_data['username'] == response.json['username']


    def test_signup_with_invalid_data(self, client: FlaskClient):
        '''If invalid data is incoming, it should raise keyerror.'''
        invalid_data = {}
        response = client.post('/api/signup', json=invalid_data)
        assert response.status_code == 400


    def test_signup_with_existing_username(self, client: FlaskClient):
        '''Username must be unique, otherwise error will be raised.'''
        incoming_data = {'username': 'pera', 'password': 'perapera'}
        response = client.post('/api/signup', json=incoming_data)
        assert response.status_code == 400


class TestClassLogin:
    '''Test case for when user logs in.'''

    def test_login_success(self, client: FlaskClient):
        response = client.post('/api/login', json = {'username': 'pera_test', 'password': 'perapera'})
        assert response.status_code == 200

    def test_login_with_wrong_username(self, client: FlaskClient):
        incoming_data = {'username': 'trash', 'password': 'perapera'}
        response = client.post('/api/login', json = {'username': incoming_data['username'], 'password': incoming_data['password']})
        assert response.status_code == 404

    def test_login_with_wrong_password(self, client: FlaskClient):
        incoming_data = {'username': 'pera_test', 'password': 'trash'}
        response = client.post('/api/login', json = {'username': incoming_data['username'], 'password': incoming_data['password']})        
        assert response.status_code == 400

    def test_login_without_password(self, client: FlaskClient):
        incoming_data = {'username': 'pera_test'}
        response = client.post('/api/login', json = {'username': incoming_data['username']})        
        assert response.status_code == 400
