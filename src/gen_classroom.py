from datetime import datetime
from database import create_session, ReservableClassroom
from module.function import generate_token


rooms = [
    {
        'id': 'XCuNoRz8xCr8qgy0',
        'room':'J301',
        'start':datetime.strptime('2024-03-02 16:00:00', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2024-03-02 20:00:00', '%Y-%m-%d %H:%M:%S')
    }, 
    {
        'id': 'XCuNoRz8xCr8qgy1',
        'room':'J302',
        'start':datetime.strptime('2024-03-02 16:00:00', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2024-03-02 20:00:00', '%Y-%m-%d %H:%M:%S')
    }, 
    {
        'id': 'XCuNoRz8xCr8qgy2',
        'room':'J303',
        'start':datetime.strptime('2024-03-02 16:00:00', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2024-03-02 20:00:00', '%Y-%m-%d %H:%M:%S')
    }, 
    {
        'id': 'XCuNoRz8xCr8qgy3',
        'room':'J304',
        'start':datetime.strptime('2024-03-02 16:00:00', '%Y-%m-%d %H:%M:%S'),
        'end':datetime.strptime('2024-03-02 20:00:00', '%Y-%m-%d %H:%M:%S')
    }
]

session = create_session()

for room in rooms :
    session.add(ReservableClassroom(classroom_id=room['id'],classroom_name=room['room'], reservable_start_time=room['start'], reservable_end_time=room['end']))

session.commit()

session.close()