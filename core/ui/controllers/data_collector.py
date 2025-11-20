# core/data_collector.py
import time
from typing import List, Optional
import re
import logging
from dotenv import load_dotenv
import requests

from core.utils.tools.tools import dict_to_cookie_string, parse_cookie_header

load_dotenv()
from core.utils.database import get_db_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QNDataCollector:
    """
    数据收集器 - 青鸟平台管理数据收集逻辑
    """

    def __init__(self):
        self.host = 'chain36226.tmwanba.com'
        self.db_manager = get_db_manager()
        self.cookie_header = None
        self.session = requests.Session()

    def load_cookie(self):
        # 确保数据库连接
        if not self.db_manager.connected:
            success = self.db_manager.connect()
            if not success:
                logger.warning("无法连接到数据库，使用默认域名列表")
                return

        # 获取 target_domains 集合
        if self.db_manager.db is not None:
            cookie_collection = self.db_manager.db["chain_cookies"]
            cookie_document = cookie_collection.find_one({"host": self.host})
            if cookie_document:
                self.cookie_header = parse_cookie_header(cookie_document["cookie_header"])
                logger.info(f"成功加载域名 {self.host} 的 cookie:{self.cookie_header}")
            else:
                logger.warning(f"域名 {self.host} 的 cookie 不存在")
        else:
            logger.warning("数据库连接失败，无法加载 cookie")

    def get_offline_store_list(self):
        '''
        获取线下门店列表
        :return:
        '''
        self.load_cookie()
        url = f"https://{self.host}/default/chains"

        headers = {
            # "Cookie": f"chain-id={self.CHAIN_ID}; chain={self.CHAIN}; {self.HM_LVT_KEY}={self.HM_LVT_VALUE}; HMACCOUNT={self.HMACCOUNT}; {self.HM_LPVT_KEY}={self.HM_LPVT_VALUE}",
            "Cookie": dict_to_cookie_string(self.cookie_header),
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) MacWechat/3.8.7(0x13080712) UnifiedPCMacWechat(0xf2641112) XWEB/16730 Flue",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"https://{self.host}/release208/",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i"
        }

        params = {
            "name": "",
            "chain_id": self.cookie_header.get('chain-id'),
            "dingzuo": "1"
        }
        response = self.session.get(url, headers=headers, params=params, verify=False)
        logger.info(f"获取线下门店列表:{response.text}")
        return response.json()

    def select_offline_store(self, offline_store_id: str):
        '''
        选择线下门店
        :param store_id: 门店ID
        :return:
        '''
        url = f"https://{self.host}/default/select_chain"
        params = {
            "mch_id": offline_store_id
        }

        response = requests.get(url, params=params)
        return response.json()

    def get_offline_store_data(self):
        '''
        获取线下门店数据
        :return:
        '''
        url = f"https://{self.host}/dingzuo/item"
        response = requests.get(url)
        return response.json()

    def get_all_data(self):
        '''
        获取所有数据
        :return:
        '''
        # 获取一个连锁网吧的门店信息
        data_dict = {
            'store_id': self.cookie_header.get('chain-id'),
            'store_name': self.host,
            'offline_stores': []
        }
        offline_store_list = self.get_offline_store_list()
        if offline_store_list['code'] != 0:
            print(f'获取门店列表信息失败:{self.cookie_header.get('chain-id')}')
            print(self.cookie_header)
            return
        for store in offline_store_list['data']:
            offline_store_id = store.get('id')
            self.select_offline_store(offline_store_id)  # 选择门店
            # 获取门店订座信息
            area_list = []
            temp_book_seat_info = self.get_offline_store_data()
            while temp_book_seat_info.get('code') != 0:
                print(f"{store.get('name')}获取门店订座信息失败，正在重试...:{temp_book_seat_info.get('msg')}，等待50s")
                time.sleep(50)
                temp_book_seat_info = self.get_offline_store_data()
            for direct_item in temp_book_seat_info.get('data'):
                # 组装区域信息
                area_list.append({
                    'area_name': direct_item.get('name'),
                    'online_machine_count': len(direct_item.get('on_machine')),
                    'offline_machine_count': len(direct_item.get('off_machine'))
                })
            offline_store_dict = {
                'offline_store_id': store.get('id'),
                'offline_store_name': store.get('name'),
                'areas': area_list
            }
            # 组装店铺信息
            data_dict['offline_stores'].append(offline_store_dict)
        print(data_dict)
        self.db_manager.insert_online_rate(data_dict)


if __name__ == '__main__':
    collector = QNDataCollector()
    collector.db_manager.connect()
    collector.get_offline_store_list()
