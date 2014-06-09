# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import pymongo
from utils.settings import *  # @UnusedWildImport
import traceback
import redis

class MongoHelper():

    @staticmethod
    def get_mongo():
        return pymongo.Connection(mongo_host, mongo_port)

    @staticmethod
    def close_mongo(mongo):
        if mongo:
            mongo.close()

def mongo_exec(mongo):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(mongo = mongo, *args, **kwargs)
            except:
                raise Exception(traceback.format_exc())
            finally:
                MongoHelper.close_mongo(mongo)
        return _exec
    return wrapper

class RedisHelper():

    @staticmethod
    def get_redis_conn(db=redis_def_db):
        return redis.Redis(host=redis_host, port=redis_port, db=db)

    @staticmethod
    def close_redis_conn(rconn):
        if rconn:
            del rconn

def redis_exec(rconn):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(rconn = rconn, *args, **kwargs)
            except:
                raise Exception(traceback.format_exc())
            finally:
                RedisHelper.close_redis_conn(rconn)
        return _exec
    return wrapper
