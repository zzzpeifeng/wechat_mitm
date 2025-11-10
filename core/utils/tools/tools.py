import re


def dict_to_cookie_string(cookie_dict):
    """
    将字典转换为 Cookie 字符串格式

    :param cookie_dict: 包含 cookie 键值对的字典
    :return: Cookie 格式字符串
    """
    cookie_items = []
    for key, value in cookie_dict.items():
        cookie_items.append(f"{key}={value}")
    return "; ".join(cookie_items)


def parse_cookie_header(cookie_header):
    """
    使用正则表达式解析cookie_header字符串，提取所有键值对

    :param cookie_header: cookie header字符串
    :return: 包含所有键值对的字典
    """
    # 正则表达式模式：匹配 key=value 格式，考虑逗号分隔
    pattern = r'([^,=]+)=([^,]*)(?=,|$)'

    # 查找所有匹配项
    matches = re.findall(pattern, cookie_header)

    # 构造键值对字典
    cookies = {}
    for key, value in matches:
        cookies[key.strip()] = value.strip()

    return cookies