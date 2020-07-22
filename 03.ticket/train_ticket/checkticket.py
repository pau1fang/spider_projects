import requests
from urllib.parse import urlencode


class CheckTicket():
    def __init__(self, date, station_start, station_end, purpose):
        self.base_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?'
        self.url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
        self.date = date
        self.start_station = station_start
        self.end_station = station_end
        self.purpose = purpose

    def station_abbr(self):
        """
        查出车站对应的编码
        :return:
        """

        response1 = requests.get(self.url)
        a = response1.text.split('@')
        a.pop(0)
        for each in a:
            i = each.split('|')
            if self.start_station == i[1]:
                self.start_station = i[2]
            elif self.end_station == i[1]:
                self.end_station = i[2]
        return [self.start_station, self.end_station]

    @property
    def get_info(self):
        station = self.station_abbr()

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': 'kyfw.12306.cn',
            'Cookie': '_jc_save_fromStation=; _jc_save_toStation=; _jc_save_fromDate=',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        data = {
            'leftTicketDTO.train_date': self.date,
            'leftTicketDTO.from_station': station[0],
            'leftTicketDTO.to_station': station[1],
            'purpose_codes': self.purpose
        }
        url = self.base_url + urlencode(data)
        response = requests.get(url, headers=headers)
        json_data = response.json()
        maps = json_data['data']['map']
        count = 0
        index = 1
        i_c = {}
        for each in json_data['data']['result']:
            count += 1
            s = each.split('|')[3:]
            info = {
                'train': s[0],
                'start_end': maps[s[3]] + '-' + maps[s[4]],
                'time': s[5] + '-' + s[6],
                '历时': s[7],
                '二等座': s[-17]
            }
            try:
                if info['二等座'] == '有' or int(info['二等座']):
                    print(
                        f'[{index}] 车次:{info["train"]}  始发站:{info["start_end"]}  始-终:{info["time"]}  '
                        f'历时:{info["历时"]}  二等座:{info["二等座"]}')
                    i_c[index] = count
                    index += 1
            except ValueError:
                continue
        return i_c

