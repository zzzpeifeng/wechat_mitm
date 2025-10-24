# core/data_collector.py
from typing import List, Optional
import re
import logging

class DataCollector:
    """
    数据收集器 - 管理数据收集逻辑
    """

    def __init__(self):
        self.is_collecting = False
        self.target_domains: List[str] = []
        self.logger = logging.getLogger(__name__)

    def set_target_domains(self, domains: List[str]):
        """
        设置目标域名列表

        Args:
            domains (List[str]): 目标域名列表
        """
        self.target_domains = domains
        self.logger.info(f"设置目标域名: {domains}")

    def enable_collection(self, enabled: bool):
        """
        启用或禁用数据收集

        Args:
            enabled (bool): 是否启用数据收集
        """
        self.is_collecting = enabled
        action = "启用" if enabled else "禁用"
        self.logger.info(f"数据收集{action}")

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
        从Cookie字符串中提取chain值

        Args:
            cookie_str (str): Cookie字符串

        Returns:
            Optional[str]: 提取到的chain值，未找到则返回None
        """
        if not cookie_str:
            return None

        # 使用正则表达式匹配chain值
        chain_match = re.search(r'chain=([^;]*)', cookie_str)
        if chain_match:
            return chain_match.group(1).strip()
        return None
