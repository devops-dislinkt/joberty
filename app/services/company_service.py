from dataclasses import field
from typing import Literal
from app.models import User, Company, UserRole, Comment, Grade
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
    

def create_comment(user: User, company_id: int, description: str):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
    if not company.approved:
        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')
    
    comment = Comment({'company_id': company_id, 'description': description, 'user_id': user.id})
    return database.add_or_update(comment)


def add_grade(user: User, company_id: int, grade: int):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
    if not company.approved:
        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')

    if grade < 1 or grade > 5:
        raise Exception('grade must be in range [1,5].')

    grade = Grade({'company_id': company_id, 'grade': grade, 'user_id': user.id})
    return database.add_or_update(grade)


class NotApproved(Exception):
    '''When company registration is not approved by admin.'''
    def __init__(self, message):            
        super().__init__(message)
