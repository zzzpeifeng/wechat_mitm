# utils/database.py
import pymongo
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from config.settings import DatabaseConfig  # 导入配置类
from urllib.parse import quote_plus

class MongoDBManager:
    """
    MongoDB 数据库管理类
    负责数据库连接、数据存储等操作
    """

    def __init__(self):
        """初始化数据库连接"""
        self.client: Optional[pymongo.MongoClient] = None
        self.db: Optional[pymongo.database.Database] = None
        self.collection: Optional[pymongo.collection.Collection] = None
        self.connected = False

        # 加载环境变量
        load_dotenv()

    def connect(self) -> bool:
        """
        连接到 MongoDB 数据库

        Returns:
            bool: 连接是否成功
        """
        try:
            # 从 settings.py 获取数据库配置
            mongodb_host = DatabaseConfig.MONGODB_HOST
            mongodb_port = DatabaseConfig.MONGODB_PORT
            mongodb_database = DatabaseConfig.MONGODB_DATABASE
            mongodb_collection = os.getenv('MONGODB_COLLECTION', 'chain_cookies')  # collection仍从环境变量获取
            mongodb_username = quote_plus(DatabaseConfig.MONGODB_USERNAME)
            mongodb_password = quote_plus(DatabaseConfig.MONGODB_PASSWORD)

            logging.info(mongodb_password)
            # 构建连接字符串
            if mongodb_username and mongodb_password:
                connection_string = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_host}:{mongodb_port}/"
            else:
                connection_string = f"mongodb://{mongodb_host}:{mongodb_port}/"

            # 建立连接
            self.client = pymongo.MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000  # 5秒超时
            )

            # 测试连接
            self.client.server_info()

            # 获取数据库和集合
            self.db = self.client[mongodb_database]
            self.collection = self.db[mongodb_collection]

            self.connected = True
            logging.info(f"成功连接到 MongoDB: {mongodb_host}:{mongodb_port}")
            return True

        except Exception as e:
            logging.error(f"连接 MongoDB 失败: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            self.connected = False
            logging.info("已断开 MongoDB 连接")

    def insert_chain_data(self,host:str, domain: str, cookie_header: str, timestamp: datetime = None) -> bool:
        """
        插入 chain 数据到数据库

        Args:
            domain (str): 请求域名
            chain_value (str): 从 cookie 中提取的 chain 值
            cookie (str): 完整的 cookie 字符串
            timestamp (datetime): 时间戳，默认为当前时间

        Returns:
            bool: 插入是否成功
        """
        logging.info(f"成功进入insert_chain_data")
        if not self.connected or self.collection is None:
            logging.error("数据库未连接，无法插入数据")
            return False
        try:
            # 准备数据文档
            document = {
                'host': host,
                "domain": domain,
                "cookie_header": cookie_header,
                "timestamp": timestamp or datetime.now(),
                "created_at": datetime.now()
            }

            # 插入数据
            logging.info(f"准备插入数据")
            # 使用 upsert 操作：如果存在相同 domain 的数据则更新，否则插入
            result = self.collection.update_one(
                {"host": host},  # 查询条件
                {"$set": document},  # 更新数据
                upsert=True  # 如果不存在则插入
            )
            if result.upserted_id:
                logging.info(f"成功插入新数据，ID: {result.upserted_id}")
            elif result.modified_count > 0:
                logging.info(f"成功更新域名为 {domain} 的数据")
            else:
                logging.info(f"数据无变化，域名为 {domain} 的数据已存在且未被修改")

            return True

        except Exception as e:
            logging.error(f"插入数据失败: {str(e)}")
            return False

    def insert_request_data(self, data: Dict[str, Any]) -> bool:
        """
        插入完整的请求数据到数据库

        Args:
            data (Dict[str, Any]): 请求数据字典

        Returns:
            bool: 插入是否成功
        """
        if not self.connected or not self.collection:
            logging.error("数据库未连接，无法插入数据")
            return False

        try:
            # 添加创建时间
            data["created_at"] = datetime.now()

            # 插入数据
            result = self.collection.insert_one(data)
            logging.info(f"成功插入请求数据，ID: {result.inserted_id}")
            return True

        except Exception as e:
            logging.error(f"插入请求数据失败: {str(e)}")
            return False

    def get_connection_status(self) -> Dict[str, Any]:
        """
        获取数据库连接状态

        Returns:
            Dict[str, Any]: 连接状态信息
        """
        return {
            "connected": self.connected,
            "database": DatabaseConfig.MONGODB_DATABASE if self.connected else None,
            "collection": os.getenv('MONGODB_COLLECTION', 'chain_cookies') if self.connected else None
        }


# 全局数据库管理实例
db_manager = MongoDBManager()


def get_db_manager() -> MongoDBManager:
    """
    获取全局数据库管理实例

    Returns:
        MongoDBManager: 数据库管理实例
    """
    return db_manager
