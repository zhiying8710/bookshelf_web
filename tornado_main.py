# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import os
from utils.common import _base64
import tornado
from web.handlers import MainHandler, LoginRegHandler, CommonHandler,\
    ShelfHandler, BookHandler, UserHandler, ErrHandler, SearchHandler

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret" : _base64("bingege@soshu.com")
}

application = tornado.web.Application([
    (r"/([0-9]*)", MainHandler),
    (r"/authority/?([a-zA-Z0-9]*)", LoginRegHandler),
    (r"/common/([a-zA-Z][a-zA-Z0-9]+)/?([a-zA-Z0-9]*)", CommonHandler),
    (r"/shelf", ShelfHandler),
    (r"/book/([a-zA-Z0-9]+)/?([a-zA-Z]*)/?([a-zA-Z0-9/]*)", BookHandler),
    (r"/user/([a-zA-Z0-9]+)/?([a-zA-Z0-9]*)", UserHandler),
    (r"/search", SearchHandler),
    (r"/.+", ErrHandler),
], **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
