# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YtCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class YoutubeVideoItem(scrapy.Item) :
    video_id = scrapy.Field()
    # snippet
    published_at = scrapy.Field()
    channel_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    channel_title = scrapy.Field()
    tags = scrapy.Field()
    category_id = scrapy.Field()
    
    #snippet - thumbnails
    thumbnail_default = scrapy.Field()
    thumbnail_medium = scrapy.Field()
    thumbnail_high = scrapy.Field()
    thumbnail_standard = scrapy.Field()
    thumbnail_maxres = scrapy.Field()
    
    #  statistics
    view_count = scrapy.Field()
    like_count = scrapy.Field()
    comment_count = scrapy.Field()

    period_day = scrapy.Field()
    crawled_at = scrapy.Field()

class YoutubeVideoIdItem(scrapy.Item) :
    video_id = scrapy.Field()
    channel_id = scrapy.Field()
    query = scrapy.Field()
    crawled_at = scrapy.Field()

class YoutubePlayListIdItem(scrapy.Item) :
    playlist_id = scrapy.Field()
    start_video_id = scrapy.Field()
    channel_id = scrapy.Field()
    query = scrapy.Field()
    crawled_at = scrapy.Field()

class YoutubeChannelItem(scrapy.Item) :
    channel_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    published_at = scrapy.Field()
    view_count = scrapy.Field()
    subscriber_count = scrapy.Field()
    video_count = scrapy.Field()
    country = scrapy.Field()
    crawled_at = scrapy.Field()
    period_day = scrapy.Field()
