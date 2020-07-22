import requests
from requests import exceptions
import re
from multiprocessing import Pool
import os


def get_pic_info():
    url = 'https://www.duitang.com/napi/index/hot/?'
    for i in range(1000):
        params = {
            'include_fields': 'top_comments,is_root,source_link,item,buyable,root_id,status,like_count,sender,album',
            'limit': '24',
            'start': 24 * i,
        }
        response = requests.get(url, params=params)
        json_data = response.json()
        pic_list = json_data['data']['object_list']
        for pic_ in pic_list:
            image = {}
            pic_info = pic_['album']
            pic_url = pic_info['covers'][0]
            image['pic_name'] = re.sub(r'[\\/:*?"<>|\r\n。，.？ ]+', '', pic_info['name']) + '.' + pic_url.split('.')[-1]
            image['pic_url'] = pic_url
            yield image


def download_pic(image):
    if not os.path.exists(f'./img/{image["pic_name"]}'):
        try:
            resp = requests.get(image['pic_url'])
            if resp.status_code == 200:
                    with open(f'./img/{image["pic_name"]}', 'wb') as f:
                        f.write(resp.content)
        except exceptions:
            return None
    else:
        print(image['pic_name'] + ' has already downloaded')


if __name__ == '__main__':
    if not os.path.exists('./img'):
        os.mkdir('./img')
    pool = Pool()
    pool.map(download_pic, get_pic_info())
    pool.close()
    pool.join()
