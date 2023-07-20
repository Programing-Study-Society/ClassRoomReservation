from flask import Blueprint, request, jsonify, abort
from src.database import Reservation, Classroom, create_session
from sqlalchemy import and_, or_
from datetime import datetime
import string, secrets
import re

class ReserveValueError(Exception):
    pass


class PostValueError(Exception):
    pass


class ManyAttemptsError(Exception):
    pass


reserve = Blueprint('reserve', __name__, url_prefix='/reserve')

MAX_ATTEMPTS = 2000


# 予約IDを設定します
def generate_reservation_id():
    include_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(include_chars) for _ in range(16))


# 予約時間が予約可能かチェックします
def is_reservation_available(session, classroom_id, start_time, end_time):
    return session.query(Reservation).filter(
        Reservation.classroom_id == classroom_id,
        or_(
            and_(Reservation.start_time >= start_time, Reservation.start_time <= end_time),
            and_(Reservation.end_time >= start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time),
            and_(Reservation.start_time <= start_time, Reservation.end_time >= end_time),
        )
    ).first() is None


# 過去の予約データを削除します
def delete_past_reserved_date(session):
    while True:
        delete_reserve = session.query(Reservation).filter(Reservation.end_time < datetime.now()).first()
        if delete_reserve is None:
            break

        session.delete(delete_reserve)
        session.commit()


# 予約するエンドポイントです
@reserve.route('/register', methods=['POST'])
def register_reserve():
    try:
        posts_data = request.json
        start_time = datetime.strptime(posts_data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(posts_data['end_time'], '%Y-%m-%d %H:%M:%S')

        if start_time < datetime.now() or end_time < datetime.now():
            raise ReserveValueError('無効な日時です。')

        if start_time.date() != end_time.date():
            raise ReserveValueError('日を跨いだ予約はできません.')

        session = create_session()

        if not is_reservation_available(session, posts_data['classroom_id'], start_time, end_time):
            raise ReserveValueError('すでに予約されています。')

        cnt = 0
        while True:
            cnt += 1
            reservation_id = generate_reservation_id()

            if not session.query(Reservation).filter(Reservation.reservation_id == reservation_id).first():
                break

            elif cnt >= MAX_ATTEMPTS:
                raise ManyAttemptsError('もう一度お試しください.')

        reservation_value = Reservation(
            reservation_id=reservation_id,
            classroom_id=posts_data['classroom_id'],
            start_time=start_time,
            end_time=end_time,
        )

        session.add(reservation_value)
        session.commit()

        return jsonify({'result': True, 'reservation_id': reservation_value.reservation_id}), 200

    except ReserveValueError as e:
        print(e)
        return jsonify({'result': False, 'message': e.args[0]}), 400

    except Exception as e:
        print(e)
        return jsonify({'result': False, 'message': 'Internal Server Error !'}), 500


# 予約情報を取得するエンドポイントです
@reserve.route('/get/<string:mode>', methods=['POST', 'GET'])
def reserve_get(mode):
    try:
        session = create_session()

        if mode == 'id':
            if request.method != 'POST':
                abort(404)

            reservation_id = request.json['reservation_id']
            reserve_value = session.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()

            if not reserve_value:
                raise PostValueError('指定されたIDは存在しません.')

            classroom = session.query(Classroom).filter(Classroom.classroom_id == reserve_value.classroom_id).first()

            return jsonify({
                'result': True,
                'value': {
                    'classroom_name': classroom.classroom_name,
                    'reserve': reserve_value.to_dict(),
                },
            }), 200

        elif mode == 'full':
            if request.method != 'GET':
                abort(404)

            reserve_values = session.query(Reservation).join(Classroom, Classroom.classroom_id == Reservation.classroom_id).all()
            reserve_list = []
            for reserve in reserve_values:
                classroom = session.query(Classroom).filter(Classroom.classroom_id == reserve.classroom_id).first()
                reserve_list.append({
                    'classroom_name': classroom.classroom_name,
                    'reserve': reserve.to_dict(),
                })

            return jsonify({'result': True, 'value': reserve_list}), 200

        elif mode == 'date':
            if request.method != 'POST':
                abort(404)

            post_data = request.json
            date = post_data['date']

            if re.match(r'\d+-\d+-\d+', date) is None :
                raise PostValueError('日付のフォーマットが間違えています。(yyyy-mm-dd)')

            start_time = datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')

            reserve_values = session.query(Reservation).filter(
                and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time)
            ).all()

            return jsonify({
                'result': True,
                'value': [reserve_value.to_dict() for reserve_value in reserve_values],
            }), 200

        else:
            abort(404)

    except PostValueError as e:
        print(e)
        return jsonify({'result': False, 'message': e.args[0]}), 400

    except Exception as e:
        print(e)
        return jsonify({'result': False, 'message': 'Internal Server Error'}), 500