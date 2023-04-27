"""
二创管理
"""
import functools
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
bp = Blueprint('worksManage', __name__, url_prefix='/works')

pooldb = readio.database.connectPool.pooldb

def random_get_pieces_brief_sql(size: int) -> list:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select piecesId, serialId, title, userId, state, content, likes, views, shares from pieces')
        rows = cursor.fetchall()
        #随机从列表中抽取size个元素
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

def get_tags_by_seriesId_sql(seriesId:int) -> list:
    try:
        # print(f'[DEBUG] seriesId = {seriesId} type = {type(seriesId)}')
        conn, cursor = pooldb.get_conn()
        cursor.execute('select tags.tagId as tagId, tags.content as content, linkedTimes from tags, tag_series where '
                       'tag_series.serialId = %s  and tag_series.tagId = tags.tagId', seriesId)

        rows = cursor.fetchall()
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
        #默认每次随机返回15条数据
        mode = 'random'
        size = 15

        if 'mode' in data:
            mode = data['mode']

        if 'size' in data:
            size = data['size']

        if mode == 'random':
            rows = random_get_pieces_brief_sql(size)
        print(111)
        #查找最热门的标签
        for i in range(len(rows)):
            tag_list = get_tags_by_seriesId_sql(int(rows[i]['serialId']))
            if(len(tag_list)):
                max_linked_id = 0
                max_linked_tag = None
                for tag in tag_list:
                    if tag['linkedTimes'] >= max_linked_id:
                        max_linked_id = tag['linkedTimes']
                        max_linked_tag = tag
                rows[i]['tag'] = max_linked_tag
        print(222)
        #查找对应的用户
        for i in range(len(rows)):
            rows[i]['user'] = get_user_by_id(rows[i]['userId'])

        return build_success_response(rows)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')

# @bp.route('/getSeriesBrief', methods=['GET'])
# def get_detail():
#     """
#     获取系列简略信息
#     """
#     pass
#
# @bp.route('/getPiecesDetail', methods=['GET'])
# def update_pieces():
#     """
#     获取一章详细信息
#     """
#     pass
#
# @bp.route('/getSeriesDetail', methods=['GET'])
# def update_pieces():
#     """
#     获取系列详细信息
#     """
#     pass
#
# @bp.route('/getUserSeriesList', methods=['GET'])
# def update_pieces():
#     """
#     获取属于用户的所有系列的列表
#     """
#     pass
#
# @bp.route('/getUserPiecesList', methods=['GET'])
# def update_pieces():
#     """
#     获取属于用户的所有篇章的列表（不包括内容）
#     """
#     pass
#
# @bp.route('/addPieces', methods=['POST'])
# def add_pieces():
#     """
#     添加一章
#     """
#     pass
#
# @bp.route('/addSeries', methods=['POST'])
# def add_series():
#     """
#     添加系列
#     """
#     pass
#
# @bp.route('/delPieces', methods=['GET'])
# def del_pieces():
#     """
#     删除一章
#     """
#     pass
#
# @bp.route('/delSeries', methods=['GET'])
# def del_series():
#     """
#     删除系列
#     """
#     pass

# @bp.route('/updatePieces', methods=['POST'])
# def update_pieces():
#     """
#     更新一章
#     """
#     pass

# @bp.route('/updateSeries', methods=['POST'])
# def update_series():
#     """
#     更新系列
#     """
#     pass


