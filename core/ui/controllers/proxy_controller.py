# core/proxy_controller.py
import subprocess
import platform
import os
import signal
import logging
from typing import Optional


class ProxyController:
    """
    代理控制器 - 管理mitmproxy服务和系统代理
    """

    def __init__(self):
        self.mitm_process: Optional[subprocess.Popen] = None
        self.logger = logging.getLogger(__name__)

    def start_mitmproxy(self, log_callback=None) -> bool:
        """
        启动mitmproxy服务

        Returns:
            bool: 启动是否成功
        """
        try:
            # 检查mitmdump是否可用
            import shutil
            if not shutil.which("mitmdump"):
                self.logger.error("mitmdump命令未找到，请确保mitmproxy已正确安装")
                return False

            # 构建mitmproxy命令

            # 使用绝对路径或确保路径正确
            handler_path = os.path.join(os.path.dirname(__file__), "..", "..", 'scripts', "mitmproxy_handler.py")
            handler_path = os.path.abspath(handler_path)

            if not os.path.exists(handler_path):
                self.logger.error(f"mitmproxy处理脚本未找到: {handler_path}")
                return False

            cmd = [
                'mitmdump',
                "-s", handler_path,
                "--listen-port", "8081",
                # "--ssl-insecure"  # 忽略SSL证书验证
            ]

            # CMD启动mitmproxy进程
            self.mitm_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )

            # 启动线程来读取输出
            import threading

            def read_output(pipe, prefix=""):
                try:
                    for line in iter(pipe.readline, ''):
                        # if log_callback:
                        #     log_callback(f"[{prefix}] {line.rstrip()}")
                        # else:
                        self.logger.info(f"[{prefix}] {line.rstrip()}")
                except Exception as e:
                    self.logger.error(f"读取mitmproxy输出时出错: {e}")
                finally:
                    pipe.close()

            threading.Thread(target=read_output,
                             args=(self.mitm_process.stdout, "OUT"),
                             daemon=True).start()
            threading.Thread(target=read_output,
                             args=(self.mitm_process.stderr, "ERR"),
                             daemon=True).start()

            # 给进程一点时间启动
            import time
            time.sleep(1)

            # 检查进程是否仍在运行
            if self.mitm_process.poll() is not None:
                # 进程已经退出，读取错误信息
                stdout, stderr = self.mitm_process.communicate()
                self.logger.error(f"mitmproxy启动失败: {stderr}")
                return False

            self.logger.info("mitmproxy服务启动成功")
            return True

        except Exception as e:
            self.logger.error(f"启动mitmproxy服务失败: {str(e)}")
            return False

    def stop_mitmproxy(self):
        """停止mitmproxy服务"""
        if self.mitm_process and self.mitm_process.poll() is None:
            try:
                # 在Windows上使用taskkill，其他平台使用terminate
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/F", "/PID", str(self.mitm_process.pid)],
                                   capture_output=True)
                else:
                    self.mitm_process.terminate()
                    self.mitm_process.wait(timeout=5)

                self.logger.info("mitmproxy服务已停止")
            except Exception as e:
                self.logger.error(f"停止mitmproxy服务时出错: {str(e)}")

        self.mitm_process = None

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
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")

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
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.http", "host", "'127.0.0.1'"
            ], check=True, capture_output=True)

            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.http", "port", "8080"
            ], check=True, capture_output=True)

            # 设置HTTPS代理
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.https", "host", "'127.0.0.1'"
            ], check=True, capture_output=True)

            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy.https", "port", "8080"
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
            subprocess.run([
                "gsettings", "set", "org.gnome.system.proxy", "mode", "'none'"
            ], check=True, capture_output=True)

            self.logger.info("Linux全局代理已禁用")

        except Exception as e:
            self.logger.error(f"禁用Linux代理时出错: {str(e)}")
