import inspect
from typing import List, Dict


# 读取数据库
def execute_sql_query(pooldb, sql: str, *args) -> List[Dict]:
    """
    执行 SQL 查询并返回查询结果，结果以字典列表形式返回。
    """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行 SQL 查询
        cursor.execute(sql, *args)
        # 返回结果集
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise e
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


# 写入数据库
def execute_sql_write(pooldb, sql: str, *args):
    conn, cursor = pooldb.get_conn()
    try:
        # 执行SQL
        cursor.execute(sql, *args)
        conn.commit()
        # 获取插入自增主键 ID
        id_ = cursor.lastrowid
        return id_
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise e
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None
