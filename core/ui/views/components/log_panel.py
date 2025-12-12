# ui/views/components/log_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt


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
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_group = self._create_log_group()
        layout.addWidget(self.log_group)

    def _create_log_group(self) -> QGroupBox:
        """创建日志显示组"""
        group = QGroupBox("运行日志")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        self.log_text.setMinimumHeight(100)
        self.log_text.setObjectName("logText")
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                padding: 1px;
                font-size: 10px;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                background-color: #ffffff;
                color: #606266;
            }
        """)
        layout.addWidget(self.log_text)

        # 底部按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.clear_log_btn = QPushButton("清除日志")
        self.clear_log_btn.setObjectName("clearLogBtn")
        # self.clear_log_btn.setFixedWidth(100)
        self.clear_log_btn.setFixedSize(930,20)

        button_layout.addWidget(self.clear_log_btn)
        button_layout.addStretch(2)  # 添加弹性空间，使按钮靠左对齐
        
        layout.addLayout(button_layout)

        return group