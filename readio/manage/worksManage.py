"""
二创管理
"""
import functools
from typing import List

from flask import request
from flask import Blueprint
from flask import redirect
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from readio.utils.buildResponse import *
from readio.utils.auth import *
import readio.database.connectPool
import readio.utils.check as check
from readio.utils.myExceptions import *
from readio.utils.executeSQL import *

# appAuth = Blueprint('/auth/app', __name__)
bp = Blueprint('worksManage', __name__, url_prefix='/works')

pooldb = readio.database.connectPool.pooldb


def random_get_pieces_brief_sql(size: int) -> list:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select piecesId, seriesId, title, userId, state, content, likes, views, shares from pieces')
        rows = cursor.fetchall()
        # 随机从列表中抽取size个元素
        if size > len(rows):
            size = len(rows)
        res = random.sample(rows, size)
        return res

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def get_tags_by_seriesId_sql(seriesId: int) -> list:
    try:
        # print(f'[DEBUG] seriesId = {seriesId} type = {type(seriesId)}')
        conn, cursor = pooldb.get_conn()
        cursor.execute('select tags.tagId as tagId, tags.content as content, linkedTimes from tags, tag_series where '
                       'tag_series.seriesId = %s  and tag_series.tagId = tags.tagId', seriesId)

        rows = cursor.fetchall()
        for i in range(len(rows)):
            rows[i]['type'] = 'primary'
        # print(f'[DEBUG] rows = {rows}')
        return rows

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/getPiecesBrief', methods=['GET'])
def get_bref():
    """
    获取一章简略信息
    """
    try:
        data = request.args
        # 默认每次随机返回15条数据
        mode = 'random'
        size = 15

        if 'mode' in data:
            mode = data['mode']

        if 'size' in data:
            size = data['size']

        if mode == 'random':
            rows = random_get_pieces_brief_sql(size)
        # 查找最热门的标签
        for i in range(len(rows)):
            tag_list = get_tags_by_seriesId_sql(int(rows[i]['seriesId']))
            if (len(tag_list)):
                max_linked_id = 0
                max_linked_tag = None
                for tag in tag_list:
                    if tag['linkedTimes'] >= max_linked_id:
                        max_linked_id = tag['linkedTimes']
                        max_linked_tag = tag
                rows[i]['tag'] = max_linked_tag
        # 查找对应的用户
        for i in range(len(rows)):
            rows[i]['user'] = get_user_by_id(rows[i]['userId'])

        # 缩短content
        for i in range(len(rows)):
            rows[i]['content'] = rows[i]['content'][:40]
        return build_success_response(rows)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __query_series_brief_sql(query_param: dict) -> List[dict]:
    try:
        conn, cursor = pooldb.get_conn()
        sql_from_table = 'select distinct series.seriesId as seriesId, seriesName, userId, isFinished, abstract, likes, views, shares, collect, series.createTime as createTime from series '
        arg_list = []
        sql = sql_from_table
        if 'seriesName' in query_param or 'seriesId' in query_param or 'seriesTag' in query_param:
            sql_where = ' where 1=1 '
            if 'seriesName' in query_param:
                sql_where += ' and seriesName like %s '
                arg_list.append(f'%{query_param["seriesName"]}%')
            if 'seriesId' in query_param:
                sql_where += ' and seriesId = %s '
                arg_list.append(query_param['seriesId'])
            if 'seriesTag' in query_param:
                sql_from_table += ' , tag_series, tags '
                sql_where += ' and tag_series.seriesId = series.seriesId and tag_series.tagId = tags.tagId and tags.content like %s '
                arg_list.append(f"%{query_param['seriesTag']}%")

            sql = sql_from_table + sql_where

        if 'sortMode' in query_param:
            if query_param['sortMode'] == 'Hot':
                sql += ' order by series.likes desc '
            elif query_param['sortMode'] == 'New':
                sql += ' order by series.createTime desc '

        # print(f'[DEBUG] sql = {sql}')
        cursor.execute(sql, tuple(arg_list))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        check.printException(e)
        if conn is not None:
            conn.rollback()
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/getSeriesBrief', methods=['GET'])
def get_series_brief():
    """
    获取系列简略信息
    """
    try:
        query_param = {}
        seriesName = request.args.get('seriesName')
        seriesId = request.args.get('seriesId')
        seriesTag = request.args.get('seriesTag')
        sortMode = request.args.get('sortMode')
        if seriesName is not None:
            query_param['seriesName'] = seriesName
        if seriesId is not None:
            query_param['seriesId'] = seriesId
        if seriesTag is not None:
            query_param['seriesTag'] = seriesTag
        if sortMode is not None:
            query_param['sortMode'] = sortMode
        rows = __query_series_brief_sql(query_param)

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
            rows[i]['user'] = get_user_by_id(rows[i]['userId'])
            rows[i]['tag'] = get_tags_by_seriesId_sql(rows[i]['seriesId'])

        return build_success_response(data=rows, length=length)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def get_pieces_by_id_sql(piecesId: int) -> dict:
    try:
        # print(f'[DEBUG] seriesId = {seriesId} type = {type(seriesId)}')
        conn, cursor = pooldb.get_conn()
        cursor.execute(
            'select pieces.piecesId as piecesId, pieces.seriesId as seriesId, pieces.title as title, pieces.userId as userId,  pieces.content as content, pieces.createTime as createTime, pieces.updateTime as updateTime, pieces.state as state, pieces.likes as likes, pieces.views as views, pieces.shares as shares, series.seriesName as seriesName from pieces, series where piecesId = %s and pieces.seriesId = series.seriesId ',
            piecesId)

        row = cursor.fetchone()

        # print(f'[DEBUG] row = {row}')
        return row

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/getPiecesDetail', methods=['GET'])
def get_pieces_detail():
    """
    获取一章详细信息
    """
    try:
        data = request.args
        if 'piecesId' not in data:
            raise NetworkException(400, '传入数据错误，未包含piecesId')

        pieceId = data['piecesId']
        piece = get_pieces_by_id_sql(pieceId)
        if piece is None:
            raise NetworkException(404, '该章节不存在')
        if 'createTime' in piece:
            piece['createTime'] = piece['createTime'].strftime('%Y-%m-%d %H:%M:%S')
        if 'updateTime' in piece:
            piece['updateTime'] = piece['updateTime'].strftime('%Y-%m-%d %H:%M:%S')
        tag_list = get_tags_by_seriesId_sql(piece['seriesId'])
        piece['tag'] = tag_list
        piece['user'] = get_user_by_id(piece['userId'])

        return build_success_response(piece)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/getSeriesDetail', methods=['GET'])
