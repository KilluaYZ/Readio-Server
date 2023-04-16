from flask import request
import inspect
import hashlib
import os
import random
from werkzeug.security import check_password_hash, generate_password_hash
import readio.database.connectPool
global pooldb
pooldb = readio.database.connectPool.pooldb
from  readio.utils.buildResponse import *

def build_token():
    while True:
        token = hashlib.sha1(os.urandom(24)).hexdigest()
        rows = pooldb.read('select * from user_token where token="%s"' % token)
        if not rows or (rows and len(rows) == 0) :
            #找到一个不重复的token
            break
    return token
            
def build_session(uid):
    try:
        token = build_token()
        # print('[DEBUG] build token success, token=',token)
        conn,cursor = pooldb.get_conn()
        cursor.execute('insert into user_token(uid, token) values(%s, %s)',(uid,token))
        conn.commit()
        pooldb.close_conn(conn,cursor)
        return token
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        print(e)
        raise Exception('创建会话失败')

def update_token_visit_time(token):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('update user_token set visitTime=CURRENT_TIMESTAMP where token=%s',(token))
        conn.commit()
        pooldb.close_conn(conn,cursor)
        return token
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        print(e)
        raise Exception('更新token状态失败')

def get_user_by_token(token):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('select * from users, user_token where token=%s and user_token.uid=users.id',(token))
        row = cursor.fetchone()
        if row is None or len(row) <= 0:
            raise Exception('会话不存在')
        
        pooldb.close_conn(conn,cursor)
        return row
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        print(e)
        raise Exception('会话不存在')

def checkTokens(token,roles):
    try:
        if token == None:
            return 404
            
        # print('token=',token)
        user = get_user_by_token(token)
        if not user:
            #查无此人
            return 404
        
        if roles == 'admin':
            if user['roles'] != 'admin':
                #没有权限
                return 403
        elif roles == 'manager':
            if user['roles'] not in ['admin','manager']:
                #没有权限
                return 403
        elif roles == 'common':
            if user['roles'] not in ['admin','manager','common']:
                return 403
        else:
            #未知roles
            return 500
        
        update_token_visit_time(token)
        #有对应权限,放行
        return 200
        
    except Exception as e:
        print(e)
        #运行时错误
        return 500

#检查Token和权限，如果不是200就直接返回到客户端
def checkTokensReponseIfNot200(token, roles):
    state = checkTokens(token,roles)
    if state == 404:
        return build_error_response(400,'会话未建立，请重新登录')
    elif state == 403:
        return build_error_response(403,'您没有该操作的权限，请联系管理员')
    elif state == 500:
        return build_error_response(500,'服务器内部发生错误，请联系管理员')


def random_gen_str(strlen = 14)->str:
    char_list = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM_'
    res = ''
    for _ in range(strlen):
        res += char_list[random.randint(0,len(char_list)-1)]
    return res


def random_gen_username():
    return random_gen_str()
