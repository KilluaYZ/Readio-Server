"""
该文件包含的函数主要功能是构造response
"""
import json
from flask import make_response


def build_response(code: int, msg: str, data=None):
    if data is None:
        data = {}
    return make_response(json.dumps({'code': code, 'msg': msg, 'data': data}), code)


def build_error_response(code=400, msg='操作失败'):
    return build_response(code, msg)


def build_success_response(data=None):
    return build_response(200, '操作成功', data)


def build_404_response():
    build_response(404, '不存在')


def build_raw_response(response):
    return json.dumps(response)


def build_redirect_response(msg: str, url: str):
    url_data = dict({'url': url})
    return build_response(302, msg, url_data)
