from flask import Blueprint, jsonify, request
from flask import session as client_session
from flask_login import login_required
from src.database import create_session, Approved_User, User


class PostValueError(Exception) :
    pass


class LuckOfAdministrativeUserError(Exception):
    pass


user_api = Blueprint(
    'user',
    __name__,
    url_prefix='/user',
    static_folder='./static',
    )

@user_api.route('/current-user', methods=['GET'])
def get_current_user():
    if 'id' in client_session.keys() :
        return jsonify({
            'result': True,
            'data':{
                'id':client_session["id"],
                'name': client_session["name"],
                'email':client_session['email']
            }
            }), 200

    else :
        return jsonify({
            'result':False,
            'message':'ログインしていません。'
        }), 400


@user_api.route('/get', methods=['GET'])
@login_required
def get_user():
    try :
        session = create_session()
        approved_users = session.query(Approved_User).all()

    except Exception as e :
        print(e)
        return jsonify({
            'result':False,
            'message':'サービスにエラーが発生しました。'
        }), 500

    else :
        return jsonify({
            'result': True,
            'data':[approved_user.to_dict() for approved_user in approved_users]
        }), 200
    
    finally :
        session.close()


@user_api.route('/add', methods=['POST'])
@login_required
def add_user():
    try:
        session = create_session()

        user = request.json
        print(user)

        if not ('email' in user or 'user-name' in user or 'is-admin' in user) :
            raise PostValueError('必要な情報が不足しています。')

        if len(user['email']) >= 64 or len(user['user-name']) >= 128:
            raise PostValueError('文字の長さが長すぎます。')

        session.add(Approved_User(approved_email=user['email'], approved_user_name=user['user-name'], is_admin=user['is-admin']))

        session.commit()

        return jsonify({
            'result':True
        }), 200

    except PostValueError as e :
        print(e)
        return jsonify({
            'result':False,
            'message':e.args[0]
        }), 400

    except Exception as e :
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            'message':'サービスにエラーが発生しました。'
        }), 500

    finally :
        session.close()


@user_api.route('/delete', methods=['POST'])
@login_required
def user_delete():
    try:
        session = create_session()

        data = request.json

        print(data)

        if (not 'email' in data):
            raise PostValueError('必要な情報が不足しています。')

        if len(data['email']) >= 64:
            raise PostValueError('文字の長さが長すぎます。')

        approved_user = session.query(Approved_User).filter(Approved_User.approved_email == data['email']).first()

        if approved_user == None:
            raise PostValueError('存在しないユーザーです。')
        
        if approved_user.is_admin and session.query(Approved_User).filter(Approved_User.is_admin == True).count() <= 1:
            raise LuckOfAdministrativeUserError('管理者が不足しています。')

        user = session.query(User).filter(User.user_email == data['email']).first()

        if user != None:
            session.delete(user)

        session.delete(approved_user)

        session.commit()

        return jsonify({
            'result':True
        }), 200

    except PostValueError as e :
        print(e)
        return jsonify({
            'result':False,
            'message':e.args[0]
        }), 400
    
    except LuckOfAdministrativeUserError as e :
        print(e)
        return jsonify({
            'result':False,
            'message':e.args[0]
        }), 400

    except Exception as e :
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            'message':'サービスにエラーが発生しました。'
        }), 500

    finally :
        session.close()