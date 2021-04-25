from flask import request
import requests

from utils import get_response_json


def add_new_users(user_name, email, password):
    basic_url = f'{request.host_url}api/users'

    response = get_response_json(requests.post(basic_url, data={'username': user_name,
                                                                'email': email,
                                                                'password': password}))
    if not response:
        return 'Server Error'
    if response.get('message') is not None and response.get('message') != 'OK':
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


def get_users(token):
    basic_url = f'{request.host_url}api/users'
    response = get_response_json(requests.get(basic_url, data={'token': token}))
    if not response:
        return None, 'Not Found error'
    if response.get('users') is None:
        return None, response.get('message', 'Unknown error')
    return response['users'], None


def get_chats(token, host_url=None):
    host_url = host_url if host_url is not None else request.host_url
    url = f'{host_url}api/chats'
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


# def read_message(chat_id, message_id, token):
#     url = f'{request.host_url}api/chats/{chat_id}/messages/{message_id}'
#     response = get_response_json(requests.put(url, data={'is_read': True, 'token': token}))
#     if response.get('message') is not None:
#         return response['message']
#     return Trueя