def get_series_detail():
    """
    获取系列详细信息
    """
    return build_success_response()


def get_series_by_user_id(user_id: int) -> list:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute("select * from series where userId = %d", int(user_id))

        rows = cursor.fetchall()
        return rows

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/getUserSeriesList', methods=['GET'])
def get_user_series_list():
    """
    获取属于用户的所有系列的列表
    """
    try:
        user = check_user_before_request(request)
        series_list = get_series_by_user_id(user['id'])
        for i in range(len(series_list)):
            series_list[i]['createTime'] = series_list[i]['createTime'].strftime('%Y-%m-%d %H:%M:%S')

        return build_success_response(series_list)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/getUserPiecesList', methods=['GET'])
def get_user_pieces_list():
    """
    获取属于用户的所有篇章的列表（不包括内容）
    """

    return build_success_response()


@bp.route('/addPieces', methods=['POST'])
def add_pieces():
    """
    添加一章
    """
    return build_success_response()


def __add_series_sql(data: dict):
    try:
        sql = 'insert into series('
        args_list = []

        # 系列名
        sql += ' seriesName '
        args_list.append(data['seriesName'])
        value_sql = ' %s '

        # 用户名
        if 'userId' in data:
            sql += ' ,userId '
            args_list.append(data['userId'])
            value_sql += ' ,%s '

        if 'abstract' in data:
            sql += ' ,abstract '
            args_list.append(data['abstract'])
            value_sql += ' ,%s '
        sql += f') values({value_sql})'

        print(sql)
        seriesId = execute_sql_write(pooldb, sql, tuple(args_list))
        print(f'add series id {seriesId}')

    except Exception as e:
        check.printException(e)
        raise e


