from flask import Blueprint, request, jsonify, abort, session as client_session
from src.database import Reservation, ReservableClassroom, User, Authority, create_session
from sqlalchemy import and_, or_, orm
from datetime import datetime, timedelta
import re
from src.module.function import generate_token, get_user_state
from flask_login import login_required
import smtplib
from email import policy
from email.mime.text import MIMEText
from email.utils import formatdate
import os
import threading


class ReserveValueError(Exception):
    pass


class PostValueError(Exception):
    pass


class ManyAttemptsError(Exception):
    pass


class NotLoginError(Exception):
    pass


class NonExistentUser(Exception) :
    pass


reserve = Blueprint('reserve', __name__, url_prefix='/reserve')


@reserve.errorhandler(404)
def notfound():
    return jsonify({'result':False, 'message':'Not found'}), 404


MAX_ATTEMPTS = 2000


def send_reserve_delete_mail(reservation) :
    mail = smtplib.SMTP(
        host = os.environ.get('MAIL_SERVER'),
        port=os.environ.get('MAIL_PORT')
        )
    
    mail.starttls()

    mail.login(
        user = os.environ.get('MAIL_USERNAME'),
        password = os.environ.get('MAIL_PASSWORD')
    )
                
    formated_start_date = reservation['start-date'].replace('-', '/')
    formated_end_date = reservation['end-date'].replace('-', '/')
    
    send_txt = f"{reservation['user-name']} 様\n\n当サイトにてご予約いただいた\n\n{reservation['classroom-name']}教室　{formated_start_date} ～ {formated_end_date}\n\nの予約が取り消されました。\n\n当日は教室を貸出できないためご了承下さい。\n\n何かご不明な点がございましたら学務課までご連絡お願いいたします。"
    
    message = MIMEText(send_txt, "plain", "utf-8", policy=policy.default)
    message['Subject'] = '【お知らせ】教室のご予約取り消しについて'
    message['From'] = os.environ.get('MAIL_SENDER')
    message['To'] = reservation['user-email']
    message['Date'] = formatdate()

    mail.send_message(message)

    mail.close()
    

# 予約時間が予約可能かチェックします
def check_reservable(session:orm.Session, classroom_id:str, start_time:datetime, end_time:datetime, user:User) -> str | None:
    if session.query(ReservableClassroom).filter(
        ReservableClassroom.classroom_id == classroom_id,
        and_(
            ReservableClassroom.reservable_start_time <= start_time,
            ReservableClassroom.reservable_end_time >= end_time
        )
    ).first() is None :
        return 'その時間では予約できません。'
    
    if session.query(Reservation).filter(
        Reservation.classroom_id == classroom_id,
        or_(
            and_(Reservation.start_time >= start_time, Reservation.start_time < end_time),
            and_(Reservation.end_time > start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time <= start_time, Reservation.end_time >= end_time),
        )
    ).first() != None :
        return '既に予約が入っています。'
    
    start_date = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)
    
    if session.query(Reservation).filter(
        Reservation.reserved_user_id == user.get_id(),
        Reservation.start_time >= start_date,
        Reservation.start_time <= start_date + timedelta(days=1)
    ).count() >= 1 :
        return '既に予約されている日付には予約出来ません。'
    
    return None


@reserve.errorhandler(404)
def notfound():
    return jsonify({'result':False, 'message':'Not found'}), 404


