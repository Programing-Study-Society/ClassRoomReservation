from database import create_database, create_session, Classroom, Approved_User

create_database()

rooms = ['J301', 'J302', 'J303', 'J304', 'J401', 'J402', 'J403', 'J404']
users = [
    {
        'email':'gp22a074@oecu.jp',
        'name':'haruto',
        'is_admin':True
    },
    {
        'email':'gp22a043@oecu.jp',
        'name':'hajime',
        'is_admin':True
    },
    {
        'email':'gp22a030@oecu.jp',
        'name':'shiryu',
        'is_admin':True
    },
    {
        'email':'mm23a008@oecu.jp',
        'name':'shuto',
        'is_admin':True
    }
]

session = create_session()

for room in rooms :
    session.add(Classroom(classroom_name=room))

for user in users :
    session.add(Approved_User(approved_email=user['email'], approved_user_name=user['name'], is_admin=user['is_admin']))

session.commit()

session.close()