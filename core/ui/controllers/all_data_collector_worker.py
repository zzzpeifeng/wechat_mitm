from PyQt5.QtCore import QThread, pyqtSignal

from core.ui.controllers.all_collector import AllCollector


class AllDataCollectorWorker(QThread):
    """
    所有数据收集工作线程类
    """
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.all_data_collector = AllCollector()

    def run(self):
        try:
            self.log_message.emit("开始执行所有数据收集任务...")
            # 设置日志回调函数，以便AllCollector可以发送日志消息到UI
            self.all_data_collector.log_callback = lambda msg: self.log_message.emit(msg)
            self.all_data_collector.get_all_data()
            self.progress.emit("所有数据收集任务完成")
        except Exception as e:
            error_msg = f"所有数据收集任务失败: {str(e)}"
            self.progress.emit(error_msg)
            self.log_message.emit(error_msg)
        finally:
            self.finished.emit()
