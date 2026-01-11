# core/data_collector.py
import time
import logging
import uuid
import urllib3
from dotenv import load_dotenv
import requests
from core.utils.tools.tools import dict_to_cookie_string, parse_cookie_header
from PyQt5.QtCore import QThread, pyqtSignal

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
from core.utils.database import get_db_manager
from core.utils.tools.feishu_sheet_client import FeishuSheetClient
from core.ui.controllers.dbz_data_collector import DBZDataCollector

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
        # 初始化飞书表格客户端
        self.feishu_client = FeishuSheetClient()

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

    def update_db_online_data(self, data_dict):
        """
        更新数据库中的线上数据

        Args:
            data_dict (dict): 从青鸟平台获取的数据
        """
        upload_data = {}
        for index, store in enumerate(data_dict.get('offline_stores', []), 1):
            # 计算总座位数
            total_seats = store.get('online_machine_count', 0) + store.get('offline_machine_count', 0)
            off_store_key = f'{store.get('offline_store_id')}-{store.get('offline_store_name', '')}'
            online_value = f'{str(store.get('online_machine_count', 0))} / {str(total_seats)}'
            upload_data.update({off_store_key: online_value})
        self.db_manager.insert_online_rate_v2(upload_data)

    def upload_to_feishu_sheet(self, data_dict):
        """
        将数据上传到飞书电子表格
        
        Args:
            data_dict (dict): 从青鸟平台获取的数据
        """
        try:
            # 表格配置信息（需要根据实际情况修改）
            SPREADSHEET_TOKEN = "LkgdwebJHi5yOUkgOPAc2fnonFb"  # 电子表格token
            SHEET_ID = "9a4941"  # 工作表ID

            # 构造数据行
            rows = []
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 处理每个线下门店的数据
            for index, store in enumerate(data_dict.get('offline_stores', []), 1):
                # 生成唯一的ID（使用UUID）
                unique_id = str(uuid.uuid4())

                # 计算总座位数
                total_seats = store.get('online_machine_count', 0) + store.get('offline_machine_count', 0)

                row = [
                    unique_id,  # ID（使用UUID保证唯一性）
                    data_dict.get('store_name', ''),  # 店铺
                    store.get('offline_store_name', ''),  # 门店
                    f'{str(store.get('online_machine_count', 0))} / {str(total_seats)}',  # 在线坐席数 / 总座位数
                    timestamp,  # 记录时间
                    "",  # 其他数据（可按需填充）
                    ""  # 备注（可按需填充）
                ]
                rows.append(row)

            # 如果有数据需要上传
            if rows:
                # 调用飞书表格客户端追加数据
                result = self.feishu_client.append_sheet_data(SPREADSHEET_TOKEN, SHEET_ID, rows)
                if result.get("success"):
                    self.log(f"成功上传 {len(rows)} 条数据到飞书表格")
                    return True
                else:
                    error_msg = result.get("error_msg", "未知错误")
                    self.log(f"上传数据到飞书表格失败: {error_msg}")
                    return False
            else:
                self.log("没有数据需要上传到飞书表格")
                return True

        except Exception as e:
            self.log(f"上传数据到飞书表格时发生异常: {e}")
            return False

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
        # 获取门店列表
        offline_store_list = self.get_offline_store_list()
        if offline_store_list['code'] != 0:
            # print(f'获取门店列表信息失败:{self.cookie_header.get('chain-id')}')
            self.log(f'获取门店列表信息失败:{self.cookie_header.get("chain-id")}')
            self.log(self.cookie_header)
            return
        # 循环门店列表
        self.log(f'门店数:{len(offline_store_list.get("data"))}')
        for store in offline_store_list['data']:
            offline_store_id = store.get('id')
            if offline_store_id == data_dict.get('store_id'):
                self.log(f'门店id:{offline_store_id}与品牌店铺id相同，跳过')
                continue

            # 选择门店
            selected_res = self.select_offline_store(offline_store_id)  # 选择门店
            if selected_res['code'] != 0:
                self.log(f'选择门店失败:{store.get("name")}')
                continue
            self.log(f'选择门店成功:{store.get("name")}')

            # 获取门店订座信息
            area_list = []
            # 重试三次，三次失败后不获取该门店，继续保存
            retry_count = 0
            temp_book_seat_info = self.get_offline_store_data()
            while temp_book_seat_info.get('code') != 0:
                self.log(
                    f"{store.get('name')}获取门店订座信息失败，正在重试...:{temp_book_seat_info.get('msg')}，等待50s")
                time.sleep(50)
                retry_count += 1
                if retry_count >= 3:
                    self.log(f"{store.get('name')}获取门店订座信息失败，重试3次仍失败，放弃获取该门店")
                    break

                selected_res = self.select_offline_store(offline_store_id)  # 选择门店
                if selected_res['code'] != 0:
                    self.log(f'选择门店失败:{store.get("name")}')
                    continue
                self.log(f'选择门店成功:{store.get("name")}')
                try:
                    temp_book_seat_info = self.get_offline_store_data()
                except Exception as e:
                    self.log(f"{store.get('name')}获取门店订座信息失败，重试失败:{e}")
                    continue
            if temp_book_seat_info.get('code') != 0:
                self.log(f"{store.get('name')}获取门店订座信息失败:{temp_book_seat_info.get('msg')},跳过")
                continue

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
                'offline_machine_count': offline_online_machine_count,
                'online_machine_count': offline_offline_machine_count
            }
            # 组装店铺信息
            data_dict['offline_stores'].append(offline_store_dict)
            self.log(f"{store.get('name')}获取门店订座信息成功,等待2s，防止被封禁")
            time.sleep(2)
        print(data_dict)
        # self.db_manager.insert_online_rate(data_dict)
        self.update_db_online_data(data_dict)

        # 上传数据到飞书表格
        self.log("开始上传数据到飞书表格...")
        upload_success = self.upload_to_feishu_sheet(data_dict)
        if upload_success:
            self.log("数据上传到飞书表格完成")
        else:
            self.log("数据上传到飞书表格失败")

        # 调用大巴掌平台数据收集功能
        self.log("开始执行大巴掌平台数据收集任务...")
        dbz_collector = DBZDataCollector()
        dbz_result = dbz_collector.run_full_process()
        self.log(f"大巴掌平台数据收集任务完成，结果: {dbz_result.get('mongodb_save_result', 'Unknown')}")


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