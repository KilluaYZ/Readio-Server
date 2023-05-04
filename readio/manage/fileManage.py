"""
文件管理层，用于向上层提供透明的图片、书籍、二创等大文件的存储服务
"""
import base64
import functools
import platform
import struct
import sys
from typing import BinaryIO

from flask import request
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import send_file
from werkzeug.security import check_password_hash, generate_password_hash
from readio.utils.buildResponse import *
from readio.utils.auth import *
import readio.database.connectPool
import readio.utils.check as check

# appAuth = Blueprint('/auth/app', __name__)
bp = Blueprint('file', __name__, url_prefix='/file')

pooldb = readio.database.connectPool.pooldb

BASE_FILE_STORE_DIR = './readio_server_runtime_data'
PICTURE_TYPES = ['jpeg', 'jpg', 'png', 'tif', 'gif', 'bmp', 'svg']
BOOK_TYPES = ['txt', 'pdf', 'mobi', 'epub']


def __getFileInfoById(id: str) -> dict:
    """
    通过id唯一地找到对应的文件信息
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where fileId=%s', (id))
        row = cursor.fetchone()
        return row
    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def __getFilesInfoByNameExact(name: str) -> list:
    """
    通过文件名，找到文件名完全匹配的文件信息列表
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where fileName=%s', (name))
        row = cursor.fetchone()
        return row

    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def __getFilesInfoByNameFuzzy(name: str) -> list:
    """
    通过文件名，找到文件名模糊匹配的文件信息列表
    """
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from file_info where fileName LIKE %s', (f'%{name}%'))
        row = cursor.fetchone()
        return row

    except Exception as e:
        check.printException(e)

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def __loadFileByte(fileInfo: dict):
    """
    fileInfo中要求存在id、type和path，函数会读入<path>/<id>.<type>的文件
    例如: path = /home  id = 123  type = jpg
    /home/123.jpg
    返回的是byte
    """
    if 'fileId' not in fileInfo or 'filePath' not in fileInfo or 'fileType' not in fileInfo:
        raise Exception('待读取fileInfo缺少path、type或id')
    with open(
            f"{os.path.join(BASE_FILE_STORE_DIR, os.path.join(fileInfo['filePath'], fileInfo['fileId']))}.{fileInfo['fileType']}",
            "rb") as f:
        content = f.read()
    return content


def __loadFileClass(fileInfo: dict) -> bytes:
    """
    fileInfo中要求存在id、type和path，函数会读入<path>/<id>.<type>的文件
    例如: path = /home  id = 123  type = jpg
    /home/123.jpg
    返回的是一个class
    """
    content = __loadFileByte(fileInfo)
    content = struct.unpack("<4H2I", content)
    return content


def __loadFileHandle(fileInfo: dict) -> BinaryIO:
    """
    通过fileInfo获取文件句柄
    """
    if 'fileId' not in fileInfo or 'filePath' not in fileInfo or 'fileType' not in fileInfo:
        raise Exception('待读取fileInfo缺少path、type或id')
    fileHandler = open(
        f"{os.path.join(BASE_FILE_STORE_DIR, os.path.join(fileInfo['filePath'], fileInfo['fileId']))}.{fileInfo['fileType']}",
        "rb")
    return fileHandler


def __rmFile(fileInfo: dict):
    """
        通过fileInfo删除文件
    """
    os.remove(
        f"{os.path.join(BASE_FILE_STORE_DIR, os.path.join(fileInfo['filePath'], fileInfo['fileId']))}.{fileInfo['fileType']}")


def getFilesByteByNameExact(name: str) -> list:
    """
    通过Name获取文件二进制（精确的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameExact(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileByte(fileInfo))
    return res


def getFilesByteByNameFuzzy(name: str) -> list:
    """
    通过Name获取文件二进制（模糊的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameFuzzy(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileByte(fileInfo))
    return res


def getFilesHandlerByNameExact(name: str) -> list:
    """
    通过Name获取文件句柄（精确的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameExact(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileHandle(fileInfo))
    return res


def getFilesHandlerByNameFuzzy(name: str) -> list:
    """
    通过Name获取文件句柄（模糊的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameFuzzy(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileHandle(fileInfo))
    return res


