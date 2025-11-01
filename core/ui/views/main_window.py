# ui/views/main_window.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QLabel, QTextEdit, QGroupBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor

from core.ui.views.components.control_panel import ControlPanel


class MitmProxyMainView(QMainWindow):
    """
    主窗口视图类 - 负责UI展示和布局
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面布局"""
        self.setWindowTitle("MitmProxy 控制面板")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 标题
        title_label = self._create_title_label()
        main_layout.addWidget(title_label)

        # 功能控制区域
        control_layout = self._create_control_area()
        main_layout.addLayout(control_layout)

        # 状态显示区域
        status_layout = self._create_status_area()
        main_layout.addLayout(status_layout)

        # 日志显示区域
        log_layout = self._create_log_area()
        main_layout.addLayout(log_layout)

    def log_message(self, message: str):
        """向日志区域添加消息"""
        self.log_panel.log_text.append(message)
        # 自动滚动到底部
        self.log_panel.log_text.moveCursor(QTextCursor.End)

    def _create_title_label(self) -> QLabel:
        """创建标题标签"""
        title_label = QLabel("MitmProxy 控制面板")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def _create_control_area(self) -> QHBoxLayout:
        """创建控制区域布局"""
        control_layout = QHBoxLayout()

        # 使用完整的 ControlPanel 替代手工创建的控件
        self.control_panel = ControlPanel()
        control_layout.addWidget(self.control_panel)

        return control_layout

    def _create_status_area(self) -> QHBoxLayout:
        """创建状态显示区域"""
        from core.ui.views.components.status_panel import StatusPanel

        status_layout = QHBoxLayout()

        # 使用 StatusPanel 组件替代手工创建的状态显示控件
        self.status_panel = StatusPanel()
        status_layout.addWidget(self.status_panel)

        return status_layout

    def _create_log_area(self) -> QVBoxLayout:
        """创建日志显示区域"""
        from core.ui.views.components.log_panel import LogPanel

        log_layout = QVBoxLayout()

        # 使用 LogPanel 组件替代手工创建的日志显示控件
        self.log_panel = LogPanel()
        log_layout.addWidget(self.log_panel)

        return log_layout

def main():
    """测试入口"""
    app = QApplication(sys.argv)
    window = MitmProxyMainView()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
