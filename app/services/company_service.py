from dataclasses import field
from typing import Literal
from app.models import User, Company, UserRole
from app import database
from sqlalchemy.exc import NoResultFound
from psycopg2.errors import NotNullViolation

def create_company_registration(user: User, data: dict):
    company = Company(fields=data)
    company.approved = False
    user.company = company
    try: 
        return database.add_or_update(company)
    except NotNullViolation:
        raise NotNullViolation('some fields are missing in request.')

def resolve_company_registration(username: str, reject: bool):
    '''Resolves company registration by the owner. Can reject or accept. 
    If reject, request is deleted, is accept, request is approved.
    Returns True if successfully deleted, returns company object otherwise.'''

    user = database.find_by_username(username)
    print(user, user.to_dict())

    if not user:
        raise NoResultFound(f"No user with given username: {user['username']}")

    if reject:
        database.delete_instance(Company, user.company.id)
        return True

    else:
        user.company.approved = True
        user.role = UserRole.company_owner
        user = database.add_or_update(user)
        return user.company


def get_all_companies(type: Literal['approved', 'all', 'not-resolved']):
    companies = database.get_all(Company)

    match type:
        case 'all':
            return companies
        case 'approved':
            return [co for co in companies if co.approved == True]
        case 'not-resolved':
            return [co for co in companies if co.approved == False]
    

class NotApproved(Exception):
    '''When company registration is not approved by admin.'''
    def __init__(self, message):            
        super().__init__(message)