def getClassFileByNameExact(name: str) -> list:
    """
    通过Name获取二进制文件并将其转化为class（精确的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameExact(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileClass(fileInfo))
    return res


def getClassFileByNameFuzzy(name: str) -> list:
    """
    通过Name获取二进制文件并将其转化为class（模糊的）
    """
    res = []
    fileInfoList = __getFilesInfoByNameFuzzy(name)
    for fileInfo in fileInfoList:
        res.append(__loadFileClass(fileInfo))
    return res


def getFileHandlerById(fileId: str) -> BinaryIO:
    """
    通过id拿到文件句柄
    """
    fileInfo = __getFileInfoById(fileId)
    return __loadFileHandle(fileInfo)


def getFileByteById(fileId: str):
    """
    通过id拿到文件二进制
    """
    fileInfo = __getFileInfoById(fileId)
    return __loadFileByte(fileInfo)


def getClassFileByteById(fileId: str) -> bytes:
    """
    通过id拿到文件二进制并转化为class
    """
    fileInfo = __getFileInfoById(fileId)
    return __loadFileClass(fileInfo)


def saveFileFromByte(fileInfo: dict, content):
    if 'fileId' not in fileInfo or 'filePath' not in fileInfo or 'fileType' not in fileInfo:
        raise Exception('待写入fileInfo缺少path、type或id')
    dir_abs_path = os.path.join(BASE_FILE_STORE_DIR, fileInfo['filePath'])
    # dir_abs_path = BASE_FILE_STORE_DIR + '/' + fileInfo['filePath']
    if not os.path.exists(dir_abs_path):
        os.makedirs(dir_abs_path)
    with open(f"{os.path.join(dir_abs_path, fileInfo['fileId'])}.{fileInfo['fileType']}",
              "wb") as f:
        f.write(content)


def saveFileFromClass(fileInfo: dict, content):
    content = struct.pack("<4H2I", *content)
    saveFileFromByte(fileInfo, content)


@bp.route('/downloadBinary', methods=['GET'])
def downloadFileBinary():
    try:
        data = request.args
        if 'fileId' in data and 'fileName' in data:
            return build_error_response(code=400, msg='不能同时指定文件Id和Name')

        elif 'fileId' in data:
            fileId = data['fileId']
            fileInfo = __getFileInfoById(fileId)
            print("fileInfo = ", fileInfo)
            fileContent = getFileByteById(fileId)

            response = {
                "fileId": fileInfo['fileId'],
                "fileName": fileInfo['fileName'],
                "fileType": fileInfo['fileType'],
                # "fileContent": f'data:image/{fileInfo["fileType"]};base64,{str(base64.b64encode(fileContent))}'
                "fileContent": str(base64.b64encode(fileContent))
            }
            return build_success_response(data=response, msg='获取成功')

        elif 'fileName' in data:
            fileName = data['fileName']
            if 'mode' in data and data['mode'] == 'exact':
                fileInfoList = __getFilesInfoByNameExact(fileName)
            else:
                fileInfoList = __getFilesInfoByNameFuzzy(fileName)

            response = []
            for fileInfo in fileInfoList:
                fileContent = getFileByteById(fileInfo)
                singleFileResponse = {
                    "fileId": fileInfo['fileId'],
                    "fileName": fileInfo['fileName'],
                    "fileType": fileInfo['fileType'],
                    "fileContent": base64.b64encode(fileContent)
                }
                response.append(singleFileResponse)

            return build_success_response(data=response, msg='获取成功')

        else:
            return build_error_response(code=404, msg='资源不存在')

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误，无法获取该资源')


@bp.route('/getFileBinaryById', methods=['GET'])
def get_file_binary_by_id():
    try:
        data = request.args
        if 'fileId' not in data:
            raise NetworkException(code=400, msg='不能同时指定文件Id和Name')

        fileId = data['fileId']
        fileInfo = __getFileInfoById(fileId)
        if fileInfo is None:
            raise NetworkException(code=404, msg='资源不存在')
        print("fileInfo = ", fileInfo)
        fileContentHandle = getFileHandlerById(fileId)
        if fileContentHandle is None:
            raise Exception("无法获取该文件的二进制数据")

        # response = {
        #     "fileId": fileInfo['fileId'],
        #     "fileName": fileInfo['fileName'],
        #     "fileType": fileInfo['fileType'],
        #     "fileContent": f'data:image/{fileInfo["fileType"]};base64,{str(base64.b64encode(fileContent))}'
        # }
        # return build_success_response(data=response, msg='获取成功')
        return send_file(fileContentHandle, fileInfo['fileType'],
                         download_name=f"{fileInfo['fileName']}.{fileInfo['fileType']}")

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误，无法获取该资源')


def uploadFileBinarySql(fileInfo: dict):
    try:
        conn, cursor = pooldb.get_conn()
        fileType = fileInfo['fileType'].lower()
        fileInfo['fileType'] = fileInfo['fileType'].lower()
        fileName = fileInfo['fileName']
        fileContent = base64.b64decode(fileInfo['fileContent'])
        hashObj = hashlib.sha256()
        hashObj.update(fileContent)
        fileInfo['fileId'] = hashObj.hexdigest()

        if 'filePath' not in fileInfo:
            if fileType in PICTURE_TYPES:
                filePath = 'pic'
            elif fileType in BOOK_TYPES:
                filePath = 'book'
            else:
                filePath = 'default'
            fileInfo['filePath'] = filePath

        saveFileFromByte(fileInfo, fileContent)

        cursor.execute('insert into file_info(fileId,fileName,fileType,filePath) values(%s,%s,%s,%s)',
                       (fileInfo['fileId'], fileName, fileType, fileInfo['filePath']))
        conn.commit()
        pooldb.close_conn(conn, cursor)

    except Exception as e:
        if conn is not None:
            pooldb.close_conn(conn, cursor)
        raise e


@bp.route('/uploadBinary', methods=['POST'])
def uploadFileBinary():
    try:
        data = request.json
        # print(f'[DEBUG] {data}')
        if 'fileName' not in data or 'fileType' not in data or 'fileContent' not in data:
            return build_error_response(400, '上传错误，fileName,fileType,fileContent信息不全')

        print(f'[DEBUG] fileContent = {data["fileContent"][:50]}')

        uploadFileBinarySql(data)

        return build_success_response()

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误，无法获取该资源')


def delFileSql(fileInfo: dict):
    try:
        conn, cursor = pooldb.get_conn()

        __rmFile(fileInfo)

        cursor.execute('delete from file_info where fileId = %s',
                       (fileInfo['fileId']))
        conn.commit()
        pooldb.close_conn(conn, cursor)

    except Exception as e:
        if conn is not None:
            pooldb.close_conn(conn, cursor)
        raise e


@bp.route('/delete', methods=['GET'])
def deleteFile():
    try:
        data = request.args
        if 'fileId' not in data:
            return build_error_response(400, '上传错误，fileName,fileType,fileContent信息不全')

        fileInfo = getFileByteById(data['fileId'])
        __rmFile(fileInfo)

        return build_success_response()

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误，无法获取该资源')


def __get_res_info_by_type_sql(type=None):
    try:
        conn, cursor = pooldb.get_conn()
        if type is None:
            cursor.execute('select * from file_info')

        else:
            cursor.execute('select * from file_info where fileType = %s', type)

        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def __query_res_info_sql(query_param: dict) -> list:
    try:
        conn, cursor = pooldb.get_conn()
        sql = f'select * from file_info'
        arg_list = []
        if 'fileName' in query_param or 'fileType' in query_param:
            sql = sql + ' where 1=1 '
            if 'fileName' in query_param:
                sql += f' and fileName like %s'
                arg_list.append(f'%{query_param["fileName"]}%')
            if 'fileType' in query_param:
                sql += f' and fileType=%s'
                arg_list.append(query_param['fileType'])
        if 'sortMode' in query_param:
            if query_param['sortMode'] == 'Old':
                sql += ' order by createTime asc '
            else:
                sql += ' order by createTime desc '
        else:
            sql += ' order by createTime desc '

        cursor.execute(sql, tuple(arg_list))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/getResInfo', methods=['GET'])
def getResInfo():
    try:

        fileName = request.args.get('fileName')
        fileType = request.args.get('fileType')
        sortMode = request.args.get('sortMode')
        query_param = {}
        if fileName is not None:
            query_param['fileName'] = fileName
        if fileType is not None:
            query_param['fileType'] = fileType
        if sortMode is not None:
            query_param['sortMode'] = sortMode

        rows = __query_res_info_sql(query_param)
        length = len(rows)
        # 如果前端传来了pageSize和pageNum则说明需要分页
        pageSize = request.args.get('pageSize')
        pageNum = request.args.get('pageNum')
        if pageNum is not None and pageSize is not None:
            pageSize = int(pageSize)
            pageNum = int(pageNum)
            rows = rows[(pageNum - 1) * pageSize:pageNum * pageSize]

        for i in range(len(rows)):
            rows[i]['createTime'] = rows[i]['createTime'].strftime('%Y-%m-%d %H:%M:%S')
            rows[i]['visitTime'] = rows[i]['visitTime'].strftime('%Y-%m-%d %H:%M:%S')

        return build_success_response(data=rows, length=length)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误，无法获取该资源')
