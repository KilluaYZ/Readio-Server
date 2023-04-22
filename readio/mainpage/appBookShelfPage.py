from flask import Blueprint
from flask import request
from flask import url_for
import inspect
from typing import List, Dict

from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
import readio.database.connectPool

# 前缀为app的蓝图
bp = Blueprint('bookshelf', __name__, url_prefix='/app/books')

pooldb = readio.database.connectPool.pooldb


# TODO:
#  先获取用户信息，然后获取数据库中用户书架上的书，返回书籍信息（GET）；如果添加书籍，写入数据库（POST）
#  之后是阅读详情页，点击书架上的书，获取数据库中上次读取的地方，以字为单位，返回书籍全部内容和偏移量
#  考虑：设计新的页面，点击进去，展示书的详情信息（收藏、评论等）


def get_books(user_id: int) -> List[Dict[str, str]]:
    """
    获取某个用户已经阅读过的书籍信息列表
    :param user_id: 用户ID
    :return: 包含书籍信息的字典列表，每个字典中包括了书籍的ID、名称、作者等信息
    """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行SQL查询，获取用户已经阅读过的所有书籍信息
        cursor.execute("SELECT * FROM user_read_info, books WHERE userId=%s AND user_read_info.bookId=books.id",
                       user_id)
        books = cursor.fetchall()  # 获取查询结果集
        return books
    except Exception as e:
        # 如果出现异常，打印错误信息，并返回None表示获取失败
        print("[ERROR] Can't get books." + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        return []
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


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
        check_user_before_request(request)
        uid = request.json.get('userId')
        bid = request.json.get('bookId')
        progress = request.json.get('progress', 0)

        # uid bid 其中一个为空
        if not all([uid, bid]):
            raise Exception('userId and bookId are required for adding books.')

        if check_added(uid, bid):
            print('该书已加入书架，无需重复加入')
        else:
            # 将书本信息写入数据库
            add_book_sql(uid, bid, progress)
        response = build_redirect_response(f'添加书{bid}，重定向至书架页', url_for('bookshelf.index'))
        return response


@bp.route('/update', methods=['POST'])
def update():
    """ 更新阅读进度 """
    if request.method == 'POST':
        check_user_before_request(request)
        uid = request.json.get('userId')
        bid = request.json.get('bookId')
        progress = request.json.get('progress', 0)

        # uid bid 其中一个为空
        if not all([uid, bid]):
            raise Exception('userId and bookId are required for updating progress.')

        # 书架上已有
        if check_added(uid, bid):
            update_book_sql(uid, bid, progress)
        else:
            print('书架上没有这本书，已添加')
            add_book_sql(uid, bid, progress)
        response = build_redirect_response(f'书{bid}更新阅读进度，重定向至书架页', url_for('bookshelf.index'))
        return response


@bp.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        check_user_before_request(request)
        uid = request.json.get('userId')
        bid = request.json.get('bookId')

        # uid bid 其中一个为空
        if not all([uid, bid]):
            raise Exception('userId and bookId are required for deleting books.')

        # 书架上已有
        if check_added(uid, bid):
            # 数据库中删除书籍信息
            del_book_sql(uid, bid)
        else:
            raise Exception('书架上没有这本书，无法删除')
        response = build_redirect_response(f'删除书{bid}，重定向至书架页', url_for('bookshelf.index'))
        return response


@bp.route('/list', methods=['GET'])
def index():
    """展示用户书架"""
    # books: [{},{}]
    if request.method == 'GET':
        user = check_user_before_request(request)
        books = get_books(user['id'])
        # print(type(books[0]), books[0]) if len(books) > 0 else print('get 0 books from user:', books)
        data = {
            "size": len(books),
            "data": books
        }
        response = build_success_response(data)
        return response
