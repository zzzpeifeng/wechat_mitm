#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台运行 all_collector.py 的脚本
支持 macOS 和 Windows 系统
自动检测虚拟环境
"""

import os
import sys
import platform
import subprocess
import importlib.util


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


def run_all_collector():
    """运行 all_collector.py 脚本"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 添加项目根目录到 Python 路径
    sys.path.insert(0, project_root)
    
    # 添加 distutils 兼容性补丁
    try:
        import distutils.util
    except ImportError:
        # 如果 distutils 不可用，创建一个模拟的模块
        import sys as _sys
        import importlib.util as _importlib_util
        from importlib import machinery as _machinery

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
                    path = path.replace("%({0})s".format(key), str(value))
                return path

        # 创建虚拟模块
        distutils_module = MockDistUtils()
        distutils_module.util = MockUtil()
        
        # 注册到 sys.modules
        _sys.modules['distutils'] = distutils_module
        _sys.modules['distutils.util'] = distutils_module.util

    # 导入 AllCollector 类
    all_collector_path = os.path.join(project_root, 'core', 'ui', 'controllers', 'all_collector.py')
    
    spec = importlib.util.spec_from_file_location("all_collector", all_collector_path)
    all_collector_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(all_collector_module)
    
    # 创建 AllCollector 实例并运行
    collector = all_collector_module.AllCollector()
    
    # 定义日志回调函数
    def log_callback(message):
        print(f"[LOG] {message}")
    
    # 设置日志回调
    collector.log_callback = log_callback
    
    # 运行数据收集任务
    try:
        print("开始执行所有数据收集任务...")
        collector.get_all_data()
        print("所有数据收集任务已完成！")
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def run_with_subprocess():
    """使用子进程方式运行脚本"""
    python_executable = get_python_executable()
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 构造命令
    script_path = os.path.join(project_root, 'core', 'ui', 'controllers', 'all_collector.py')
    
    # 设置环境变量，确保 Python 能够找到项目模块
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{project_root}:{env.get('PYTHONPATH', '')}"
    
    # 构造包含兼容性补丁的命令
    cmd = [python_executable, '-c', f'''
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
                path = path.replace("%({{0}})s".format(key), str(value))
            return path

    # 创建虚拟模块
    distutils_module = MockDistUtils()
    distutils_module.util = MockUtil()
    
    # 注册到 sys.modules
    sys.modules['distutils'] = distutils_module
    sys.modules['distutils.util'] = distutils_module.util

sys.path.insert(0, r"{project_root}")

# 导入 AllCollector 类并运行
from core.ui.controllers.all_collector import AllCollector

# 创建一个简单的日志回调函数
def log_callback(message):
    print("[LOG] {{message}}")

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
''']
    
    print(f"使用 Python 解释器: {python_executable}")
    print(f"运行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, env=env, check=True)
        print("脚本执行完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"脚本执行失败: {e}")
        return False


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
    
    # 检查是否可以直接导入模块运行
    try:
        print("\n尝试直接导入并运行 AllCollector...")
        run_all_collector()
    except ImportError as e:
        print(f"无法直接导入模块: {e}")
        print("尝试使用子进程方式运行...")
        run_with_subprocess()
    except Exception as e:
        print(f"直接运行时出错: {e}")
        print("尝试使用子进程方式运行...")
        run_with_subprocess()


if __name__ == "__main__":
    main()