import lark_oapi as lark
import requests
from lark_oapi.api.contact.v3 import *

from config.settings import FEISHUConfig


class FeishuClient:
    def __init__(self):
        # 加载环境变量
        self.client = (lark.Client.builder()
                       .app_id(FEISHUConfig.FEISHU_APP_ID)
                       .app_secret(FEISHUConfig.FEISHU_APP_SECRET)
                       .domain(FEISHUConfig.FEISHU_DOMAIN)
                       .timeout(3)
                       .enable_set_token(False)
                       .log_level(lark.LogLevel.DEBUG)
                       .build())

    def test_connection(self):
        """测试飞书连接"""
        try:
            request: BatchGetIdUserRequest = BatchGetIdUserRequest.builder().user_id_type("open_id").request_body(
                BatchGetIdUserRequestBody.builder()
                .mobiles(["13051528719"])
                .build()).build()
            response: BatchGetIdUserResponse = self.client.contact.v3.user.batch_get_id(request)
            return True
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False


if __name__ == '__main__':
    client = FeishuClient()
    client.test_connection()
    # url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    # # 应用凭证里的 app id 和 app secret
    # post_data = {"app_id": "cli_a9bb9e88bf385bc6", "app_secret": 'yNh8KAzF0HN8X6LASixdugaChfQbPj8n'}
    # r = requests.post(url, data=post_data)
    # tat = r.json()["tenant_access_token"]
    # print(tat)
