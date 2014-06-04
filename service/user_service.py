# encoding: utf-8
# Created on 2014-5-23
# @author: binge

from utils.conns_helper import mongo_exec, MongoHelper, redis_exec, RedisHelper
import time
from utils.common import _md5
from utils import settings

class UserService():

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_by_name(self, user_name, mongo=None):
        return mongo.bookshelf.users.find_one({'user_name' : user_name})

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_by_id(self, user_id, mongo=None):
        return mongo.bookshelf.users.find_one({'_id' : user_id})

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def auto_reg_user(self, user_name, pass_word, user_id=None, mongo=None, is_cookie=False):
        if not user_id:
            user_id = _md5(user_name + pass_word + str(time.time()))
            mongo.bookshelf.users.insert({'_id' : user_id, 'user_name' : user_name, 'pass_word' : _md5(pass_word), 'is_cookie' : is_cookie})
        else:
            mongo.bookshelf.users.update({'_id' : user_id}, {'$set' : {'user_name' : user_name, 'pass_word' : _md5(pass_word), 'is_cookie' : is_cookie}})
        return mongo.bookshelf.users.find_one({'_id' : user_id})

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_by_name_pwd(self, user_name, pass_word, mongo=None):
        return mongo.bookshelf.users.find_one({'user_name' : user_name, 'pass_word' : _md5(pass_word)})

    @redis_exec(rconn=RedisHelper.get_redis_conn())
    def clear_user_update_count(self, user_id, b_id, rconn=None):
        rconn.hdel(settings.user_favos_update_counts_key_prefix + user_id, b_id)

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def favo(self, user_id, b_id, mongo=None):
        if not user_id:
            user = self.auto_reg_user('', '', is_cookie=True)
        else:
            user = self.find_by_id(user_id)
        if not user:
            return False
        user_favos = mongo.bookshelf.user_favos.find_one({'_id' : user_id})
        if user_favos:
            mongo.bookshelf.user_favos.update({'_id' : user_id}, {'$addToSet' : {'b_ids' : b_id}})
        else:
            mongo.bookshelf.user_favos.insert({'_id' : user_id, 'b_ids' : [b_id]})
        return True

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def unfavo(self, user_id, b_ids, mongo=None):
        mongo.bookshelf.user_favos.update({'_id' : user_id}, {'$pull' : {'b_ids' : {'$in' : b_ids}}})
        return True

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def unfavoall(self, user_id, mongo=None):
        mongo.bookshelf.user_favos.remove({'_id' : user_id})
        return True

    @mongo_exec(mongo=MongoHelper.get_mongo())
    def append_favos_from_cookie_uid(self, user_id, cookie_user_id, mongo=None):
        db = mongo.bookshelf.user_favos
        cookie_user_favos = db.find_one({'_id' : cookie_user_id})
        if cookie_user_favos and cookie_user_favos['b_ids']:
            db.update({'_id' : user_id}, {'$addToSet' : {'b_ids' : {'$each' : cookie_user_favos['b_ids']}}})
        db.remove({'_id' : cookie_user_id})
