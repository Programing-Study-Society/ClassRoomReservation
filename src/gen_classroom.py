from datetime import datetime
from database import create_session, ReservableClassroom
from module.function import generate_token


rooms = [
    {
        'id': generate_token(16),
        'room':'J301',
        'start':datetime.strptime('2004-03-02 16:44:35', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2004-03-02 16:46:35', '%Y-%m-%d %H:%M:%S')
    }, 
    {
        'id': generate_token(16),
        'room':'J302',
        'start':datetime.strptime('2024-03-02 16:44:35', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2024-03-02 16:46:35', '%Y-%m-%d %H:%M:%S')
    }
]

session = create_session()

for room in rooms :
    session.add(ReservableClassroom(classroom_id=room['id'],classroom_name=room['room'], reservable_start_time=room['start'], reservable_end_time=room['end']))

session.commit()

session.close()