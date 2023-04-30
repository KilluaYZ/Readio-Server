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
from readio.utils.executeSQL import execute_sql_write, execute_sql_query
from readio.utils.check import check_book_added, check_has_comment

import readio.database.connectPool

# 前缀为 app/book 的蓝图
bp = Blueprint('book_detail', __name__, url_prefix='/app/book')

pooldb = readio.database.connectPool.pooldb


def get_book_details(bid, user=None):
    details, comments_data = {}, {}
    # 书籍信息
    get_book_sql = 'SELECT * FROM books WHERE books.id=%s'
    books = execute_sql_query(pooldb, get_book_sql, bid)
    if len(books) > 0:
        book_info = books[0]
    else:
        raise Exception('查无此书')
    # 评论等信息 (comments_data)
    get_comments_sql = 'SELECT c.* FROM comments AS c, comment_book AS cb ' \
                       'WHERE cb.bookId=%s AND c.commentId=cb.commentId'
    comments = execute_sql_query(pooldb, get_comments_sql, bid)
    # createTime 转为 str
    comments = [comment.update({'createTime': str(comment['createTime'])}) or comment for comment in comments]
    comments_data['size'] = len(comments)
    comments_data['data'] = comments
    # 信息汇总 -> 书籍详情 (details)
    details['book_info'] = book_info
    details['comments'] = comments_data
    details['added'] = False if user is None else check_book_added(pooldb, user['id'], bid)
    return details


def add_comments_sql(uid: int, bid: int, content: str):
    # 修改 comments 表
    add_c_sql = 'insert into comments(userId, content,likes,shares) values(%s,%s,%s,%s)'
    args = uid, content, 0, 0  # tuple
    comment_id = execute_sql_write(pooldb, add_c_sql, args)

    # 修改 comment_book 表
    add_cb_sql = 'insert into comment_book(bookId, commentId) values(%s,%s)'
    args = bid, comment_id
    execute_sql_write(pooldb, add_cb_sql, args)
    return comment_id


def del_comments_sql(uid: int, bid: int, cid: int):
    """
    删除一条评论记录和与之相关的所有关联记录。
    注意： 必须先删除 comment_book 表中的关联记录，再删除 comments 表中的评论记录

    :param uid: 用户 ID。
    :param bid: 书籍 ID。
    :param cid: 评论 ID。

    :return: None
    :raises NetworkException: 当执行 SQL 发生错误时，抛出此异常。
    """
    # 删除 comment_book
    del_cb_sql = "DELETE FROM comment_book WHERE bookId=%s AND commentId=%s"
    cb_args = (bid, cid)
    execute_sql_write(pooldb, del_cb_sql, cb_args)

    # 删除 comment
    del_c_sql = "DELETE FROM comments WHERE userId=%s AND commentId=%s"
    c_args = (uid, cid)
    execute_sql_write(pooldb, del_c_sql, c_args)


@bp.route('/<int:book_id>/comments/add', methods=['POST'])
def add_comments(book_id):
    if request.method == 'POST':
        try:
            user = check_user_before_request(request)
            # print(user)
            uid, bid = user['id'], request.json.get('bookId')
            content = request.json.get('content')
            # 检查 URL 与请求参数 book_id 是否一致
            if str(bid) != str(book_id):
                raise NetworkException(400, 'Invalid book_id')
            # uid bid 其中一个为空
            if not all([uid, bid]):
                raise NetworkException(400, 'userId 或 bookId 缺失')
            cid = add_comments_sql(uid, bid, content)
            url = url_for('book_detail.index', book_id=bid)
            response = build_redirect_response(f'添加评论 {cid} 成功，重定向至书籍详情页', url)
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response


@bp.route('/<int:book_id>/comments/delete', methods=['POST'])
def delete_comments(book_id):
    if request.method == 'POST':
        try:
            user = check_user_before_request(request)
            uid = user['id']
            bid, cid = request.json.get('bookId'), request.json.get('commentId')
            # 检查 URL 与请求参数 book_id 是否一致
            if str(bid) != str(book_id):
                raise NetworkException(400, 'Invalid book_id')
            # 检查评论 ID 是否为空，前面已经保证 uid 和 bid 不为空
            if not cid:
                raise NetworkException(400, 'commentId 缺失')
            # 检查是否有这条评论
            if check_has_comment(pooldb, uid, cid):
                del_comments_sql(uid, bid, cid)  # 数据库中删除该条评论
            else:
                raise NetworkException(400, f'评论 {cid} 不存在或无权删除')
            url = url_for('book_detail.index', book_id=bid)
            response = build_redirect_response(f'删除评论 {cid} 成功，重定向至书籍详情页', url)
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response


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
