# ui/controllers/main_controller.py
from PyQt5.QtCore import QObject, pyqtSignal,Qt
from typing import List
import logging

from PyQt5.QtWidgets import QTableWidgetItem

from core.ui.controllers.data_collector import QNDataCollector, DataCollectionWorker
from core.ui.views.main_window import MitmProxyMainView
from core.ui.controllers.proxy_controller import ProxyController
from core.utils.database import get_db_manager


class MainController(QObject):
    """
    主控制器 - 协调UI和业务逻辑
    """

    # 信号定义
    data_collected = pyqtSignal(int)  # 数据收集信号
    status_updated = pyqtSignal(str, bool)  # 状态更新信号

    def __init__(self, view: MitmProxyMainView):
        super().__init__()
        self.view = view
        self.proxy_controller = ProxyController()
        self.data_qn_collector = QNDataCollector()
        self.qn_data_worker = None
        self.db_manager = get_db_manager()

        # 状态管理
        self.is_collecting = False
        self.is_mitm_running = False
        self.is_proxy_enabled = False
        self.collected_count = 0

        self.setup_connections()
        self.initialize_services()

    def setup_connections(self):
        """设置信号槽连接"""
        # UI事件连接
        # 数据收集控制连接
        # self.view.control_panel.collect_checkbox.stateChanged.connect(self.on_collect_toggle)
        self.view.control_panel.add_domain_btn.clicked.connect(self.on_add_domain)

        # 服务控制连接
        self.view.control_panel.mitm_service_btn.clicked.connect(self.on_mitm_service_toggle)
        self.view.control_panel.proxy_btn.clicked.connect(self.on_proxy_toggle)

        # 数据收集开始连接
        self.view.control_panel.crawler_btn.clicked.connect(self.on_crawler_toggle)

        # 日志控制连接
        self.view.log_panel.clear_log_btn.clicked.connect(self.on_clear_logs)

        # 业务逻辑信号连接
        self.data_collected.connect(self.on_data_collected)
        self.status_updated.connect(self.on_status_updated)

        # 添加域名按钮连接
        self.view.control_panel.add_domain_btn.clicked.connect(self.on_add_domain)

    def initialize_services(self):
        """初始化服务"""
        # 初始化数据库连接
        if self.db_manager.connect():
            self.view.status_panel.update_db_status(True)
            # 初始化时加载数据库中的域名数据
            self.load_domains_from_mongodb()
        else:
            self.view.status_panel.update_db_status(False)

        self.view.log_message("控制器初始化完成")

    def load_domains_from_mongodb(self) -> bool:
        """
        从MongoDB数据库加载域名数据到表格

        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查数据库连接状态 - 修复数据库对象布尔值判断问题
            if not self.db_manager.connected or self.db_manager.db is None:
                self.view.log_message("数据库未连接，无法加载域名")
                return False

            # 获取target_domains集合
            collection = self.db_manager.db["target_domains"]

            # 查询所有域名
            domains = list(collection.find({}, {"domain": 1}))

            # 清空现有表格内容
            table = self.view.control_panel.domain_table
            table.setRowCount(0)

            # 填充表格数据
            for domain_doc in domains:
                row_count = table.rowCount()
                table.insertRow(row_count)
                item = QTableWidgetItem(domain_doc["domain"])
                # 设置为不可编辑
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_count, 0, item)

            self.view.log_message(f"从数据库加载了 {len(domains)} 个域名")
            return True

        except Exception as e:
            logging.error(f"从MongoDB加载域名失败: {e}")
            self.view.log_message(f"加载域名失败: {str(e)}")
            return False

    def on_add_domain(self):
        """添加域名到列表"""
        # 获取输入的域名
        domain = self.view.control_panel.domain_input.text().strip()

        if domain:
            # 添加到表格显示
            table = self.view.control_panel.domain_table
            row_count = table.rowCount()
            table.insertRow(row_count)
            table.setItem(row_count, 0, QTableWidgetItem(domain))

            # 清空输入框
            self.view.control_panel.domain_input.clear()

            # TODO: 保存到MongoDB数据库
            self.save_domain_to_mongodb(domain)

            self.view.log_message(f"已添加域名: {domain}")
        else:
            self.view.log_message("请输入有效的域名")

    def save_domain_to_mongodb(self, domain: str) -> bool:
        """
        保存域名到MongoDB数据库

        Args:
            domain (str): 要保存的域名

        Returns:
            bool: 保存是否成功
        """
        try:
            # 检查数据库连接状态 - 修复数据库对象布尔值判断问题
            if not self.db_manager.connected or self.db_manager.db is None:
                self.view.log_message("数据库未连接，无法保存域名")
                return False

            # 获取或创建target_domains集合
            collection = self.db_manager.db["target_domains"]

            # 检查域名是否已存在
            existing_domain = collection.find_one({"domain": domain})
            if existing_domain:
                # 域名已存在，无需重复保存
                return True

            # 插入新域名
            from datetime import datetime
            result = collection.insert_one({
                "domain": domain,
                "created_at": datetime.now()
            })

            return result.acknowledged

        except Exception as e:
            logging.error(f"保存域名到MongoDB失败: {e}")
            self.view.log_message(f"保存域名失败: {str(e)}")
            return False


        # 获取目标域名
        domain_text = self.view.control_panel.domain_input.text()
        target_domains = [d.strip() for d in domain_text.split(',') if d.strip()]

        # 配置数据收集器
        self.data_collector.set_target_domains(target_domains)
        self.data_collector.enable_collection(is_checked)

        action = "启用" if is_checked else "禁用"
        self.view.log_message(f"数据收集{action}")

    def on_mitm_service_toggle(self):
        """MitmProxy服务开关切换"""
        if not self.is_mitm_running:
            # 启动服务
            success = self.proxy_controller.start_mitmproxy(self.view.log_message)
            if success:
                self.is_mitm_running = True
                self.view.control_panel.mitm_service_btn.setText("停止青鸟监控")
                self.view.status_panel.mitm_status_label.setText("青鸟监控: 运行中")
                self.view.status_panel.mitm_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.view.log_message("青鸟平台服务启动成功")
            else:
                self.view.log_message("青鸟平台服务启动失败")
                self.view.mitm_service_btn.setChecked(False)
        else:
            # 停止服务
            self.proxy_controller.stop_mitmproxy()
            self.is_mitm_running = False
            self.view.control_panel.mitm_service_btn.setText("启动青鸟监控")
            self.view.status_panel.mitm_status_label.setText("青鸟监控: 未运行")
            self.view.status_panel.mitm_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.view.log_message("青鸟监控 服务已停止")

    def on_proxy_toggle(self):
        """全局代理开关切换"""
        if not self.is_proxy_enabled:
            # 启用代理
            success = self.proxy_controller.enable_global_proxy()
            if success:
                self.is_proxy_enabled = True
                self.view.control_panel.proxy_btn.setText("禁用全局代理")
                self.view.status_panel.proxy_status_label.setText("全局代理: 已启用")
                self.view.status_panel.proxy_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.view.log_message("全局代理已启用")
            else:
                self.view.log_message("全局代理启用失败")
                self.view.proxy_btn.setChecked(False)
        else:
            # 禁用代理
            self.proxy_controller.disable_global_proxy()
            self.is_proxy_enabled = False
            self.view.control_panel.proxy_btn.setText("启用全局代理")
            self.view.status_panel.proxy_status_label.setText("全局代理: 未启用")
            self.view.status_panel.proxy_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.view.log_message("全局代理已禁用")


    def on_crawler_toggle(self):
        """爬虫开关切换"""
        # 先关闭全局代理、修改按钮状态
        self.proxy_controller.disable_global_proxy()
        self.is_proxy_enabled = False
        self.view.control_panel.proxy_btn.setText("启用全局代理")
        self.view.status_panel.proxy_status_label.setText("全局代理: 未启用")
        self.view.status_panel.proxy_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.view.log_message("由于开始爬虫，全局代理已禁用")

        # 爬虫开始
        # 创建并启动工作线程
        self.data_collection_worker = DataCollectionWorker(self.data_qn_collector)
        self.data_collection_worker.finished.connect(self.on_data_collection_finished)
        self.data_collection_worker.progress.connect(self.view.log_message)
        self.data_collection_worker.log_message.connect(self.view.log_message)  # 连接日志信号
        self.data_collection_worker.start()

        # 禁用爬虫按钮防止重复点击
        self.view.control_panel.crawler_btn.setEnabled(False)
        self.view.control_panel.crawler_btn.setText("数据收集中...")


    def on_data_collection_finished(self):
        """数据收集完成回调"""
        self.view.control_panel.crawler_btn.setEnabled(True)
        self.view.control_panel.crawler_btn.setText("开始爬虫")
        self.view.log_message("数据收集任务已完成")

        # 清理工作线程
        if self.qn_data_worker:
            self.qn_data_worker.deleteLater()
            self.qn_data_worker = None




    def on_clear_logs(self):
        """清除日志"""
        self.view.log_panel.log_text.clear()

    def on_data_collected(self, count: int):
        """数据收集回调"""
        self.collected_count += count
        self.view.collected_count_label.setText(f"已收集数据: {self.collected_count} 条")

    def on_status_updated(self, service: str, status: bool):
        """状态更新回调"""
        if service == "mitm":
            self.is_mitm_running = status
            if status:
                self.view.mitm_status_label.setText("青鸟监控: 运行中")
                self.view.mitm_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.view.mitm_status_label.setText("青鸟监控: 未运行")
                self.view.mitm_status_label.setStyleSheet("color: red; font-weight: bold;")
        elif service == "proxy":
            self.is_proxy_enabled = status
            if status:
                self.view.proxy_status_label.setText("全局代理: 已启用")
                self.view.proxy_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.view.proxy_status_label.setText("全局代理: 未启用")
                self.view.proxy_status_label.setStyleSheet("color: red; font-weight: bold;")

    def shutdown(self):
        """程序关闭时的清理工作"""
        # 停止所有服务
        if self.is_mitm_running:
            self.proxy_controller.stop_mitmproxy()
        if self.is_proxy_enabled:
            self.proxy_controller.disable_global_proxy()

        # 断开数据库连接
        self.db_manager.disconnect()

        self.view.log_message("程序已安全关闭")
