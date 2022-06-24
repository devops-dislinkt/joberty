from dataclasses import field
from typing import Literal
from models import Job, Salary, User, Company, UserRole, Comment, Interview

import database
from sqlalchemy.exc import NoResultFound
from psycopg2.errors import NotNullViolation


def create_company_registration(user: User, data: dict):
    company = Company(fields=data)
    company.approved = False
    user.company = company
    print(f"data = {data} \n user = {user.to_dict()}")
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


def get_one_company(company_id: int):
    company = database.find_by_id(Company, id=company_id)
    print(f"get one comapny = {company}")
    return company


def get_all_companies(type: Literal['approved', 'all', 'not-resolved']):
    companies = database.get_all(Company)

    match type:
        case 'all':
            return companies
        case 'approved':
            return [co for co in companies if co.approved == True]
        case 'not-resolved':
            return [co for co in companies if co.approved == False]


def get_all_comments():
    comments = database.get_all(Comment)
    return comments


def get_all_interview():
    interviews = database.get_all(Interview)
    return interviews


def get_all_salaries():
    salaries = database.get_all(Salary)
    return salaries

def get_all_jobs():
    jobs = database.get_all(Job)
    return jobs


def get_company_comments(id: int):
    comments = database.find_by_company_id(id)
    return comments


def create_comment(user: User, company_id: int, data):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
#    if not company.approved:
#        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')

    comment = Comment({'company_id': company_id,
                       'positive': data.get('positive'),
                       'negative': data.get('negative'),
                       'rating': data.get('rating'),
                       'user_id': user.id})
    try:
        return database.add_or_update(comment)
    except NotNullViolation:
        raise NotNullViolation('some fields are missing in request.')


def create_interview_comment(user: User, company_id: int, data):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
#    if not company.approved:
#        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')

    interview = Interview({'company_id': company_id,
                           'technical': data.get('technical'),
                           'hr': data.get('hr'),
                           'rating': data.get('rating'),
                           'user_id': user.id})
    try:
        return database.add_or_update(interview)
    except NotNullViolation:
        raise NotNullViolation('some fields are missing in request.')


def create_salary(user: User, company_id: int, data):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
#    if not company.approved:
#        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')

    salary = Salary({'company_id': company_id,
                     'position': data.get('position'),
                     'salary': data.get('salary'),
                     'user_id': user.id})
    try:
        return database.add_or_update(salary)
    except NotNullViolation:
        raise NotNullViolation('some fields are missing in request.')

def create_job(user: User, company_id: int, data):
    company = database.find_by_id(Company, id=company_id)
    if not company:
        raise NoResultFound(f'no company with id: {company_id}')
#    if not company.approved:
#        raise NotApproved('company registration not approved by admin')
    if user.role != UserRole.user:
        raise Exception('must login as user')

    salary = Job({'company_id': company_id,
                     'title': data.get('title'),
                     'description': data.get('description'),
                     'user_id': user.id})
    try:
        return database.add_or_update(salary)
    except NotNullViolation:
        raise NotNullViolation('some fields are missing in request.')


class NotApproved(Exception):
    '''When company registration is not approved by admin.'''

    def __init__(self, message):
        super().__init__(message)
