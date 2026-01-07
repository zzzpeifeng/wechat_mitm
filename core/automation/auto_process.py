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
    """
        查理熊
    """

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
    """
        星海电竞馆
    """

    def click_xh_text_btn(self):
        self.automator.click_element('星海电竞馆', by='text')

    def click_member_enter_btn(self):
        self.automator.click_element('会员中心', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("xinghaidianjingguan")
        self.click_xh_text_btn()
        self.click_member_enter_btn()


class LeYouProcess(QingNiaoAutoProcess):
    """
        乐游电堂
    """

    def click_leyou_text_btn(self):
        self.automator.click_element('乐游电堂', by='text')

    def click_fast_enter_btn(self):
        self.automator.click_element('快捷入口', by='text')

    def click_one_short_reserve_btn(self):
        self.automator.click_element('一键订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("leyoudiantang")
        self.click_leyou_text_btn()
        self.click_fast_enter_btn()
        self.click_one_short_reserve_btn()


class QingniaoUnitProcess(QingNiaoAutoProcess):
    """
        青鸟电竞联盟
    """

    def click_qingniao_text_btn(self):
        self.automator.click_element('青鸟电竞联盟', by='text')

    def click_fast_enter_btn(self):
        self.automator.click_element('快捷入口', by='text')

    def click_one_short_reserve_btn(self):
        self.automator.click_element('一键订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("qingniaodianjinglianmeng")
        self.click_qingniao_text_btn()
        self.click_fast_enter_btn()
        self.click_one_short_reserve_btn()


class DianfengVSProcess(QingNiaoAutoProcess):
    """
        巅峰VS电竞
    """

    def click_dianfeng_item(self):
        self.automator.click_element('巅峰VS电竞', by='text')

    def click_nearby_offstore_enter_btn(self):
        self.automator.click_element('附近门店', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content('dianfeng')
        self.click_dianfeng_item()
        self.click_nearby_offstore_enter_btn()


if __name__ == '__main__':
    # clx = ChaLiXiongProcess()
    # clx.main_process()
    #
    # time.sleep(5)
    # xh = XingHaiProcess()
    # xh.main_process()
    #
    # time.sleep(5)
    # ly = LeYouProcess()
    # ly.main_process()
    #
    # time.sleep(5)
    # qn = QingniaoUnitProcess()
    # qn.main_process()
    # time.sleep(5)

    df = DianfengVSProcess()
    df.main_process()
