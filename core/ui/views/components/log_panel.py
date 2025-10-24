# ui/views/components/log_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QPushButton
)

class LogPanel(QWidget):
    """
    日志面板组件 - 显示运行日志
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化日志面板UI"""
        layout = QVBoxLayout(self)

        self.log_group = self._create_log_group()
        layout.addWidget(self.log_group)

    def _create_log_group(self) -> QGroupBox:
        """创建日志显示组"""
        group = QGroupBox("运行日志")
        layout = QVBoxLayout(group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setObjectName("logText")
        layout.addWidget(self.log_text)

        self.clear_log_btn = QPushButton("清除日志")
        self.clear_log_btn.setObjectName("clearLogBtn")
        layout.addWidget(self.clear_log_btn)

        return group
