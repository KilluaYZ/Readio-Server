import inspect
import random

from flask import Blueprint
from flask import request

import readio.database.connectPool
from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
from readio.utils.myExceptions import NetworkException
from readio.utils.executeSQL import execute_sql_query, execute_sql_query_one

# 前缀为app的蓝图
bp = Blueprint('homepage', __name__, url_prefix="/app")

pooldb = readio.database.connectPool.pooldb


def get_sentences():
    get_sql = "select * from sentences"
    sentences = execute_sql_query(pooldb, get_sql, ())
    return sentences


# 从数据库中随机选一些句子
def get_random_sentences(size):
    # count_sql = "select COUNT(*) from sentences"
    # sentences_count = execute_sql_query_one(pooldb, count_sql, ())
    # all_size = sentences_count['COUNT(*)']  # 句子总数
    # # 从 id 序列中随机选取 size 个不重复的 id
    # ids = random.sample(range(1, all_size + 1), size)
    sql = ' select id from sentences '
    ids = execute_sql_query(pooldb, sql)
    ids = list(map(lambda x:x['id'], ids))
    ids = random.sample(ids, size)
    # 将 id 转换成字符串并用逗号拼接
    id_string = ','.join(str(i) for i in ids)
    # 构造 SQL 语句
    # get_random_sql = f"SELECT * FROM sentences WHERE id IN ({id_string})"
    get_random_sql = f"SELECT s.*, b.bookName, b.authorName " \
                     f"FROM sentences s " \
                     f"LEFT JOIN books b ON s.bookId = b.id " \
                     f"WHERE s.id IN ({id_string})"
    sentences = execute_sql_query(pooldb, get_random_sql, ())  # 执行 SQL 语句并返回结果
    return sentences


def rec_random(all_sent, size):
    sentences = list()
    for _ in range(size):
        i = random.randint(0, len(all_sent) - 1)  # 生成随机数
        sent = all_sent[i]
        sent["createTime"] = str(sent["createTime"])
        sentences.append(sent)  # 取出句子并添加到列表中
    return sentences


def rec_sent(all_sent, size, user=None):
    if user is None:
        sentences = rec_random(all_sent, size)
    else:
        sentences = rec_random(all_sent, size)
    return sentences


@bp.route('/homepage', methods=['GET'])
def recommend():
    """ 推荐好句 """
    if request.method == 'GET':
        try:
            size = int(request.headers.get('size', 10))
            user = check_user_before_request(request, raise_exc=False)
            # sentences_all, sentences_rec -> [{},{}]
            # 拿到所有数据然后随机选，性能较差
            # sentences_all = get_sentences()
            # sentences_rec = rec_sent(sentences_all, size, user)
            # 生成随机 id，然后选
            sentences_rec = get_random_sentences(size)
            response = {
                "size": len(sentences_rec),
                "data": sentences_rec
            }
            response = build_success_response(response)
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response
