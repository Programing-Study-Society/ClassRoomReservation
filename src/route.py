from src.database import User, User, Authority, create_session
from flask import Blueprint, request, redirect, abort, current_app
from flask import session as client_session
from google.auth import jwt
from flask_login import login_user, login_required, logout_user
from sqlalchemy import orm
from datetime import datetime

class NotApprovedUserError(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


route = Blueprint('route', __name__, url_prefix='/', static_folder='./static', static_url_path='')


def check_user_user(session:orm.Session, user_email:str) -> bool :
    return session.query(User).filter(User.user_email == user_email).first() != None


@route.errorhandler(404)
def not_found() :
    return redirect('/html/notfound.html')


@route.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return redirect('/html/login_page.html')

    elif request.method == 'POST':
        try:

            session = create_session()

            # Googleから送られてきたPOSTを辞書型に
            data = request.form.to_dict()

            if not ('credential' in data) :
                raise AuthenticationFailed('ログインにエラーが発生しました。')

            # デコードをして読み取れる形に
            persed_request = jwt.decode(data['credential'], verify=False)
            sub_id = persed_request['sub']
            email = persed_request['email']

            if not check_user_user(session, email) :
                raise NotApprovedUserError('登録されているユーザーではありません。')

            # cookieに情報を保存
            client_session['id'] = sub_id

            user = session.query(User).filter(User.user_email == email).first()

            # cookieに情報を保存
            if user is None :
                client_session['user-state'] = None
            else :
                client_session['user-state'] = user.user_state

            user_authority = session.query(Authority).filter(Authority.name == user.user_state).first()

            if user.user_sub == None :
                user.user_sub = sub_id
                session.commit()

            login_user(user)

            if user_authority.is_admin :
                return redirect('/html/management/classroom_management.html')
            else :
                return redirect('/html/reserve_page.html')

        except NotApprovedUserError as e:
            current_app.logger.exception(e)
            session.rollback()
            return redirect('/html/login_failed.html')

        except Exception as e :
            current_app.logger.exception(e)
            session.rollback()
            return redirect('/html/login_failed.html')

        finally :
            session.close()

    else :
        abort(404)


@route.route('/logout')
@login_required
def logout():
    # Session情報の削除
    client_session.pop("id", None)

    #ログアウト処理
    logout_user()

    return redirect('/')