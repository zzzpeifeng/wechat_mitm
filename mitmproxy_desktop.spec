# -*- mode: python ; coding: utf-8 -*-

import os
import sys
try:
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules
    from PyInstaller.building.build_main import Tree
except ImportError:
    try:
        from kivy.tools.packaging.pyinstaller import Tree
    except ImportError:
        Tree = None

block_cipher = None

# 获取当前目录
if getattr(sys, 'frozen', False):
    # 当在PyInstaller环境中运行时
    current_dir = os.path.dirname(sys.executable)
else:
    # 开发环境中，使用当前工作目录
    current_dir = os.path.abspath(".")

# 收集所有需要的数据文件
datas = []
# 添加配置文件
if os.path.exists('config'):
    config_files = collect_data_files('config')
    datas.extend(config_files)
# 添加核心模块
if os.path.exists('core'):
    core_files = collect_data_files('core')
    datas.extend(core_files)

# 分析主程序
a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'mitmproxy',
        'mitmproxy.addons',
        'mitmproxy.master',
        'mitmproxy.proxy',
        'mitmproxy.options',
        'mitmproxy.tools',
        'mitmproxy.tools.dump',
        'mitmproxy.utils',
        'mitmproxy.certs',
        'mitmproxy.contentviews',
        'mitmproxy.http',
        'mitmproxy.net',
        'mitmproxy.websocket',
        'mitmproxy.connections',
        'mitmproxy.flowfilter',
        'mitmproxy.log',
        'mitmproxy.proxy.layers',
        'mitmproxy.proxy.server',
        'mitmproxy.tcp',
        'mitmproxy.tls',
        'mitmproxy.udp',
        'mitmproxy.utils.human',
        'mitmproxy.utils.data',
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 合并分析结果
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mitmproxy_desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI应用不需要控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)