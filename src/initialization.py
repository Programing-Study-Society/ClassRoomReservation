from database import create_database, create_session, Approved_User, UserStatus

create_database()

user_status = [
    {
        'name':'administrator',
        'is-edit-reserve':True,
        'is-edit-user':True
    },
    {
        'name':'moderator',
        'is-edit-reserve':True,
        'is-edit-user':False
    },
    {
        'name':'user',
        'is-edit-reserve':False,
        'is-edit-user':False
    }
]

users = [
    {
        'email':'gp22a074@oecu.jp',
        'name':'haruto',
        'user-state':'administrator'
    },
    {
        'email':'gp22a043@oecu.jp',
        'name':'hajime',
        'user-state':'administrator'
    },
    {
        'email':'gp22a030@oecu.jp',
        'name':'shiryu',
        'user-state':'administrator'
    },
    {
        'email':'mm23a008@oecu.jp',
        'name':'shuto',
        'user-state':'administrator'
    }
]

session = create_session()

for i, user_state in enumerate(user_status) :
    print(user_state)
    session.add(UserStatus(name=user_state['name'], is_edit_reserve=user_state['is-edit-reserve'], is_edit_user=user_state['is-edit-user']))

for user in users :
    session.add(Approved_User(approved_email=user['email'], approved_user_name=user['name'], user_state=user['user-state']))

session.commit()

session.close()