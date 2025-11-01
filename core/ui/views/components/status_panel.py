# ui/views/components/status_panel.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel
)

class StatusPanel(QWidget):
    """
    状态面板组件 - 显示各种服务和数据状态
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化状态面板UI"""
        layout = QHBoxLayout(self)

        # 服务状态组
        self.service_group = self._create_service_status_group()
        layout.addWidget(self.service_group)

        # 数据统计组
        self.stats_group = self._create_stats_group()
        layout.addWidget(self.stats_group)

    def _create_service_status_group(self) -> QGroupBox:
        """创建服务状态组"""
        group = QGroupBox("服务状态")
        layout = QVBoxLayout(group)

        self.mitm_status_label = QLabel("MitmProxy: 未运行")
        self.mitm_status_label.setObjectName("mitmStatusLabel")
        layout.addWidget(self.mitm_status_label)

        self.proxy_status_label = QLabel("全局代理: 未启用")
        self.proxy_status_label.setObjectName("proxyStatusLabel")
        layout.addWidget(self.proxy_status_label)

        self.db_status_label = QLabel("数据库: 未连接")
        self.db_status_label.setObjectName("dbStatusLabel")
        layout.addWidget(self.db_status_label)

        return group

    def _create_stats_group(self) -> QGroupBox:
        """创建数据统计组"""
        group = QGroupBox("数据统计")
        layout = QVBoxLayout(group)

        self.collected_count_label = QLabel("已收集数据: 0 条")
        self.collected_count_label.setObjectName("collectedCountLabel")
        layout.addWidget(self.collected_count_label)

        self.last_update_label = QLabel("最后更新: --")
        self.last_update_label.setObjectName("lastUpdateLabel")
        layout.addWidget(self.last_update_label)

        return group

    def update_mitm_status(self, running: bool):
        """更新MitmProxy状态显示"""
        status_text = "运行中" if running else "未运行"
        self.mitm_status_label.setText(f"MitmProxy: {status_text}")

        # 设置样式
        if running:
            self.mitm_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.mitm_status_label.setStyleSheet("color: red; font-weight: bold;")

    def update_proxy_status(self, enabled: bool):
        """更新代理状态显示"""
        status_text = "已启用" if enabled else "未启用"
        self.proxy_status_label.setText(f"全局代理: {status_text}")

        # 设置样式
        if enabled:
            self.proxy_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.proxy_status_label.setStyleSheet("color: red; font-weight: bold;")

    def update_db_status(self, connected: bool):
        """更新数据库状态显示"""
        status_text = "已连接" if connected else "未连接"
        self.db_status_label.setText(f"数据库: {status_text}")

        # 设置样式
        if connected:
            self.db_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.db_status_label.setStyleSheet("color: red; font-weight: bold;")
