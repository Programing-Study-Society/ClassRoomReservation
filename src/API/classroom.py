from flask import Blueprint, jsonify, request, abort, session as client_session
from sqlalchemy import or_, and_
from src.database import create_session
from src.module.function import generate_token, get_user_state
from  datetime import datetime
import src.database as DB
import re
from flask_login import login_required
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from email import policy
import os
import threading


classroom = Blueprint('classroom', __name__, url_prefix='/classroom')


class LuckOfInformationError(Exception):
    pass


class ReservationTimeValueError(Exception):
    pass


class Post_Value_Error(Exception):
    pass


class ManyAttemptsError(Exception):
    pass


class NothingResultValueError(Exception):
    pass


MAX_ATTEMPTS = 2000


def send_reserve_delete_mail(reservations) :
    mail = smtplib.SMTP(
        host = os.environ.get('MAIL_SERVER'),
        port=os.environ.get('MAIL_PORT')
        )
    
    mail.starttls()

    mail.login(
        user = os.environ.get('MAIL_USERNAME'),
        password = os.environ.get('MAIL_PASSWORD')
    )

    for reserve in reservations :
                
        formated_start_date = reserve['start-date'].replace('-', '/')
        formated_end_date = reserve['end-date'].replace('-', '/')
        
        send_txt = f"{reserve['user-name']} 様\n\n当サイトにてご予約いただいた\n\n{reserve['classroom-name']}教室　{formated_start_date} ～ {formated_end_date}\n\nの予約が取り消されました。\n\n当日は教室を貸出できないためご了承下さい。\n\n何かご不明な点がございましたら学務課までご連絡お願いいたします。"
        
        message = MIMEText(send_txt, "plain", "utf-8", policy=policy.default)
        message['Subject'] = '【お知らせ】教室のご予約取り消しについて'
        message['From'] = os.environ.get('MAIL_SENDER')
        message['To'] = reserve['user-email']
        message['Date'] = formatdate()

        mail.send_message(message)

    mail.close()


@classroom.errorhandler(404)
def notfound():
    return jsonify({'result':False, 'message':'Not found'}), 404


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
                
                post_data = request.json
            

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
                        
                classroom_values = session.query(DB.ReservableClassroom)\
                    .filter(and_(DB.ReservableClassroom.reservable_start_time <= start_time),
                        (DB.ReservableClassroom.reservable_end_time >= end_time)).all()
                
                #予約済みの教室を除いた教室
                
                # classrooms = session.query(DB.ReservableClassroom)\
                #     .filter(~DB.ReservableClassroom.classroom_name.in_(
                #             [classroom.classroom_name for classroom in reserved_classroom]
                #         )
                #     ).all()

                classroom_list = []
                for classroom_value in classroom_values :

                    classroom_dict = classroom_value.to_dict()

                    reserves = session.query(DB.Reservation.classroom_id).filter(DB.Reservation.classroom_id == classroom_value.classroom_id).first()

                    if reserves == None :
                        classroom_dict['is_reserved'] = False
                    else :
                        classroom_dict['is_reserved'] = True
                    
                    classroom_list.append(classroom_dict)
                
                return jsonify({
                    'result': True,
                    'data': classroom_list,
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
                    'message': 'サービスにエラーが発生しました。'
                }),500
            
            finally :
                session.close()
        
        case 'full':
            try:
                session = create_session()
                
                if request.method != 'GET':
                    abort(404)
                
                reserved_classrooms = session.query(DB.ReservableClassroom).\
                    order_by((DB.ReservableClassroom.reservable_start_time)).all()
                    
                # classroom_values = session.query(DB.ReservableClassroom)\
                #     .filter(~DB.ReservableClassroom.classroom_name.in_(
                #             [classroom.classroom_name for classroom in reserved_classroom]
                #         )
                #     ).all()
                    
                classroom_list = []
                for classroom_value in reserved_classrooms:

                    classroom_dict = classroom_value.to_dict()

                    reserves = session.query(DB.Reservation.classroom_id).filter(DB.Reservation.classroom_id == classroom_value.classroom_id).first()

                    if reserves == None :
                        classroom_dict['is_reserved'] = False
                    else :
                        classroom_dict['is_reserved'] = True
                    
                    classroom_list.append(classroom_dict)
                
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
                    'message': 'サービスにエラーが発生しました。'
                }),500
            

