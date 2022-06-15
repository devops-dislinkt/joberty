import pytest
from flask import Flask
from app import create_app, db
from app import database
from app.services import auth_service
from app.models import User
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError

def seed_db():
    pass


@pytest.fixture
def app() -> Flask:
    '''
    Initializa flask client app which is used for unit testing with app context.
    Returns Flask app.
    '''

    # setup
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()
        yield app

    # teardown
    with app.app_context():
        db.drop_all()


class TestSignup:
    '''Test case for integration tests for signup.'''
    def test_signup_success(self, app: Flask):
        incoming_data = {'username': 'pera', 'password': 'perapera'}
        
        created_user = auth_service.signup(incoming_data['username'], incoming_data['password'])
        assert incoming_data['username'] == created_user.username
        assert check_password_hash(created_user.password, incoming_data['password'])

    @pytest.mark.parametrize('invalid_data', [{'username': 'pera'}, {'password': 'perapera'}, {}])
    def test_signup_with_invalid_data(self, app: Flask, invalid_data):
        '''If invalid data is incoming, it should raise keyerror.'''
        with pytest.raises(KeyError):
            auth_service.signup(invalid_data['username'], invalid_data['password'])

    def test_signup_with_existing_username(self, app: Flask):
        '''Username must be unique, otherwise error will be raised.'''
        incoming_data = {'username': 'pera', 'password': 'perapera'}
        auth_service.signup(incoming_data['username'], incoming_data['password'])

        with pytest.raises(IntegrityError):
            auth_service.signup(incoming_data['username'], incoming_data['password'])
        
        assert len(database.get_all(User)) == 1
