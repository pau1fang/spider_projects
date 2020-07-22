import requests
import random
from Crypto.Cipher import AES
import base64
import codecs
import hashlib
import json
import re


class DATA:
    def __init__(self):
        self.modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.exponent = "010001"
        self.nonce = "0CoJUm6Qyw8W8jud"

    @staticmethod
    def get_random_str(n):
        random_str = ''
        character = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for i in range(n):
            j = random.randint(0, len(character) - 1)
            random_str += character[j]
        return random_str

    @staticmethod
    def get_encText(text, key):
        pad = 16 - len(text) % 16
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        text = text + str(pad * chr(pad))
        iv = '0102030405060708'
        c = AES.new(key=bytes(key, encoding='utf-8'), mode=AES.MODE_CBC, iv=bytes(iv, encoding='utf-8'))
        f = c.encrypt(bytes(text, encoding='utf8'))
        return base64.b64encode(f).decode('utf8')

    def get_encSecKey(self, message):
        modulus = int(self.modulus, 16)
        exponent = int(self.exponent, 16)
        message = int(codecs.encode(message[::-1].encode('utf-8'), 'hex_codec'), 16)
        key = pow(message, exponent, modulus)
        return '{:x}'.format(key).zfill(256)

    def data(self, message):
        random_str = self.get_random_str(16)
        encText = self.get_encText(text=message, key=self.nonce)
        encText = self.get_encText(encText, random_str)
        encSecKey = self.get_encSecKey(random_str)
        return {
            "params": encText,
            "encSecKey": encSecKey
        }


class MUSIC163:
    def __init__(self):
        self.login_url = 'https://music.163.com/weapi/login/cellphone?csrf_token='
        self.s = requests.session()
        self.code = ''

    @staticmethod
    def headers():
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'origin': 'https://music.163.com',
            'Referer': 'https://music.163.com/',
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            }

    def login(self, username, password):
        if not self.is_phone_number(username):
            print('请检查您的手机号码是否正确')
            return
        message = self.get_message(username, password)
        d = DATA()
        data = d.data(message)
        response = self.s.post(self.login_url, headers=self.headers(), data=data)
        if response.json()['code'] == 200:
            print('登录成功')
            self.code = 1
        elif response.json()['code'] == 250:
            print('当前登录失败，请稍后再试')
        elif response.json()['code'] == 501:
            print('帐号不存在')
        else:
            print('其他错误')

    def sign(self):
        if self.code == 1:
            csrf = self.s.cookies['__csrf']
            sign_url = f'https://music.163.com/weapi/point/dailyTask?csrf_token={csrf}'
            d = DATA()
            message = '{"type":1}'
            data = d.data(message)
            resp = self.s.post(sign_url, headers=self.headers(), data=data)
            print(resp.json()['msg'])
        else:
            return

    @staticmethod
    def get_message(username, password):
        password = password.encode('utf-8')
        password = hashlib.md5(password).hexdigest()
        message = {"phone": username,
                   "password": password,
                   "rememberLogin": "true",
                   "checkToken": "",
                   "csrf_token": ""}
        return json.dumps(message)

    @staticmethod
    def is_phone_number(username):
        num = re.match('\d{11}', username)
        if num is not None and len(username) == 11:
            return True
        else:
            return False


if __name__ == '__main__':
    music = MUSIC163()
    music.login('phone_number', 'password')
    music.sign()
