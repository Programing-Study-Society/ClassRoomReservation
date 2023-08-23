import string
import secrets

# 予約IDを設定します
def generate_token(len:int):
    include_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(include_chars) for _ in range(len))