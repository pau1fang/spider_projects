from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
import base64
import os
import io
import random


class Jingdong():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.url = 'https://passport.jd.com/new/login.aspx?'
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=self.options, executable_path='D:\Program Files (x86)\chromedriver.exe')
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.maximize_window()

    def open_browser(self):
        self.browser.get(self.url)
        time.sleep(2)
        self.browser.find_element_by_class_name('login-tab-r').click()
        time.sleep(1)
        self.browser.find_element_by_id('loginname').send_keys(self.username)
        self.browser.find_element_by_id('nloginpwd').send_keys(self.password)
        self.browser.find_element_by_class_name('login-btn').click()
        time.sleep(1)

    def get_img_url(self):
        # 获取验证码缺口图片的地址
        img_url = self.browser.find_element_by_class_name('JDJRV-bigimg').find_element_by_css_selector(
            'img').get_attribute('src')
        return img_url

    @staticmethod
    def get_image(image1):
        # 将验证码的缺口图片与已有文件夹中的完整图片进行比较以取得其对应的完整图片
        difference = 0
        image_ = image1
        size = image1.size
        images = os.listdir('./img2')
        pixel1 = image1.load()
        for image in images:
            image = Image.open(f'./img2/{image}')
            pixel2 = image.load()
            diff = 0
            for j in range(size[1]):
                for i in range(size[0]):
                    delta = abs(pixel1[i, j][0] - pixel2[i, j][0]) + abs(pixel1[i, j][1] - pixel2[i, j][1]) + abs(
                        pixel1[i, j][2] - pixel2[i, j][2])
                    diff += delta
            if difference == 0:
                difference = diff
                image_ = image
            elif difference > diff:
                difference = diff
                image_ = image
        return image_

    @staticmethod
    def is_pixel_equal(image1, image2, x, y):
        # 判断两张图片相同坐标的rgb数值是否近似
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 5
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self):
        # 返回验证码缺口的距离
        left = 60
        img_url = self.get_img_url()
        image1_bytes = base64.urlsafe_b64decode(img_url.split(',')[-1])
        image1 = Image.open(io.BytesIO(image1_bytes)).convert("RGB")
        image2 = self.get_image(image1)
        if not image2:
            self.browser.find_element_by_class_name('JDJRV-img-refresh').click()
            time.sleep(1)
            self.get_gap()
        else:
            for i in range(left, image1.size[0]):
                for j in range(image1.size[1]):
                    if not self.is_pixel_equal(image1, image2, i, j):
                        return i
        return left

    @staticmethod
    def get_track(distance):
        # 轨迹生成
        track = []
        track_ = []
        delta_t = 0.1
        for i in range(1, 21):
            delta_dis = 1 / 12 * distance * (delta_t * i) ** 3 - 1 / 12 * distance * (delta_t * (i - 1)) ** 3
            track.append(round(delta_dis))
        for i in range(1, 10):
            delta_dis = 1 / 3 * distance * (i * delta_t) ** 3 - 1 / 3 * distance * ((i - 1) * delta_t) ** 3
            track_.append(round(delta_dis))
        track.append(0)
        while len(track_) > 0:
            track.append(track_.pop())
        track[20] = distance - sum(track)
        return track

    def verify(self):
        # 滑动滑块进行验证
        distince = self.get_gap()
        if distince > 180:
            distince = distince - abs(180-distince)/180*40 - 40
        else:
            distince = distince + abs(180-distince)/180*40 - 40
        tracks = self.get_track(distince)
        slider = self.browser.find_element_by_class_name('JDJRV-slide-btn')
        ActionChains(self.browser).click_and_hold(slider).perform()
        for axis in tracks:
            yoffset = random.randint(-2, 2)
            ActionChains(self.browser).move_by_offset(xoffset=axis, yoffset=yoffset).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()
        time.sleep(3)
        if self.browser.current_url != self.url:
            print("登录成功")
            time.sleep(3)
            self.browser.close()
        else:
            self.verify()

    def main(self):
        self.open_browser()
        time.sleep(1)
        self.verify()

if __name__ == '__main__':
    jingdong = Jingdong('username', 'password')
    jingdong.main()





