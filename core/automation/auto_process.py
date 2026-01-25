import time

from core.automation.auto import AndroidAutomation


class QingNiaoAutoProcess(object):
    WECHAT_APP_NAME = '微信'
    WECHAT_SEARCH_BTN_XPATH = ('//*[@resource-id="com.tencent.mm:id/jha"]/android.widget.ImageView[1]', 'xpath')
    WECHAT_SEARCH_INPUT_XPATH = ('//*[@resource-id="com.tencent.mm:id/d98"]', 'xpath')

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


class JiMuProcess(QingNiaoAutoProcess):
    """
         吉姆电竞
    """

    def click_huakaifuggui_text_btn(self):
        self.automator.click_element('//*[@text="花开富贵"]', by='xpath')

    def huakaifugui_btn_exists(self):
        return self.automator.element_exists('花开富贵', by='text')

    def click_jimu_text_btn(self):
        self.automator.click_element('吉姆电竞', by='text')

    def jimu_btn_exists(self):
        return self.automator.element_exists('吉姆电竞', by='text')

    def click_jimu_serve_btn(self):
        return self.automator.click_element('//*[@resource-id="com.tencent.mm:id/ani"]', by='xpath')

    def jimu_serve_btn_exists(self):
        return self.automator.element_exists('//*[@resource-id="com.tencent.mm:id/ani"]', by='xpath')

    def click_member_center_btn(self):
        self.automator.click_element('会员中心', by='text')

    def _member_center_btn_exists(self):
        return self.automator.element_exists('会员中心', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
            self.input_search_content("jimudianjing")



        retry_times = 0
        while not self._member_center_btn_exists():
            time.sleep(1)
            self.click_jimu_text_btn()  # 点击吉姆电竞搜索结果
            retry_times += 1
            if retry_times > 5:
                break

        retry_times = 0
        while self._member_center_btn_exists():
            time.sleep(1)
            self.click_member_center_btn()  # 点击会员中心
            retry_times += 1
            if retry_times > 5:
                break


class ChaLiXiongProcess(QingNiaoAutoProcess):
    """
        查理熊
    """

    def click_clx_text_btn(self):
        self.automator.click_element('查理熊电竞馆', by='text')

    def click_reserve_btn(self):
        self.automator.click_element('在线预定', by='text')

    def reserve_btn_exists(self):
        return self.automator.element_exists('在线预定', by='text')

    def click_reserve_online_book_btn(self):
        self.automator.click_element('在线订座', by='text')

    def reserve_online_book_btn_exists(self):
        return self.automator.element_exists('在线订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()  # 搜索
        self.input_search_content("chalixiong")  # 输入搜索chalixiong
        retry_times = 0
        while not self.reserve_btn_exists():
            time.sleep(2)
            self.click_clx_text_btn()  # 点击查理熊电竞馆搜索结果
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while not self.reserve_online_book_btn_exists():
            time.sleep(2)
            self.click_reserve_btn()  # 点击在线预定
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while self.reserve_online_book_btn_exists():
            time.sleep(2)
            self.click_reserve_online_book_btn()  # 点击在线订座,有就点
            retry_times += 1
            if retry_times > 5:
                break
        # self.adb_input_search_content('chalixiong')


class XingHaiProcess(QingNiaoAutoProcess):
    """
        星海电竞馆
    """

    def click_xh_text_btn(self):
        self.automator.click_element('星海电竞馆', by='text')

    def click_member_enter_btn(self):
        self.automator.click_element('会员中心', by='text')

    def member_enter_btn_exists(self):
        return self.automator.element_exists('会员中心', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()

        self.input_search_content("xinghaidianjingguan")
        retry_times = 0
        while not self.member_enter_btn_exists():
            time.sleep(1)
            self.click_xh_text_btn()
            retry_times += 1
            if retry_times > 5:
                break

        retry_times = 0
        while self.member_enter_btn_exists():
            time.sleep(1)
            self.click_member_enter_btn()
            retry_times += 1
            if retry_times > 5:
                break


class LeYouProcess(QingNiaoAutoProcess):
    """
        乐游电堂
    """

    def click_leyou_text_btn(self):
        self.automator.click_element('乐游电堂', by='text')

    def click_fast_enter_btn(self):
        self.automator.click_element('快捷入口', by='text')

    def fast_enter_btn_exists(self):
        return self.automator.element_exists('快捷入口', by='text')

    def click_one_short_reserve_btn(self):
        self.automator.click_element('一键订座', by='text')

    def one_short_reserve_btn_exists(self):
        return self.automator.element_exists('一键订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("leyoudiantang")
        retry_times = 0
        while not self.fast_enter_btn_exists():
            time.sleep(1)
            self.click_leyou_text_btn()
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while not self.one_short_reserve_btn_exists():
            time.sleep(1)
            self.click_fast_enter_btn()
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while self.one_short_reserve_btn_exists():
            time.sleep(1)
            self.click_one_short_reserve_btn()
            retry_times += 1
            if retry_times > 5:
                break


class QingniaoUnitProcess(QingNiaoAutoProcess):
    """
        青鸟电竞联盟
    """

    def click_qingniao_text_btn(self):
        self.automator.click_element('青鸟电竞联盟', by='text')

    def click_fast_enter_btn(self):
        self.automator.click_element('快捷入口', by='text')

    def fast_enter_btn_exists(self):
        return self.automator.element_exists('快捷入口', by='text')

    def click_one_short_reserve_btn(self):
        self.automator.click_element('一键订座', by='text')

    def one_short_reserve_btn_exists(self):
        return self.automator.element_exists('一键订座', by='text')

    def main_process(self):
        self.open_wechat()
        if not self.search_bar_exists():
            self.enter_search_page()
        self.input_search_content("qingniaodianjinglianmeng")
        retry_times = 0
        while not self.fast_enter_btn_exists():
            time.sleep(1)
            self.click_qingniao_text_btn()
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while not self.one_short_reserve_btn_exists():
            time.sleep(1)
            self.click_fast_enter_btn()
            retry_times += 1
            if retry_times > 5:
                break
        retry_times = 0
        while self.one_short_reserve_btn_exists():
            time.sleep(1)
            self.click_one_short_reserve_btn()
            retry_times += 1
            if retry_times > 5:
                break


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
