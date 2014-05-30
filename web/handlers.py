# encoding: utf-8
# Created on 2014-5-23
# @author: binge

from web import BaseHandler, auto_login, logout, except_err
from service.book_service import BookService
from utils.common import TimeHelper, _md5, _base64
from service.section_service import SectionService
from service.common_service import CommonService

class MainHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.book_service = BookService()

    @except_err()
    @auto_login()
    def get(self, curr_page=1):
        context = {}
        if self.current_user:
            context['curr_user'] = self.current_user
            context['user_books'] = self.book_service.find_user_books(self.current_user['_id'])
        else:
            user_id = self.get_secure_cookie('user_id')
            if user_id:
                context['user_books'] = self.book_service.find_user_books(user_id)

        context['books_page'] = self.book_service.find_books_page(curr_page)
        context['now_time'] = TimeHelper.time_2_str()
        self.render('views/index', context=context)

    def post(self, curr_page=1):
        self.get(curr_page)

class LoginRegHandler(BaseHandler):

    CODE_NAME_PWD_EMPTY = 0
    CODE_AUTO_REG_SUCC = 1
    CODE_AUTO_REG_FAIL = 2
    CODE_LOGIN_SUCC = 2
    CODE_LOGIN_PWD_ERR = 3

    def initialize(self):
        BaseHandler.initialize(self)

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
                    user_id = user['_id']
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
        self.book_service = BookService()

    @except_err()
    @auto_login()
    def get(self, *args):
        context = {'now_time' : TimeHelper.time_2_str()}
        if self.current_user:
            context['curr_user'] = self.current_user
            context['user_books'] = self.book_service.find_user_books(self.current_user['_id'])
        else:
            user_id = self.get_secure_cookie('user_id')
            if user_id:
                context['user_books'] = self.book_service.find_user_books(user_id)
        self.render("views/shelf", context=context)

    def post(self):
        self.get()

class UserHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.book_service = BookService()

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

    def favo(self, params):
        args = self.list_parms(params, self.URL_NOT_FOUND)
        if not args:
            return
        b_id = args[0]
        if self.current_user:
            user_id = self.current_user['_id']
        else:
            user_id = self.get_secure_cookie('user_id')
        self.ajax_result({'succ' : self.user_service.favo(user_id, b_id)})

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
        self.book_service = BookService()
        self.section_service = SectionService()

    @except_err()
    @auto_login()
    def get(self, _id=None, m=None, params=None):
        if not m:
            self.page(_id, [])
        else:
            if not hasattr(self, m) or m in self._skip_attrs:
                self.raise_http_error(self.URL_NOT_FOUND)
            else:
                eval("self." + m + "(_id, params)")

    def post(self,_id=None, m=None, params=None):
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
        context = {}
        if 'desc' in book:
            book['desc'] = _base64(book['desc'], e=False)
        else:
            book['desc'] = ''
        context['book'] = book
        context['author_books'] = self.book_service.find_author_books(book['author'])
        context['site'] = site
        if len(context['author_books']) == 1:
            context['author_books'] = []
        sections_page = self.section_service.find_sections_page_by_id_site(_id, site, curr_page)
        context['sections_page'] = sections_page
        if self.current_user:
            context['curr_user'] = self.current_user
            self.user_service.clear_user_update_count(self.current_user['_id'], _id)

        self.render('views/book', context=context)

class SearchHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self);
        self.book_service = BookService()

    def get(self):
        self.raise_http_error(self.MTHOD_NOT_ALLOWED)

    @except_err()
    @auto_login()
    def post(self):
        kw = self.get_argument('kw', None)
        if not kw:
            self.redirect('/')
        else:
            books = self.book_service.search(kw)
            context = {'books' : books, 'kw' : kw, 'now_time' : TimeHelper.time_2_str()}
            if self.current_user:
                context['curr_user'] = self.current_user
            self.render('views/search', context=context)

class CommonHandler(BaseHandler):

    BOOK_INFO_NAME_SITE_EMPTY = 0;
    BOOK_INFO_SITE_ERR = 1
    BOOK_INFO_SAVE_ERR = 2
    BOOK_INFO_BOOK_EXISTS = 3
    BOOK_INFO_SAVE_REPEAT = 4

    FIRST_SITES = ['qd', 'cs', 'zh', 'k17']

    def initialize(self):
        BaseHandler.initialize(self);
        self.book_service = BookService()
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

    def bookinfo(self, params=None):
        op = None
        try:
            op = self.list_parms(params)[0]
        except:
            pass
        if op:
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
        else:
            self.render('views/add_bookinfo')

class ErrHandler(BaseHandler):

    def get(self):
        self.raise_http_error(self.URL_NOT_FOUND)

    def post(self):
        self.get()
