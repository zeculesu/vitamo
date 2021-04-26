import os
from json import JSONDecodeError
from random import choice

from flask import url_for
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


def process_chat_form_data(form, request):
    title = form.title.data
    members = ','.join(form.users.data)
    logo = request.files.get('logo')
    if logo:
        mimetype = logo.mimetype.split('/')[-1]
        img_folder = url_for('static', filename='img').lstrip('/')
        existing_names = [x.split('.')[0] for x in os.listdir(img_folder)]
        filename = generate_random_name(existing_names)
        logo.save(os.path.join(img_folder, f'{filename}.{mimetype}'))
    return title, members, logo
