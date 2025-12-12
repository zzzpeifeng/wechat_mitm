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
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # 数据收集控制组
        self.collect_group = self._create_collect_group()
        layout.addWidget(self.collect_group, 3)

        # 服务控制组
        self.service_group = self._create_service_group()
        layout.addWidget(self.service_group, 1)

    def _create_collect_group(self) -> QGroupBox:
        """创建数据收集控制组"""
        group = QGroupBox("数据收集控制")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # 域名输入区域
        domain_input_layout = QHBoxLayout()
        domain_input_layout.setSpacing(10)
        
        domain_label = QLabel("目标域名:")
        domain_label.setStyleSheet("font-weight: normal;")
        domain_input_layout.addWidget(domain_label)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("输入目标域名")
        self.domain_input.setObjectName("domainInput")
        domain_input_layout.addWidget(self.domain_input)

        self.add_domain_btn = QPushButton("添加")
        self.add_domain_btn.setObjectName("addDomainBtn")
        self.add_domain_btn.setFixedWidth(80)
        domain_input_layout.addWidget(self.add_domain_btn)
        layout.addLayout(domain_input_layout)

        # 域名列表表格
        self.domain_table = QTableWidget(0, 1)
        self.domain_table.setHorizontalHeaderLabels(["域名列表"])
        self.domain_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.domain_table.verticalHeader().setVisible(False)
        self.domain_table.setObjectName("domainTable")
        self.domain_table.setMinimumHeight(100)
        self.domain_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                gridline-color: #ebeef5;
                background-color: #ffffff;
            }
            
            QTableWidget::item {
                padding: 8px 5px;
                color: #606266;  /* 添加这行来设置字体颜色 */
            }
            
            QHeaderView::section {
                background-color: #f5f7fa;
                color: #909399;
                padding: 5px;
                font-weight: normal;
                border: none;
                border-bottom: 1px solid #dcdfe6;
            }
        """)
        layout.addWidget(self.domain_table)

        return group

    def _create_service_group(self) -> QGroupBox:
        """创建服务控制组"""
        group = QGroupBox("服务控制")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 15, 10)

        self.mitm_service_btn = QPushButton("启动青鸟监控")
        self.mitm_service_btn.setCheckable(True)
        self.mitm_service_btn.setObjectName("mitmServiceBtn")
        self.mitm_service_btn.setFixedSize(150, 100)
        layout.addWidget(self.mitm_service_btn)

        self.crawler_btn = QPushButton("启动青鸟爬虫")
        self.crawler_btn.setCheckable(True)
        self.crawler_btn.setObjectName("crawlerBtn")
        self.crawler_btn.setFixedSize(150, 100)
        layout.addWidget(self.crawler_btn)

        self.proxy_btn = QPushButton("启用全局代理")
        self.proxy_btn.setCheckable(True)
        self.proxy_btn.setObjectName("proxyBtn")
        self.proxy_btn.setFixedSize(150, 30)
        layout.addWidget(self.proxy_btn)

        # 添加弹性空间
        layout.addStretch(1)

        return group