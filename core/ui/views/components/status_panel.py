# ui/views/components/status_panel.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel
)
from PyQt5.QtCore import Qt


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
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # 服务状态组
        self.service_group = self._create_service_status_group()
        layout.addWidget(self.service_group, 1)

        # 数据统计组
        self.stats_group = self._create_stats_group()
        layout.addWidget(self.stats_group, 1)

    def _create_service_status_group(self) -> QGroupBox:
        """创建服务状态组"""
        group = QGroupBox("服务状态")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 20, 10, 15)

        self.mitm_status_label = QLabel("青鸟监控: 未运行")
        self.mitm_status_label.setObjectName("mitmStatusLabel")
        self.mitm_status_label.setStyleSheet("""
            color: #f56c6c;
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)
        layout.addWidget(self.mitm_status_label)

        self.proxy_status_label = QLabel("全局代理: 未启用")
        self.proxy_status_label.setObjectName("proxyStatusLabel")
        self.proxy_status_label.setStyleSheet("""
            color: #f56c6c;
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)
        layout.addWidget(self.proxy_status_label)

        self.db_status_label = QLabel("数据库: 未连接")
        self.db_status_label.setObjectName("dbStatusLabel")
        self.db_status_label.setStyleSheet("""
            color: #f56c6c;
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)
        layout.addWidget(self.db_status_label)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def _create_stats_group(self) -> QGroupBox:
        """创建数据统计组"""
        group = QGroupBox("数据统计")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 20, 10, 15)

        self.collected_count_label = QLabel("已收集数据: 0 条")
        self.collected_count_label.setObjectName("collectedCountLabel")
        self.collected_count_label.setStyleSheet("""
            color: #606266;
            font-size: 14px;
            padding: 3px 0;
        """)
        layout.addWidget(self.collected_count_label)

        self.last_update_label = QLabel("最后更新: --")
        self.last_update_label.setObjectName("lastUpdateLabel")
        self.last_update_label.setStyleSheet("""
            color: #606266;
            font-size: 14px;
            padding: 3px 0;
        """)
        layout.addWidget(self.last_update_label)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def update_mitm_status(self, running: bool):
        """更新MitmProxy状态显示"""
        status_text = "运行中" if running else "未运行"
        color = "#67c23a" if running else "#f56c6c"  # 绿色表示运行中，红色表示未运行
        self.mitm_status_label.setText(f"青鸟监控: {status_text}")
        self.mitm_status_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)

    def update_proxy_status(self, enabled: bool):
        """更新代理状态显示"""
        status_text = "已启用" if enabled else "未启用"
        color = "#67c23a" if enabled else "#f56c6c"  # 绿色表示已启用，红色表示未启用
        self.proxy_status_label.setText(f"全局代理: {status_text}")
        self.proxy_status_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)

    def update_db_status(self, connected: bool):
        """更新数据库状态显示"""
        status_text = "已连接" if connected else "未连接"
        color = "#67c23a" if connected else "#f56c6c"  # 绿色表示已连接，红色表示未连接
        self.db_status_label.setText(f"数据库: {status_text}")
        self.db_status_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 14px;
            padding: 3px 0;
        """)