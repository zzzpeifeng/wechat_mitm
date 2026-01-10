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
            mongodb_username = quote_plus(DatabaseConfig.MONGODB_USERNAME)
            mongodb_password = quote_plus(DatabaseConfig.MONGODB_PASSWORD)

            logging.info("Connecting to MongoDB...")
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
            # self.collection = self.db[mongodb_collection]

            self.connected = True
            logging.info(f"Successfully connected to MongoDB: {mongodb_host}:{mongodb_port}")
            return True

        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
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
            logging.info("Disconnected from MongoDB")

    def insert_chain_data(self, host: str, domain: str, chain_id: str, cookie_header: str,
                          timestamp: datetime = None) -> bool:
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
        logging.info(f"Successfully entered insert_chain_data")
        self.collection = self.db['chain_cookies']
        if not self.connected or self.collection is None:
            logging.error("Database not connected, unable to insert data")
            return False
        try:
            # 准备数据文档
            document = {
                'host': host,
                "domain": domain,
                'chain_id': chain_id,
                "cookie_header": cookie_header,
                "timestamp": timestamp or datetime.now(),
                "created_at": datetime.now()
            }

            # 插入数据
            logging.info(f"Preparing to insert data")
            # 使用 upsert 操作：如果存在相同 domain 的数据则更新，否则插入
            result = self.collection.update_one(
                {"host": host},  # 查询条件
                {"$set": document},  # 更新数据
                upsert=True  # 如果不存在则插入
            )
            if result.upserted_id:
                logging.info(f"Successfully inserted new data, ID: {result.upserted_id}")
            elif result.modified_count > 0:
                logging.info(f"Successfully updated data for domain {domain}")
            else:
                logging.info(f"No changes made, data for domain {domain} already exists and is unchanged")

            return True

        except Exception as e:
            logging.error(f"Failed to insert data: {str(e)}")
            return False

    def insert_request_data(self, data: Dict[str, Any]) -> bool:
        """
        插入完整的请求数据到数据库

        Args:
            data (Dict[str, Any]): 请求数据字典

        Returns:
            bool: 插入是否成功
        """
        if not self.connected:
            logging.error("Database not connected, unable to insert data")
            return False

        self.collection = self.db['chain_cookies']

        try:
            # 添加创建时间
            data["created_at"] = datetime.now()

            # 插入数据
            result = self.collection.insert_one(data)
            logging.info(f"Successfully inserted request data, ID: {result.inserted_id}")
            return True

        except Exception as e:
            logging.error(f"Failed to insert request data: {str(e)}")
            return False

    def insert_online_rate_v2(self, data: Dict[str, Any]):
        """
       插入在线率数据到数据库

       Args:
           data (Dict[str, Any]): 在线率数据字典

       Returns:
           bool: 插入是否成功
       """
        if not self.connected:
            logging.error("Database not connected, unable to insert data")
            return False

        self.collection = self.db['online_rate_new']

        # 获取当天日期 yyyy-mm-dd格式
        today = datetime.now().strftime("%Y-%m-%d")

        # 查询集合中是否有sheet_date等于当天日期的数据
        existing_data = self.collection.find_one({"sheet_date": today})

        # 获取当前小时
        current_hour = datetime.now().strftime("%H")  # 保持为字符串，例如 "00", "14"
        # current_hour = int(current_hour)  # 转换为整数 - 注释掉，保持为字符串

        if existing_data:
            # 如果已存在当天的数据，获取当前小时的数据并合并
            existing_hour_data = existing_data.get('data', {}).get(current_hour, {})
            # 将新数据合并到现有数据中
            merged_data = {**existing_hour_data, **data}
            
            result = self.collection.update_one(
                {"sheet_date": today},
                {"$set": {f"data.{current_hour}": merged_data}}
            )
            if result.modified_count > 0:
                logging.info(f"Successfully updated online rate data for date: {today}, hour: {current_hour}")
            else:
                logging.info(f"Updated online rate data but no changes made, date: {today}, hour: {current_hour}")
        else:
            # 如果不存在当天的数据，创建新的文档
            new_document = {
                "sheet_date": today,
                "data": {
                    current_hour: data
                }
            }
            result = self.collection.insert_one(new_document)
            logging.info(f"Successfully created new online rate data document, date: {today}, hour: {current_hour}, ID: {result.inserted_id}")

        return True

    def insert_online_rate(self, data: Dict[str, Any]) -> bool:
        """
        插入在线率数据到数据库

        Args:
            data (Dict[str, Any]): 在线率数据字典

        Returns:
            bool: 插入是否成功
        """
        if not self.connected:
            logging.error("Database not connected, unable to insert data")
            return False

        self.collection = self.db['online_rate']

        try:
            # 添加创建时间
            data["created_at"] = datetime.now()
            data['updated_at'] = datetime.now()
            data['record_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 插入数据
            result = self.collection.insert_one(data)
            logging.info(f"Successfully inserted online rate data, ID: {result.inserted_id}")
            return True

        except Exception as e:
            logging.error(f"Failed to insert online rate data: {str(e)}")
            return False

    def get_chain_cookie(self) -> Optional[Dict[str, Any]]:
        """
        从 chain_cookies 集合中获取一条数据
        
        Returns:
            Optional[Dict[str, Any]]: 返回查询到的数据字典，如果未找到则返回None
        """
        # 如果数据库未连接，尝试连接
        if not self.connected:
            logging.warning("Database not connected, attempting to connect...")
            success = self.connect()
            if not success:
                logging.error("Unable to connect to database, cannot query data")
                return None

        try:
            # 使用 'chain_cookies' 集合作为数据源
            collection = self.db['chain_cookies']

            # 由于表中永远只有一条数据，使用 find_one 查询第一条
            result = collection.find_one()

            if result:
                logging.info("Successfully retrieved chain_cookies data")
            else:
                logging.info("No data found in chain_cookies collection")

            return result

        except Exception as e:
            logging.error(f"Failed to query chain_cookies data: {str(e)}")
            return None

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