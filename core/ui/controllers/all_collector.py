import time
from datetime import datetime
from core.utils.database import db_manager

from core.utils.tools.proxy_utils import enable_global_proxy, disable_global_proxy
from core.utils.scheduler_manager import SchedulerManager
from core.ui.controllers.data_collector import QNDataCollector
from core.ui.controllers.dbz_data_collector import DBZDataCollector


class AllCollector:

    def __init__(self, scheduler_manager=None):
        self.process_obj = None
        self.log_callback = None  # 日志回调函数
        self.scheduler_manager = scheduler_manager or SchedulerManager()

    def _import_auto_processes(self):
        """延迟导入自动化处理模块，避免uiautomator2兼容性问题"""
        from core.automation.auto_process import ChaLiXiongProcess, XingHaiProcess, LeYouProcess, QingniaoUnitProcess, \
            DianfengVSProcess, JiMuProcess
        return ChaLiXiongProcess, XingHaiProcess, LeYouProcess, QingniaoUnitProcess, DianfengVSProcess, JiMuProcess

    def _collect_qn_data(self, wb_name, chain_id):
        """执行青鸟数据收集任务"""
        self.log_callback(f"开始执行{wb_name}-{chain_id}数据收集任务...")
        qn_collector = QNDataCollector()
        qn_collector.log_callback = self.log_callback  # 设置日志回调
        qn_collector.get_all_data()
        self.log_callback("青鸟数据收集任务完成")

    def _collect_dbz_data(self):
        """执行大巴掌平台数据收集任务"""
        self.log_callback("开始执行大巴掌平台数据收集任务...")
        dbz_collector = DBZDataCollector()
        result = dbz_collector.run_full_process()
        self.log_callback(f"大巴掌平台数据收集任务完成，结果: {result.get('mongodb_save_result', 'Unknown')}")
        return result

    def get_all_data(self):
        try:
            # 发送日志到UI
            self.log_callback("开始执行吉姆电竞数据收集任务...")

            # 延迟导入自动化处理模块
            _, _, _, _, _, JiMuProcess = self._import_auto_processes()

            self.process_obj = JiMuProcess()
            self.process_obj.main_process()
            time.sleep(5)

            # 检查数据时间戳
            check_res = self._check_data_timestamp("吉姆电竞")

            # 调用QNDataCollector获取青鸟数据
            if check_res:
                self._collect_qn_data('吉姆电竞', check_res)

            if self.log_callback:
                self.log_callback("吉姆电竞数据收集任务完成，开始执行查理熊数据收集任务...")

            # 延迟导入自动化处理模块
            ChaLiXiongProcess, _, _, _, _, _ = self._import_auto_processes()

            self.process_obj = ChaLiXiongProcess()
            self.process_obj.main_process()
            time.sleep(5)

            # 检查数据时间戳
            check_res = self._check_data_timestamp("查理熊")

            # 调用QNDataCollector获取青鸟数据
            if check_res:
                self._collect_qn_data('查理熊', check_res)

            if self.log_callback:
                self.log_callback("查理熊数据收集任务完成，开始执行星海电竞馆数据收集任务...")

            # 延迟导入自动化处理模块
            _, XingHaiProcess, _, _, _, _ = self._import_auto_processes()

            self.process_obj = XingHaiProcess()
            self.process_obj.main_process()
            time.sleep(5)

            # 检查数据时间戳
            check_res = self._check_data_timestamp("星海电竞馆")

            # 调用QNDataCollector获取青鸟数据
            if check_res:
                self._collect_qn_data('青海电竞馆', check_res)

            if self.log_callback:
                self.log_callback("星海电竞馆数据收集任务完成，开始执行乐游数据收集任务...")

            # 延迟导入自动化处理模块
            _, _, LeYouProcess, _, _, _ = self._import_auto_processes()

            self.process_obj = LeYouProcess()
            self.process_obj.main_process()
            time.sleep(5)

            # 检查数据时间戳
            check_res = self._check_data_timestamp("乐游")

            # 调用QNDataCollector获取青鸟数据
            if check_res:
                self._collect_qn_data('乐游', check_res)
            if self.log_callback:
                self.log_callback("乐优数据收集任务完成，开始执行青鸟数据收集任务...")

            # 延迟导入自动化处理模块
            _, _, _, QingniaoUnitProcess, _, _ = self._import_auto_processes()

            self.process_obj = QingniaoUnitProcess()
            self.process_obj.main_process()
            time.sleep(5)

            # 检查数据时间戳
            check_res = self._check_data_timestamp("青鸟")

            # 调用QNDataCollector获取青鸟数据
            if check_res:
                self._collect_qn_data('青鸟', check_res)

            if self.log_callback:
                self.log_callback("青鸟数据收集任务完成，开始执行电锋VS数据收集任务...")

            # self.process_obj = DianfengVSProcess()
            # self.process_obj.main_process()
            # time.sleep(5)
            #
            # # 检查数据时间戳
            # self._check_data_timestamp("电锋VS")

            # 调用QNDataCollector获取青鸟数据
            # self._collect_qn_data()

            if self.log_callback:
                self.log_callback("开始执行大巴掌平台数据收集任务...")
            
            # 调用大巴掌平台数据收集功能
            self._collect_dbz_data()

            if self.log_callback:
                self.log_callback("所有数据收集任务完成")
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"数据收集任务执行出错: {str(e)}")
            # 记录错误但不中断定时任务的后续执行
            import traceback
            print(f"定时任务执行错误: {traceback.format_exc()}")

    def _check_data_timestamp(self, process_name: str):
        """检查数据库中的数据时间戳与当前时间的差距"""
        # 确保数据库已连接
        if not db_manager.connected:
            print(f"警告: 数据库未连接，正在尝试连接...")
            if not db_manager.connect():
                print(f"错误: 无法连接到数据库，无法检查 {process_name} 的时间戳")
                self.log_callback(f"错误: 无法连接到数据库，无法检查 {process_name} 的时间戳")
                return None
        
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
                self.log_callback(f"{process_name}- {chain_id} - 时间校验成功：{created_at}")
            else:
                self.log_callback(f"{process_name} - 时间差距: {int(time_diff)}秒")
            return chain_id
        else:
            self.log_callback(f"{process_name} - 未找到数据或created_at字段")
            return None

    def start_scheduled_task(self, hours_interval=2):
        """启动定时任务，可配置间隔小时数"""
        self.scheduler_manager.add_scheduled_job(
            func=self.get_all_data,
            job_id='all_data_collection',
            hours_interval=hours_interval,
            name='所有数据收集任务'
        )
        self.scheduler_manager.start_scheduler()
        if self.log_callback:
            self.log_callback(f"定时任务已启动，每{hours_interval}小时执行一次")

    def stop_scheduled_task(self):
        """停止定时任务"""
        self.scheduler_manager.remove_job('all_data_collection')
        if self.log_callback:
            self.log_callback("定时任务已停止")

    def is_scheduler_running(self):
        """检查调度器是否正在运行"""
        return self.scheduler_manager.is_job_scheduled('all_data_collection')