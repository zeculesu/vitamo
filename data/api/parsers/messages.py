from flask_restful.reqparse import RequestParser


class MessageAddParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(MessageAddParser, self).__init__(*args, **kwargs)
        self.add_argument('text', required=False)
        self.add_argument('attachments', required=False)


class MessagePutParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(MessagePutParser, self).__init__(*args, **kwargs)
        # self.add_argument('chat_id', type=int, required=False)
        self.add_argument('text', required=False)
        self.add_argument('attachments', required=False)
        self.add_argument('is_read', type=bool, required=False)


class MessageDeleteParser(RequestParser):
    def __init__(self, *args, **kwargs):
        super(MessageDeleteParser, self).__init__(*args, **kwargs)
        self.add_argument('self_only', type=bool, required=False)