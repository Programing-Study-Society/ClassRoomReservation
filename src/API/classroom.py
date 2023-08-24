from flask import Blueprint,jsonify,request
from sqlalchemy import or_, and_
from src.database import create_session
import src.database as DB
from  datetime import datetime

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')


class ReservationTimeValueError(Exception):
    pass

class Post_Value_Error(Exception):
    pass


@classroom.route('/get', methods=['POST'])
def get_classrooms():
    try:
        session = create_session()

        posts_data = request.json

        start_time = datetime.strptime(posts_data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(posts_data['end_time'], '%Y-%m-%d %H:%M:%S')
        now_time = datetime.now()

        if start_time < now_time:
            raise ReservationTimeValueError("現在時刻より後の時刻を入力してください")

        if  start_time > end_time:
            raise ReservationTimeValueError("開始時刻は終了時刻より前を入力してください")
                
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
            "result": True,
            "classrooms": [classroom.to_dict() for classroom in classrooms]
        })

    except ReservationTimeValueError as e:
        print(e)
        session.rollback()
        return jsonify({
            "result": False,
            "message": e.args[0]
        }),400
        
    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({
            "result":False,
            "message": "Internal Server error"
        }),500
    
    finally :
        session.close()
        
@classroom.route('/add',methods=['POST'])
def add_classroom():
    try:
        session = create_session()
        
        classroom = request.get_json()
        print(classroom)
        
        name = 'classroom_name' in classroom.keys()
        
        if not name:
            raise Post_Value_Error('必要な情報が不足しています')
        
        if (not name.startswith('J')) or (not name.startswith('Z')):
            raise Post_Value_Error('存在しない教室名です')
        
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
            "result": False,
            "message": e.args[0]
        }),400
        
    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({
            'result':False,
            "message": "Internal Server error"
        }),500
        
    finally :
        session.close()
        
# @classroom.route('/delete',methods=['DELETE'])
# def delete_classroom():
#     try:
#         session = create_session()
        
#         classroom = request.get_json()
#         print(classroom)
        
#         name = 'classroom_name' in classroom.keys()

#         if not name:
#             raise Post_Value_Error('必要な情報が不足しています')
        
#         if (not name.startswith('J')) or (not name.startswith('Z')):
#             raise Post_Value_Error('存在しない教室名です')
        
        
        
        
        