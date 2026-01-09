@echo off
REM Windows 批处理脚本，用于运行 all_collector.py
REM 自动检测虚拟环境并运行脚本

setlocal enabledelayedexpansion

echo 检测操作系统: Windows
echo.

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo 虚拟环境: !VIRTUAL_ENV!
    set "PYTHON_PATH=!VIRTUAL_ENV!\Scripts\python.exe"
) else if defined CONDA_DEFAULT_ENV (
    echo Conda 环境: !CONDA_DEFAULT_ENV!
    set "PYTHON_PATH=!CONDA_PREFIX!\python.exe"
) else (
    echo 使用系统 Python
    set "PYTHON_PATH=python"
)

echo Python 可执行文件: !PYTHON_PATH!
echo.

REM 获取项目根目录
set "PROJECT_ROOT=%~dp0"

REM 移除末尾的反斜杠
set "PROJECT_ROOT=!PROJECT_ROOT:~0,-1!"

echo 项目根目录: !PROJECT_ROOT!
echo.

REM 设置 PYTHONPATH 环境变量
set "PYTHONPATH=!PROJECT_ROOT!;!PYTHONPATH!"

REM 运行 all_collector.py 脚本
echo 正在运行 all_collector 任务...
echo.

REM 使用 -c 参数直接运行 Python 代码，避免导入问题
"!PYTHON_PATH!" -c "
import sys
import os
import warnings
# 为了兼容 Python 3.12+，添加 distutils 兼容性补丁
try:
    import distutils.util
except ImportError:
    # 如果 distutils 不可用，创建一个模拟的模块
    import sys
    import importlib.util
    from importlib import machinery

    # 创建一个虚拟的 distutils 模块
    class MockDistUtils:
        pass

    # 创建一个虚拟的 util 子模块
    class MockUtil:
        @staticmethod
        def subst_vars(path, local_vars):
            # 简单的变量替换
            import re
            for key, value in local_vars.items():
                path = path.replace('%({0})s'.format(key), str(value))
            return path

    # 创建虚拟模块
    distutils_module = MockDistUtils()
    distutils_module.util = MockUtil()
    
    # 注册到 sys.modules
    sys.modules['distutils'] = distutils_module
    sys.modules['distutils.util'] = distutils_module.util

sys.path.insert(0, r'!PROJECT_ROOT!')

# 导入 AllCollector 类并运行
from core.ui.controllers.all_collector import AllCollector

# 创建一个简单的日志回调函数
def log_callback(message):
    print('[LOG] {message}')

# 创建 AllCollector 实例并运行
collector = AllCollector()
collector.log_callback = log_callback

print('开始执行所有数据收集任务...')
try:
    collector.get_all_data()
    print('所有数据收集任务已完成！')
except Exception as e:
    print(f'执行过程中发生错误: {e}')
    import traceback
    traceback.print_exc()
"

echo.
echo 任务执行完成!
pause