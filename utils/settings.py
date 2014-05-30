# encoding: utf-8
# Created on 2014-5-23
# @author: binge

mongo_host = '127.0.0.1'
mongo_port = 27017

redis_host = '127.0.0.1'
redis_port = 6379
redis_def_db = 0
redis_sep = ':::'

user_books_page_size = 20
all_books_page_size = 50
max_all_books_page = 20
book_sections_size = 50

user_favos_update_counts_key_prefix = '__user_favos_update_counts_'
unrecord_book_info_queue_key = '__unrecord_book_info_queue'

SESSION_MAXLIFETIME = 30 * 60
SESSION_REDIS_DB = 1
