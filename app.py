from flask import Flask, redirect, session as client_session, request, jsonify
from src.route import route
from src.API.reserve import reserve
from src.API.classroom import classroom
from src.API.user import user_api
import os
from flask_login import LoginManager
from src.module.function import generate_token
from src.database import create_session, User, Reservation, ReservableClassroom
from datetime import timedelta, datetime
import threading
import schedule
from time import sleep
from dotenv import load_dotenv
import logging


### Ctrl + C を押したときに正常終了する ###

import signal
import sys

def signal_handler(signum, frame):
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

### ここまで ###

# 環境変数ファイルの読み込み
load_dotenv('./.env')


app = Flask(__name__, static_folder=os.environ.get('STATIC_FILE_PATH'), static_url_path='/')

app.register_blueprint(route)
app.register_blueprint(reserve)
app.register_blueprint(classroom)
app.register_blueprint(user_api)

app.config['SECRET_KEY'] = generate_token(32)

### ログファイルの出力設定 ###

log_level = logging.ERROR
app.logger.setLevel(log_level)
file_handler = logging.FileHandler(
        filename=os.environ.get('LOG_FILE_PATH') + '/error.log',
        encoding='utf-8'
    )
file_handler.setLevel(log_level)
formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formater)
app.logger.addHandler(file_handler)

###

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
    app.permanent_session_lifetime = timedelta(hours=2)
    client_session.modified = True
    

@login_manager.unauthorized_handler
def unauth_handler():
    if request.method == 'GET' :
        return redirect('/html/login_failed.html')
    if request.method == 'POST' :
        return jsonify({'result':False, 'message':'Session error occurred.'}), 400
    
    return redirect('/html/login_failed.html')


@app.errorhandler(404)
def not_found(e) :
    return redirect('/html/notfound.html')




### 定期実行プログラム ###

def check_past_reservations():
    # 過ぎた予約の削除
    def delete_past_reservations():
        try:
            session = create_session()

            reservations_delete = session.query(Reservation).filter(Reservation.end_time <= datetime.now()).all()
            
            if reservations_delete is None:
                return
            
            for reservation in reservations_delete:
                session.delete(reservation)

            session.commit()

        except Exception as e:
            session.rollback()
            return
        
        finally :
            session.close()

    # 利用可能時間が過ぎた教室の削除
    def delete_past_classrooms():
        try:
            session = create_session()

            classroom_delete = session.query(ReservableClassroom).filter(ReservableClassroom.reservable_end_time <= datetime.now()).all()
            
            if classroom_delete is None:
                return
            
            for classroom in classroom_delete:
                session.delete(classroom)

            session.commit()

        except Exception as e:
            app.logger.exception(e)
            session.rollback()
            return
        
        finally :
            session.close()


    schedule.every().day.at('00:00').do(delete_past_reservations)
    schedule.every().day.at('00:00').do(delete_past_classrooms)
    while True:
        schedule.run_pending()
        sleep(1)


thread1 = threading.Thread(target=check_past_reservations, daemon=True)

thread1.start()

if __name__ == '__main__' :

    host = os.environ.get('FLASK_RUN_HOST')
    port = os.environ.get('FLASK_RUN_PORT')
    is_debug = os.environ.get('FLASK_DEBUG')

    if is_debug :
        print(f' * http://localhost:{os.environ.get("FLASK_RUN_PORT")}')

    app.run(host=host, port=port, debug=is_debug)