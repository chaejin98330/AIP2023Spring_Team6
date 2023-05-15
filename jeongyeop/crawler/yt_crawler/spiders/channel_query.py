import scrapy

from ..items import YoutubeVideoIdItem, YoutubePlayListIdItem

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

import logging
from datetime import datetime
import time
class ChannelQuerySpider(scrapy.Spider):
    name = 'channel_query'
    allowed_domains = ['youtube.com', 'googleapis.com']
    start_urls = ['https://www.googleapis.com/youtube/v3/']

    headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71',
        'referer' : 'https://www.youtube.com',
    }

    def __init__(self, channel='', query='먹방', *args, **kwargs):
        self.query = query
        self.channel_list = []
        self.count = 0
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('window-size=1920,1080')
        self.options.add_argument('headless')
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--log-level=3")
        
        self.driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=self.options)

        page_load_timeout = 60
        self.driver.set_page_load_timeout(page_load_timeout)

        if channel != '':
            self.channel_list = channel.split(',')


    def start_requests(self):
        for ch in self.channel_list :
            item = self.get_search_channel(ch)
            if item is not None:
                yield item


    def get_search_channel(self, channel):
        SEARCH_URL = f'https://www.youtube.com/channel/{channel}/search?query={self.query}'
        # 예시 URL: https://www.youtube.com/channel/UC-i2ywiuvjvpTy2zW-tXfkw/search?query=먹방
        self.driver.get(SEARCH_URL)
        time.sleep(3)
        # self.driver.implicitly_wait(5)
        # generator 오류를 막기 위해 fake request 보냄
        return scrapy.Request(SEARCH_URL, callback=self.parse, meta={'channel': channel}, headers=self.headers)

    def parse(self, response):
        soup=BeautifulSoup(self.driver.page_source, "html.parser")

        targets = soup.find_all('a',{'id':'thumbnail', 'href':True})
        print("targets", len(targets))
        self.count += len(targets)
        for i, target in enumerate(targets):
            
            href = target['href']
            print(f"{i}: href={href}")
            if 'list' in href:
                print("YoutubePlayListIdItem")
                item = YoutubePlayListIdItem()
                item['channel_id'] = response.meta['channel']
                href_split = href.split('list=')
                item['playlist_id'] = href_split[1]
                item['start_video_id'] = href_split.split('v=')[1]
                item['query'] = self.query
                now = datetime.now()
                item['crawled_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
                yield item
            else:
                print("YoutubeVideoIdItem", self.count)
                item = YoutubeVideoIdItem()
                item['channel_id'] = response.meta['channel']
                item['video_id'] = href.split('=')[1]
                item['query'] = self.query
                try:
                    time_status = target.select_one('#text.ytd-thumbnail-overlay-time-status-renderer')
                    time_status_label = time_status['aria-label']
                    print("time_status_label", time_status_label, '분' in time_status_label and '1분' != time_status_label)
                    
                    if '분' in time_status_label and '1분' != time_status_label:
                        # 쇼츠 영상이 아닌 것을 확인하여 산출
                        now = datetime.now()
                        item['crawled_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
                        yield item
                    else:
                        print("shorts", item['video_id'])
                except Exception as e:
                    print("ERROR: time_status_label", e)
