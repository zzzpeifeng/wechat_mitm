def enable_windows_proxy() -> bool:
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
        return True
    except Exception as e:
        return False


def disable_windows_proxy():
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
        return True
    except Exception as e:
        return False


def enable_macos_proxy() -> bool:
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

        return True
    except Exception as e:
        return False


def disable_macos_proxy():
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

        return True
    except Exception as e:
        return False


def enable_linux_proxy() -> bool:
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

        return True
    except Exception as e:
        return False


def disable_linux_proxy():
    """禁用Linux系统代理"""
    try:
        # 禁用代理
        import subprocess
        subprocess.run([
            "gsettings", "set", "org.gnome.system.proxy", "mode", "'none'"
        ], check=True, capture_output=True)

        return True
    except Exception as e:
        return False


def enable_global_proxy() -> bool:
    """启用系统全局代理"""
    import platform
    system = platform.system()
    
    if system == "Windows":
        return enable_windows_proxy()
    elif system == "Darwin":  # macOS
        return enable_macos_proxy()
    elif system == "Linux":
        return enable_linux_proxy()
    else:
        print(f"不支持的操作系统: {system}")
        return False


def disable_global_proxy():
    """禁用系统全局代理"""
    import platform
    system = platform.system()
    
    if system == "Windows":
        return disable_windows_proxy()
    elif system == "Darwin":  # macOS
        return disable_macos_proxy()
    elif system == "Linux":
        return disable_linux_proxy()
    else:
        print(f"不支持的操作系统: {system}")
        return False
