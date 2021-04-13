from flask_restful.reqparse import RequestParser


class MethodParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(MethodParser, self).__init__(*args, **kwargs)
        self.add_argument('method', required=True)


class ChatAddUserParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(ChatAddUserParser, self).__init__(*args, **kwargs)
        self.add_argument('user_id', required=True)


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
chat_parser.add_argument('users', required=False, type=list)
chat_parser.add_argument('title', required=False)
chat_parser.add_argument('logo', required=False)

chat_add_user_parser = RequestParser()
chat_add_user_parser.add_argument('user_id', required=True, type=int)

chat_kick_user_parser = RequestParser()
chat_kick_user_parser.add_argument('user_id', required=True, type=int)