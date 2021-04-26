from flask_restful.reqparse import RequestParser


class ChatAddParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(ChatAddParser, self).__init__(*args, **kwargs)
        self.add_argument('users', required=True)
        self.add_argument('title', required=False)
        self.add_argument('logo', required=False)


class ChatPutParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(ChatPutParser, self).__init__(*args, **kwargs)
        self.add_argument('users', required=False)
        self.add_argument('title', required=False)
        self.add_argument('logo', required=False)


class ChatAddUserParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(ChatAddUserParser, self).__init__(*args, **kwargs)
        self.add_argument('user_id', required=True, type=int)


class ChatKickUserParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(ChatKickUserParser, self).__init__(*args, **kwargs)
        self.add_argument('user_id', required=True, type=int)
