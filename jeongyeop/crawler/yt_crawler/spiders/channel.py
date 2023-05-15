import scrapy

from ..items import YoutubeChannelItem
from ..secret import API_KEY

import json
import logging
from datetime import datetime

API_URL = "https://www.googleapis.com/youtube/v3/"

class ChannelSpider(scrapy.Spider):
    name = 'channel'
    allowed_domains = ['youtube.com', 'googleapis.com']
    start_urls = ['https://www.googleapis.com/youtube/v3/']
    
    def __init__(self, query='', *args, **kwargs):
        self.query_list = []
        if query != '':
            self.query_list = query.split(',')

    def start_requests(self):
        for q in self.query_list :
            yield self.get_search_channel(q)

    def get_search_channel(self, q):
        # channel id를 얻기 위해 Search API 사용
        SEARCH_URL = f'{API_URL}search?part=snippet&q={q}&key={API_KEY}&maxResults=1'
        return scrapy.Request(SEARCH_URL, callback=self.find_channel)
    
    def find_channel(self, response):
        # channel id 탐색
        try:
            channel_id = None
            
            res_json = json.loads(response.body)
            if "items" in res_json :
                items = res_json['items']
                for item in items:
                    if item['id']['kind'] == 'youtube#channel':
                        channel_id = item['id']['channelId']
                        break
            else:
                print("items not in res_json")
        except:
            logging.error('Error parsing JSON', exc_info=True)
        
        return self.get_channel_stat(channel_id, callback=self.parse)

    def get_channel_stat(self, channel_id, callback):
        # channel id를 이용해 채널 데이터 수집
        STAT_URL = f'{API_URL}channels?part=snippet,statistics&id={channel_id}&key={API_KEY}'
        return scrapy.Request(STAT_URL, callback=callback)

    def parse(self, response):
        # Channels API 분석
        data = json.loads(response.body)
        data = data['items'][0]
        item = YoutubeChannelItem()
        item['channel_id'] = data['id']
        print("item['channel_id']", item['channel_id'])
        
        # Parse Snippet
        snippet = data['snippet']
        item['title'] = snippet['title']
        item['description'] = snippet['description'] if 'description' in snippet else None

        published_at = None
        # datetime 형식이 동일하지 않아 통일하는 작업 필요
        try:
            dt = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
            published_at = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        except:
            pass
                
        if published_at is None:
            try:
                published_at = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
        
        item['published_at'] = published_at
        item['country'] = snippet['country'] if 'country' in snippet else None
        # print("snippet", snippet)
        
        # Parse Statistics
        statistics = data['statistics']
        item['view_count'] = statistics['viewCount']
        item['subscriber_count'] = statistics['subscriberCount']
        item['video_count'] = statistics['videoCount']
        # print("statistics", statistics)
        
        print("item['published_at']", type(item['published_at']), item['published_at'])
        # Additional data
        print("item['published_at']", item['published_at'])
        now = datetime.now()
        
        item['crawled_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        print("item['crawled_at']", item['crawled_at'])
        
        
        period = now - item['published_at']
        item['period_day'] = period.days
        print("item['period_day']", item['period_day'])
        yield item
