# ui/views/components/status_panel.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


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
        layout.setSpacing(15)
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

        # 创建状态指示器容器
        mitm_container = QHBoxLayout()
        mitm_container.setSpacing(8)
        self.mitm_status_indicator = QLabel()
        self.mitm_status_indicator.setFixedSize(12, 12)
        self.mitm_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        mitm_container.addWidget(self.mitm_status_indicator)
        
        self.mitm_status_label = QLabel("青鸟监控: 未运行")
        self.mitm_status_label.setObjectName("mitmStatusLabel")
        self.mitm_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        mitm_container.addWidget(self.mitm_status_label)
        mitm_container.addStretch()
        layout.addLayout(mitm_container)

        # 全局代理状态
        proxy_container = QHBoxLayout()
        proxy_container.setSpacing(8)
        self.proxy_status_indicator = QLabel()
        self.proxy_status_indicator.setFixedSize(12, 12)
        self.proxy_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        proxy_container.addWidget(self.proxy_status_indicator)
        
        self.proxy_status_label = QLabel("全局代理: 未启用")
        self.proxy_status_label.setObjectName("proxyStatusLabel")
        self.proxy_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        proxy_container.addWidget(self.proxy_status_label)
        proxy_container.addStretch()
        layout.addLayout(proxy_container)

        # 数据库状态
        db_container = QHBoxLayout()
        db_container.setSpacing(8)
        self.db_status_indicator = QLabel()
        self.db_status_indicator.setFixedSize(12, 12)
        self.db_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        db_container.addWidget(self.db_status_indicator)
        
        self.db_status_label = QLabel("数据库: 未连接")
        self.db_status_label.setObjectName("dbStatusLabel")
        self.db_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        db_container.addWidget(self.db_status_label)
        db_container.addStretch()
        layout.addLayout(db_container)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def _create_stats_group(self) -> QGroupBox:
        """创建数据统计组"""
        group = QGroupBox("数据统计")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 20, 10, 15)

        # 数据收集统计
        collected_container = QHBoxLayout()
        collected_container.setSpacing(8)
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 16px;")
        collected_container.addWidget(icon_label)
        
        self.collected_count_label = QLabel("已收集数据: 0 条")
        self.collected_count_label.setObjectName("collectedCountLabel")
        self.collected_count_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        collected_container.addWidget(self.collected_count_label)
        collected_container.addStretch()
        layout.addLayout(collected_container)

        # 最后更新时间
        update_container = QHBoxLayout()
        update_container.setSpacing(8)
        icon_label2 = QLabel("🕒")
        icon_label2.setStyleSheet("font-size: 16px;")
        update_container.addWidget(icon_label2)
        
        self.last_update_label = QLabel("最后更新: --")
        self.last_update_label.setObjectName("lastUpdateLabel")
        self.last_update_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        update_container.addWidget(self.last_update_label)
        update_container.addStretch()
        layout.addLayout(update_container)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def update_mitm_status(self, running: bool):
        """更新MitmProxy状态显示"""
        status_text = "运行中" if running else "未运行"
        color = "#67c23a" if running else "#f56c6c"
        self.mitm_status_label.setText(f"青鸟监控: {status_text}")
        self.mitm_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

    def update_proxy_status(self, enabled: bool):
        """更新代理状态显示"""
        status_text = "已启用" if enabled else "未启用"
        color = "#67c23a" if enabled else "#f56c6c"
        self.proxy_status_label.setText(f"全局代理: {status_text}")
        self.proxy_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

    def update_db_status(self, connected: bool):
        """更新数据库状态显示"""
        status_text = "已连接" if connected else "未连接"
        color = "#67c23a" if connected else "#f56c6c"
        self.db_status_label.setText(f"数据库: {status_text}")
        self.db_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)