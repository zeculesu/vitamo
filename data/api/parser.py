from typing import List

from flask_restful.reqparse import RequestParser

user_put_parser = RequestParser()
user_put_parser.add_argument('username', required=False)
user_put_parser.add_argument('password', required=False)
user_put_parser.add_argument('description', required=False)
user_put_parser.add_argument('logo', required=False)

user_add_parser = RequestParser()
user_add_parser.add_argument('email', required=True)
user_add_parser.add_argument('username', required=True)
user_add_parser.add_argument('password', required=True)
user_add_parser.add_argument('description', required=True)
user_add_parser.add_argument('logo', required=False)

chat_parser = RequestParser()
chat_parser.add_argument('users', required=True, type=list)
chat_parser.add_argument('title', required=False)
chat_parser.add_argument('logo', required=False)
