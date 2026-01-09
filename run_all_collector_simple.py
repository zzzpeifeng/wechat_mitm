#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单运行 all_collector.py 的脚本
支持 macOS 和 Windows 系统
自动检测虚拟环境
"""

import os
import sys
import platform
import subprocess


def get_python_executable():
    """获取当前 Python 解释器路径"""
    # 如果在虚拟环境中，返回虚拟环境的 Python 可执行文件
    if hasattr(sys, 'real_prefix') or (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix):
        # 虚拟环境 (venv 或 virtualenv)
        if platform.system().lower() == 'windows':
            return os.path.join(sys.prefix, 'Scripts', 'python.exe')
        else:
            return os.path.join(sys.prefix, 'bin', 'python')
    
    # 如果是 conda 环境
    elif 'CONDA_DEFAULT_ENV' in os.environ and os.environ.get('CONDA_EXE'):
        if platform.system().lower() == 'windows':
            return os.path.join(os.environ['CONDA_PREFIX'], 'python.exe')
        else:
            return os.path.join(os.environ['CONDA_PREFIX'], 'bin', 'python')
    
    # 否则返回当前使用的 Python 可执行文件
    else:
        return sys.executable


def main():
    """主函数"""
    print(f"操作系统: {platform.system()}")
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件: {sys.executable}")
    
    # 检查虚拟环境
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix) or 
        'VIRTUAL_ENV' in os.environ or 
        'CONDA_DEFAULT_ENV' in os.environ
    )
    
    print(f"是否在虚拟环境中: {'是' if in_venv else '否'}")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 构造 all_collector.py 的路径
    all_collector_path = os.path.join(project_root, 'core', 'ui', 'controllers', 'all_collector.py')
    
    # 检查文件是否存在
    if not os.path.exists(all_collector_path):
        print(f"错误: 未找到文件 {all_collector_path}")
        sys.exit(1)
    
    # 设置环境变量，确保 Python 能够找到项目模块
    env = os.environ.copy()
    python_path = env.get('PYTHONPATH', '')
    if python_path:
        env['PYTHONPATH'] = f"{project_root}:{python_path}"
    else:
        env['PYTHONPATH'] = project_root
    
    # 构造命令
    python_exec = get_python_executable()
    cmd = [python_exec, '-c', '''import sys
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
                path = path.replace("%({{0}})s".format(key), str(value))
            return path

    # 创建虚拟模块
    distutils_module = MockDistUtils()
    distutils_module.util = MockUtil()
    
    # 注册到 sys.modules
    sys.modules['distutils'] = distutils_module
    sys.modules['distutils.util'] = distutils_module.util

sys.path.insert(0, "{0}")

# 导入 AllCollector 类并运行
from core.ui.controllers.all_collector import AllCollector

# 创建一个简单的日志回调函数
def log_callback(message):
    print("[LOG] {{0}}".format(message))

# 创建 AllCollector 实例并运行
collector = AllCollector()
collector.log_callback = log_callback

print("开始执行所有数据收集任务...")
try:
    collector.get_all_data()
    print("所有数据收集任务已完成！")
except Exception as e:
    print("执行过程中发生错误: {{0}}".format(e))
    import traceback
    traceback.print_exc()
'''.format(project_root)]
    
    print(f"使用 Python 解释器: {python_exec}")
    print(f"运行 all_collector 任务...")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, env=env, check=True)
        print("任务执行完成!")
    except subprocess.CalledProcessError as e:
        print(f"任务执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()