import time

import lark_oapi as lark
import requests
from lark_oapi.api.contact.v3 import *
from lark_oapi.api.bitable.v1 import *

from config.settings import FEISHUConfig


class FeishuClient:
    def __init__(self, tenant_access_token=None):
        # 加载环境变量
        self.client = (lark.Client.builder()
                       .app_id(FEISHUConfig.FEISHU_APP_ID)
                       .app_secret(FEISHUConfig.FEISHU_APP_SECRET)
                       .domain(FEISHUConfig.FEISHU_DOMAIN)
                       .timeout(3)
                       .enable_set_token(True)
                       .log_level(lark.LogLevel.DEBUG)
                       .build())
        token, expire = self._get_tenant_access_token()
        self.tenant_access_token = tenant_access_token or token
        self.token_expire_time = time.time() + expire

    @staticmethod
    def _get_tenant_access_token():
        """获取租户访问令牌"""
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
            post_data = {
                "app_id": FEISHUConfig.FEISHU_APP_ID,
                "app_secret": FEISHUConfig.FEISHU_APP_SECRET
            }
            response = requests.post(url, json=post_data)
            response.raise_for_status()
            result = response.json()
            return result["tenant_access_token"], result.get("expire", 7200)
        except Exception as e:
            print(f"获取 tenant_access_token 失败: {e}")
            return None, 0

    def _refresh_token_if_needed(self):
        """检查并刷新token"""
        if time.time() >= self.token_expire_time - 60:  # 提前1分钟刷新
            token, expire = self._get_tenant_access_token()
            if token:
                self.tenant_access_token = token
                self.token_expire_time = time.time() + expire
                print("Tenant access token 已刷新")
            else:
                print("刷新 tenant_access_token 失败")

    def test_connection(self):
        """测试飞书连接"""
        try:

            self._refresh_token_if_needed()  # 刷新token

            request: BatchGetIdUserRequest = BatchGetIdUserRequest.builder().user_id_type("open_id").request_body(
                BatchGetIdUserRequestBody.builder()
                .mobiles(["13051528719"])
                .build()).build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()
            response: BatchGetIdUserResponse = self.client.contact.v3.user.batch_get_id(request, request_option=option)
            return True
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False

    def insert_bitable_record(self, app_token: str, table_id: str, fields: dict) -> dict:
        """
        向飞书多维表格插入一条记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            fields (dict): 要插入的记录字段，格式为 {"字段名": "字段值"}
            
        Returns:
            dict: 插入结果，包含 success 状态和 record_id 或错误信息
        """
        try:
            self._refresh_token_if_needed()  # 刷新token
            
            # 构造请求对象
            request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .request_body(
                AppTableRecord.builder()
                .fields(fields)
                .build()
            ).build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

            # 发送请求
            response: CreateAppTableRecordResponse = self.client.bitable.v1.app_table_record.create(request,
                                                                                                    request_option=option)

            # 检查响应结果
            if response.success():
                print(f"成功插入记录，记录ID: {response.data.record_id}")
                return {
                    "success": True,
                    "record_id": response.data.record_id
                }
            else:
                print(f"插入记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return {
                    "success": False,
                    "error_code": response.code,
                    "error_msg": response.msg
                }

        except Exception as e:
            print(f"插入记录时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def batch_insert_bitable_records(self, app_token: str, table_id: str, records: list) -> dict:
        """
        批量向飞书多维表格插入记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            records (list): 要插入的记录列表，每个元素是一个 dict，格式为 {"字段名": "字段值"}
            
        Returns:
            dict: 插入结果，包含 success 状态和 records 或错误信息
        """
        try:
            self._refresh_token_if_needed()  # 刷新token
            # 构造记录列表
            record_list = []
            for record_fields in records:
                record = AppTableRecord.builder().fields(record_fields).build()
                record_list.append(record)

            # 构造请求对象
            request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .request_body(
                BatchCreateAppTableRecordRequestBody.builder()
                .records(record_list)
                .build()
            ).build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

            # 发送请求
            response: BatchCreateAppTableRecordResponse = self.client.bitable.v1.app_table_record.batch_create(request,
                                                                                                               request_option=option)

            # 检查响应结果
            if response.success():
                print(f"成功批量插入 {len(response.data.records)} 条记录")
                record_ids = [record.record_id for record in response.data.records]
                return {
                    "success": True,
                    "record_ids": record_ids,
                    "count": len(record_ids)
                }
            else:
                print(f"批量插入记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return {
                    "success": False,
                    "error_code": response.code,
                    "error_msg": response.msg
                }

        except Exception as e:
            print(f"批量插入记录时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def query_bitable_records(self, app_token: str, table_id: str, filter_conditions: dict = None, 
                              field_names: list = None, max_count: int = 100) -> dict:
        """
        查询飞书多维表格记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            filter_conditions (dict, optional): 过滤条件，例如 {"field_name": "value"}
            field_names (list, optional): 需要返回的字段名列表
            max_count (int): 最大返回记录数，默认100
            
        Returns:
            dict: 查询结果，包含 success 状态和 records 或错误信息
        """
        try:
            self._refresh_token_if_needed()  # 刷新token
            
            # 构建过滤条件
            filter_str = ""
            if filter_conditions:
                conditions = []
                for field, value in filter_conditions.items():
                    # 简单等值条件构造，实际可根据需要扩展更复杂的条件
                    if isinstance(value, str):
                        conditions.append(f'{field}="{value}"')
                    else:
                        conditions.append(f'{field}={value}')
                filter_str = " AND ".join(conditions)
            
            # 构造请求对象
            builder = ListAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .page_size(max_count)
                
            if filter_str:
                builder.filter(filter_str)
                
            if field_names:
                builder.field_names(field_names)

            request: ListAppTableRecordRequest = builder.build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

            # 发送请求
            response: ListAppTableRecordResponse = self.client.bitable.v1.app_table_record.list(request,
                                                                                               request_option=option)

            # 检查响应结果
            if response.success():
                print(f"成功查询到 {len(response.data.items)} 条记录")
                records = []
                for item in response.data.items:
                    records.append({
                        "record_id": item.record_id,
                        "fields": item.fields
                    })
                return {
                    "success": True,
                    "records": records,
                    "total": len(records)
                }
            else:
                print(f"查询记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return {
                    "success": False,
                    "error_code": response.code,
                    "error_msg": response.msg
                }

        except Exception as e:
            print(f"查询记录时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def update_bitable_record(self, app_token: str, table_id: str, record_id: str, fields: dict) -> dict:
        """
        更新飞书多维表格中的记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            record_id (str): 记录 ID
            fields (dict): 要更新的字段，格式为 {"字段名": "字段值"}
            
        Returns:
            dict: 更新结果，包含 success 状态和更新后的记录或错误信息
        """
        try:
            self._refresh_token_if_needed()  # 刷新token
            
            # 构造请求对象
            request: UpdateAppTableRecordRequest = UpdateAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .record_id(record_id) \
                .request_body(
                AppTableRecord.builder()
                .fields(fields)
                .build()
            ).build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

            # 发送请求
            response: UpdateAppTableRecordResponse = self.client.bitable.v1.app_table_record.update(request,
                                                                                                    request_option=option)

            # 检查响应结果
            if response.success():
                print(f"成功更新记录，记录ID: {response.data.record_id}")
                return {
                    "success": True,
                    "record_id": response.data.record_id,
                    "fields": response.data.fields
                }
            else:
                print(f"更新记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return {
                    "success": False,
                    "error_code": response.code,
                    "error_msg": response.msg
                }

        except Exception as e:
            print(f"更新记录时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }

    def delete_bitable_record(self, app_token: str, table_id: str, record_id: str) -> dict:
        """
        删除飞书多维表格中的记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            record_id (str): 要删除的记录 ID
            
        Returns:
            dict: 删除结果，包含 success 状态或错误信息
        """
        try:
            self._refresh_token_if_needed()  # 刷新token
            
            # 构造请求对象
            request: DeleteAppTableRecordRequest = DeleteAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .record_id(record_id) \
                .build()

            # 使用 tenant_access_token
            option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

            # 发送请求
            response: DeleteAppTableRecordResponse = self.client.bitable.v1.app_table_record.delete(request,
                                                                                                    request_option=option)

            # 检查响应结果
            if response.success():
                print(f"成功删除记录，记录ID: {record_id}")
                return {
                    "success": True,
                    "record_id": record_id
                }
            else:
                print(f"删除记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return {
                    "success": False,
                    "error_code": response.code,
                    "error_msg": response.msg
                }

        except Exception as e:
            print(f"删除记录时发生异常: {e}")
            return {
                "success": False,
                "error_msg": str(e)
            }


if __name__ == '__main__':
    client = FeishuClient()
    client.test_connection()