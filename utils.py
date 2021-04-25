from json import JSONDecodeError
from random import choice

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


def generate_random_name(existing_names, length=15):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    chars = [str(i) for i in range(10)] + list(alphabet) + list(alphabet.upper())
    output = None
    while output in existing_names or output is None:
        output = ''.join([choice(chars) for _ in range(length)])
    return output