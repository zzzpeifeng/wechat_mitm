#!/usr/bin/env python3
"""
应用打包脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def prepare_build():
    """准备构建环境"""
    print("准备构建环境...")
    
    # 创建dist和build目录
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        
    dist_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    
    # 如果没有.env文件，则创建一个示例
    env_file = Path(".env")
    if not env_file.exists():
        print("创建示例.env文件...")
        with open(env_file, "w") as f:
            f.write("""# MongoDB配置
MONGODB_HOST=8.138.164.134
MONGODB_PORT=27017
MONGODB_DATABASE=netbar_data
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_password_here

# 飞书配置
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_DOMAIN=https://open.feishu.cn
""")
        print("请根据实际情况修改.env文件中的配置信息")

def run_pyinstaller():
    """运行PyInstaller进行打包"""
    print("开始打包应用...")
    
    try:
        # 使用.spec文件进行打包
        cmd = [
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "mitmproxy_desktop.spec"
        ]
        
        # 更改工作目录到项目根目录
        cwd = os.getcwd()
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        
        if result.returncode == 0:
            print("打包成功完成！")
            return True
        else:
            print("打包过程中出现错误:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"运行PyInstaller时出错: {e}")
        return False

def post_build():
    """打包后处理"""
    print("执行打包后处理...")
    
    # 复制.env文件到dist目录
    try:
        shutil.copy(".env", "dist/.env")
        print("已将.env配置文件复制到dist目录")
    except Exception as e:
        print(f"复制.env文件时出错: {e}")
    
    # 检查不同的可能输出文件
    possible_paths = [
        Path("dist/mitmproxy_desktop"),
        Path("dist/mitmproxy_desktop.exe"),
        Path("dist/mitmproxy_desktop.app")
    ]
    
    output_path = None
    for path in possible_paths:
        if path.exists():
            output_path = path
            break
    
    if output_path:
        print(f"应用已打包至: {output_path.absolute()}")
        print("\n注意事项:")
        print("1. 打包后的应用需要在同一目录下保留配置文件(.env)")
        print("2. 应用会在运行目录生成日志文件(app.log)")
        print("3. 如需在其他机器上运行，请确保目标机器满足系统要求")
        return True
    else:
        print("未能找到打包后的应用文件")
        print("请检查dist目录内容:")
        dist_dir = Path("dist")
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                print(f"  {item}")
        return False

def main():
    """主函数"""
    print("开始打包MitmProxy桌面应用...")
    
    prepare_build()
    
    if not run_pyinstaller():
        print("打包失败!")
        sys.exit(1)
    
    if not post_build():
        print("打包后处理失败!")
        sys.exit(1)
        
    print("应用打包完成!")

if __name__ == "__main__":
    main()