from src.database import User, User, Authority, create_session
from flask import Blueprint, request, redirect, abort, current_app
from flask import session as client_session
from google.auth import jwt
from flask_login import login_user, login_required, logout_user
from sqlalchemy import orm
from datetime import datetime
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('./.env')

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", None)

class NotApprovedUserError(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


route = Blueprint('route', __name__, url_prefix='/', static_folder='./static', static_url_path='')

# OAuth2クライアント設定
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def check_user_user(session:orm.Session, user_email:str) -> bool :
    return session.query(User).filter(User.user_email == user_email).first() != None

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@route.errorhandler(404)
def not_found(e) :
    return redirect('/html/notfound.html')


@route.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return redirect('/html/login_page.html')

@route.get('/login')
def login():
    # 認証用のエンドポイントを取得する
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # ユーザプロファイルを取得するログイン要求
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@route.route('/login/callback')
def after_login():
    try:
        session = create_session()
        # Googleから返却された認証コードを取得する
        code = request.args.get("code")

        #トークンを取得するためのURLを取得する
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # トークンを取得するための情報を生成し、送信する
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=GOOGLE_REDIRECT_URI,
            code=code,
            approval_prompt='force',
            access_type="offline",
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # トークンをparse
        client.parse_request_body_response(json.dumps(token_response.json()))

        # トークンができたので、GoogleからURLを見つけてヒットした、
        # Googleプロフィール画像やメールなどのユーザーのプロフィール情報を取得
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        # メールが検証されていれば、名前、email、プロフィール画像を取得します
        if not userinfo_response.json().get("email_verified"):
            raise Exception("User email not available or not verified by Google.")
        
        
        sub_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]

        # Googleから送られてきたPOSTを辞書型に
        # data = request.form.to_dict()

        # if not ('credential' in data) :
        #     raise AuthenticationFailed('ログインにエラーが発生しました。')

        # デコードをして読み取れる形に
        # persed_request = jwt.decode(data['credential'], verify=False)
        # sub_id = persed_request['sub']
        # email = persed_request['email']

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


@route.route('/logout')
@login_required
def logout():
    # Session情報の削除
    client_session.pop("id", None)

    #ログアウト処理
    logout_user()

    return redirect('/')