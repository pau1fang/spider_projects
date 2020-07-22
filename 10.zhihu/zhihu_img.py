import requests
import re
import os


class CrawlImg:
    def __init__(self):
        self.question_number = 311745535
        self.url = f'https://www.zhihu.com/api/v4/questions/{self.question_number}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default'
        self.headers = self.get_headers()

    def get_headers(self):
        return {
            'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'referer': f'https://www.zhihu.com/question/{self.question_number}',
            }

    def get_img_info(self, url):
        response = requests.get(url=url, headers=self.headers)
        if response.status_code==200:
            content = response.json()
            data = content.get('data')
            for answer in data:
                author_name = re.sub(r'[\\/:*?"<>|\r\n。，.？ ]+', '', answer.get('author').get('name'))
                imgs = re.findall('data-actualsrc="(.*?)"/>', answer.get('content'))
                for img in imgs:
                    yield {"author": author_name, "img_url": img}
            is_end = content.get('paging').get('is_end')
            while not is_end:
                next = content.get('paging').get('next')
                response_ = requests.get(url=next, headers=self.headers)
                if response.status_code==200:
                    content = response_.json()
                    for answer in content.get('data'):
                        author_name = re.sub(r'[\\/:*?"<>|\r\n。，.？ ]+', '', answer.get('author').get('name'))
                        imgs = re.findall('data-actualsrc="(.*?)"/>', answer.get('content'))
                        for img in imgs:
                            yield {"author": author_name, "img_url": img}
                    is_end = content.get('paging').get('is_end')

    def download_img(self, img):
        url = img.get('img_url')
        author_name = img.get('author')
        filename = f'./imgs/{author_name}'
        if not os.path.exists(filename):
            os.mkdir(filename)
        try:
            response = requests.get(url)
            if response.status_code==200:
                img_name=re.search('v2-(.*)\?', url).group(1)
                img_path = f'{filename}/{img_name}'
                with open(img_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('download failed')
        except:
            return None

    def main(self):
        if not os.path.exists('./imgs'):
            os.mkdir('./imgs')
        for img_info in self.get_img_info(self.url):
            self.download_img(img_info)


if __name__ == '__main__':
    c = CrawlImg()
    c.main()
