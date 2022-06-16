from dataclasses import field
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

def resolve_company_registration(user: User, reject: bool):
    '''Resolves company registration by the owner. Can reject or accept. If reject, request is deleted, is accept, request is approved.'''

    if reject:
        database.delete_instance(Company, user.company.id)
        return user.company

    else:
        user.company.approved = True
        user.role = UserRole.company_owner
        user = database.add_or_update(user)
        return user.company


class NotApproved(Exception):
    '''When company registration is not approved by admin.'''
    def __init__(self, message):            
        super().__init__(message)
