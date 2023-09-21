from src.database import User, Approved_User, Authority, create_session
from flask import Blueprint, request, redirect, abort
from flask import session as client_session
from google.auth import jwt
from flask_login import login_user, login_required, logout_user
from sqlalchemy import orm

class NotApprovedUserError(Exception):
    pass


route = Blueprint('route', __name__, url_prefix='/', static_folder='./static', static_url_path='')


def check_approved_user(session:orm.Session, user_email:str) -> bool :
    return session.query(Approved_User).filter(Approved_User.approved_email == user_email).first() != None


@route.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return redirect('/html/login_page.html')

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

            client_session['id'] = id
            client_session['name'] = name
            client_session['email'] = email

            approved_user = session.query(Approved_User).filter(Approved_User.approved_email == email).first()

            if approved_user is None :
                client_session['user-state'] = None
            else :
                client_session['user-state'] = approved_user.user_state

            # must change
            user = User(user_name=name, user_id=id, user_email=email)
            user_authority = session.query(Authority).filter(Authority.name == approved_user.user_state).first()

            if session.query(User).filter(User.user_id == id).first() != None :
                login_user(user)

                if user_authority.is_admin :
                    return redirect('/html/management/classroom_management.html')
                else :
                    return redirect('/html/reserve_page.html')

            else:
                session.add(user)
                session.commit()

                login_user(user)

                if user_authority.is_admin :
                    return redirect('/html/management/classroom_management.html')
                else :
                    return redirect('/html/reserve_page.html')

        except NotApprovedUserError as e:
            print(e)
            session.rollback()
            return redirect('/html/login_failed.html')

        except Exception as e :
            print(e)
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
    client_session.pop("name", None)
    client_session.pop("email", None)
    client_session.pop("user-state", None)

    #ログアウト処理
    logout_user()

    return redirect('/')