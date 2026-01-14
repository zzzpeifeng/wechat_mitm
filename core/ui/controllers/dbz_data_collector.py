import requests
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from config.settings import FEISHUConfig
# 导入飞书表格客户端
from core.utils.tools.feishu_sheet_client import FeishuSheetClient
from core.utils.database import get_db_manager


@dataclass
class AuthConfig:
    """认证配置数据类"""
    open_id: str
    uniacid: int
    host: str


@dataclass
class APIResponse:
    """API响应数据类"""
    success: bool
    status_code: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    error_type: Optional[str] = None
    error_msg: Optional[str] = None


class DBZDataCollector:
    """电瓶鸟数据收集器类，用于与青鸟网咖系统API交互"""

    # 公共常量字段
    SOURCE = "7"
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI "
        "MicroMessenger/7.0.20.1781(0x6700143B) MacWechat/3.8.7(0x13080712) "
        "UnifiedPCMacWechat(0xf264151c) XWEB/17078 Flue"
    )
    ACCEPT_HEADER = "application/json, text/plain, */*"
    SEC_FETCH_SITE = "same-site"
    SEC_FETCH_MODE = "cors"
    SEC_FETCH_DEST = "empty"
    ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9"

    # 默认认证配置
    DEFAULT_AUTH_CONFIGS = [
        AuthConfig(
            open_id='oSzeE7BSc6BckJzhTk9D2oaN9Mvg',
            uniacid=30066,
            host='api.n1.xinjifei.com'
        ),
        AuthConfig(
            open_id='oNzHz6lMvW_N5N0h3R9zdoX9SiSg',
            uniacid=20031,
            host='api.wbzzsf.com.cn'
        )
    ]

    def __init__(self):
        """初始化数据收集器"""
        self.session = requests.Session()
        self.token = None
        # 初始化飞书表格客户端
        self.feishu_client = FeishuSheetClient()
        # 初始化数据库管理器
        self.db_manager = get_db_manager()

    def _get_headers(self, host: str, token: Optional[str] = None) -> Dict[str, str]:
        """
        获取带有认证信息的请求头
        
        Args:
            host (str): API主机地址
            token (str, optional): 认证token
            
        Returns:
            dict: 完整的请求头字典
        """
        return {
            "Host": host,
            "source": self.SOURCE,
            "User-Agent": self.USER_AGENT,
            "Accept": self.ACCEPT_HEADER,
            "Origin": f"https://{host}",
            "Sec-Fetch-Site": self.SEC_FETCH_SITE,
            "Sec-Fetch-Mode": self.SEC_FETCH_MODE,
            "Sec-Fetch-Dest": self.SEC_FETCH_DEST,
            "Referer": f"https://{host}/",
            "Accept-Language": self.ACCEPT_LANGUAGE,
            "token": token if token is not None else self.token or ""
        }

    def _make_request(self, method: str, url: str, headers: Dict[str, str],
                      data: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        通用HTTP请求方法
        
        Args:
            method (str): HTTP方法 ('GET', 'POST'等)
            url (str): 请求URL
            headers (dict): 请求头
            data (dict, optional): 请求数据
            
        Returns:
            APIResponse: 结构化的响应对象
        """
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, headers=headers, data=data, verify=False)
            else:
                response = self.session.get(url, headers=headers, params=data, verify=False)

            response.raise_for_status()

            return APIResponse(
                success=True,
                status_code=response.status_code,
                data=response.json() if response.content else {},
                headers=dict(response.headers)
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP请求失败: {e}")
            return APIResponse(
                success=False,
                error_type="RequestException",
                error_msg=str(e),
                status_code=getattr(e.response, 'status_code', None) if e.response else None
            )
        except ValueError as e:  # JSON解析错误
            logging.error(f"响应JSON解析失败: {e}")
            return APIResponse(
                success=False,
                error_type="ValueError",
                error_msg=f"JSON解析失败: {e}"
            )
        except Exception as e:
            logging.error(f"请求失败: {e}")
            return APIResponse(
                success=False,
                error_type="Exception",
                error_msg=str(e)
            )

    def mobile_login_with_headers(self, host: str, uniacid: int, openid: str) -> APIResponse:
        """
        使用完整Headers的移动端登录方法
        
        Args:
            host (str): API主机地址
            uniacid (int): 商户ID
            openid (str): 微信用户唯一标识
            
        Returns:
            APIResponse: 登录响应结果
        """
        url = f"https://{host}/netbar/login/mobile"

        # 定义请求数据
        data = {
            "loading": "false",
            "no_toast": "no_toast",
            "uniacid": uniacid,
            "openId": openid
        }

        # 发送POST请求，使用空token
        headers = self._get_headers(host, token="")
        response = self._make_request('POST', url, headers, data)

        if response.success and response.data:
            logging.info(f"移动端登录(带Headers)响应: {response.data}")
            # 更新实例token
            try:
                if 'data' in response.data and 'token' in response.data['data']:
                    self.token = response.data['data']['token']
            except (KeyError, TypeError):
                pass  # 忽略token提取失败的情况
        else:
            logging.error(f"移动端登录失败: {response.error_msg}")

        return response

    def get_machines(self, host: str, gid: int, account: str, token: Optional[str] = None) -> APIResponse:
        """
        获取指定网吧的机器座位信息
        
        Args:
            host (str): API主机地址
            gid (int): 网吧ID
            account (str): 账户ID/身份证号
            token (str, optional): 认证token，如果不提供则使用实例中的token
            
        Returns:
            APIResponse: 机器座位信息响应结果
        """
        url = f"https://{host}/netbar/mobile/reserveSeat/getMachines"

        # 定义请求数据
        data = {
            "gid": gid,
            "account": account
        }

        # 发送POST请求
        headers = self._get_headers(host, token)
        response = self._make_request('POST', url, headers, data)

        if response.success:
            logging.info(f"获取机器座位信息响应: {response.data}")
        else:
            logging.error(f"获取机器座位信息失败: {response.error_msg}")

        return response

    def get_remaining_limit(self, host: str, gid: int, account: str, token: Optional[str] = None) -> APIResponse:
        """
        获取指定网吧的剩余限制信息（在线机器数和空闲机器数）
        
        Args:
            host (str): API主机地址
            gid (int): 网吧ID
            account (str): 账户ID/身份证号
            token (str, optional): 认证token，如果不提供则使用实例中的token
            
        Returns:
            APIResponse: 剩余限制信息响应结果
        """
        url = f"https://{host}/netbar/mobile/reserveSeat/getRemainingLimit"

        # 定义请求数据
        data = {
            "gid": gid,
            "account": account
        }

        # 发送POST请求
        headers = self._get_headers(host, token)
        response = self._make_request('POST', url, headers, data)

        if response.success:
            logging.info(f"获取剩余限制信息响应: {response.data}")
        else:
            logging.error(f"获取剩余限制信息失败: {response.error_msg}")

        return response

    def collect_netbar_data(self, auth_configs: Optional[List[AuthConfig]] = None) -> List[Dict[str, Any]]:
        """
        收集所有网吧数据
        
        Args:
            auth_configs (List[AuthConfig], optional): 认证配置列表，如果未提供则使用默认配置
            
        Returns:
            list: 所有收集到的数据
        """
        # 使用默认认证配置或传入的配置
        configs = auth_configs if auth_configs is not None else self.DEFAULT_AUTH_CONFIGS
        collected_data = []

        for auth_config in configs:
            # 登录获取token
            login_result = self.mobile_login_with_headers(
                auth_config.host,
                auth_config.uniacid,
                auth_config.open_id
            )

            # 检查登录是否成功
            if not login_result.success or not login_result.data:
                logging.warning(f"登录失败: {auth_config.host}")
                continue

            # 获取token和用户信息
            try:
                token = login_result.data["data"]["token"]
                netbar_list = login_result.data["data"]["auth"]["netbarList"]
                member_info = login_result.data["data"]["auth"]["member"]
                brand_info = login_result.data["data"]["auth"]["company"]
            except (KeyError, TypeError) as e:
                logging.error(f"登录响应数据结构异常: {e}")
                continue

            # 为每个品牌创建数据容器
            brand_data = {
                "brand_name": brand_info.get("name", ""),
                "brand_id": brand_info.get("id", ""),
                "member": member_info,
                "netbars": []
            }

            # 遍历所有网吧门店
            for netbar in netbar_list:
                gid = netbar.get("id")
                netbar_name = netbar.get("name", "未知门店")

                logging.info(f"正在处理门店: {netbar_name}")

                # 获取机器座位信息
                machines_result = self.get_machines(
                    auth_config.host,
                    gid,
                    member_info.get("idcard"),
                    token
                )

                # 获取剩余限制信息（在线机器数和空闲机器数）
                remaining_limit_result = self.get_remaining_limit(
                    auth_config.host,
                    gid,
                    member_info.get("idcard"),
                    token
                )

                # 保存数据
                brand_data["netbars"].append({
                    "info": netbar,
                    "machines": machines_result.__dict__ if machines_result else {},
                    "remaining_limit": remaining_limit_result.__dict__ if remaining_limit_result else {}
                })

            collected_data.append(brand_data)

        return collected_data

    def process_netbar_data(self, collected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理收集到的网吧数据，统计座位信息
        
        Args:
            collected_data (list): 收集到的原始数据
            
        Returns:
            list: 处理后的数据
        """
        processed_data = []

        for brand_data in collected_data:
            processed_brand = {
                "brand_name": brand_data["brand_name"],
                "brand_id": brand_data["brand_id"],
                "netbars": []
            }

            for netbar_data in brand_data["netbars"]:
                netbar_info = netbar_data["info"]
                machines_result = netbar_data["machines"]
                remaining_limit_result = netbar_data["remaining_limit"]

                # 统计座位信息
                total_seats = 0
                online_seats = 0
                offline_seats = 0

                # 优先使用机器信息中的数据
                if (machines_result.get("success") and
                        machines_result.get("data") and
                        isinstance(machines_result["data"], dict) and
                        "data" in machines_result["data"]):

                    online_seats, offline_seats, total_seats = self._calculate_seats_from_machines(machines_result)
                else:
                    # 如果没有机器信息，回退到剩余限制数据分析
                    if (remaining_limit_result.get("success") and
                            remaining_limit_result.get("data") and
                            isinstance(remaining_limit_result["data"], dict) and
                            "data" in remaining_limit_result["data"]):

                        remaining_data = remaining_limit_result["data"]["data"]
                        if isinstance(remaining_data, dict):
                            # 使用剩余限制接口提供的数据

                            offline_seats = remaining_data.get("remainingCount", 0)
                            total_seats = remaining_data.get("machineCount", 0)
                            online_seats = total_seats - offline_seats
                        else:
                            # 如果都没有数据，返回默认值
                            online_seats = 0
                            offline_seats = 0
                            total_seats = 0
                    else:
                        # 如果都没有数据，返回默认值
                        online_seats = 0
                        offline_seats = 0
                        total_seats = 0

                processed_brand["netbars"].append({
                    "netbar_info": netbar_info,
                    "seats_stats": {
                        "total": total_seats,
                        "online": online_seats,
                        "offline": offline_seats
                    },
                    "raw_data": {
                        "machines": machines_result,
                        "remaining_limit": remaining_limit_result
                    }
                })

            processed_data.append(processed_brand)

        return processed_data

    def _calculate_seats_from_machines(self, machines_result: Dict[str, Any]) -> tuple:
        """
        从机器数据中计算座位数量
        
        Args:
            machines_result (dict): 机器数据结果
            
        Returns:
            tuple: (online_seats, offline_seats, total_seats)
        """
        online_seats = 0
        offline_seats = 0

        # 从机器数据中统计座位
        if (machines_result.get("success") and
                machines_result.get("data") and
                isinstance(machines_result["data"].get("data"), list)):

            machines = machines_result["data"]["data"]
            for machine in machines:
                if isinstance(machine, dict) and "state" in machine:
                    # state=1 表示机器可用
                    if machine["state"] == 1:
                        # 检查是否有用户在线（通过netbarOnline字段）
                        netbar_online = machine.get("netbarOnline")
                        if netbar_online is not None:  # 有用户在线
                            online_seats += 1
                        else:  # 没有用户在线，但机器可用
                            offline_seats += 1

        total_seats = len(machines_result["data"]["data"])
        return online_seats, offline_seats, total_seats

    def format_for_feishu(self, processed_data: List[Dict[str, Any]]) -> List[List[str]]:
        """
        将处理后的数据格式化为飞书表格所需的格式
        
        Args:
            processed_data (list): 处理后的数据
            
        Returns:
            list: 适用于飞书表格的行列数据
        """
        rows = []
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        black_netbar_list = [
            "青鸟-铁健网咖",
            "青鸟-深蓝网咖",
            "青鸟-易网网咖",
            "青鸟-老地方店",
            "青鸟-永济易酷网咖",
            "帝京网客",
            "天际壹号网咖-儒城店",
            "魔杰电竞盛隆店",
            "68鑫杰网咖",
            "新蓝网苑",
            "四季电竞",
            "馨宇网咖",
            "涵度电竞",
            "星盟电竞",
            "天河电竞",
            "满天鑫网吧",
            "鲸羽电竞",
            "天际壹号网咖-升辉店",
            "蜂巢电竞",
            "蜗牛快跑柠芒心动店",
            "巅峰电竞",
            "伊时代电子竞技俱乐部",
            "街角电竞",
            "大富豪电竞",
            "极夜未来电竞综合体",
            "斑马电竞",
            "魔方电竞",
            "D+电竞馆",
            "黑神话电竞",
            "中太电竞网咖",
            "运城米兔电竞",
            "中太网咖（崇文街店）",
            "灵枫电竞",
            "孝义花样年华网吧",
            "内蒙古津乙电竞",
            "悟空电竞",
            "海安市唐会电竞",
            "闪电熊网吧",
            "忻悦电竞",
            "赵盟电竞",
            "极境电竞生活馆",
            "螳螂电竞",
            "极境电竞酷艺店",
            "极境电竞白鲸店",
            "极地电竞",
            "涵度电竞天空店",
            "鑫驰电竞",
            "暗影猫电竞"
        ]

        # 添加数据行
        for brand_data in processed_data:
            brand_name = brand_data["brand_name"]

            for netbar_data in brand_data["netbars"]:
                netbar_info = netbar_data["netbar_info"]
                seats_stats = netbar_data["seats_stats"]

                # 生成唯一的ID（使用UUID）
                unique_id = str(uuid.uuid4())
                if netbar_info.get("name") in black_netbar_list:
                    continue

                row = [
                    unique_id,  # ID
                    brand_name,  # 品牌名称
                    netbar_info.get("name", ""),  # 门店名称
                    f'{str(seats_stats["online"])} / {str(seats_stats["total"])}',  # 在线座位数
                    timestamp,  # 记录时间
                    "",  # 其他数据
                    ""  # 备注
                ]
                rows.append(row)

        return rows

    def upload_to_feishu_sheet(self, spreadsheet_token: str, sheet_id: str,
                               rows: List[List[str]]) -> Dict[str, Any]:
        """
        将数据上传到飞书电子表格
        
        Args:
            spreadsheet_token (str): 飞书电子表格token
            sheet_id (str): 工作表ID
            rows (list): 要上传的行列数据
            
        Returns:
            dict: 上传结果
        """
        try:
            if not rows:
                return {
                    "success": True,
                    "message": "没有数据需要上传"
                }

            # 调用飞书表格客户端追加数据
            result = self.feishu_client.append_sheet_data(spreadsheet_token, sheet_id, rows)

            if result.get("success"):
                logging.info(f"成功上传 {len(rows) - 1} 条数据到飞书表格")  # 减去表头
                return {
                    "success": True,
                    "message": f"成功上传 {len(rows) - 1} 条数据",
                    "data": result.get("data")
                }
            else:
                error_msg = result.get("error_msg", "未知错误")
                logging.error(f"上传数据到飞书表格失败: {error_msg}")
                return {
                    "success": False,
                    "message": f"上传失败: {error_msg}",
                    "error": error_msg
                }

        except Exception as e:
            logging.error(f"上传数据到飞书表格时发生异常: {e}")
            return {
                "success": False,
                "message": f"上传异常: {e}",
                "error": str(e)
            }

    def save_to_mongodb(self, processed_data: List[Dict[str, Any]]) -> bool:
        """
        将处理后的数据保存到MongoDB，参考QNDataCollector.update_db_online_data的格式
        
        Args:
            processed_data (list): 处理后的数据
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 连接数据库
            if not self.db_manager.connect():
                logging.error("无法连接到数据库")
                return False

            # 构建要保存的数据格式
            upload_data = {}
            for brand_data in processed_data:
                for netbar_data in brand_data["netbars"]:
                    netbar_info = netbar_data["netbar_info"]
                    seats_stats = netbar_data["seats_stats"]
                    
                    # 构建键值对，格式与QNDataCollector.update_db_online_data相同
                    netbar_key = f'{netbar_info.get("id")}-{netbar_info.get("name", "")}'
                    online_value = f'{str(seats_stats["online"])} / {str(seats_stats["total"])}'
                    upload_data.update({netbar_key: online_value})
            
            # 调用数据库管理器的insert_online_rate_v2方法
            success = self.db_manager.insert_online_rate_v2(upload_data)
            logging.info(f"数据保存到MongoDB完成，成功: {success}")
            
            return success
        except Exception as e:
            logging.error(f"保存数据到MongoDB时发生异常: {e}")
            return False
        finally:
            # 断开数据库连接
            self.db_manager.disconnect()

    def run_full_process(self, auth_configs: Optional[List[AuthConfig]] = None,
                         spreadsheet_token: Optional[str] = None,
                         sheet_id: Optional[str] = None) -> Dict[str, Any]:
        """
        运行完整的数据收集和上传流程
        
        Args:
            auth_configs (List[AuthConfig], optional): 认证配置列表
            spreadsheet_token (str, optional): 飞书电子表格token
            sheet_id (str, optional): 工作表ID
            
        Returns:
            dict: 完整流程的结果
        """
        # 1. 收集数据
        logging.info("开始收集网吧数据...")
        collected_data = self.collect_netbar_data(auth_configs)

        # 2. 处理数据
        logging.info("处理收集到的数据...")
        processed_data = self.process_netbar_data(collected_data)

        # 3. 格式化数据
        logging.info("格式化数据以适应飞书表格...")
        formatted_rows = self.format_for_feishu(processed_data)

        # 4. 保存数据到MongoDB
        logging.info("保存数据到MongoDB...")
        mongodb_save_result = self.save_to_mongodb(processed_data)

        result = {
            "collected_data": collected_data,
            "processed_data": processed_data,
            "formatted_rows": formatted_rows,
            "mongodb_save_result": mongodb_save_result,
            "upload_result": None
        }

        # 5. 上传数据（如果提供了飞书参数）
        if spreadsheet_token and sheet_id:
            logging.info("上传数据到飞书表格...")
            upload_result = self.upload_to_feishu_sheet(spreadsheet_token, sheet_id, formatted_rows)
            result["upload_result"] = upload_result
        else:
            logging.info("未提供飞书表格参数，跳过上传步骤")
            result["upload_result"] = {
                "success": True,
                "message": "未提供飞书表格参数，跳过上传"
            }

        return result


def main():
    """主函数，用于演示如何使用DBZDataCollector类"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 创建数据收集器实例
    collector = DBZDataCollector()

    print("=== 开始完整数据收集流程 ===")

    # 运行完整流程（不上传到飞书）
    result = collector.run_full_process()

    # 输出统计信息
    total_brands = len(result["collected_data"])
    total_netbars = sum(len(brand["netbars"]) for brand in result["collected_data"])

    print(f"收集到 {total_brands} 个品牌，共 {total_netbars} 个门店的数据")

    # 表格配置信息（需要根据实际情况修改）
    SPREADSHEET_TOKEN = "LkgdwebJHi5yOUkgOPAc2fnonFb"  # 电子表格token
    SHEET_ID = "9a4941"  # 工作表ID
    result = collector.run_full_process(
        spreadsheet_token=SPREADSHEET_TOKEN,
        sheet_id=SHEET_ID
    )

    return result


if __name__ == '__main__':
    main()