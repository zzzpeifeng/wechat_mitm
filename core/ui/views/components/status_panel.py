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
