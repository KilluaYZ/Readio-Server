"""
书籍阅读页
返回文字内容
点击书架上的书，获取数据库中上次读取的地方，以字为单位，返回书籍全部内容和偏移量
"""
from flask import Blueprint
from flask import request
from flask import url_for
import inspect
from typing import List, Dict, Optional

import readio.database.connectPool
from readio.utils.buildResponse import *
from readio.utils.auth import check_user_before_request
from readio.utils.check import check_book_added
from readio.utils.myExceptions import NetworkException
from readio.utils.executeSQL import execute_sql_write, execute_sql_query
from readio.utils.filechange import FileChangeSys
from readio.mainpage.appBookDetailsPage import get_book_info_sql
from readio.manage.fileManage import getFilePathById

# 前缀为 app/books/reading 的蓝图
bp = Blueprint('book_reading', __name__, url_prefix='/app/books/reading')

pooldb = readio.database.connectPool.pooldb


# 根据文件路径获取内容
def get_file_content(path):
    file = FileChangeSys(path)
    print(path)
    print(file)
    text = file.Chapter_uniform
    print(text)
    return None


def get_book_content(bid, user=None):
    data = {}
    book_info = get_book_info_sql(bid)
    book_hash = book_info['sha256']
    print(book_hash)
    book_path = getFilePathById(book_hash)  # 根据 hash 获取文件路径
    content = get_file_content(book_path)  # 根据文件路径获取内容
    # 构建返回的数据
    data['id'] = book_info['id']
    data['bookName'] = book_info['bookName']
    data['authorName'] = book_info['authorName']
    data['abstract'] = book_info['abstract']
    data['content'] = content
    return data


@bp.route('/<int:book_id>', methods=['GET'])
def index(book_id):
    if request.method == 'GET':
        try:
            # 检查是否有用户 token ，有返回用户，否则返回 None
            user = check_user_before_request(request, raise_exc=False)
            book_content = get_book_content(book_id, user)
            data = book_content
            response = build_success_response(data)
        except NetworkException as e:
            response = build_error_response(code=e.code, msg=e.msg)
        except Exception as e:
            print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
            print(e)
            response = build_error_response(msg=str(e))
        return response
