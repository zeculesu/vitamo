from json import JSONDecodeError
from flask_jwt_extended import decode_token


def get_response_json(response):
    try:
        return response.json()
    except JSONDecodeError:
        return None


def get_user_id_from_jwt(jwt_token):
    return decode_token(jwt_token).get('user')