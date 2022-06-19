import pytest
from flask import Flask
from app import create_app, db
from app import database
from app.services import company_service
from app.models import User, Company, UserRole
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, NoResultFound



def seed_db():
    mika = User(
        {
            "username": "mika_test",
            "password": generate_password_hash("mikamika")
        }
    )
    zika = User(
        {
            "username": "zika_test",
            "password": generate_password_hash("zikazika"),
        }
    )
    admin = User(
        {
            "username": "admin_test",
            "password": generate_password_hash("adminadmin"),
        }
    )

    co1 = Company({
        'approved': False,
        'name': 'co1',
        'email': 'contact@co1.com',
        'location': 'ulica 1, Neki Grad',
        'website': 'website.co1.com',
        'description': 'best company ever',
        'user_id': 1
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
        'approved': True,
        'name': 'co3',
        'email': 'contact@co3.com',
        'location': 'ulica 2, Neki Grad',
        'website': 'website.co3.com',
        'description': 'best company ever'
    })

    companies = [co1, co2, co3]
    users = [mika, zika, admin]

    db.session.bulk_save_objects(users)
    db.session.bulk_save_objects(companies)
    db.session.commit()


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


# PARAMS
@pytest.fixture(scope="function")
def mika() -> User:
    return database.find_by_username("mika_test")


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
    
    def test_create_company_request_success(self, app: Flask, mika: User, valid_co_data:dict):
        company = company_service.create_company_registration(user=mika, data=valid_co_data)
        assert valid_co_data['name'] == company.name
        assert valid_co_data['approved'] == company.approved
        assert valid_co_data['email'] == company.email
        assert valid_co_data['location'] == company.location
        assert valid_co_data['website'] == company.website
        assert valid_co_data['description'] == company.description
        assert mika.company.name == company.name

    def test_create_company_request_with_approved_set_to_true(self, app: Flask, mika: User, valid_co_data:dict):
        valid_co_data['approved'] == True
        company = company_service.create_company_registration(user=mika, data=valid_co_data)
        assert mika.company.id == company.id
        assert valid_co_data['name'] == company.name
        assert valid_co_data['approved'] == company.approved
        assert valid_co_data['email'] == company.email
        assert valid_co_data['location'] == company.location
        assert valid_co_data['website'] == company.website
        assert valid_co_data['description'] == company.description


    def test_create_company_request_invalid_data(self, app: Flask, mika: User, invalid_co_data:dict):
        '''all fields are neccessary.'''
        with pytest.raises(IntegrityError):
            company_service.create_company_registration(user=mika, data=invalid_co_data)
        assert True
    

    def test_reject_company_registration(self, app: Flask, mika: User):
        '''when registration is rejected, company obj should be deleted.'''
        num_of_co_before_reject = len(database.get_all(Company))
        res = company_service.resolve_company_registration(username='mika_test', reject=True)
        assert res == True
        assert mika.company == None
        
        num_of_co_after_reject = len(database.get_all(Company))
        assert num_of_co_before_reject == num_of_co_after_reject + 1

    
    def test_accept_company_registration(self, app: Flask, mika: User):
        '''when registration is accepted, company obj should be approved and user should become company owner.'''
        assert mika.role == UserRole.user
        company = company_service.resolve_company_registration(username='mika_test', reject=False)
        assert company != None
        assert mika.company == company
        assert mika.role == UserRole.company_owner

    def test_get_all_companies(self, app: Flask):
        '''Should return all companies'''
        companies = company_service.get_all_companies('all')
        assert len(companies) == 3
    
    def test_get_all_approved_companies(self, app: Flask):
        '''Should return all companies'''
        companies = company_service.get_all_companies('approved')
        assert len(companies) == 1

    
    def test_get_all_not_resolved_companies(self, app: Flask):
        '''Should return all companies'''
        companies = company_service.get_all_companies('not-resolved')
        assert len(companies) == 2