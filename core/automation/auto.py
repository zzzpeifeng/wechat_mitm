import uiautomator2 as u2
from typing import Optional, List, Dict, Any
import time
import subprocess
import logging
import os


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
        self.connect()
    
    def _check_and_install_atx(self):
        """
        检查并安装ATX应用
        """
        try:
            # 检查ATX应用是否已安装
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", "com.github.uiautomator"], 
                capture_output=True, text=True
            )
            
            if "com.github.uiautomator" not in result.stdout:
                print("ATX应用未安装，正在自动安装...")
                
                # 初始化uiautomator2，这将自动安装ATX应用
                import tempfile
                import urllib.request
                import zipfile
                
                # 使用uiautomator2的初始化功能
                subprocess.run(["python", "-m", "uiautomator2", "init", "--serial", self.d.serial], 
                             capture_output=True)
                
                print("ATX应用安装完成")
            else:
                print("ATX应用已安装")
                
            # 确保ATX服务已启动
            self._ensure_atx_service()
                
        except Exception as e:
            print(f"检查或安装ATX应用时出错: {e}")
            # 尝试直接初始化
            try:
                subprocess.run(["python", "-m", "uiautomator2", "init"], check=True)
                print("ATX应用初始化完成")
            except Exception as e2:
                print(f"ATX应用初始化失败: {e2}")
    
    def _ensure_atx_service(self):
        """
        确保ATX服务正在运行
        """
        try:
            # 启动ATX服务
            self.d.service("com.github.uiautomator").start()
            time.sleep(2)  # 等待服务启动
        except Exception as e:
            print(f"启动ATX服务时出错: {e}")
    
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
            self.d.app_start(package_name)
            time.sleep(2)  # 等待应用启动
            
        except Exception as e:
            print(f"打开应用时出错: {e}")
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
            self.d.app_stop(package_name)
            time.sleep(1)  # 等待应用停止
            
        except Exception as e:
            print(f"杀死应用时出错: {e}")
            raise
    
    def click_element(self, selector: str, by: str = "text", timeout: int = 10):
        """
        点击指定元素
        
        Args:
            selector: 元素选择器值
            by: 选择器类型，可选值: "text", "resourceId", "className", "description"
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
            else:
                raise ValueError(f"不支持的选择器类型: {by}")
            
            if element.exists(timeout=timeout):
                element.click()
                print(f"成功点击元素: {selector}")
            else:
                print(f"未找到元素: {selector} (超时 {timeout} 秒)")
                
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
    
    def input_text(self, selector: str, text: str, by: str = "text", timeout: int = 10):
        """
        在指定元素中输入文本
        
        Args:
            selector: 元素选择器值
            text: 要输入的文本
            by: 选择器类型，可选值: "text", "resourceId", "className", "description"
            timeout: 等待元素出现的超时时间（秒）
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
            
            if element.exists(timeout=timeout):
                element.set_text(text)
                print(f"成功在元素 {selector} 中输入文本")
            else:
                print(f"未找到元素: {selector} (超时 {timeout} 秒)")
                
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
    
    def close(self):
        """
        关闭连接并清理资源
        """
        # uiautomator2通常不需要显式关闭连接
        print("已断开与设备的连接")
        self.d = None


# 使用示例
def main():
    try:
        # 检查是否有连接的设备
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
        connected_devices = [line.split("\t")[0] for line in lines if line.strip() and "\t" in line]
        
        if not connected_devices:
            print("未检测到连接的安卓设备。请连接设备并确保开发者选项已启用。")
            print("您也可以使用安卓模拟器（如Android Studio模拟器、BlueStacks等）")
            return
        
        print(f"检测到设备: {connected_devices}")
        
        # 连接到设备（如果连接多个设备，可以指定设备ID）
        automation = AndroidAutomation()
        
        # 搜索设备
        devices = automation.search_android_device()
        print(f"找到设备: {devices}")
        
        # 获取应用列表
        apps = automation.get_app_list()
        print(f"应用数量: {len(apps)}")
        
        # 获取当前应用
        current_app = automation.get_current_app()
        print(f"当前应用: {current_app}")
        
        # 示例：打开微信应用（如果设备上安装了的话）
        # automation.open_app("com.tencent.mm")
        
        # 示例：杀死微信应用
        # automation.kill_app("com.tencent.mm")
        
        # 示例：点击操作
        # automation.click_element("微信", by="text")
        
        # 示例：通过坐标点击
        # automation.click_coordinates(500, 1000)
        
        # 示例：通过属性点击元素
        # automation.click_element_by_attributes({"text": "微信", "className": "android.widget.TextView"})
        
        # 示例：输入文本
        # automation.input_text("输入框描述", "Hello World", by="description")
        
        # 示例：滑动操作
        # automation.swipe(500, 1500, 500, 500, 1.0)  # 向上滑动
        
        # 示例：截图
        # automation.screenshot("test_screenshot.png")
        
    except Exception as e:
        print(f"执行自动化操作时出错: {e}")
    finally:
        # 关闭连接
        if 'automation' in locals():
            automation.close()


if __name__ == "__main__":
    main()