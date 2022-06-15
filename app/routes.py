from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__)
import app.routes_utils

@api.get('/test')
def test():
    return jsonify('hello-world')
