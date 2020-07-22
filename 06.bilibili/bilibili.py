import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import base64
from PIL import Image
import io
import random
import json


class BilibiliLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.url = 'https://passport.bilibili.com/login'
        self.cookies = {}

    def login(self):
        self.driver.get(url=self.url)
        wait = WebDriverWait(self.driver, 10)
        input_username = wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        input_password = wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        btn_login = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-login')))
        input_username.send_keys(self.username)
        input_password.send_keys(self.password)
        btn_login.click()
        time.sleep(3)
        self.verify()
        for cookie in self.driver.get_cookies():
            self.cookies[cookie['name']] = cookie['value']

    def get_username(self):
        follow_url = 'https://api.bilibili.com/x/relation/followings?vmid=' + self.cookies['DedeUserID'] + '&pn=1&ps=20&order=desc&jsonp=jsonp&callback=__jp7'
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': f'https://space.bilibili.com/{self.cookies["DedeUserID"]}/fans/follow',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        resp = requests.get(url=follow_url, cookies=self.cookies, headers=headers)
        data = resp.text
        data = data[6: -1]
        data = json.loads(data, strict=False)
        users = data['data']['list']
        for user in users:
            print(user['uname'])

    def verify(self):
        distance = self.get_gap_position()
        distance = distance - 10
        slider = self.driver.find_element_by_class_name('geetest_slider_button')
        track = self.get_track(distance)
        ActionChains(self.driver).click_and_hold(slider).perform()
        for i in track:
            y_offset = random.randint(-3, 3)
            ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=y_offset).perform()
        ActionChains(self.driver).pause(0.5).release().perform()
        time.sleep(3)
        if self.driver.current_url != self.url:
            print('登录成功')
        else:
            btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_panel_error_content')))
            btn.click()
            time.sleep(2)
            self.verify()

    def get_captacha_image(self, class_name):
        #获取滑块验证码图片
        captacha_image = self.driver.execute_script(
            f'return document.getElementsByClassName("{class_name}")[0].toDataURL("image/png");')
        captacha_image = base64.b64decode(captacha_image.split(',')[-1])
        return Image.open(io.BytesIO(captacha_image))

    def get_gap_position(self):
        #获取滑块验证码的缺口
        image1 = self.get_captacha_image('geetest_canvas_fullbg')
        image2 = self.get_captacha_image('geetest_canvas_bg')
        x, y = image1.size[0], image1.size[1]
        pixel1 = image1.load()
        pixel2 = image2.load()
        for i in range(x):
            for j in range(y):
                data1 = pixel1[i, j]
                data2 = pixel2[i, j]
                if abs(data1[0]-data2[0]) < 20 and abs(data1[1]-data2[1]) < 20 and abs(data1[2]-data2[2]) < 20:
                    continue
                else:
                    return i

    @staticmethod
    def get_track(distance):
        #轨迹生成
        track = []
        track_ = []
        delta_t = 0.1
        for i in range(1, 21):
            delta_dis = 1/12*distance*(delta_t*i)**3-1/12*distance*(delta_t*(i-1))**3
            track.append(round(delta_dis))
        for i in range(1, 10):
            delta_dis = 1/3*distance*(i*delta_t)**3 - 1/3*distance*((i-1)*delta_t)**3
            track_.append(round(delta_dis))
        track.append(0)
        while len(track_) > 0:
            track.append(track_.pop())
        track[20] = distance-sum(track)
        return track

    def __repr__(self):
        return 'bilibili'


if __name__ == '__main__':
    b = BilibiliLogin('telephone', 'password')
    b.login()
    b.get_username()
