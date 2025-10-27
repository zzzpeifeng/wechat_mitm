# ui/controllers/main_controller.py
from PyQt5.QtCore import QObject, pyqtSignal
from typing import List
import logging

from core.ui.views.main_window import MitmProxyMainView
from core.ui.controllers.proxy_controller import ProxyController
from core.ui.controllers.data_collector import DataCollector
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
        self.data_collector = DataCollector()
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
        self.view.collect_checkbox.stateChanged.connect(self.on_collect_toggle)
        self.view.mitm_service_btn.clicked.connect(self.on_mitm_service_toggle)
        self.view.proxy_btn.clicked.connect(self.on_proxy_toggle)
        self.view.clear_log_btn.clicked.connect(self.on_clear_logs)

        # 业务逻辑信号连接
        self.data_collected.connect(self.on_data_collected)
        self.status_updated.connect(self.on_status_updated)

    def initialize_services(self):
        """初始化服务"""
        # 初始化数据库连接
        if self.db_manager.connect():
            self.view.db_status_label.setText("数据库: 已连接")
            self.view.db_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.view.db_status_label.setText("数据库: 连接失败")
            self.view.db_status_label.setStyleSheet("color: red; font-weight: bold;")

        self.view.log_message("控制器初始化完成")

    def on_collect_toggle(self, state):
        """数据收集开关切换"""
        is_checked = state == 2  # Qt.Checked
        self.is_collecting = is_checked

        # 获取目标域名
        domain_text = self.view.domain_input.text()
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
                self.view.mitm_service_btn.setText("停止 MitmProxy 服务")
                self.view.mitm_status_label.setText("MitmProxy: 运行中")
                self.view.mitm_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.view.log_message("MitmProxy 服务启动成功")
            else:
                self.view.log_message("MitmProxy 服务启动失败")
                self.view.mitm_service_btn.setChecked(False)
        else:
            # 停止服务
            self.proxy_controller.stop_mitmproxy()
            self.is_mitm_running = False
            self.view.mitm_service_btn.setText("启动 MitmProxy 服务")
            self.view.mitm_status_label.setText("MitmProxy: 未运行")
            self.view.mitm_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.view.log_message("MitmProxy 服务已停止")

    def on_proxy_toggle(self):
        """全局代理开关切换"""
        if not self.is_proxy_enabled:
            # 启用代理
            success = self.proxy_controller.enable_global_proxy()
            if success:
                self.is_proxy_enabled = True
                self.view.proxy_btn.setText("禁用全局代理")
                self.view.proxy_status_label.setText("全局代理: 已启用")
                self.view.proxy_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.view.log_message("全局代理已启用")
            else:
                self.view.log_message("全局代理启用失败")
                self.view.proxy_btn.setChecked(False)
        else:
            # 禁用代理
            self.proxy_controller.disable_global_proxy()
            self.is_proxy_enabled = False
            self.view.proxy_btn.setText("启用全局代理")
            self.view.proxy_status_label.setText("全局代理: 未启用")
            self.view.proxy_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.view.log_message("全局代理已禁用")

    def on_clear_logs(self):
        """清除日志"""
        self.view.log_text.clear()

    def on_data_collected(self, count: int):
        """数据收集回调"""
        self.collected_count += count
        self.view.collected_count_label.setText(f"已收集数据: {self.collected_count} 条")

    def on_status_updated(self, service: str, status: bool):
        """状态更新回调"""
        if service == "mitm":
            self.is_mitm_running = status
            if status:
                self.view.mitm_status_label.setText("MitmProxy: 运行中")
                self.view.mitm_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.view.mitm_status_label.setText("MitmProxy: 未运行")
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
