import os
import sys

from dotenv import load_dotenv


def resource_path(relative_path):
    """获取资源文件路径，兼容PyInstaller打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 加载.env文件
# 先尝试从可执行文件同目录加载.env文件，如果不存在则使用默认路径
if getattr(sys, 'frozen', False):
    # 打包后的环境
    env_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # 开发环境
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')

# 如果指定路径的.env文件不存在，则尝试当前目录
if not os.path.exists(env_path):
    env_path = '.env'

# 加载环境变量
load_dotenv(env_path, override=True)


class DatabaseConfig:
    """数据库配置类"""
    MONGODB_HOST = os.getenv('MONGODB_HOST', '8.138.164.134')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'netbar_data')
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'admin')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'xxxx')


class FEISHUConfig:
    """飞书配置类"""
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a9bb9e88bf385bc6')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', 'yNh8KAzF0HN8X6LASixdugaChfQbPj8n')
    FEISHU_DOMAIN = os.getenv('FEISHU_DOMAIN', 'https://open.feishu.cn')


if __name__ == '__main__':
    print(FEISHUConfig.FEISHU_APP_ID)