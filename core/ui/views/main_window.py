# ui/views/main_window.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QLabel, QTextEdit, QGroupBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor



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
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.moveCursor(QTextCursor.End)


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

        # 数据收集控制组
        collect_group = QGroupBox("数据收集控制")
        collect_layout = QVBoxLayout(collect_group)

        self.collect_checkbox = QCheckBox("启用数据收集")
        self.collect_checkbox.setObjectName("collectCheckbox")
        collect_layout.addWidget(self.collect_checkbox)

        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("目标域名:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("输入目标域名，多个用逗号分隔")
        self.domain_input.setObjectName("domainInput")
        domain_layout.addWidget(self.domain_input)
        collect_layout.addLayout(domain_layout)

        # 服务控制组
        service_group = QGroupBox("服务控制")
        service_layout = QVBoxLayout(service_group)

        self.mitm_service_btn = QPushButton("启动 MitmProxy 服务")
        self.mitm_service_btn.setCheckable(True)
        self.mitm_service_btn.setObjectName("mitmServiceBtn")
        service_layout.addWidget(self.mitm_service_btn)

        self.proxy_btn = QPushButton("启用全局代理")
        self.proxy_btn.setCheckable(True)
        self.proxy_btn.setObjectName("proxyBtn")
        service_layout.addWidget(self.proxy_btn)

        control_layout.addWidget(collect_group)
        control_layout.addWidget(service_group)

        return control_layout

    def _create_status_area(self) -> QHBoxLayout:
        """创建状态显示区域"""
        status_layout = QHBoxLayout()

        # 服务状态组
        service_group = QGroupBox("服务状态")
        service_layout = QVBoxLayout(service_group)

        self.mitm_status_label = QLabel("MitmProxy: 未运行")
        self.mitm_status_label.setObjectName("mitmStatusLabel")
        service_layout.addWidget(self.mitm_status_label)

        self.proxy_status_label = QLabel("全局代理: 未启用")
        self.proxy_status_label.setObjectName("proxyStatusLabel")
        service_layout.addWidget(self.proxy_status_label)

        self.db_status_label = QLabel("数据库: 未连接")
        self.db_status_label.setObjectName("dbStatusLabel")
        service_layout.addWidget(self.db_status_label)

        # 数据统计组
        stats_group = QGroupBox("数据统计")
        stats_layout = QVBoxLayout(stats_group)

        self.collected_count_label = QLabel("已收集数据: 0 条")
        self.collected_count_label.setObjectName("collectedCountLabel")
        stats_layout.addWidget(self.collected_count_label)

        self.last_update_label = QLabel("最后更新: --")
        self.last_update_label.setObjectName("lastUpdateLabel")
        stats_layout.addWidget(self.last_update_label)

        status_layout.addWidget(service_group)
        status_layout.addWidget(stats_group)

        return status_layout

    def _create_log_area(self) -> QVBoxLayout:
        """创建日志显示区域"""
        log_layout = QVBoxLayout()

        log_group = QGroupBox("运行日志")
        log_group_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setObjectName("logText")
        log_group_layout.addWidget(self.log_text)

        self.clear_log_btn = QPushButton("清除日志")
        self.clear_log_btn.setObjectName("clearLogBtn")
        log_group_layout.addWidget(self.clear_log_btn)

        log_layout.addWidget(log_group)

        return log_layout

def main():
    """测试入口"""
    app = QApplication(sys.argv)
    window = MitmProxyMainView()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
