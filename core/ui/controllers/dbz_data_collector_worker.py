# ui/controllers/dbz_data_collector_worker.py
from PyQt5.QtCore import QThread, pyqtSignal
from core.ui.controllers.dbz_data_collector import DBZDataCollector


class DBZDataCollectorWorker(QThread):
    """
    DBZ数据收集工作线程类
    """
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    log_message = pyqtSignal(str)  # 添加日志信号

    def __init__(self, dbz_data_collector: DBZDataCollector):
        """
        初始化DBZ数据收集工作线程
        
        Args:
            dbz_data_collector (DBZDataCollector): DBZ数据收集器实例
        """
        super().__init__()
        self.dbz_data_collector = dbz_data_collector
        # 飞书表格配置信息（与QNDataCollector中保持一致）
        self.spreadsheet_token = "LkgdwebJHi5yOUkgOPAc2fnonFb"  # 电子表格token
        self.sheet_id = "9a4941"  # 工作表ID

    def run(self):
        """
        线程运行方法
        """
        try:
            # 运行完整的数据收集流程并上传到飞书表格
            self.log_message.emit("开始执行大巴掌数据收集任务...")
            result = self.dbz_data_collector.run_full_process(
                spreadsheet_token=self.spreadsheet_token,
                sheet_id=self.sheet_id
            )
            
            # 输出统计信息
            total_brands = len(result["collected_data"])
            total_netbars = sum(len(brand["netbars"]) for brand in result["collected_data"])
            self.log_message.emit(f"数据收集完成，共收集到 {total_brands} 个品牌，{total_netbars} 个门店的数据")
            
            # 检查上传结果
            upload_result = result.get("upload_result", {})
            if upload_result.get("success"):
                self.log_message.emit(upload_result.get("message", "数据上传成功"))
            else:
                self.log_message.emit(f"数据上传失败: {upload_result.get('message', '未知错误')}")
            
            self.progress.emit("大巴掌数据收集任务完成")
        except Exception as e:
            error_msg = f"大巴掌数据收集任务失败: {str(e)}"
            self.progress.emit(error_msg)
            self.log_message.emit(error_msg)
        finally:
            self.finished.emit()