from database import create_database, create_session, Classroom

create_database()
rooms = ['J301', 'J302', 'J303', 'J304', 'J401', 'J402', 'J403', 'J404']
session = create_session()
for room in rooms :
    session.add(Classroom(classroom_name=room))
    session.commit()