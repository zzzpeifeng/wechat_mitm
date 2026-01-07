import uiautomator2 as u2
from typing import Optional, List, Dict, Any
import time
import subprocess
import os
import cv2
import numpy as np


class AndroidAutomation:
    """
    使用uiautomator2操作安卓设备的自动化类
    """

    def __init__(self, device_id: Optional[str] = None):
        """
        初始化安卓自动化类

        Args:
            device_id: 设备ID，如果为None则连接到默认设备（USB连接的第一个设备或通过WiFi连接的设备）
        """
        self.device_id = device_id
        self.d = None
        self.adb_kill_start_shell()
        self.connect()

    def _check_and_install_atx(self):
        """
        检查并安装ATX应用
        """
        try:
            print("正在检查ATX应用是否已安装...")

            # 检查ATX应用是否已安装
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", "com.github.uiautomator"],
                capture_output=True, text=True
            )

            if "com.github.uiautomator" not in result.stdout:
                print("ATX应用未安装，正在自动安装...")

                # 直接使用uiautomator2的init命令安装ATX应用
                init_cmd = ["python", "-m", "uiautomator2", "init"]
                if self.device_id:
                    init_cmd.extend(["--serial", self.device_id])

                result = subprocess.run(init_cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print("ATX应用安装完成")
                else:
                    print(f"ATX应用安装可能失败: {result.stderr}")
                    # 尝试不带设备ID的初始化
                    subprocess.run(["python", "-m", "uiautomator2", "init"], capture_output=True)
            else:
                print("ATX应用已安装")

            # 确保ATX服务已启动
            self._ensure_atx_service()
            self.go_home()

        except Exception as e:
            print(f"检查或安装ATX应用时出错: {e}")
            # 尝试直接初始化
            try:
                init_cmd = ["python", "-m", "uiautomator2", "init"]
                if self.device_id:
                    init_cmd.extend(["--serial", self.device_id])
                subprocess.run(init_cmd, capture_output=True, text=True)
                print("ATX应用初始化完成")
            except Exception as e2:
                print(f"ATX应用初始化失败: {e2}")
                print("请手动运行 'python -m uiautomator2 init' 进行初始化")

    def _ensure_atx_service(self):
        """
        确保ATX服务正在运行
        """
        try:
            # 尝试启动ATX服务 - 注意：在较新版本的uiautomator2中，API可能有所不同
            if hasattr(self.d, 'service'):
                self.d.service("com.github.uiautomator").start()
            else:
                # 对于较新版本，可能需要使用其他方式启动服务
                subprocess.run([
                    "adb", "shell", "am", "start", "-n",
                    "com.github.uiautomator/.MainActivity"
                ], capture_output=True)

            time.sleep(2)  # 等待服务启动
            print("ATX服务已启动")
            self.go_home()
        except Exception as e:
            print(f"启动ATX服务时出错: {e}")
            # 尝试通过ADB启动服务
            try:
                subprocess.run([
                    "adb", "shell", "am", "start", "-n",
                    "com.github.uiautomator/.MainActivity"
                ], capture_output=True)
                time.sleep(3)
                print("通过ADB启动ATX应用")
            except Exception as e2:
                print(f"通过ADB启动ATX应用也失败: {e2}")

    def connect(self):
        """
        连接到安卓设备
        """
        try:
            if self.device_id:
                # 连接到指定设备（通过设备ID或IP地址）
                self.d = u2.connect(self.device_id)
            else:
                # 连接到默认设备
                self.d = u2.connect()

            if not self.d:
                raise Exception("无法连接到安卓设备")

            print(f"已连接到设备: {self.d.info['productName']} (序列号: {self.d.serial})")

            # 检查并安装ATX应用
            self._check_and_install_atx()

        except Exception as e:
            print(f"连接到安卓设备时出错: {e}")
            print("请确保:")
            print("1. 已连接安卓设备或启动了安卓模拟器")
            print("2. 已启用设备的开发者选项和USB调试")
            raise

    def search_android_device(self, device_name: Optional[str] = None) -> List[dict]:
        """
        搜索可用的安卓设备

        Args:
            device_name: 特定设备名称，如果为None则返回所有可用设备

        Returns:
            可用安卓设备列表
        """
        try:
            # 使用adb命令获取设备列表
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            devices = []
            for line in lines:
                if line.strip() and "\t" in line:
                    device_id, status = line.split("\t")
                    device_info = {
                        "id": device_id,
                        "status": status.strip()
                    }

                    # 尝试获取设备详细信息
                    try:
                        d = u2.connect(device_id)
                        device_info.update({
                            "model": d.info.get('productName', 'Unknown'),
                            "brand": d.info.get('brand', 'Unknown'),
                            "serial": d.serial
                        })
                        d.app_list()  # 测试连接
                    except:
                        device_info.update({
                            "model": "Unknown",
                            "brand": "Unknown",
                            "serial": device_id
                        })

                    if device_name is None or device_name.lower() in device_info["model"].lower():
                        devices.append(device_info)

            return devices
        except Exception as e:
            print(f"搜索安卓设备时出错: {e}")
            return []

    def open_app(self, package_name: str):
        """
        打开指定的应用

        Args:
            package_name: 应用包名
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在打开应用: {package_name}")

            # 首先检查应用是否安装
            if not self.d.app_info(package_name):
                print(f"应用未安装: {package_name}")
                # 尝试列出设备上的所有应用，看是否有类似包名的应用
                apps = self.d.app_list()
                similar_apps = [app for app in apps if package_name.lower() in app.lower()]
                if similar_apps:
                    print(f"找到相似包名的应用: {similar_apps}")
                else:
                    print(f"在设备上未找到应用: {package_name}")
                return False

            # 尝试启动应用
            self.d.app_start(package_name)
            time.sleep(3)  # 等待应用启动，增加等待时间

            # 检查应用是否成功启动
            current_app = self.d.app_current()
            if current_app.get('packageName') == package_name:
                print(f"成功打开应用: {package_name}")
                return True
            else:
                print(f"可能未成功打开应用: {package_name}, 当前应用是: {current_app.get('packageName')}")
                return False

        except Exception as e:
            print(f"打开应用时出错: {e}")
            # 检查应用是否存在于设备上
            try:
                apps = self.d.app_list()
                if package_name not in apps:
                    print(f"应用 {package_name} 未安装在设备上")
                else:
                    print(f"应用 {package_name} 已安装，但启动失败")
            except:
                pass  # 如果无法获取应用列表，则忽略此步骤
            raise

    def kill_app(self, package_name: str):
        """
        杀死指定的应用

        Args:
            package_name: 应用包名
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在杀死应用: {package_name}")

            # 检查应用是否正在运行
            current_app = self.d.app_current()
            if current_app.get('packageName') == package_name:
                self.d.app_stop(package_name)
                time.sleep(1)  # 等待应用停止
                print(f"成功停止应用: {package_name}")
                return True
            else:
                # 即使应用不是前台应用，也尝试停止它
                self.d.app_stop(package_name)
                time.sleep(1)
                print(f"已发送停止应用命令: {package_name}")
                return True

        except Exception as e:
            print(f"杀死应用时出错: {e}")
            raise

    def force_kill_app(self, package_name: str) -> bool:
        """
        强制杀死指定的应用（使用ADB命令强制停止）

        Args:
            package_name: 应用包名

        Returns:
            bool: 是否成功执行操作
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在强制杀死应用: {package_name}")

            # 使用ADB命令强制停止应用
            if self.device_id:
                cmd = ["adb", "-s", self.device_id, "shell", "am", "force-stop", package_name]
            else:
                cmd = ["adb", "shell", "am", "force-stop", package_name]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"成功强制停止应用: {package_name}")
                return True
            else:
                print(f"强制停止应用失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"强制杀死应用时出错: {e}")
            return False

    def is_app_installed(self, package_name: str) -> bool:
        """
        检查应用是否已安装

        Args:
            package_name: 应用包名

        Returns:
            bool: 应用是否已安装
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            return self.d.app_info(package_name) is not None
        except Exception as e:
            print(f"检查应用安装状态时出错: {e}")
            return False

    def is_app_running(self, package_name: str) -> bool:
        """
        检查应用是否正在运行

        Args:
            package_name: 应用包名

        Returns:
            bool: 应用是否正在运行
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            current_app = self.d.app_current()
            return current_app.get('packageName') == package_name
        except Exception as e:
            print(f"检查应用运行状态时出错: {e}")
            return False

    def open_app_by_name(self, app_name: str) -> bool:
        """
        根据应用名称打开应用

        Args:
            app_name: 应用名称（支持模糊匹配）

        Returns:
            bool: 是否成功打开应用
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在查找应用: {app_name}")

            self.d(text=app_name).click()
            # 判断是否已经打开app
            return True

        except Exception as e:
            print(f"根据应用名称打开应用时出错: {e}")
            return False

    def click_element(self, selector: str, by: str = "text", timeout: int = 10):
        """
        点击指定元素

        Args:
            selector: 元素选择器值
            by: 选择器类型，可选值: "text", "resourceId", "className", "description", "xpath", "textContains", "textStartsWith", "resourceIdMatches", "image"
            timeout: 等待元素出现的超时时间（秒）
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"点击元素: {selector} (通过{by}定位)")

            # 根据选择器类型定位元素
            if by == "text":
                element = self.d(text=selector)
            elif by == "resourceId":
                element = self.d(resourceId=selector)
            elif by == "className":
                element = self.d(className=selector)
            elif by == "description":
                element = self.d(description=selector)
            elif by == "xpath":
                element = self.d.xpath(selector)
            elif by == "textContains":
                element = self.d(textContains=selector)
            elif by == "textStartsWith":
                element = self.d(textStartsWith=selector)
            elif by == "resourceIdMatches":
                element = self.d(resourceIdMatches=selector)
            elif by == "image":
                # 使用图片进行匹配和点击
                return self.click_by_image(selector)
            else:
                raise ValueError(f"不支持的选择器类型: {by}")
            element.click()
        except Exception as e:
            print(f"点击元素时出错: {e}")
            raise

    def click_element_by_attributes(self, attributes: Dict[str, Any], timeout: int = 10):
        """
        根据多个属性定位并点击元素

        Args:
            attributes: 元素属性字典，例如 {"text": "按钮", "className": "android.widget.Button"}
            timeout: 等待元素出现的超时时间（秒）
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"根据属性点击元素: {attributes}")

            # 使用u2的Selector根据多个属性定位元素
            element = self.d(**attributes)

            if element.exists(timeout=timeout):
                element.click()
                print(f"成功点击元素: {attributes}")
            else:
                print(f"未找到元素: {attributes} (超时 {timeout} 秒)")

        except Exception as e:
            print(f"根据属性点击元素时出错: {e}")
            raise

    def element_exists(self, selector: str, by: str = "text") -> bool:
        """
        判断指定元素是否存在

        Args:
            selector: 元素选择器值
            by: 选择器类型，可选值: "text", "resourceId", "className", "description", "xpath", "textContains", "textStartsWith", "resourceIdMatches", "image"

        Returns:
            bool: 元素是否存在
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"检查元素是否存在: {selector} (通过{by}定位)")

            # 根据选择器类型定位元素
            if by == "text":
                element = self.d(text=selector)
            elif by == "resourceId":
                element = self.d(resourceId=selector)
            elif by == "className":
                element = self.d(className=selector)
            elif by == "description":
                element = self.d(description=selector)
            elif by == "xpath":
                element = self.d.xpath(selector)
            elif by == "textContains":
                element = self.d(textContains=selector)
            elif by == "textStartsWith":
                element = self.d(textStartsWith=selector)
            elif by == "resourceIdMatches":
                element = self.d(resourceIdMatches=selector)
            elif by == "image":
                # 使用图片进行匹配
                return self.find_image(selector, threshold=0.8) != []
            else:
                raise ValueError(f"不支持的选择器类型: {by}")

            exists = element.exists
            print(f"元素 '{selector}' 存在状态: {exists}")
            return exists

        except Exception as e:
            print(f"判断元素存在时出错: {e}")
            return False

    def adb_input_text(self, text: str) -> bool:
        """
        使用ADB在当前焦点输入文本

        Args:
            text: 要输入的文本内容

        Returns:
            bool: 是否输入成功
        """
        try:
            if not self.device_id:
                cmd = ["adb", "shell", "input", "text", text]
            else:
                cmd = ["adb", "-s", self.device_id, "shell", "input", "text", text]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"使用ADB成功输入文本: {text}")
                return True
            else:
                print(f"使用ADB输入文本失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"使用ADB输入文本时出错: {e}")
            return False

    def adb_send_keys(self, text: str) -> bool:
        """
        使用ADB发送按键，处理特殊字符

        Args:
            text: 要发送的文本内容

        Returns:
            bool: 是否发送成功
        """
        try:
            # 将空格转换为 %s，将其他特殊字符转义
            escaped_text = text.replace(' ', '%s')

            if not self.device_id:
                cmd = ["adb", "shell", "input", "text", escaped_text]
            else:
                cmd = ["adb", "-s", self.device_id, "shell", "input", "text", escaped_text]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"使用ADB成功发送按键: {text}")
                return True
            else:
                print(f"使用ADB发送按键失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"使用ADB发送按键时出错: {e}")
            return False

    def adb_kill_start_shell(self) -> bool:
        """
        执行adb kill-server && adb start-server && adb shell命令序列

        Returns:
            bool: 命令序列是否成功执行
        """
        try:
            print("正在执行: adb kill-server")
            result = subprocess.run(["adb", "kill-server"], capture_output=True, text=True)
            time.sleep(1)
            if result.returncode != 0:
                print(f"adb kill-server 命令可能失败: {result.stderr}")
            else:
                print("adb kill-server 执行成功")

            print("正在执行: adb start-server")
            result = subprocess.run(["adb", "start-server"], capture_output=True, text=True)
            time.sleep(1)
            if result.returncode != 0:
                print(f"adb start-server 命令失败: {result.stderr}")
                return False
            else:
                print("adb start-server 执行成功")

            print("正在执行: adb shell")
            # 由于adb shell是一个交互式命令，我们需要发送exit命令来退出
            import signal
            import threading

            # 创建一个进程来执行adb shell并立即退出
            result = subprocess.run(["adb", "shell", "echo", "test"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"adb shell 命令失败: {result.stderr}")
                return False
            else:
                print("adb shell 命令执行成功")

            print("adb kill-server && adb start-server && adb shell 命令序列执行完成")
            return True

        except Exception as e:
            print(f"执行adb命令序列时出错: {e}")
            return False

    def click_coordinates(self, x: int, y: int):
        """
        点击指定坐标

        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"点击坐标: ({x}, {y})")
            self.d.click(x, y)

        except Exception as e:
            print(f"点击坐标时出错: {e}")
            raise

    def input_text(self, selector: str, text: str, by: str = "text"):
        """
        在指定元素中输入文本

        Args:
            selector: 元素选择器值
            text: 要输入的文本
            by: 选择器类型，可选值: "text", "resourceId", "className", "description", "xpath"
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"在元素 {selector} 中输入文本: {text}")

            # 根据选择器类型定位元素
            if by == "text":
                element = self.d(text=selector)
            elif by == "resourceId":
                element = self.d(resourceId=selector)
            elif by == "className":
                element = self.d(className=selector)
            elif by == "description":
                element = self.d(description=selector)
            elif by == "xpath":
                element = self.d.xpath(selector)
            else:
                raise ValueError(f"不支持的选择器类型: {by}")

            if element.exists:
                try:
                    # 尝试使用uiautomator2的set_text方法
                    element.set_text(text)
                    print(f"成功在元素 {selector} 中输入文本")
                except Exception as input_error:
                    # 检查是否是输入法相关的错误
                    if "AdbKeyboard" in str(input_error) or "IME" in str(input_error):
                        print(f"检测到输入法错误: {input_error}")
                        print("尝试使用ADB命令输入文本...")

                        # 如果是输入法错误，使用ADB方法输入文本
                        success = self.adb_input_text(text)
                        if success:
                            print(f"使用ADB成功输入文本: {text}")
                        else:
                            print(f"使用ADB输入文本也失败了")
                            raise input_error
                    else:
                        # 如果不是输入法错误，直接抛出异常
                        raise input_error
            else:
                print(f"未找到元素: {selector}")

        except Exception as e:
            print(f"输入文本时出错: {e}")
            raise

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """
        滑动屏幕

        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 滑动持续时间(秒)
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"滑动: 从({start_x}, {start_y}) 到 ({end_x}, {end_y})")
            self.d.swipe(start_x, start_y, end_x, end_y, duration)

        except Exception as e:
            print(f"滑动屏幕时出错: {e}")
            raise

    def get_app_list(self) -> List[str]:
        """
        获取设备上安装的所有应用列表

        Returns:
            应用包名列表
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            return self.d.app_list()
        except Exception as e:
            print(f"获取应用列表时出错: {e}")
            return []

    def get_current_app(self) -> dict:
        """
        获取当前前台应用信息

        Returns:
            包含当前应用信息的字典
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            return self.d.app_current()
        except Exception as e:
            print(f"获取当前应用信息时出错: {e}")
            return {}

    def click_by_image(self, template_path: str, threshold: float = 0.8) -> bool:
        """
        根据图片模板在屏幕上查找并点击匹配的元素

        Args:
            template_path: 模板图片路径
            threshold: 匹配阈值，范围0-1，值越高要求匹配度越高

        Returns:
            bool: 是否找到并点击成功
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在根据图片模板查找并点击: {template_path}")

            # 获取当前屏幕截图
            screen_img = self.d.screenshot()

            # 将截图保存到临时文件以供OpenCV读取
            temp_screenshot_path = "temp_screenshot.png"
            self.d.screenshot(temp_screenshot_path)

            # 读取屏幕截图和模板图片
            screen = cv2.imread(temp_screenshot_path)
            template = cv2.imread(template_path)

            if screen is None or template is None:
                print("无法读取屏幕截图或模板图片")
                return False

            # 执行模板匹配
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

            # 获取匹配结果中的最大值和位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                # 计算匹配区域的中心坐标
                h, w = template.shape[:2]
                center_x = int(max_loc[0] + w // 2)
                center_y = int(max_loc[1] + h // 2)

                # 点击匹配区域的中心
                self.d.click(center_x, center_y)
                print(f"成功匹配并点击图片，相似度: {max_val:.3f}, 坐标: ({center_x}, {center_y})")

                # 删除临时文件
                if os.path.exists(temp_screenshot_path):
                    os.remove(temp_screenshot_path)

                return True
            else:
                print(f"未找到匹配的图片，最高相似度: {max_val:.3f}，阈值: {threshold}")

                # 删除临时文件
                if os.path.exists(temp_screenshot_path):
                    os.remove(temp_screenshot_path)

                return False

        except Exception as e:
            print(f"根据图片点击时出错: {e}")
            # 确保临时文件被清理
            temp_screenshot_path = "temp_screenshot.png"
            if os.path.exists(temp_screenshot_path):
                os.remove(temp_screenshot_path)
            raise

    def find_image(self, template_path: str, threshold: float = 0.8, multiple: bool = False) -> List[Dict[str, Any]]:
        """
        根据图片模板在屏幕上查找匹配的元素位置

        Args:
            template_path: 模板图片路径
            threshold: 匹配阈值，范围0-1，值越高要求匹配度越高
            multiple: 是否查找多个匹配项

        Returns:
            List[Dict]: 匹配结果列表，每个元素包含坐标和匹配度
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"正在根据图片模板查找: {template_path}")

            # 获取当前屏幕截图
            temp_screenshot_path = "temp_screenshot.png"
            self.d.screenshot(temp_screenshot_path)

            # 读取屏幕截图和模板图片
            screen = cv2.imread(temp_screenshot_path)
            template = cv2.imread(template_path)

            if screen is None or template is None:
                print("无法读取屏幕截图或模板图片")
                return []

            # 执行模板匹配
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

            # 获取匹配结果中满足阈值的位置
            locations = np.where(result >= threshold)

            matches = []
            h, w = template.shape[:2]

            if len(locations[0]) > 0:
                # 将匹配位置转换为坐标
                for pt in zip(*locations[::-1]):  # locations[::-1] 将y,x转换为x,y
                    center_x = int(pt[0] + w // 2)
                    center_y = int(pt[1] + h // 2)
                    match_val = float(result[pt[1], pt[0]])  # 获取该位置的匹配度
                    matches.append({
                        "x": center_x,
                        "y": center_y,
                        "match_value": match_val,
                        "top_left": (int(pt[0]), int(pt[1]))
                    })

                # 如果不需要多个匹配，只返回最佳匹配
                if not multiple and matches:
                    best_match = max(matches, key=lambda x: x["match_value"])
                    matches = [best_match]

                print(f"找到 {len(matches)} 个匹配项")
            else:
                print(f"未找到匹配的图片，阈值: {threshold}")

            # 删除临时文件
            if os.path.exists(temp_screenshot_path):
                os.remove(temp_screenshot_path)

            return matches

        except Exception as e:
            print(f"查找图片时出错: {e}")
            # 确保临时文件被清理
            temp_screenshot_path = "temp_screenshot.png"
            if os.path.exists(temp_screenshot_path):
                os.remove(temp_screenshot_path)
            return []

    def screenshot(self, filename: str = None) -> str:
        """
        截取屏幕截图

        Args:
            filename: 截图文件保存路径，如果为None则生成默认文件名

        Returns:
            截图文件路径
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            if filename is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            self.d.screenshot(filename)
            print(f"截图已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"截图时出错: {e}")
            return ""

    def press_key(self, key: str):
        """
        按下设备按键

        Args:
            key: 按键名称，如 'home', 'back', 'menu', 'volume_up', 'volume_down', 'power' 等
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print(f"按下按键: {key}")
            self.d.press(key)

        except Exception as e:
            print(f"按键操作时出错: {e}")
            raise

    def wait_for_idle(self, timeout: int = 10):
        """
        等待设备空闲

        Args:
            timeout: 超时时间（秒）
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            self.d.wait_idle(timeout=timeout)
            print("设备已空闲")

        except Exception as e:
            print(f"等待设备空闲时出错: {e}")
            raise

    def go_home(self):
        """
        返回桌面
        """
        try:
            if not self.d:
                raise Exception("设备未连接")

            print("返回桌面")
            self.d.press("home")

        except Exception as e:
            print(f"返回桌面时出错: {e}")
            raise

    def close(self):
        """
        关闭连接并清理资源
        """
        # uiautomator2通常不需要显式关闭连接
        print("已断开与设备的连接")
        self.d = None


def main():
    au = AndroidAutomation()


if __name__ == "__main__":
    main()
