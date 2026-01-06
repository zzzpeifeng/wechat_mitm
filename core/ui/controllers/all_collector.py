import time

from core.automation.auto_process import ChaLiXiongProcess, XingHaiProcess, LeYouProcess, QingniaoUnitProcess, \
    DianfengVSProcess
from core.utils.tools.proxy_utils import enable_global_proxy, disable_global_proxy


class AllCollector:

    def __init__(self):
        self.process_obj = None
        # self.clx_process = ChaLiXiongProcess()  # 查理熊
        # self.xinghai_process = XingHaiProcess()  # 星海电竞馆
        # self.leyou_process = LeYouProcess()
        # self.qingniao_process = QingniaoUnitProcess()
        # self.dianfeng_process = DianfengVSProcess()
        self.log_callback = None  # 日志回调函数

    def get_all_data(self):
        # 发送日志到UI
        if enable_global_proxy():
            self.log_callback("查理熊采集cookie前打开代理：成功")
        else:
            self.log_callback("查理熊采集cookie前打开代理：失败")
        self.log_callback("开始执行查理熊数据收集任务...")
        self.process_obj = ChaLiXiongProcess()
        self.process_obj.main_process()
        time.sleep(5)
        if disable_global_proxy():
            self.log_callback("查理熊采集cookie前禁用代理：成功")
        else:
            self.log_callback("禁用全局禁用代理：失败")

        # if self.log_callback:
        #     self.log_callback("查理熊数据收集任务完成，开始执行星海电竞馆数据收集任务...")
        #
        # self.xinghai_process.main_process()
        # time.sleep(5)
        #
        # if self.log_callback:
        #     self.log_callback("星海电竞馆数据收集任务完成，开始执行乐优数据收集任务...")
        #
        # self.leyou_process.main_process()
        # time.sleep(5)
        #
        # if self.log_callback:
        #     self.log_callback("乐优数据收集任务完成，开始执行青鸟数据收集任务...")
        #
        # self.qingniao_process.main_process()
        # time.sleep(5)
        #
        # if self.log_callback:
        #     self.log_callback("青鸟数据收集任务完成，开始执行电锋VS数据收集任务...")
        #
        # self.dianfeng_process.main_process()
        # time.sleep(5)
        #
        # if self.log_callback:
        #     self.log_callback("所有数据收集任务完成")
