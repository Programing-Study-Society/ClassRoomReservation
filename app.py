from flask import Flask,jsonify,session as client_session
from src.API.reserve import reserve
from src.API.classroom import classroom
from src.API.user import user_api
import os
from flask_login import LoginManager
from src.module.function import generate_token
from src.database import create_session, create_scoped_session, User, Reservation
from datetime import timedelta, datetime
import threading
import schedule
from time import sleep


### Ctrl + C を押したときに正常終了する ###

import signal
import sys

def signal_handler(signum, frame):
    print('end program')
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

### ここまで ###


app = Flask(__name__, static_folder='./static', static_url_path='/')


app.register_blueprint(reserve)
app.register_blueprint(classroom)
app.register_blueprint(user_api)


app.config['SECRET_KEY'] = generate_token(32)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'route.default_route'


@login_manager.user_loader
def load_user(user_id):

    session = create_session()
    loaded_user = session.query(User).filter(User.user_id == user_id).first()
    session.close()

    return loaded_user


@app.before_request
def before_request():
    # リクエストのたびにセッションの寿命を更新する
    client_session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    client_session.modified = True


@login_manager.unauthorized_handler
def unauth_handler():
    return jsonify({
        'result': False,
        'message': 'ログインしていません' 
    }), 400


@app.route('/')
def default_route():
    return app.send_static_file('html/reserve_form.html')


## ここからはテスト用のエンドポイント
@app.route('/home')
def login_test():
    return app.send_static_file('back_test/html/templates/home.html')


@app.route('/faild')
def login_faild():
    return app.send_static_file('back_test/html/templates/loginFaild.html')


print(f' * http://localhost:{os.environ.get("FLASK_RUN_PORT")}')


### 定期実行プログラム ###

def check_past_reservations():

    def delete_past_reservations():
        try:
            session = create_session()

            reservations_delete = session.query(Reservation).filter(Reservation.end_time <= datetime.now()).all()
            
            if reservations_delete is None:
                return
            
            for reservation in reservations_delete:
                print(f'{reservation.reservation_id} was deleted!')
                session.delete(reservation)

            session.commit()

        except Exception as e:
            print(e)
            session.rollback()
            return
        
        finally :
            session.close()

    schedule.every().day.at('02:30').do(delete_past_reservations)
    while True:
        schedule.run_pending()
        sleep(1)


thread1 = threading.Thread(target=check_past_reservations, daemon=True)

thread1.start()