# -*- coding: utf-8 -*-
# python 3.x
# Filename: ESServiceSystem.py
# 定义一个ESImageFileSystem类实现图片文件系统
import os.path

from flask import Flask, send_file, make_response

from util.PlantUml import MyPlantUML
from util.ElasticsearchManager import ElasticsearchManager
from util.FileUtil import FileUtil
from util.LogUtil import LogUtil
from util.MD5Util import MD5Util
from util.ShellUtil import ShellUtil

TAG = 'ESImageFileSystem'

# 创建Flask服务
app = Flask(__name__)


@app.route('/images/uml/<path:id>')
def getImage(id: str):
    LogUtil.i(TAG, f'getImage {id}')
    errPic = os.path.join(FileUtil.getProjectPath(), 'resources/icons/projectManager/error.png')
    umlData = ElasticsearchManager.getFiled(id=id, fieldName='umlData')
    if not umlData:
        return send_file(errPic, mimetype='image/png')
    fileName = MD5Util.md5(umlData)
    tmpDir = os.path.join(FileUtil.getProjectPath(), 'temp/image/uml')
    FileUtil.mkDirs(tmpDir)
    imageFp = os.path.join(tmpDir, fileName)
    if FileUtil.existsFile(imageFp):
        return send_file(imageFp, mimetype='image/png')
    fp, err = MyPlantUML.jarProcesses(umlData, imageFp, tmpDir)
    if fp:
        return send_file(fp, mimetype='image/png')
    return send_file(errPic, mimetype='image/png')


@app.route('/open/file/<path:fileInfo>')
def openFile(fileInfo: str):
    LogUtil.i(TAG, f'openFile {fileInfo}')
    data = fileInfo.split(';')
    fp = data[0]
    position = data[1]
    ShellUtil.exec(f'D:/Ksoftware/notepad++/notepad++ "{fp}" -p{position}')
    return make_response()


class ESServiceSystem:
    @staticmethod
    def start():
        app.run()

    @staticmethod
    def stop():
        app.request.environ.get('werkzeug.server.shutdown')()


if __name__ == '__main__':
    ESServiceSystem.start()
