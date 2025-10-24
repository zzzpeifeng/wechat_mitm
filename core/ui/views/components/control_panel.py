# ui/views/components/control_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QLineEdit, QLabel
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

        self.collect_checkbox = QCheckBox("启用数据收集")
        self.collect_checkbox.setObjectName("collectCheckbox")
        layout.addWidget(self.collect_checkbox)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("目标域名:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("输入目标域名，多个用逗号分隔")
        self.domain_input.setObjectName("domainInput")
        domain_layout.addWidget(self.domain_input)
        layout.addLayout(domain_layout)

        return group

    def _create_service_group(self) -> QGroupBox:
        """创建服务控制组"""
        group = QGroupBox("服务控制")
        layout = QVBoxLayout(group)

        self.mitm_service_btn = QPushButton("启动 MitmProxy 服务")
        self.mitm_service_btn.setCheckable(True)
        self.mitm_service_btn.setObjectName("mitmServiceBtn")
        layout.addWidget(self.mitm_service_btn)

        self.proxy_btn = QPushButton("启用全局代理")
        self.proxy_btn.setCheckable(True)
        self.proxy_btn.setObjectName("proxyBtn")
        layout.addWidget(self.proxy_btn)

        return group
