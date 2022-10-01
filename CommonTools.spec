# -*- mode: python -*-
import sys
import os.path as osp

sys.setrecursionlimit(5000)

block_cipher = None

SETUP_DIR = './'

a = Analysis(['RunMain.py',
              'constant/ColorConst.py',
              'constant/const.py',
              'constant/TestStepConst.py',
              'constant/WidgetConst.py',
              'util/AdbUtil.py',
              'util/AutoTestUtil.py',
              'util/CipherUtil.py',
              'util/ClipboardUtil.py',
              'util/DataTypeUtil.py',
              'util/DateUtil.py',
              'util/DialogUtil.py',
              'util/DomXmlUtil.py',
              'util/DragInputWidget.py',
              'util/EmittingStream.py',
              'util/ExcelUtil.py',
              'util/FileUtil.py',
              'util/GraphicsUtil.py',
              'util/HashUtil.py',
              'util/ImageUtil.py',
              'util/JsonUtil.py',
              'util/LogUtil.py',
              'util/MyThread.py',
              'util/NetworkUtil.py',
              'util/OpenpyxlUtil.py',
              'util/OperaIni.py',
              'util/PlatformUtil.py',
              'util/RandomUtil.py',
              'util/ReUtil.py',
              'util/ShellUtil.py',
              'util/TinifyUtil.py',
              'util/Uiautomator.py',
              'util/WeditorUtil.py',
              'util/WidgetUtil.py',
              'widget/account/AccountManager.py',
              'widget/account/AccountManagerDialog.py',
              'widget/algorithm/sort/SelectionSortDialog.py',
              'widget/algorithm/AlgorithmDescDialog.py',
              'widget/algorithm/AlgorithmVisualizerManagerDialog.py',
              'widget/colorManager/AddColorResDialog.py',
              'widget/colorManager/AndroidColorResDialog.py',
              'widget/compressPicture/CompressPicDialog.py',
              'widget/fileOperation/FileOperationDialog.py',
              'widget/hash/FileHashDialog.py',
              'widget/mockExam/Excel2Word.py',
              'widget/mockExam/MockExamDialog.py',
              'widget/mockExam/MockExamUtil.py',
              'widget/mockExam/Word2Excel.py',
              'widget/photoWall/PhotoWallWindow.py',
              'widget/photoWall/PicturePreviewDialog.py',
              'widget/progressBar/RoundProgressBar.py',
              'widget/test/AndroidAdbDialog.py',
              'widget/test/AndroidAssistTestDialog.py',
              'widget/test/EditTestStepDialog.py',
              'widget/AndroidResDialog.py',
              'widget/JsonDialog.py',
              'widget/LoadingDialog.py',
              'widget/MainWidget.py'],
             pathex=['./'],
             binaries=[],
             datas=[(SETUP_DIR+'resources','resources')],
             hiddenimports=['pandas', 'pandas._libs', 'pandas._libs.tslibs.np_datetime',
                            'pandas._libs.tslibs.timedeltas',
                            'pandas._libs.tslibs.nattype', 'pandas._libs.skiplist', 'scipy._lib',
                            'scipy._lib.messagestream', 'uiautomator2'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='CommonTools',
          debug=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='CommonTools')
