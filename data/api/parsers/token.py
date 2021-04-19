from flask_restful.reqparse import RequestParser


class TokenGetParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(TokenGetParser, self).__init__(*args, **kwargs)
        self.add_argument('username', required=True)
        self.add_argument('password', required=True)