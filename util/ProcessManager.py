# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProcessManager.py
# 定义一个ProcessManager工具类实现调用外部进程相关的功能
import os
import threading
from time import sleep

from PyQt5.QtCore import QProcess, QProcessEnvironment, QTextCodec, pyqtSignal, QObject

from util.DateUtil import DateUtil
from util.DictUtil import DictUtil
from util.LogUtil import LogUtil

KEY_NAME = 'name'
KEY_VALUE = 'value'

KEY_PROGRAM = "program"
KEY_ARGUMENTS = "arguments"
KEY_WORKING_DIR = "workingDir"


class ProcessManager(QObject):
    standardOutput = pyqtSignal(str)
    standardError = pyqtSignal(str)

    def __init__(self, name='', cmdList=[], workingDir="./", processEnv=[], standardOutput=None, standardError=None):
        QObject.__init__(self)
        self.name = name
        self.cmdList = cmdList
        self.workingDir = workingDir

        self.process = QProcess()
        env: QProcessEnvironment = self.process.processEnvironment()
        for item in processEnv:
            env.insert(item[KEY_NAME], item[KEY_VALUE])
        LogUtil.d("processEnvironment", env.toStringList())
        self.process.setProcessEnvironment(env)

        if standardOutput:
            self.standardOutput.connect(standardOutput)
        if standardError:
            self.standardError.connect(standardError)
        self.isSuccess = True
        pass

    def run(self):
        startTime = DateUtil.nowTimestamp(isMilliSecond=True)
        self.handleStandardOutput(f'{self.name} 开始执行 {threading.currentThread().ident}\n')
        # sleep(115)
        for cmd in self.cmdList:
            self.executeCmd(cmd)
        self.handleStandardOutput(f"{self.name} 执行结束。耗时：{DateUtil.nowTimestamp(isMilliSecond=True) - startTime} ms\n")
        return self.isSuccess

    def executeCmd(self, cmdInfo):
        workingDir = DictUtil.get(cmdInfo, KEY_WORKING_DIR)
        if not workingDir:
            workingDir = self.workingDir
        self.process.setWorkingDirectory(workingDir)
        args = DictUtil.get(cmdInfo, KEY_ARGUMENTS)
        cmd = f"{DictUtil.get(cmdInfo, KEY_PROGRAM)} {args if args else ''}"
        self.handleStandardOutput(f"executeCmd: {cmd} start. workingDir: {workingDir}\n")
        self.handleStandardOutput(f"执行指令：{cmd}\n")
        self.process.start(cmd)
        # self.process.start("lsss")
        # 必须执行了程序后设置读取输出才有效
        self.process.readyReadStandardOutput.connect(lambda: self.readStandardOutput())
        self.process.readyReadStandardError.connect(lambda: self.readStandardError())
        # self.process.waitForReadyRead()
        self.process.waitForFinished()
        LogUtil.d(f"executeCmd: {cmd} end.", self.process.state(), self.process.exitCode(), self.process.exitStatus(),
                  self.process.error())

    def readStandardOutput(self):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardOutput())
        self.handleStandardOutput(log)

    def handleStandardOutput(self, log):
        if log:
            self.standardOutput.emit(f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.currentThread().ident} {log}")

    def readStandardError(self):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardError())
        self.handleStandardError(log)

    def handleStandardError(self, log):
        if log:
            self.standardError.emit(f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.currentThread().ident} {log}")
        self.isSuccess = False

    def kill(self):
        self.process.kill()
        pass


if __name__ == "__main__":
    processThread = ProcessManager(name="test", cmdList=[
        {KEY_PROGRAM: 'ls'},
        {KEY_PROGRAM: 'ls', KEY_ARGUMENTS: "-l"},
        {KEY_PROGRAM: 'ls', KEY_WORKING_DIR: "../"},
        {KEY_PROGRAM: 'ls', KEY_ARGUMENTS: "-l", KEY_WORKING_DIR: "../"}
    ], processEnv=[{KEY_NAME: "aa", KEY_VALUE: "dd"}])
    processThread.run()
    pass
