import requests
import logging
from core.utils.database import get_db_manager


class DBZDataCollector:
    def __init__(self):
        super().__init__()
        self.host = 'api.n1.xinjifei.com'
        self.session = requests.Session()
        self.openid = 'oSzeE7BSc6BckJzhTk9D2oaN9Mvg'
        self.uniacid = 30066
        self.token = None

    def mobile_login(self):
        url = f"https://{self.host}/netbar/login/mobile"
        data = {
            "loading": "false",
            "no_toast": "no_toast",
            "uniacid": self.uniacid,
            "openId": self.openid
        }

        try:
            response = self.session.post(url, data=data, verify=False)
            print(f"移动端登录响应: {response.text}")
            return response.json()
        except Exception as e:
            print(f"移动端登录请求失败: {e}")
            return {"code": -1, "msg": f"请求失败: {e}"}


if __name__ == '__main__':
    dbz_data_collector = DBZDataCollector()
    print(dbz_data_collector.mobile_login())