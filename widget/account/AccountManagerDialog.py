# -*- coding: utf-8 -*-
# python 3.x
# Filename: AccountManagerDialog.py
# 定义一个AccountManagerDialog类实现账号管理相关功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.WidgetConst import *
from util.ClipboardUtil import ClipboardUtil
from util.DialogUtil import *
from util.OperaIni import *
from util.ReUtil import ReUtil
from util.CipherUtil import CipherUtil
from widget.account.AccountManager import *


class AccountManagerDialog(QtWidgets.QDialog):
    AES_KEY = "1234567812345678"

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AccountManagerDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AccountManagerDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d("Account Manager Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="账号管理"))

        self.setObjectName("AccountManagerDialog")
        self.resize(AccountManagerDialog.WINDOW_WIDTH, AccountManagerDialog.WINDOW_HEIGHT)
        # self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)

        self.isDebug = isDebug
        self.accountManager = AccountManager(isDebug=isDebug)
        self.flavors = self.accountManager.flavors
        if not self.flavors:
            self.flavors = {KEY_DEFAULT: None, KEY_LIST: []}
        self.countries = self.accountManager.countries
        if not self.countries:
            self.countries = {KEY_DEFAULT: None, KEY_LIST: []}
        self.curFlavorInfo = self.flavors[KEY_DEFAULT]
        self.curCountryInfo = self.countries[KEY_DEFAULT]
        # 当前账号列表对应的key
        self.curAccountsInfoKey = None
        self.accounts = None
        self.curAccountInfo = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.accountManagerGroupBox = self.createAccountManagerGroupBox(self)
        vLayout.addWidget(self.accountManagerGroupBox)

        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createAccountManagerGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent)
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入密码加密的密钥：", minSize=QSize(150, const.HEIGHT)))
        self.aesKeyLineEdit = WidgetUtil.createLineEdit(box, text=AccountManagerDialog.AES_KEY,
                                                        holderText="请输入16个字符，用于加解密密码数据，请自己妥善保管，以免信息泄漏",
                                                        toolTip="用于解密数据的密钥，请自己妥善保管，以免信息泄漏",
                                                        echoMode=QtWidgets.QLineEdit.Password,
                                                        editingFinished=self.aesKeyChanged)
        hbox.addWidget(self.aesKeyLineEdit)
        self.showOrHideAesKeyBtn = WidgetUtil.createPushButton(box, text="显示", onClicked=self.showOrHideAesKey)
        hbox.addWidget(self.showOrHideAesKeyBtn)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Copy", onClicked=self.copyAesKeyToClipboard))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择渠道信息：", minSize=QSize(150, const.HEIGHT)))
        self.flavorsComboBox = WidgetUtil.createComboBox(box, activated=self.flavorIndexChanged)
        self.updateFlavorComboBox()
        hbox.addWidget(self.flavorsComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加渠道", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.addFlavor))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择国家：", minSize=QSize(150, const.HEIGHT)))
        self.countriesComboBox = WidgetUtil.createComboBox(box, activated=self.countryIndexChanged)
        self.updateCountriesComboBox()
        hbox.addWidget(self.countriesComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加国家", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.addCountry))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加账号", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.addAccount))
        vbox.addLayout(hbox)

        tableBox = WidgetUtil.createVBoxLayout(box)
        self.accountTableView = WidgetUtil.createTableView(box, doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.accountTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.accountTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.accountTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.accountTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.accountTableView.customContextMenuRequested.connect(self.customRightMenu)
        tableBox.addWidget(self.accountTableView)
        vbox.addLayout(tableBox, 1)

        self.updateAccountInfoTableView()
        return box

    def aesKeyChanged(self):
        aesKey = self.aesKeyLineEdit.text().strip()
        if not ReUtil.match(aesKey, ".{16}"):
            WidgetUtil.showAboutDialog(text="请输入16位的密钥，否则会引起密码加解密问题。")
        else:
            AccountManagerDialog.AES_KEY = aesKey
        pass

    def showOrHideAesKey(self):
        LogUtil.d("showOrHideAesKey")
        if self.aesKeyLineEdit.echoMode() == QLineEdit.Password:
            self.aesKeyLineEdit.setEchoMode(QLineEdit.Normal)
            self.showOrHideAesKeyBtn.setText("隐藏")
        else:
            self.aesKeyLineEdit.setEchoMode(QLineEdit.Password)
            self.showOrHideAesKeyBtn.setText("显示")
        pass

    def copyAesKeyToClipboard(self):
        LogUtil.d("copyAesKeyToClipboard")
        ClipboardUtil.copyToClipboard(AccountManagerDialog.AES_KEY)
        pass

    def updateFlavorComboBox(self):
        if self.flavors and self.flavors[KEY_LIST]:
            self.flavorsComboBox.clear()
            for index, item in enumerate(self.flavors[KEY_LIST]):
                self.flavorsComboBox.addItem(item[KEY_DESC], item)
            if not self.curFlavorInfo:
                self.curFlavorInfo = self.flavors[KEY_LIST][0]
            self.flavorsComboBox.setCurrentText(self.curFlavorInfo[KEY_DESC])
            LogUtil.d('updateFlavorComboBox setCurrentText', self.curFlavorInfo)
        pass

    def flavorIndexChanged(self, index):
        flavorInfo = self.flavorsComboBox.currentData()
        if flavorInfo:
            self.curFlavorInfo = flavorInfo
        LogUtil.d('flavorIndexChanged', index, self.curFlavorInfo, flavorInfo)
        self.updateFlavorInfo()
        pass

    def addFlavor(self):
        LogUtil.d("addFlavor")
        AddFlavorDialog(flavorList=self.flavors[KEY_LIST], callback=self.addFlavorCallback, isDebug=self.isDebug).show()
        pass

    def addFlavorCallback(self, flavorName, flavorDesc):
        LogUtil.d("addFlavorCallback", flavorName, flavorDesc)
        flavorList = self.flavors[KEY_LIST]

        flavorList.append({KEY_FLAVOR_NAME: flavorName, KEY_DESC: flavorDesc})
        self.flavors[KEY_LIST] = sorted(flavorList, key=lambda x: x[KEY_DESC])
        self.updateFlavorComboBox()
        self.updateFlavorInfo()
        pass

    def updateFlavorInfo(self):
        self.flavors[KEY_DEFAULT] = self.curFlavorInfo
        self.accountManager.saveFlavorInfos(self.flavors)
        self.updateAccountInfoTableView()
        pass

    def updateCountriesComboBox(self):
        if self.countries and self.countries[KEY_LIST]:
            self.countriesComboBox.clear()
            for index, item in enumerate(self.countries[KEY_LIST]):
                self.countriesComboBox.addItem(item[KEY_DESC], item)
            if not self.curCountryInfo:
                self.curCountryInfo = self.countries[KEY_LIST][0]
            self.countriesComboBox.setCurrentText(self.curCountryInfo[KEY_DESC])
            LogUtil.d('updateCountriesComboBox setCurrentText', self.curCountryInfo)
        pass

    def countryIndexChanged(self, index):
        countryInfo = self.countriesComboBox.currentData()
        if countryInfo:
            self.curCountryInfo = countryInfo
        LogUtil.d('countryIndexChanged', index, self.curCountryInfo, countryInfo)
        self.updateCountryInfo()
        pass

    def addCountry(self):
        LogUtil.d("addCountry")
        AddCountryDialog(countryList=self.countries[KEY_LIST], callback=self.addCountryCallback,
                         isDebug=self.isDebug).show()
        pass

    def addCountryCallback(self, countryCode, countryDesc):
        LogUtil.d("addCountryCallback", countryCode, countryDesc)
        countryList = self.countries[KEY_LIST]

        countryList.append({KEY_COUNTRY_CODE: countryCode, KEY_DESC: countryDesc})
        self.countries[KEY_LIST] = sorted(countryList, key=lambda x: x[KEY_DESC])
        self.updateCountriesComboBox()
        self.updateCountryInfo()
        pass

    def updateCountryInfo(self):
        self.countries[KEY_DEFAULT] = self.curCountryInfo
        self.accountManager.saveCountryInfos(self.countries)
        self.updateAccountInfoTableView()
        pass

    def updateAccountInfoTableView(self):
        if not self.curFlavorInfo or not self.curCountryInfo:
            return
        accountsInfoKey = self.curFlavorInfo[KEY_FLAVOR_NAME] + self.curCountryInfo[KEY_COUNTRY_CODE]
        LogUtil.d("updateAccountInfo", accountsInfoKey, self.curAccountsInfoKey)
        if self.curAccountsInfoKey != accountsInfoKey:
            self.curAccountsInfoKey = accountsInfoKey
            self.accounts = self.accountManager.getAccountInfos(accountsInfoKey)

        if not self.accounts or not self.accounts[KEY_LIST]:
            self.accounts = {KEY_DEFAULT: None, KEY_LIST: []}
        WidgetUtil.addTableViewData(self.accountTableView, self.accounts[KEY_LIST], ignoreCol=[KEY_PWD],
                                    headerLabels=["账号", "昵称", "描述"])
        pass

    def addAccount(self):
        LogUtil.d("addAccount")
        if not self.curFlavorInfo or not self.curCountryInfo:
            WidgetUtil.showErrorDialog(message="请先设置渠道和国家")
            return
        if not self.accounts or not self.accounts[KEY_LIST]:
            self.accounts = {KEY_DEFAULT: None, KEY_LIST: []}
        accountList = self.accounts[KEY_LIST]
        AddOrEditAccountDialog(accountList=accountList, callback=self.addOrEditAccountCallback,
                               isDebug=self.isDebug).show()
        pass

    def addOrEditAccountCallback(self, accountInfo):
        LogUtil.d("addAccountCallback", accountInfo)
        accountList = self.accounts[KEY_LIST]
        if accountInfo:
            accountList.append(accountInfo)
        self.accounts[KEY_LIST] = sorted(accountList, key=lambda x: x[KEY_ACCOUNT])
        self.updateAccountInfoTableView()
        self.updateAccountInfo()
        pass

    def updateAccountInfo(self):
        self.accounts[KEY_DEFAULT] = self.curAccountInfo
        self.accountManager.saveAccountInfos(self.curAccountsInfoKey, self.accounts)
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d("双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)

        accountInfo = self.accounts[KEY_LIST][row]
        AddOrEditAccountDialog(accountList=self.accounts[KEY_LIST], callback=self.addOrEditAccountCallback, default=accountInfo,
                               isDebug=self.isDebug).show()
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.accountTableView.currentIndex().row()
        LogUtil.i("customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delAccount)
        menu.exec(self.accountTableView.mapToGlobal(pos))
        pass

    def delAccount(self):
        account = self.accounts[KEY_LIST][self.curDelRow][KEY_ACCOUNT]
        LogUtil.i(f"delAccount {account}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{account}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i("delTreeWidgetItem")
        self.accounts[KEY_LIST].remove(self.accounts[KEY_LIST][self.curDelRow])
        self.updateAccountInfoTableView()
        self.updateAccountInfo()
        pass


class AddFlavorDialog(QtWidgets.QDialog):
    def __init__(self, flavorList, callback, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddFlavorDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddFlavorDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("Add Flavor Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加渠道信息"))

        self.callback = callback
        self.flavorList = flavorList

        self.setObjectName("AddFlavorDialog")
        self.resize(AddFlavorDialog.WINDOW_WIDTH, AddFlavorDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddFlavorDialog.WINDOW_WIDTH, AddFlavorDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入渠道名：", minSize=QSize(120, 20)))
        self.flavorNameLineEdit = WidgetUtil.createLineEdit(self, holderText="渠道名（只能包含字母数字及下划线）")
        hbox.addWidget(self.flavorNameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入渠道描述：", minSize=QSize(120, 20)))
        self.flavorDescLineEdit = WidgetUtil.createLineEdit(self, holderText="渠道描述，用于说明该渠道的作用")
        hbox.addWidget(self.flavorDescLineEdit)
        vLayout.addLayout(hbox)
        vLayout.addWidget(WidgetUtil.createLabel(self), 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        flavorName = self.flavorNameLineEdit.text().strip()
        if not flavorName:
            WidgetUtil.showErrorDialog(message="请输入渠道名")
            return
        flavorDesc = self.flavorDescLineEdit.text().strip()
        if not flavorDesc:
            WidgetUtil.showErrorDialog(message="请输入渠道描述")
            return
        if not ReUtil.match(flavorName, "\\w*"):
            WidgetUtil.showErrorDialog(message="请输入正确的渠道名（只能包含字母数字及下划线）")
            return
        for item in self.flavorList:
            if flavorName == item[KEY_FLAVOR_NAME]:
                WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的渠道，{flavorName}已经存在了，可以下拉选择")
                return
            if flavorDesc == item[KEY_DESC]:
                WidgetUtil.showErrorDialog(message=f"请设置一个其他的描述，{flavorDesc}已经存在了，相同的描述会产生混淆")
                return
        self.callback(flavorName, flavorDesc)
        self.close()
        pass


class AddCountryDialog(QtWidgets.QDialog):
    def __init__(self, countryList, callback, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddCountryDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddCountryDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("Add Country Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加国家"))

        self.callback = callback
        self.countryList = countryList

        self.setObjectName("AddCountryDialog")
        self.resize(AddCountryDialog.WINDOW_WIDTH, AddCountryDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddCountryDialog.WINDOW_WIDTH, AddCountryDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入国家码：", minSize=QSize(120, 20)))
        self.countryCodeLineEdit = WidgetUtil.createLineEdit(self, holderText="国家码")
        hbox.addWidget(self.countryCodeLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入国家描述：", minSize=QSize(120, 20)))
        self.countryDescLineEdit = WidgetUtil.createLineEdit(self, holderText="国家描述，用于说明该国家码对应的国家")
        hbox.addWidget(self.countryDescLineEdit)
        vLayout.addLayout(hbox)
        vLayout.addWidget(WidgetUtil.createLabel(self), 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        countryCode = self.countryCodeLineEdit.text().strip()
        if not countryCode:
            WidgetUtil.showErrorDialog(message="请输入国家码")
            return
        countryDesc = self.countryDescLineEdit.text().strip()
        if not countryDesc:
            WidgetUtil.showErrorDialog(message="请输入国家描述")
            return
        for item in self.countryList:
            if countryCode == item[KEY_COUNTRY_CODE]:
                WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的国家码，{countryCode}已经存在了，可以下拉选择")
                return
            if countryDesc == item[KEY_DESC]:
                WidgetUtil.showErrorDialog(message=f"请设置一个其他的描述，{countryDesc}已经存在了，相同的描述会产生混淆")
                return
        self.callback(countryCode, countryDesc)
        self.close()
        pass


class AddOrEditAccountDialog(QtWidgets.QDialog):
    def __init__(self, accountList, callback, default=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditAccountDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddOrEditAccountDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("Add or Edit Account Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑账号信息"))

        self.callback = callback
        self.accountList = accountList
        self.default = default

        self.setObjectName("AddOrEditAccountDialog")
        self.resize(AddOrEditAccountDialog.WINDOW_WIDTH, AddOrEditAccountDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddOrEditAccountDialog.WINDOW_WIDTH, AddOrEditAccountDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="登录账号名：", minSize=QSize(120, 20)))
        self.accountLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_ACCOUNT] if default else "",
                                                         holderText="注册时使用的手机号或者邮箱")
        hbox.addWidget(self.accountLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="登录密码：", minSize=QSize(120, 20)))
        self.pwdLineEdit = WidgetUtil.createLineEdit(self, text=CipherUtil.decrypt(default[KEY_PWD],
                                                                                   AccountManagerDialog.AES_KEY) if default else "",
                                                     holderText="注册账号时设置的密码，用于账号登录",
                                                     echoMode=QtWidgets.QLineEdit.PasswordEchoOnEdit)
        hbox.addWidget(self.pwdLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="昵称：", minSize=QSize(120, 20)))
        self.nickNameLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_NICKNAME] if default else "",
                                                          holderText="用户的昵称")
        hbox.addWidget(self.nickNameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="描述：", minSize=QSize(120, 20)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_DESC] if default else "",
                                                      holderText="账号的相关描述，便于识别存储的账户")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        vLayout.addWidget(WidgetUtil.createLabel(self), 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        account = self.accountLineEdit.text().strip()
        if not account:
            WidgetUtil.showErrorDialog(message="请输入登录账号名")
            return
        pwd = self.pwdLineEdit.text().strip()
        if not pwd:
            WidgetUtil.showErrorDialog(message="请输入账号登录密码")
            return
        if not self.default or self.default[KEY_ACCOUNT] != account:
            for item in self.accountList:
                if account == item[KEY_ACCOUNT]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的账号，{account}已经存在了，不能重复添加")
                    return
        nickName = self.nickNameLineEdit.text().strip()
        desc = self.descLineEdit.text().strip()
        if self.default:
            self.default[KEY_ACCOUNT] = account
            self.default[KEY_PWD] = CipherUtil.encrypt(pwd, AccountManagerDialog.AES_KEY)
            self.default[KEY_NICKNAME] = nickName
            self.default[KEY_DESC] = desc
            self.callback(None)
        else:
            self.callback({KEY_ACCOUNT: account, KEY_PWD: CipherUtil.encrypt(pwd, AccountManagerDialog.AES_KEY),
                           KEY_NICKNAME: nickName,
                           KEY_DESC: desc})
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AccountManagerDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
