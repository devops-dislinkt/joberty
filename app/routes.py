from flask import Blueprint, jsonify, request

from app import database
from app.models import User

api = Blueprint('api', __name__)
import app.routes_utils

@api.get('/test')
def test():
    user = User(username='pera',password='pera', id=1)
    database.add_or_update(user)
    user = database.find_by_username('pera')
    print(user.role.name)
    return jsonify(user.to_dict())