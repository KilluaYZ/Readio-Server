from flask import Blueprint
from readio.utils.buildResponse import *
import readio.database.connectPool

# 前缀为app的蓝图
bp = Blueprint('homepage', __name__, url_prefix="/app")

pooldb = readio.database.connectPool.pooldb


def get_sentences():
    conn, cursor = pooldb.get_conn()
    try:
        cursor.execute("select * "
                       "from sentences")
        sentences = cursor.fetchall()
    except:
        print("ERROR! Can't get sentences.")
        return None
    else:
        return sentences
    finally:
        pooldb.close_conn(conn, cursor) if conn is not None else None


def choose(all_sent, size=1):
    sentences = list()
    for i in range(size):
        sent = all_sent[i]
        sent["createTime"] = str(sent["createTime"])
        sentences.append(sent)
    # sentences = [for i in range(size)]
    return sentences


@bp.route('/homepage', methods=['GET'])
def recommend():
    """推荐好句"""
    # sentences_all: [{},{}]
    sentences_all = get_sentences()
    # print(type(sentences_all[0]), sentences_all[0])
    # sentences_rec: [{},{}]
    sentences_rec = choose(sentences_all, size=1)
    # print(type(sentences_rec), sentences_rec)
    response = {
        "length": len(sentences_rec),
        "data": sentences_rec
    }
    # response = build_raw_response(response)
    response = build_success_response(response)
    # print(type(response), response)
    return response
