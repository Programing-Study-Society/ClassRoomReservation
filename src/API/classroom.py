from flask import Blueprint,jsonify,request,abort
from flask import session as client_session
from sqlalchemy import or_, and_
from src.database import create_session
from src.module.function import generate_token
from  datetime import datetime
import src.database as DB
import re

classroom = Blueprint('classroom', __name__, url_prefix='/classroom')


class ReservationTimeValueError(Exception):
    pass

class Post_Value_Error(Exception):
    pass

class ManyAttemptsError(Exception):
    pass

MAX_ATTEMPTS = 2000


#　予約可能な教室の取得をするエンドポイントです
@classroom.route('/get/<string:mode>', methods=['GET','POST'])
def get_classrooms(mode):
    match mode:
        # 日付での取得
        case 'date':
            try:
                session = create_session()

                if request.method == 'POST':
                    abort(404)
                
                post_data = request.get_json()
                print(post_data)
                
                date = post_data['date']

                if re.match(r'\d+-\d+-\d+', date) is None:
                    raise Post_Value_Error('日付のフォーマットが間違えています。(yyyy-mm-dd)')

                start_time = datetime.strptime(post_data['start_time'], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(post_data['end_time'], '%Y-%m-%d %H:%M:%S')
                now_time = datetime.now()

                if start_time < now_time or end_time < now_time:
                    raise ReservationTimeValueError('現在時刻より後の時刻を入力してください')

                if  start_time > end_time:
                    raise ReservationTimeValueError('開始時刻は終了時刻より前を入力してください')
                        
                reserved_classroom = session.query(DB.ReservableClassroom)\
                    .join(DB.Reservation, DB.Reservation.classroom_id == DB.ReservableClassroom.classroom_id)\
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
                
                classrooms = session.query(DB.ReservableClassroom)\
                    .filter(~DB.ReservableClassroom.classroom_name.in_(
                            [classroom.classroom_name for classroom in reserved_classroom]
                        )
                    ).all()
                
                return jsonify({
                    'result': True,
                    'data': [classroom.to_dict() for classroom in classrooms]
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
        
        case 'full':
            try:
                session = create_session()
                
                if request.method != 'GET':
                    abort(404)
                
                reserved_classroom = session.query(DB.ReservableClassroom)\
                    .join(DB.Reservation, DB.Reservation.classroom_id == DB.ReservableClassroom.classroom_id).all()
                    
                classroom_values = session.query(DB.ReservableClassroom)\
                    .filter(~DB.ReservableClassroom.classroom_name.in_(
                            [classroom.classroom_name for classroom in reserved_classroom]
                        )
                    ).all()
                    
                classroom_list = []
                for classroom_value in classroom_values:
                    classroom_list.append({
                        'result': True,
                        'date': classroom_value.to_dict()
                    })
                
                return jsonify({
                    'result': True,
                    'data': classroom_list
                }),200
            
            except Post_Value_Error as e:
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
                    'result': False,
                    'message': 'Internal Server Error'
                }),500

#　教室の追加をするエンドポイントです
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
            
            if not session.query(DB.ReservableClassroom).filter(DB.ReservableClassroom.classroom_id == classroom_id).first():
                break
            
            elif cnt >= MAX_ATTEMPTS:
                session.close()
                raise ManyAttemptsError('もう一度お試しください。')
        
        session.add(DB.ReservableClassroom(classroom['classroom_name']))
        session.commit()
        
        return jsonify({
            'result':True,
            'message':'成功',
            'classroom':[{
                'result':True,
                'message':'成功',
                'classroom-name': client_session['classroom_name'],
                'start-date': client_session['start_date'],
                'end-date': client_session['end_date']
            }]
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
        
# 教室の削除をするエンドポイントです
@classroom.route('/delete',methods=['DELETE'])
def delete_classroom():
    try:
        session = create_session()
        
        post_data = request.get_json()
        print(post_data)
    
        if not post_data in 'classroom':
            raise Post_Value_Error('JSONの形式が異なります')
        
        delete_classroom_data = session.query(DB.ReservableClassroom)\
            .filter(DB.ReservableClassroom.classroom_id == post_data['classroom_id']).first()
        
        if delete_classroom_data is None:
            raise Post_Value_Error('削除可能な教室がありません')
        
        session.delete(delete_classroom_data)
        session.commit()
        
    except Post_Value_Error as e :
        print(e)
        session.close()
        return jsonify({
            'result':False, 
            'message':e.args[0]
        })
        
    except Exception as e :
        print(e)
        session.close()
        return jsonify({
            'result':False, 
            'message':'Internal Server Error'
        }), 500
    
    finally :
        session.close() 