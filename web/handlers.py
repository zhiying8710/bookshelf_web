# encoding: utf-8
# Created on 2014-5-23
# @author: binge

from web import BaseHandler, auto_login, logout, except_err
from utils.common import TimeHelper, _md5, _base64
from service.section_service import SectionService
from service.common_service import CommonService
import tornado.web
from utils import settings
import os

class MainHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)

    @except_err()
    @auto_login()
    def get(self, curr_page=1):
        if self.current_user:
            self.context['user_books'] = self.book_service.find_user_books(self.current_user['_id'])
        else:
            user_id = self.get_secure_cookie('user_id')
            if user_id:
                self.context['user_books'] = self.book_service.find_user_books(user_id)

        self.context['books_page'] = self.book_service.find_books_page(curr_page)
        self.context['now_time'] = TimeHelper.time_2_str()
        self.render('views/index')

    @tornado.web.asynchronous
    @except_err()
    @auto_login()
    def post(self, *args):
        kw = self.get_argument('kw', None)
        if not kw:
            self.redirect('/')
        else:
            books = self.book_service.search(kw)
            self.context['books'] = books
            self.context['kw'] = kw
            self.render('views/search')
            self.book_service.record_search_kw(kw)

class LoginRegHandler(BaseHandler):

    CODE_NAME_PWD_EMPTY = 0
    CODE_AUTO_REG_SUCC = 1
    CODE_AUTO_REG_FAIL = 2
    CODE_LOGIN_SUCC = 2
    CODE_LOGIN_PWD_ERR = 3

    def initialize(self):
        BaseHandler.initialize(self, init_context=False)

    @except_err()
    def post(self, *args):
        user_name = self.get_argument('user_name', None)
        pass_word = self.get_argument('pass_word', None)
        save_me = self.get_argument('saveme', None)
        if not user_name or not user_name.strip() or not pass_word or not pass_word.strip():
            self.ajax_result({'succ' : False, 'code' : self.CODE_NAME_PWD_EMPTY})
        else:
            user = self.user_service.find_by_name(user_name)
            result = {}
            user_id = self.get_secure_cookie("user_id")
            if not user:
                user = self.user_service.auto_reg_user(user_name, pass_word, user_id)
                if user:
                    user_id = user['_id']
                    result['succ'] = True
                    result['code'] = self.CODE_AUTO_REG_SUCC
                else:
                    result['succ'] = False
                    result['code'] = self.CODE_AUTO_REG_FAIL
            else:
                if _md5(pass_word) == user['pass_word']:
                    t_user_id = user['_id']
                    if user_id and not user_id == t_user_id:
                        self.user_service.append_favos_from_cookie_uid(t_user_id, user_id)
                    user_id = t_user_id
                    result['succ'] = True
                    result['code'] = self.CODE_LOGIN_SUCC
                else:
                    result['succ'] = False
                    result['code'] = self.CODE_LOGIN_PWD_ERR
            if user and result['succ']:
                self.__set_session_attr__('user', user)
                self.set_secure_cookie('user_id', user_id, 365 * 10)
                self.set_secure_cookie('save_me', '1', int(save_me))
                user['pass_word'] = ''
                result['curr_user'] = user
            self.ajax_result(result)

    @except_err()
    def get(self, method=None):
        if not method:
            self.render('views/login_reg')
        else:
            if not hasattr(self, method) or method in self._skip_attrs:
                self.raise_http_error(self.URL_NOT_FOUND)
                return
            eval("self." + method + "()")

    @except_err()
    @logout()
    def logout(self, *args):
        self.redirect('/')

class ShelfHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)

    @except_err()
    @auto_login()
    def get(self, *args):
        if self.current_user:
            self.context['user_books'] = self.book_service.find_user_books(self.current_user['_id'])
        else:
            user_id = self.get_secure_cookie('user_id')
            if user_id:
                self.context['user_books'] = self.book_service.find_user_books(user_id)
        self.render("views/shelf")

    def post(self, *args):
        self.get()

class UserHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self, init_context=False)

    def post(self, m, *args):
        self.get(m, *args)

    @except_err()
    @auto_login()
    def get(self, m, params=None):
        if not m:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            if not hasattr(self, m) or m in self._skip_attrs:
                self.raise_http_error(self.URL_NOT_FOUND)
            else:
                eval("self." + m + "(params)")

    @tornado.web.asynchronous
    def favo(self, params):
        args = self.list_parms(params, self.URL_NOT_FOUND)
        b_id = args[0]
        if self.current_user:
            user_id = self.current_user['_id']
        else:
            user_id = self.get_secure_cookie('user_id')
        self.ajax_result({'succ' : self.user_service.favo(user_id, b_id)})
        self.book_service.record_book_favo(b_id)

    def unfavo(self, *args):
        bids = self.get_arguments('u_books')
        if self.current_user:
            user_id = self.current_user['_id']
        else:
            user_id = self.get_secure_cookie('user_id')
        if bids and user_id:
            self.ajax_result({'succ' : self.user_service.unfavo(user_id, bids)})
        else:
            self.ajax_result({'succ' : True})

    def unfavoall(self, *args):
        if self.current_user:
            user_id = self.current_user['_id']
        else:
            user_id = self.get_secure_cookie('user_id')
        if user_id:
            self.ajax_result({'succ' : self.user_service.unfavoall(user_id)})
        else:
            self.ajax_result({'succ' : True})

class BookHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.section_service = SectionService()

    @tornado.web.asynchronous
    @except_err()
    @auto_login()
    def get(self, _id, m=None, params=None):
        if not m:
            self.page(_id, [])
            self.book_service.record_book_cpc(_id)
        else:
            if not hasattr(self, m) or m in self._skip_attrs:
                self.raise_http_error(self.URL_NOT_FOUND)
            else:
                eval("self." + m + "(_id, params)")

    def post(self,_id, m=None, params=None):
        self.get(_id, m, params)

    def page(self, _id, params):
        if not _id:
            self.raise_http_error(self.URL_NOT_FOUND)
            return
        book = self.book_service.find_book_by_id(_id)
        if not book:
            self.redirect('/')
            return
        args = self.list_parms(params)
        curr_page = 1
        site = None
        try:
            curr_page = args[0]
            site = args[1]
        except:
            pass
        if 'desc' in book:
            book['desc'] = _base64(book['desc'], e=False)
        else:
            book['desc'] = ''
        self.context['book'] = book
        self.context['author_books'] = self.book_service.find_author_books(book['author'])
        self.context['site'] = site
        if len(self.context['author_books']) == 1:
            self.context['author_books'] = []
        sections_page = self.section_service.find_sections_page_by_id_site(_id, site, curr_page)
        self.context['sections_page'] = sections_page
        if self.current_user:
            self.context['curr_user'] = self.current_user
            self.user_service.clear_user_update_count(self.current_user['_id'], _id)

        self.render('views/book')

class RankHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self);

    @except_err()
    @auto_login()
    def get(self, *args):
        week_cpc_books = self.book_service.get_rank_books(settings.books_cpc_week_key_prefix + TimeHelper.get_week_no())
        month_cpc_books = self.book_service.get_rank_books(settings.books_cpc_month_key_prefix + TimeHelper.get_month())
        alldays_cpc_books = self.book_service.get_rank_books(settings.books_cpc_alldays_key)
        week_favo_books = self.book_service.get_rank_books(settings.books_favo_week_key_prefix + TimeHelper.get_week_no())
        month_favo_books = self.book_service.get_rank_books(settings.books_favo_month_key_prefix + TimeHelper.get_month())
        alldays_favo_books = self.book_service.get_rank_books(settings.books_favo_alldays_key)
        self.context['week_cpc_books'] = week_cpc_books
        self.context['month_cpc_books'] = month_cpc_books
        self.context['alldays_cpc_books'] = alldays_cpc_books
        self.context['week_favo_books'] = week_favo_books
        self.context['month_favo_books'] = month_favo_books
        self.context['alldays_favo_books'] = alldays_favo_books
        self.render('views/rank')

    def post(self):
        self.get()

