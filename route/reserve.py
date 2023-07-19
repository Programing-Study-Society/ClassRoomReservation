from flask import Blueprint, request, jsonify, abort
from database import Reservation, Classroom, create_session
from sqlalchemy import and_, or_
from datetime import datetime
import string, secrets

class ReserveValueError(Exception):
    pass


class PostValueError(Exception):
    pass


class ManyAttemptsError(Exception):
    pass


reserve = Blueprint('reserve', __name__, url_prefix='/reserve')

max_attempts = 2000


@reserve.route('/register', methods=['POST'])
def Register_reserve():
    try :

        posts_data = request.json

        start_time = datetime.strptime(posts_data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(posts_data['end_time'], '%Y-%m-%d %H:%M:%S')

        if start_time < datetime.now() or end_time < datetime.now() :
            raise ReserveValueError('無効な日時です。')
        
        if start_time.date() != end_time.date():
            raise ReserveValueError('日を跨いだ予約はできません。')

        session = create_session()
        
        str_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f'start : {str_start_time}')
        str_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f'end : {str_end_time}')

        advance_reservations = session.query(Reservation).filter(
            Reservation.classroom_id == posts_data['classroom_id'],
            or_(
                    and_(
                        Reservation.start_time >= start_time, 
                        Reservation.start_time <= end_time
                    ),
                    and_(
                        Reservation.end_time >= start_time,
                        Reservation.end_time <= end_time
                    ),
                    and_(
                        Reservation.start_time >= start_time,
                        Reservation.end_time <= end_time
                    ),
                    and_(
                        Reservation.start_time <= start_time,
                        Reservation.end_time >= end_time
                    )
                )
        ).all()

        if advance_reservations :
            raise ReserveValueError('すでに予約されています。')
        
        cnt = 0
        while True:
            cnt += 1
            include_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
            reservation_id = ''.join(secrets.choice(include_chars) for x in range(16))

            if not (session.query(Reservation).filter(Reservation.reservation_id == reservation_id).all()):
                break
            elif cnt >= max_attempts:
                raise ManyAttemptsError('もう一度お試しください')
            
        
        reservation_value = Reservation(
            reservation_id = reservation_id,
            classroom_id = posts_data['classroom_id'],
            start_time = start_time,
            end_time = end_time
        )

        session.add(reservation_value)
        session.commit()

        return jsonify({'result':True, 'reservation_id':reservation_value.reservation_id}), 200
        

    except ReserveValueError as e:
        print(e)
        return jsonify({'result':False, 'message':e.args[0]}), 400
    
    except Exception as e:
        print(e)
        return jsonify({'result':False, 'message':'Internal Server Error !'}), 500


@reserve.route('/get/<string:mode>', methods=['POST', 'GET'])
def reserve_get(mode):
    try :
        
        session = create_session()

        match mode:
            case 'id':
                
                if request.method != 'POST':
                    abort(404)

                reserve_value = session.query(Reservation)\
                    .filter(Reservation.reservation_id == request.json['reservation_id']).first()
                
                if not reserve_value :
                    raise PostValueError('指定されたIDは存在しません')
                
                classroom = session.query(Classroom)\
                    .filter(Classroom.classroom_id == reserve_value.classroom_id).first()
                
                return jsonify({
                        'result':True,
                        'value':{
                            'classroom_name':classroom.classroom_name,
                            'reserve':reserve_value.to_dict()
                        }
                    }), 200
            
            
            case 'full':

                if request.method != 'GET':
                    abort(404)

                reserve_values = session.query(Reservation)\
                    .join(Classroom, Classroom.classroom_id == Reservation.classroom_id).all()

                reserve_list = list()
                for reserve in reserve_values:
                    classroom = session.query(Classroom).filter(Classroom.classroom_id == reserve.classroom_id).first()
                    reserve_list.append({
                        'classroom_name':classroom.classroom_name,
                        'reserve':reserve.to_dict()
                    })
            
                return jsonify({
                    'result':True,
                    'value':reserve_list
                }), 200
            

            case 'date':
                
                if request.method != 'POST':
                    abort(404)

                post_data = request.json

                start_time = datetime.strptime(post_data['date'] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(post_data['date'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')

                # いま編集中！
                reserve_values = session.query(Reservation)\
                    .filter(and_(
                        Reservation.start_time >= start_time,
                        Reservation.end_time <= end_time
                    )).all()
                
                return jsonify({
                    'result':True,
                    'value':[reserve_value.to_dict() for reserve_value in reserve_values]
                })

        
        
    except PostValueError as e:
        print(e)
        return jsonify({'result':False, 'message':e.args[0]}), 400

    except Exception as e:
        print(e)
        return jsonify({'result':False, 'message':'Internal Server Error'}), 500