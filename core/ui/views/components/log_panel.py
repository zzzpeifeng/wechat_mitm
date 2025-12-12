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
        layout.setSpacing(8)  # 减少间距
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_group = self._create_log_group()
        layout.addWidget(self.log_group)

    def _create_log_group(self) -> QGroupBox:
        """创建日志显示组"""
        group = QGroupBox("运行日志")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)  # 减少间距
        layout.setContentsMargins(12, 15, 12, 12)  # 减少边距

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(130)  # 减小最大高度
        self.log_text.setMinimumHeight(100)  # 减小最小高度
        self.log_text.setObjectName("logText")
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e4e7ed;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
                background-color: #fafafa;
                color: #606266;
            }
        """)
        layout.addWidget(self.log_text)

        # 底部按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clear_log_btn = QPushButton("清除日志")
        self.clear_log_btn.setObjectName("clearLogBtn")
        self.clear_log_btn.setFixedSize(80, 24)  # 减小按钮尺寸，符合规范
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #f4f4f5;
                border: 1px solid #dcdfe6;
                color: #606266;
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 4px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #ecf5ff;
                border-color: #b3d8ff;
            }
            
            QPushButton:pressed {
                background-color: #d9ecff;
                border-color: #409eff;
            }
        """)

        button_layout.addWidget(self.clear_log_btn)
        button_layout.addStretch(1)  # 添加弹性空间，使按钮靠左对齐
        
        layout.addLayout(button_layout)

        return group