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
from util.StrUtil import StrUtil
from widget.projectManage.ProjectManager import KEY_CHECK_CODE_MODIFY

KEY_NAME = 'name'
KEY_VALUE = 'value'

KEY_PROGRAM = "program"
KEY_ARGUMENTS = "arguments"
KEY_WORKING_DIR = "workingDir"
KEY_CONDITION_INPUT = 'conditionInput'
KEY_EVN_IS_PATH = 'isPath'

TAG = "ProcessManager"

# git status 本地有代码修改时会输出的log
LOG_GIT_LOCAL_MODIFY = ["Changes to be committed", "Changes not staged for commit", "Your branch is ahead of "]


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
        # 执行程序是否需要特殊处理
        self.needSpecialHandler = False
        self.log = ""
        self.resultData = None
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
            if not self.isSuccess:
                break
        self.handleStandardOutput(f"执行结束。耗时：{DateUtil.nowTimestamp(isMilliSecond=True) - startTime} ms\n")
        self.destroy()
        return self.isSuccess, self.name, self.resultData

    def executeCmd(self, cmdInfo):
        workingDir = DictUtil.get(cmdInfo, KEY_WORKING_DIR)
        if not workingDir:
            workingDir = self.workingDir
        self.process.setWorkingDirectory(workingDir)
        program = DictUtil.get(cmdInfo, KEY_PROGRAM, "")
        args = DictUtil.get(cmdInfo, KEY_ARGUMENTS, "")
        cmd = f"{program} {args}"
        self.handleStandardOutput(f"executeCmd: {cmd} start. \nworkingDir: {workingDir}\n")
        self.lock.acquire()
        if self.needFinished:
            self.lock.release()
            return
        self.lock.release()
        if "git" in program:
            self.needSpecialHandler = True
            if "pull" in args:
                self.gitUpdateCode(cmdInfo=cmdInfo)
            elif KEY_CHECK_CODE_MODIFY in args:
                self.gitCheckCodeModify(cmdInfo=cmdInfo)
            else:
                self.needSpecialHandler = False
                self.log = ""
                self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
        else:
            self.needSpecialHandler = False
            self.log = ""
            self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
        pass

    def gitUpdateCode(self, cmdInfo):
        needStash = self.isModifyCode(cmdInfo=cmdInfo)
        if needStash:
            cmd = f'git stash save "stash by tools on {DateUtil.nowTime()}"'
            self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
        cmd = "git pull --rebase"
        self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
        if "Permission denied" in self.log:
            self.isSuccess = False
            self.handleStandardError("您代码更新需要密码")
            return
        if needStash:
            cmd = "git stash pop"
            self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
            if "Merge conflict in" in self.log:
                self.isSuccess = False
        pass

    def gitCheckCodeModify(self, cmdInfo):
        self.resultData = self.isModifyCode(cmdInfo=cmdInfo)
        pass

    def isModifyCode(self, cmdInfo):
        cmd = "git status"
        self.runCmd(cmd=cmd, cmdInfo=cmdInfo)
        return StrUtil.containsStr(self.log, LOG_GIT_LOCAL_MODIFY)

    def runCmd(self, cmd, cmdInfo):
        self.handleStandardOutput(f"runCmd: {cmd}")
        self.process.start(cmd)

        self.process.readyReadStandardOutput.connect(lambda: self.readStandardOutput(cmdInfo))
        self.process.readyReadStandardError.connect(lambda: self.readStandardError(cmdInfo))

        self.process.waitForReadyRead()
        self.process.waitForFinished(-1)
        LogUtil.d(TAG, f"runCmd: {cmd} end.", self.process.state(), self.process.exitCode(),
                  self.process.exitStatus(),
                  self.process.error())
        pass

    def readStandardOutput(self, cmdInfo):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardOutput())
        if log:
            if self.needSpecialHandler:
                self.log += log
            self.handleConditionInput(cmdInfo, log)
            self.handleStandardOutput(log)

    def handleStandardOutput(self, log):
        self.standardOutput.emit(
            f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.current_thread().ident} {self.name} {log}")

    def readStandardError(self, cmdInfo):
        log = QTextCodec.codecForLocale().toUnicode(self.process.readAllStandardError())
        if log:
            if self.needSpecialHandler:
                self.log += log
            self.handleConditionInput(cmdInfo, log)
            self.handleStandardError(log)

    def handleStandardError(self, log):
        self.standardError.emit(
            f"{DateUtil.nowTimeMs()} {os.getpid()} {threading.current_thread().ident} {self.name} {log}")
        pass

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
        self.isSuccess = False
        self.lock.release()
        self.destroy()
        LogUtil.d(TAG, f"{self.name} kill process.")
        pass

    def destroy(self):
        self.log = ""
        if self.process:
            try:
                self.process.kill()
            except Exception as ex:
                LogUtil.e(TAG, "kill process Exception", ex)
        pass

    def getName(self):
        return self.name


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
