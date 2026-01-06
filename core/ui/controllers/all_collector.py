import time
from datetime import datetime
from core.utils.database import db_manager

from core.automation.auto_process import ChaLiXiongProcess, XingHaiProcess, LeYouProcess, QingniaoUnitProcess, \
    DianfengVSProcess
from core.utils.tools.proxy_utils import enable_global_proxy, disable_global_proxy


class AllCollector:

    def __init__(self):
        self.process_obj = None
        self.log_callback = None  # 日志回调函数

    def get_all_data(self):
        # 发送日志到UI
        self.log_callback("开始执行查理熊数据收集任务...")
        self.process_obj = ChaLiXiongProcess()
        self.process_obj.main_process()
        time.sleep(5)

        # 检查数据时间戳
        self._check_data_timestamp("查理熊")

        if self.log_callback:
            self.log_callback("查理熊数据收集任务完成，开始执行星海电竞馆数据收集任务...")

        self.process_obj = XingHaiProcess()
        self.process_obj.main_process()
        time.sleep(5)

        # 检查数据时间戳
        self._check_data_timestamp("星海电竞馆")

        if self.log_callback:
            self.log_callback("星海电竞馆数据收集任务完成，开始执行乐游数据收集任务...")

        self.process_obj = LeYouProcess()
        self.process_obj.main_process()
        time.sleep(5)

        # 检查数据时间戳
        self._check_data_timestamp("乐游")

        if self.log_callback:
            self.log_callback("乐优数据收集任务完成，开始执行青鸟数据收集任务...")

        self.process_obj = QingniaoUnitProcess()
        self.process_obj.main_process()
        time.sleep(5)

        # 检查数据时间戳
        self._check_data_timestamp("青鸟")

        if self.log_callback:
            self.log_callback("青鸟数据收集任务完成，开始执行电锋VS数据收集任务...")

        self.process_obj = DianfengVSProcess()
        self.process_obj.main_process()
        time.sleep(5)

        # 检查数据时间戳
        self._check_data_timestamp("电锋VS")

        if self.log_callback:
            self.log_callback("所有数据收集任务完成")

    def _check_data_timestamp(self, process_name: str):
        """检查数据库中的数据时间戳与当前时间的差距"""
        data = db_manager.get_chain_cookie()
        if data and 'created_at' in data:
            created_at = data['created_at']
            chain_id = data['chain_id']
            # 确保 created_at 是 datetime 对象
            if isinstance(created_at, str):
                # 尝试解析ISO格式的时间字符串
                try:
                    # 处理带时区信息的ISO格式
                    if '.' in created_at and '+' in created_at:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    elif 'Z' in created_at:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    elif '.' in created_at:
                        created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    # 如果解析失败，尝试其他格式
                    try:
                        created_at = datetime.fromisoformat(created_at)
                    except ValueError:
                        self.log_callback(f"无法解析 {process_name} 的时间戳: {created_at}")
                        return

            current_time = datetime.now()
            time_diff = abs((current_time - created_at).total_seconds())

            if time_diff < 60:  # 小于1分钟
                self.log_callback(f"{process_name}- {chain_id} - 成功")
            else:
                self.log_callback(f"{process_name} - 时间差距: {int(time_diff)}秒")
        else:
            self.log_callback(f"{process_name} - 未找到数据或created_at字段")
