from selenium import webdriver
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException
import time
import requests
import json
from io import BytesIO


class BuyTicket():
    def __init__(self, station_start, station_end, date, username, password, purpose, attr, num):
        self.num = 1
        self.start = station_start
        self.end = station_end
        self.date = date
        self.username = username
        self.password = password
        self.purpose = purpose
        self.station_attr = attr
        self.num = num
        self.browser = webdriver.Chrome()
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
        self.wait = WebDriverWait(self.browser, 10)

    def login(self):
        self.browser.get(self.login_url)
        try:
            input_name = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
            input_pd = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
            button = self.wait.until(EC.presence_of_element_located((By.ID, 'loginSub')))
            time.sleep(1)
            input_name.send_keys(self.username)
            input_pd.send_keys(self.password)
            c = Code(self.browser)
            c.main()
            button.click()
            time.sleep(2)
            while self.browser.current_url == self.login_url + '#':
                c = Code(self.browser)
                c.main()
                button.click()
                time.sleep(2)
            self.check()
        except NoSuchElementException:
            self.login()

    def check(self):
        self.browser.add_cookie({'name': '_jc_save_fromStation',
                            'value': json.dumps(self.start).strip('"').replace('\\', '%') + '%2C' + self.station_attr[0]})
        self.browser.add_cookie({'name': '_jc_save_toStation',
                            'value': json.dumps(self.end).strip('"').replace('\\', '%') + '%2C' + self.station_attr[1]})
        self.browser.add_cookie({'name': '_jc_save_fromDate', 'value': self.date})
        self.browser.get(self.ticket_url)
        if self.purpose == '0X00':
            btn = self.browser.find_element_by_id('sf2')
            time.sleep(1)
            btn.click()
        button = self.browser.find_element_by_id('query_ticket')
        time.sleep(1)
        button.click()

    def book_ticket(self):
        print('开始预订车票...')
        time.sleep(4)
        button = self.browser.find_elements_by_class_name('no-br')
        button[self.num - 1].click()
        time.sleep(3)
        button2 = self.wait.until(EC.presence_of_element_located((By.ID, 'normalPassenger_0')))  # 选择第一个常用联系人
        button2.click()
        button3 = self.browser.find_element_by_id('submitOrder_id')
        time.sleep(1)
        button3.click()
        time.sleep(3)
        try:
            button4 = self.browser.find_element_by_id('qr_submit_id')
            button4.click()
        except ElementNotVisibleException:
            button4 = self.browser.find_element_by_id('qr_submit_id')
            button4.click()
        print('[INFO]:车票预定成功！请在30分钟内完成付款！')

    def main(self):
        self.login()
        self.book_ticket()


class Code():
    def __init__(self, browser):
        """
        verity_url: 验证码识别网址
        :param browser:
        """
        self.browser = browser
        self.verify_url = 'http://littlebigluo.qicp.net:47720/'

    def get_position(self):
        """
        获取验证码位置
        :return:
        """
        element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'touclick-img-par')))
        time.sleep(1)
        location = element.location
        size = element.size
        position= (location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height'])
        return position

    def get_screenshot(self):
        """
        :return: 截取页面
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_captcha(self):
        """
        裁剪出验证码图片并保存
        :return:
        """
        position = self.get_position()
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(position)
        captcha.save('captcha.png')

    def parse_img(self):
        files = {'pic_xxfile': open('captcha.png', 'rb')}
        response = requests.post(self.verify_url, files=files)
        num = response.text.split('<B>')[1].split('<')[0]
        try:
            if int(num):
                return [int(num)]
        except ValueError:
            num = list(map(int, num.split()))
            return num

    def img_select(self):
        num = self.parse_img()
        try:
            element = self.browser.find_element_by_class_name('touclick-img-par')
            for i in num:
                if i <= 4:
                    ActionChains(self.browser).move_to_element_with_offset(element, 40+72*(i-1), 73).click().perform()
                else:
                    i -= 4
                    ActionChains(self.browser).move_to_element_with_offset(element, 40+72*(i-1), 145).click().perform()
        except:
            print('元素不可选！')

    def main(self):
        self.get_captcha()
        self.img_select()


