import string
import secrets
from src.database import create_session, Authority


# 予約IDを設定します
def generate_token(len:int):
    include_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(include_chars) for _ in range(len))


def get_user_state(client_session) -> Authority | None:
    if client_session['user-state'] is None :
        return None
    session = create_session()
    user_state = session.query(Authority).filter(Authority.name == client_session['user-state']).first()
    session.close()
    return user_state