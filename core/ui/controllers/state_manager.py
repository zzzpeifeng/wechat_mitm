"""
全局状态管理器 - 统一管理应用的各种状态
"""
from PyQt5.QtCore import QObject, pyqtSignal


class StateManager(QObject):
    """
    全局状态管理器 - 统一管理数据库状态、MITM启动状态和全局代理状态
    """
    # 状态变更信号
    db_status_changed = pyqtSignal(bool)  # 数据库状态变更
    mitm_status_changed = pyqtSignal(bool)  # MITM启动状态变更
    proxy_status_changed = pyqtSignal(bool)  # 全局代理状态变更

    def __init__(self):
        super().__init__()
        # 初始化状态
        self._db_connected = False
        self._mitm_running = False
        self._proxy_enabled = False

    @property
    def db_connected(self) -> bool:
        """数据库连接状态"""
        return self._db_connected

    @db_connected.setter
    def db_connected(self, value: bool):
        if self._db_connected != value:
            self._db_connected = value
            self.db_status_changed.emit(value)

    @property
    def mitm_running(self) -> bool:
        """MITM运行状态"""
        return self._mitm_running

    @mitm_running.setter
    def mitm_running(self, value: bool):
        if self._mitm_running != value:
            self._mitm_running = value
            self.mitm_status_changed.emit(value)

    @property
    def proxy_enabled(self) -> bool:
        """全局代理启用状态"""
        return self._proxy_enabled

    @proxy_enabled.setter
    def proxy_enabled(self, value: bool):
        if self._proxy_enabled != value:
            self._proxy_enabled = value
            self.proxy_status_changed.emit(value)

    def get_all_states(self) -> dict:
        """
        获取所有状态
        
        Returns:
            dict: 包含所有状态的字典
        """
        return {
            'db_connected': self._db_connected,
            'mitm_running': self._mitm_running,
            'proxy_enabled': self._proxy_enabled
        }

    def update_states(self, **kwargs):
        """
        批量更新状态
        
        Args:
            **kwargs: 状态键值对，如 db_connected=True, mitm_running=False 等
        """
        for key, value in kwargs.items():
            if key == 'db_connected':
                self.db_connected = value
            elif key == 'mitm_running':
                self.mitm_running = value
            elif key == 'proxy_enabled':
                self.proxy_enabled = value
