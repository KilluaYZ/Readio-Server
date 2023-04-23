"""
文件管理层，用于向上层提供透明的图片、书籍、二创等大文件的存储服务
"""

import functools
import struct

from flask import request
from flask import Blueprint
from flask import redirect
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from readio.utils.buildResponse import *
from readio.utils.auth import *
import readio.database.connectPool
import readio.utils.check as check

# appAuth = Blueprint('/auth/app', __name__)
bp = Blueprint('file', __name__, url_prefix='/file')

pooldb = readio.database.connectPool.pooldb


def getFileInfoById(id:str) -> dict:
    """
    通过id唯一地找到对应的文件信息
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where id=%s',(id))
        row = cursor.fetchone()
        return row

    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def getFilesInfoByNameExact(name: str) -> list:
    """
    通过文件名，找到文件名完全匹配的文件信息列表
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where name=%s', (name))
        row = cursor.fetchone()
        return row

    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)

def getFilesInfoByNameFuzzy(name: str) -> list:
    """
    通过文件名，找到文件名模糊匹配的文件信息列表
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where name LIKE %s', (f'%{name}%'))
        row = cursor.fetchone()
        return row

    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)

def loadFileByte(fileInfo:dict):
    """
    fileInfo中要求存在id、type和path，函数会读入<path>/<id>.<type>的文件
    例如: path = /home  id = 123  type = jpg
    /home/123.jpg
    返回的是byte
    """
    try:
        if 'id' not in fileInfo or 'path' not in fileInfo or 'type' not in fileInfo:
            raise Exception('待读取fileInfo缺少path、type或id')
        content = None
        with open(f"{os.path.join(fileInfo['path'],fileInfo['id'])}.{fileInfo['type']}", "rb") as f:
               content = f.read()
        return content

    except Exception as e:
        check.printException(e)

def loadFileClass(fileInfo:dict):
    """
    fileInfo中要求存在id、type和path，函数会读入<path>/<id>.<type>的文件
    例如: path = /home  id = 123  type = jpg
    /home/123.jpg
    返回的是一个class
    """
    try:
        content = loadFileByte(fileInfo)
        content = struct.unpack("<4H2I", content)
        return content

    except Exception as e:
        check.printException(e)

def saveFileByte(fileInfo:dict, content):
    try:
        if 'id' not in fileInfo or 'path' not in fileInfo or 'type' not in fileInfo:
            raise Exception('待写入fileInfo缺少path、type或id')
        content = None
        with open(f"{os.path.join(fileInfo['path'], fileInfo['id'])}.{fileInfo['type']}", "wb") as f:
            f.write(content)

    except Exception as e:
        check.printException(e)

def saveFileClass(fileInfo:dict, content):
    try:
        content = struct.pack("<4H2I",*content)
        saveFileByte(content)
    except Exception as e:
        check.printException(e)

def getFilesByName():
    """
    通过Name获取文件
    """
    pass

def getFileById():
    """
    通过id拿到文件
    """
    pass

def saveFile():
    """
    储存文件
    """
    pass



