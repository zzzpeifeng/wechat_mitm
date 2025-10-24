import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class DatabaseConfig:
    """数据库配置类"""
    MONGODB_HOST = os.getenv('MONGODB_HOST', '8.138.164.134')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'netbar_data')
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'admin')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'xxxx')