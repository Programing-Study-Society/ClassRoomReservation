from flask import Blueprint,jsonify,request
from flask import session as client_session
from sqlalchemy import or_, and_
from src.database import create_session
from src.module.function import generate_token
import src.database as DB
from  datetime import datetime

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')


class ReservationTimeValueError(Exception):
    pass

class Post_Value_Error(Exception):
    pass

class ManyAttemptsError(Exception):
    pass

MAX_ATTEMPTS = 2000


#予約可能な教室の取得
@classroom.route('/get', methods=['GET'])
def get_classrooms():
    try:
        session = create_session()

        posts_data = request.json
        print(posts_data)

        start_time = datetime.strptime(posts_data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(posts_data['end_time'], '%Y-%m-%d %H:%M:%S')
        now_time = datetime.now()

        if start_time < now_time:
            raise ReservationTimeValueError('現在時刻より後の時刻を入力してください')

        if  start_time > end_time:
            raise ReservationTimeValueError('開始時刻は終了時刻より前を入力してください')
                
        reserved_classroom = session.query(DB.Classroom)\
            .join(DB.Reservation, DB.Reservation.classroom_id == DB.Classroom.classroom_id)\
            .filter( or_(
                    and_(
                        DB.Reservation.start_time >= start_time, 
                        DB.Reservation.start_time <= end_time
                    ),
                    and_(
                        DB.Reservation.end_time >= start_time,
                        DB.Reservation.end_time <= end_time
                    ),
                    and_(
                        DB.Reservation.start_time >= start_time,
                        DB.Reservation.end_time <= end_time
                    ),
                    and_(
                        DB.Reservation.start_time <= start_time,
                        DB.Reservation.end_time >= end_time
                    )
                )
            ).all()
        
        classrooms = session.query(DB.Classroom)\
            .filter(~DB.Classroom.classroom_name.in_(
                    [classroom.classroom_name for classroom in reserved_classroom]
                )
            ).all()
        
        return jsonify({
            'result': True,
            'data': [{
                'classroom': [classroom.to_dict() for classroom in classrooms],
                'start-date': client_session['start_date'],
                'end-date': client_session['end_date']
            }]
        })

    except ReservationTimeValueError as e:
        print(e)
        session.rollback()
        return jsonify({
            'result': False,
            'message': e.args[0]
        }),400
        
    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            'message': 'Internal Server error'
        }),500
    
    finally :
        session.close()
        
@classroom.route('/add',methods=['POST'])
def add_classroom():
    try:
        session = create_session()
        
        classroom_data = request.get_json()
        print(classroom_data)
        
        name = classroom_data['classroom_name']
        
        if (not 'classroom_name' in classroom_data.keys()):
            raise Post_Value_Error('必要な情報が不足しています')
        
        if (not name.startswith('J')) or (not name.startswith('Z')):
            raise Post_Value_Error('存在しない教室名です')
        
        cnt = 0
        while True:
            cnt+=1
            classroom_id = generate_token(16)
            
            if not session.query(DB.Classroom).filter(DB.Classroom.classroom_id == classroom_id).first():
                break
            
            elif cnt >= MAX_ATTEMPTS:
                session.close()
                raise ManyAttemptsError('もう一度お試しください。')
        
        session.add(DB.Classroom(classroom['classroom_name']))
        
        session.commit()
        
        return jsonify({
            'result':True,
            # 'classroom':[{
            #     'result':True,
            #     'message': 'Internal'
            # }]
        }),200
        
    except ReservationTimeValueError as e:
        print(e)
        session.rollback()
        return jsonify({
            'result': False,
            'message': e.args[0]
        }),400
        
    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            'message': 'Internal Server error'
        }),500
        
    finally :
        session.close()
        
# @classroom.route('/delete',methods=['DELETE'])
# def delete_classroom():
#     try:
#         session = create_session()
        
#         classroom_data = request.get_json()
#         print(classroom_data)
    
#         if not 'classroom_name' in classroom_data.keys():
#             raise Post_Value_Error('必要な情報が不足しています')
        
#         if (not classroom_data['classroom_name'].startswith('J')) or (not classroom_data['classroom_name'].startswith('Z')):
#             raise Post_Value_Error('存在しない教室名です')