# core/data_collector.py
import time
import logging
from dotenv import load_dotenv
import requests
from core.utils.tools.tools import dict_to_cookie_string, parse_cookie_header
from PyQt5.QtCore import QThread, pyqtSignal

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
        self.log_callback = None  # 添加日志回调属性

    def log(self, message):
        """日志输出方法"""
        if self.log_callback:
            self.log_callback(message)  # 通过回调函数发送日志
        else:
            print(message)  # 默认打印到控制台

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
                for key, value in self.cookie_header.items():
                    self.session.cookies.set(key, value)
                logger.info(f"成功加载域名 {self.host} 的 cookie:{self.cookie_header}")
            else:
                logger.warning(f"域名 {self.host} 的 cookie 不存在")
        else:
            logger.warning("数据库连接失败，无法加载 cookie")

    def get_store_info(self):
        '''
        获取门店信息
        :return:
        '''
        # self.load_cookie()
        url = f"https://{self.host}/default/index"

        params = {
            "chain_id": self.cookie_header.get('chain-id')
        }
        response = self.session.get(url, params=params, verify=False)
        logger.info(f"获取门店信息:{response.text}")
        return response.json()

    def get_offline_store_list(self):
        '''
        获取线下门店列表
        :return:
        '''

        url = f"https://{self.host}/default/chains"

        params = {
            "name": "",
            "chain_id": self.cookie_header.get('chain-id'),
            "dingzuo": "1"
        }
        response = self.session.get(url, params=params, verify=False)
        logger.info(f"获取线下门店列表:{response.text}")
        return response.json()

    def select_offline_store(self, offline_store_id: str):
        '''
        选择线下门店
        :param store_id: 门店ID
        :return:
        '''
        url = f"https://{self.host}/default/session-mch"
        params = {
            "mch_id": offline_store_id
        }

        response = self.session.get(url, params=params, verify=False)
        return response.json()

    def get_offline_store_data(self):
        '''
        获取线下门店数据
        :return:
        '''
        url = f"https://{self.host}/dingzuo/item"
        response = self.session.get(url, verify=False)
        return response.json()

    def get_all_data(self):
        '''
        获取所有数据
        :return:
        '''
        # 获取一个连锁网吧的店铺信息
        self.load_cookie()
        store_info_resp = self.get_store_info()

        if store_info_resp['code'] == 0:
            self.log(f"获取品牌店铺信息成功:{store_info_resp.get('data').get('chain_name')}")
        else:
            self.log(f"获取品牌店铺信息失败:{store_info_resp.get('msg')}")
            return

        data_dict = {
            'store_id': self.cookie_header.get('chain-id'),
            'store_name': store_info_resp.get('data').get('chain_name'),
            'offline_stores': []
        }
        offline_store_list = self.get_offline_store_list()
        if offline_store_list['code'] != 0:
            # print(f'获取门店列表信息失败:{self.cookie_header.get('chain-id')}')
            self.log(f'获取门店列表信息失败:{self.cookie_header.get("chain-id")}')
            self.log(self.cookie_header)
            return

        for store in offline_store_list['data']:
            offline_store_id = store.get('id')
            selected_res = self.select_offline_store(offline_store_id)  # 选择门店
            if selected_res['code'] != 0:
                self.log(f'选择门店失败:{store.get("name")}')
                continue
            self.log(f'选择门店成功:{store.get("name")}')
            # 获取门店订座信息
            area_list = []
            temp_book_seat_info = self.get_offline_store_data()
            while temp_book_seat_info.get('code') != 0:
                self.log(
                    f"{store.get('name')}获取门店订座信息失败，正在重试...:{temp_book_seat_info.get('msg')}，等待60s")
                time.sleep(60)
                selected_res = self.select_offline_store(offline_store_id)  # 选择门店
                if selected_res['code'] != 0:
                    self.log(f'选择门店失败:{store.get("name")}')
                    continue
                self.log(f'选择门店成功:{store.get("name")}')
                temp_book_seat_info = self.get_offline_store_data()
            self.log(f"{store.get('name')}获取门店订座信息成功,开始组装信息")
            offline_online_machine_count = 0
            offline_offline_machine_count = 0
            for direct_item in temp_book_seat_info.get('data'):
                # 组装区域信息

                if direct_item.get('type') != "0":
                    continue
                item_online_machine_count = len(direct_item.get('on_machine'))
                item_offline_machine_count = len(direct_item.get('off_machine'))

                area_list.append({
                    'area_name': direct_item.get('name'),
                    'online_machine_count': item_online_machine_count,
                    'offline_machine_count': item_offline_machine_count
                })
                offline_online_machine_count += item_online_machine_count
                offline_offline_machine_count += item_offline_machine_count
            offline_store_dict = {
                'offline_store_id': store.get('id'),
                'offline_store_name': store.get('name'),
                'areas': area_list,
                'offline_machine_count': offline_offline_machine_count,
                'online_machine_count': offline_online_machine_count
            }
            # 组装店铺信息
            data_dict['offline_stores'].append(offline_store_dict)
            self.log(f"{store.get('name')}获取门店订座信息成功,等待2s，防止被封禁")
            time.sleep(2)
        print(data_dict)
        self.db_manager.insert_online_rate(data_dict)


class DataCollectionWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    log_message = pyqtSignal(str)  # 添加日志信号

    def __init__(self, qn_data_obj):
        super().__init__()
        self.data_collector = qn_data_obj

    def run(self):
        try:
            # 设置数据收集器的日志回调函数
            self.data_collector.log_callback = lambda msg: self.log_message.emit(msg)
            self.data_collector.get_all_data()
            self.progress.emit("数据采集完成")
        except Exception as e:
            self.progress.emit(f"数据采集失败:{e}")
        finally:
            self.finished.emit()


if __name__ == '__main__':
    collector = QNDataCollector()
    collector.db_manager.connect()
    collector.get_all_data()