# 予約するエンドポイントです
@reserve.route('/add', methods=['POST'])
@login_required
def register_reserve():
    try:
        session = create_session()

        reserved_user = session.query(User).filter(User.user_sub == client_session['id']).first()

        if reserved_user == None :
            abort(404)

        post_data = request.json

        if not ('start-date' in post_data and 'end-date' in post_data and 'classroom-id' in post_data) :
            raise PostValueError('無効なデータ形式です。')

        if post_data['start-date'] is None or post_data['end-date'] is None or post_data['classroom-id'] is None or post_data['start-date'] == '' or post_data['end-date'] == '' or post_data['classroom-id'] == '' :
            raise PostValueError('データが不足しています。')
            
        if re.match(r'\d+-\d+-\d+', post_data['start-date']) is None or  re.match(r'\d+-\d+-\d+', post_data['end-date']) is None:
            raise PostValueError('日時が間違っています。')

        start_time = datetime.strptime(post_data['start-date'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(post_data['end-date'], '%Y-%m-%d %H:%M:%S')

        if start_time < datetime.now() or end_time < datetime.now() or start_time == end_time:
            raise PostValueError('無効な日時です。')

        if start_time.date() != end_time.date():
            raise PostValueError('日を跨いだ予約はできません。')
        
        classroom = session.query(ReservableClassroom).filter(
            ReservableClassroom.classroom_id == post_data['classroom-id']
        ).first()

        if classroom is None :
            raise ReserveValueError('この教室は予約できません。')

        reserve_state = check_reservable(session, classroom.classroom_id, start_time, end_time, reserved_user)

        if reserve_state != None :
            raise ReserveValueError(reserve_state)

        cnt = 0
        while True:
            cnt += 1
            reservation_id = generate_token(16)

            if session.query(Reservation).filter(Reservation.reservation_id == reservation_id).first() is None:
                break

            elif cnt >= MAX_ATTEMPTS:
                raise ManyAttemptsError('もう一度お試しください。')

        reserve = Reservation(
            reservation_id=reservation_id,
            classroom_id=classroom.classroom_id,
            reserved_user_id=reserved_user.user_id,
            start_time=start_time,
            end_time=end_time,
        )

        session.add(reserve)
        session.commit()

        is_required_user_id = get_user_state(client_session).is_edit_reserve

        return jsonify({'result': True, 'data': reserve.to_dict(is_required_user_id=is_required_user_id)}), 200
    
    except PostValueError as e :
        print(e)
        session.rollback()
        return jsonify({'result': False, 'message': e.args[0]}), 400

    except ReserveValueError as e:
        print(e)
        session.rollback()
        return jsonify({'result': False, 'message': e.args[0]}), 400
    
    except ManyAttemptsError as e :
        print(e)
        session.rollback()
        return jsonify({'result':False, 'message': e.args[0]}), 500

    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({'result': False, 'message': 'Internal Server Error !'}), 500
    
    finally :
        session.close()


# 予約情報を取得するエンドポイントです
@reserve.route('/get/<string:mode>', methods=['POST', 'GET'])
def reserve_get(mode):
    match mode:
        # 全て取得
        case 'full':
            try :
                session = create_session()

                if request.method != 'GET':
                    abort(404)

                is_required_user_id = False

                if 'user-state' in client_session :
                    is_required_user_id = get_user_state(client_session).is_edit_reserve

                reserve_values = session.query(Reservation).join(
                        ReservableClassroom, 
                        ReservableClassroom.classroom_id == Reservation.classroom_id
                    ).order_by(Reservation.start_time).all()

                return jsonify({
                    'result': True, 
                    'data': [reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values]
                    }), 200

            except Exception as e:
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': 'Internal Server Error'}), 500
            
            finally :
                session.close()

        # 日付での取得
        case 'date':
            try :
                session = create_session()

                if request.method != 'POST':
                    abort(404)

                post_datas = request.json

                if not ('start-date' in post_datas and 'end-date' in post_datas) :
                    PostValueError('無効なデータ形式です。')

                start_time = post_datas['start-date']
                end_time = post_datas['end-date']

                date_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'

                if re.match(date_pattern, start_time) is None or re.match(date_pattern, end_time) is None :
                    raise PostValueError('日付のフォーマットが間違えています。(yyyy-mm-dd HH:MM:SS)')

                start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

                reserve_values = session.query(Reservation).filter(
                    and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time)
                ).all()

                is_required_user_id = False

                if 'user-state' in client_session :
                    is_required_user_id = get_user_state(client_session).is_edit_reserve

                return jsonify({
                    'result': True,
                    'data': [reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values],
                }), 200
            
            except PostValueError as e:
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': e.args[0]}), 400

            except Exception as e:
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': 'Internal Server Error'}), 500
            
            finally :
                session.close()
            
        # ユーザー個人の取得
        case 'user':
            try :
                session = create_session()

                if request.method != 'GET':
                    abort(404)

                if not 'id' in client_session :
                    raise NotLoginError('ログインしていません。')

                is_required_user_id = False

                if 'user-state' in client_session :
                    is_required_user_id = get_user_state(client_session).is_edit_reserve

                user = session.query(User).filter(User.user_sub == client_session['id']).first()

                if user == None :
                    raise NonExistentUser('存在しないユーザーです。')

                reserve_values = session.query(Reservation).filter(
                    Reservation.reserved_user_id == user.get_id()
                ).all()

                return jsonify({
                    'result': True, 
                    'data': [reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values]
                    }), 200
            
            except NotLoginError as e :
                print(e)
                session.rollback()
                return jsonify({'result':False, 'message':e.args[0]}), 400
            
            except NonExistentUser as e :
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': e.args[0]}), 400

            except Exception as e:
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': 'Internal Server Error'}), 500
            
            finally :
                session.close()

        # クラスルームから予約を検索
        case 'classroom-id' :
            try :
                session = create_session()

                if request.method != 'POST':
                    abort(404)

                post_data = request.json

                if not 'classroom-id' in post_data :
                    raise PostValueError('無効なデータ形式です。')
                
                reserve_values = session.query(Reservation).filter(Reservation.classroom_id == post_data['classroom-id']).all()

                is_required_user_id = False

                if 'user-state' in client_session :
                    is_required_user_id = get_user_state(client_session).is_edit_reserve

                return jsonify({
                        'result':True,
                        'data':[reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values]
                    })
                
            except PostValueError as e :
                print(e)
                session.rollback()
                return jsonify({'result':False, 'message':e.args[0]}), 400

            except Exception as e :
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': 'Internal Server Error'}), 500

        case _:
            abort(404)


@reserve.route('/delete', methods=['DELETE'])
@login_required
def delete_reserve():
    try :
        session = create_session()

        post_data = request.json

        user_authority = session.query(Authority).filter(Authority.name == client_session['user-state']).first()

        if user_authority is None :
            abort(404)

        if not user_authority.is_reserve :
            abort(404)

        if not ('reservation-id' in post_data) :
            raise PostValueError('無効なデータ形式です。')

        delete_data = session.query(Reservation).filter(Reservation.reservation_id == post_data['reservation-id']).first()

        if delete_data is None :
            raise PostValueError('削除する予約がありません')
        
        if get_user_state(client_session).is_edit_reserve :
            reservations_dict = delete_data.to_dict(is_required_user_id=True)
            mail_thread = threading.Thread(target=send_reserve_delete_mail, args=(reservations_dict,), daemon=True)
            mail_thread.start()

        session.delete(delete_data)
        session.commit()

        return jsonify({'result':True})
    
    except PostValueError as e :
        print(e)
        session.rollback()
        return jsonify({'result':False, 'message':e.args[0]}), 400
        
    except Exception as e :
        print(e)
        session.rollback()
        return jsonify({'result':False, 'message':'Internal Server Error'}), 500
    
    finally :
        session.close()