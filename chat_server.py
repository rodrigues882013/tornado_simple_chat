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


waiters = set()


def ws_send(url, message):
    
    ''' this method no used to client-to-client connectecion, but client -> server -> server-msg -> clients '''

    params = urllib.urlencode(dict(message=message))
    f = urllib.urlopen(url, params)
    data = f.read()
    f.close()
    return data


class SimpleChatPostHandler(RequestHandler):

    ''' this handler no used to client-to-client connectecion, but client -> server -> server-msg -> clients '''

    def data_received(self, chunk):
                pass

    def post(self):
        if 'message' in self.request.arguments:
            message = self.request.arguments['message'][0]
            print '%s:MESSAGE to %s:' % (time.time(), message)

                for waiter in waiters:
                    waiter.write_message(message)


class SimpleChatWSHandler(WebSocketHandler):
    
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
        logging.info("Sending messages to %d waiters", len(waiters))

        for waiter in waiters:
            waiter.write_message(chat)

    def open(self):
        logging.info("New Connection")
        waiters.add(self)

    def on_message(self, message):
        logging.info("Got message %r", message)

        parsed = json_decode(message)
        chat = dict(id=str(uuid.uuid4()), body=parsed)

        self.update_cache(chat)
        self.send_updates(chat)

        
    def on_close(self):
        waiters.remove(self)


def main():
    logging.basicConfig(filename='simplechat.log', level=logging.DEBUG)
    application = Application([
        (r'/simplechat', SimplChatWSHandler),
        ('r/', SimpleChatPostHandler)
    ])

    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
