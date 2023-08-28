from flask import Blueprint, request, jsonify, abort, session as client_session
from src.database import Reservation, ReservableClassroom, Approved_User, create_session
from sqlalchemy import and_, or_, orm
from datetime import datetime
import re
from src.module.function import generate_token
from flask_login import login_required
from copy import deepcopy


class ReserveValueError(Exception):
    pass


class PostValueError(Exception):
    pass


class ManyAttemptsError(Exception):
    pass


class NotLoginError(Exception):
    pass


reserve = Blueprint('reserve', __name__, url_prefix='/reserve')

MAX_ATTEMPTS = 2000


# 予約時間が予約可能かチェックします
def check_reservable(session:orm.Session, classroom_id:str, start_time:datetime, end_time:datetime) -> str | None:
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
            and_(Reservation.start_time >= start_time, Reservation.start_time <= end_time),
            and_(Reservation.end_time >= start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time <= start_time, Reservation.end_time >= end_time),
        )
    ).first() != None :
        return '既に予約済みです。'
    
    return None


def is_approved_user(session:orm.Session, email:str):
    return session.query(Approved_User).filter(Approved_User.approved_email == email).first() != None


@reserve.errorhandler(404)
def notfound():
    return jsonify({'result':False, 'message':'Not found'})


# 予約するエンドポイントです
@reserve.route('/add', methods=['POST'])
@login_required
def register_reserve():
    try:
        session = create_session()

        post_datas = request.json

        if not ('start-date' in post_datas and 'end-date' in post_datas and 'classroom-id' in post_datas) :
            raise PostValueError('無効なデータ形式です。')

        start_time = datetime.strptime(post_datas['start-date'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(post_datas['end-date'], '%Y-%m-%d %H:%M:%S')

        if start_time < datetime.now() or end_time < datetime.now():
            raise ReserveValueError('無効な日時です。')

        if start_time.date() != end_time.date():
            raise ReserveValueError('日を跨いだ予約はできません。')
        
        classroom = session.query(ReservableClassroom).filter(
            ReservableClassroom.classroom_id == post_datas['classroom-id']
        ).first()

        reserve_state = check_reservable(session, classroom.classroom_id, start_time, end_time)

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
            reserved_user_id=client_session['id'],
            start_time=start_time,
            end_time=end_time,
        )

        session.add(reserve)
        session.commit()

        is_required_user_id = False

        if 'is_admin' in client_session :
            is_required_user_id = client_session['is_admin']

        return jsonify({'result': True, 'data': reserve.to_dict(is_required_user_id=is_required_user_id)}), 200

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

                if 'is_admin' in client_session :
                    is_required_user_id = client_session['is_admin']

                reserve_values = session.query(Reservation).join(
                        ReservableClassroom, 
                        ReservableClassroom.classroom_id == Reservation.classroom_id
                    ).order_by(Reservation.start_time).all()

                reserve_list = []
                for reserve in reserve_values:
                    classroom = session.query(ReservableClassroom).filter(ReservableClassroom.classroom_id == reserve.classroom_id).first()
                    reserve_list.append({
                        'classroom_name': classroom.classroom_name,
                        'reserve': reserve.to_dict(is_required_user_id=is_required_user_id),
                    })

                return jsonify({'result': True, 'value': reserve_list}), 200

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

                if 'is_admin' in client_session :
                    is_required_user_id = client_session['is_admin']

                return jsonify({
                    'result': True,
                    'value': [reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values],
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

                if 'is_admin' in client_session :
                    is_required_user_id = client_session['is_admin']

                reserve_values = session.query(Reservation).filter(
                    Reservation.reserved_user_id == client_session['id']
                ).all()

                return jsonify({
                    'result': True, 
                    'value': [reserve_value.to_dict(is_required_user_id=is_required_user_id) for reserve_value in reserve_values]
                    }), 200
            
            except NotLoginError as e :
                print(e)
                session.rollback()
                return jsonify({'result':False, 'message':e.args[0]}), 400

            except Exception as e:
                print(e)
                session.rollback()
                return jsonify({'result': False, 'message': 'Internal Server Error'}), 500
            
            finally :
                session.close()

        case _:
            abort(404)


@reserve.route('/delete', methods=['DELETE'])
@login_required
def delete_reserve():
    try :
        session = create_session()

        post_data = request.json

        if not ('reservation-id' in post_data) :
            raise PostValueError('無効なデータ形式です。')

        delete_date = session.query(Reservation).filter(Reservation.reservation_id == post_data['reservation-id']).first()

        if delete_date is None :
            raise PostValueError('削除する予約がありません')
        
        deleted_reserve_id = deepcopy(delete_date.reservation_id)
        
        session.delete(delete_date)
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