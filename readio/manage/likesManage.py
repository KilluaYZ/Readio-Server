from flask import Blueprint
from readio.utils.auth import *
import readio.database.connectPool
from readio.utils.executeSQL import *
bp = Blueprint('likesManage', __name__, url_prefix='/like')

pooldb = readio.database.connectPool.pooldb

def __add_like(userId, piecesId, trans=None):
    sql = 'insert into user_pieces_like(userId, piecesId) values(%s, %s)'
    if trans is None:
        return execute_sql_write(pooldb, sql, (userId, piecesId))
    else:
        return trans.execute(sql, (userId, piecesId))

@bp.route('/add', methods=['GET'])
def get_bref():
    """
    获取一章简略信息
    """
    try:


        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')
