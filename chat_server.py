__author__ : 'felipe'

'''Base in oficial samples available in https://github.com/tornadoweb/tornado/tree/stable/demos'''


import logging
import uuid

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.escape import json_decode, to_basestring


class SimpleChatPostHandler(RequestHandler):

    def post(self, *args, **kwargs):
        pass


class SimpleChatWSHandler(WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def check_origin(self, origin):
        return True

    @staticmethod
    def get_compression_options():
        # Non-None enables compression with default options.
        return {}

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("Sending messages to %d waiters", len(cls.waiters))

        for waiter in cls.waiters:
            waiter.write_message(chat)

    def open(self):
        logging.info("New Connection")
        self.waiters.add(self)

    def on_message(self, message):
        logging.info("Got message %r", message)

        parsed = json_decode(message)
        chat = dict(id=str(uuid.uiid4()), body=parsed['body'])

        self.update_cache(chat)
        self.send_updates(chat)

        # self.write_message(message)

    def on_close(self):
        self.waiters.remove(self)


def main():
    logging.basicConfig(filename='simplechat.log', level=logging.DEBUG)
    application = Application([
        (r'/simplechat', SimplChatWSHandler),
    ])

    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
