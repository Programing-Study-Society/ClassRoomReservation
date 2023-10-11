from flask import Blueprint, jsonify, request, abort
from flask import session as client_session
from flask_login import login_required
from src.database import create_session, User, Authority, Reservation
from src.module.function import get_user_state, generate_token


class PostValueError(Exception) :
    pass


class LuckOfAdministrativeUserError(Exception):
    pass


class AuthorityError(Exception) :
    pass


class ManyAttemptsError(Exception):
    pass


MAX_ATTEMPTS = 2000


user_api = Blueprint(
    'user',
    __name__,
    url_prefix='/user',
    static_folder='./static',
    )


@user_api.errorhandler(404)
def notfound():
    return jsonify({'result':False, 'message':'Not found'}), 404


@user_api.route('/current-user', methods=['GET'])
def get_current_user():
    if 'id' in client_session.keys() :
        return jsonify({
            'result': True
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

        if not get_user_state(client_session).is_admin :
            abort(404)

        user_users = session.query(User).all()

    except Exception as e :
        print(e)
        return jsonify({
            'result':False,
            'message':'サービスにエラーが発生しました。'
        }), 500

    else :
        return jsonify({
            'result': True,
            'data':[user_user.to_dict() for user_user in user_users]
        }), 200
    
    finally :
        session.close()


@user_api.route('/add', methods=['POST'])
@login_required
def add_user():
    try:
        session = create_session()

        if not get_user_state(client_session).is_edit_reserve :
            abort(404)

        user = request.json

        if not ('email' in user or 'user-name' in user or 'user-state' in user) :
            raise PostValueError('必要な情報が不足しています。')
        
        if user['user-name'] == None or user['user-name'] == '' or user['email'] == None or user['email'] == '' or user['user-state'] == None :
            raise PostValueError('必要な情報が不足しています。')

        if len(user['email']) >= 64 or len(user['user-name']) >= 128:
            raise PostValueError('文字の長さが長すぎます。')

        if session.query(User).filter(User.user_email == user['email']).first() != None :
            raise PostValueError('同じメールが登録されています。')
        
        cnt = 0
        while True:
            cnt += 1
            user_id = generate_token(32)

            if session.query(User).filter(User.user_id == user_id).first() is None:
                break

            elif cnt >= MAX_ATTEMPTS:
                raise ManyAttemptsError('もう一度お試しください。')

        user_user = User(
                user_id=user_id, 
                user_email=user['email'], 
                user_name=user['user-name'], 
                user_state=user['user-state']
            )
        
        session.add(user_user)
        
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

        if not get_user_state(client_session).is_edit_reserve :
            abort(404)

        data = request.json

        if (not 'email' in data):
            raise PostValueError('必要な情報が不足しています。')

        if len(data['email']) >= 64:
            raise PostValueError('文字の長さが長すぎます。')

        delete_user = session.query(User).filter(User.user_email == data['email']).first()

        if delete_user == None:
            raise PostValueError('存在しないユーザーです。')
        
        client_authority = session.query(Authority).filter(Authority.name == client_session['user-state']).first()
        delete_user_authority = session.query(Authority).filter(Authority.name == delete_user.user_state).first()

        if not client_authority.is_edit_user and delete_user_authority.is_edit_user :
            raise AuthorityError('このユーザーは削除出来ません。')
        
        if delete_user.user_state and session.query(User).filter(User.user_state == 'administrator').count() <= 2:
            raise LuckOfAdministrativeUserError('管理者が不足しています。')
        
        delete_user_reserves = session.query(Reservation).filter(Reservation.reserved_user_id == delete_user.get_id()).all()

        for reserve in delete_user_reserves :
            session.delete(reserve)

        session.delete(delete_user)

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
    
    except AuthorityError as e :
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


@user_api.route('/get-authority')
@login_required
def get_authority():
    try :
        session = create_session()

        authorities = None
        
        if client_session['user-state'] == 'administrator' :
            authorities = session.query(Authority).all()

        if client_session['user-state'] == 'moderator' :
            authorities = session.query(Authority).filter(Authority.name == 'user').all()

        return jsonify({
            'result':True,
            'data':[authority.to_dict() for authority in authorities]
        })

    except Exception as e :
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            'message':'サービスにエラーが発生しました。'
        }), 500
    
    finally :
        session.close()