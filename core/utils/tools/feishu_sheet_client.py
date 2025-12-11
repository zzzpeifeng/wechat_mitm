import time
import requests
import json
from config.settings import FEISHUConfig


class FeishuSheetClient:
    def __init__(self, tenant_access_token=None):
        self.tenant_access_token = tenant_access_token
        self.token_expire_time = 0
        if tenant_access_token is None:
            self._refresh_tenant_access_token()
        self.base_url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets"

    def _is_token_expired(self):
        """检查token是否即将过期（提前10分钟刷新）"""
        return time.time() > self.token_expire_time - 600  # 提前10分钟刷新

    def _refresh_tenant_access_token(self):
        """获取或刷新租户访问令牌"""
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
            post_data = {
                "app_id": FEISHUConfig.FEISHU_APP_ID,
                "app_secret": FEISHUConfig.FEISHU_APP_SECRET
            }
            response = requests.post(url, json=post_data)
            response.raise_for_status()
            result = response.json()
            print(f"获取 token 的响应: {result}")  # 调试信息
            if "tenant_access_token" in result and "expire" in result:
                self.tenant_access_token = result["tenant_access_token"]
                # 设置过期时间（当前时间 + 有效期 - 1分钟安全缓冲）
                self.token_expire_time = time.time() + result["expire"] - 60
                return self.tenant_access_token
            else:
                print(f"响应中缺少 tenant_access_token 或 expire 字段: {result}")
                return None
        except Exception as e:
            print(f"获取 tenant_access_token 失败: {e}")
            return None

    def _ensure_valid_token(self):
        """确保token有效，如果即将过期则刷新"""
        if self.tenant_access_token is None or self._is_token_expired():
            return self._refresh_tenant_access_token()
        return self.tenant_access_token

    @staticmethod
    def extract_sheet_info_from_url(sheet_url: str) -> dict:
        """
        从飞书表格URL中提取spreadsheet_token和sheet_id
        
        Args:
            sheet_url (str): 飞书表格的URL
            
        Returns:
            dict: 包含spreadsheet_token和sheet_id的字典
        """
        try:
            from urllib.parse import urlparse, parse_qs
            # 解析URL
            parsed_url = urlparse(sheet_url)

            # 提取spreadsheet_token（路径中的sht开头部分）
            path_parts = parsed_url.path.split('/')
            spreadsheet_token = None
            for part in path_parts:
                if part.startswith('sht'):
                    spreadsheet_token = part
                    break

            # 提取sheet_id（查询参数中的sheet）
            query_params = parse_qs(parsed_url.query)
            sheet_id = query_params.get('sheet', [None])[0]

            return {
                "spreadsheet_token": spreadsheet_token,
                "sheet_id": sheet_id
            }
        except Exception as e:
            print(f"从URL提取表格信息失败: {e}")
            return {
                "spreadsheet_token": None,
                "sheet_id": None
            }

    def _get_headers(self):
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.tenant_access_token}"
        }

    def read_sheet_data(self, spreadsheet_token: str, sheet_id: str, range_str: str = None) -> dict:
        """
        读取飞书文档中电子表格的数据
        
        Args:
            spreadsheet_token (str): 表格token，从文档URL中获取
            sheet_id (str): 工作表ID，从文档URL中获取（sheet=后面的参数）
            range_str (str, optional): 数据范围，例如 "A1:B10"，如果不提供则读取整个工作表
            
        Returns:
            dict: 读取结果，包含 success 状态和数据或错误信息
        """
        try:
            # 确保 token 有效
            if not self._ensure_valid_token():
                return {
                    "success": False,
                    "error_msg": "无法获取有效的 tenant_access_token"
                }

            # 构造请求URL
            if range_str:
                url = f"{self.base_url}/{spreadsheet_token}/values/{sheet_id}!{range_str}"
            else:
                url = f"{self.base_url}/{spreadsheet_token}/values/{sheet_id}"

            print(f"请求URL: {url}")  # 调试信息

            headers = self._get_headers()

            # 发送GET请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 检查响应内容
            if not response.content:
                print(f"响应内容为空")
                return {
                    "success": False,
                    "error_msg": "响应内容为空"
                }
                
            result = response.json()

            if result.get("code") == 0:
                print(f"成功读取表格数据")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "msg": "读取成功"
                }
            else:
                print(f"读取表格数据失败，错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return {
                    "success": False,
                    "error_code": result.get("code"),
                    "error_msg": result.get("msg")
                }

        except requests.exceptions.HTTPError as e:
            print(f"读取表格数据时HTTP错误: {e}")
            if e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            else:
                print("无响应内容")
            return {
                "success": False,
                "error_msg": f"HTTP错误: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            print(f"读取表格数据时请求异常: {e}")
            return {
                "success": False,
                "error_msg": f"请求异常: {str(e)}"
            }
        except Exception as e:
            print(f"读取表格数据时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def write_sheet_data(self, spreadsheet_token: str, sheet_id: str, range_str: str, values: list) -> dict:
        """
        向飞书文档中的电子表格写入数据
        
        Args:
            spreadsheet_token (str): 表格token，从文档URL中获取
            sheet_id (str): 工作表ID，从文档URL中获取（sheet=后面的参数）
            range_str (str): 数据范围，例如 "A1:B10"
            values (list): 要写入的数据，二维数组格式 [[row1_col1, row1_col2], [row2_col1, row2_col2]]
            
        Returns:
            dict: 写入结果，包含 success 状态和数据或错误信息
        """
        try:
            # 确保 token 有效
            if not self._ensure_valid_token():
                return {
                    "success": False,
                    "error_msg": "无法获取有效的 tenant_access_token"
                }

            # 构造请求URL
            url = f"{self.base_url}/{spreadsheet_token}/values"

            headers = self._get_headers()

            # 构造请求体
            post_data = {
                "valueRange": {
                    "range": f"{sheet_id}!{range_str}",
                    "values": values
                }
            }

            print(f"写入请求URL: {url}")  # 调试信息
            print(f"写入请求数据: {post_data}")  # 调试信息

            # 发送PUT请求
            response = requests.put(url, headers=headers, data=json.dumps(post_data))
            response.raise_for_status()
            
            # 检查响应内容
            if not response.content:
                print(f"响应内容为空")
                return {
                    "success": False,
                    "error_msg": "响应内容为空"
                }
                
            result = response.json()

            if result.get("code") == 0:
                print(f"成功写入表格数据")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "msg": "写入成功"
                }
            else:
                print(f"写入表格数据失败，错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return {
                    "success": False,
                    "error_code": result.get("code"),
                    "error_msg": result.get("msg")
                }

        except requests.exceptions.HTTPError as e:
            print(f"写入表格数据时HTTP错误: {e}")
            if e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            else:
                print("无响应内容")
            return {
                "success": False,
                "error_msg": f"HTTP错误: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            print(f"写入表格数据时请求异常: {e}")
            return {
                "success": False,
                "error_msg": f"请求异常: {str(e)}"
            }
        except Exception as e:
            print(f"写入表格数据时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def append_sheet_data(self, spreadsheet_token: str, sheet_id: str, values: list) -> dict:
        """
        向飞书文档中的电子表格追加数据
        
        Args:
            spreadsheet_token (str): 表格token，从文档URL中获取
            sheet_id (str): 工作表ID，从文档URL中获取（sheet=后面的参数）
            values (list): 要追加的数据，二维数组格式 [[row1_col1, row1_col2], [row2_col1, row2_col2]]
            
        Returns:
            dict: 追加结果，包含 success 状态和数据或错误信息
        """
        try:
            # 确保 token 有效
            if not self._ensure_valid_token():
                return {
                    "success": False,
                    "error_msg": "无法获取有效的 tenant_access_token"
                }

            # 构造请求URL (根据您提供的正确格式进行修正)
            url = f"{self.base_url}/{spreadsheet_token}/values_append"

            headers = self._get_headers()

            # 构造请求体 (根据您提供的正确格式进行修正)
            post_data = {
                "valueRange": {
                    "range": sheet_id,
                    "values": values
                }
            }

            print(f"追加请求URL: {url}")  # 调试信息
            print(f"追加请求数据: {post_data}")  # 调试信息

            # 发送POST请求
            response = requests.post(url, headers=headers, data=json.dumps(post_data))
            response.raise_for_status()
            
            # 检查响应内容
            if not response.content:
                print(f"响应内容为空")
                return {
                    "success": False,
                    "error_msg": "响应内容为空"
                }
                
            result = response.json()

            if result.get("code") == 0:
                print(f"成功追加表格数据")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "msg": "追加成功"
                }
            else:
                print(f"追加表格数据失败，错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return {
                    "success": False,
                    "error_code": result.get("code"),
                    "error_msg": result.get("msg")
                }

        except requests.exceptions.HTTPError as e:
            print(f"追加表格数据时HTTP错误: {e}")
            if e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            else:
                print("无响应内容")
            return {
                "success": False,
                "error_msg": f"HTTP错误: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            print(f"追加表格数据时请求异常: {e}")
            return {
                "success": False,
                "error_msg": f"请求异常: {str(e)}"
            }
        except Exception as e:
            print(f"追加表格数据时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def get_sheet_metadata(self, spreadsheet_token: str) -> dict:
        """
        获取飞书文档中电子表格的元数据信息，包括所有工作表信息
        
        Args:
            spreadsheet_token (str): 表格token，从文档URL中获取
            
        Returns:
            dict: 元数据信息，包含 success 状态和数据或错误信息
        """
        try:
            # 确保 token 有效
            if not self._ensure_valid_token():
                return {
                    "success": False,
                    "error_msg": "无法获取有效的 tenant_access_token"
                }

            # 构造请求URL
            url = f"{self.base_url}/{spreadsheet_token}/sheets"

            headers = self._get_headers()

            print(f"获取元数据请求URL: {url}")  # 调试信息

            # 发送GET请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 检查响应内容
            if not response.content:
                print(f"响应内容为空")
                return {
                    "success": False,
                    "error_msg": "响应内容为空"
                }
                
            result = response.json()

            if result.get("code") == 0:
                print(f"成功获取表格元数据")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "sheets": result.get("data", {}).get("sheets", []),
                    "msg": "获取成功"
                }
            else:
                print(f"获取表格元数据失败，错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return {
                    "success": False,
                    "error_code": result.get("code"),
                    "error_msg": result.get("msg")
                }

        except requests.exceptions.HTTPError as e:
            print(f"获取表格元数据时HTTP错误: {e}")
            if e.response is not None:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            else:
                print("无响应内容")
            return {
                "success": False,
                "error_msg": f"HTTP错误: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            print(f"获取表格元数据时请求异常: {e}")
            return {
                "success": False,
                "error_msg": f"请求异常: {str(e)}"
            }
        except Exception as e:
            print(f"获取表格元数据时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }


if __name__ == '__main__':
    # 使用示例
    client = FeishuSheetClient()

    # 示例：从URL提取信息
    # url = "https://example.feishu.cn/sheets/shtcnxxxxxxxxxxxxxxx?sheet=402cb1"
    # sheet_info = client.extract_sheet_info_from_url(url)
    # print(sheet_info)  # {'spreadsheet_token': 'shtcnxxxxxxxxxxxxxxx', 'sheet_id': '402cb1'}

    # 示例：读取数据
    result = client.read_sheet_data("LkgdwebJHi5yOUkgOPAc2fnonFb", "9a4941", "A1:B10")
    print(result)
    
    # 示例：写入数据
    # data = [["姓名", "年龄"], ["张三", 25], ["李四", 30]]
    # result = client.write_sheet_data("shtcnxxxxxxxxxxxxxxx", "sheet1", "A1:B3", data)

    # 示例：追加数据
    data = [["1", "测试店铺1","测试门店1",'在线坐席数','空闲坐席数','总坐席数','记录时间','其他数据001','备注001'],
            ["2", "测试店铺2","测试门店2",'在线坐席数','空闲坐席数','总坐席数','记录时间','其他数据002','备注002']]
    result = client.append_sheet_data("LkgdwebJHi5yOUkgOPAc2fnonFb", "9a4941", data)

    # 示例：获取元数据
    # result = client.get_sheet_metadata("shtcnxxxxxxxxxxxxxxx")

    pass