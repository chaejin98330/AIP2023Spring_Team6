import pymysql
import requests

import sys
import os
import time
from tqdm import tqdm

from secret import *
from io import BytesIO
from PIL import Image

# MySQL 서버 연결
try :
    print("connect to DB...")
    crawlDB = pymysql.connect(
        user=SQL_USER,
        passwd=SQL_PW,
        host=SQL_HOST,
        port=SQL_PORT,
        db=SQL_DB
    )
    cursor = crawlDB.cursor()
except :
    print('ERROR: DB connection failed')
    sys.exit(1)

# Thumbnail 링크가 저장된 column을 불러와서 디렉토리를 만들고자함.
table_name = "video_thumbnail_0506"
sql_stat = f'''SELECT  COLUMN_NAME
            FROM    INFORMATION_SCHEMA.COLUMNS
            WHERE   TABLE_NAME = '{table_name}';'''
print("cursor.execute(sql_stat)", sql_stat)
cursor.execute(sql_stat)
results = cursor.fetchall()
target_col_list = []
col_name_list = []
for result in results:
    result_col = result[0]
    if 'thumbnail' in result_col:
        # thumbnail이 포함된 열을 가져오기 위해 리스트에 저장
        target_col_list.append(result_col)
        col_name_list.append(result_col.split('_')[1])
        # thumbnail이 포함된 열 이름대로 디렉토리 생성
        if not os.path.exists(result_col):
            os.makedirs(result_col)

target_col_list.remove('thumbnail_maxres')
target_cols = ",".join(target_col_list) 

# thumbnail_default, thumbnail_medium, thumbnail_high,  thumbnail_standard, thumbnail_maxres

# 썸네일 이미지 링크 가져오기
sql_stat = f'''SELECT video_id, {target_cols} FROM {table_name};'''
print("cursor.execute(sql_stat)", sql_stat)
cursor.execute(sql_stat)
results = cursor.fetchall()
print("query result size: ", len(results))

# 썸네일 이미지 다운로드
for result in tqdm(results):
    video_id = result[0]
    for idx, image_link in enumerate(result[1:len(result)]):
        if image_link is not None:
            response = requests.get(image_link)
            time.sleep(0.2)
            # 썸네일 이미지 저장
            image = Image.open(BytesIO(response.content))
            image.save(f"{target_col_list[idx]}/{col_name_list[idx]}_{video_id}.jpg")

crawlDB.close()
print("Done")
