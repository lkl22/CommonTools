# -*- coding: utf-8 -*-
# python 3.x
# Filename: ESImageFileSystem.py
# 定义一个ESImageFileSystem类实现图片文件系统
import os.path
from flask import Flask, send_file
from util.FileUtil import FileUtil
from util.LogUtil import LogUtil

TAG = 'ESImageFileSystem'

# 创建Flask服务
app = Flask(__name__)


@app.route('/images/<path:id>')
def getImage(id: str):
    LogUtil.i(TAG, f'getImage {id}')
    errPic = os.path.join(FileUtil.getProjectPath(), 'resources/icons/projectManager/error.png')
    return send_file(errPic, mimetype='image/png')


class ESImageFileSystem:
    @staticmethod
    def start():
        app.run()

    @staticmethod
    def stop():
        app.request.environ.get('werkzeug.server.shutdown')()


if __name__ == '__main__':
    ESImageFileSystem.start()
