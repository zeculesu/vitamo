from flask import request
import requests

from utils import get_response_json


def add_new_users(user_name, email, password):
    basic_url = 'http://127.0.0.1:5000/api/users'
    response = get_response_json(requests.post(basic_url, data={'username': user_name,
                                                                'email': email,
                                                                'password': password}))
    if not response:
        return 'Server Error'
    if response.get('message') != 'OK':
        return response['message']


def authorize_user(login, password):
    basic_url = f'{request.host_url}api/authorize'
    response = get_response_json(requests.get(basic_url, data={'username': login,
                                                               'password': password}))
    if not response:
        return None, 'Not Found error'
    if not response.get('token'):
        return None, response.get('message', 'Unknown error')
    return response['token'], None


def get_chats(token):
    url = f'{request.host_url}api/chats'
    response = get_response_json(requests.get(url, data={'token': token}))
    if response.get('message') is not None:
        return None, response['message']
    if not response:
        return 'Server Error'
    return response.get('chats'), None


def get_chat(chat_id, token):
    url = f'{request.host_url}api/chats/{chat_id}'
    response = get_response_json(requests.get(url, data={'token': token}))
    if response.get('message') is not None:
        return None, response['message']
    return response.get('chat'), None