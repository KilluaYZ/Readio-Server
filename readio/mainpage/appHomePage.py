import inspect
import random

from flask import Blueprint
from flask import request

import readio.database.connectPool
from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
from readio.utils.myExceptions import NetworkException
from readio.utils.executeSQL import execute_sql_query

# 前缀为app的蓝图
bp = Blueprint('homepage', __name__, url_prefix="/app")

pooldb = readio.database.connectPool.pooldb


def get_sentences():
    get_sql = "select * from sentences"
    sentences = execute_sql_query(pooldb, get_sql, ())
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
            sentences_all = get_sentences()
            sentences_rec = rec_sent(sentences_all, size, user)
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
