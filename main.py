# main_window.py
import sys
import logging
from PyQt5.QtWidgets import QApplication

from core.ui.views.main_window import MitmProxyMainView
from core.ui.controllers.main_controller import MainController

import sys
import os


def setup_logging():
    """设置日志配置"""
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        application_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))

    # 设置日志文件路径
    log_file_path = os.path.join(application_path, 'app.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )


def main():
    """主函数"""
    setup_logging()

    app = QApplication(sys.argv)

    # 创建视图
    view = MitmProxyMainView()

    # 创建控制器
    controller = MainController(view)

    # 显示窗口
    view.show()

    # 设置程序退出时的清理工作
    app.aboutToQuit.connect(controller.shutdown)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
