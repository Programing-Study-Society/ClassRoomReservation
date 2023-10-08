from database import create_database, create_session, User, Authority
import string
import secrets

# 予約IDを設定します
def generate_token(len:int):
    include_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(include_chars) for _ in range(len))


create_database()

session = create_session()

registered_authorities = session.query(Authority).all()
registered_users = session.query(User).all()

if registered_authorities is None :

    user_status = [
        {
            'name':'administrator',
            'is-reserve':True,
            'is-admin':True,
            'is-edit-reserve':True,
            'is-edit-user':True
        },
        {
            'name':'moderator',
            'is-reserve':False,
            'is-admin':True,
            'is-edit-reserve':True,
            'is-edit-user':False
        },
        {
            'name':'user',
            'is-reserve':True,
            'is-admin':False,
            'is-edit-reserve':False,
            'is-edit-user':False
        }
    ]


    for i, user_state in enumerate(user_status) :
        session.add(Authority(
            name=user_state['name'],
            is_reserve=user_state['is-reserve'],
            is_admin=user_state['is-admin'],
            is_edit_reserve=user_state['is-edit-reserve'], 
            is_edit_user=user_state['is-edit-user']
        ))
        
        
if registered_users is None : 

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

    for user in users :
        session.add(User(
                user_email=user['email'], 
                user_name=user['name'], 
                user_state=user['user-state'], 
                user_id=generate_token(32)
            ))
        

    session.commit()

    session.close()