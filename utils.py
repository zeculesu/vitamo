from json import JSONDecodeError
from flask_jwt_extended import decode_token


def get_response_json(response):
    try:
        return response.json()
    except JSONDecodeError:
        return None


def get_user_id_from_jwt(jwt_token):
    return decode_token(jwt_token).get('user')


def assert_sorted_data(source, data=None):
    source = [sorted(list(x.items()), key=lambda x: x[0]) for x in source]
    if data is None:
        return source
    return data if [sorted(list(x.items()), key=lambda x: x[0]) for x in data] != source else None