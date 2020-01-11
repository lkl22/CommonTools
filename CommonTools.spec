# -*- mode: python -*-
import sys
import os.path as osp

sys.setrecursionlimit(5000)

block_cipher = None

SETUP_DIR = './'

a = Analysis(['RunMain.py',
              'constant/const.py',
              'constant/WidgetConst.py',
              'util/WidgetUtil.py',
              'widget/MainWidget.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=['pandas', 'pandas._libs', 'pandas._libs.tslibs.np_datetime',
                            'pandas._libs.tslibs.timedeltas',
                            'pandas._libs.tslibs.nattype', 'pandas._libs.skiplist', 'scipy._lib',
                            'scipy._lib.messagestream'],
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
