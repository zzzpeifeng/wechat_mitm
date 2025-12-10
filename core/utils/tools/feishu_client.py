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
        self.tenant_access_token = tenant_access_token or self._get_tenant_access_token()

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
            return response.json()["tenant_access_token"]
        except Exception as e:
            print(f"获取 tenant_access_token 失败: {e}")
            return None

    def test_connection(self):
        """测试飞书连接"""
        try:
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

    def insert_bitable_record(self, app_token: str, table_id: str, fields: dict) -> bool:
        """
        向飞书多维表格插入一条记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            fields (dict): 要插入的记录字段，格式为 {"字段名": "字段值"}
            
        Returns:
            bool: 插入是否成功
        """
        try:
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
            response: CreateAppTableRecordResponse = self.client.bitable.v1.app_table_record.create(request, request_option=option)
            
            # 检查响应结果
            if response.success():
                print(f"成功插入记录，记录ID: {response.data.record_id}")
                return True
            else:
                print(f"插入记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return False
                
        except Exception as e:
            print(f"插入记录时发生异常: {e}")
            return False

    def batch_insert_bitable_records(self, app_token: str, table_id: str, records: list) -> bool:
        """
        批量向飞书多维表格插入记录
        
        Args:
            app_token (str): 多维表格应用的 token
            table_id (str): 表格 ID
            records (list): 要插入的记录列表，每个元素是一个 dict，格式为 {"字段名": "字段值"}
            
        Returns:
            bool: 插入是否成功
        """
        try:
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
            response: BatchCreateAppTableRecordResponse = self.client.bitable.v1.app_table_record.batch_create(request, request_option=option)
            
            # 检查响应结果
            if response.success():
                print(f"成功批量插入 {len(response.data.records)} 条记录")
                return True
            else:
                print(f"批量插入记录失败，错误码: {response.code}, 错误信息: {response.msg}")
                return False
                
        except Exception as e:
            print(f"批量插入记录时发生异常: {e}")
            return False


if __name__ == '__main__':
    client = FeishuClient()
    client.test_connection()