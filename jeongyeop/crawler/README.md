# Youtube Thumbnail Crawler

## What

1. Find out the channel ID and info by search API.
2. Scrap YouTube video IDs by using channels search URL.
3. Get thumbnails and information of YouTube videos based on YouTube video IDs.
4. Download thumbnail Images

## How

### Settings

```cmd
pip install -r requirements.txt
```

🔨 rename secret file and fill setting value

```cmd
mv secret_template.py secret.py
```

### Find out the channel ID and info by search API

```cmd
scrapy crawl channel -a query="channel name"
```

### Scrap YouTube video IDs by using channels search URL

```cmd
scrapy crawl channel_query -a channel="channel_id"
```

### Get thumbnails and information of YouTube videos based on YouTube video

```cmd
scrapy crawl video -a video="video_id"
```

### Download thumbnail Images

```cmd
python save_thumbnails.py
```
