import inspect

import pymysql.cursors
from readio.utils.executeSQL import execute_sql_query


def printException(e):
    print(f"[ERROR]{__file__}::{inspect.getframeinfo(inspect.currentframe().f_back)[2]} \n {e}")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def checkRequestSingleKeyWithCondition(req: dict, keyName: str, condition: str) -> bool:
    """
    取出req[keyName], 其值会被替代为condition中的#?#检查
    """
    try:
        if keyName not in req:
            raise Exception("key不存在")
        val = req[keyName]
        condition = condition.replace("#?#", f"{val}")
        return eval(condition)

    except Exception as e:
        printException(e)
        return False


def checkRequestMultipleKeysWithCondition(req: dict, keyNameList: list, condition: str) -> list:
    res = []
    for keyName in keyNameList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res


def checkRequestMultipleKeysWithCondition(req: dict, keyDefineList: list) -> list:
    res = []
    for keyName, condition in keyDefineList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res


def checkRequstIsNotNone(req: dict, keyName: str):
    if keyName not in req:
        return False

    if req[keyName] is None:
        return False

    return True


# req = {"name":"ziyang","phoneNumber":"18314266702","age":18}
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' < 20"))
# print(checksRequestSingleKeyWithCondition(req,"age","#?# < 20"))
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' == 'ziyang'"))
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' != None and len('#?#') > 5 and len('#?#') < 13"))


# ========== appBook.: 工具函数 ==========

# 检查用户 uid 的书架上是否有书 bid
# 注意：这里未检查用户是否有凭证，可以配合使用 check_user_before_request
def check_book_added(pooldb, uid, bid):
    """ 判断用户 uid 的书架是否有书籍 bid """
    try:
        check_book_sql = "SELECT COUNT(*) FROM user_read_info WHERE userId=%s AND bookId=%s"
        args = uid, bid
        book_count = execute_sql_query(pooldb, check_book_sql, args)
        # book_count = [{'COUNT(*)': 1}]
        return book_count[0]['COUNT(*)'] > 0
    except pymysql.Error as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        # raise
        raise Exception("Error occurred while checking book added: " + str(e))


# 注意：这里未检查用户是否有凭证，可以配合使用 check_user_before_request
def check_has_comment(pooldb, uid, cid):
    """ 判断用户 uid 是否有评论 cid """
    try:
        check_comment_sql = "SELECT COUNT(*) FROM comments WHERE userId=%s AND commentId=%s"
        args = uid, cid
        comment_count = execute_sql_query(pooldb, check_comment_sql, args)
        return comment_count[0]['COUNT(*)'] > 0
    except Exception as e:
        print("[ERROR] " + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise Exception("Error occurred while checking the comment: " + str(e))