#　教室の追加をするエンドポイントです
@classroom.route('/add',methods=['POST'])
@login_required
def add_classroom():
    result_list = []
    try:
        if not get_user_state(client_session).is_edit_reserve :
            abort(404)

        for classroom_data in request.json:
            try:
                session = create_session()
            
                if not ('classroom-name' in classroom_data and 'start-date' in classroom_data and 'end-date' in classroom_data) :
                    raise LuckOfInformationError('必要な情報が不足しています')
                
                if len(classroom_data['start-date'] and classroom_data['end-date'] and classroom_data['classroom-name']) == 0:
                    raise LuckOfInformationError('必要な情報の値がありません')
                
                date_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'

                if re.match(date_pattern, classroom_data['start-date']) is None or re.match(date_pattern, classroom_data['end-date']) is None :
                    raise Post_Value_Error('日時が間違えています。(yyyy-mm-dd HH:MM:SS)')
                
                start_time = datetime.strptime(classroom_data['start-date'], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(classroom_data['end-date'], '%Y-%m-%d %H:%M:%S')
                now_time = datetime.now()
                
                if (start_time >= end_time):
                    raise Post_Value_Error('開始時刻は終了時刻よりも前の時間にしてください')
                
                if (start_time <= now_time):
                    raise Post_Value_Error('過去の日時は指定出来ません')
                
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
                
                session.add(add_classroom_data)
                session.commit()
                
                
                result_list.append(
                    {
                        'result':True,
                        'data': add_classroom_data.to_dict()
                    }
                )

            except LuckOfInformationError as e :
                print(e)
                
                classroom_name = classroom_data['classroom-name'] if 'classroom-name' in classroom_data else None
                start_date = classroom_data['start-date'] if 'start-date' in classroom_data else None
                end_date = classroom_data['end-date'] if 'end-date' in classroom_data else None

                result_list.append({
                    'result': False,
                    'message': e.args[0],
                    'data':{
                        'classroom-name':classroom_name,
                        'start-date':start_date,
                        'end-date':end_date
                    }
                })
                
            except ReservationTimeValueError as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result': False,
                    'message': e.args[0],
                    'data':{
                        'classroom-name':classroom_data['classroom-name'],
                        'start-date':classroom_data['start-date'],
                        'end-date':classroom_data['end-date']
                    }
                })
                
            except Post_Value_Error as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result': False,
                    'message': e.args[0],
                    'data':{
                        'classroom-name':classroom_data['classroom-name'],
                        'start-date':classroom_data['start-date'],
                        'end-date':classroom_data['end-date']
                    }
                })
                
            except Exception as e:
                print(e)
                session.rollback()
                result_list.append({
                    'result':False,
                    'message': 'サービスにエラーが発生しました。',
                    'data':{
                        'classroom-name':classroom_data['classroom-name'],
                        'start-date':classroom_data['start-date'],
                        'end-date':classroom_data['end-date']
                    }
                })
                
            finally :
                session.close()

        cnt = 0
        for result_value in result_list :
            if not result_value['result'] : cnt += 1

        if len(result_list) == cnt :
            raise NothingResultValueError('教室の追加に失敗しました。')
        
    except NothingResultValueError as e :
        print(e)
        return jsonify({
            'result': False,
            'message': e.args[0],
            'errors':result_list
        }), 400
    
    except Exception as e:
        print(e)
        return jsonify({
            'result': False,
            'message': 'サービスにエラーが発生しました。'
        }),500
    
    else:
        return jsonify({
            'result': True,
            'classroom': result_list
        }),200
        

# 教室の削除をするエンドポイントです
@classroom.route('/delete',methods=['DELETE'])
@login_required
def delete_classroom():
    try:
        if not get_user_state(client_session).is_edit_reserve :
            abort(404)

        session = create_session()
        
        post_data = request.json
    
        if not 'classroom-id' in post_data:
            raise Post_Value_Error('JSONの形式が異なります')
        
        delete_classroom_data = session.query(DB.ReservableClassroom)\
            .filter(DB.ReservableClassroom.classroom_id == post_data['classroom-id']).first()
        
        if delete_classroom_data is None:
            raise Post_Value_Error('削除可能な教室がありません')
        
        delete_classroom_id = delete_classroom_data.classroom_id

        reservations = session.query(DB.Reservation).filter(DB.Reservation.classroom_id == delete_classroom_id).all()
        
        if reservations != None :
            reservations_dict = [reserve.to_dict(is_required_user_id=True) for reserve in reservations]
            mail_thread = threading.Thread(target=send_reserve_delete_mail, args=(reservations_dict,), daemon=True)
            mail_thread.start()
        
        session.delete(delete_classroom_data)

        for reserve in reservations :
            session.delete(reserve)

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
        }), 400
        
    except Exception as e :
        print(e)
        session.close()
        return jsonify({
            'result':False, 
            'message':'サービスにエラーが発生しました。'
        }), 500
    
    finally :
        session.close() 