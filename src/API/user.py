from flask import Blueprint,jsonify

user_api = Blueprint('user',__name__, url_prefix='/user')

class UserNotFoundError(Exception):
    pass