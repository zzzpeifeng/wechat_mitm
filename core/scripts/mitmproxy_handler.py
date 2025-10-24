# core/mitmproxy_handler.py
import re
from urllib.parse import urlparse
from datetime import datetime
import logging
from typing import Optional

from mitmproxy import http
from mitmproxy.script import concurrent

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
        self.db_manager = get_db_manager()
        self.target_domains = []  # 目标域名列表
        self.is_collecting = False  # 是否正在收集数据

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

    def is_target_domain(self, host: str) -> bool:
        """
        判断是否为目标域名

        Args:
            host (str): 请求主机名

        Returns:
            bool: 是否为目标域名
        """
        if not self.target_domains:
            return True  # 如果没有设置目标域名，则匹配所有

        for domain in self.target_domains:
            if domain in host or host.endswith(domain):
                return True
        return False

    def extract_chain_from_cookie(self, cookie_str: str) -> Optional[str]:
        """
        从 Cookie 字符串中提取 chain 值

        Args:
            cookie_str (str): Cookie 字符串

        Returns:
            Optional[str]: 提取到的 chain 值，未找到则返回 None
        """
        if not cookie_str:
            return None

        # 使用正则表达式匹配 chain 值
        chain_match = re.search(r'chain=([^;]*)', cookie_str)
        if chain_match:
            return chain_match.group(1).strip()
        return None

    @concurrent
    def request(self, flow: http.HTTPFlow) -> None:
        """
        处理请求事件

        Args:
            flow (http.HTTPFlow): HTTP 流对象
        """
        # 检查是否启用数据收集
        if not self.is_collecting:
            return

        # 获取请求信息
        request = flow.request
        host = request.host.lower()

        # 检查是否为目标域名
        if not self.is_target_domain(host):
            return

        # 获取 Cookie
        cookie_header = request.headers.get('Cookie', '')
        if not cookie_header:
            return

        # 提取 chain 值
        chain_value = self.extract_chain_from_cookie(cookie_header)
        if not chain_value:
            return

        # 记录日志
        logger.info(f"捕获到目标请求 - 域名: {host}, Chain值: {chain_value}")

        # 保存到数据库
        self.save_chain_data(host, chain_value, cookie_header, request.timestamp_start)

    def save_chain_data(self, domain: str, chain_value: str, cookie: str, timestamp: float):
        """
        保存 chain 数据到数据库

        Args:
            domain (str): 请求域名
            chain_value (str): chain 值
            cookie (str): 完整的 Cookie
            timestamp (float): 时间戳
        """
        try:
            # 确保数据库连接
            if not self.db_manager.connected:
                success = self.db_manager.connect()
                if not success:
                    logger.error("无法连接到数据库")
                    return

            # 转换时间戳
            dt_timestamp = datetime.fromtimestamp(timestamp)

            # 插入数据
            success = self.db_manager.insert_chain_data(
                domain=domain,
                chain_value=chain_value,
                cookie=cookie,
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


def start():
    """
    启动脚本时的初始化
    """
    logger.info("Chain Cookie 拦截器启动")


def done():
    """
    脚本结束时的清理工作
    """
    logger.info("Chain Cookie 拦截器关闭")
