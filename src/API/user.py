from src.database import User, create_session
from flask import Blueprint, request, jsonify, redirect
from flask import session as client_session
from google.auth import jwt
from flask_login import login_user, login_required, logout_user, current_user


user_api = Blueprint(
    'user',
    __name__, 
    url_prefix='/user', 
    static_folder='./static',
    static_url_path='/static'
    )


class UserNotFoundError(Exception):
    pass


class MaxValueError(Exception):
    pass


@user_api.route('/', methods=["POST"])
def create_user():
    try:
        session = create_session()

        # Googleから送られてきたPOSTを辞書型に
        data = request.form.to_dict()
        # デコードをして読み取れる形に
        persed_request = jwt.decode(data['credential'], verify=False)
        id = persed_request['sub']
        name = persed_request['name']
        email = persed_request['email']
        print(f'name : {name}, id : {id}, email : {email}')

        user = User(user_name=name, user_id=id,user_email=email)

        client_session['id'] = id
        client_session['name'] = name
        client_session['email'] = email

        if session.query(User).filter(User.user_id == id).first() :
            login_user(user)
            return redirect('/back_test/html/templates/success.html')
        
        else:
            session.add(user)
            session.commit()
            session.close()

            login_user(user)

            return redirect('/back_test/html/templates/success.html')
    
    except Exception as e :
        print(e)
        session.rollback()
        return jsonify({'result':False, 'message':'Internal Server Error'}), 500
    
    finally :
        session.close()


@user_api.route('/get-user')
@login_required
def get_user():
    print(f'id : {client_session["id"]}')
    return jsonify({
        'result': True,
        'data':{
            'id':client_session["id"],
            'name': client_session["name"]
        }
        }), 200


@user_api.route('/logout')
@login_required
def logout():
    # Session情報の削除
    client_session.pop("id", None)
    client_session.pop("name", None)

    #ログアウト処理
    logout_user()

    return redirect('/back_test/html/templates/home.html')
