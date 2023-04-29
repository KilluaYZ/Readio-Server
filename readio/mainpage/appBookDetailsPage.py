"""
书籍详情页
返回收藏、评论等信息，标志是否已加入书架
"""

from flask import Blueprint
from flask import request
from flask import url_for
import inspect
from typing import List, Dict

from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
from readio.utils.myExceptions import NetworkException
from readio.utils.buildSQL import execute_sql_write, execute_sql_query
from readio.utils.check import check_book_added

import readio.database.connectPool

# 前缀为 app/book 的蓝图
bp = Blueprint('book_detail', __name__, url_prefix='/app/book')

pooldb = readio.database.connectPool.pooldb


def get_book_details(bid, user=None):
    details = {}
    # 书籍信息
    get_book_sql = 'SELECT * FROM books WHERE books.id=%s'
    books = execute_sql_query(pooldb, get_book_sql, bid)
    if len(books) > 0:
        book_info = books[0]
    else:
        raise Exception('查无此书')
    # 评论等信息
    comments_data = {}
    get_comments_sql = 'SELECT c.* ' \
                       'FROM comments AS c, comment_book AS cb ' \
                       'WHERE cb.bookId=%s AND c.commentId=cb.commentId'
    comments = execute_sql_query(pooldb, get_comments_sql, bid)
    comments_data['size'] = len(comments)
    comments_data['data'] = comments
    # 信息汇总，书籍详情
    details['book_info'] = book_info
    details['comments'] = comments_data
    if user is None:
        details['added'] = False
    else:
        details['added'] = check_book_added(pooldb, user['id'], bid)
    return details


@bp.route('/<int:book_id>', methods=['GET'])
def index(book_id):
    if request.method == 'GET':
        try:
            # 检查是否有用户 token ，有返回用户，否则返回 None
            user = check_user_before_request(request, raise_exc=False)
            details = get_book_details(book_id, user)
            data = details
            response = build_success_response(data)
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response
