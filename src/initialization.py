from database import create_database, create_session, Classroom, Approved_User

create_database()

rooms = ['J301', 'J302', 'J303', 'J304', 'J401', 'J402', 'J403', 'J404']
users = [
    {
        'email':'gp22a074@oecu.jp',
        'name':'haruto'
    },
    {
        'email':'gp22a43@oecu.jp',
        'name':'hajime'
    },
    {
        'email':'gp22a030@oecu.jp',
        'name':'shiryu'
    },
    {
        'email':'mm23a008@oecu.jp',
        'name':'shuto'
    }
]

session = create_session()

for room in rooms :
    session.add(Classroom(classroom_name=room))

for user in users :
    session.add(Approved_User(approved_email=user['email'], approved_user_name=user['name']))

session.commit()

session.close()