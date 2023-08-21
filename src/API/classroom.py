from flask import Blueprint,jsonify,request
from sqlalchemy import or_, and_
from src.database import create_session
import src.database as DB
from  datetime import datetime

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')


class ReservationTimeValueError(Exception):
    pass


@classroom.route('/get', methods=['POST'])
def submit_reserve():
    try:
        posts_data = request.json

        start_time = datetime.strptime(posts_data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(posts_data['end_time'], '%Y-%m-%d %H:%M:%S')
        now_time = datetime.now()
        
        session = create_session()

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
        
        session.close()
        
        return jsonify({
            "result": True,
            "classrooms": [classroom.to_dict() for classroom in classrooms]
        })

    except ReservationTimeValueError as e:
        print(e)
        session.close()
        return jsonify({
            "result": False,
            "message": e.args[0]
        }),400
        

    except Exception as e:
        print(e)
        session.close()
        return jsonify({
            "result":False,
            "message": "Internal Server error"
        }),500