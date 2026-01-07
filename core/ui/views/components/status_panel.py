# ui/views/components/status_panel.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StatusPanel(QWidget):
    """
    状态面板组件 - 显示各种服务和数据状态
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化状态面板UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        # 服务状态组
        self.service_group = self._create_service_status_group()
        layout.addWidget(self.service_group, 1)

        # 定时任务组
        self.schedule_group = self._create_schedule_group()
        layout.addWidget(self.schedule_group, 1)

    def _create_service_status_group(self) -> QGroupBox:
        """创建服务状态组"""
        group = QGroupBox("服务状态")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 20, 10, 15)

        # 创建状态指示器容器
        mitm_container = QHBoxLayout()
        mitm_container.setSpacing(8)
        self.mitm_status_indicator = QLabel()
        self.mitm_status_indicator.setFixedSize(12, 12)
        self.mitm_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        mitm_container.addWidget(self.mitm_status_indicator)
        
        self.mitm_status_label = QLabel("青鸟监控: 未运行")
        self.mitm_status_label.setObjectName("mitmStatusLabel")
        self.mitm_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        mitm_container.addWidget(self.mitm_status_label)
        mitm_container.addStretch()
        layout.addLayout(mitm_container)

        # 全局代理状态
        proxy_container = QHBoxLayout()
        proxy_container.setSpacing(8)
        self.proxy_status_indicator = QLabel()
        self.proxy_status_indicator.setFixedSize(12, 12)
        self.proxy_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        proxy_container.addWidget(self.proxy_status_indicator)
        
        self.proxy_status_label = QLabel("全局代理: 未启用")
        self.proxy_status_label.setObjectName("proxyStatusLabel")
        self.proxy_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        proxy_container.addWidget(self.proxy_status_label)
        proxy_container.addStretch()
        layout.addLayout(proxy_container)

        # 数据库状态
        db_container = QHBoxLayout()
        db_container.setSpacing(8)
        self.db_status_indicator = QLabel()
        self.db_status_indicator.setFixedSize(12, 12)
        self.db_status_indicator.setStyleSheet("""
            background-color: #f56c6c;
            border-radius: 6px;
        """)
        db_container.addWidget(self.db_status_indicator)
        
        self.db_status_label = QLabel("数据库: 未连接")
        self.db_status_label.setObjectName("dbStatusLabel")
        self.db_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        db_container.addWidget(self.db_status_label)
        db_container.addStretch()
        layout.addLayout(db_container)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def _create_schedule_group(self) -> QGroupBox:
        """创建定时任务组"""
        group = QGroupBox("定时任务")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)  # 增加间距以提升视觉效果
        layout.setContentsMargins(12, 20, 12, 15)  # 增加边距

        # 任务状态显示
        status_container = QHBoxLayout()
        status_container.setSpacing(10)  # 统一间距
        status_icon = QLabel("⏱️")
        status_icon.setStyleSheet("""
            font-size: 18px;
            min-width: 20px;
            text-align: center;
        """)
        status_container.addWidget(status_icon)
        
        self.schedule_status_label = QLabel("状态: 未运行")
        self.schedule_status_label.setObjectName("scheduleStatusLabel")
        self.schedule_status_label.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        status_container.addWidget(self.schedule_status_label)
        status_container.addStretch()
        layout.addLayout(status_container)

        # 任务执行间隔设置
        interval_container = QHBoxLayout()
        interval_container.setSpacing(10)  # 统一间距
        interval_icon = QLabel("🕒")
        interval_icon.setStyleSheet("""
            font-size: 18px;
            min-width: 20px;
            text-align: center;
        """)
        interval_container.addWidget(interval_icon)
        
        interval_text = QLabel("执行间隔:")
        interval_text.setStyleSheet("""
            color: #606266;
            font-size: 13px;
            font-weight: 500;
            padding: 3px 0;
        """)
        interval_container.addWidget(interval_text)
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1", "2", "3", "4", "6", "8", "12"])
        self.interval_combo.setCurrentText("2")  # 默认2小时
        self.interval_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
                min-width: 65px;
                background-color: #ffffff;
                color: #606266;
                selection-background-color: #409eff;
            }
            
            QComboBox:focus {
                border: 1px solid #409eff;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-radius: 0 6px 6px 0;
            }
            
            QComboBox::down-arrow {
                image: none;
                width: 12px;
                height: 12px;
                margin-right: 5px;
            }
            
            QComboBox::down-arrow::after {
                content: '▼';
                font-size: 10px;
                color: #c0c4cc;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                background-color: #ffffff;
                selection-background-color: #ecf5ff;
                selection-color: #606266;
                padding: 2px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                color: #606266;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #ecf5ff;
                color: #409eff;
            }
        """)
        # 设置下拉框的最小高度以匹配文本高度
        self.interval_combo.setFixedHeight(32)
        interval_container.addWidget(self.interval_combo)
        
        interval_unit = QLabel("小时")
        interval_unit.setStyleSheet("""
            color: #909399;
            font-size: 13px;
            font-weight: normal;
            padding: 3px 0;
        """)
        interval_container.addWidget(interval_unit)
        interval_container.addStretch()
        layout.addLayout(interval_container)

        # 定时任务控制按钮
        button_container = QHBoxLayout()
        button_container.setSpacing(10)  # 统一间距
        
        self.schedule_task_btn = QPushButton("启动定时任务")
        self.schedule_task_btn.setCheckable(True)
        self.schedule_task_btn.setObjectName("scheduleTaskBtn")
        self.schedule_task_btn.setFixedHeight(32)  # 增加按钮高度以匹配下拉框
        self.schedule_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: none;
                color: white;
                padding: 6px 16px;
                font-size: 13px;
                border-radius: 6px;
                font-weight: 500;
                outline: none;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background-color: #5dade2;
            }
            
            QPushButton:pressed {
                background-color: #2980b9;
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
        button_container.addWidget(self.schedule_task_btn)
        button_container.addStretch()
        layout.addLayout(button_container)

        # 添加弹性空间
        layout.addStretch(1)

        return group

    def update_mitm_status(self, running: bool):
        """更新MitmProxy状态显示"""
        status_text = "运行中" if running else "未运行"
        color = "#67c23a" if running else "#f56c6c"
        self.mitm_status_label.setText(f"青鸟监控: {status_text}")
        self.mitm_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

    def update_proxy_status(self, enabled: bool):
        """更新代理状态显示"""
        status_text = "已启用" if enabled else "未启用"
        color = "#67c23a" if enabled else "#f56c6c"
        self.proxy_status_label.setText(f"全局代理: {status_text}")
        self.proxy_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

    def update_db_status(self, connected: bool):
        """更新数据库状态显示"""
        status_text = "已连接" if connected else "未连接"
        color = "#67c23a" if connected else "#f56c6c"
        self.db_status_label.setText(f"数据库: {status_text}")
        self.db_status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

    def update_schedule_status(self, running: bool):
        """更新定时任务状态显示"""
        status_text = "运行中" if running else "未运行"
        color = "#67c23a" if running else "#f56c6c"
        self.schedule_status_label.setText(f"状态: {status_text}")
        # 也可以在这里更新状态指示器颜色