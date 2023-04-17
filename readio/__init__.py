from distutils.log import debug
from flask import Flask, url_for
from flask import request
from flask_cors import CORS  # 跨域
# from dbtest.showdata10 import db # 引入其他蓝图
import os
import sys

from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler

from readio.database.init_db import init_db
from readio.manage.tagManage import tag
from readio.manage.postManage import posts
from readio.auth.webAuth import webAuth
from readio.auth.appAuth import appAuth
from readio.monitor.monitor import monitor
from readio.manage.userManage import user
# app
from readio.mainpage import appHomePage

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
        app.register_blueprint(appAuth, url_prefix='/auth/app')
        app.register_blueprint(monitor, url_prefix='/monitor')
        app.register_blueprint(user, url_prefix='/user')
        # app
        app.register_blueprint(appHomePage.bp)
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
    with app.test_request_context():
        # 获取url: /app/homepage
        url = url_for('homepage.recommend')
        print(url)
        # print(url_for('login'))
        # print(url_for('login', next='/'))
        # print(url_for('profile', username='John Doe'))

        # 使用测试客户端发送请求
        client = app.test_client()
        response = client.get(url)
        assert response.status_code == 200

        # assert b'Hello, John!' in response.data

        # 获取请求上下文中保存的请求对象
        # assert request.args['name'] == 'John'

    return app
