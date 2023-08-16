from flask import Flask,jsonify,session as client_session
from src.API.reserve import reserve
from src.API.classroom import classroom
import os
from flask_login import LoginManager
from src.module.function import generate_token
from src.database import create_session, User
from datetime import timedelta

app = Flask(__name__, static_folder='./static', static_url_path='/')


app.register_blueprint(reserve)
app.register_blueprint(classroom)

app.config['SECRET_KEY'] = generate_token(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'route.default_route'

@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).filter(User.id == user_id).first()

@app.before_request
def before_request():
    # リクエストのたびにセッションの寿命を更新する
    client_session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    client_session.modified = True

@app.errorhandler(404)
def not_found(e):
    print(f'httpステータス:{e.code}, メッセージ:{e.name}, 詳細:{e.description}')
    return app.send_static_file('html/notfound.html')


@app.route('/')
def default_route():
    return app.send_static_file('html/reserve_form.html')