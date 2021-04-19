import requests


def add_new_users(user_name, email, password, description):
    basic_url = 'http://127.0.0.1:5000/api/users'
    response = requests.post(basic_url, params={'username': user_name,
                                                'email': email,
                                                'password': password,
                                                'description': description})
    return response


def authorize_user(login, password):
    basic_url = 'http://127.0.0.1:5000/api/authorize'
    response = requests.post(basic_url, params={'email': login,
                                                'password': password})
    return response
