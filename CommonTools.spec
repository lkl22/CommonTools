# -*- mode: python -*-
import sys
import os.path as osp

sys.setrecursionlimit(5000)

block_cipher = None

SETUP_DIR = './'

a = Analysis(['RunMain.py',
              'constant/const.py',
              'constant/TestStepConst.py',
              'constant/WidgetConst.py',
              'util/AutoTestUtil.py',
              'util/DataTypeUtil.py',
              'util/DateUtil.py',
              'util/DialogUtil.py',
              'util/DomXmlUtil.py',
              'util/ExcelUtil.py',
              'util/FileUtil.py',
              'util/ImageUtil.py',
              'util/JsonUtil.py',
              'util/LogUtil.py',
              'util/OperaIni.py',
              'util/PlatformUtil.py',
              'util/ReUtil.py',
              'util/ShellUtil.py',
              'util/Uiautomator.py',
              'util/WeditorUtil.py',
              'util/WidgetUtil.py',
              'widget/autoTest/AndroidAdbDialog.py',
              'widget/autoTest/EditTestStepDialog.py',
              'widget/colorManager/AddColorResDialog.py',
              'widget/colorManager/AndroidColorResDialog.py',
              'widget/photoWall/PhotoWallWindow.py',
              'widget/photoWall/PicturePreviewDialog.py',
              'widget/AndroidResDialog.py',
              'widget/JsonDialog.py',
              'widget/MainWidget.py'],
             pathex=['./'],
             binaries=[],
             datas=[(SETUP_DIR+'config','config'), (SETUP_DIR+'icons','icons'), (SETUP_DIR+'software','software')],
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
