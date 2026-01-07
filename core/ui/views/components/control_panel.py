# ui/views/components/control_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QLineEdit, QLabel, QTableWidget, QHeaderView, QFrame, QComboBox
)
from PyQt5.QtCore import Qt


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
        layout.setSpacing(15)  # 减少间距
        layout.setContentsMargins(0, 0, 0, 0)

        # 数据收集控制组
        self.collect_group = self._create_collect_group()
        layout.addWidget(self.collect_group, 3)  # 保持3:1比例

        # 服务控制组
        self.service_group = self._create_service_group()
        layout.addWidget(self.service_group, 1)

    def _create_collect_group(self) -> QGroupBox:
        """创建数据收集控制组"""
        group = QGroupBox("数据收集控制")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)  # 减少间距
        layout.setContentsMargins(12, 15, 12, 12)  # 减少边距

        # 域名输入区域
        domain_input_layout = QHBoxLayout()
        domain_input_layout.setSpacing(8)  # 减少间距
        
        domain_label = QLabel("目标域名:")
        domain_label.setStyleSheet("font-weight: normal; font-size: 12px;")  # 减小字体
        domain_input_layout.addWidget(domain_label)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("输入目标域名，例如: example.com")
        self.domain_input.setObjectName("domainInput")
        self.domain_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
                background-color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 1px solid #409eff;
                outline: none;
            }
        """)
        domain_input_layout.addWidget(self.domain_input)

        self.add_domain_btn = QPushButton("添加")
        self.add_domain_btn.setObjectName("addDomainBtn")
        self.add_domain_btn.setFixedWidth(60)  # 减小宽度
        self.add_domain_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                border: none;
                color: white;
                padding: 6px 12px;
                font-size: 12px;
                border-radius: 4px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #66b1ff;
            }
            
            QPushButton:pressed {
                background-color: #3a8ee6;
            }
            
            QPushButton:disabled {
                background-color: #a0cfff;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        domain_input_layout.addWidget(self.add_domain_btn)
        layout.addLayout(domain_input_layout)

        # 域名列表表格
        self.domain_table = QTableWidget(0, 1)
        self.domain_table.setHorizontalHeaderLabels(["域名列表"])
        self.domain_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.domain_table.verticalHeader().setVisible(False)
        self.domain_table.setObjectName("domainTable")
        self.domain_table.setMinimumHeight(100)  # 减小高度
        self.domain_table.setAlternatingRowColors(True)
        self.domain_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e4e7ed;
                border-radius: 4px;
                gridline-color: #f5f7fa;
                background-color: #ffffff;
                selection-background-color: #ecf5ff;
                selection-color: #606266;
            }
            
            QTableWidget::item {
                padding: 6px 5px;
                color: #606266;
                border-bottom: 1px solid #f5f7fa;
            }
            
            QTableWidget::item:selected {
                background-color: #ecf5ff;
            }
            
            QHeaderView::section {
                background-color: #f5f7fa;
                color: #909399;
                padding: 6px 5px;
                font-weight: 500;
                border: none;
                border-bottom: 1px solid #e4e7ed;
                font-size: 12px;
            }
            
            QTableCornerButton::section {
                background: #f5f7fa;
                border: none;
            }
        """)
        layout.addWidget(self.domain_table)

        return group

    def _create_service_group(self) -> QGroupBox:
        """创建服务控制组"""
        group = QGroupBox("服务控制")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)  # 减少间距
        layout.setContentsMargins(12, 15, 12, 12)  # 减少边距

        # 创建按钮容器，使按钮居中对齐
        buttons_container = QVBoxLayout()
        buttons_container.setSpacing(10)  # 减少按钮间距，符合规范
        buttons_container.setAlignment(Qt.AlignCenter)
        
        self.mitm_service_btn = QPushButton("启动青鸟监控")
        self.mitm_service_btn.setCheckable(True)
        self.mitm_service_btn.setObjectName("mitmServiceBtn")
        self.mitm_service_btn.setFixedSize(140, 24)  # 固定尺寸，高度符合规范
        self.mitm_service_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                border: none;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 6px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #66b1ff;
            }
            
            QPushButton:pressed {
                background-color: #3a8ee6;
            }
            
            QPushButton:checked {
                background-color: #f56c6c;
            }
            
            QPushButton:checked:hover {
                background-color: #f78989;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        buttons_container.addWidget(self.mitm_service_btn)

        self.crawler_btn = QPushButton("启动青鸟爬虫")
        self.crawler_btn.setCheckable(True)
        self.crawler_btn.setObjectName("crawlerBtn")
        self.crawler_btn.setFixedSize(140, 24)  # 固定尺寸，高度符合规范
        self.crawler_btn.setStyleSheet("""
            QPushButton {
                background-color: #67c23a;
                border: none;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 6px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #85ce61;
            }
            
            QPushButton:pressed {
                background-color: #5daf34;
            }
            
            QPushButton:checked {
                background-color: #f56c6c;
            }
            
            QPushButton:checked:hover {
                background-color: #f78989;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        buttons_container.addWidget(self.crawler_btn)

        # 添加大巴掌爬虫按钮
        self.dbz_crawler_btn = QPushButton("大巴掌爬虫")
        self.dbz_crawler_btn.setCheckable(True)
        self.dbz_crawler_btn.setObjectName("dbzCrawlerBtn")
        self.dbz_crawler_btn.setFixedSize(140, 24)  # 固定尺寸，高度符合规范
        self.dbz_crawler_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6a23c;
                border: none;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 6px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #ebb563;
            }
            
            QPushButton:pressed {
                background-color: #cf9236;
            }
            
            QPushButton:checked {
                background-color: #f56c6c;
            }
            
            QPushButton:checked:hover {
                background-color: #f78989;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        buttons_container.addWidget(self.dbz_crawler_btn)

        self.proxy_btn = QPushButton("启用全局代理")
        self.proxy_btn.setCheckable(True)
        self.proxy_btn.setObjectName("proxyBtn")
        self.proxy_btn.setFixedSize(140, 24)  # 固定尺寸，高度符合规范
        self.proxy_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6a23c;
                border: none;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 4px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #ebb563;
            }
            
            QPushButton:pressed {
                background-color: #cf9236;
            }
            
            QPushButton:checked {
                background-color: #f56c6c;
            }
            
            QPushButton:checked:hover {
                background-color: #f78989;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        buttons_container.addWidget(self.proxy_btn)

        # 添加启动自动化按钮
        self.automation_btn = QPushButton("启动自动化")
        self.automation_btn.setCheckable(True)
        self.automation_btn.setObjectName("automationBtn")
        self.automation_btn.setFixedSize(140, 24)  # 固定尺寸，高度符合规范
        self.automation_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                border: none;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 6px;
                font-weight: 500;
                outline: none;
            }
            
            QPushButton:hover {
                background-color: #b06ab8;
            }
            
            QPushButton:pressed {
                background-color: #8a4da5;
            }
            
            QPushButton:checked {
                background-color: #f56c6c;
            }
            
            QPushButton:checked:hover {
                background-color: #f78989;
            }
            
            QPushButton:focus {
                outline: none;
            }
        """)
        buttons_container.addWidget(self.automation_btn)

        layout.addLayout(buttons_container)

        return group