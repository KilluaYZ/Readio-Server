from flask import request
from flask import Blueprint
import inspect
from werkzeug.security import check_password_hash, generate_password_hash
from readio.utils.buildResponse import *
from readio.utils.auth import *

appAuth = Blueprint('/auth/app', __name__)
import readio.database.connectPool

pooldb = readio.database.connectPool.pooldb

def authorize_phoneNumber_password(phoneNumber,passWord):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('select * from users where phoneNumber=%s',(phoneNumber))
        user = cursor.fetchone()
        pooldb.close_conn(conn,cursor)
        if user is None:
            raise Exception('用户名不正确')
        
        if not check_password_hash(user['passWord'],passWord):
            raise Exception('密码不正确')
        
        #都正确了，开始创建会话
        print('验证成功')
        return user
    except Exception as e:
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        return None

def authorize_userId_password(userId,passWord):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('select * from users where id=%s',(userId))
        user = cursor.fetchone()
        pooldb.close_conn(conn,cursor)
        if user is None:
            raise Exception('用户名不正确')
        
        if not check_password_hash(user['password'],passWord):
            raise Exception('密码不正确')
        
        #都正确了，开始创建会话
        print('验证成功')
        return user
    except Exception as e:
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        return None

#用户注册的sql语句, 默认的用户名随机生成，用户用phoneNumber和password注册
def register_user_sql(password,phoneNumber):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('insert into users(username,password,phonenumber,roles) values(%s,%s,%s,%s)',(random_gen_username(),generate_password_hash(password),phoneNumber,'common'))
        conn.commit()
        pooldb.close_conn(conn,cursor)
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)


#检查phoneNumber是不是唯一的，如果是则返回True，否则返回False
def checkPhoneNumberIsUnique(phoneNumer):
    try:
        conn,cursor = pooldb.get_conn()
        cursor.execute('select * from users where phonenumber=%s',(phoneNumer))
        rows = cursor.fetchall()
        pooldb.close_conn(conn,cursor)
        if(len(rows) == 0):
            return True
        return False
            
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)

@appAuth.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if('phoneNumber' not in data or 'passWord' not in data):
            raise Exception('前端数据错误！缺少phoneNumer或passWord')
        if not checkPhoneNumberIsUnique(data['phoneNumber']):
            return build_error_response(msg='该手机号已被注册')
        register_user_sql(data['passWord'], data['phoneNumber'])        
        return build_success_response()
    
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        return build_error_response(msg='注册失败')


#收到用户名密码，返回会话对应的toKen
@appAuth.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if('phoneNumber' not in data or 'passWord' not in data):
            raise Exception('前端数据不正确，phoneNumber或passWord')
        phoneNumber = data['phoneNumber']
        
        password = data['passWord']
        user = authorize_phoneNumber_password(phoneNumber,password)
        if user is None:
            return build_error_response(msg='用户名或密码错误')
        
        token = build_session(user['id'])
        print('[DEBUG] get token, token = ',token)
        # tokenList.append(token)
        return build_raw_response({"msg":'操作成功',"token":token})
    
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        return build_error_response(msg='登录失败')    
    
#退出登录，本质上就是删除与用户建立的对话
@appAuth.route('/logout', methods=['POST','GET'])
def logout():
    try:
        token = request.cookies.get('Admin-Token')
        if token is None:
            return build_success_response()
        conn,cursor = pooldb.get_conn()
        cursor.execute('delete from user_token where token=%s',(token))
        conn.commit()
        pooldb.close_conn(conn,cursor)
        return build_success_response()
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        return build_error_response()

#data里面应该有user的所有信息
def user_profile_update_user_sql(userId,data):
    try:
        conn, cursor = pooldb.get_conn()
        sql = 'update users set userName=%s,email=%s where id=%s'
        cursor.execute(sql,(data['userName'],data['email'],userId))
        conn.commit()
        pooldb.close_conn(conn,cursor)
        
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        raise Exception('update_ser_sql错误')

#获取用户详细信息
@appAuth.route('/profile', methods=['GET','POST'])
def getprofile():
    try:
        if request.method == 'GET':
            token = request.cookies.get('Admin-Token')
            if token is None:
                raise Exception('token不存在，无法查询')

            checkTokensReponseIfNot200(token,'common')
            
            #经过checkTokensReponseIfNot200的检查，到这里我们可以保证token是存在的，且本次访问符合对应的权限
            user = get_user_by_token(token)
            
            #格式化datetime
            if not isinstance(user['createTime'],str):
                user['createTime'] = user['createTime'].strftime('%Y-%m-%d %H:%M:%S')

            response = {
                "msg": "操作成功",
                "roles": [user['roles']],
                "data":{
                    "userId": user['id'],
                    "userName": user['userName'],
                    "email": user['email'],
                    "phoneNumber": user['phoneNumber'],
                    "avator":user['avator'],
                    "createTime":user['createTime'],
                    "fansNum":123,
                    "subscribeNum":234,
                    "hotNum":678
                }
            }
            
            return build_success_response(response)
        
        elif request.method == 'POST':
            token = request.cookies.get('Admin-Token')
            if token is None:
                raise Exception('token不存在，无法修改信息')

            checkTokensReponseIfNot200(token,'common')
            user = get_user_by_token(token)
            data = request.json
            user_profile_update_user_sql(user['id'],data)
            
            return build_success_response()
    
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        return build_error_response()

def user_profile_update_user_pwd(uid,pwd):
    try:
        sql = 'update users set passWord=%s where id=%s'
        conn,cursor = pooldb.get_conn()
        cursor.execute(sql,(generate_password_hash(pwd),uid))
        conn.commit()
        pooldb.close_conn(conn,cursor)
    except Exception as e:
        print(e)
        if conn is not None:
            pooldb.close_conn(conn,cursor)
        raise Exception(f'用户{uid}密码修改失败')


@appAuth.route('/profile/updatePwd', methods=['POST'])
def updatePwd():
    try:
        data = request.json
        if('oldPassword' not in data or 'newPassword' not in data):
            raise Exception('前端数据错误，不存在oldPassword或newPassword')
        
        token = request.cookies.get('Admin-Token')
        if token is None:
            raise Exception('token不存在')
        
        checkTokensReponseIfNot200(token,'common')
        
        user = get_user_by_token(token)
        
        res = authorize_userId_password(user['id'],data['oldPassword'])
        if res is None:
            raise Exception('密码不正确')
        
        user_profile_update_user_pwd(user['id'],data['newPassword'])
        
        return build_success_response()
    
    except Exception as e:
        print("[ERROR]"+__file__+"::"+inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        return build_error_response()