@bp.route('/addSeries', methods=['POST'])
def add_series():
    """
    添加系列
    """
    try:
        userId = request.json.get('userId')
        if userId is None:
            # 如果没有传进来userId则说明，这是用户本人想要在自己名下添加一条series
            user = check_user_before_request(request)
            userId = user['userId']
        else:
            # 如果传来了userId，则说明这是管理人员尝试向某个用户添加一条series
            user = check_user_before_request(request, roles='manager')

        seriesName = request.json.get('seriesName')
        if seriesName is None:
            raise NetworkException(code=400, msg='前端数据错误，缺少seriesName')

        __add_series_sql(request.json)

        return build_success_response(msg='添加系列成功')

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/delPieces', methods=['POST'])
def del_pieces():
    """
    删除一章
    """
    return build_success_response()


def __check_if_all_series_are_belong_to_user(seriesIdList: list, userId: str) -> bool:
    try:
        sql = 'select * from series where userId = %s'
        rows = execute_sql_query(pooldb, sql, userId)
        if rows is None or len(rows) <= 0:
            raise NetworkException(code=400, msg=f'没有任何系列属于ID为{userId}的用户')

        seriesIdListOriginSet = set(seriesIdList)
        seriesIdListNewSet = set(map(lambda x: x['seriesId'], rows))

        seriesCommon = list(seriesIdListOriginSet & seriesIdListNewSet)
        if len(seriesCommon) != len(seriesIdList):
            return False

        return True

    except Exception as e:
        check.printException(e)
        raise e


def __del_series_sql(seriesId: str):
    try:
        sql = 'delete from series where seriesId = %s'
        execute_sql_write(pooldb, sql, seriesId)

    except Exception as e:
        check.printException(e)
        raise e


@bp.route('/delSeries', methods=['POST'])
def del_series():
    """
    删除系列
    """
    try:
        seriesIdList = request.json.get('seriesIdList')
        if seriesIdList is None:
            raise NetworkException(code=400, msg='前端数据错误，缺少seriesIdList')
        # 先检查所有的series是不是都属于这个用户
        user = check_user_before_request(request, roles='common')

        if __check_if_all_series_are_belong_to_user(seriesIdList, user['id']):
            # 如果这个seires属于发出请求的用户，则可以操作
            for seriesId in seriesIdList:
                __del_series_sql(seriesId)
        else:
            # 如果这个seires不属于发出请求的用户，则需要验证管理员身份
            check_user_before_request(request, roles='manager')
            for seriesId in seriesIdList:
                __del_series_sql(seriesId)

        return build_success_response(msg='删除系列成功')

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/updatePieces', methods=['POST'])
def update_pieces():
    """
    更新一章
    """
    return build_success_response()


def __update_series_sql(data: dict):
    try:
        sql = 'update series set '
        args_list = []

        if 'seriesName' in data:
            args_list.append(['seriesName', data['seriesName']])
        if 'abstract' in data:
            args_list.append(['abstract', data['abstract']])
        if 'userId' in data:
            args_list.append(['userId', data['userId']])
        param_list = []
        if len(args_list):
            sql += f'{args_list[0][0]}=%s '
            param_list.append(args_list[0][1])
            for i in range(1, len(args_list)):
                sql += f' ,{args_list[i][0]}=%s '
                param_list.append(args_list[i][1])
        sql += ' where seriesId = %s'
        param_list.append(data['seriesId'])

        seriesId = execute_sql_write(pooldb, sql, tuple(param_list))

    except Exception as e:
        check.printException(e)
        raise e


@bp.route('/updateSeries', methods=['POST'])
def update_series():
    """
    更新系列
    """
    try:
        user = check_user_before_request(request, roles='manager')

        seriesId = request.json.get('seriesId')
        if seriesId is None:
            raise NetworkException(code=400, msg='前端数据错误，缺少seriesId')

        __update_series_sql(request.json)

        return build_success_response(msg='修改系列成功')

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')

    return build_success_response()
