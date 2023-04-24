"""
书架页
"""
from flask import Blueprint
from flask import request
from flask import url_for
import inspect
from typing import List, Dict

from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
import readio.database.connectPool
from readio.utils.myExceptions import NetworkException

# 前缀为app的蓝图
bp = Blueprint('bookshelf', __name__, url_prefix='/app/books')

pooldb = readio.database.connectPool.pooldb


def get_books(user_id: int) -> List[Dict[str, str]]:
    """
    获取某个用户已经阅读过的书籍信息列表
    :param user_id: 用户ID
    :return: 包含书籍信息的字典列表，每个字典中包括了书籍的ID、名称、作者等信息
    """
    conn, cursor = pooldb.get_conn()
    # 执行SQL查询，获取用户已经阅读过的所有书籍信息
    cursor.execute("SELECT info.* , books.* "
                   "FROM user_read_info AS info, books "
                   "WHERE userId=%s AND info.bookId=books.id",
                   user_id)
    books = cursor.fetchall()  # 获取查询结果集
    # 关闭数据库连接和游标对象
    pooldb.close_conn(conn, cursor) if conn is not None else None
    return books


def check_added(uid, bid):
    """ 判断用户 uid 的书架是否有书籍 bid """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行SQL查询，判断用户uid和书籍bid是否在表user_read_info中存在
        cursor.execute("SELECT * FROM user_read_info WHERE userId=%s AND bookId=%s",
                       (uid, bid))
        book = cursor.fetchall()  # 获取查询结果集
        return len(book) != 0
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


def add_book_sql(uid, bid, progress):
    """将用户书本阅读信息写入数据库"""
    conn, cursor = pooldb.get_conn()
    try:
        cursor.execute('insert into user_read_info(userId, bookId, progress) values(%s,%s,%s)',
                       (uid, bid, progress))
        conn.commit()
        pooldb.close_conn(conn, cursor)
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


def update_book_sql(uid, bid, progress):
    """ 更新用户书本阅读进度 """
    conn, cursor = pooldb.get_conn()
    try:
        cursor.execute(
            'update user_read_info set progress=%s where userId=%s and bookId=%s',
            (progress, uid, bid))
        conn.commit()
        pooldb.close_conn(conn, cursor)
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


def del_book_sql(uid, bid):
    """将用户书本阅读信息写入数据库"""
    conn, cursor = pooldb.get_conn()
    try:
        cursor.execute('delete from user_read_info where userId=%s and bookId=%s', (uid, bid))
        conn.commit()
        pooldb.close_conn(conn, cursor)
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


@bp.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        try:
            check_user_before_request(request)
            uid = request.json.get('userId')
            bid = request.json.get('bookId')
            progress = request.json.get('progress', 0)

            # uid bid 其中一个为空
            if not all([uid, bid]):
                raise Exception('userId 或 bookId 缺失')

            if check_added(uid, bid):
                raise Exception('该书已加入书架，无需重复加入')
            else:
                # 将书本信息写入数据库
                add_book_sql(uid, bid, progress)
            response = build_redirect_response(f'添加书{bid}，重定向至书架页', url_for('bookshelf.index'))
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response
    # else:
    #     return build_method_error_response(method='POST')


@bp.route('/update', methods=['POST'])
def update():
    """ 更新阅读进度 """
    if request.method == 'POST':
        try:
            check_user_before_request(request)
            uid = request.json.get('userId')
            bid = request.json.get('bookId')
            progress = request.json.get('progress', 0)

            # uid bid 其中一个为空
            if not all([uid, bid]):
                raise Exception('userId 或 bookId 缺失')

            # 书架上已有
            if check_added(uid, bid):
                update_book_sql(uid, bid, progress)
                msg = f'书{bid}更新阅读进度，重定向至书架页'
            else:
                print('书架上没有这本书，已添加')
                add_book_sql(uid, bid, progress)
                msg = f'书架上没有书{bid}，现已添加，重定向至书架页'
            response = build_redirect_response(msg, url_for('bookshelf.index'))
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        # check_user_before_request会抛出NetworkException，这是自定义的Exception，用于构造error_reponse
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        return response
    # else:
    #     return build_method_error_response(method='POST')


@bp.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        try:
            check_user_before_request(request)
            uid = request.json.get('userId')
            bid = request.json.get('bookId')

            # uid bid 其中一个为空
            if not all([uid, bid]):
                raise Exception('userId 或 bookId 缺失')

            # 书架上已有
            if check_added(uid, bid):
                # 数据库中删除书籍信息
                del_book_sql(uid, bid)
            else:
                raise Exception(f'书架上没有书{bid}，无法删除')
            response = build_redirect_response(f'删除书{bid}，重定向至书架页', url_for('bookshelf.index'))
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        return response
    # else:
    #     return build_method_error_response(method='POST')


@bp.route('/list', methods=['GET'])
def index():
    """展示用户书架"""
    # books: [{},{}]
    if request.method == 'GET':
        try:
            user = check_user_before_request(request)
            books = get_books(user['id'])
            # print(type(books[0]), books[0]) if len(books) > 0 else print('get 0 books from user:', books)
            data = {
                "size": len(books),
                "data": books
            }
            response = build_success_response(data)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response()
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        return response
    # else:
    #     return build_method_error_response(method='GET')
