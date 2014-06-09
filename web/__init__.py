# encoding: utf-8
# Created on 2014-5-27
# @author: binge

from tornado.web import RequestHandler, HTTPError
import os
import tenjin
from tenjin.helpers import *
import json
import traceback
from utils.conns_helper import RedisHelper
import uuid
import time
from hashlib import sha1
from utils import settings
from service.user_service import UserService
from service.book_service import BookService
from utils.common import TimeHelper

tenjin_engine = tenjin.Engine(pp=[ tenjin.TrimPreprocessor() ], layout=os.path.join(os.path.dirname(__file__), "views/_layout.html"))

class BaseHandler(RequestHandler):

    MTHOD_NOT_ALLOWED = 405
    URL_NOT_FOUND = 404
    SERVER_ERROR = 500

    _skip_attrs = ['get', 'post']

    _redis = RedisHelper.get_redis_conn(db=settings.SESSION_REDIS_DB)

    def initialize(self, init_context=True):
        self.user_service = UserService()
        self.book_service = BookService()
        self.context = self.__init_context(init_context)

    def __init_context(self, init_context):
        context = {}
        if init_context:
            hot_kws = self.book_service.get_hot_search_kws(settings.hot_kws_show_count)
            context['hot_kws'] = hot_kws
            context['now_time'] = TimeHelper.time_2_str()
        top_books = self.book_service.get_rank_books(settings.books_cpc_alldays_key)
        descprition_kws = []
        for book in top_books:
            descprition_kws.append(book['name'])
        context['descprition_kws'] = ' '.join(descprition_kws)
        return context

    def render(self, template_name_prefix, template_name_suffix='.html', layout=True):
        self.write(tenjin_engine.render(os.path.join(os.path.dirname(__file__), template_name_prefix + template_name_suffix), self.context, layout=layout))
        self.finish()

#     def get_current_user(self):
#         user_id = self.get_secure_cookie("user_id")
#         if not user_id: return None
#         return self.backend.get_user_by_id(user_id)

    def raise_http_error(self, err_code, err_info=None):
        if err_info:
            err_info = traceback.format_exc()
        if err_info:
            print err_info
        if 'X-Requested-With' in self.request.headers and 'XMLHttpRequest' == self.request.headers['X-Requested-With']:
            self.set_status(err_code)
            self.finish()
        else:
            self.context['err_code'] = err_code
            self.render('views/err', layout=False)
#             raise HTTPError(err_code)

    def ajax_result(self, result):
        self.write(json.dumps(result, ensure_ascii=False))
        self.finish()

    def list_parms(self, params, empty_err_code=None):
        if not params:
            if empty_err_code:
                self.raise_http_error(empty_err_code)
            return []
        return params.split('/')

    def __set_session_attr__(self, name, value):
        Session(self).__setattr__(name, value)

    def __get_session_attr__(self, name):
        return Session(self).__getattr__(name)

    def __del_session_attr__(self, name):
        Session(self).__delattr__(name)

    def __destory_session__(self):
        Session(self).__destory__()

class Session(object):
    _prefix = "_session:"
    _id = None
    _skip = ['_redis', '_request', '_id']
    def __init__(self, request):
        self._redis = request._redis
        self._request = request
        # init session id
        _id = request.get_secure_cookie('sessionid')
        if _id and self._redis.exists(_id):
            self._id = _id

    def init_session(self):
        """初始化"""
        if not self._id:
            self._id = self.generate_session_id()
            self._request.set_secure_cookie('sessionid', self._id)
        # 延期过期时间
        self._redis.hset(self._id, 'lastActive', time.time())
        self._redis.expire(self._id, settings.SESSION_MAXLIFETIME)

    def generate_session_id(self):
        """Generate a random id for session"""
        secret_key = self._request.settings['cookie_secret']
        ip = self._request.request.remote_ip
        while True:
            rand = os.urandom(16)
            now = time.time()
            sessionid = sha1("%s%s%s%s" % (rand, now, ip, secret_key))
            sessionid = self._prefix + sessionid.hexdigest()
            if not self._redis.exists(sessionid):
                break
        return sessionid

    def __getattr__(self, name):
        if self._id:
            return self._redis.hget(self._id, name)
        if not name in self._skip:
            return None
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if not name in self._skip:
            self.init_session()
            self._redis.hset(self._id, name, value)
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if not name in self._skip:
            return self._redis.hdel(self._id, name)
        object.__delattr__(self, name)

    def __destory__(self):
        self._redis.delete(self._id)

def auto_login():
    def wrapper(fn):
        def login(request, *args):
            user = request.__get_session_attr__('user')
            if not user:
                user_id = request.get_secure_cookie('user_id')
                save_me = request.get_secure_cookie('save_me')
                if user_id and save_me:
                    user = request.user_service.find_by_id(user_id)
                    if user:
                        request.__set_session_attr__('user', user)
            else:
                user = eval(user)
            if user:
                request.current_user = user
                request.context['curr_user'] = user
            return fn(request, *args)
        return login
    return wrapper

def logout():
    def wrapper(fn):
        def _do(request, *args):
            request.__destory_session__()
            request.set_secure_cookie('save_me', '', 0)
            return fn(request, *args)
        return _do
    return wrapper

def except_err():
    def wrapper(fn):
        def _except(request, *args):
            try:
                return fn(request, *args)
            except:
                request.raise_http_error(request.SERVER_ERROR, traceback.format_exc())
            finally:
                pass
        return _except
    return wrapper
