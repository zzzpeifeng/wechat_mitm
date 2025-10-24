# main_window.py
import sys
import logging
from PyQt5.QtWidgets import QApplication

from ui.views.main_window import MitmProxyMainView
from ui.controllers.main_controller import MainController

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
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
