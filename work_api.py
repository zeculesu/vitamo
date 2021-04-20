import requests

from utils import get_response_json


def add_new_users(user_name, email, password):
    basic_url = 'http://127.0.0.1:5000/api/users'
    response = get_response_json(requests.post(basic_url, data={'username': user_name,
                                                                'email': email,
                                                                'password': password}))
    print(f'response: {response}')
    if not response:
        return 'Server Error'


def authorize_user(login, password):
    basic_url = 'http://127.0.0.1:5000/api/authorize'
    response = get_response_json(requests.get(basic_url, data={'username': login,
                                                               'password': password}))
    if not response:
        return None, 'Not Found error'
    if not response.get('token'):
        return None, response.get('message', 'Unknown error')
    return response['token'], None
