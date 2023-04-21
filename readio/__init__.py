from distutils.log import debug
from flask import Flask, url_for
from flask import request
from flask_cors import CORS  # 跨域
# from dbtest.showdata10 import db # 引入其他蓝图
import os
import json
import sys

from sqlalchemy import func
# from apscheduler.schedulers.background import BackgroundScheduler

from readio.database.init_db import init_db
from readio.manage.tagManage import tag
from readio.manage.postManage import posts
from readio.auth.webAuth import webAuth
# from readio.auth.appAuth import appAuth
from readio.monitor.monitor import monitor
from readio.manage.userManage import user
# app
from readio.auth import appAuth
from readio.mainpage import appHomePage
from readio.mainpage.appBookListPage import appBookListPage

from readio.manage.tagManage import tag as prod_tag
from readio.manage.postManage import posts as prod_posts
from readio.auth.webAuth import webAuth as prod_auth
from readio.monitor.monitor import monitor as prod_monitor
from readio.manage.userManage import user as prod_user


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

    FLASK_ENV = os.environ.get('FLASK_ENV')
    print('FLASK_ENV = ', FLASK_ENV)
    # 在开发环境中注册蓝图
    if FLASK_ENV == 'development':
        print('当前服务器在开发环境下运行')
        app.register_blueprint(tag, url_prefix='/tag')
        app.register_blueprint(posts, url_prefix='/post')
        app.register_blueprint(webAuth, url_prefix='/auth/web')
        app.register_blueprint(monitor, url_prefix='/monitor')
        app.register_blueprint(user, url_prefix='/user')
        # app
        # app.register_blueprint(appAuth, url_prefix='/auth/app')
        app.register_blueprint(appAuth.bp)
        app.register_blueprint(appHomePage.bp)
        app.register_blueprint(appBookListPage.bp)
    # 生产环境蓝图注册
    elif FLASK_ENV is None or FLASK_ENV == 'production':
        print('当前服务器在生产环境下运行')
        app.register_blueprint(prod_tag, url_prefix='/prod-api/tag')
        app.register_blueprint(prod_posts, url_prefix='/prod-api/post')
        app.register_blueprint(prod_auth, url_prefix='/prod-api/auth')
        app.register_blueprint(prod_monitor, url_prefix='/prod-api/monitor')
        app.register_blueprint(prod_user, url_prefix='/prod-api/user')

    # #配置定时任务
    # from manage.userManage import checkSessionsAvailability
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=checkSessionsAvailability,
    #                 id='checkSessionsAvailability',
    #                 trigger='interval',
    #                 seconds=1800,
    #                 replace_existing=True
    # )
    # 启动任务列表
    # scheduler.start()
    """ 测试 """
    # app_test(app)
    
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
def client_test(client, url_for_: str, method: str, data=None):
    url = url_for(url_for_)
    print('\t------------')
    print('test url:', url)
    if method == 'POST':
        response = response2dict(client.post(url, json=data))
    elif method == 'GET':
        response = response2dict(client.get(url, headers=data))
    else:
        response = 'test: No method!'
    print("client get:", type(response), response)
    print('\t------------')
    return response


def app_test(app):
    with app.test_request_context():
        # 使用测试客户端发送请求
        client = app.test_client()
        """ test auth """
        user_data = {
            "phoneNumber": "19800380215",
            "passWord": "123456"
        }
        # register
        # client_test(client, url_for_='auth.register', method='POST', data=user_data)
        # login
        resp_dict = client_test(client, url_for_='auth.login', method='POST', data=user_data)
        # profile
        token = resp_dict.get('token', None)
        user_data['Authorization'] = token
        # user_data['Authorization'] = 'a974075986a7519ddbeaff7dc3756c7b41a2db32'
        # print(user_data)
        profile_dict = client_test(client, url_for_='auth.getprofile', method='GET', data=user_data)

        """ test homepage """
        # # 获取url: /app/homepage
        # url_homeapge = url_for('homepage.recommend')
        # # 使用测试客户端发送请求
        # client = app.test_client()
        # response = client.get(url_homeapge)
        # assert response.status_code == 200

        # print(url_for('login'))
        # print(url_for('login', next='/'))
        # print(url_for('profile', username='John Doe'))
        # assert b'Hello, John!' in response.data

        # 获取请求上下文中保存的请求对象
        # assert request.args['name'] == 'John'
