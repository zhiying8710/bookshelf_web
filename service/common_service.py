# encoding: utf-8
# Created on 2014-5-30
# @author: binge
from utils.conns_helper import redis_exec, RedisHelper
from utils import settings

class CommonService():

    @redis_exec(rconn=RedisHelper.get_redis_conn())
    def save_book_info(self, book_info, rconn=None):
        return rconn.sadd(settings.unrecord_book_info_queue_key, book_info)
