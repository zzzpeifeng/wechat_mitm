# core/proxy_controller.py
import platform
import os
import sys
import asyncio
import threading
from typing import Optional
import logging

# 导入mitmproxy相关模块
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options

# 添加项目根目录到Python路径，以便可以导入自定义模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入拦截器模块
from core.scripts.mitmproxy_handler import interceptor


class ProxyController:
    """
    代理控制器 - 管理mitmproxy服务和系统代理
    """

    def __init__(self):
        self.master_thread: Optional[threading.Thread] = None
        self.master_instance: Optional[DumpMaster] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.logger = logging.getLogger(__name__)
        self.is_running = False

    def start_mitmproxy(self, log_callback=None) -> bool:
        """
        启动mitmproxy服务

        Returns:
            bool: 启动是否成功
        """
        try:
            if self.is_running:
                self.logger.info("mitmproxy服务已在运行中")
                return True
                
            # 在新线程中运行mitmproxy
            self.master_thread = threading.Thread(target=self._run_master, daemon=True)
            self.master_thread.start()
            
            # 等待一段时间确保master实例已创建
            import time
            time.sleep(1)
            
            self.is_running = True
            self.logger.info("mitmproxy服务启动成功")
            return True

        except Exception as e:
            self.logger.error(f"启动mitmproxy服务失败: {str(e)}")
            return False

    def _run_master(self):
        """在独立线程中运行mitmproxy主循环"""
        try:
            # 在新线程中创建事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 配置选项
            opts = Options(
                listen_port=8081,
                ssl_insecure=True  # 忽略SSL证书验证
            )
            
            # 创建DumpMaster实例，显式传递事件循环
            self.master_instance = DumpMaster(opts, loop=self.loop, with_termlog=False, with_dumper=False)
            
            # 添加拦截器addon到master
            self.master_instance.addons.add(interceptor)
            
            # 启动master
            self.logger.info("正在启动mitmproxy...")
            self.loop.run_until_complete(self.master_instance.run())
            
        except Exception as e:
            self.logger.error(f"运行mitmproxy时出错: {str(e)}")
        finally:
            # 确保清理所有资源
            try:
                # 取消所有未完成的任务
                if self.loop:
                    pending = asyncio.all_tasks(self.loop)
                    for task in pending:
                        task.cancel()
                    
                    # 运行一次事件循环以处理取消的任务
                    if pending:
                        self.loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
            except Exception as e:
                self.logger.warning(f"清理任务时出错: {str(e)}")
            
            self.is_running = False
            if self.loop:
                self.loop.close()
                self.loop = None

    def stop_mitmproxy(self):
        """停止mitmproxy服务"""
        try:
            if not self.is_running:
                self.logger.info("mitmproxy服务未在运行")
                return
                
            if self.master_instance:
                # 使用DumpMaster自带的shutdown方法
                self.master_instance.shutdown()
                
                # 等待一小段时间让正常的关闭流程完成
                import time
                time.sleep(0.5)
                
                # 如果事件循环仍在运行，则强制关闭
                if self.loop and self.loop.is_running():
                    # 取消所有待处理的任务
                    try:
                        pending_tasks = [task for task in asyncio.all_tasks(self.loop) if not task.done()]
                        for task in pending_tasks:
                            task.cancel()
                            
                        # 给一点时间让任务取消完成
                        if pending_tasks:
                            self.loop.call_soon_threadsafe(
                                lambda: asyncio.ensure_future(
                                    asyncio.gather(*pending_tasks, return_exceptions=True)
                                )
                            )
                    except Exception as e:
                        self.logger.warning(f"取消待处理任务时出错: {str(e)}")
                    
                    # 安全地停止事件循环
                    try:
                        self.loop.call_soon_threadsafe(self.loop.stop)
                    except Exception as e:
                        self.logger.warning(f"停止事件循环时出错: {str(e)}")
                
                # 等待线程结束
                if self.master_thread and self.master_thread.is_alive():
                    self.master_thread.join(timeout=5)
                    
                self.master_instance = None
                self.loop = None
                self.is_running = False
                self.logger.info("mitmproxy服务已停止")
                
        except Exception as e:
            self.logger.error(f"停止mitmproxy服务时出错: {str(e)}")

    def stop_mitmproxy_gracefully(self):
        """平滑退出mitmproxy服务"""
        self.stop_mitmproxy()

    def enable_global_proxy(self) -> bool:
        """
        启用系统全局代理

        Returns:
            bool: 启用是否成功
        """
        try:
            system = platform.system()

            if system == "Windows":
                return self._enable_windows_proxy()
            elif system == "Darwin":  # macOS
                return self._enable_macos_proxy()
            elif system == "Linux":
                return self._enable_linux_proxy()
            else:
                self.logger.error(f"不支持的操作系统: {system}")
                return False

        except Exception as e:
            self.logger.error(f"启用全局代理失败: {str(e)}")
            return False

    def disable_global_proxy(self):
        """禁用系统全局代理"""
        try:
            system = platform.system()

            if system == "Windows":
                self._disable_windows_proxy()
            elif system == "Darwin":  # macOS
                self._disable_macos_proxy()
            elif system == "Linux":
                self._disable_linux_proxy()

            self.logger.info("全局代理已禁用")

        except Exception as e:
            self.logger.error(f"禁用全局代理时出错: {str(e)}")

    def _enable_windows_proxy(self) -> bool:
        """启用Windows系统代理"""
        try:
            import winreg

            # 设置注册表项
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8081")

            # 刷新系统设置
            import ctypes
            internet_set_option = ctypes.windll.wininet.InternetSetOptionW
            internet_set_option(None, 37, None, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
            internet_set_option(None, 39, None, 0)  # INTERNET_OPTION_REFRESH

            self.logger.info("Windows全局代理已启用")
            return True

        except Exception as e:
            self.logger.error(f"启用Windows代理失败: {str(e)}")
            return False

    def _disable_windows_proxy(self):
        """禁用Windows系统代理"""
        try:
            import winreg

            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

            # 刷新系统设置
            import ctypes
            internet_set_option = ctypes.windll.wininet.InternetSetOptionW
            internet_set_option(None, 37, None, 0)
            internet_set_option(None, 39, None, 0)

            self.logger.info("Windows全局代理已禁用")

        except Exception as e:
            self.logger.error(f"禁用Windows代理时出错: {str(e)}")

    def _enable_macos_proxy(self) -> bool:
        """启用macOS系统代理"""
        try:
            # 设置HTTP代理
            import subprocess
            subprocess.run([
                "networksetup", "-setwebproxy", "Wi-Fi", "127.0.0.1", "8081"
            ], check=True, capture_output=True)

            # 设置HTTPS代理
            subprocess.run([
                "networksetup", "-setsecurewebproxy", "Wi-Fi", "127.0.0.1", "8081"
            ], check=True, capture_output=True)

            # 启用代理
            subprocess.run([
                "networksetup", "-setwebproxystate", "Wi-Fi", "on"
            ], check=True, capture_output=True)

            subprocess.run([
                "networksetup", "-setsecurewebproxystate", "Wi-Fi", "on"
            ], check=True, capture_output=True)

            self.logger.info("macOS全局代理已启用")
            return True

        except Exception as e:
            self.logger.error(f"启用macOS代理失败: {str(e)}")
            return False

    def _disable_macos_proxy(self):
        """禁用macOS系统代理"""
        try:
            # 禁用HTTP代理
            import subprocess
            subprocess.run([
                "networksetup", "-setwebproxystate", "Wi-Fi", "off"
            ], check=True, capture_output=True)

            # 禁用HTTPS代理
            subprocess.run([
                "networksetup", "-setsecurewebproxystate", "Wi-Fi", "off"
            ], check=True, capture_output=True)

            self.logger.info("macOS全局代理已禁用")

        except Exception as e:
            self.logger.error(f"禁用macOS代理时出错: {str(e)}")

    def _enable_linux_proxy(self) -> bool:
        """启用Linux系统代理（GNOME环境）"""
        try:
            # 设置HTTP代理
            import subprocess
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.http", "host", "'127.0.0.1'"
            ], check=True, capture_output=True)

            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.http", "port", "8081"
            ], check=True, capture_output=True)

            # 设置HTTPS代理
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.https", "host", "'127.0.0.1'"
            ], check=True, capture_output=True)

            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.https", "port", "8081"
            ], check=True, capture_output=True)

            # 启用代理
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy", "mode", "'manual'"
            ], check=True, capture_output=True)

            self.logger.info("Linux全局代理已启用")
            return True

        except Exception as e:
            self.logger.error(f"启用Linux代理失败: {str(e)}")
            return False

    def _disable_linux_proxy(self):
        """禁用Linux系统代理"""
        try:
            # 禁用代理
            import subprocess
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy", "mode", "'none'"
            ], check=True, capture_output=True)

            self.logger.info("Linux全局代理已禁用")

        except Exception as e:
            self.logger.error(f"禁用Linux代理时出错: {str(e)}")