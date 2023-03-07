# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProcessManager.py
# 定义一个ProcessManager工具类实现调用外部进程相关的功能
import os
import threading

from PyQt5.QtCore import QProcess, QProcessEnvironment, QTextCodec, pyqtSignal, QObject

from util.DateUtil import DateUtil
from util.DictUtil import DictUtil
from util.LogUtil import LogUtil

KEY_NAME = 'name'
KEY_VALUE = 'value'

KEY_PROGRAM = "program"
KEY_ARGUMENTS = "arguments"
KEY_WORKING_DIR = "workingDir"
KEY_CONDITION_INPUT = 'conditionInput'
KEY_EVN_IS_PATH = 'isPath'

TAG = "ProcessManager"


class ProcessManager(QObject):
    standardOutput = pyqtSignal(str)
    standardError = pyqtSignal(str)

    def __init__(self, name='', cmdList=[], workingDir="./", processEnv=[], standardOutput=None, standardError=None):
        QObject.__init__(self)
        self.name = name
        self.cmdList = cmdList
        self.workingDir = workingDir
        self.processEnv = processEnv
        self.process = None
        self.needFinished = False
        self.lock = threading.RLock()

        LogUtil.d(TAG, name, cmdList, workingDir, processEnv)
        if standardOutput:
            self.standardOutput.connect(standardOutput)
        if standardError:
            self.standardError.connect(standardError)
        self.isSuccess = True

    def run(self):
        startTime = DateUtil.nowTimestamp(isMilliSecond=True)
        self.handleStandardOutput(f'开始执行 {threading.current_thread().ident}\n')
        # 必须放到run方法里，不然多线程在构造函数里创建就会出现需要用户输入时一直没有StandardOutput
        self.process = QProcess()
        # 必须将系统环境变量也一起设置进去，不然会出现指令找不到、没有操作路径权限的情况
        env: QProcessEnvironment = QProcessEnvironment.systemEnvironment()
        for item in self.processEnv:
            if DictUtil.get(item, KEY_EVN_IS_PATH, False):
                env.insert("PATH", item[KEY_VALUE] + os.pathsep + env.value("PATH", ""))
            else:
                env.insert(item[KEY_NAME], item[KEY_VALUE])
        LogUtil.d(TAG, "processEnvironment", env.toStringList())
        self.process.setProcessEnvironment(env)

        for cmd in self.cmdList:
            self.lock.acquire()
            if self.needFinished:
                self.lock.release()
                break
            self.lock.release()
            self.executeCmd(cmd)
        self.handleStandardOutput(f"执行结束。耗时：{DateUtil.nowTimestamp(isMilliSecond=True) - startTime} ms\n")
        return self.isSuccess, self.name

    def executeCmd(self, cmdInfo):
        workingDir = DictUtil.get(cmdInfo, KEY_WORKING_DIR)
        if not workingDir:
            workingDir = self.workingDir
        self.process.setWorkingDirectory(workingDir)
        args = DictUtil.get(cmdInfo, KEY_ARGUMENTS)
        cmd = f"{DictUtil.get(cmdInfo, KEY_PROGRAM)} {args if args else ''}"
        self.handleStandardOutput(f"executeCmd: {cmd} start. \nworkingDir: {workingDir}\n")
        self.lock.acquire()
        if self.needFinished:
            self.lock.release()
            return
        self.lock.release()
        self.process.start(cmd)

        self.process.readyReadStandardOutput.connect(lambda: self.readStandardOutput(cmdInfo))
        self.process.readyReadStandardError.connect(lambda: self.readStandardError(cmdInfo))

        self.process.waitForReadyRead()
        self.process.waitForFinished(-1)
        LogUtil.d(TAG, f"executeCmd: {cmd} end.", self.process.state(), self.process.exitCode(), self.process.exitStatus(),
                  self.process.error())

    def readStandardOutput(self, cmdInfo):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardOutput())
        if log:
            self.handleConditionInput(cmdInfo, log)
            self.handleStandardOutput(log)

    def handleStandardOutput(self, log):
        self.standardOutput.emit(f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.current_thread().ident} {self.name} {log}")

    def readStandardError(self, cmdInfo):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardError())
        if log:
            self.handleConditionInput(cmdInfo, log)
            self.handleStandardError(log)

    def handleStandardError(self, log):
        self.standardError.emit(f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.current_thread().ident} {self.name} {log}")
        self.isSuccess = False

    def handleConditionInput(self, cmdInfo, log):
        conditionInput = DictUtil.get(cmdInfo, KEY_CONDITION_INPUT, [])
        for item in conditionInput:
            for key in item:
                if key in log:
                    LogUtil.e(TAG, "handleConditionInput", item[key])
                    self.process.write(item[key].encode('utf-8'))
                    self.handleStandardOutput(f"自动输入\n{key} ----> {item[key]}")
        pass

    def kill(self):
        self.lock.acquire()
        self.needFinished = True
        self.lock.release()
        if self.process:
            try:
                self.process.kill()
            except Exception as ex:
                LogUtil.e(TAG, "kill process Exception", ex)
        LogUtil.d(TAG, f"{self.name} kill process.")
        pass


if __name__ == "__main__":
    processThread = ProcessManager(
        name="test",
        cmdList=[
            {KEY_PROGRAM: 'ls'},
            {KEY_PROGRAM: 'ls', KEY_ARGUMENTS: "-l"},
            {KEY_PROGRAM: 'ls', KEY_WORKING_DIR: "../"},
            {KEY_PROGRAM: 'ls', KEY_ARGUMENTS: "-l", KEY_WORKING_DIR: "../"}
        ],
        processEnv=[
            {KEY_NAME: "aa", KEY_VALUE: "aa"},
            {KEY_NAME: "ddd", KEY_VALUE: "ddd", KEY_EVN_IS_PATH: True},
            {KEY_NAME: "ccc", KEY_VALUE: "ccc", KEY_EVN_IS_PATH: True}
        ],
        standardOutput=lambda log: LogUtil.d(TAG, log),
        standardError=lambda log: LogUtil.e(TAG, log))
    processThread.run()
    pass
