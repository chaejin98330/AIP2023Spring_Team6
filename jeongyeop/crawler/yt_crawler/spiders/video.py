import scrapy
from ..items import YoutubeVideoItem
from ..secret import API_KEY

import json
import logging
from datetime import datetime


API_URL = "https://www.googleapis.com/youtube/v3/"

class VideoSpider(scrapy.Spider):
    name = 'video'
    allowed_domains = ['youtube.com', 'googleapis.com']
    start_urls = ['https://www.googleapis.com/youtube/v3/']

    def __init__(self, video='', *args, **kwargs):
        self.video_list = []
        if  video != '':
            self.video_list = video.split(',')


    def start_requests(self):
        video_len = len(self.video_list)
        step = 50
        for i in range(0, video_len, step):
            print("start_requests", i)
            if i+50 < video_len:
                print(",".join(self.video_list[i:i+step]))
                v_query = ",".join(self.video_list[i:i+step])
                yield self.get_video_info(v_query)
            else:
                print(",".join(self.video_list[i:video_len]))
                v_query = ",".join(self.video_list[i:video_len])
                yield self.get_video_info(v_query)


    def get_video_info(self, v_qeury):
        # video 정보를 얻기 위해 Videos API 사용
        SEARCH_URL = f'{API_URL}videos?part=id,snippet,statistics&id={v_qeury}&key={API_KEY}'
        return scrapy.Request(SEARCH_URL, callback=self.parse)


    def parse(self, response):
        res_json = json.loads(response.body)
        item = YoutubeVideoItem()
        elements =  res_json['items']
        for element in elements:
            try:
                item['video_id'] = element['id']

                snippet = element['snippet']
                item['published_at'] = snippet['publishedAt']
                item['channel_id'] = snippet['channelId']
                item['title'] = snippet['title'].replace(',', '')
                item['description'] = snippet['description'].replace(',', '') if 'description' in snippet else None
                item['channel_title'] = snippet['channelTitle'].replace(',', '')
                item['tags'] = "|".join(snippet['tags']) if 'tags' in snippet else None
                item['category_id'] = snippet['categoryId'] if 'categoryId' in snippet else None

                thumbnails = snippet['thumbnails']
                item['thumbnail_default'] = thumbnails['default']['url']
                item['thumbnail_medium'] = thumbnails['medium']['url']
                item['thumbnail_high'] = thumbnails['high']['url']
                item['thumbnail_standard'] = thumbnails['standard']['url'] if 'standard' in thumbnails else None
                item['thumbnail_maxres'] = thumbnails['maxres']['url'] if 'maxres' in thumbnails else None

                statistics = element['statistics']
                item['view_count'] = statistics['viewCount']
                item['like_count'] = statistics['likeCount'] if 'likeCount' in statistics else None
                item['comment_count'] = statistics['commentCount'] if 'commentCount' in statistics else None

                published_at = None
                # datetime 형식이 동일하지 않아 통일하는 작업 필요
                try:
                    # .%f가 있는 형식을 없는 형식으로 변경
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

                now = datetime.now()
                item['crawled_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
                print("item['crawled_at']", item['crawled_at'])

                period = now - item['published_at']
                item['period_day'] = period.days
                yield item
            except Exception as e:
                print(f"ERROR parse {element['id']} res {e}")
