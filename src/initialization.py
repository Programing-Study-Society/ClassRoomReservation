from database import create_database, create_session, Approved_User

create_database()

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

for user in users :
    session.add(Approved_User(approved_email=user['email'], approved_user_name=user['name'], is_admin=user['is_admin']))

session.commit()

session.close()