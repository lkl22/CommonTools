# -*- coding: utf-8 -*-
# python 3.x
# Filename: CompressPicDialog.py
# 定义一个CompressPicDialog类实现图片压缩的功能
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

META_DATA_NICKNAME_LIST = ['版权信息', '创建日期时间', '位置信息']
META_DATA_LIST = ['copyright', 'creation', 'location']

CONFIG_SECTION = 'PictureCompress'
KEY_SRC_FILE_DIR_PATH = 'srcFileDirPath'
KEY_DST_FILE_DIR_PATH = 'dstFileDirPath'
KEY_MAX_WORKER_THREAD_COUNT = 'maxWorkerThreadCount'

threadLock = threading.Lock()


class CompressPicDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Compress Pic Dialog")
        self.setObjectName("CompressPicDialog")
        self.resize(CompressPicDialog.WINDOW_WIDTH, CompressPicDialog.WINDOW_HEIGHT)
        self.setFixedSize(CompressPicDialog.WINDOW_WIDTH, CompressPicDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="图片压缩工具"))

        if isDebug:
            self.operaIni = OperaIni("../../resources/config/BaseConfig.ini")
        else:
            self.operaIni = OperaIni(FileUtil.getProjectPath() + "/resources/config/BaseConfig.ini")
        self.maxWorkerThreadCount = int(self.getConfig(KEY_MAX_WORKER_THREAD_COUNT))
        if not self.maxWorkerThreadCount:
            self.maxWorkerThreadCount = 5
        self.apiKeys = self.getTinifyApiKeys()
        self.apiKeyIndex = 0

        self.metaDataList = []
        self.metaDataBtns = []
        self.compressRes = []

        vLayout = WidgetUtil.createVBoxWidget(self, margins=QMargins(0, 0, 0, 0),
                                              geometry=QRect(const.PADDING, const.PADDING,
                                                             CompressPicDialog.WINDOW_WIDTH - const.PADDING * 2,
                                                             CompressPicDialog.WINDOW_HEIGHT - const.PADDING * 2))

        apiKeyConfigGroupBox = self.createApiKeyConfigGroupBox(self)
        picCompressGroupBox = self.createPicCompressGroupBox(self)

        vLayout.addWidget(apiKeyConfigGroupBox)
        vLayout.addWidget(picCompressGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createApiKeyConfigGroupBox(self, parent):
        width = CompressPicDialog.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="TinyPng API Key Config", minSize=QSize(width, 100))
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = CompressPicDialog.WINDOW_WIDTH - const.PADDING * 4

        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))

        WidgetUtil.createLabel(splitter, text="请输入要添加的API key：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT))
        self.apiKeysLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy,
                                                         holderText="请输入要添加的API key，多个以\";\"分隔。（https://tinypng.com/developers 可以注册）",
                                                         textChanged=self.srcFnTextChanged)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 150, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="添加key", onClicked=self.addApiKeys)
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

        yPos = const.GROUP_BOX_MARGIN_TOP
        width = CompressPicDialog.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, int(const.HEIGHT * 2.5)))
        vLayout = WidgetUtil.createVBoxWidget(splitter, margins=QMargins(0, 0, 0, 0), sizePolicy=sizePolicy)

        vLayout1 = WidgetUtil.createVBoxWidget(splitter, margins=QMargins(20, 0, 10, 0))
        btn = WidgetUtil.createPushButton(splitter, text="", fixedSize=QSize(30, 40),
                                          styleSheet="background-color: white",
                                          iconSize=QSize(30, 40),
                                          # icon=QIcon(FileUtil.getIconFp('androidRes/exchange.png')),
                                          icon=QIcon("../../resources/icons/androidRes/exchange.png"),
                                          onClicked=self.exchangeDirs)
        vLayout1.addWidget(btn)

        srcFileDirPath = ''
        if self.getConfig(KEY_SRC_FILE_DIR_PATH):
            srcFileDirPath = self.getConfig(KEY_SRC_FILE_DIR_PATH)
        splitter = WidgetUtil.createSplitter(box,
                                             geometry=QRect(const.PADDING, yPos, width - const.HEIGHT, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, text=srcFileDirPath, isEnable=False,
                                                             sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box,
                                             geometry=QRect(const.PADDING, yPos, width - const.HEIGHT, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="目标文件路径", onClicked=self.getDstFilePath)
        dstFileDirPath = ''
        if self.getConfig(KEY_DST_FILE_DIR_PATH):
            dstFileDirPath = self.getConfig(KEY_DST_FILE_DIR_PATH)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, text=dstFileDirPath, holderText="不填跟源路径一样",
                                                             sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="源图片匹配正则表达式：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy,
                                                               holderText="请输入源图片文件名称正则表达式，多个以\";\"分隔。默认源目录下所有图片",
                                                               isEnable=True if srcFileDirPath else False,
                                                               textChanged=self.srcFnTextChanged)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="目标图片文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT))
        self.dstFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy, isEnable=False,
                                                               holderText="请输入目标图片文件名称。只有一个源图片文件名时有效，无效时以源文件名作为目标文件名")

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="选择保留的元数据：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT))

        for i in range(len(META_DATA_NICKNAME_LIST)):
            self.metaDataBtns.append(WidgetUtil.createCheckBox(splitter, text=META_DATA_NICKNAME_LIST[i] + "  ",
                                                               stateChanged=self.metaDataCheckChanged))

        WidgetUtil.createLabel(splitter, text="", sizePolicy=WidgetUtil.createSizePolicy())

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 300, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="同时压缩文件数量：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(140, const.HEIGHT))
        self.maxWorkerThreadCountSpinBox = WidgetUtil.createSpinBox(splitter,
                                                                    value=self.maxWorkerThreadCount,
                                                                    minValue=3,
                                                                    maxValue=25,
                                                                    step=1,
                                                                    sizePolicy=sizePolicy,
                                                                    valueChanged=self.maxWorkerThreadCountChanged)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 150, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="启动压缩", onClicked=self.startPicCompress)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 600, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="压缩进度：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(50, const.HEIGHT))
        self.compressProgressBar = WidgetUtil.createProgressBar(splitter, value=0, format="%p%", textVisible=True,
                                                                sizePolicy=sizePolicy)
        self.progressTextLabel = WidgetUtil.createLabel(splitter, text="", alignment=Qt.AlignVCenter | Qt.AlignHCenter,
                                                        minSize=QSize(100, const.HEIGHT))
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

                argRes = {"srcFile": srcFile, "dstFile": dstFile, "srcFileSize": FileUtil.readFileSize(srcFile)}
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

    def picCompress(self, args: ()):
        (argRes, preserves) = args
        srcFp = argRes.get("srcFile")
        dstFp = argRes.get("dstFile")
        LogUtil.d("picCompress start.", srcFp, dstFp, preserves)
        if not self.apiKeys:
            WidgetUtil.showErrorDialog(message="请添加tinypng API key。（https://tinypng.com/developers 可以注册）")
            return "api keys is empty. Please config."
        # 获取锁，用于线程同步
        threadLock.acquire()
        apiKey = self.apiKeys[self.apiKeyIndex]
        while not TinifyUtil.validate(apiKey):
            if self.apiKeyIndex == len(self.apiKeys) - 1:
                WidgetUtil.showErrorDialog(message="请检查网络或是否API key有效。")
                threadLock.release()
                return "api keys all invalid or network invalid. "
            else:
                self.apiKeyIndex += 1
                apiKey = self.apiKeys[self.apiKeyIndex]
        # 释放锁
        threadLock.release()

        argRes["msg"] = TinifyUtil.compressing(apiKey, srcFp, dstFp, preserves)
        argRes["dstFileSize"] = FileUtil.readFileSize(dstFp)
        argRes["compressRatio"] = round((argRes["srcFileSize"] - argRes["dstFileSize"]) / float(argRes["srcFileSize"]) * 100, 2)
        return argRes
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompressPicDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
