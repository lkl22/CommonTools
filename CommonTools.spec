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

              'util/excel/Excel2003Operator.py',
              'util/excel/Excel2007Operator.py',
              'util/excel/ExcelOperator.py',
              'util/excel/IExcelOperator.py',

              'util/AdbUtil.py',
              'util/AutoTestUtil.py',
              'util/CipherUtil.py',
              'util/ClipboardUtil.py',
              'util/DataTypeUtil.py',
              'util/DateUtil.py',
              'util/DialogUtil.py',
              'util/DictUtil.py',
              'util/DomXmlUtil.py',
              'util/EmittingStream.py',
              'util/ExcelUtil.py',
              'util/FileUtil.py',
              'util/GraphicsUtil.py',
              'util/HashUtil.py',
              'util/ImageUtil.py',
              'util/JsonUtil.py',
              'util/ListUtil.py',
              'util/LogUtil.py',
              'util/MD5Util.py',
              'util/MyThread.py',
              'util/NetworkUtil.py',
              'util/NetworkxUtil.py',
              'util/OpenpyxlUtil.py',
              'util/OperaIni.py',
              'util/PlatformUtil.py',
              'util/ProcessManager.py',
              'util/RandomUtil.py',
              'util/ReUtil.py',
              'util/ShellUtil.py',
              'util/StrUtil.py',
              'util/TinifyUtil.py',
              'util/TLV.py',
              'util/Uiautomator.py',
              'util/WeditorUtil.py',
              'util/WidgetUtil.py',
              'widget/account/AccountManager.py',
              'widget/account/AccountManagerDialog.py',
              'widget/algorithm/sort/SelectionSortDialog.py',
              'widget/algorithm/AlgorithmDescDialog.py',
              'widget/algorithm/AlgorithmVisualizerManagerDialog.py',

              'widget/analysis/extract/AddOrEditExtracCfgDialog.py',
              'widget/analysis/extract/ExtractLogDialog.py',
              'widget/analysis/extract/ExtractMergeLogDialog.py',
              'widget/analysis/AddOrEditAnalysisCfgDialog.py',
              'widget/analysis/AddOrEditCategoryDialog.py',
              'widget/analysis/CategoryConfigWidget.py',
              'widget/analysis/CategoryManagerWidget.py',
              'widget/analysis/LogAnalysisManager.py',
              'widget/analysis/LogAnalysisWindow.py',

              'widget/colorManager/AddColorResDialog.py',
              'widget/colorManager/AndroidColorResDialog.py',
              'widget/compressPicture/CompressPicDialog.py',

              'widget/custom/progressBar/RoundProgressBar.py',
              'widget/custom/tree/TreePlotter.py',
              'widget/custom/ChoiceButton.py',
              'widget/custom/ClickLabel.py',
              'widget/custom/ClickTextEdit.py',
              'widget/custom/CommonComboBox.py',
              'widget/custom/DragInputWidget.py',
              'widget/custom/LoadingDialog.py',

              'widget/fileOperation/FileOperationDialog.py',

              'widget/findFileContent/AddOrEditConfigDialog.py',
              'widget/findFileContent/AddOrEditMatchDialog.py',
              'widget/findFileContent/FindFileContentManager.py',
              'widget/findFileContent/FindFileContentUtil.py',
              'widget/findFileContent/FindFileContentWindow.py',

              'widget/hash/FileHashDialog.py',
              'widget/mockExam/Excel2Word.py',
              'widget/mockExam/MockExamDialog.py',
              'widget/mockExam/MockExamUtil.py',
              'widget/mockExam/Word2Excel.py',
              'widget/photoWall/PhotoWallWindow.py',
              'widget/photoWall/PicturePreviewDialog.py',

              'widget/resource/AndroidResDialog.py',
              'widget/resource/HarmonyMergeResDialog.py',

              'widget/projectManage/AddOrEditCmdDialog.py',
              'widget/projectManage/AddOrEditCmdGroupDialog.py',
              'widget/projectManage/AddOrEditDynamicParamDialog.py',
              'widget/projectManage/AddOrEditEvnDialog.py',
              'widget/projectManage/AddOrEditModuleDialog.py',
              'widget/projectManage/AddOrEditOptionDialog.py',
              'widget/projectManage/AddOrEditOptionGroupDialog.py',
              'widget/projectManage/AddOrEditPreconditionDialog.py',
              'widget/projectManage/AddOrEditProjectDialog.py',
              'widget/projectManage/CmdManagerWidget.py',
              'widget/projectManage/ModuleDependencyDialog.py',
              'widget/projectManage/ModuleManagerWidget.py',
              'widget/projectManage/OptionManagerWidget.py',
              'widget/projectManage/ProjectManager.py',
              'widget/projectManage/ProjectManagerUtil.py',
              'widget/projectManage/ProjectManagerWidget.py',
              'widget/projectManage/ProjectManagerWindow.py',

              'widget/test/AndroidAdbDialog.py',
              'widget/test/AndroidAssistTestDialog.py',
              'widget/test/EditTestStepDialog.py',

              'widget/JsonDialog.py',
              'widget/MainWidget.py'],
             pathex=['./', '../ven/Lib/site-packages/'],
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
