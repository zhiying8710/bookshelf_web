# encoding: utf-8
# Created on 2014-5-26
# @author: binge

from utils.conns_helper import mongo_exec, MongoHelper, redis_exec, RedisHelper
from utils import settings

class BookService():

    def gene_book_page(self, page_size, total, curr_page, books_cursor):
        if not total:
            total_page = 1
            curr_page = 1
        else:
            total_page = (total / page_size) if not total % page_size else (total / page_size + 1)
        books = []
        for book in books_cursor:
            books.append(book)
        return {'total' : total, 'page_size' : page_size, 'total_page' : total_page, 'curr_page' : curr_page, 'books' : books}

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_user_books_page(self, user_id, curr_page=None, mongo=None):
        if not curr_page or int(curr_page) < 1:
            curr_page = 1
        else:
            curr_page = int(curr_page)
        db = mongo.bookshelf
        user_favos = db.user_favos.find_one({'_id' : user_id})
        if user_favos and user_favos['b_ids']:
            b_ids = user_favos['b_ids']
            return self.gene_book_page(settings.user_books_page_size, len(b_ids) / settings.user_books_page_size, curr_page, \
                                       db.books.find({'_id': {'$in' : b_ids}}).sort([('update_time', -1)]).skip((curr_page - 1) * settings.user_books_page_size).limit(settings.user_books_page_size))
        else:
            return self.gene_book_page(settings.user_books_page_size, 1, 1, [])

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_user_books(self, user_id, mongo=None):
        db = mongo.bookshelf
        user_favos = db.user_favos.find_one({'_id' : user_id})
        if user_favos and user_favos['b_ids']:
            b_ids = user_favos['b_ids']
            return self.gene_book_page(1, 0, 0, db.books.find({'_id': {'$in' : b_ids}}).sort([('update_time', -1)]))['books']
        else:
            return []

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_books_page(self, curr_page=None, mongo=None):
        if not curr_page or int(curr_page) < 1:
            curr_page = 1
        else:
            curr_page = int(curr_page)
        db = mongo.bookshelf
        total = db.books.count()
        if curr_page > settings.max_all_books_page:
            curr_page = settings.max_all_books_page
        if total > settings.max_all_books_page * settings.all_books_page_size:
            total = settings.max_all_books_page * settings.all_books_page_size

        return self.gene_book_page(settings.all_books_page_size, total, curr_page, \
                                   db.books.find().sort([('update_time', -1)]).skip((curr_page - 1) * settings.all_books_page_size).limit(settings.all_books_page_size))

    @redis_exec(rconn=RedisHelper.get_redis_conn())
    def get_update_counts(self, user_id, book_ids, rconn=None):
        key = settings.user_favos_update_counts_key_prefix + user_id
        counts = {}
        for book_id in book_ids:
            count = rconn.hget(key, book_id)
            if count and count > 0:
                counts[book_id] = count
        return counts

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_book_by_id(self, b_id, mongo=None):
        return mongo.bookshelf.books.find_one({'_id' : b_id})

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_author_books(self, author, mongo=None):
        if not author:
            return []
        books_cursor = mongo.bookshelf.books.find({'author' : author})
        books = []
        for book in books_cursor:
            books.append(book)
        return books

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def search(self, kw, mongo=None):
        books_cursor = mongo.bookshelf.books.find({'$or' : [{'name' : {'$regex' : kw}}, {'author' : {'$regex' : kw}}]})
        return self.gene_book_page(1, 0, 0, books_cursor)['books']

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_book_by_info(self, book_info, mongo=None):
        author = book_info['author']
        source = book_info['source']
        conditions = {'name' : book_info['name'], 'source_short_name' : book_info['source_short_name']}
        if author:
            conditions['author'] = author
        if source:
            conditions['source'] = source
        return mongo.bookshelf.books.find_one(conditions)
