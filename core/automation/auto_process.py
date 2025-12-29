import time

from core.automation.auto import AndroidAutomation


class QingNiaoAutoProcess(object):
    WECHAT_APP_NAME = '微信'
    WECHAT_SEARCH_BTN_XPATH = ('//*[@resource-id=\"com.tencent.mm:id/jha\"]/android.widget.ImageView[1]', 'xpath')
    WECHAT_SEARCH_INPUT_XPATH = ('//*[@resource-id=\"com.tencent.mm:id/d98\"]', 'xpath')

    def __init__(self):
        self.automator = AndroidAutomation()

    def open_wechat(self):
        # 搜索设备
        devices = self.automator.search_android_device()
        self.automator.kill_app('com.tencent.mm')
        self.automator.open_app_by_name(self.WECHAT_APP_NAME)
        cur_app = self.automator.get_current_app()
        print(cur_app)
        if cur_app == "com.tencent.mm":
            print("微信已打开")
            return True
        else:
            print("微信未打开")
            return False

    def search_bar_exists(self):
        return self.automator.element_exists(self.WECHAT_SEARCH_INPUT_XPATH[0],
                                             by=self.WECHAT_SEARCH_INPUT_XPATH[1])

    def enter_search_page(self):
        self.automator.click_element(self.WECHAT_SEARCH_BTN_XPATH[0],
                                     by=self.WECHAT_SEARCH_BTN_XPATH[1])

    def input_search_content(self, search_content):
        self.automator.click_element(self.WECHAT_SEARCH_INPUT_XPATH[0],
                                     by=self.WECHAT_SEARCH_INPUT_XPATH[1])
        self.automator.input_text(self.WECHAT_SEARCH_INPUT_XPATH[0],
                                  by=self.WECHAT_SEARCH_INPUT_XPATH[1], text=search_content)

    def adb_input_search_content(self, search_content):
        self.automator.adb_input_text(search_content)


class ChaLiXiongProcess(QingNiaoAutoProcess):

    def click_clx_text_btn(self):
        self.automator.click_element('查理熊电竞馆', by='text')

    def click_reserve_btn(self):
        self.automator.click_element('在线预定', by='text')

    def click_reserve_online_book_btn(self):
        self.automator.click_element('在线订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("chalixiong")
        self.click_clx_text_btn()
        self.click_reserve_btn()
        self.click_reserve_online_book_btn()
        # self.adb_input_search_content('chalixiong')


class XingHaiProcess(QingNiaoAutoProcess):
    def click_clx_text_btn(self):
        self.automator.click_element('星海电竞馆', by='text')

    def click_member_enter_btn(self):
        self.automator.click_element('会员中心', by='text')


    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("xinghaidianjingguan")
        self.click_clx_text_btn()
        self.click_member_enter_btn()


if __name__ == '__main__':
    clx = ChaLiXiongProcess()
    clx.main_process()

    time.sleep(5)
    xh = XingHaiProcess()
    xh.main_process()
