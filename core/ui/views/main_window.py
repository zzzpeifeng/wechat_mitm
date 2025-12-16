# ui/views/main_window.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QLabel, QTextEdit, QGroupBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPalette
import platform

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
        
        # 设置窗口大小 - 调整为更合适的默认尺寸
        self.setGeometry(100, 100, 1200, 750)
        # 设置窗口最小大小
        self.setMinimumSize(1000, 650)
        
        # 在 macOS 上启用原生窗口装饰
        if platform.system() == "Darwin":
            self.setWindowFlags(Qt.Window)
        
        # 设置整体样式
        self.setStyleSheet(self.get_stylesheet())

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)  # 减少间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 减少边距

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

    def get_stylesheet(self):
        """获取应用程序样式表"""
        return """
        QMainWindow {
            background-color: #f5f7fa;
        }
        
        /* 标题栏样式 */
        QMainWindow::title {
            background-color: #409eff;
            color: white;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel {
            color: #606266;
            font-size: 14px;
        }
        
        QPushButton {
            background-color: #409eff;
            border: none;
            color: white;
            padding: 9px 15px;
            font-size: 14px;
            border-radius: 4px;
            min-height: 30px;
        }
        
        QPushButton:hover {
            background-color: #66b1ff;
        }
        
        QPushButton:pressed {
            background-color: #3a8ee6;
        }
        
        QPushButton:disabled {
            background-color: #a0cfff;
            color: #ffffff;
        }
        
        QGroupBox {
            font-size: 14px;
            font-weight: 600;
            border: 1px solid #e4e7ed;
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 10px;
            padding-bottom: 10px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            color: #303133;
        }
        
        QLineEdit {
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            padding: 8px 10px;
            font-size: 14px;
            background-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #409eff;
        }
        
        QTextEdit {
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            padding: 10px;
            font-size: 13px;
            background-color: #ffffff;
            color: #606266;
        }
        
        QTableWidget {
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            gridline-color: #ebeef5;
            background-color: #ffffff;
            selection-background-color: #ecf5ff;
            selection-color: #606266;
        }
        
        QTableWidget::item {
            padding: 5px;
        }
        
        QHeaderView::section {
            background-color: #f5f7fa;
            color: #909399;
            padding: 8px;
            font-weight: normal;
            border: none;
            border-bottom: 1px solid #dcdfe6;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #f5f7fa;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #c0c4cc;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #a0a4ac;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #f5f7fa;
            height: 10px;
            margin: 0px 0px 0px 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #c0c4cc;
            border-radius: 5px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #a0a4ac;
        }
        """

    def _create_title_label(self) -> QLabel:
        """创建标题标签"""
        title_label = QLabel("MitmProxy 控制面板")
        title_font = QFont()
        title_font.setPointSize(18)  # 减小字体大小
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #303133;
            margin-bottom: 5px;
            padding: 10px;
            background-color: white;
            border-radius: 6px;
            border: 1px solid #e4e7ed;
            font-weight: 600;
        """)
        return title_label

    def _create_control_area(self) -> QHBoxLayout:
        """创建控制区域布局"""
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)  # 减少间距

        # 使用完整的 ControlPanel 替代手工创建的控件
        self.control_panel = ControlPanel()
        control_layout.addWidget(self.control_panel)

        return control_layout

    def _create_status_area(self) -> QHBoxLayout:
        """创建状态显示区域"""
        from core.ui.views.components.status_panel import StatusPanel

        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)  # 减少间距

        # 使用 StatusPanel 组件替代手工创建的状态显示控件
        self.status_panel = StatusPanel()
        status_layout.addWidget(self.status_panel)

        return status_layout

    def _create_log_area(self) -> QVBoxLayout:
        """创建日志显示区域"""
        from core.ui.views.components.log_panel import LogPanel

        log_layout = QVBoxLayout()
        log_layout.setSpacing(8)  # 减少间距

        # 使用 LogPanel 组件替代手工创建的日志显示控件
        self.log_panel = LogPanel()
        log_layout.addWidget(self.log_panel)

        return log_layout

def main():
    """测试入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序全局字体
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = MitmProxyMainView()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()