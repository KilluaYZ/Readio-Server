from flask import Blueprint
from readio.utils.auth import *
import readio.database.connectPool
from readio.utils.executeSQL import *

bp = Blueprint('likesManage', __name__, url_prefix='/like')

pooldb = readio.database.connectPool.pooldb


def __add_pieces_like(userId, piecesId, trans=None):
    sql = 'insert into user_pieces_like(userId, piecesId) values(%s, %s)'
    if trans is None:
        return execute_sql_write(pooldb, sql, (userId, piecesId))
    else:
        return trans.execute(sql, (userId, piecesId))


def __get_all_like_pieces_id_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有like的pieces的id
    """
    sql = 'select piecesId from user_pieces_like where userId=%s'
    rows = execute_sql_query(pooldb, sql, userId)
    rows = list(map(lambda x: int(x['piecesId']), rows))
    return rows


def __get_all_like_pieces_obj_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有like的pieces
    """
    sql = 'select pieces.piecesId as piecesId, pieces.seriesId as seriesId, ' \
          'pieces.title as title, pieces.userId as userId, pieces.content as content, ' \
          'pieces.createTime as createTime, pieces.updateTime as updateTime, ' \
          'pieces.status as status, pieces.likes as likes, pieces.views as views, ' \
          'pieces.shares as shares, pieces.collect as collect from pieces, user_pieces_like ' \
          'where pieces.piecesId = user_pieces_like.piecesId ' \
          'and user_pieces_like.userId=%s'
    return execute_sql_query(pooldb, sql, userId)


def __check_if_user_like_pieces(userId, piecesId) -> bool:
    rows = __get_all_like_pieces_id_by_userid(userId)
    piecesId = int(piecesId)
    if rows is not None and len(rows) and piecesId in rows:
        return True
    return False


@bp.route('/pieces/add', methods=['GET'])
def add_pieces_like():
    """
    增加pieces的点赞
    """
    try:
        piecesId = request.args.get("piecesId")
        if piecesId is None:
            raise NetworkException(400, "前端数据缺失，缺少piecesId")

        user = check_user_before_request(request)
        userId = user['id']
        if not __check_if_user_like_pieces(userId, piecesId):
            # 还没有点赞过
            __add_pieces_like(userId, piecesId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_pieces_like(userId, piecesId, trans=None):
    sql = 'delete from user_pieces_like where userId=%s and piecesId=%s'
    if trans is None:
        return execute_sql_write(pooldb, sql, (userId, piecesId))
    else:
        return trans.execute(sql, (userId, piecesId))


@bp.route('/pieces/del', methods=['GET'])
def del_pieces_like():
    """
    取消pieces的点赞
    """
    try:
        piecesId = request.args.get("piecesId")
        if piecesId is None:
            raise NetworkException(400, "前端数据缺失，缺少piecesId")

        user = check_user_before_request(request)
        userId = user['id']
        __del_pieces_like(userId, piecesId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/pieces/get', methods=['GET'])
def get_pieces_like():
    """
    获取该用户点赞的所有pieces
    """
    try:
        user = check_user_before_request(request)
        userId = user['id']
        rows = __get_all_like_pieces_obj_by_userid(userId)

        return build_success_response(data=rows, length=len(rows))

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')
