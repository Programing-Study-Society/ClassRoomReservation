from flask import Blueprint,jsonify,request,abort
from sqlalchemy import or_, and_
from src.database import create_session
from src.module.function import generate_token
from  datetime import datetime
import src.database as DB
import re
from flask_login import login_required

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

                if request.method != 'POST':
                    abort(404)
                
                post_data = request.get_json()
                print(post_data)
            

                if re.match(r'\d+-\d+-\d+', post_data['start-date']) is None or \
                    re.match(r'\d+-\d+-\d+', post_data['end-date']) is None:
                    raise Post_Value_Error('日付のフォーマットが間違えています。(yyyy-mm-dd)')

                start_time = datetime.strptime(post_data['start-date'], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(post_data['end-date'], '%Y-%m-%d %H:%M:%S')
                now_time = datetime.now()

                if start_time < now_time or end_time < now_time:
                    raise ReservationTimeValueError('現在時刻より後の時刻を入力してください')

                if  start_time > end_time:
                    raise ReservationTimeValueError('開始時刻は終了時刻より前を入力してください')
                        
                reserved_classroom = session.query(DB.ReservableClassroom)\
                    .filter(and_(DB.ReservableClassroom.reservable_start_time <= start_time),
                        (DB.ReservableClassroom.reservable_end_time >= end_time)).all()
                
                #予約済みの教室を除いた教室
                
                # classrooms = session.query(DB.ReservableClassroom)\
                #     .filter(~DB.ReservableClassroom.classroom_name.in_(
                #             [classroom.classroom_name for classroom in reserved_classroom]
                #         )
                #     ).all()
                
                return jsonify({
                    'result': True,
                    'data': [classroom.to_dict() for classroom in reserved_classroom],
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
@login_required
def add_classroom():
    result_list = []
    try:
        for classroom_data in request.json:
            try:
                session = create_session()
                
                print('ここから下')
                print()
                
                name = classroom_data['classroom-name']
                
                if (not 'classroom-name' in classroom_data.keys()):
                    raise Post_Value_Error('必要な情報が不足しています')
                
                if (not name.startswith('J')) and (not name.startswith('Z')):
                    raise Post_Value_Error('存在しない教室名です')
                
                if (classroom_data['start-date'] >= classroom_data['end-date']):
                    raise Post_Value_Error('開始時刻は終了時刻よりも前の時間にしてください')
                
                cnt = 0
                while True:
                    cnt+=1
                    classroom_id = generate_token(16)
                    
                    if not session.query(DB.ReservableClassroom).filter(DB.ReservableClassroom.classroom_id == classroom_id).first():
                        break
                    
                    elif cnt >= MAX_ATTEMPTS:
                        raise ManyAttemptsError('もう一度お試しください。')
                
                add_classroom_data = DB.ReservableClassroom(
                    classroom_id = classroom_id,
                    classroom_name = classroom_data['classroom-name'],
                    reservable_start_time = datetime.strptime(classroom_data['start-date'], '%Y-%m-%d %H:%M:%S'),
                    reservable_end_time = datetime.strptime(classroom_data['end-date'], '%Y-%m-%d %H:%M:%S')
                )
                
                if session.query(DB.ReservableClassroom).filter(
                    DB.ReservableClassroom.classroom_name == add_classroom_data.classroom_name,\
                        or_(
                            and_(DB.ReservableClassroom.reservable_start_time >= add_classroom_data.reservable_start_time, \
                                DB.ReservableClassroom.reservable_start_time <= add_classroom_data.reservable_end_time),
                            and_(DB.ReservableClassroom.reservable_end_time >= add_classroom_data.reservable_start_time, \
                                DB.ReservableClassroom.reservable_end_time <= add_classroom_data.reservable_end_time),
                            and_(DB.ReservableClassroom.reservable_start_time >= add_classroom_data.reservable_start_time, \
                                DB.ReservableClassroom.reservable_end_time <= add_classroom_data.reservable_end_time),
                            and_(DB.ReservableClassroom.reservable_start_time <= add_classroom_data.reservable_start_time, \
                                DB.ReservableClassroom.reservable_end_time >= add_classroom_data.reservable_end_time),
                        )).first() != None:
                    raise Post_Value_Error('既に追加された教室です')
                
                else:
                    session.add(add_classroom_data)
                session.commit()
                
                
                result_list.append(
                    {
                        'result':True,
                        'data': add_classroom_data.to_dict()
                    }
                )
                
            except ReservationTimeValueError as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result': False,
                    'message': e.args[0]
                })
                
            except Post_Value_Error as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result': False,
                    'message': e.args[0]
                })
                
            except Exception as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result':False,
                    'message': 'Internal Server error'
                })
                
            finally :
                session.close()
    
    except Exception as e:
        return jsonify({
            'result': False,
            'message': 'Internal Server Error'
        }),500
    
    else:
        return jsonify({
            'result': True,
            'data': result_list
        }),200
        
# 教室の削除をするエンドポイントです
@classroom.route('/delete',methods=['DELETE'])
@login_required
def delete_classroom():
    try:
        session = create_session()
        
        post_data = request.get_json()
        print(post_data)
    
        if not 'classroom_id' in post_data:
            raise Post_Value_Error('JSONの形式が異なります')
        
        delete_classroom_data = session.query(DB.ReservableClassroom)\
            .filter(DB.ReservableClassroom.classroom_id == post_data['classroom_id']).first()
        
        if delete_classroom_data is None:
            raise Post_Value_Error('削除可能な教室がありません')
        
        session.delete(delete_classroom_data)
        session.commit()
        
        return jsonify({
            'result': True
        }),200
        
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