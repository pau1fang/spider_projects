import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml.html import etree
import bs4
import jieba
import wordcloud
import re
from matplotlib import pyplot


class Movie():
    def __init__(self, name):
        self.url = f'https://search.douban.com/movie/subject_search?search_text={name}'
        self.headers = 'User-Agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/78.0.3904.108 Safari/537.36"'
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(self.headers)
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.wait = WebDriverWait(self.browser, 10)

    def get_search(self):
        self.browser.get(self.url)
        response = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.title > a')))
        if response:
            print('请选择:')
            movies = []
            for i in range(10):
                name = response[i].text
                url = response[i].get_attribute('href')
                print(f'{[i]}.{name}')
                movies.append([name, url])
            self.browser.close()
            return movies
        else:
            print("没有搜到您要的信息，请重新输入")
            self.get_search()

    def get_movie_info(self, movie):
        name = movie[0]
        url = movie[1]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'}
        resp = requests.get(url, headers=headers)
        try:
            if resp.status_code == 200:
                soup = bs4.BeautifulSoup(resp.text, 'html.parser')
                info = soup.find(name='div', attrs={'id': 'info'}).text
                rating = soup.find(name='div', attrs={'class': 'rating_self'})
                rating_num = rating.strong.text
                rating_people = rating.a.text
                print(info)
                print(rating_num)
                print(rating_people)
                text = self.get_reviews(url, headers)
                self.word_cloud(name, text)
            else:
                return None
        except requests.exceptions:
            return None

    @staticmethod
    def get_reviews(url, headers):
        text = ''
        for i in range(5):
            url = f'{url}reviews?start=i'
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.text)
            reviews = html.xpath('//*[@class="short-content"]/text()')
            reviews = ''.join(''.join(reviews).split())
            reviews = ''.join(reviews.split('()'))
            text += reviews
        return text

    @staticmethod
    def word_cloud(name, word):
        name = re.sub(r'[\\/:*?"<>|\r\n。，.？]+', '', name)
        ls = jieba.lcut(word)
        text = ' '.join(ls)
        w = wordcloud.WordCloud(font_path='simkai.ttf', width=800, height=600, background_color='white')
        w.generate(text)
        w.to_file(f'{name}.png')
        pyplot.imshow(w)
        pyplot.axis(False)
        pyplot.show()


def main():
    movie_name = input("请输入电影名称，即可查询对应的影片信息:")
    m = Movie(movie_name)
    movies = m.get_search()
    num = input('请输入序号选择:')
    num = int(num)
    m.get_movie_info(movies[num])


if __name__ == '__main__':
    main()

