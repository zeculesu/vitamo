from flask_restful.reqparse import RequestParser


class UserAddParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(UserAddParser, self).__init__(*args, **kwargs)
        self.add_argument('email', required=True)
        self.add_argument('username', required=True)
        self.add_argument('password', required=True)
        self.add_argument('description', required=False)
        self.add_argument('logo', required=False)


class UserPutParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(UserPutParser, self).__init__(*args, **kwargs)
        self.add_argument('username', required=False)
        self.add_argument('email', required=False)
        self.add_argument('password', required=False)
        self.add_argument('description', required=False)
        self.add_argument('logo', required=False)