class CommonHandler(BaseHandler):

    BOOK_INFO_NAME_SITE_EMPTY = 0
    BOOK_INFO_SITE_ERR = 1
    BOOK_INFO_SAVE_ERR = 2
    BOOK_INFO_BOOK_EXISTS = 3
    BOOK_INFO_SAVE_REPEAT = 4
    BOOK_INFO_SAVE_REPEAT = 4

    SITE_INFO_SITE_EMPTY = 0
    SITE_INFO_SAVE_ERR = 2
    SITE_INFO_SAVE_REPEAT = 4

    FIRST_SITES = ['qd', 'cs', 'zh', 'k17']

    def initialize(self):
        BaseHandler.initialize(self);
        self.common_service = CommonService()

    @except_err()
    @auto_login()
    def get(self, method, params=None):
        if not hasattr(self, method) or method in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
            return
        eval("self." + method + "(params)")

    def post(self, method, params=None):
        self.get(method, params)

    def buc(self, params=None):
        book_ids_str = self.get_argument("book_ids", None)
        if self.current_user and book_ids_str and book_ids_str.split(','):
            self.ajax_result(self.book_service.get_update_counts(self.current_user['_id'], book_ids_str.split(',')))
        else:
            self.ajax_result({})

    @except_err()
    @auto_login()
    def bookinfo(self, params=None):
        op = None
        try:
            op = self.list_parms(params)[0]
        except:
            pass
        if not op:
            self.render('views/add_bookinfo')
            return
        if op == 'save':
            book_name = self.get_argument('book_name', None)
            first_site = self.get_argument('first_site', None)
            if not book_name or not first_site:
                self.ajax_result({'succ' : False, 'code' : self.BOOK_INFO_NAME_SITE_EMPTY})
            elif not first_site in self.FIRST_SITES:
                self.ajax_result({'succ' : False, 'code' : self.BOOK_INFO_SITE_ERR})
            else:
                book_info = {'name' : book_name, 'source_short_name' : first_site, 'author' : self.get_argument('author_name', ''), 'source' : self.get_argument('first_url', '')}
                book = self.book_service.find_book_by_info(book_info)
                if book:
                    self.ajax_result({'succ' : False, 'code' : self.BOOK_INFO_BOOK_EXISTS, 'b_id' : book['_id']})
                    return
                r = self.common_service.save_book_info(book_info)
                if r == 1:
                    self.ajax_result({'succ' : True})
                elif r == 0:
                    self.ajax_result({'succ' : False, 'code' : self.BOOK_INFO_SAVE_REPEAT})
                else:
                    self.ajax_result({'succ' : False, 'code' : self.BOOK_INFO_SAVE_ERR})
        else:
            self.raise_http_error(self.URL_NOT_FOUND)

    @except_err()
    @auto_login()
    def siteinfo(self, params=None):
        op = None
        try:
            op = self.list_parms(params)[0]
        except:
            pass
        if not op:
            self.render('views/add_siteinfo')
            return
        if op == 'save':
            site_url = self.get_arguments('site_url', None)
            if not site_url:
                self.ajax_result({'succ' : False, 'code' : self.SITE_INFO_SITE_EMPTY})
            else:
                site_info = {'site_url' : site_url}
                r = self.common_service.save_site_info(site_info)
                if r == 1:
                    self.ajax_result({'succ' : True})
                elif r == 0:
                    self.ajax_result({'succ' : False, 'code' : self.SITE_INFO_SAVE_REPEAT})
                else:
                    self.ajax_result({'succ' : False, 'code' : self.SITE_INFO_SAVE_ERR})
        else:
            self.raise_http_error(self.URL_NOT_FOUND)


class ErrHandler(BaseHandler):

    def get(self, res):
        if res:
            try:
                fns = os.path.dirname(__file__).split(os.sep)[:-1]
                fns.append(res)
                rf = open(os.sep.join(fns))
                self.finish(rf.read())
            except:
                self.raise_http_error(self.URL_NOT_FOUND)
            finally:
                return
        self.raise_http_error(self.URL_NOT_FOUND)

    def post(self, res):
        self.get()

