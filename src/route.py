from src.database import User, Approved_User, create_session
from flask import Blueprint, request, redirect, abort
from flask import session as client_session
from google.auth import jwt
from flask_login import login_user, login_required, logout_user
from sqlalchemy import orm

class NotApprovedUserError(Exception):
    pass


route = Blueprint('route', __name__, url_prefix='/', static_folder='./static', static_url_path='')


def check_approved_user(session:orm.Session, user_email:str) -> bool :
    return session.query(Approved_User).filter(Approved_User.approved_email == user_email).first is not None


@route.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return redirect('/back_test/html/templates/home.html')

    elif request.method == 'POST':
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

            if not check_approved_user(session, email) :
                raise NotApprovedUserError('登録されているユーザーではありません')

            user = User(user_name=name, user_id=id, user_email=email)

            client_session['id'] = id
            client_session['name'] = name
            client_session['email'] = email

            if session.query(User).filter(User.user_id == id).first() :
                login_user(user)
                return redirect('/back_test/html/reserve_form.html')

            else:
                session.add(user)
                session.commit()
                session.close()

                login_user(user)

                return redirect('/back_test/html/reserve_form.html')

        except NotApprovedUserError as e:
            print(e)
            session.rollback()
            return redirect('/')

        except Exception as e :
            print(e)
            session.rollback()
            return redirect('/')

        finally :
            session.close()

    else :
        abort(404)


@route.route('/logout')
@login_required
def logout():
    # Session情報の削除
    client_session.pop("id", None)
    client_session.pop("name", None)

    #ログアウト処理
    logout_user()

    return redirect('/back_test/html/templates/home.html')