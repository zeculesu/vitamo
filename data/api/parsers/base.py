from flask_restful.reqparse import RequestParser


class MethodParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(MethodParser, self).__init__(*args, **kwargs)
        self.add_argument('method', required=True)