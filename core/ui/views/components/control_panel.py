# ui/views/components/control_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QLineEdit, QLabel, QTableWidget, QHeaderView
)


class ControlPanel(QWidget):
    """
    控制面板组件 - 包含数据收集和服务器控制功能
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化控制面板UI"""
        layout = QHBoxLayout(self)

        # 数据收集控制组
        self.collect_group = self._create_collect_group()
        layout.addWidget(self.collect_group)

        # 服务控制组
        self.service_group = self._create_service_group()
        layout.addWidget(self.service_group)

    def _create_collect_group(self) -> QGroupBox:
        """创建数据收集控制组"""
        group = QGroupBox("数据收集控制")
        layout = QVBoxLayout(group)

        # self.collect_checkbox = QCheckBox("启用数据收集")
        # self.collect_checkbox.setObjectName("collectCheckbox")
        # layout.addWidget(self.collect_checkbox)

        # 域名输入区域
        domain_input_layout = QHBoxLayout()
        domain_input_layout.addWidget(QLabel("目标域名:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("输入目标域名")
        self.domain_input.setObjectName("domainInput")
        domain_input_layout.addWidget(self.domain_input)

        self.add_domain_btn = QPushButton("添加")
        self.add_domain_btn.setObjectName("addDomainBtn")
        domain_input_layout.addWidget(self.add_domain_btn)
        layout.addLayout(domain_input_layout)

        # 域名列表表格
        self.domain_table = QTableWidget(0, 1)
        self.domain_table.setHorizontalHeaderLabels(["域名列表"])
        self.domain_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.domain_table.verticalHeader().setVisible(False)
        self.domain_table.setObjectName("domainTable")
        # 设置表格最小高度以确保可见
        self.domain_table.setMinimumHeight(150)
        layout.addWidget(self.domain_table)

        # 连接按钮点击事件（如果需要）
        # self.add_domain_btn.clicked.connect(self.add_domain_to_table)

        return group

    def _create_service_group(self) -> QGroupBox:
        """创建服务控制组"""
        group = QGroupBox("服务控制")
        layout = QVBoxLayout(group)

        self.mitm_service_btn = QPushButton("启动青鸟监控")
        self.mitm_service_btn.setCheckable(True)
        self.mitm_service_btn.setObjectName("mitmServiceBtn")
        layout.addWidget(self.mitm_service_btn)

        self.crawler_btn = QPushButton("启动青鸟爬虫")
        self.crawler_btn.setCheckable(True)
        self.crawler_btn.setObjectName("crawlerBtn")
        layout.addWidget(self.crawler_btn)

        self.proxy_btn = QPushButton("启用全局代理")
        self.proxy_btn.setCheckable(True)
        self.proxy_btn.setObjectName("proxyBtn")
        layout.addWidget(self.proxy_btn)

        return group
