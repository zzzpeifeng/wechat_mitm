# 运行 all_collector.py 脚本说明

本项目提供了多个脚本，用于跨平台运行 all_collector.py，支持 macOS 和 Windows 系统，并自动检测虚拟环境。

## 脚本文件

- `run_all_collector.py` - 主要的 Python 脚本，具有更完善的错误处理
- `run_all_collector_simple.py` - 简化的 Python 脚本，直接运行
- `run_all_collector.sh` - macOS/Linux 系统的 shell 脚本
- `run_all_collector.bat` - Windows 系统的批处理脚本

## 使用方法

### macOS/Linux 系统

#### 方法 1: 使用 shell 脚本
```bash
./run_all_collector.sh
```

#### 方法 2: 使用 Python 脚本
```bash
python run_all_collector_simple.py
# 或者
python run_all_collector.py
```

### Windows 系统

#### 方法 1: 双击运行
双击 `run_all_collector.bat` 文件

#### 方法 2: 命令行运行
```cmd
python run_all_collector_simple.py
# 或者
python run_all_collector.py
```

## 虚拟环境支持

脚本会自动检测以下虚拟环境：
- venv/virtualenv 虚拟环境
- Conda 环境

## Python 3.12+ 兼容性

由于 Python 3.12+ 移除了 distutils 模块，脚本包含了兼容性补丁，确保在新版本 Python 中正常运行。

## 注意事项

1. 本项目中的 all_collector.py 依赖 Android 设备或模拟器，需要连接设备并启用 USB 调试
2. 确保已安装所有依赖项：`pip install -r requirements.txt`
3. 需要预先配置好 .env 文件以提供必要的环境变量

## 错误处理

如果遇到 "Can't find any android device/emulator" 错误，表示需要连接 Android 设备或启动模拟器。

如果遇到其他依赖问题，请检查是否正确安装了 requirements.txt 中的依赖项。