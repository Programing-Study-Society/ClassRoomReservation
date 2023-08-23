from flask import Blueprint, jsonify
from flask import session as client_session
from flask_login import login_required


user_api = Blueprint(
    'user',
    __name__,
    url_prefix='/user',
    static_folder='./static',
    )


@user_api.route('/get-user')
def get_user():
    if 'id' in client_session.keys() :
        return jsonify({
            'result': True,
            'data':{
                'id':client_session["id"],
                'name': client_session["name"]
            }
            }), 200
    
    else :
        return jsonify({
            'result':False,
            'message':'You are not logged in.'
        }), 400
