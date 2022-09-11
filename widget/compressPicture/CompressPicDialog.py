# -*- coding: utf-8 -*-
# python 3.x
# Filename: CompressPicDialog.py
# 定义一个CompressPicDialog类实现图片压缩的功能
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.TinifyUtil import TinifyUtil
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), 'resources/certifi/cacert.pem')

META_DATA_NICKNAME_LIST = ['版权信息', '创建日期时间', '位置信息']
META_DATA_LIST = ['copyright', 'creation', 'location']

CONFIG_SECTION = 'PictureCompress'
KEY_SRC_FILE_DIR_PATH = 'srcFileDirPath'
KEY_DST_FILE_DIR_PATH = 'dstFileDirPath'
KEY_MAX_WORKER_THREAD_COUNT = 'maxWorkerThreadCount'

threadLock = threading.Lock()


class CompressPicDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        CompressPicDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        CompressPicDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d("Init Compress Pic Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="图片压缩工具"))
        self.setObjectName("CompressPicDialog")
        self.resize(CompressPicDialog.WINDOW_WIDTH, CompressPicDialog.WINDOW_HEIGHT)
        # self.setFixedSize(CompressPicDialog.WINDOW_WIDTH, CompressPicDialog.WINDOW_HEIGHT)

        self.isDebug = isDebug
        if isDebug:
            self.operaIni = OperaIni("../../resources/config/BaseConfig.ini")
        else:
            self.operaIni = OperaIni()
        self.maxWorkerThreadCount = int(self.getConfig(KEY_MAX_WORKER_THREAD_COUNT))
        if not self.maxWorkerThreadCount:
            self.maxWorkerThreadCount = 5
        self.apiKeys = self.getTinifyApiKeys()
        self.apiKeyIndex = 0

        self.metaDataList = []
        self.metaDataBtns = []
        self.compressRes = []

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        apiKeyConfigGroupBox = self.createApiKeyConfigGroupBox(self)
        picCompressGroupBox = self.createPicCompressGroupBox(self)

        vLayout.addWidget(apiKeyConfigGroupBox)
        vLayout.addWidget(picCompressGroupBox)
        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createApiKeyConfigGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="TinyPng API Key Config")
        vbox = WidgetUtil.createHBoxLayout(box, margins=QMargins(10, 10, 10, 10))
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入要添加的API key：", alignment=Qt.AlignVCenter | Qt.AlignRight))
        self.apiKeysLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=WidgetUtil.createSizePolicy(),
                                                         holderText="请输入要添加的API key，多个以\";\"分隔。（https://tinypng.com/developers 可以注册）",
                                                         textChanged=self.srcFnTextChanged)
        hbox.addWidget(self.apiKeysLineEdit)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加key", onClicked=self.addApiKeys))
        vbox.addLayout(hbox)
        return box

    def addApiKeys(self):
        apiKeyStr = self.apiKeysLineEdit.text().strip()
        if not apiKeyStr:
            WidgetUtil.showErrorDialog(message="请输入要添加的API keys")
            return
        apiKeys = apiKeyStr.split(";")
        for apiKey in apiKeys:
            if apiKey not in self.apiKeys:
                self.apiKeys.append(apiKey)

        self.setTinifyApiKeys(self.apiKeys)
        LogUtil.d("addApiKeys", self.apiKeys)

    def createPicCompressGroupBox(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy()
        box = WidgetUtil.createGroupBox(parent, title="图片压缩", sizePolicy=sizePolicy)

        vLayout = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)

        hbox = WidgetUtil.createHBoxLayout()

        srcFileDirPath = ''
        if self.getConfig(KEY_SRC_FILE_DIR_PATH):
            srcFileDirPath = self.getConfig(KEY_SRC_FILE_DIR_PATH)

        vLayout1 = WidgetUtil.createVBoxLayout()
        hbox1 = WidgetUtil.createHBoxLayout()
        hbox1.addWidget(WidgetUtil.createPushButton(box, text="源文件路径", minSize=QSize(120, const.HEIGHT), onClicked=self.getSrcFilePath))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(box, text=srcFileDirPath, isEnable=False)
        hbox1.addWidget(self.srcFilePathLineEdit)
        vLayout1.addLayout(hbox1)

        hbox1 = WidgetUtil.createHBoxLayout()
        hbox1.addWidget(WidgetUtil.createPushButton(box, text="目标文件路径", minSize=QSize(120, const.HEIGHT), onClicked=self.getDstFilePath))
        dstFileDirPath = ''
        if self.getConfig(KEY_DST_FILE_DIR_PATH):
            dstFileDirPath = self.getConfig(KEY_DST_FILE_DIR_PATH)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(box, text=dstFileDirPath, holderText="不填跟源路径一样")
        hbox1.addWidget(self.dstFilePathLineEdit)
        vLayout1.addLayout(hbox1)

        hbox.addLayout(vLayout1)
        btn = WidgetUtil.createPushButton(box, text="", fixedSize=QSize(30, 40),
                                          styleSheet="background-color: white",
                                          iconSize=QSize(30, 40),
                                          icon=QIcon("../../resources/icons/androidRes/exchange.png") if self.isDebug
                                          else QIcon(FileUtil.getIconFp('androidRes/exchange.png')),
                                          onClicked=self.exchangeDirs)
        hbox.addWidget(btn)
        vLayout.addLayout(hbox, 2)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="源图片匹配正则表达式：", alignment=Qt.AlignVCenter | Qt.AlignRight))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy,
                                                               holderText="请输入源图片文件名称正则表达式，多个以\";\"分隔。默认源目录下所有图片",
                                                               isEnable=True if srcFileDirPath else False,
                                                               textChanged=self.srcFnTextChanged)
        hbox.addWidget(self.srcFnPatternsLineEdit)
        vLayout.addLayout(hbox, 1)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="目标图片文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,minSize=QSize(140, const.HEIGHT)))
        self.dstFnPatternsLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy, isEnable=False,
                                                               holderText="请输入目标图片文件名称。只有一个源图片文件名时有效，无效时以源文件名作为目标文件名")
        hbox.addWidget(self.dstFnPatternsLineEdit)
        vLayout.addLayout(hbox, 1)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="选择保留的元数据：", alignment=Qt.AlignVCenter | Qt.AlignRight,minSize=QSize(140, const.HEIGHT)))

        for i in range(len(META_DATA_NICKNAME_LIST)):
            checkBox = WidgetUtil.createCheckBox(box, text=META_DATA_NICKNAME_LIST[i] + "  ", stateChanged=self.metaDataCheckChanged)
            self.metaDataBtns.append(checkBox)
            hbox.addWidget(checkBox)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hbox, 1)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="同时压缩文件数量：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT)))
        self.maxWorkerThreadCountSpinBox = WidgetUtil.createSpinBox(box,
                                                                    value=self.maxWorkerThreadCount,
                                                                    minValue=3,
                                                                    maxValue=25,
                                                                    step=1,
                                                                    minSize=QSize(60, const.HEIGHT),
                                                                    valueChanged=self.maxWorkerThreadCountChanged)
        hbox.addWidget(self.maxWorkerThreadCountSpinBox)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hbox, 1)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="启动压缩", onClicked=self.startPicCompress))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hbox, 1)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="压缩进度：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(50, const.HEIGHT)))
        self.compressProgressBar = WidgetUtil.createProgressBar(box, value=0, format="%p%", textVisible=True,
                                                                sizePolicy=sizePolicy)
        hbox.addWidget(self.compressProgressBar)
        self.progressTextLabel = WidgetUtil.createLabel(box, text="", alignment=Qt.AlignVCenter | Qt.AlignHCenter,
                                                        minSize=QSize(100, const.HEIGHT))
        hbox.addWidget(self.progressTextLabel)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hbox, 1)

        vbox1 = WidgetUtil.createVBoxLayout(spacing=10)
        self.compressResTableView = WidgetUtil.createTableView(box, sizePolicy=sizePolicy)
        vbox1.addWidget(self.compressResTableView)
        vLayout.addLayout(vbox1, 12)
        return box

    def getTinifyApiKeys(self):
        return JsonUtil.decode(self.operaIni.getValue("keys", "tinify"))

    def setTinifyApiKeys(self, keys: []):
        self.operaIni.addItem("tinify", "keys", JsonUtil.encode(keys))
        self.operaIni.saveIni()

    def getConfig(self, key: str):
        return self.operaIni.getValue(key, CONFIG_SECTION)

    def setConfig(self, key: str, value: str):
        self.operaIni.addItem(CONFIG_SECTION, key, value)
        self.operaIni.saveIni()
        pass

    def getSrcFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.srcFilePathLineEdit.setText(fp)
            self.setConfig(KEY_SRC_FILE_DIR_PATH, fp)
        pass

    def getDstFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.dstFilePathLineEdit.setText(fp)
            self.setConfig(KEY_DST_FILE_DIR_PATH, fp)
        pass

    def exchangeDirs(self):
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        dstFileDirPath = self.dstFilePathLineEdit.text().strip()

        self.srcFilePathLineEdit.setText(dstFileDirPath)
        self.setConfig(KEY_SRC_FILE_DIR_PATH, dstFileDirPath)

        self.dstFilePathLineEdit.setText(srcFileDirPath)
        self.setConfig(KEY_DST_FILE_DIR_PATH, srcFileDirPath)
        pass

    def metaDataCheckChanged(self):
        self.metaDataList.clear()
        for i in range(0, len(META_DATA_LIST)):
            if self.metaDataBtns[i].isChecked():
                self.metaDataList.append(META_DATA_LIST[i])
        LogUtil.d("metaDataCheckChanged", self.metaDataList)
        pass

    def srcFnTextChanged(self, data):
        if not data:
            self.dstFnPatternsLineEdit.setEnabled(False)
            return
        srcFnPs = data.split(";")
        # 查找需要修改的图片列表
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        srcFiles = FileUtil.findFilePathList(srcFileDirPath, srcFnPs)
        if len(srcFiles) == 1:
            self.dstFnPatternsLineEdit.setEnabled(True)
        else:
            self.dstFnPatternsLineEdit.setEnabled(False)

    def maxWorkerThreadCountChanged(self):
        maxWorkerThreadCount = self.maxWorkerThreadCountSpinBox.value()
        self.setConfig(KEY_MAX_WORKER_THREAD_COUNT, str(maxWorkerThreadCount))
        LogUtil.d("maxWorkerThreadCountChanged", maxWorkerThreadCount)
        pass

    def setCompressPicProgress(self, cur, totalCount):
        self.compressProgressBar.setMaximum(totalCount)
        self.compressProgressBar.setValue(cur)
        self.progressTextLabel.setText(f"{cur}/{totalCount}")
        # 触发实时显示数据
        QApplication.instance().processEvents()

    def startPicCompress(self):
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件目录")
            return
        dstFileDirPath = self.dstFilePathLineEdit.text().strip()
        if not dstFileDirPath:
            dstFileDirPath = srcFileDirPath
        while dstFileDirPath.endswith("/") or dstFileDirPath.endswith("\\"):
            dstFileDirPath = dstFileDirPath[:len(dstFileDirPath) - 1]
        LogUtil.d("目标目录：", dstFileDirPath)
        srcFnPatterns = self.srcFnPatternsLineEdit.text().strip()
        if not srcFnPatterns:
            srcFnPatterns = ".*.((jpg)|(JPG)|(png)|(PNG)|(JPEG)|(jpeg))"
        srcFnPs = srcFnPatterns.split(";")
        LogUtil.d("源图片文件名正则匹配表达式：", srcFnPs)

        dstFnPs = self.dstFnPatternsLineEdit.text().strip()
        LogUtil.d("目标图片文件名：", dstFnPs)

        # 查找需要修改的图片列表
        srcFiles = FileUtil.findFilePathList(srcFileDirPath, srcFnPs)
        if srcFiles:
            self.setCompressPicProgress(0, len(srcFiles))
            self.compressRes.clear()
            self.compressPicByThread(srcFiles, srcFileDirPath, dstFileDirPath, dstFnPs)
        else:
            WidgetUtil.showErrorDialog(message="指定目录下未查找到指定的图片文件")
        pass

    def compressPicByThread(self, srcFiles, srcFileDirPath, dstFileDirPath, dstFnPs):
        LogUtil.d("compressPicByThread")
        with ThreadPoolExecutor(max_workers=self.maxWorkerThreadCount) as t:
            futureList = []
            for srcFile in srcFiles:
                dstFile = srcFile.replace(srcFileDirPath, dstFileDirPath, 1)
                if len(srcFiles) == 1 and dstFnPs:
                    fp, fn = os.path.split(dstFile)  # 分离文件名和路径
                    dstFile = os.path.join(fp, dstFnPs)

                argRes = {"srcFile": srcFile, "srcFileName": FileUtil.getFileName(srcFile),
                          "srcFileSize": FileUtil.readFileSize(srcFile),
                          "dstFile": dstFile, "dstFileName": FileUtil.getFileName(dstFile)}
                self.compressRes.append(argRes)
                future = t.submit(self.picCompress,
                                  (argRes, self.metaDataList if self.metaDataList else None,))
                futureList.append(future)

            compressFinishedCount = 0
            for future in as_completed(futureList):
                compressFinishedCount += 1
                self.setCompressPicProgress(compressFinishedCount, len(srcFiles))
                data = future.result()
                LogUtil.e(f"main: {data}")

            LogUtil.d("all pic compress finished", self.compressRes)
            WidgetUtil.addTableViewData(self.compressResTableView, data=self.compressRes,
                                        ignoreCol=["srcFile", "dstFile", "msg"],
                                        headerLabels=["源文件", "源文件大小", "压缩文件", "压缩文件大小", "压缩比"])

    def picCompress(self, args: ()):
        (argRes, preserves) = args
        srcFp = argRes.get("srcFile")
        dstFp = argRes.get("dstFile")
        LogUtil.d("picCompress start.", srcFp, dstFp, preserves)
        if not self.apiKeys:
            # 子线程不能显示dialog
            # WidgetUtil.showErrorDialog(message="请添加tinypng API key。（https://tinypng.com/developers 可以注册）")
            return "keyEmpty", "api keys is empty. Please config."
        # 获取锁，用于线程同步
        threadLock.acquire()
        apiKey = self.apiKeys[self.apiKeyIndex]
        while not TinifyUtil.validate(apiKey):
            if self.apiKeyIndex == len(self.apiKeys) - 1:
                # 子线程不能显示dialog
                # WidgetUtil.showErrorDialog(message="请检查网络或是否API key有效。")
                LogUtil.d("api keys all invalid or network invalid.")
                threadLock.release()
                return "invalid", "api keys all invalid or network invalid. "
            else:
                self.apiKeyIndex += 1
                apiKey = self.apiKeys[self.apiKeyIndex]
        # 释放锁
        threadLock.release()

        argRes["msg"] = TinifyUtil.compressing(apiKey, srcFp, dstFp, preserves)
        argRes["dstFileSize"] = FileUtil.readFileSize(dstFp)
        argRes["compressRatio"] = f'{round((argRes["srcFileSize"] - argRes["dstFileSize"]) / float(argRes["srcFileSize"]) * 100, 2)}%'
        return "success", argRes
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompressPicDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
