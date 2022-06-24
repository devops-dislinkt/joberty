from flask import Blueprint, jsonify, request

from app import database
from app.models import User, Company
from app.services import auth_service
from app.services import company_service
from app.services.company_service import NotApproved
from app.services.auth_service import AuthException
from sqlalchemy.exc import IntegrityError


api = Blueprint("api", __name__)
from app.routes_utils import check_token, required_roles, get_logged_in_user


@api.get("/server/test")
def test():
    user = User(username="pera", password="pera", id=1)
    database.add_or_update(user)
    user = database.find_by_username("pera")
    print(user.role.name)
    return jsonify(user.to_dict())


@api.post("/server/signup")
def signup():
    """Registers new user on the system"""
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return "did not receive username or password", 400

    try:
        user = auth_service.signup(data.get("username"), data.get("password"))
        return jsonify(user.to_dict())
    except IntegrityError:
        return "username not unique", 400


@api.post("/server/login")
def login():
    """login on system"""
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return "did not receive username or password", 400

    username = data["username"]
    password = data["password"]

    try:
        token = auth_service.login(username, password)
        return jsonify(token)
    except AuthException as e:
        return jsonify(str(e)), 400


@api.post("/server/company/resolve-registration")
@check_token
@required_roles(["admin"])
def resolve_company_registration():
    """Only admin role can resolve registration request."""

    data = request.json
    if not data or data.get("reject") == None or data.get("username") == None:
        return "did not receive reject status or username.", 400

    company = company_service.resolve_company_registration(
        username=data.get("username"), reject=data.get("reject")
    )
    if company == True:
        return "successfully deleted.", 200

    return jsonify(company.to_dict())


@api.post("/server/company")
@check_token
def create_company_registration():
    data = request.json
    if not data:
        return "did not receive data.", 400

    user = get_logged_in_user(request)
    try:
        company = company_service.create_company_registration(user, data)
        return jsonify(company.to_dict())

    except IntegrityError as e:
        return jsonify(str(e)), 400


@api.get("/server/company/<string:type>")
@check_token
@required_roles(["admin"])
def get_companies(type: str):
    """Returns all/approved/not-resolved companies. Type param can be: all, appproved or not-resolved."""
    if not type:
        return "did not receive data.", 400

    companies = company_service.get_all_companies(type)
    return jsonify([company.to_dict() for company in companies])


@api.get("/server/company/<int:company_id>")
@check_token
def get_company(company_id: int):
    """Get one company."""
    company = database.find_by_id(Company, company_id)
    return jsonify(company.to_dict())


@api.post("/server/company/<int:company_id>/comment")
@check_token
@required_roles(["user"])
def create_comment(company_id: int):
    """
    Logged in user (ony as user role) creates comment for specified (only approved) company.
    Returns created comment.
    """
    data = request.json
    if not data or not data.get("description"):
        return "did not receive data.", 400

    user = get_logged_in_user(request)
    try:
        comment = company_service.create_comment(
            user, company_id, data.get("description")
        )
        return jsonify(comment.to_dict())
    except NotApproved as e:
        return jsonify(str(e)), 400
    except Exception as e:
        return jsonify(str(e)), 403


@api.post("/server/company/<int:company_id>/grade")
@check_token
@required_roles(["user"])
def add_grade(company_id: int):
    """
    Logged in user (ony as user role) adds grade for specified (only approved) company.
    Returns created grade.
    """
    data = request.json
    if not data or not data.get("grade"):
        return "did not receive data.", 400

    user = get_logged_in_user(request)
    try:
        grade = company_service.add_grade(user, company_id, data.get("grade"))
        return jsonify(grade.to_dict())
    except Exception as e:
        return jsonify(str(e)), 400
