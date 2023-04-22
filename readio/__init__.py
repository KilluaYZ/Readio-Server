import json
# from dbtest.showdata10 import db # 引入其他蓝图
import os
from typing import Dict

from flask import Flask, url_for
from flask_cors import CORS  # 跨域

# app
from readio.auth import appAuth
from readio.auth.webAuth import webAuth
from readio.auth.webAuth import webAuth as prod_auth
from readio.database.init_db import init_db
from readio.mainpage import appHomePage, appBookShelfPage
# from readio.manage.postManage import posts
# from readio.manage.postManage import posts as prod_posts
# from readio.manage.tagManage import tag
# from readio.manage.tagManage import tag as prod_tag
# from readio.manage.userManage import user
# from readio.manage.userManage import user as prod_user
# from readio.auth.appAuth import appAuth
from readio.monitor.monitor import monitor
from readio.monitor.monitor import monitor as prod_monitor

from apscheduler.schedulers.background import BackgroundScheduler


# 创建flask app
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # 在应用中注册init_db
    @app.cli.command('init-db')
    def init_db_command():
        """删除现有的所有数据，并新建关系表"""
        init_db()
        print("已初始化数据库")

    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')
    # 在开发环境中注册蓝图
    if FLASK_DEBUG:
        print('当前服务器在开发环境下运行')
        app.register_blueprint(webAuth, url_prefix='/auth/web')
        app.register_blueprint(monitor, url_prefix='/monitor')
        app.register_blueprint(appAuth.bp)
        app.register_blueprint(appHomePage.bp)
        app.register_blueprint(appBookShelfPage.bp)
    # 生产环境蓝图注册
    else:
        print('当前服务器在生产环境下运行')
        app.register_blueprint(prod_auth, url_prefix='/prod-api/auth')
        app.register_blueprint(prod_monitor, url_prefix='/prod-api/monitor')

    #配置定时任务
    #该任务作用是每个一个小时检查一次user_token表，将超过1天未活动的token删掉（随便定的，后面改
    from readio.manage.userManage import checkSessionsAvailability
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=checkSessionsAvailability,
                    id='checkSessionsAvailability',
                    trigger='interval',
                    seconds=3600,
                    replace_existing=True
    )
    #启动任务列表
    scheduler.start()
    """ 测试 """
    app_test(app)

    return app


# 将 response 解析为可显示中文的 dict
def response2dict(response):
    # response.data.decode('utf-8') <str>
    # json.loads(): JSON 格式的字符串转换为 dict、list、str 等
    return json.loads(response.data.decode('utf-8'))


def json_append(json_old, key: str, value):
    dict_json = json.loads(json_old)
    dict_json[key] = value
    return json.dumps(dict_json)


# post return dict
def client_test(client, url_for_: str, method: str, headers, data=None) -> Dict[str, any]:
    url = url_for(url_for_)
    print('\t------------')
    print('\t[test url]:', url)
    if method == 'POST':
        response = response2dict(client.post(url, headers=headers, json=data))
    elif method == 'GET':
        headers.update(data) if data is not None else None
        response = response2dict(client.get(url, headers=headers))
    else:
        response = 'test: No method!'
    print("\t[client get]:", type(response), response)
    print('\t------------')
    return response


def app_test(app):
    with app.test_request_context():
        # 使用测试客户端发送请求
        client = app.test_client()
        headers = {
            # 'Content-Type': 'application/json',
        }
        """ test homepage """
        # 获取url: /app/homepage
        response = client_test(client, 'homepage.recommend', 'GET', headers)
        """ test auth """
        user_data = {
            "phoneNumber": "19800380215",
            "passWord": "123456"
        }
        # register
        # client_test(client, url_for_='auth.register', method='POST', data=user_data)
        # login
        resp_dict = client_test(client, url_for_='auth.login', method='POST', headers=headers, data=user_data)
        # profile
        # token = resp_dict.get('token', None)
        token = resp_dict['data']['token']
        print(f'[INFO] token = {token}')
        user_data['Authorization'] = token
        # user_data['Authorization'] = 'a974075986a7519ddbeaff7dc3756c7b41a2db32'
        profile_dict = client_test(client, 'auth.profile', 'GET', headers=headers, data=user_data)
        uid = profile_dict['data']['userInfo']['userId'] if profile_dict is not None else None
        # print(id_)

        """ test bookshelf """
        # index
        bookshelf_dict = client_test(client, url_for_='bookshelf.index', method='GET',
                                     headers=headers, data=user_data)
        read_info = dict()
        read_info['userId'] = uid if uid is not None else 3
        read_info['bookId'] = 7
        read_info['progress'] = 3
        # print(read_info)
        # add
        client_test(client, 'bookshelf.add', 'POST', headers=headers, data=read_info)
        # update
        client_test(client, 'bookshelf.update', 'POST', headers=headers, data=read_info)
        # del
        client_test(client, 'bookshelf.delete', 'POST', headers=headers, data=read_info)
