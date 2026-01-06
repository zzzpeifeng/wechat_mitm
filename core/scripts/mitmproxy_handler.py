# core/mitmproxy_handler.py
import re
from urllib.parse import urlparse
from datetime import datetime
import logging

from typing import Optional

from mitmproxy import http
from mitmproxy.script import concurrent
from mitmproxy import ctx

from core.utils.database import get_db_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChainCookieInterceptor:
    """
    Chain Cookie 拦截器
    负责拦截请求并提取特定域名下的 cookie 中的 chain 值
    """

    def __init__(self):
        """初始化拦截器"""
        print('ChainCookieInterceptor 初始化')
        self.db_manager = get_db_manager()
        self.target_domains = []  # 目标域名列表
        self.is_collecting = True  # 是否正在收集数据
        print('ChainCookieInterceptor 完成')

    def load_target_domains_from_db(self):
        """
        从 MongoDB 数据库加载目标域名列表
        """
        try:
            # 确保数据库连接
            if not self.db_manager.connected:
                success = self.db_manager.connect()
                if not success:
                    logger.warning("无法连接到数据库，使用默认域名列表")
                    return

            # 获取 target_domains 集合
            if self.db_manager.db is not None:
                collection = self.db_manager.db["target_domains"]

                # 确保 collection 不为 None
                if collection is not None:
                    # 查询所有域名
                    domains = list(collection.find({}, {"domain": 1}))

                    # 提取域名列表
                    self.target_domains = [doc["domain"] for doc in domains if "domain" in doc]
                    logger.info(f"从数据库加载了 {len(self.target_domains)} 个目标域名: {self.target_domains}")
                else:
                    logger.warning("无法获取目标域名集合")
            else:
                logger.warning("数据库未初始化，无法加载目标域名")

        except Exception as e:
            logger.error(f"从数据库加载目标域名失败: {e}")
            # 出错时使用空列表或默认域名

    def set_target_domains(self, domains: list):
        """
        设置目标域名列表

        Args:
            domains (list): 域名列表
        """
        self.target_domains = domains
        logger.info(f"设置目标域名: {domains}")

    def enable_collection(self, enabled: bool):
        """
        启用或禁用数据收集

        Args:
            enabled (bool): 是否启用数据收集
        """
        self.is_collecting = enabled
        logger.info(f"数据收集 {'启用' if enabled else '禁用'}")

    def is_target_domain(self, url: str) -> bool:
        """
        判断是否为目标域名（通过检查整个URL）

        Args:
            url (str): 请求完整URL

        Returns:
            bool: 是否为目标域名
        """
        # 如果目标域名列表为空，从数据库重新加载
        if not self.target_domains:
            self.load_target_domains_from_db()

        # 如果仍然没有目标域名，则匹配所有（向后兼容）
        if not self.target_domains:
            logger.info("未设置目标域名，匹配所有请求")
            return True

        try:
            # 解析URL
            parsed_url = urlparse(url)
            host = parsed_url.netloc.lower()

            logger.info(f"检查URL: {url}")
            logger.info(f"解析出的域名: {host}")

            # 检查域名是否匹配目标域名列表
            for domain in self.target_domains:
                if domain in url or host in domain:
                    logger.info(f"匹配到目标域名: {domain}")
                    return True

                # 同时检查URL路径中是否包含目标域名
                if domain in parsed_url.path:
                    logger.info(f"URL路径匹配到目标域名: {domain}")
                    return True

        except Exception as e:
            logger.error(f"URL解析错误: {e}")
            return False

        return False

    # @concurrent
    def request(self, flow: http.HTTPFlow) -> None:
        """
        处理请求事件

        Args:
            flow (http.HTTPFlow): HTTP 流对象
        """

        logger.info(f"请求到达: {flow.request.method} {flow.request.url}")
        # 检查是否启用数据收集
        if not self.is_collecting:
            logger.info(f"数据收集未启用：{self.is_collecting}")
            return

        # 获取请求信息
        request = flow.request

        # 检查是否为目标域名
        logger.info(f"处理请求: {request.method} {request.path}")

        if not self.is_target_domain(request.url):
            return

        # 获取 Cookie
        cookie_header = request.headers.get('Cookie', '')
        if not cookie_header:
            return

        # 记录日志
        logger.info(f"捕获到目标请求 - 域名: {request.url}, cookie值: {cookie_header}")

        # 保存到数据库
        self.save_chain_data(request.host, request.url, cookie_header, request.timestamp_start)

    def save_chain_data(self, host: str, domain: str, cookie_header: str, timestamp: float):
        """
        保存 chain 数据到数据库

        Args:
            host (str): host
            domain (str): 请求域名
            cookie_header (str): 完整的 Cookie
            timestamp (float): 时间戳
        """
        try:
            # 检查 cookie 中是否包含必需的字段
            required_fields = ['chain-id', 'chain', 'HMACCOUNT']
            missing_fields = []

            for field in required_fields:
                if field not in cookie_header:
                    missing_fields.append(field)

            if missing_fields:
                logger.warning(f"Cookie 缺少必需字段: {missing_fields}，跳过保存")
                return

            # 从 cookie_header 中提取 chain-id
            chain_id = None
            # 使用正则表达式提取 chain-id 的值
            chain_id_match = re.search(r'chain-id=([^;,\s]+)', cookie_header)
            if chain_id_match:
                chain_id = chain_id_match.group(1)
                logger.info(f"提取到 chain-id: {chain_id}")
            else:
                logger.warning("未能从 cookie 中提取到 chain-id")
                return

            # 确保数据库连接
            if not self.db_manager.connected:
                success = self.db_manager.connect()
                if not success:
                    logger.error("无法连接到数据库")
                    return

            # 集合总是存在的（MongoDB会在第一次插入时自动创建）
            # 直接进行数据保存操作
            # 转换时间戳
            dt_timestamp = datetime.fromtimestamp(timestamp)

            # 插入数据
            success = self.db_manager.insert_chain_data(
                host=host,
                domain=domain,
                chain_id=chain_id,
                cookie_header=cookie_header,
                timestamp=dt_timestamp
            )

            if success:
                logger.info(f"数据已保存到数据库 - 域名: {domain}")
            else:
                logger.error(f"数据保存失败 - 域名: {domain}")

        except Exception as e:
            logger.error(f"保存数据时发生错误: {str(e)}")


# 创建全局实例
interceptor = ChainCookieInterceptor()


def configure(updated: dict) -> None:
    """
    配置回调函数

    Args:
        updated (dict): 更新的配置项
    """
    logger.info("MitmProxy 脚本配置更新")


def request(flow: http.HTTPFlow) -> None:
    """
    请求处理回调函数

    Args:
        flow (http.HTTPFlow): HTTP 流对象
    """
    interceptor.request(flow)


def server_connect(server_conn):
    """
    当与服务器建立连接时的回调函数
    """
    logger.info(f"连接到服务器: {server_conn.address}")


def tls_established_server(conn):
    """
    TLS连接建立成功时的回调函数
    """
    logger.info(f"与服务器建立TLS连接: {conn.address}")


print("Script loading started")


def start():
    """
    启动脚本时的初始化
    """
    print("START FUNCTION CALLED")  # 确保能看到输出
    logger.info("Chain Cookie 拦截器启动")


def done():
    """
    脚本结束时的清理工作
    """
    logger.info("Chain Cookie 拦截器关闭")


print("Script loading completed")
